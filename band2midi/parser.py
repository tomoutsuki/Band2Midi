"""Decode the length-delimited Logic song layout in the supplied iOS fixtures.

See docs/format.md for offsets, evidence, and the supported format boundary.
Only projectData is opened; media and instrument payloads are never exported.
"""

from dataclasses import dataclass
from pathlib import Path
import plistlib
import struct
from xml.parsers.expat import ExpatError

from .model import Note, Project, Region, Track, TICKS_PER_BEAT

NOTE_ORIGIN = 40 * TICKS_PER_BEAT
ARRANGE_ORIGIN = 36 * TICKS_PER_BEAT
MAGIC = bytes.fromhex("2347c0abcf0903000400000001000800")


class BandFormatError(ValueError):
    """A malformed or unsupported project, with a user-facing explanation."""


@dataclass(frozen=True)
class Chunk:
    tag: bytes
    version: int
    category: int
    object_id: int
    owner: int
    index: int
    data: bytes
    offset: int


def project_data_path(path: Path) -> Path:
    if path.is_file() and path.name == "projectData":
        return path
    if not path.is_dir() or path.suffix.lower() != ".band":
        raise BandFormatError(f"Expected a .band package directory or projectData: {path}")
    if (path / "projectData").is_file():
        return path / "projectData"
    # Several supplied fixtures have one extra package wrapper after unpacking.
    nested = path / path.name / "projectData"
    if nested.is_file():
        return nested
    raise BandFormatError(f"No projectData in {path}")


def read_song(path: Path) -> bytes:
    try:
        archive = plistlib.loads(project_data_path(path).read_bytes())
        objects = archive["$objects"]

        def resolve(ref):
            index = ref.data if isinstance(ref, plistlib.UID) else ref["CF$UID"]
            if not isinstance(index, int) or not 0 <= index < len(objects):
                raise BandFormatError("Invalid keyed-archive object reference")
            return objects[index]

        model = resolve(archive["$top"]["DfDocument logic model"])
        song = resolve(model["DfLogicModelLogicSong"])["NS.data"]
        if not isinstance(song, bytes):
            raise BandFormatError("Logic song is not binary data")
        return song
    except (plistlib.InvalidFileException, ExpatError, KeyError, IndexError, TypeError,
            OverflowError, struct.error) as exc:
        raise BandFormatError("Unsupported or damaged GarageBand keyed archive") from exc


def chunks(song: bytes) -> list[Chunk]:
    if len(song) < 24 or song[:16] != MAGIC:
        raise BandFormatError("Unsupported Logic song header; tested with GarageBand iOS 2.3.19")
    if struct.unpack_from("<Q", song, 16)[0] != len(song) - 24:
        raise BandFormatError("Logic song length does not match its header")
    result = []
    offset = 24
    while offset < len(song):
        if len(song) - offset < 36:
            raise BandFormatError(f"Truncated chunk header at {offset}")
        tag, version, category, object_id, owner, index, flags, size = struct.unpack_from(
            "<4sHiiii6sQ", song, offset
        )
        end = offset + 36 + size
        if end > len(song) or flags != bytes.fromhex("020000000200"):
            raise BandFormatError(f"Invalid chunk at {offset}")
        result.append(Chunk(tag, version, category, object_id, owner, index,
                            song[offset + 36:end], offset))
        offset = end
    return result


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _time(data: bytes, offset: int) -> float:
    fraction, ticks = struct.unpack_from("<Hi", data, offset)
    return ticks + fraction / 65536


def _string(data: bytes, offset: int) -> tuple[str, int]:
    size = struct.unpack_from("<H", data, offset)[0]
    end = offset + 2 + size
    if end > len(data):
        raise BandFormatError("Truncated string in Logic song")
    return data[offset + 2:end].decode("utf-8").rstrip("\0"), end + size % 2


def events(chunk: Chunk) -> list[bytes]:
    if chunk.version != 1 or len(chunk.data) % 16:
        raise BandFormatError(f"Unsupported event sequence at {chunk.offset}")
    result = []
    data = chunk.data
    offset = 0
    while offset < len(data):
        if data[offset] == 0xF1 and data[offset + 7] < 0x80:
            if offset != len(data) - 16:
                raise BandFormatError("Data after event sequence terminator")
            return result
        if data[offset + 7] >= 0x80:
            raise BandFormatError("Event sequence starts with an orphan extension")
        end = offset + 16
        while end < len(data) and data[end + 7] >= 0x80:
            end += 16
        result.append(data[offset:end])
        offset = end
    raise BandFormatError("Missing event sequence terminator")


def _notes(chunk: Chunk) -> tuple[list[Note], set[int]]:
    notes = []
    ignored = set()
    for event in events(chunk):
        if event[0] not in (0x90, 0x91):
            ignored.add(event[0])
            continue
        if len(event) < 32 or event[23] != 0x89 or event[15] != 1:
            raise BandFormatError(f"Unsupported note record at {chunk.offset}")
        pitch, velocity, channel = event[12], event[11], event[13]
        if pitch > 127 or velocity > 127 or channel > 15:
            raise BandFormatError("Invalid MIDI note values")
        duration = _time(event, 26)
        if duration < 0:
            raise BandFormatError("Negative note duration")
        if duration and velocity:
            notes.append(Note(_time(event, 2) - NOTE_ORIGIN, duration,
                              pitch, velocity, channel))
    return notes, ignored


def visible_notes(notes: list[Note], source_start: float, duration: float,
                  transpose: int = 0) -> list[Note]:
    result = []
    for note in notes:
        # Trimming hides note attacks outside the region, including their tails.
        local = note.start - source_start
        if local < 0 or local >= duration:
            continue
        pitch = note.pitch + transpose
        if not 0 <= pitch <= 127:
            raise BandFormatError("Region transposition exceeds the MIDI pitch range")
        result.append(Note(local, min(note.duration, duration - local),
                           pitch, note.velocity, note.channel))
    return sorted(result, key=lambda n: (n.start, n.pitch, n.channel))


def load_project(path: str | Path) -> Project:
    path = Path(path)
    try:
        return _decode(path, chunks(read_song(path)))
    except (struct.error, UnicodeDecodeError) as exc:
        raise BandFormatError("Truncated or unsupported musical data") from exc


def _decode(path: Path, records: list[Chunk]) -> Project:
    sequences = {}
    streams = {}
    instruments = {}
    lanes = {}
    for chunk in records:
        key = (chunk.category, chunk.object_id)
        target = sequences if chunk.tag == b"qeSM" else streams if chunk.tag == b"qSvE" else None
        if target is not None:
            if key in target:
                raise BandFormatError(f"Duplicate sequence {key}")
            target[key] = chunk
        if chunk.tag == b"ivnE":
            name, _ = _string(chunk.data, 158)
            instruments[chunk.object_id] = (name, chunk.data[155])
        if chunk.tag == b"karT" and key == (23, 4) and chunk.data:
            if chunk.version != 6 or len(chunk.data) != 58 or chunk.index < 0:
                raise BandFormatError("Unsupported arrangement track record")
            lanes[chunk.index + 1] = _u32(chunk.data, 8)

    if (23, 4) not in streams or (23, 4) not in sequences:
        raise BandFormatError("No supported arrangement root")
    tracks = {}
    for index, instrument in sorted(lanes.items()):
        if instrument not in instruments:
            raise BandFormatError("Missing arrangement instrument")
        name, kind = instruments[instrument]
        if kind == 9:
            tracks[index] = Track(index, name)

    tempo_events = events(streams[(3, 0)]) if (3, 0) in streams else []
    signature_events = events(streams[(1, 0)]) if (1, 0) in streams else []
    if len(tempo_events) != 1 or tempo_events[0][0] != 0x60 or len(tempo_events[0]) < 32:
        raise BandFormatError("Only a single constant project tempo is supported")
    bpm = _u32(tempo_events[0], 16) / 10000
    if not 4 <= bpm <= 999:
        raise BandFormatError("Invalid project tempo")
    if len(signature_events) != 2 or signature_events[0][:16] != bytes.fromhex(
        "30000000000000000000000204000000"
    ):
        raise BandFormatError("Only the experimentally verified 4/4 meter is supported")
    project = Project(project_data_path(path).parent.stem, list(tracks.values()),
                      round(60_000_000 / bpm), (4, 4))
    ignored = set()
    for event in events(streams[(23, 4)]):
        if event[0] != 0x20 or len(event) != 80 or event[23] != 0x89 or event[39] != 0x88:
            raise BandFormatError("Unsupported arrangement region record")
        lane = event[20]
        if lane not in lanes:
            raise BandFormatError("Region references a missing arrangement track")
        if lane not in tracks:
            continue
        ref = _u32(event, 32)
        key = (23, ref)
        if key not in sequences or key not in streams:
            raise BandFormatError(f"Missing MIDI region sequence {ref}")
        metadata = sequences[key]
        name, base = _string(metadata.data, 16)
        if metadata.version != 5 or len(metadata.data) - base != 279:
            raise BandFormatError(f"Unsupported region metadata: {name}")
        source_start = _time(metadata.data, base + 2)
        duration = _time(metadata.data, base + 58)
        start = _time(event, 2) - ARRANGE_ORIGIN
        if start < 0 or source_start < 0 or duration < 0:
            raise BandFormatError(f"Unsupported negative region boundary: {name}")
        if _u32(event, 16) != lanes[lane]:
            raise BandFormatError("Region instrument does not match its track")
        source_notes, other_events = _notes(streams[key])
        ignored.update(other_events)
        transpose = struct.unpack_from("<b", event, 53)[0]
        notes = visible_notes(source_notes, source_start, duration, transpose)
        tracks[lane].regions.append(Region(ref, name, start, duration, source_start,
                                          notes, len(source_notes)))
    for track in tracks.values():
        track.regions.sort(key=lambda r: (r.start, r.id))
    if ignored:
        project.warnings.append("Non-note sequence events are not exported (types " +
                                ", ".join(f"0x{x:02x}" for x in sorted(ignored)) + ").")
    return project

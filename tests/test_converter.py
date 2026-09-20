from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import plistlib
import struct

import mido
import pytest

from band2midi import BandFormatError, load_project
from band2midi.cli import main
from band2midi.export import export_project
from band2midi.model import Note
from band2midi.parser import chunks, visible_notes

FIXTURES = Path(__file__).resolve().parents[1] / ".experimental"


def fixture(name):
    matches = [p for p in FIXTURES.rglob("projectData") if p.parent.name == name + ".band"]
    if not matches:
        pytest.skip(f"Local experimental fixture unavailable: {name}")
    assert len(matches) == 1
    return matches[0]


def notes(project):
    return [n for t in project.tracks for r in t.regions for n in r.notes]


@pytest.mark.parametrize("tone,pitch", [("C3", 60), ("G3", 67), ("C4", 72)])
@pytest.mark.parametrize("position,velocity", [(1000, 1), (1000, 100), (1000, 127), (3000, 127)])
def test_one_note(tone, pitch, position, velocity):
    project = load_project(fixture(f"{tone}_b{position}_v{velocity}"))
    assert notes(project) == [Note((position - 1000) * 960 / 1000, 960, pitch, velocity)]
    assert project.tempo == 545455
    assert project.time_signature == (4, 4)


@pytest.mark.parametrize("name,pitches,velocities,durations", [
    ("4notes_diff_length", [72] * 4, [127] * 4, [240, 480, 720, 960]),
    ("4notes_diff_tone_C3_D3_E3_F3", [60, 62, 64, 65], [100] * 4, [960] * 4),
    ("4notes_diff_velocity", [60] * 4, [127, 100, 127, 100], [960] * 4),
])
def test_multiple_notes(name, pitches, velocities, durations):
    result = notes(load_project(fixture(name)))
    assert result == [Note(i * 960, length, pitch, velocity)
                      for i, (pitch, velocity, length) in enumerate(zip(pitches, velocities, durations))]


def test_twinkle():
    result = notes(load_project(fixture("twinkle_twinkle_little_star")))
    pitches = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60]
    beats = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]
    assert result == [Note(beat * 960, 960, pitch, 100) for beat, pitch in zip(beats, pitches)]


def test_all_128_pitches():
    assert notes(load_project(fixture("all_notes_sequence_c-2_g8"))) == [
        Note(pitch * 120, 120, pitch, 100) for pitch in range(128)
    ]


def test_ampoule_hidden_notes_and_track_ownership():
    project = load_project(fixture("Inside the Ampoule"))
    assert [t.name for t in project.tracks] == ["Track1", "Track2", "Track3", "Track4"]
    assert [len(t.regions) for t in project.tracks] == [10, 4, 11, 7]
    assert [sum(len(r.notes) for r in t.regions) for t in project.tracks] == [371, 83, 227, 200]
    empty = []
    for track in project.tracks:
        for region in track.regions:
            assert region.name.startswith(f"T{track.index}-")
            if "Empty" in region.name:
                empty.append(region)
                assert region.source_note_count > 0
                assert region.notes == []
            else:
                assert region.notes
            assert all(0 <= n.start < n.start + n.duration <= region.duration for n in region.notes)
    assert len(empty) == 11


def test_trim_excludes_hidden_attacks_and_clips_note_end():
    source = [Note(0, 200, 60, 100), Note(100, 200, 62, 100), Note(200, 50, 64, 100)]
    assert visible_notes(source, 100, 100) == [Note(0, 100, 62, 100)]
    assert visible_notes(source, 100, 100, -12) == [Note(0, 100, 50, 100)]


def midi_notes(path):
    midi = mido.MidiFile(path, charset="utf-8")
    result = []
    for track in midi.tracks:
        active = {}
        tick = 0
        for message in track:
            assert message.time >= 0
            tick += message.time
            if message.type == "note_on" and message.velocity:
                active.setdefault((message.channel, message.note), []).append((tick, message.velocity))
            elif message.type == "note_off" or (message.type == "note_on" and not message.velocity):
                key = (message.channel, message.note)
                assert key in active and active[key], "Note-off without note-on"
                start, velocity = active[key].pop(0)
                result.append((start, tick - start, message.note, velocity, message.channel))
        assert not any(active.values()), "Hanging note"
    assert midi.ticks_per_beat == 960
    return midi, result


@pytest.mark.parametrize("mode,count", [("project", 1), ("tracks", 4), ("regions", 21)])
def test_all_export_modes_roundtrip(tmp_path, mode, count):
    project = load_project(fixture("Inside the Ampoule"))
    paths = export_project(project, tmp_path, mode, timeline=True)
    assert len(paths) == count
    recovered = []
    for path in paths:
        midi, parsed = midi_notes(path)
        assert midi.tracks[0][1].tempo == project.tempo
        assert midi.tracks[0][2].numerator == 4
        recovered.extend(parsed)
    expected = []
    for track in project.tracks:
        for region in track.regions:
            for note in region.notes:
                start = round(region.start + note.start)
                stop = round(region.start + note.start + note.duration)
                if stop > start:
                    expected.append((start, stop - start, note.pitch, note.velocity, note.channel))
    assert Counter(recovered) == Counter(expected)
    assert len(recovered) == 881


def test_region_export_rebases_to_region_boundary(tmp_path):
    project = load_project(fixture("C3_b3000_v127"))
    project.tracks[0].regions[0].start = 8000
    paths = export_project(project, tmp_path, "regions")
    _, result = midi_notes(paths[0])
    assert result == [(1920, 960, 60, 127, 0)]


def test_unicode_names_and_note_off_order(tmp_path):
    project = load_project(fixture("C3_b1000_v127"))
    project.tracks[0].name = "Piano \u65e5\u672c"
    project.tracks[0].regions[0].notes = [Note(0, 960, 60, 100), Note(960, 960, 60, 100)]
    midi, recovered = midi_notes(export_project(project, tmp_path)[0])
    assert midi.tracks[1].name == project.tracks[0].name
    assert [n[:2] for n in recovered] == [(0, 960), (960, 960)]
    messages = [m.type for m in midi.tracks[1] if m.type in {"note_on", "note_off"}]
    assert messages == ["note_on", "note_off", "note_on", "note_off"]


def test_conflict_is_detected_before_any_output(tmp_path):
    project = load_project(fixture("Inside the Ampoule"))
    conflict = tmp_path / "04_Track4.mid"
    conflict.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        export_project(project, tmp_path, "tracks")
    assert list(tmp_path.iterdir()) == [conflict]
    assert conflict.read_bytes() == b"existing"
    assert len(export_project(project, tmp_path, "tracks", overwrite=True)) == 4


def test_package_wrapper_and_binary_plist(tmp_path):
    original = fixture("C3_b1000_v127")
    wrapper = tmp_path / "Example.BAND"
    nested = wrapper / wrapper.name
    nested.mkdir(parents=True)
    archive = plistlib.loads(original.read_bytes())

    def binary_refs(value):
        if isinstance(value, dict):
            if set(value) == {"CF$UID"}:
                return plistlib.UID(value["CF$UID"])
            return {k: binary_refs(v) for k, v in value.items()}
        if isinstance(value, list):
            return [binary_refs(v) for v in value]
        return value

    (nested / "projectData").write_bytes(plistlib.dumps(binary_refs(archive), fmt=plistlib.FMT_BINARY))
    assert notes(load_project(wrapper)) == notes(load_project(original))


def rewrite_song(tmp_path, mutate):
    archive = plistlib.loads(fixture("C3_b1000_v127").read_bytes())
    song = bytearray(archive["$objects"][7]["NS.data"])
    mutate(song)
    archive["$objects"][7]["NS.data"] = bytes(song)
    path = tmp_path / "projectData"
    path.write_bytes(plistlib.dumps(archive))
    return path


def test_unreferenced_source_notes_are_not_exported(tmp_path):
    def mutate(song):
        for chunk in chunks(bytes(song)):
            if (chunk.tag, chunk.category, chunk.object_id) == (b"qSvE", 23, 4):
                # Leave the complete source sequence present, remove its arrangement event.
                payload = chunk.data[-16:]
                song[chunk.offset + 36:chunk.offset + 36 + len(chunk.data)] = payload
                struct.pack_into("<Q", song, chunk.offset + 28, len(payload))
                struct.pack_into("<Q", song, 16, len(song) - 24)
                return
    assert notes(load_project(rewrite_song(tmp_path, mutate))) == []


def test_audio_track_is_excluded(tmp_path):
    def mutate(song):
        for chunk in chunks(bytes(song)):
            if chunk.tag == b"ivnE" and chunk.object_id == 100:
                song[chunk.offset + 36 + 155] = 8
    assert load_project(rewrite_song(tmp_path, mutate)).tracks == []


@pytest.mark.parametrize("mutation", [
    lambda b: b.__setitem__(0, 0),
    lambda b: b.pop(),
    lambda b: struct.pack_into("<Q", b, 24 + 28, len(b) * 2),
])
def test_corrupt_binary_rejected(tmp_path, mutation):
    with pytest.raises(BandFormatError):
        load_project(rewrite_song(tmp_path, mutation))


def test_cli_inspect_and_errors(tmp_path, capsys):
    assert main([str(fixture("C3_b1000_v127")), "--inspect"]) == 0
    assert json.loads(capsys.readouterr().out)["tracks"][0]["regions"][0]["notes"][0]["pitch"] == 60
    assert main([str(tmp_path / "missing.band")]) == 1
    assert "Traceback" not in capsys.readouterr().err
    malformed = tmp_path / "projectData"
    malformed.write_bytes(b"not a plist")
    assert main([str(malformed)]) == 1


def test_empty_project_creates_no_outputs(tmp_path):
    project = deepcopy(load_project(fixture("C3_b1000_v127")))
    project.tracks[0].regions[0].notes = []
    with pytest.raises(ValueError, match="No visible MIDI"):
        export_project(project, tmp_path / "absent")
    assert not (tmp_path / "absent").exists()

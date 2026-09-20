"""Write standard MIDI through Mido, retaining arrangement timing."""

from io import BytesIO
from pathlib import Path
import re

import mido

from .model import Project, Region, Track, TICKS_PER_BEAT


def _name(value: str) -> str:
    return re.sub(r"[^\w .-]+", "_", value).strip(" .")[:80] or "untitled"


def _midi(project: Project, tracks: list[Track], region: Region | None = None,
          timeline: bool = False) -> bytes:
    midi = mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT, charset="utf-8")
    conductor = mido.MidiTrack([
        mido.MetaMessage("track_name", name=project.name),
        mido.MetaMessage("set_tempo", tempo=project.tempo),
        mido.MetaMessage("time_signature", numerator=project.time_signature[0],
                         denominator=project.time_signature[1]),
    ])
    midi.tracks.append(conductor)
    for track in tracks:
        output = mido.MidiTrack([mido.MetaMessage("track_name", name=track.name)])
        pending = []
        end = 0
        for item in ([region] if region else track.regions):
            origin = item.start if region is None or timeline else 0
            end = max(end, round(origin + item.duration))
            pending.append((round(origin), 0, mido.MetaMessage("marker", text=item.name)))
            for note in item.notes:
                start = round(origin + note.start)
                stop = min(round(origin + item.duration), round(origin + note.start + note.duration))
                if stop <= start:
                    continue
                pending.append((start, 2, mido.Message("note_on", note=note.pitch,
                    velocity=note.velocity, channel=note.channel)))
                pending.append((stop, 1, mido.Message("note_off", note=note.pitch,
                    velocity=0, channel=note.channel)))
        previous = 0
        for tick, _, message in sorted(pending, key=lambda x: (x[0], x[1])):
            output.append(message.copy(time=tick - previous))
            previous = tick
        output.append(mido.MetaMessage("end_of_track", time=max(0, end - previous)))
        midi.tracks.append(output)
    buffer = BytesIO()
    midi.save(file=buffer)
    return buffer.getvalue()


def export_project(project: Project, output: str | Path, mode: str = "project",
                   *, timeline: bool = False, overwrite: bool = False) -> list[Path]:
    if mode not in {"project", "tracks", "regions"}:
        raise ValueError(f"Unknown export mode: {mode}")
    if not any(r.notes for t in project.tracks for r in t.regions):
        raise ValueError("No visible MIDI notes to export")
    output = Path(output)
    planned = []
    if mode == "project":
        target = output if output.suffix.lower() == ".mid" else output / f"{_name(project.name)}.mid"
        planned.append((target, _midi(project, project.tracks)))
    else:
        if output.suffix.lower() == ".mid":
            raise ValueError("Track and region modes require an output directory")
        for track in project.tracks:
            prefix = f"{track.index:02d}_{_name(track.name)}"
            if mode == "tracks":
                planned.append((output / f"{prefix}.mid", _midi(project, [track])))
            else:
                for number, region in enumerate(track.regions, 1):
                    if region.notes:
                        target = output / f"{prefix}_{number:03d}_{_name(region.name)}.mid"
                        planned.append((target, _midi(project, [track], region, timeline)))
    # Validate the complete plan before writing any output.
    for target, _ in planned:
        if target.exists() and not overwrite:
            raise FileExistsError(f"Output exists: {target}; use --overwrite to replace it")
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"Output is not a regular file: {target}")
    for target, data in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb" if overwrite else "xb") as stream:
            stream.write(data)
    return [target for target, _ in planned]

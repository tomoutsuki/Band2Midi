"""Command-line entry point."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .export import export_project
from .parser import BandFormatError, load_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract visible MIDI notes from a GarageBand .band package.")
    parser.add_argument("project", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("midi-output"))
    parser.add_argument("--mode", choices=["project", "tracks", "regions"], default="project")
    parser.add_argument("--region-timeline", action="store_true",
                        help="Keep project positions in region exports (default: region starts at zero)")
    parser.add_argument("--inspect", action="store_true", help="Print decoded musical data as JSON without exporting")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.region_timeline and args.mode != "regions":
        parser.error("--region-timeline requires --mode regions")
    try:
        project = load_project(args.project)
        if args.inspect:
            print(json.dumps(asdict(project), indent=2, ensure_ascii=False))
            return 0
        for warning in project.warnings:
            print(f"Warning: {warning}", file=sys.stderr)
        paths = export_project(project, args.output, args.mode,
                               timeline=args.region_timeline, overwrite=args.overwrite)
        for path in paths:
            print(path)
        count = sum(len(r.notes) for t in project.tracks for r in t.regions)
        print(f"Exported {count} notes to {len(paths)} MIDI file(s).", file=sys.stderr)
        return 0
    except (BandFormatError, OSError, ValueError) as exc:
        print(f"band2midi: {exc}", file=sys.stderr)
        return 1

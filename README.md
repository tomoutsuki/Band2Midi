# Band2Midi

**Band2Midi** is an independent Python tool for extracting MIDI information from Apple GarageBand `.band` project files and converting it into standard MIDI (`.mid`) files.

The project is intended to improve **interoperability and portability of user-created musical projects**, allowing MIDI information contained within GarageBand projects to be extracted and used by other music-production software.

> **Band2Midi is an independent, community-developed project and is not affiliated with, endorsed by, or sponsored by Apple Inc. or GarageBand.**

## What does Band2Midi do?

### Install and run

Requires Python 3.10 or newer. From the repository root:

```bash
python -m pip install .
band2midi "My Song.band" -o song.mid
band2midi "My Song.band" --mode tracks -o midi-tracks
band2midi "My Song.band" --mode regions -o midi-regions
```

Alternatively, use `uv run band2midi ...`. The module entry point is
`python -m band2midi ...`.

The default produces one MIDI file containing all MIDI tracks. Track mode
produces one file per software-instrument arrangement track. Region mode produces
one file per region with visible notes; trimmed-away notes and empty regions are
excluded. Project and track modes retain the original timeline, including rests.
Region files start at the region boundary; `--region-timeline` retains project
positions instead. Existing files are protected unless `--overwrite` is supplied.

```bash
band2midi "My Song.band" --inspect
uv run --extra test pytest
```

`--inspect` reports tracks, regions, trim windows, notes, and warnings as JSON
without writing MIDI. Only `projectData` is read, never package media files.

**Current support:** the 18 supplied GarageBand iOS 2.3.19 fixtures, including
four-track Inside the Ampoule. Exports preserve notes, region boundaries, names,
constant tempo, and 4/4 meter. Controller/sustain events, pitch bend, automation,
loop repetition, stretching, and Smart/Drummer generation are not implemented.
Other GarageBand versions are not verified. See [format analysis](docs/format.md)
for decoded fields, experimental evidence, and limitations. Fixture tests skip
when the local `.experimental` dataset is unavailable.

GarageBand project files do not simply contain MIDI data as standalone `.mid` files. Relevant musical information is represented within GarageBand's project data structures and binary representations.

Band2Midi independently analyzes those structures and translates the relevant musical information into standard MIDI data.

Conceptually:

```text
GarageBand project
        │
        ▼
   Band2Midi
        │
        ├── MIDI notes
        ├── Note positions
        ├── Durations
        ├── Pitch
        ├── Velocity
        └── Other supported MIDI information
        │
        ▼
   Standard MIDI (.mid)
```

The resulting MIDI file is an independently generated output and does not contain GarageBand software.

## Independent implementation

Band2Midi is implemented independently and does not contain or depend upon:

* GarageBand source code
* Apple source code
* GarageBand executable binaries
* Apple proprietary libraries or frameworks
* Apple's proprietary audio assets
* Apple's instruments or sound libraries

The project does not modify, patch, or redistribute GarageBand.

The parser is based on analysis of project files generated during development and controlled experiments. Test projects can be created with known musical contents, allowing individual parameters such as pitch, duration, velocity, and position to be compared between files.

For example, a controlled experiment can consist of:

```text
Project A:
    C4
    velocity = 64
    duration = 1 beat

Project B:
    C4
    velocity = 100
    duration = 1 beat
```

By comparing the resulting project data, the implementation can identify how the corresponding information is represented and independently reproduce the necessary parsing logic.

No Apple implementation or source code is required for the parser.

## Interoperability

The primary purpose of Band2Midi is interoperability.

Musical information created by users should not necessarily be confined to the application that originally stored it. Band2Midi aims to provide an independent way of transferring MIDI information from GarageBand projects into an open, widely supported format.

The project may eventually support additional interoperable project representations, such as `.dawproject`, where technically feasible.

Any such conversion will be performed by Band2Midi's own implementation rather than by incorporating GarageBand or Apple software.

## Scope

Band2Midi is intended to process project files that the user is legitimately able to access.

The project does **not** attempt to:

* bypass DRM or technological protection measures;
* defeat authentication or licensing mechanisms;
* obtain unauthorized access to GarageBand projects;
* extract or redistribute Apple's proprietary software;
* extract or redistribute Apple's proprietary audio libraries or sound assets;
* provide unauthorized copies of GarageBand;
* reproduce GarageBand itself.

Band2Midi operates on project data supplied by the user.

## Test methodology

The format analysis used by this project is based on controlled, experimentally generated project files.

Development may involve creating minimal projects specifically for testing, such as projects containing:

* a single MIDI note;
* multiple notes;
* different pitches;
* different velocities;
* different durations;
* different positions;
* different combinations of MIDI properties.

The resulting files can then be compared to identify relationships between known musical information and its binary representation.

This approach allows the parser to be implemented independently from GarageBand's own software implementation.

## Legal and interoperability considerations

Band2Midi is provided as an independent interoperability project.

The project does not claim ownership of Apple's software, trademarks, or proprietary assets. Apple, GarageBand, and related trademarks belong to their respective owners.

The project's implementation is original to this project and is intended to process data supplied by the user.

Software reverse engineering and interoperability can involve different legal considerations depending on jurisdiction, applicable license agreements, copyright law, technological protection measures, and the particular methods used. Nothing in this repository should be interpreted as legal advice or as a representation that every possible use of the software is legally permitted.

In particular, Band2Midi intentionally avoids distributing Apple software, Apple source code, Apple libraries, or Apple proprietary media.

Users are responsible for ensuring that the project files and other material they process are lawfully accessible to them and that their use of the resulting files complies with applicable law and the terms applicable to their software and content.

## Project status

Band2Midi is an ongoing reverse-engineering and interoperability project.

Support for GarageBand project structures may be incomplete, and some GarageBand-specific features may not have direct equivalents in standard MIDI.

As development progresses, additional project structures and musical information may be supported.

## Disclaimer

Band2Midi is provided on an **"AS IS"** basis, without warranties of any kind.

The developers are not affiliated with Apple Inc. or GarageBand.

Apple, GarageBand, and related names and trademarks are the property of their respective owners.

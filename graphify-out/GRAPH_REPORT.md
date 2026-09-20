# Graph Report - Band2Midi  (2026-09-20)

## Corpus Check
- 21 files · ~15,493 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 162 nodes · 294 edges · 17 communities (12 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `352bab03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Band2Midi (ongoing Python interoperability project)
- test_converter.py
- What You Must Do When Invoked
- parser.py
- cli.py
- graphify reference: extra exports and benchmark
- chunks
- graphify reference: query, path, explain
- Experimentally Decoded Format
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md
- band2midi

## God Nodes (most connected - your core abstractions)
1. `load_project()` - 25 edges
2. `BandFormatError` - 17 edges
3. `_decode()` - 15 edges
4. `fixture()` - 14 edges
5. `export_project()` - 13 edges
6. `What You Must Do When Invoked` - 12 edges
7. `Note` - 11 edges
8. `/graphify` - 10 edges
9. `chunks()` - 9 edges
10. `graphify reference: extra exports and benchmark` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_multiple_notes()` --uses--> `Note`  [INFERRED]
  tests/test_converter.py → band2midi/model.py
- `test_one_note()` --uses--> `Note`  [INFERRED]
  tests/test_converter.py → band2midi/model.py
- `mutate()` --calls--> `chunks()`  [EXTRACTED]
  tests/test_converter.py → band2midi/parser.py
- `test_trim_excludes_hidden_attacks_and_clips_note_end()` --calls--> `visible_notes()`  [EXTRACTED]
  tests/test_converter.py → band2midi/parser.py
- `test_audio_track_is_excluded()` --calls--> `load_project()`  [EXTRACTED]
  tests/test_converter.py → band2midi/parser.py

## Import Cycles
- None detected.

## Communities (17 total, 5 thin omitted)

### Community 0 - "Band2Midi (ongoing Python interoperability project)"
Cohesion: 0.17
Nodes (16): Processing legitimately accessible user-supplied project data, Band2Midi (ongoing Python interoperability project), GarageBand .band project data, Binary representation of musical information, Controlled project-file experiments, .dawproject (possible future output representation), Apple GarageBand, Independent implementation (+8 more)

### Community 1 - "test_converter.py"
Cohesion: 0.19
Nodes (28): band2midi, main(), export_project(), Path, Note, load_project(), collections, copy (+20 more)

### Community 2 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 3 - "parser.py"
Cohesion: 0.19
Nodes (20): GarageBand project interoperability through independently decoded MIDI notes., BandFormatError, Chunk, _decode(), events(), _notes(), project_data_path(), Path (+12 more)

### Community 4 - "cli.py"
Cohesion: 0.14
Nodes (16): argparse, Command-line entry point., _midi(), _name(), Write standard MIDI through Mido, retaining arrangement timing., Project, Musical data in project ticks (960 ticks per quarter note)., Region (+8 more)

### Community 5 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 6 - "chunks"
Cohesion: 0.67
Nodes (6): chunks(), rewrite_song(), test_audio_track_is_excluded(), mutate(), test_unreferenced_source_notes_are_not_exported(), mutate()

### Community 7 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 8 - "Experimentally Decoded Format"
Cohesion: 0.33
Nodes (5): Archive and Chunks, Experimentally Decoded Format, Notes and Timing, Tempo and Boundaries of Support, Tracks and Region Windows

### Community 9 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 10 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 11 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **50 isolated node(s):** `band2midi`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 80 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_project()` connect `test_converter.py` to `parser.py`, `cli.py`, `chunks`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `BandFormatError` connect `parser.py` to `test_converter.py`, `cli.py`, `chunks`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `band2midi`, `Usage`, `What graphify is for` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `What You Must Do When Invoked` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14210526315789473 - nodes in this community are weakly interconnected._
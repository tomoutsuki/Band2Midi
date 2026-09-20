# Graph Report - Band2Midi  (2026-09-20)

## Corpus Check
- Corpus is ~814 words - fits in a single context window. You may not need a graph.

## Summary
- 16 nodes · 21 edges · 3 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: unavailable for host-agent extraction; zero values in cost.json are placeholders, not measured usage.

## Community Hubs (Navigation)
- MIDI Parameters and Experiments
- Project Scope and Interoperability
- GarageBand Data Parsing

## God Nodes (most connected - your core abstractions)
1. `Band2Midi (ongoing Python interoperability project)` - 7 edges
2. `Standard MIDI .mid output` - 6 edges
3. `Controlled project-file experiments` - 6 edges
4. `GarageBand .band project data` - 3 edges
5. `Independent project-data parser` - 3 edges
6. `Independent implementation` - 2 edges
7. `Binary representation of musical information` - 2 edges
8. `MIDI note positions` - 2 edges
9. `MIDI note durations` - 2 edges
10. `MIDI note pitch` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Band2Midi (ongoing Python interoperability project)` --references--> `GarageBand .band project data`  [EXTRACTED]
  README.md → README.md  _Bridges community 1 → community 2_
- `Band2Midi (ongoing Python interoperability project)` --implements--> `Independent implementation`  [EXTRACTED]
  README.md → README.md  _Bridges community 1 → community 0_
- `Independent project-data parser` --implements--> `Controlled project-file experiments`  [EXTRACTED]
  README.md → README.md  _Bridges community 2 → community 0_

## Communities (3 total, 0 thin omitted)

### Community 0 - "MIDI Parameters and Experiments"
Cohesion: 0.36
Nodes (8): Controlled project-file experiments, Independent implementation, MIDI notes, MIDI note durations, MIDI note pitch, MIDI note positions, MIDI note velocity, Standard MIDI .mid output

### Community 1 - "Project Scope and Interoperability"
Cohesion: 0.50
Nodes (4): Processing legitimately accessible user-supplied project data, Band2Midi (ongoing Python interoperability project), .dawproject (possible future output representation), Musical-project interoperability and portability

### Community 2 - "GarageBand Data Parsing"
Cohesion: 0.50
Nodes (4): GarageBand .band project data, Binary representation of musical information, Apple GarageBand, Independent project-data parser

## Knowledge Gaps
- **3 isolated node(s):** `Apple GarageBand`, `MIDI notes`, `.dawproject (possible future output representation)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 5 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Band2Midi (ongoing Python interoperability project)` connect `Project Scope and Interoperability` to `MIDI Parameters and Experiments`, `GarageBand Data Parsing`?**
  _High betweenness centrality (0.595) - this node is a cross-community bridge._
- **Why does `Standard MIDI .mid output` connect `MIDI Parameters and Experiments` to `Project Scope and Interoperability`?**
  _High betweenness centrality (0.390) - this node is a cross-community bridge._
- **Why does `GarageBand .band project data` connect `GarageBand Data Parsing` to `Project Scope and Interoperability`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **What connects `Apple GarageBand`, `MIDI notes`, `.dawproject (possible future output representation)` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
## Extraction Audit
- Scope: README.md only (814 words); .experimental/ was excluded by .gitignore. No code files were detected.
- Graph health warning: the default undirected graph merged one pair of opposite-direction relationships between Band2Midi and interoperability (22 extracted edges became 21 graph edges). The original directed relationships and provenance are retained in extraction.json.
- No dangling endpoints, missing endpoints, or self-loops were found.

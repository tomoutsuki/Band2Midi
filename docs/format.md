# Experimentally Decoded Format

This is an independent analysis of the 18 projectData fixtures in `.experimental`.
All identify GarageBand iOS 2.3.19. These observations are not a specification of
every GarageBand or Logic format. No application executable or media asset was
used. The parser reads only projectData.

## Archive and Chunks

`plistlib` reads the XML NSKeyedArchiver archive. Follow the `$top` key
`DfDocument logic model`, then `DfLogicModelLogicSong`, then `NS.data`.
Resolve `CF$UID` references through `$objects`; object indices are not fixed.
The parser also accepts equivalent binary plists with `plistlib.UID` references.

The song has a 24-byte header. Its first 16 bytes in these fixtures are
`2347c0abcf0903000400000001000800`. The little-endian uint64 at byte 16 is
the remaining file length. Chunks follow sequentially; no byte-pattern scanning
is needed, and embedded plugin data cannot be mistaken for musical records.

| Chunk Header Offset | Representation | Meaning |
| --- | --- | --- |
| 0 | 4 bytes | Tag, reversed on disk (e.g. `qSvE` / EvSq) |
| 4 | uint16 | Chunk version |
| 6 | int32 | Object category |
| 10 | int32 | Object reference |
| 14 | int32 | Owner/reference metadata |
| 18 | int32 | Index, including arrangement lane index |
| 22 | 6 bytes | `020000000200` in the fixtures |
| 28 | uint64 | Payload length, excluding the 36-byte header |

Relevant tags are `qeSM` (sequence metadata), `qSvE` (events), `karT`
(track records), and `ivnE` (instrument metadata). The arrangement lives in
category 23, reference 4. Other sequences include TRASH, automation, alternatives,
and unreferenced source objects. Merely finding notes in them does not authorize
their inclusion in the arrangement.

## Notes and Timing

EvSq records consist of 16-byte cells. A primary cell has byte 7 below 0x80;
following cells with byte 7 at or above 0x80 are extensions of that record.
`f1` terminates the sequence. Both primary types `90` and `91` represent notes;
the low bit here must not be interpreted as a MIDI channel.

| Note Record Offset | Meaning |
| --- | --- |
| 2 | uint16 fractional part of onset, in 1/65536 tick |
| 4 | int32 onset ticks |
| 11 | MIDI velocity |
| 12 | MIDI pitch |
| 13 | Channel (zero in the controlled fixtures) |
| 15 | Note discriminator, 1 |
| 23 | Duration extension discriminator, 0x89 |
| 26 | uint16 fractional duration |
| 28 | int32 duration ticks |

The experiments establish 960 ticks per quarter note. The note time origin in
this layout is 38400 ticks (40 beats). The arrangement origin is 34560 ticks
(36 beats). These constants are specific to the supported layout, not inferred
from the first note, so intentional leading rests survive.

The C3, G3, C4 fixtures decode to pitches 60, 67, 72, respectively. Octave labels
vary across DAWs; the chromatic fixture confirms actual MIDI numbers 0 through
127. A `b3000` note starts 1920 ticks later than its `b1000` counterpart. The four
lengths decode to 240, 480, 720, and 960 ticks. Velocity variants decode to 1,
100, and 127. Additional bytes in the velocity field change too; only the
validated seven-bit MIDI value is exported.

## Tracks and Region Windows

Root `karT` records contain an instrument reference at payload byte 8; their
header index is the zero-based lane order. `ivnE` has a length-prefixed UTF-8 name
at payload byte 158. Byte 155 equals 9 for the software-instrument channels in
these fixtures. Output tracks come from arrangement lanes, not all instrument
objects: the real project has unused instrument objects that must be excluded.

Root region events are 80 bytes. Their onset is at byte 2, instrument reference
at 16, one-based lane at 20, and region sequence reference at 32. Byte 53 is
treated as signed semitone transposition (the real fixture includes -12).
Transposition is inferred from the real fixture; a controlled transpose
experiment is still needed. Other region processing flags are not interpreted.

Sequence metadata version 5 has a length-prefixed name at byte 16, padded to an
even byte count. Let B be the byte immediately after that padded name. The
remaining payload is 279 bytes. Each time is a uint16 fractional part followed
by int32 ticks:

| Offset From B | Meaning |
| --- | --- |
| 2 | Source window start, relative to the note origin |
| 58 | Visible duration |
| 222 | Stored arrangement offset, corroborating root event timing |

For a source note N, the visible local onset is
`N.onset - 38400 - source_window_start`. Export only attacks in
`[0, visible_duration)`, and shorten note duration at the right boundary.
Notes whose attacks precede a left trim are excluded, including their tails.
Add the root event's onset minus 34560 for project and track export.
Region exports start at zero by default, preserving silence inside the region.

This produces four active tracks, 32 region placements, and 21 nonempty regions
in Inside the Ampoule. All 11 regions labeled Empty contain source notes but
zero visible notes. Track note counts are 371, 83, 227, and 200 (881 total).
These counts are regression observations of the decoded windows, not an
independent audio-render comparison. Labels are used only as test expectations;
the parser never filters using region names.

## Tempo and Boundaries of Support

The category 3/reference 0 event stream contains constant tempo: event 0x60,
uint32 at byte 16, BPM multiplied by 10000. Controlled fixtures use 110 BPM;
Inside the Ampoule uses 123 BPM. The validated category 1/reference 0 meter
record identifies 4/4. Other meters and tempo maps currently raise an error.

The converter exports note attacks, durations, pitches, velocities, inferred
region transposition, track names, region markers, constant tempo, and 4/4 meter.
Mido handles Standard MIDI File serialization and delta times:
<https://mido.readthedocs.io/en/stable/files/midi.html>.
Fractional project ticks round to the nearest MIDI tick, with sub-tick notes
that collapse to zero duration omitted. Note-offs precede simultaneous note-ons.

Controller events (including sustain), pitch bend, automation, quantization,
loop repetition, time stretching, mixer processing, and Smart/Drummer generation
are not implemented. Non-note primary events in referenced sequences produce a
warning; they are never silently exported as notes. There are no controlled
fixtures for loops, stretch, changing tempo/meter, alternate channels, audio
regions, or Smart regions. Their complete playback behavior is not claimed.
Audio payloads, instrument sounds, and Apple Loops assets are never opened or
copied. Additional format versions require new fixtures before support can be
claimed; the reader validates known headers, record lengths, and references.

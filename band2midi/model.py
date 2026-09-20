"""Musical data in project ticks (960 ticks per quarter note)."""

from dataclasses import dataclass, field

TICKS_PER_BEAT = 960


@dataclass(frozen=True)
class Note:
    start: float
    duration: float
    pitch: int
    velocity: int
    channel: int = 0


@dataclass
class Region:
    id: int
    name: str
    start: float
    duration: float
    source_start: float
    notes: list[Note]
    source_note_count: int


@dataclass
class Track:
    index: int
    name: str
    regions: list[Region] = field(default_factory=list)


@dataclass
class Project:
    name: str
    tracks: list[Track]
    tempo: int
    time_signature: tuple[int, int]
    warnings: list[str] = field(default_factory=list)

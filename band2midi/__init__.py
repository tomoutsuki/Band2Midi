"""GarageBand project interoperability through independently decoded MIDI notes."""

from .parser import BandFormatError, load_project

__all__ = ["BandFormatError", "load_project"]


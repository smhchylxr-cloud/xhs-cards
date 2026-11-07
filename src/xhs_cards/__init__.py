"""xhs-cards — render Xiaohongshu-style card decks from a JSON spec."""

__version__ = "0.1.0"

from .render import build, load_spec  # noqa: F401
from .theme import PRESETS, Theme  # noqa: F401

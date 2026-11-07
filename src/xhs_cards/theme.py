"""Value objects and colour presets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Colour tokens for one poster deck."""

    name: str
    paper: tuple
    ink: tuple
    muted: tuple
    sub: tuple
    rule: tuple
    accent: tuple


IKB = Theme(
    name="ikb",
    paper=(244, 241, 234),
    ink=(11, 11, 12),
    muted=(122, 117, 108),
    sub=(74, 69, 61),
    rule=(201, 196, 184),
    accent=(0, 47, 167),
)

INK = Theme(
    name="ink",
    paper=(250, 249, 246),
    ink=(16, 16, 16),
    muted=(120, 118, 112),
    sub=(70, 68, 64),
    rule=(206, 202, 194),
    accent=(16, 16, 16),
)

LEMON = Theme(
    name="lemon",
    paper=(247, 245, 236),
    ink=(18, 18, 16),
    muted=(124, 120, 108),
    sub=(76, 72, 60),
    rule=(208, 202, 186),
    accent=(196, 146, 0),
)

PRESETS = {t.name: t for t in (IKB, INK, LEMON)}

"""Find a usable CJK font on this machine.

Order matters: the first existing path wins. Override with XHS_FONT_DIR
or with the explicit XHS_FONT_REGULAR / XHS_FONT_BOLD / XHS_FONT_MONO vars.
"""

import os
import sys

from PIL import ImageFont

_WIN = r"C:\Windows\Fonts"
_MAC = "/System/Library/Fonts"
_MAC_SUP = "/System/Library/Fonts/Supplemental"
_LINUX = "/usr/share/fonts"

CANDIDATES = {
    "regular": [
        os.path.join(_WIN, "msyh.ttc"),
        os.path.join(_WIN, "msyhl.ttc"),
        os.path.join(_WIN, "simhei.ttf"),
        os.path.join(_MAC, "PingFang.ttc"),
        os.path.join(_MAC_SUP, "Songti.ttc"),
        os.path.join(_LINUX, "opentype/noto/NotoSansCJK-Regular.ttc"),
        os.path.join(_LINUX, "truetype/noto/NotoSansCJK-Regular.ttc"),
        os.path.join(_LINUX, "truetype/wqy/wqy-zenhei.ttc"),
    ],
    "bold": [
        os.path.join(_WIN, "msyhbd.ttc"),
        os.path.join(_WIN, "simhei.ttf"),
        os.path.join(_MAC, "PingFang.ttc"),
        os.path.join(_LINUX, "opentype/noto/NotoSansCJK-Bold.ttc"),
        os.path.join(_LINUX, "truetype/noto/NotoSansCJK-Bold.ttc"),
    ],
    "mono": [
        os.path.join(_WIN, "consola.ttf"),
        os.path.join(_MAC, "Menlo.ttc"),
        os.path.join(_LINUX, "truetype/dejavu/DejaVuSansMono.ttf"),
    ],
    "hand": [
        os.path.join(_WIN, "simkai.ttf"),
        os.path.join(_WIN, "STKAITI.TTF"),
        os.path.join(_MAC_SUP, "Kaiti.ttc"),
        os.path.join(_LINUX, "opentype/noto/NotoSerifCJK-Regular.ttc"),
        os.path.join(_LINUX, "truetype/arphic/ukai.ttc"),
    ],
}

_cache = {}


def _env(name):
    return os.environ.get(name) or ""


def find(kind):
    """Return the path of an existing font file for kind in {regular,bold,mono}."""
    if kind in _cache:
        return _cache[kind]

    override = _env("XHS_FONT_" + kind.upper())
    if override and os.path.exists(override):
        _cache[kind] = override
        return override

    search = list(CANDIDATES.get(kind, []))
    font_dir = _env("XHS_FONT_DIR")
    if font_dir:
        search = [os.path.join(font_dir, os.path.basename(p)) for p in search] + search

    for path in search:
        if os.path.exists(path):
            _cache[kind] = path
            return path

    raise RuntimeError(
        "No CJK font found for %r.\n"
        "Set XHS_FONT_DIR to a directory holding msyh.ttc / NotoSansCJK-Regular.ttc,\n"
        "or set XHS_FONT_%s to an explicit .ttf/.ttc path.\n"
        "Searched:\n  %s" % (kind, kind.upper(), "\n  ".join(search))
    )


def load(kind, size):
    """Load a font at a pixel size."""
    return ImageFont.truetype(find(kind), int(size))


def platform_hint():
    return {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")

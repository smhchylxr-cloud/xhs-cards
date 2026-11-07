"""Page layouts. Each renderer returns a PIL image plus the lowest used y."""

from PIL import Image, ImageDraw

from . import decor, fonts, text as T
from .theme import Theme

W, H = 1080, 1440
PAD = 88
SAFE_BOTTOM = 1180
FOOT_RULE = 1240

REQUIRED = {
    "cover": ("eyebrow", "no", "headline", "repo", "stats", "cmd", "hook"),
    "list": ("eyebrow", "no", "h2", "items", "foot"),
    "steps": ("eyebrow", "no", "h2", "steps", "foot"),
    "note": ("eyebrow", "no", "h2", "blocks", "foot"),
}


class LayoutError(ValueError):
    """Raised when a page cannot fit its content inside the safe area."""


def _check(page, index):
    kind = page.get("type")
    if kind not in REQUIRED:
        raise LayoutError(f"page {index}: unknown type {kind!r}, expected one of {list(REQUIRED)}")
    missing = [k for k in REQUIRED[kind] if k not in page]
    if missing:
        raise LayoutError(f"page {index} ({kind}): missing keys {missing}")


def _canvas(theme):
    img = Image.new("RGB", (W, H), theme.paper)
    return img, ImageDraw.Draw(img)


def _decorate(img, page):
    """Apply the optional pen marks a page asks for: notes, circles, underlines."""
    for mark in page.get("marks", []):
        kind = mark.get("kind")
        if kind == "note":
            decor.note(
                img,
                tuple(mark["xy"]),
                mark["text"],
                size=mark.get("size", 44),
                angle=mark.get("angle", -2.0),
                color=tuple(mark.get("color", (176, 58, 48))),
            )
        elif kind == "circle":
            decor.circle(
                img,
                tuple(mark["center"]),
                mark.get("rx", 44),
                mark.get("ry", 36),
                angle=mark.get("angle", -4),
            )
        elif kind == "underline":
            decor.underline(img, mark["x0"], mark["x1"], mark["y"])
        elif kind == "highlight":
            img = decor.highlight(img, mark["box"], alpha=mark.get("alpha", 70))
    return img


def _head(d, page, theme):
    T.tracked(d, (PAD, 88), page["eyebrow"], fonts.load("regular", 26), theme.muted, 5.5)
    T.draw_right(d, W - PAD, 88, page["no"], fonts.load("mono", 27), theme.accent, 2)
    d.rectangle([PAD, 152, W - PAD, 154], fill=theme.ink)


def _foot(d, page, theme):
    label, value = page["foot"]
    d.rectangle([PAD, FOOT_RULE, W - PAD, FOOT_RULE + 3], fill=theme.ink)
    T.tracked(d, (PAD, FOOT_RULE + 38), label, fonts.load("regular", 24), theme.muted, 3.4)
    font = fonts.load("regular", 25)
    lines = T.wrap(value, font, W - 2 * PAD)
    for i, line in enumerate(lines[:2]):
        d.text((PAD, FOOT_RULE + 90 + i * 34), line, font=font, fill=theme.ink)


def _mono_or_text(line):
    """Command lines stay monospaced unless they contain CJK."""
    return "regular" if T.has_cjk(line) else "mono"


def render_cover(page, theme):
    img, d = _canvas(theme)
    _head(d, page, theme)

    compact = bool(page.get("compact"))
    font, lines, size = T.fit(
        page["headline"],
        "bold",
        W - 2 * PAD + 8,
        520 if compact else 392,
        start=136 if compact else 112,
        minimum=72,
        ratio=1.08,
    )
    y = 236 if compact else 208
    for i, line in enumerate(lines):
        colour = theme.accent if i == len(lines) - 1 else theme.ink
        d.text((PAD - 4, y), line, font=font, fill=colour)
        y += int(size * 1.08)

    y += 76 if compact else 62
    mono = fonts.load("mono", 33)
    d.rectangle([PAD, y + 12, PAD + 11, y + 23], fill=theme.accent)
    owner, sep, name = page["repo"].partition("/")
    if sep:
        d.text((PAD + 26, y), owner + " / ", font=mono, fill=theme.sub)
        x = PAD + 26 + d.textlength(owner + " / ", font=mono)
        d.text((x, y), name.strip(), font=mono, fill=theme.ink)
    else:
        d.text((PAD + 26, y), page["repo"], font=mono, fill=theme.ink)

    y += 60
    meta = fonts.load("regular", 29)
    x = PAD
    for item in page["stats"]:
        d.text((x, y), item, font=meta, fill=theme.sub)
        x += d.textlength(item, font=meta) + 44

    if compact:
        # Feed-legibility mode: headline + repo + stats + one line. Nothing else.
        d.rectangle([PAD, 1230, W - PAD, 1233], fill=theme.ink)
        hook = fonts.load("bold", 42)
        for i, line in enumerate(page["hook"][:2]):
            d.text((PAD, 1250 + i * 66), line, font=hook, fill=theme.ink)
        return _decorate(img, page), y + 40

    mid = max(830, y + 104)
    if mid > 1010:
        raise LayoutError("cover: headline too tall, shorten it or lower the font size")

    d.rectangle([PAD, mid, W - PAD, mid + 1], fill=theme.rule)
    label = fonts.load("regular", 24)
    value = fonts.load("regular", 31)
    rows = [("输入", page.get("in")), ("输出", page.get("out"))]
    ry = mid + 36
    for key, val in rows:
        if not val:
            continue
        T.tracked(d, (PAD, ry), key, label, theme.muted, 3.0)
        d.text((PAD, ry + 36), val, font=value, fill=theme.ink)
        ry += 106

    cmd_font = fonts.load("mono", 26)
    d.text((PAD, mid + 278), page["cmd"], font=cmd_font, fill=theme.accent)

    d.rectangle([PAD, 1230, W - PAD, 1233], fill=theme.ink)
    hook = fonts.load("bold", 36)
    for i, line in enumerate(page["hook"][:2]):
        d.text((PAD, 1256 + i * 62), line, font=hook, fill=theme.ink)

    # The hook band is fixed furniture; the checkable content ends at the command line.
    return _decorate(img, page), mid + 300


def render_list(page, theme):
    img, d = _canvas(theme)
    _head(d, page, theme)

    h2f, h2lines, h2size = T.fit(page["h2"], "bold", W - 2 * PAD, 210, start=78, minimum=58, ratio=1.1)
    y = 206
    for line in h2lines:
        d.text((PAD - 3, y), line, font=h2f, fill=theme.ink)
        y += int(h2size * 1.1)

    y = max(y + 44, 470)
    num = fonts.load("mono", 38)
    h3 = fonts.load("bold", 37)
    body = fonts.load("regular", 27)
    for item in page["items"]:
        d.text((PAD, y + 2), str(item["n"]), font=num, fill=theme.accent)
        title_lines = T.wrap(item["title"], h3, W - 2 * PAD - 96)
        ty = y
        for line in title_lines:
            d.text((PAD + 96, ty), line, font=h3, fill=theme.ink)
            ty += 48
        ty += 10
        for raw in item.get("desc", []):
            for line in T.wrap(raw, body, W - 2 * PAD - 96):
                d.text((PAD + 96, ty), line, font=body, fill=theme.sub)
                ty += 42
        y = ty + 46

    _foot(d, page, theme)
    return _decorate(img, page), y


def render_steps(page, theme):
    img, d = _canvas(theme)
    _head(d, page, theme)

    h2f, h2lines, h2size = T.fit(page["h2"], "bold", W - 2 * PAD, 210, start=78, minimum=58, ratio=1.1)
    y = 206
    for line in h2lines:
        d.text((PAD - 3, y), line, font=h2f, fill=theme.ink)
        y += int(h2size * 1.1)

    y = max(y + 44, 470)
    num = fonts.load("mono", 40)
    h3 = fonts.load("bold", 36)
    for step in page["steps"]:
        d.text((PAD, y), str(step["n"]), font=num, fill=theme.accent)
        d.text((PAD + 96, y - 4), step["title"], font=h3, fill=theme.ink)
        ty = y + 58
        for raw in step.get("desc", []):
            is_cmd = raw.startswith("$")
            content = raw[1:].strip() if is_cmd else raw
            if is_cmd and not T.has_cjk(content):
                ty = decor.pill(img, (PAD + 96, ty), content, size=25) + 18
                continue
            kind = _mono_or_text(content)
            font = fonts.load(kind, 27 if kind == "mono" else 26)
            colour = theme.accent if is_cmd else theme.sub
            for line in T.wrap(content, font, W - 2 * PAD - 96):
                d.text((PAD + 96, ty), line, font=font, fill=colour)
                ty += 42
        y = ty + 48

    _foot(d, page, theme)
    return _decorate(img, page), y


def render_note(page, theme):
    img, d = _canvas(theme)
    _head(d, page, theme)

    h2f, h2lines, h2size = T.fit(page["h2"], "bold", W - 2 * PAD, 210, start=78, minimum=58, ratio=1.1)
    y = 206
    for line in h2lines:
        d.text((PAD - 3, y), line, font=h2f, fill=theme.ink)
        y += int(h2size * 1.1)

    y = max(y + 44, 470)
    h3 = fonts.load("bold", 33)
    body = fonts.load("regular", 26)
    for block in page["blocks"]:
        d.rectangle([PAD, y + 10, PAD + 11, y + 21], fill=theme.accent)
        d.text((PAD + 26, y), block["label"], font=h3, fill=theme.ink)
        ty = y + 58
        for raw in block.get("lines", []):
            for line in T.wrap(raw, body, W - 2 * PAD - 26):
                d.text((PAD + 26, ty), line, font=body, fill=theme.sub)
                ty += 42
        y = ty + 44

    _foot(d, page, theme)
    return _decorate(img, page), y


RENDERERS = {
    "cover": render_cover,
    "list": render_list,
    "steps": render_steps,
    "note": render_note,
}


def render_page(page, index, theme):
    _check(page, index)
    img, lowest = RENDERERS[page["type"]](page, theme)
    if lowest > SAFE_BOTTOM:
        raise LayoutError(
            f"page {index} ({page['type']}) overflows the safe area: "
            f"content ends at {lowest}px, limit is {SAFE_BOTTOM}px. "
            f"Shorten the text or split the page."
        )
    if page.get("texture"):
        img = decor.paper(img)
    return img

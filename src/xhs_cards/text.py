"""Text measurement, wrapping and auto-fit."""

from . import fonts


def has_cjk(text):
    return any("\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" for ch in text)


def wrap(text, font, max_width):
    """Greedy wrap: CJK breaks anywhere, latin prefers spaces."""
    if not text:
        return [""]
    lines, current = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        if font.getlength(current + ch) <= max_width:
            current += ch
            continue
        if ch != " " and " " in current and not has_cjk(ch):
            cut = current.rfind(" ")
            lines.append(current[:cut])
            current = current[cut + 1:] + ch
        else:
            lines.append(current)
            current = ch
    lines.append(current)
    return lines


def fit(lines, kind, max_width, max_height, start, minimum, ratio=1.14, floor=0):
    """Shrink until every line fits max_width and the stack fits max_height.

    Returns (font, wrapped_lines, size).
    """
    size = start
    while size >= minimum:
        font = fonts.load(kind, size)
        wrapped = []
        for line in lines:
            wrapped.extend(wrap(line, font, max_width))
        widest = max(font.getlength(l) for l in wrapped)
        height = len(wrapped) * size * ratio
        if widest <= max_width and height <= max_height:
            return font, wrapped, size
        size -= 2
    font = fonts.load(kind, minimum)
    wrapped = []
    for line in lines:
        wrapped.extend(wrap(line, font, max_width))
    return font, wrapped, minimum


def tracked(draw, xy, text, font, fill, tracking=0.0):
    """Draw text with extra letter spacing. Returns the x cursor after the run."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def tracked_width(draw, text, font, tracking=0.0):
    if not text:
        return 0.0
    return sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)


def draw_right(draw, right_x, y, text, font, fill, tracking=0.0):
    x = right_x - tracked_width(draw, text, font, tracking)
    tracked(draw, (x, y), text, font, fill, tracking)
    return x

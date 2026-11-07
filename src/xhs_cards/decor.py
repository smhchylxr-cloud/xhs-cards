"""Hand-made finishing: paper grain, felt-tip marks, handwritten notes.

Machine-clean output reads as "generated". These helpers put the small
imperfections back: a noisy paper, a wobbly underline, a pen circle, a
note in a handwriting face, a command in a dark terminal pill.
"""

import math
import random

import numpy as np
from PIL import Image, ImageDraw

from . import fonts

PEN = (176, 58, 48)
HILITE = (255, 214, 64)


def paper(img, grain=1.2, mottle=0.0, cells=48, vignette=0.05, seed=7):
    """Paper, not pixels: slow blotching carries the texture, grain only breaks banding.

    Fine grain is expensive in JPEG bytes and gets smeared by the platform's own
    re-compression, so it stays low; the low-frequency mottling is what reads as paper.
    """
    arr = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    h, w = arr.shape[:2]

    arr += rng.normal(0, grain, (h, w))[..., None]

    # Low-frequency mottling: what actually reads as paper rather than film grain.
    cells = cells
    small = rng.normal(0, 1, (cells, cells))
    span = np.ptp(small) + 1e-6
    blot = Image.fromarray(((small - small.min()) / span * 255).astype(np.uint8))
    blot = blot.resize((w, h), Image.BICUBIC)
    flat = np.asarray(blot).astype(np.float32)
    arr += ((flat - flat.mean()) / (flat.std() + 1e-6) * mottle)[..., None]

    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    arr *= (1 - vignette * d)[..., None]

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def note(img, xy, text, size=44, color=PEN, angle=-2.0, tracking=0.6):
    """A line in a handwriting face, slightly askew."""
    layer = _layer(img.size)
    d = ImageDraw.Draw(layer)
    font = fonts.load("hand", size)
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=color + (255,))
        x += d.textlength(ch, font=font) + tracking
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=xy)
    img.paste(layer, (0, 0), layer)
    return img


def underline(img, x0, x1, y, color=PEN, width=3, wobble=2.2):
    """A pen underline that is not quite straight."""
    layer = _layer(img.size)
    d = ImageDraw.Draw(layer)
    rng = random.Random(int(x0) + int(y))
    steps = 16
    pts = []
    for i in range(steps + 1):
        t = i / steps
        px = x0 + (x1 - x0) * t
        py = y + math.sin(t * math.pi * 1.6) * wobble + rng.uniform(-0.9, 0.9)
        pts.append((px, py))
    d.line(pts, fill=color + (225,), width=width, joint="curve")
    img.paste(layer, (0, 0), layer)
    return img


def circle(img, center, rx, ry, color=PEN, width=3, angle=-4):
    """A felt-tip circle drawn around something."""
    layer = _layer(img.size)
    d = ImageDraw.Draw(layer)
    cx, cy = center
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=color + (215,), width=width)
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=center)
    img.paste(layer, (0, 0), layer)
    return img


def highlight(img, box, color=HILITE, alpha=70, radius=5):
    base = img.convert("RGBA")
    layer = _layer(img.size)
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=radius, fill=color + (alpha,))
    base.alpha_composite(layer)
    return base.convert("RGB")


def pill(img, xy, text, size=25, pad=(18, 10), fill=(26, 26, 30), ink=(240, 238, 232)):
    """Draw a command as a dark terminal pill and return its bottom y."""
    d = ImageDraw.Draw(img)
    font = fonts.load("mono", size)
    tw = d.textlength(text, font=font)
    x, y = xy
    box = [x, y, x + tw + pad[0] * 2, y + size + pad[1] * 2]
    d.rounded_rectangle(box, radius=(size + pad[1] * 2) // 2, fill=fill)
    d.text((x + pad[0], y + pad[1] - 2), text, font=font, fill=ink)
    return box[3]

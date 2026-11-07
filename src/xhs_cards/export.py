"""Export help: white-background JPEG, no metadata, upload-friendly names."""

import os
import re

from PIL import Image

MAX_SIDE = 1440
QUALITY = 92


def _flatten(img):
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


def save_jpeg(img, path, quality=QUALITY):
    img = _flatten(img)
    if max(img.size) > MAX_SIDE:
        ratio = MAX_SIDE / max(img.size)
        img = img.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)
    img.save(path, "JPEG", quality=quality, subsampling=0, optimize=True)
    return path


def export_dir(src_dir, out_dir, quality=QUALITY):
    """Rename 01_cover.png -> 01_cover.jpg in order; returns [(path, size, bytes)]."""
    os.makedirs(out_dir, exist_ok=True)
    names = sorted(
        f for f in os.listdir(src_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    results = []
    for index, name in enumerate(names, 1):
        stem = re.sub(r"^\d+[-_]?", "", os.path.splitext(name)[0])
        dst = os.path.join(out_dir, f"{index:02d}_{stem}.jpg")
        save_jpeg(Image.open(os.path.join(src_dir, name)), dst, quality)
        results.append((dst, Image.open(dst).size, os.path.getsize(dst)))
    return results

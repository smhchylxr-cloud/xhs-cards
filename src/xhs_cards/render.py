"""Turn an issue spec into image files."""

import json
import os
from dataclasses import replace

from . import layout, theme as theme_mod


def load_spec(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if "pages" not in spec or not isinstance(spec["pages"], list):
        raise ValueError("spec must contain a 'pages' list")
    return spec


def resolve_theme(spec):
    name = spec.get("theme", "ikb")
    base = theme_mod.PRESETS.get(name)
    if base is None:
        raise ValueError(f"unknown theme {name!r}, available: {list(theme_mod.PRESETS)}")
    accent = spec.get("accent")
    if accent:
        if len(accent) != 3:
            raise ValueError("accent must be [r, g, b]")
        base = replace(base, accent=tuple(int(c) for c in accent))
    return base


def build(spec, out_dir, jpeg=False, quality=92):
    """Render every page. Returns the list of written file paths."""
    os.makedirs(out_dir, exist_ok=True)
    theme = resolve_theme(spec)
    written = []
    defaults = {key: spec[key] for key in ("compact",) if key in spec}

    for index, page in enumerate(spec["pages"], 1):
        if defaults:
            page = {**defaults, **page}
        img = layout.render_page(page, index, theme)
        stem = f"{index:02d}_{page['type']}"
        if jpeg:
            from .export import save_jpeg

            path = os.path.join(out_dir, stem + ".jpg")
            save_jpeg(img, path, quality)
        else:
            path = os.path.join(out_dir, stem + ".png")
            img.save(path, "PNG")
        written.append(path)

    return written

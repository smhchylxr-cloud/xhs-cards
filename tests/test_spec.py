import json
import pathlib

import pytest
from PIL import Image

from xhs_cards import build, load_spec
from xhs_cards.layout import LayoutError

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.json"))


@pytest.mark.parametrize("spec_path", EXAMPLES, ids=lambda p: p.stem)
def test_examples_render(spec_path, tmp_path):
    spec = load_spec(spec_path)
    paths = build(spec, tmp_path)
    assert len(paths) == len(spec["pages"])
    for path in paths:
        with Image.open(path) as img:
            assert img.size == (1080, 1440)


def test_unknown_page_type_fails():
    with pytest.raises(LayoutError):
        build({"pages": [{"type": "poster"}]}, ".")


def test_missing_key_is_reported():
    with pytest.raises(LayoutError) as err:
        build({"pages": [{"type": "list", "eyebrow": "x", "no": "1", "h2": ["a"]}]}, ".")
    assert "items" in str(err.value)


def test_overflow_is_reported():
    spec = {
        "pages": [
            {
                "type": "list",
                "eyebrow": "x",
                "no": "01",
                "h2": ["标题"],
                "items": [
                    {"n": str(i), "title": "标题" * 6, "desc": ["描述" * 20] * 3}
                    for i in range(1, 6)
                ],
                "foot": ["a", "b"],
            }
        ]
    }
    with pytest.raises(LayoutError) as err:
        build(spec, ".")
    assert "overflows" in str(err.value)


def test_jpeg_output_is_white_background(tmp_path):
    spec = json.loads((ROOT / "examples" / "project.json").read_text(encoding="utf-8"))
    paths = build(spec, tmp_path, jpeg=True)
    assert paths[0].endswith(".jpg")
    with Image.open(paths[0]) as img:
        assert img.mode == "RGB"
        assert img.getpixel((2, 2)) == (255, 255, 255) or img.getpixel((2, 2))[0] > 200


def _band_ink(path, top=900, bottom=1150, step=4):
    """Sample a horizontal band and count pixels darker than the paper."""
    with Image.open(path) as img:
        grey = img.convert("L")
        px = grey.load()
        return sum(
            1
            for y in range(top, bottom, step)
            for x in range(0, grey.width, step)
            if px[x, y] < 120
        )


def _cover_spec(compact):
    spec = {
        "pages": [
            {
                "type": "cover",
                "eyebrow": "x",
                "no": "NO.1",
                "headline": ["短标题"],
                "repo": "a/b",
                "stats": ["1 star"],
                "cmd": "pip install nothing",
                "hook": ["a", "b"],
            }
        ]
    }
    if compact:
        spec["compact"] = True
    return spec


def test_compact_flag_reaches_the_cover(tmp_path):
    """A deck-level flag must reach the page dict (regression: it once did not)."""
    plain = build(_cover_spec(False), tmp_path / "plain")
    compact = build(_cover_spec(True), tmp_path / "compact")
    assert _band_ink(plain[0]) > 20
    assert _band_ink(compact[0]) == 0


def test_paper_texture_leaves_grain(tmp_path):
    """Texture must actually change pixels, not just be accepted as a key."""
    spec = _cover_spec(True)
    bare = build(spec, tmp_path / "bare")[0]
    spec_tex = {**spec, "texture": True}
    textured = build(spec_tex, tmp_path / "textured")[0]

    def flat_std(path):
        with Image.open(path) as img:
            grey = img.convert("L")
            patch = grey.crop((700, 620, 980, 820))
            values = list(patch.tobytes())
            mean = sum(values) / len(values)
            return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    assert flat_std(bare) < 0.6
    assert flat_std(textured) > 0.8

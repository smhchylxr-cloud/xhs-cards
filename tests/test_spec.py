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

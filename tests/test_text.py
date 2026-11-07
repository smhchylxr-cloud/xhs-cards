import pytest

from xhs_cards import fonts, text


@pytest.fixture(scope="module")
def body_font():
    return fonts.load("regular", 27)


def test_has_cjk():
    assert text.has_cjk("中文")
    assert not text.has_cjk("plain ascii")


def test_wrap_keeps_content(body_font):
    source = "这一行足够长，应该被拆成多行显示，而不是一直往右延伸出去。"
    lines = text.wrap(source, body_font, 300)
    assert len(lines) > 1
    assert "".join(lines) == source


def test_wrap_respects_width(body_font):
    lines = text.wrap("a" * 200, body_font, 300)
    assert all(body_font.getlength(line) <= 300 for line in lines)


def test_wrap_prefers_spaces_for_latin(body_font):
    lines = text.wrap("alpha beta gamma delta epsilon", body_font, 120)
    assert all(not line.startswith(" ") for line in lines)
    assert " ".join(lines).split() == "alpha beta gamma delta epsilon".split()


def test_fit_shrinks_until_it_fits():
    font, lines, size = text.fit(["一" * 40], "bold", 600, 300, start=112, minimum=48)
    assert size >= 48
    assert font.getlength(lines[0]) <= 600

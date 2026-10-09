import re

import plotly.express as px
import plotly.io as pio
import pytest

from shelf_life import palette

HEX = re.compile(r"^#[0-9a-f]{6}$")


def _luminance(hex_color: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(int(hex_color[i : i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@pytest.mark.parametrize(
    "colors",
    [
        palette.CATEGORICAL,
        palette.CATEGORICAL_DARK,
        palette.SEQUENTIAL,
        palette.DIVERGING,
    ],
)
def test_colors_are_hex(colors):
    assert all(HEX.match(c) for c in colors)


def test_categorical_has_seven_named_slots():
    assert len(palette.CATEGORICAL) == len(palette.CATEGORICAL_DARK) == 7
    assert list(palette.COLORS) == palette.CATEGORICAL_NAMES


def test_sequential_runs_light_to_dark():
    lums = [_luminance(c) for c in palette.SEQUENTIAL]
    assert lums == sorted(lums, reverse=True)


def test_diverging_is_symmetric_around_light_midpoint():
    lums = [_luminance(c) for c in palette.DIVERGING]
    mid = len(lums) // 2
    assert lums[:mid] == sorted(lums[:mid])
    assert lums[mid + 1 :] == sorted(lums[mid + 1 :], reverse=True)
    assert lums[mid] == max(lums)


def test_register_sets_default_template():
    previous = pio.templates.default
    try:
        palette.register()
        assert pio.templates.default == "shelf_life"
        fig = px.bar(x=["a", "b"], y=[1, 2], color=["a", "b"])
        assert fig.layout.template.layout.colorway == tuple(palette.CATEGORICAL)
        assert "shelf_life_dark" in pio.templates
    finally:
        pio.templates.default = previous

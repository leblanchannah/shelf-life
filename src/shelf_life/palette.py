"""Plot colours and the plotly template for the Shelf Life posts.

Usage in a notebook::

    from shelf_life import palette

    palette.register()  # makes "shelf_life" the default plotly template
    px.bar(df, x="brand", y="price", color="category")

The categorical colours were validated (OKLab Delta E x100, Machado 2009 CVD
simulation) for the slot order below:

- light, on ``SURFACE``: worst adjacent pair 13.0 under protan/deutan, 20.8 for
  normal vision; the first three slots also clear all-pairs (13.0 / 23.3).
- dark, on ``SURFACE_DARK``: worst adjacent pair 11.4 / 17.2; first three
  all-pairs 11.5 / 18.6.

Every light slot is >= 3:1 against the surface except ochre (2.4:1), so a chart
that uses six or more series needs direct labels or a table alongside it.
Scatter plots and other charts where any two colours can touch should use only
the first three slots; fold the rest into "Other" or facet.

If you change a hex, keep the order and re-validate before publishing.
"""

import plotly.graph_objects as go
import plotly.io as pio

# Surfaces and ink. Warm cream rather than white so charts read as a set on the page.
SURFACE = "#fbf8f4"
SURFACE_DARK = "#1d1a1f"
INK = "#2b2430"
INK_MUTED = "#6b6270"
GRID = "#ebe4dd"
INK_DARK = "#f4eff2"
INK_MUTED_DARK = "#b7adb6"
GRID_DARK = "#3a3439"

# Categorical, in assignment order. Never cycle past slot 7: fold extras into "Other".
CATEGORICAL_NAMES = ["plum", "teal", "terracotta", "slate", "olive", "ochre", "rose"]
CATEGORICAL = ["#7f3471", "#1d9999", "#ce683f", "#4a70b7", "#526e2a", "#cd9c34", "#bf4d73"]
CATEGORICAL_DARK = ["#9d498d", "#0da5a5", "#d16b42", "#5b82cb", "#527023", "#b28938", "#ba496f"]
COLORS = dict(zip(CATEGORICAL_NAMES, CATEGORICAL, strict=True))

# Sequential (magnitude): one plum hue, light -> dark. The light end sits near the
# surface on purpose (zero fades into the page in heatmaps). For discrete,
# ordered bars use ORDINAL, whose lightest step still shows against the surface.
SEQUENTIAL = [
    "#fbedf7",
    "#f0cfe9",
    "#ddabd5",
    "#c585be",
    "#aa61a6",
    "#894489",
    "#6a2e6d",
    "#4b1d4f",
]
ORDINAL = SEQUENTIAL[3:]

# Diverging (above/below a baseline, e.g. price vs category median): blue for
# cheaper, terracotta for pricier, warm grey at the midpoint. Equal steps per arm.
DIVERGING = [
    "#015182",
    "#2177b4",
    "#67a2d2",
    "#aecbe5",
    "#efeae5",
    "#e5bdaf",
    "#d0866b",
    "#af5331",
    "#81300f",
]

FONT_FAMILY = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"


def colorscale(colors: list[str]) -> list[list[float | str]]:
    """Evenly spaced plotly colorscale, e.g. ``coloraxis_colorscale=colorscale(DIVERGING)``."""
    step = 1 / (len(colors) - 1)
    return [[round(i * step, 4), c] for i, c in enumerate(colors)]


def template(dark: bool = False) -> go.layout.Template:
    """Build the Shelf Life plotly template (light by default)."""
    surface = SURFACE_DARK if dark else SURFACE
    ink = INK_DARK if dark else INK
    muted = INK_MUTED_DARK if dark else INK_MUTED
    grid = GRID_DARK if dark else GRID
    colorway = CATEGORICAL_DARK if dark else CATEGORICAL
    # In dark mode low values should fade into the dark surface, so flip the ramp.
    sequential = SEQUENTIAL[::-1] if dark else SEQUENTIAL

    axis = {
        "showgrid": False,
        "gridcolor": grid,
        "gridwidth": 1,
        "zerolinecolor": muted,
        "showline": True,
        "linecolor": grid,
        "linewidth": 1,
        "ticks": "",
        "tickfont": {"color": muted},
        "title": {"font": {"color": muted}, "standoff": 10},
        "zeroline": False,
        "automargin": True,
    }
    value_axis = {**axis, "showgrid": True, "showline": False}

    layout = go.Layout(
        colorway=colorway,
        colorscale={
            "sequential": colorscale(sequential),
            "sequentialminus": colorscale(sequential[::-1]),
            "diverging": colorscale(DIVERGING),
        },
        coloraxis={"colorscale": colorscale(sequential), "colorbar": {"outlinewidth": 0}},
        font={"family": FONT_FAMILY, "size": 13, "color": ink},
        title={
            "font": {"size": 18, "color": ink},
            "x": 0,
            "xanchor": "left",
            "xref": "paper",
        },
        paper_bgcolor=surface,
        plot_bgcolor=surface,
        xaxis=axis,
        yaxis=value_axis,
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": 1.02,
            "yanchor": "bottom",
            "title": {"text": ""},
            "font": {"color": muted},
            "bgcolor": "rgba(0,0,0,0)",
        },
        hoverlabel={
            "bgcolor": surface,
            "bordercolor": grid,
            "font": {"family": FONT_FAMILY, "color": ink},
        },
        hovermode="closest",
        bargap=0.25,
        bargroupgap=0.08,
        margin={"l": 60, "r": 24, "t": 72, "b": 56},
    )

    data = go.layout.template.Data(
        bar=[go.Bar(marker={"line": {"color": surface, "width": 1.5}})],
        histogram=[go.Histogram(marker={"line": {"color": surface, "width": 1.5}})],
        scatter=[
            go.Scatter(
                line={"width": 2}, marker={"size": 8, "line": {"color": surface, "width": 1}}
            )
        ],
        box=[go.Box(line={"width": 1.5}, marker={"size": 5})],
        violin=[go.Violin(line={"width": 1.5})],
        pie=[go.Pie(marker={"line": {"color": surface, "width": 2}})],
        heatmap=[go.Heatmap(colorscale=colorscale(sequential), xgap=2, ygap=2)],
    )
    return go.layout.Template(layout=layout, data=data)


def register(default: bool = True) -> None:
    """Register ``shelf_life`` and ``shelf_life_dark`` with plotly.io.templates."""
    pio.templates["shelf_life"] = template()
    pio.templates["shelf_life_dark"] = template(dark=True)
    if default:
        pio.templates.default = "shelf_life"

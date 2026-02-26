"""
World Globe Explorer — Premium Interactive 3D Globe
Built with Python, Plotly & Dash | Deploy-ready for Render
"""

import json
import os

import dash
from dash import Input, Output, State, callback_context, dcc, html, no_update
import plotly.graph_objects as go

from data.cities_data import CITIES_DATA, CONTINENT_COLORS, CONTINENT_EMOJIS

# ─── App Initialization ───────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    title="🌍 World Globe Explorer",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Interactive Premium 3D World Globe Explorer"},
        {"name": "theme-color", "content": "#020d18"},
    ],
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:ital,wght@0,300;0,400;0,600;1,300&display=swap"
    ],
)
server = app.server  # Expose Flask server for gunicorn


# ─── Helper Functions ─────────────────────────────────────────────────────────

def fmt_pop(n: int) -> str:
    """Format population number to readable string."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def build_figure(view_mode: str = "globe", continent: str = "All") -> go.Figure:
    """Build the Plotly Scattergeo figure for 3D globe or flat map."""

    cities = (
        CITIES_DATA
        if continent == "All"
        else [c for c in CITIES_DATA if c["continent"] == continent]
    )

    fig = go.Figure()

    for cont, color in CONTINENT_COLORS.items():
        grp = [c for c in cities if c["continent"] == cont]
        if not grp:
            continue

        lats = [c["lat"] for c in grp]
        lons = [c["lon"] for c in grp]
        sizes = [max(10, min(26, c["population"] / 750_000 * 2.5)) for c in grp]
        custom = [json.dumps(c) for c in grp]
        hover = [
            (
                f"<b style='font-size:15px'>{c['name']}</b><br>"
                f"<span style='color:#aac'>{c['flag']}  {c['country']} · {c['continent']}</span><br>"
                f"────────────────────<br>"
                f"👥 Population: <b>{fmt_pop(c['population'])}</b><br>"
                f"🗣  Language: {c['language']}<br>"
                f"🏆 Famous for: {c['best_known_for'][:55]}…"
            )
            for c in grp
        ]

        # ── Glow / halo layer (behind markers) ──
        fig.add_trace(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="markers",
                marker=dict(
                    size=[s * 2.4 for s in sizes],
                    color=color,
                    opacity=0.12,
                    line=dict(width=0),
                ),
                hoverinfo="skip",
                showlegend=False,
                name=f"_halo_{cont}",
            )
        )

        # ── Mid glow layer ──
        fig.add_trace(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="markers",
                marker=dict(
                    size=[s * 1.6 for s in sizes],
                    color=color,
                    opacity=0.22,
                    line=dict(width=0),
                ),
                hoverinfo="skip",
                showlegend=False,
                name=f"_mid_{cont}",
            )
        )

        # ── Main marker layer ──
        fig.add_trace(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=color,
                    opacity=0.95,
                    line=dict(color="rgba(255,255,255,0.55)", width=1.5),
                    symbol="circle",
                ),
                name=CONTINENT_EMOJIS.get(cont, "") + "  " + cont,
                hovertext=hover,
                hoverinfo="text",
                hoverlabel=dict(
                    bgcolor="rgba(5,15,35,0.96)",
                    bordercolor=color,
                    font=dict(color="#ddeeff", size=13, family="Exo 2"),
                    namelength=0,
                ),
                customdata=custom,
                showlegend=True,
            )
        )

    # ── Geo layout ──
    geo = dict(
        showland=True,
        landcolor="#14293d",
        showocean=True,
        oceancolor="#081624",
        showcountries=True,
        countrycolor="#1b3a50",
        countrywidth=0.4,
        showcoastlines=True,
        coastlinecolor="#1e4d6a",
        coastlinewidth=0.7,
        showlakes=True,
        lakecolor="#081624",
        showrivers=False,
        showgraticules=True,
        graticulecolor="rgba(80,160,220,0.07)",
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
    )

    if view_mode == "globe":
        geo.update(
            projection_type="orthographic",
            projection_rotation=dict(lon=10, lat=20, roll=0),
        )
    else:
        geo.update(
            projection_type="natural earth",
            lataxis_range=[-90, 90],
            lonaxis_range=[-180, 180],
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=geo,
        legend=dict(
            orientation="v",
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(2,13,26,0.82)",
            bordercolor="rgba(0,200,255,0.25)",
            borderwidth=1,
            font=dict(color="#b0cce0", size=12, family="Exo 2"),
            title=dict(
                text="<b>Continents</b>",
                font=dict(color="#60b0e8", size=12, family="Exo 2"),
            ),
            tracegroupgap=4,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        uirevision=f"{view_mode}",
    )
    return fig


def build_stat_chip(icon: str, label: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Span(icon, className="chip-icon"),
            html.Div(
                [
                    html.Span(label, className="chip-label"),
                    html.Span(value, className="chip-value"),
                ],
                className="chip-text",
            ),
        ],
        className="stat-chip",
    )


def build_city_panel(city: dict) -> html.Div:
    """Render the city detail panel content."""
    color = CONTINENT_COLORS.get(city["continent"], "#00d2ff")
    pop_pct = min(100, city["population"] / 22_000_000 * 100)

    tags = [
        html.Span(t.strip(), className="tag", style={"borderColor": color + "88"})
        for t in city["best_known_for"].split(",")
    ]

    attractions = [
        html.Li(
            [html.Span("✦", className="bullet", style={"color": color}), a],
            className="attr-item",
        )
        for a in city["top_attractions"]
    ]

    facts = [
        html.Li(f, className="fact-item") for f in city.get("fun_facts", [])
    ]

    stats = [
        build_stat_chip("👥", "Population", fmt_pop(city["population"])),
        build_stat_chip("🗣", "Language", city["language"]),
        build_stat_chip("💱", "Currency", city["currency"]),
        build_stat_chip("🕐", "Timezone", city["timezone"]),
        build_stat_chip("📅", "Founded", city.get("founded", "Ancient")),
        build_stat_chip("🌍", "Continent", city["continent"]),
    ]

    return html.Div(
        [
            # ── Header ──────────────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        city["flag"],
                        className="panel-flag",
                        style={"filter": f"drop-shadow(0 0 12px {color})"},
                    ),
                    html.Div(
                        [
                            html.H2(city["name"], className="panel-city-name"),
                            html.Div(
                                [
                                    html.Span(city["country"], className="panel-country"),
                                    html.Span("·", className="dot"),
                                    html.Span(
                                        city["continent"],
                                        className="panel-continent",
                                        style={"color": color},
                                    ),
                                ],
                                className="panel-meta",
                            ),
                        ],
                        className="panel-header-text",
                    ),
                ],
                className="panel-header",
                style={"borderBottom": f"2px solid {color}33"},
            ),

            # ── Description ─────────────────────────────────────────────
            html.P(city["description"], className="panel-description"),

            # ── Tags ────────────────────────────────────────────────────
            html.Div(tags, className="tags-row"),

            # ── Population Bar ──────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Population", className="bar-label"),
                            html.Span(
                                f"{city['population']:,}",
                                className="bar-number",
                                style={"color": color},
                            ),
                        ],
                        className="bar-row",
                    ),
                    html.Div(
                        html.Div(
                            style={
                                "width": f"{pop_pct:.0f}%",
                                "height": "100%",
                                "background": f"linear-gradient(90deg, {color}cc, {color}44)",
                                "borderRadius": "4px",
                                "transition": "width 1.2s cubic-bezier(0.4,0,0.2,1)",
                            }
                        ),
                        className="pop-bar",
                    ),
                ],
                className="pop-section",
            ),

            # ── Stat Chips Grid ─────────────────────────────────────────
            html.Div(stats, className="stats-grid"),

            # ── Top Attractions ─────────────────────────────────────────
            html.Div(
                [
                    html.H3(
                        [html.Span("🏛", className="sec-icon"), " Top Attractions"],
                        className="sec-title",
                        style={"color": color},
                    ),
                    html.Ul(attractions, className="attr-list"),
                ],
                className="panel-section",
            ),

            # ── Fun Facts ───────────────────────────────────────────────
            html.Div(
                [
                    html.H3(
                        [html.Span("💡", className="sec-icon"), " Fun Facts"],
                        className="sec-title",
                        style={"color": color},
                    ),
                    html.Ul(facts, className="facts-list"),
                ],
                className="panel-section",
            )
            if facts
            else html.Div(),
        ],
        className="city-panel-inner",
    )


# ─── App Layout ───────────────────────────────────────────────────────────────

app.layout = html.Div(
    [
        # ── Header ──────────────────────────────────────────────────────────
        html.Header(
            [
                html.Div(
                    [
                        html.Div("🌍", className="logo-globe"),
                        html.Div(
                            [
                                html.H1("World Globe Explorer", className="app-title"),
                                html.P(
                                    "Click any city to explore · Drag to rotate · Scroll to zoom",
                                    className="app-subtitle",
                                ),
                            ]
                        ),
                    ],
                    className="header-brand",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(str(len(CITIES_DATA)), className="stat-num"),
                                html.Span("Cities", className="stat-lbl"),
                            ],
                            className="hdr-stat",
                        ),
                        html.Div(
                            [
                                html.Span(str(len(CONTINENT_COLORS)), className="stat-num"),
                                html.Span("Continents", className="stat-lbl"),
                            ],
                            className="hdr-stat",
                        ),
                    ],
                    className="header-stats",
                ),
            ],
            className="app-header",
        ),

        # ── Controls Bar ─────────────────────────────────────────────────────
        html.Div(
            [
                # View mode toggle
                html.Div(
                    [
                        html.Button(
                            [html.Span("⚫", className="btn-dot"), "  3D Globe"],
                            id="btn-globe",
                            className="view-btn active",
                            n_clicks=0,
                        ),
                        html.Button(
                            [html.Span("🗺", className="btn-dot"), "  Flat Map"],
                            id="btn-map",
                            className="view-btn",
                            n_clicks=0,
                        ),
                    ],
                    className="toggle-group",
                ),

                # Continent dropdown
                dcc.Dropdown(
                    id="continent-dd",
                    options=[{"label": "🌐  All Continents", "value": "All"}]
                    + [
                        {
                            "label": CONTINENT_EMOJIS.get(c, "") + "  " + c,
                            "value": c,
                        }
                        for c in CONTINENT_COLORS
                    ],
                    value="All",
                    clearable=False,
                    className="continent-dd",
                    placeholder="Filter by continent…",
                ),

                # Live city counter
                html.Div(id="city-counter", className="city-counter"),
            ],
            className="controls-bar",
        ),

        # ── Main Content Area ─────────────────────────────────────────────────
        html.Div(
            [
                # Globe / Map graph
                html.Div(
                    dcc.Graph(
                        id="globe",
                        figure=build_figure(),
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": [
                                "select2d",
                                "lasso2d",
                                "autoScale2d",
                            ],
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "world_globe_explorer",
                                "height": 900,
                                "width": 1400,
                                "scale": 2,
                            },
                        },
                        style={"height": "100%", "width": "100%"},
                        className="globe-graph",
                    ),
                    id="globe-wrap",
                    className="globe-wrap",
                ),

                # City detail panel (always in DOM, shown/hidden via class)
                html.Div(
                    [
                        html.Button(
                            "✕",
                            id="close-btn",
                            className="close-btn",
                            n_clicks=0,
                            title="Close panel",
                        ),
                        html.Div(id="city-content", className="city-scroll"),
                    ],
                    id="city-panel",
                    className="city-panel hidden",
                ),
            ],
            className="main-content",
        ),

        # ── Footer ───────────────────────────────────────────────────────────
        html.Footer(
            html.P(
                [
                    "Built with ",
                    html.Span("♥", style={"color": "#ff4757"}),
                    " using Python & Plotly Dash  ·  Data is illustrative",
                ],
                className="footer-text",
            ),
            className="app-footer",
        ),

        # ── Hidden State Stores ───────────────────────────────────────────────
        dcc.Store(id="view-store", data="globe"),
    ],
    className="root",
    id="app-root",
)


# ─── Callbacks ────────────────────────────────────────────────────────────────

@app.callback(
    Output("view-store", "data"),
    Output("btn-globe", "className"),
    Output("btn-map", "className"),
    Input("btn-globe", "n_clicks"),
    Input("btn-map", "n_clicks"),
    State("view-store", "data"),
    prevent_initial_call=True,
)
def switch_view(gc, mc, current):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    if btn == "btn-globe":
        return "globe", "view-btn active", "view-btn"
    return "flat", "view-btn", "view-btn active"


@app.callback(
    Output("globe", "figure"),
    Output("city-counter", "children"),
    Input("view-store", "data"),
    Input("continent-dd", "value"),
)
def refresh_globe(view, cont):
    fig = build_figure(view_mode=view or "globe", continent=cont or "All")
    n = (
        len(CITIES_DATA)
        if not cont or cont == "All"
        else sum(1 for c in CITIES_DATA if c["continent"] == cont)
    )
    label = html.Span(
        [html.Span(str(n), className="count-num"), " cities shown"],
        className="counter-inner",
    )
    return fig, label


@app.callback(
    Output("city-content", "children"),
    Output("city-panel", "className"),
    Input("globe", "clickData"),
    Input("close-btn", "n_clicks"),
    prevent_initial_call=True,
)
def handle_panel(click_data, _close):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "close-btn":
        return html.Div(), "city-panel hidden"

    if trigger == "globe" and click_data:
        pts = click_data.get("points", [])
        if not pts:
            return no_update, no_update
        pt = pts[0]
        raw = pt.get("customdata")
        if raw is None:
            return no_update, no_update
        try:
            city = json.loads(raw)
            return build_city_panel(city), "city-panel visible"
        except (json.JSONDecodeError, KeyError):
            return no_update, no_update

    return no_update, no_update


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)

"""
World Globe Explorer — Premium 3D Globe v2
Natural Space View · Rich Hover Stats · City Detail Modal · CSV Export
"""

import csv
import io
import json
import os

import dash
from dash import Input, Output, State, ctx, dcc, html, no_update
import plotly.graph_objects as go

from data.cities_data import CITIES_DATA, CONTINENT_COLORS, CONTINENT_EMOJIS

# ─── App Init ─────────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    title="🌍 World Globe Explorer",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:ital,wght@0,300;0,400;0,600;1,300&display=swap"
    ],
)
server = app.server

# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt_pop(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def pop_bar(n: int, width: int = 14) -> str:
    """Unicode block bar — used inside hover tooltips."""
    filled = max(1, min(width, round(n / 22_000_000 * width)))
    return "█" * filled + "░" * (width - filled)


def hex_rgba(hex_color: str, opacity: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


# ─── Globe Figure ─────────────────────────────────────────────────────────────

def build_figure(view_mode: str = "globe", continent: str = "All") -> go.Figure:
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

        lats  = [c["lat"] for c in grp]
        lons  = [c["lon"] for c in grp]
        sizes = [max(9, min(24, c["population"] / 850_000 * 2.3)) for c in grp]

        hover = [
            (
                f"<b style='font-size:15px;color:{color}'>{c['flag']}  {c['name']}</b><br>"
                f"<span style='color:#99bbcc;font-size:12px'>{c['country']}  ·  {c['continent']}</span>"
                f"<br><br>"
                f"<span style='color:#6090a8;font-size:10px;letter-spacing:1px'>POPULATION</span><br>"
                f"<span style='color:{color};font-size:11px'>{pop_bar(c['population'])}</span>"
                f"  <b style='color:#ddeeff;font-size:12px'>{fmt_pop(c['population'])}</b>"
                f"<br><br>"
                f"<span style='color:#6090a8;font-size:10px;letter-spacing:1px'>FAMOUS FOR</span><br>"
                f"<span style='color:#c0ddf0;font-size:12px'>{c['best_known_for'][:65]}</span>"
                f"<br><br>"
                f"<span style='color:#6090a8;font-size:10px;letter-spacing:1px'>TOP ATTRACTION</span><br>"
                f"<span style='color:#e8f4ff;font-size:12px'>⭐  {c['top_attractions'][0]}</span>"
                f"<br><br>"
                f"<span style='color:{color};font-size:10px;font-style:italic'>"
                f"Click for full details &amp; CSV export  ›</span>"
            )
            for c in grp
        ]

        fig.add_trace(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=color,
                    opacity=0.93,
                    line=dict(color="rgba(255,255,255,0.55)", width=1.5),
                ),
                name=CONTINENT_EMOJIS.get(cont, "") + "  " + cont,
                hovertext=hover,
                hoverinfo="text",
                hoverlabel=dict(
                    bgcolor="rgba(3,12,28,0.97)",
                    bordercolor=color,
                    font=dict(color="#ddeeff", size=12, family="Exo 2"),
                    namelength=0,
                ),
                customdata=[json.dumps(c) for c in grp],
                showlegend=True,
            )
        )

    # ── Natural Earth colours ──────────────────────────────────────────────
    geo = dict(
        showland=True,        landcolor="#2d5e1e",
        showocean=True,       oceancolor="#12345e",
        showcountries=True,   countrycolor="#3a7028",  countrywidth=0.5,
        showcoastlines=True,  coastlinecolor="#4a9040", coastlinewidth=0.7,
        showlakes=True,       lakecolor="#1a4972",
        showrivers=True,      rivercolor="#1a4972",     riverwidth=0.4,
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        resolution=50,
    )

    if view_mode == "globe":
        geo.update(
            projection=dict(type="orthographic", rotation=dict(lon=15, lat=15, roll=0))
        )
    else:
        geo.update(
            projection=dict(type="natural earth"),
            lataxis=dict(range=[-85, 85]),
            lonaxis=dict(range=[-180, 180]),
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=geo,
        legend=dict(
            x=0.01, y=0.99, xanchor="left", yanchor="top",
            bgcolor="rgba(2,10,22,0.82)",
            bordercolor="rgba(0,200,255,0.22)", borderwidth=1,
            font=dict(color="#b0cce0", size=11, family="Exo 2"),
            title=dict(text="<b>Continents</b>",
                       font=dict(color="#60b0e8", size=11, family="Exo 2")),
            tracegroupgap=3,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        uirevision=view_mode,
    )
    return fig


# ─── Modal Charts ─────────────────────────────────────────────────────────────

def build_pop_chart(city: dict) -> go.Figure:
    cont_cities = sorted(
        [c for c in CITIES_DATA if c["continent"] == city["continent"]],
        key=lambda x: x["population"],
    )
    color = CONTINENT_COLORS.get(city["continent"], "#00d2ff")
    bar_colors = [
        color if c["name"] == city["name"] else "rgba(30,55,90,0.65)"
        for c in cont_cities
    ]

    fig = go.Figure(
        go.Bar(
            y=[c["name"] for c in cont_cities],
            x=[c["population"] for c in cont_cities],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[fmt_pop(c["population"]) for c in cont_cities],
            textposition="outside",
            textfont=dict(color="#8aafc8", size=10),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8aafc8", family="Exo 2", size=11),
        margin=dict(l=0, r=55, t=36, b=0),
        height=max(200, len(cont_cities) * 38),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#b0cce0")),
        title=dict(
            text=f"Population — {city['continent']}",
            font=dict(color="#60b0e8", size=12, family="Exo 2"),
            x=0,
        ),
        bargap=0.35,
    )
    return fig


def build_attraction_chart(city: dict) -> go.Figure:
    color = CONTINENT_COLORS.get(city["continent"], "#00d2ff")
    attrs = city["top_attractions"]
    short = [a[:22] + "…" if len(a) > 22 else a for a in attrs]
    scores = [95, 88, 80, 73, 65][: len(attrs)]
    opacities = [0.95, 0.82, 0.70, 0.58, 0.46][: len(attrs)]
    bar_colors = [hex_rgba(color, op) for op in opacities]

    fig = go.Figure(
        go.Bar(
            x=short,
            y=scores,
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{s}" for s in scores],
            textposition="outside",
            textfont=dict(color="#8aafc8", size=10),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8aafc8", family="Exo 2", size=10),
        margin=dict(l=0, r=0, t=36, b=0),
        height=260,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=9, color="#8aafc8"),
            tickangle=-18,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
            showticklabels=False, zeroline=False, range=[0, 115],
        ),
        title=dict(
            text="Attraction Popularity Score",
            font=dict(color="#60b0e8", size=12, family="Exo 2"),
            x=0,
        ),
    )
    return fig


# ─── CSV Helpers ──────────────────────────────────────────────────────────────

def city_to_csv(city: dict) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Field", "Value"])
    w.writerows([
        ("City",          city["name"]),
        ("Country",       city["country"]),
        ("Continent",     city["continent"]),
        ("Population",    city["population"]),
        ("Latitude",      city["lat"]),
        ("Longitude",     city["lon"]),
        ("Language",      city["language"]),
        ("Currency",      city["currency"]),
        ("Timezone",      city["timezone"]),
        ("Founded",       city.get("founded", "Unknown")),
        ("Famous For",    city["best_known_for"]),
        ("Top Attractions", " | ".join(city["top_attractions"])),
        ("Fun Facts",     " | ".join(city.get("fun_facts", []))),
    ])
    return out.getvalue()


def all_cities_csv() -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow([
        "City", "Country", "Continent", "Population",
        "Latitude", "Longitude", "Language", "Currency",
        "Timezone", "Founded", "Famous For",
    ])
    for c in CITIES_DATA:
        w.writerow([
            c["name"], c["country"], c["continent"], c["population"],
            c["lat"], c["lon"], c["language"], c["currency"],
            c["timezone"], c.get("founded", "Unknown"), c["best_known_for"],
        ])
    return out.getvalue()


# ─── UI Building Blocks ───────────────────────────────────────────────────────

def stat_chip(icon: str, label: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Span(icon, className="chip-icon"),
            html.Div(
                [html.Span(label, className="chip-label"),
                 html.Span(value, className="chip-value")],
                className="chip-text",
            ),
        ],
        className="stat-chip",
    )


def build_modal_body(city: dict) -> html.Div:
    color = CONTINENT_COLORS.get(city["continent"], "#00d2ff")
    pop_pct = min(100, city["population"] / 22_000_000 * 100)

    return html.Div(
        [
            # ── Hero ────────────────────────────────────────────────────
            html.Div(
                [
                    html.Div(city["flag"], className="hero-flag",
                             style={"filter": f"drop-shadow(0 0 14px {color})"}),
                    html.Div(
                        [
                            html.H1(city["name"], className="hero-city"),
                            html.Div(
                                [
                                    html.Span(city["country"], className="hero-country"),
                                    html.Span("·", className="hero-dot"),
                                    html.Span(city["continent"], className="hero-continent",
                                              style={"color": color}),
                                ],
                                className="hero-meta",
                            ),
                        ],
                        className="hero-text",
                    ),
                ],
                className="modal-hero",
                style={"borderBottomColor": color + "44"},
            ),

            # ── Description ─────────────────────────────────────────────
            html.P(city["description"], className="modal-desc"),

            # ── Tags ────────────────────────────────────────────────────
            html.Div(
                [
                    html.Span(t.strip(), className="tag",
                              style={"borderColor": color + "66"})
                    for t in city["best_known_for"].split(",")
                ],
                className="tags-row",
            ),

            # ── Population bar ──────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [html.Span("Population", className="bar-label"),
                         html.Span(f"{city['population']:,}", className="bar-number",
                                   style={"color": color})],
                        className="bar-row",
                    ),
                    html.Div(
                        html.Div(style={
                            "width": f"{pop_pct:.0f}%", "height": "100%",
                            "background": f"linear-gradient(90deg,{color}cc,{color}44)",
                            "borderRadius": "4px",
                            "transition": "width 1.2s cubic-bezier(0.4,0,0.2,1)",
                        }),
                        className="pop-bar",
                    ),
                ],
                className="pop-section",
            ),

            # ── Stats chips ─────────────────────────────────────────────
            html.Div(
                [
                    stat_chip("👥", "Population", fmt_pop(city["population"])),
                    stat_chip("🗣", "Language",   city["language"]),
                    stat_chip("💱", "Currency",   city["currency"]),
                    stat_chip("🕐", "Timezone",   city["timezone"]),
                    stat_chip("📅", "Founded",    city.get("founded", "Ancient")),
                    stat_chip("🌍", "Continent",  city["continent"]),
                ],
                className="modal-stats",
            ),

            # ── Charts row ──────────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Population Comparison", className="chart-title"),
                            dcc.Graph(
                                figure=build_pop_chart(city),
                                config={"displayModeBar": False},
                                style={"height": "100%"},
                            ),
                        ],
                        className="chart-box",
                    ),
                    html.Div(
                        [
                            html.P("Top Attraction Scores", className="chart-title"),
                            dcc.Graph(
                                figure=build_attraction_chart(city),
                                config={"displayModeBar": False},
                                style={"height": "100%"},
                            ),
                        ],
                        className="chart-box",
                    ),
                ],
                className="charts-row",
            ),

            # ── Top Attractions ─────────────────────────────────────────
            html.Div(
                [
                    html.H3([html.Span("🏛  ", className="sec-icon"), "Top Attractions"],
                            className="sec-title", style={"color": color}),
                    html.Ul(
                        [html.Li([html.Span("✦  ", style={"color": color}), a],
                                 className="attr-item")
                         for a in city["top_attractions"]],
                        className="attr-list",
                    ),
                ],
                className="modal-section",
            ),

            # ── Fun Facts ───────────────────────────────────────────────
            html.Div(
                [
                    html.H3([html.Span("💡  ", className="sec-icon"), "Fun Facts"],
                            className="sec-title", style={"color": color}),
                    html.Ul(
                        [html.Li(f, className="fact-item")
                         for f in city.get("fun_facts", [])],
                        className="facts-list",
                    ),
                ],
                className="modal-section",
            ) if city.get("fun_facts") else html.Div(),
        ],
        className="modal-content-inner",
    )


# ─── Layout ───────────────────────────────────────────────────────────────────

CONTINENT_FILTER_OPTIONS = [
    {"label": "🌐  All",         "value": "All"},
    {"label": "🌏  Asia",        "value": "Asia"},
    {"label": "🌍  Europe",      "value": "Europe"},
    {"label": "🌎  N. America",  "value": "North America"},
    {"label": "🌎  S. America",  "value": "South America"},
    {"label": "🌍  Africa",      "value": "Africa"},
    {"label": "🌏  Oceania",     "value": "Oceania"},
]

app.layout = html.Div(
    [
        # ── Header ──────────────────────────────────────────────────────────
        html.Header(
            [
                html.Div(
                    [
                        html.Span("🌍", className="logo"),
                        html.Div(
                            [
                                html.H1("World Globe Explorer", className="app-title"),
                                html.P(
                                    "Hover any city for stats  ·  Click for full details & CSV export",
                                    className="app-subtitle",
                                ),
                            ]
                        ),
                    ],
                    className="header-brand",
                ),
                html.Div(
                    [
                        html.Div([html.Span(str(len(CITIES_DATA)), className="stat-num"),
                                  html.Span("Cities", className="stat-lbl")],
                                 className="hdr-stat"),
                        html.Div([html.Span(str(len(CONTINENT_COLORS)), className="stat-num"),
                                  html.Span("Continents", className="stat-lbl")],
                                 className="hdr-stat"),
                    ],
                    className="header-stats",
                ),
            ],
            className="app-header",
        ),

        # ── Controls ────────────────────────────────────────────────────────
        html.Div(
            [
                html.Div(
                    [
                        html.Button("⬤  3D Globe", id="btn-globe",
                                    className="view-btn active", n_clicks=0),
                        html.Button("🗺  Flat Map", id="btn-map",
                                    className="view-btn", n_clicks=0),
                    ],
                    className="toggle-group",
                ),
                dcc.RadioItems(
                    id="continent-filter",
                    options=CONTINENT_FILTER_OPTIONS,
                    value="All",
                    className="continent-pills",
                    inputClassName="pill-radio",
                    labelClassName="pill-label",
                ),
                html.Div(className="spacer"),
                html.Button("📊  Export All Cities",
                            id="export-all-btn", className="export-btn", n_clicks=0),
                dcc.Download(id="download-all-csv"),
            ],
            className="controls-bar",
        ),

        # ── Globe ────────────────────────────────────────────────────────────
        html.Div(
            dcc.Graph(
                id="globe",
                figure=build_figure(),
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                    "toImageButtonOptions": {
                        "format": "png", "filename": "world_globe",
                        "height": 900, "width": 1400, "scale": 2,
                    },
                },
                style={"height": "100%", "width": "100%"},
                responsive=True,
            ),
            className="globe-wrap",
        ),

        # ── City Detail Modal ────────────────────────────────────────────────
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.Button("← Back to Globe", id="close-modal-btn",
                                        className="back-btn", n_clicks=0),
                            html.Button("💾  Export City CSV", id="export-city-btn",
                                        className="export-city-btn", n_clicks=0),
                            dcc.Download(id="download-city-csv"),
                        ],
                        className="modal-topbar",
                    ),
                    html.Div(id="modal-body", className="modal-body"),
                ],
                className="modal-card",
            ),
            id="city-modal",
            className="modal-overlay hidden",
        ),

        # ── Stores ───────────────────────────────────────────────────────────
        dcc.Store(id="view-store", data="globe"),
        dcc.Store(id="city-store", data=None),
    ],
    className="root",
)


# ─── Callbacks ────────────────────────────────────────────────────────────────

@app.callback(
    Output("view-store", "data"),
    Output("btn-globe", "className"),
    Output("btn-map",   "className"),
    Input("btn-globe", "n_clicks"),
    Input("btn-map",   "n_clicks"),
    prevent_initial_call=True,
)
def switch_view(_gc, _mc):
    if ctx.triggered_id == "btn-globe":
        return "globe", "view-btn active", "view-btn"
    return "flat", "view-btn", "view-btn active"


@app.callback(
    Output("globe", "figure"),
    Input("view-store",       "data"),
    Input("continent-filter", "value"),
)
def refresh_globe(view, continent):
    return build_figure(
        view_mode=view or "globe",
        continent=continent or "All",
    )


@app.callback(
    Output("city-store",   "data"),
    Output("city-modal",   "className"),
    Input("globe",         "clickData"),
    Input("close-modal-btn", "n_clicks"),
    prevent_initial_call=True,
)
def handle_click(click_data, _close):
    if ctx.triggered_id == "close-modal-btn":
        return no_update, "modal-overlay hidden"

    if ctx.triggered_id == "globe" and click_data:
        pts = click_data.get("points", [])
        if pts and "customdata" in pts[0]:
            return pts[0]["customdata"], "modal-overlay visible"

    return no_update, no_update


@app.callback(
    Output("modal-body", "children"),
    Input("city-store",  "data"),
    prevent_initial_call=True,
)
def update_modal(city_json):
    if not city_json:
        return html.Div()
    city = json.loads(city_json) if isinstance(city_json, str) else city_json
    return build_modal_body(city)


@app.callback(
    Output("download-city-csv", "data"),
    Input("export-city-btn",    "n_clicks"),
    State("city-store",         "data"),
    prevent_initial_call=True,
)
def export_city(n, city_json):
    if not n or not city_json:
        return no_update
    city = json.loads(city_json) if isinstance(city_json, str) else city_json
    fname = city["name"].lower().replace(" ", "_") + "_data.csv"
    return dict(content=city_to_csv(city), filename=fname)


@app.callback(
    Output("download-all-csv", "data"),
    Input("export-all-btn",    "n_clicks"),
    prevent_initial_call=True,
)
def export_all(n):
    if not n:
        return no_update
    return dict(content=all_cities_csv(), filename="world_cities_data.csv")


# ─── Entry ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

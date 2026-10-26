"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sit_constants as C
import sit_evaluation as ev


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.28), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_seats(a):
    """Sitze je Verband und Verfahren (gruppierte Säulen); die exakte Quote als Raute. Säulen, die die Quotenregel verletzen, haben einen roten Rand."""
    fig = go.Figure()
    xs = [ev.label(i) for i in range(a.k)]
    for m in ev.METHODS:
        s = a.seats[m]
        if s is None:
            continue
        bad = dict(a.violations[m])
        fig.add_trace(go.Bar(
            x=xs, y=s, name=C.METHOD_SHORT[m], marker_color=C.METHOD_COLORS[m],
            marker_line_color=[C.COLOR_ALERT if i in bad else "rgba(0,0,0,0)" for i in range(a.k)], marker_line_width=[3 if i in bad else 0 for i in range(a.k)],
            hovertemplate="%{x}: %{y} Sitze<extra>" + C.METHOD_SHORT[m] + "</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[float(q) for q in a.quotas], mode="markers", name="Quote (exakt)", marker=dict(symbol="diamond", size=10, color="#222", line=dict(color="white", width=1)),
                             hovertemplate="%{x}: Quote %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Sitze")
    fig.update_xaxes(title_text="Verband (roter Rand: Quotenregel verletzt)")
    return _base(fig, height=400)


def build_deviation(a):
    """Sitze minus Quote je Verband: innerhalb des Bandes von −1 bis +1 gilt die Quotenregel."""
    fig = go.Figure()
    xs = [ev.label(i) for i in range(a.k)]
    for m in ev.METHODS:
        if a.seats[m] is None:
            continue
        fig.add_trace(go.Bar(x=xs, y=[float(a.seats[m][i] - a.quotas[i]) for i in range(a.k)], name=C.METHOD_SHORT[m], marker_color=C.METHOD_COLORS[m],
                             hovertemplate="%{x}: %{y:+.2f}<extra>" + C.METHOD_SHORT[m] + "</extra>"))
    for y in (-1, 1):
        fig.add_hline(y=y, line_color="rgba(128,128,128,0.7)", line_dash="dot")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Sitze minus Quote")
    fig.update_xaxes(title_text="Verband")
    return _base(fig, height=340)


def build_history(a, i):
    """Sitze minus Quote des Verbands i über der Hausgröße, je Verfahren eine Linie; rote Kreuze: dort verliert der Verband beim Schritt zum nächsten Haus einen Sitz."""
    fig = go.Figure()
    hs = list(range(a.k, C.SCAN_MAX + 1))
    for m in ev.METHODS:
        ys = [None if a.seqs[m][h - 1] is None else float(ev.deviation(a, m, i, h)) for h in hs]
        fig.add_trace(go.Scatter(x=hs, y=ys, mode="lines", name=C.METHOD_SHORT[m], line=dict(color=C.METHOD_COLORS[m], width=2, shape="hv"),
                                 hovertemplate="%{x} Sitze im Haus: %{y:+.2f}<extra>" + C.METHOD_SHORT[m] + "</extra>"))
        marks = [(h + 1, float(ev.deviation(a, m, i, h + 1))) for (h, v, _, _) in a.losses[m] if v == i]
        if marks:
            fig.add_trace(go.Scatter(x=[x for x, _ in marks], y=[y for _, y in marks], mode="markers", name=f"Verlust ({C.METHOD_SHORT[m]})", marker=dict(symbol="x", size=9, color=C.COLOR_ALERT),
                                     hovertemplate="Bei %{x} Sitzen im Haus ein Sitz weniger als davor<extra></extra>"))
    for y in (-1, 1):
        fig.add_hline(y=y, line_color="rgba(128,128,128,0.7)", line_dash="dot")
    if a.k <= a.h <= C.SCAN_MAX:
        fig.add_vline(x=a.h, line_color=C.COLOR_ALERT, line_dash="dash", annotation_text=f"h = {a.h}", annotation_position="top left")
    fig.update_xaxes(title_text="Sitze im Haus (Hausgröße)")
    fig.update_yaxes(title_text=f"Sitze von {ev.label(i)} minus Quote")
    return _base(fig, height=400)


def _grouped(x, series, y_title, x_title, fmt=".0%", height=340):
    """Gruppierte Säulen: je Verfahren eine Säule je x-Wert; `series[m]` ist die Liste der Anteile."""
    fig = go.Figure()
    for m in ev.METHODS:
        fig.add_trace(go.Bar(x=x, y=series[m], name=C.METHOD_SHORT[m], marker_color=C.METHOD_COLORS[m], hovertemplate="%{x}: %{y:" + fmt + "}<extra>" + C.METHOD_SHORT[m] + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=y_title, tickformat=fmt, rangemode="tozero")
    fig.update_xaxes(title_text=x_title, type="category")
    return _base(fig, height=height)


def build_alabama_series(rows):
    return _grouped([f"{r['k']} Verbände" for r in rows], {m: [r["inst"][m] / r["runs"] for r in rows] for m in ev.METHODS}, "Instanzen mit mindestens einem Sitzverlust", "Zahl der Verbände")


def build_quota_series(rows):
    return _grouped([f"{r['h']} Sitze" for r in rows], {m: [r["viol"][m] / r["runs"] for r in rows] for m in ev.METHODS}, "Instanzen mit Quotenverstoß", f"Hausgröße ({rows[0]['k']} Verbände)")


def build_paradox_series(rows):
    return _grouped([f"{r['h']} Sitze" for r in rows], {m: [r["paradox"][m] / r["runs"] for r in rows] for m in ev.METHODS}, "Instanzen mit Bevölkerungsparadox", f"Hausgröße ({rows[0]['k']} Verbände)")

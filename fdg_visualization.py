"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import fdg_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_layers(sizes: list):
    """Zahl der Zustände (Knoten) je Schicht des Diagramms: eine Schicht je Kante."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(len(sizes))), y=sizes, name="Knoten der Schicht", marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Schicht (Nummer der Kante in der Ordnung)")
    fig.update_yaxes(title_text="Zahl der Zustände")
    return _base(fig, 300)


def build_size(res: dict):
    """Lösungen gegen Diagrammknoten für die Wege im n×n-Gitter (logarithmische Achse)."""
    fig = go.Figure()
    ns = [int(r["Gitter"].split("×")[0]) for r in res["paths"]]
    fig.add_trace(go.Scatter(x=ns, y=[r["Lösungen"] for r in res["paths"]], mode="lines+markers", name="Wege", line=dict(color=C.COLOR_WARN)))
    fig.add_trace(go.Scatter(x=ns, y=[r["Knoten"] for r in res["paths"]], mode="lines+markers", name="Diagrammknoten (reduziert)", line=dict(color=C.COLOR_MAIN)))
    fig.add_trace(go.Scatter(x=ns, y=[r["Zustände"] for r in res["paths"]], mode="lines+markers", name="Zustände", line=dict(color=C.COLOR_LINE, dash="dot")))
    fig.update_xaxes(title_text="Seitenlänge n des n×n-Gitters")
    fig.update_yaxes(title_text="Zahl", type="log")
    return _base(fig, 360)


def build_order(rows: list):
    """Zustände in Zeilenordnung gegen schlechte Ordnung je Aufgabe und Gitter (logarithmische Achse)."""
    fig = go.Figure()
    xs = [f"{r['Aufgabe'].split()[-1]} {r['Gitter']}" for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["zeile"]["Zustände"] for r in rows], name="Zeilenordnung", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=xs, y=[r["schlecht"]["Zustände"] for r in rows], name="schlechte Ordnung", marker_color=C.COLOR_WARN))
    fig.update_yaxes(title_text="Zustände", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 340)


def build_beam(row: dict):
    """Untere und obere Schranke für den längsten Weg gegen die Breite, mit dem exakten Wert."""
    fig = go.Figure()
    ws = [r["Breite"] for r in row["Reihe"] if r["untere"] is not None]
    fig.add_trace(go.Scatter(x=ws, y=[r["untere"] for r in row["Reihe"] if r["untere"] is not None], mode="lines+markers", name="untere Schranke", line=dict(color=C.COLOR_MAIN)))
    fig.add_trace(go.Scatter(x=ws, y=[r["obere"] for r in row["Reihe"] if r["untere"] is not None], mode="lines+markers", name="obere Schranke", line=dict(color=C.COLOR_WARN)))
    fig.add_hline(y=row["exakt"], line=dict(color=C.COLOR_ALL, dash="dash"))
    fig.update_xaxes(title_text="Breite (Zustände je Schicht)", type="log")
    fig.update_yaxes(title_text=f"längster Weg im {row['n']}×{row['n']}-Gitter")
    return _base(fig, 320)

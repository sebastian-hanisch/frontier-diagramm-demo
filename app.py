"""Frontier und Entscheidungsdiagramm – wenn die Struktur kein Baukasten ist - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 13 der Reihe „Abzählen und erzeugende Funktionen“: Was tun, wenn die Struktur kein Baukasten ist? Die Frontier-Methode entscheidet die Kanten eines Gitters der Reihe nach und merkt sich nur, was die Frontier über den Rest
wissen muss; gleiche Zustände fallen zusammen, es entsteht ein Entscheidungsdiagramm, das weit kleiner ist als die Lösungszahl. Auf demselben Diagramm: Zählen, kleinstes und größtes Gewicht, Zahl der Optimalen, Ziehen und Schranken bei begrenzter Breite.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import fdg_constants as C
from fdg_evaluation import (
    Settings,
    analyse,
    beam_rows,
    big_text,
    check_rows,
    de,
    factor_text,
    order_rows,
    per_node_text,
    play_grid,
    semiring_rows,
    size_rows,
    verdict_answers,
    verdict_beam,
    verdict_check,
    verdict_order,
    verdict_play,
    verdict_semiring,
    verdict_size,
)
from fdg_layout import dunkles_design, kopf_css
from fdg_pdf_export import build_pdf
from fdg_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from fdg_visualization import build_beam, build_layers, build_order, build_size

st.set_page_config(page_title="Frontier und Diagramm – Sebastian Hanisch", layout="wide")

SPINNER = "Die Experimente werden einmal gerechnet …"


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=SPINNER)
def _sizes():
    return size_rows()


@st.cache_data(show_spinner=SPINNER)
def _checks():
    return check_rows()


@st.cache_data(show_spinner=SPINNER)
def _orders():
    return order_rows()


@st.cache_data(show_spinner=SPINNER)
def _semiring():
    return semiring_rows()


@st.cache_data(show_spinner=SPINNER)
def _beam():
    return beam_rows()


@st.cache_data(show_spinner=False)
def _play(rows, cols, seed):
    return play_grid(rows, cols, seed)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in fdg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🕸️ Frontier und Diagramm – wenn die Struktur kein Baukasten ist")
st.markdown(
    """
**Was tun, wenn die Struktur kein Baukasten ist?** Stück 3 bis 12 haben Strukturen **gebaut** (Gleichung, Tabelle, Symmetrie). **Einfache Wege** von Ecke zu Ecke im Gitter, **perfekte Paarungen** und **Spannbäume** sind Teilgraphen mit einer Nebenbedingung,
für die es keinen Baukasten gibt. Die **Frontier-Methode** (Simpath von Knuth) entscheidet die Kanten der Reihe nach und merkt sich nur, **was die Frontier über den Rest wissen muss**; **gleiche Zustände fallen zusammen**. Heraus kommt ein
**Entscheidungsdiagramm**: ein azyklischer Graph mit zwei Kindern je Knoten, jeder Weg von oben nach unten ist eine Lösung. Es ist **weit kleiner als die Lösungszahl**, und auf demselben Diagramm rechnet man **Zahl, Optimum, Zahl der Optimalen und Ziehen**
(Semiring, Stück 4 und 10). Mit **begrenzter Breite** entstehen Schranken. Die **Kantenordnung** entscheidet über die Größe.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Frontier-Methode", expanded=True):
    st.markdown(
        """
1. **Kanten ordnen:** Die Kanten werden der Reihe nach entschieden (nein oder ja). Die **Frontier** sind die Knoten, an denen schon eine, aber noch nicht alle Kanten entschieden sind.
2. **Zustand:** Er merkt sich, was die Frontier für den Rest braucht: bei Wegen für jeden Frontier-Knoten das andere Ende seines Teilwegs, bei Paarungen, welche Knoten schon gepaart sind, bei Spannbäumen die Zusammenhangskomponenten.
3. **Zusammenfallen:** Zwei Teilentscheidungen mit demselben Zustand haben dieselben Fortsetzungen: sie werden ein Knoten. Unmögliche Fortsetzungen (Kreis, drei Kanten an einem Knoten) fallen weg.
4. **Auswerten:** Von unten nach oben mit einem Semiring: (+, ×) zählt, (min, +) findet den kürzesten Weg, mit Zahl der Optimalen, (max, +) den längsten; mit den Zählungen zieht man gleichverteilt.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    task = st.selectbox("Aufgabe", list(C.TASKS), key="task_select", help="Einfache Wege von der oberen linken zur unteren rechten Ecke, perfekte Paarungen (Dominosteine) oder Spannbäume des Gitters.")
    rows = st.slider("Zeilen", *bounds("rows_slider"), key="rows_slider", help=f"Knoten je Spalte. Höchstens {C.SIDE_CAP['Einfache Wege']} (Wege), {C.SIDE_CAP['Perfekte Paarungen']} (Paarungen) oder {C.SIDE_CAP['Spannbäume']} (Spannbäume).")
    cols = st.slider("Spalten", *bounds("cols_slider"), key="cols_slider", help="Knoten je Zeile.")
    order = st.selectbox("Kantenordnung", list(C.ORDERS), key="order_select", help="Zeilenordnung und Spaltenordnung halten die Frontier schmal, die schlechte Ordnung (erst alle waagerechten Kanten) macht sie so breit wie das Gitter; nur bis 24 Kanten.")
    st.markdown("**Gewichte und Breite (nur Wege)**")
    seed = st.slider("Seed der Gewichte", *bounds("seed_slider"), key="seed_slider", help="Gewichte 1 bis 9 je Kante, gezogen mit diesem Seed; sie sind von der Kantenordnung unabhängig.")
    width = st.slider("Breite für die Schranken", *bounds("width_slider"), key="width_slider", help="Höchstens so viele Zustände je Schicht bleiben für den längsten Weg (untere und obere Schranke).")

sync_query_params({"task_select": task, "rows_slider": int(rows), "cols_slider": int(cols), "order_select": order, "seed_slider": int(seed), "width_slider": int(width)})

settings = Settings(task, int(rows), int(cols), order, int(seed), int(width))
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Lösungen", big_text(a.solutions), help="Zahl der Wege, Paarungen oder Spannbäume, gezählt auf dem Diagramm.")
m2.metric("Diagrammknoten (reduziert)", big_text(a.zdd), help=f"Knoten des reduzierten ZDD; vor der Reduktion {big_text(a.states)} Zustände.")
m3.metric("Lösungen je Knoten", "–" if not a.solutions else per_node_text(a.solutions, a.zdd), help="Lösungen geteilt durch Diagrammknoten: wie viel das Zusammenfassen spart.")
m4.metric("Größte Frontier", str(a.frontier), help="Wie viele Knoten gleichzeitig angefangen und noch nicht fertig sind; sie bestimmt, wie groß das Diagramm werden kann.")
st.plotly_chart(build_layers(a.layer_sizes), width="stretch", key="main_chart")
st.caption("Zahl der Zustände je Schicht (eine Schicht je Kante): das Diagramm wächst, bis die Frontier voll ist, und schrumpft am Ende.")
st.dataframe(a.ways, hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="frontier-diagramm.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was tun, wenn die Struktur kein Baukasten ist?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Das Diagramm ist weit kleiner als die Lösungszahl")
st.caption("Einfache Wege im n×n-Gitter, perfekte Paarungen und Spannbäume: Lösungen, Zustände (Knoten vor der Reduktion) und reduzierte Diagrammknoten.")
sizes = _sizes()
st.plotly_chart(build_size(sizes), width="stretch", key="size_chart")
for name, key in (("Einfache Wege", "paths"), ("Perfekte Paarungen", "matchings"), ("Spannbäume", "trees")):
    st.markdown(f"**{name}**")
    st.dataframe([{"Gitter": r["Gitter"], "Kanten": r["Kanten"], "Frontier": r["Frontier"], "Lösungen": big_text(r["Lösungen"]), "Zustände": big_text(r["Zustände"]), "Diagrammknoten": big_text(r["Knoten"]), "Lösungen je Knoten": per_node_text(r["Lösungen"], r["Knoten"])} for r in sizes[key]],
                 hide_index=True, width="stretch")
verdict(verdict_size(sizes))

st.markdown("---")

st.subheader("🔬 Experiment 2: Dieselben Zahlen auf anderen Wegen")
st.caption("Brute Force (Rückverfolgung aller Wege), die Folge der Wege im n×n-Gitter aus dem Gedächtnis, Kasteleyn (Paarungen) und Kirchhoff (Spannbäume): vier unabhängige Prüfwege.")
checks = _checks()
st.dataframe([{"Aufgabe": r["Aufgabe"], "Gitter": r["Gitter"], "Diagramm": big_text(r["Diagramm"]), "Prüfweg": r["Prüfweg"], "Prüfwert": big_text(r["Prüfwert"]), "gleich": "ja" if r["gleich"] else "nein"} for r in checks], hide_index=True, width="stretch")
verdict(verdict_check(checks))

st.markdown("---")

st.subheader("🔬 Experiment 3: Die Kantenordnung entscheidet")
st.caption("Dieselben Lösungen, zwei Kantenordnungen: Zeilenordnung (Frontier = Zeilenlänge + 1) gegen erst alle waagerechten, dann alle senkrechten Kanten (Frontier = alle Knoten).")
orders = _orders()
st.plotly_chart(build_order(orders), width="stretch", key="order_chart")
st.dataframe([{"Aufgabe": r["Aufgabe"], "Gitter": r["Gitter"], "Lösungen": big_text(r["zeile"]["Lösungen"]), "Frontier Zeile": r["zeile"]["Frontier"], "Frontier schlecht": r["schlecht"]["Frontier"], "Zustände Zeile": big_text(r["zeile"]["Zustände"]),
               "Zustände schlecht": big_text(r["schlecht"]["Zustände"]), "Knoten Zeile": big_text(r["zeile"]["Knoten"]), "Knoten schlecht": big_text(r["schlecht"]["Knoten"])} for r in orders], hide_index=True, width="stretch")
verdict(verdict_order(orders))

st.markdown("---")

st.subheader("🔬 Experiment 4: Ein Diagramm, vier Auswertungen, und Ziehen")
st.caption("Auf demselben Wegediagramm: Zahl der Wege (+, ×), kleinstes Gewicht und Zahl der kürzesten (min, +, Zahl), größtes Gewicht (max, +). Gewichte 1 bis 9 mit festem Seed; Dijkstra und Brute Force als Gegenprobe. Darunter das gleichverteilte Ziehen.")
sem = _semiring()
st.dataframe([{"n": r["n"], "Wege": big_text(r["Wege"]), "kleinstes Gewicht": r["kleinstes"], "Zahl der kleinsten": big_text(r["Zahl kleinste"]), "größtes Gewicht": r["größtes"], "Dijkstra gleich": "ja" if r["Dijkstra gleich"] else "nein",
               "Brute Force gleich": "–" if r["Brute gleich"] is None else ("ja" if r["Brute gleich"] else "nein")} for r in sem["rows"]], hide_index=True, width="stretch")
sm = sem["sample"]
st.dataframe([{"Gitter": f"{sm['n']}×{sm['n']}", "Wege": sm["total"], "Ziehungen": big_text(sm["draws"]), "Wege gezogen": sm["drawn"], "Chi-Quadrat": de(sm["chi"], 1), "z": de(sm["z"], 2)}], hide_index=True, width="stretch")
verdict(verdict_semiring(sem))

st.markdown("---")

st.subheader("🔬 Experiment 5: Begrenzte Breite, Schranken für den längsten Weg")
st.caption("Je Schicht bleiben nur die `Breite` besten Zustände: die untere Schranke ist ein zulässiger Weg, die obere nimmt abgeschnittene Zustände mit allen restlichen positiven Gewichten. Der exakte Wert kommt vom vollen Diagramm.")
beam = _beam()
for row in beam:
    st.plotly_chart(build_beam(row), width="stretch", key=f"beam_chart_{row['n']}")
    st.dataframe([{"Breite": r["Breite"], "untere Schranke": "–" if r["untere"] is None else r["untere"], "obere Schranke": "–" if r["obere"] is None else r["obere"],
                   "Abstand der unteren zum Optimum": "–" if r["untere"] is None else row["exakt"] - r["untere"]} for r in row["Reihe"]], hide_index=True, width="stretch")
verdict(verdict_beam(beam))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: ein Gitter mit Gewichten")
st.caption("Ein Gitter mit Gewichten 1 bis 9: ein gleichverteilt gezogener, der kürzeste und der längste einfache Weg von oben links nach unten rechts, als Textbild.")
q1, q2, q3 = st.columns(3)
pr = q1.slider("Zeilen", 2, C.GRAPH_DRAW_MAX, C.PLAY_ROWS_DEFAULT, key="play_rows", help="Knoten je Spalte.")
pc = q2.slider("Spalten", 2, C.GRAPH_DRAW_MAX, C.PLAY_COLS_DEFAULT, key="play_cols", help="Knoten je Zeile.")
ps = q3.slider("Seed", C.SEED_MIN, C.SEED_MAX, C.PLAY_SEED_DEFAULT, key="play_seed", help="Bestimmt die Gewichte und den gezogenen Weg.")
play = _play(int(pr), int(pc), int(ps))
cols3 = st.columns(3)
for col, (title, key) in zip(cols3, (("Gezogen (gleichverteilt)", "drawn"), ("Kürzester Weg", "shortest"), ("Längster Weg", "longest"))):
    col.markdown(f"**{title}**, Gewicht {play[key]['weight']}")
    col.code(play[key]["art"], language=None)
verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Frontier bleibt schmal** | Das Diagramm ist exponentiell in der Frontier: Wege im n×n-Gitter {big_text(1268340)} Knoten bei n = 11, bei n = 20 wären es hochgerechnet (Faktor 3,3 je Seitenlänge) grob einige zehn Milliarden. Gitter mit breiter Frontier (große Zusammenhangszahl) sind nicht mehr lösbar. | Experiment 1 |
| **Die Kantenordnung ist gut** | Dieselben Lösungen, aber in schlechter Ordnung riesig (Experiment 3); die beste Ordnung zu finden ist selbst schwer, die App kennt nur Zeile und Spalte. | Experiment 3 |
| **Der Zustand ist vollständig** | Der Zustand muss alles enthalten, was für die Fortsetzung zählt; ein vergessener Fall (zum Beispiel ein zweiter Teilweg neben dem fertigen) macht falsche Zahlen. Die Prüfwege zeigen es. | Experiment 2 |
| **Gewichte positiv** | Dijkstra und die Zählung der kürzesten Wege setzen positive Gewichte voraus; die App nimmt 1 bis 9. Mit negativen Gewichten sind kürzeste Wege nicht einfach. | – |
| **Die obere Schranke ist gut** | Die einfache obere Schranke (abgeschnittene Zustände plus alle restlichen positiven Gewichte) ist schwach; echte relaxierte Diagramme führen ähnliche Zustände zusammen und sind stärker (hier nicht gebaut). | Experiment 5 |
| **Es gibt eine Gitterstruktur** | Gebaut ist nur das Gitter; allgemeine Graphen brauchen eine Kantenordnung und haben eine andere Frontier. Der längste einfache Weg ist für allgemeine Graphen NP-schwer (Literaturwissen, hier nicht gezeigt); das Diagramm wächst im Gitter exponentiell in n (gemessen). | – |
| **Die Größe ist begrenzt** | Wege bis {C.SIDE_CAP['Einfache Wege']}×{C.SIDE_CAP['Einfache Wege']}, Paarungen bis {C.SIDE_CAP['Perfekte Paarungen']}×{C.SIDE_CAP['Perfekte Paarungen']}, Spannbäume bis {C.SIDE_CAP['Spannbäume']}×{C.SIDE_CAP['Spannbäume']}; die schlechte Ordnung nur bis {C.BAD_ORDER_EDGE_LIMIT} Kanten. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Frontier.** Sind die Kanten $e_1, \dots, e_m$ geordnet, ist die Frontier nach Kante $i$ die Menge der Knoten, an denen mindestens eine Kante unter $e_1, \dots, e_i$ und mindestens eine unter $e_{i+1}, \dots, e_m$ liegt. Eine Teilentscheidung $x_1, \dots, x_i \in \{0, 1\}$ hat als **Zustand** die Information über die Frontier, die für alle Fortsetzungen genügt; zwei Teilentscheidungen mit gleichem Zustand haben dieselben Fortsetzungen und werden ein Knoten. Die Schichtgröße ist höchstens die Zahl der möglichen Zustände (bei Paarungen $2^{|F|}$).

**Wege (Simpath).** Zustand: je Frontier-Knoten sein Partner (das andere Ende des Teilwegs), er selbst (Grad 0), $s$ oder $t$ (das andere Ende ist der geschlossene Start oder das Ziel) oder „fertig“ (Grad 2). Verboten: ein Kreis (beide Enden desselben Teilwegs), ein dritter Anschluss, ein offenes Ende, das die Frontier verlässt, ein unbenutzter Start oder ein unbenutztes Ziel.

**Paarungen und Spannbäume.** Paarungen: Menge der schon gepaarten Frontier-Knoten, jeder Knoten muss gepaart sein, bevor er die Frontier verlässt. Spannbäume: Komponentenmarken der Frontier-Knoten; ein Kreis entsteht, wenn beide Enden dieselbe Marke haben; eine Komponente darf die Frontier nur verlassen, wenn sie die letzte ist.

**Auswerten.** Mit einem Semiring $(\oplus, \otimes)$ ist der Wert eines Knotens $v$ gleich $\mathrm{lo}(v) \oplus (w_i \otimes \mathrm{hi}(v))$: $(+, \times)$ zählt, $(\min, +)$ liefert das kleinste Gewicht, mit Paaren (Gewicht, Zahl) auch die Zahl der kleinsten, $(\max, +)$ das größte. **Ziehen:** an jedem Knoten das Ja-Kind mit der Wahrscheinlichkeit (Lösungen darunter)/(Lösungen am Knoten).

**Kasteleyn und Kirchhoff.** Dominosteinparkettierungen des $m \times n$-Bretts: $\prod_{j=1}^{\lceil m/2 \rceil} \prod_{k=1}^{\lceil n/2 \rceil} \left(4\cos^2\frac{\pi j}{m+1} + 4\cos^2\frac{\pi k}{n+1}\right)$. Spannbäume eines Graphen: eine beliebige Hauptunterdeterminante der Laplace-Matrix.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
D. E. Knuth: *The Art of Computer Programming, Vol. 4A: Combinatorial Algorithms, Part 1*, Addison-Wesley, 2011, Abschnitt 7.1.4 (Simpath, ZDDs).
J. Kawahara, T. Inoue, H. Iwashita und S. Minato: *Frontier-based search for enumerating all constrained subgraphs with compressed representation*, IEICE Transactions on Fundamentals E100-A, 2017, S. 1773–1784.
S. Minato: *Zero-suppressed BDDs for set manipulation in combinatorial problems*, 30th Design Automation Conference, 1993, S. 272–277.
D. Bergman, A. A. Cire, W.-J. van Hoeve und J. Hooker: *Decision Diagrams for Optimization*, Springer, 2016.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)

"""Auswertung: die eingestellte Aufgabe mit Diagramm, Prüfwegen und Semiring, fünf Experimente, die Spielwiese und die Urteilstexte. Die Gewichte kommen aus festen Seeds."""

import functools
import math
import random
from dataclasses import dataclass, field

import fdg_algorithm as A
import fdg_constants as C

_SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


@dataclass(frozen=True)
class Settings:
    task: str
    rows: int
    cols: int
    order: str
    seed: int
    width: int


@dataclass
class Analysis:
    settings: Settings
    task: str
    rows: int
    cols: int
    order_key: str
    nv: int
    nedges: int
    frontier: int
    layer_sizes: list
    states: int
    zdd: int
    solutions: int
    ways: list
    sem: dict | None
    beam: dict | None
    problems: list
    notes: list


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def sci_text(x: float, digits: int = 2) -> str:
    if x == 0:
        return "0"
    if 0.01 <= abs(x) < 10000:
        return de(x, digits)
    mant, exp = f"{x:.{digits - 1}e}".split("e")
    return f"{mant.replace('.', ',').replace('-', '−')}·10{str(int(exp)).translate(_SUPER)}"


def factor_text(x: float) -> str:
    """Faktor: unter 10 mit zwei, bis 1000 mit einer Nachkommastelle, darüber ganzzahlig mit Tausenderpunkt."""
    if x < 10:
        return de(x, 2)
    if x < 1000:
        return de(x, 1)
    return f"{round(x):,}".replace(",", ".")


def per_node_text(solutions: int, nodes: int) -> str:
    """Lösungen je Diagrammknoten: ganzzahlig lesbar, bei sehr großen Zahlen als Zehnerpotenz (über Brüche, ohne Überlauf)."""
    q = solutions // nodes
    if q < 10 ** 6:
        whole, frac = f"{solutions / nodes:.1f}".split(".")
        return f"{int(whole):,}".replace(",", ".") + "," + frac
    return sci_text(float(q), 3)


DIAGRAM_NAMES = {"Einfache Wege": "Wegediagramm", "Perfekte Paarungen": "Paarungsdiagramm", "Spannbäume": "Spannbaumdiagramm"}


# ----------------------------------------------------------------------------- Eingaben

def effective_grid(task: str, rows: int, cols: int) -> tuple:
    if task not in C.TASKS:
        raise ValueError(f"unbekannte Aufgabe {task!r}")
    cap = C.SIDE_CAP[task]
    rows = max(C.SIDE_MIN, min(rows, cap))
    cols = max(C.SIDE_MIN, min(cols, cap))
    if rows * cols < 2:
        cols = 2
    return rows, cols


def effective_order(order: str, rows: int, cols: int) -> tuple:
    """Schlüssel der Kantenordnung und ein Hinweis, wenn die schlechte Ordnung zu groß wäre."""
    if order not in C.ORDER_KEYS:
        raise ValueError(f"unbekannte Ordnung {order!r}")
    key = C.ORDER_KEYS[order]
    if key == "schlecht" and len(A.grid_edges(rows, cols)) > C.BAD_ORDER_EDGE_LIMIT:
        return "zeile", f"Die schlechte Ordnung gibt es nur bis {C.BAD_ORDER_EDGE_LIMIT} Kanten (4×4), sonst wird sie riesig: gerechnet wird mit der Zeilenordnung."
    return key, None


# ----------------------------------------------------------------------------- die eingestellte Aufgabe

def _row(question, way, result, check=""):
    return {"Frage": question, "Weg": way, "Ergebnis": result, "Prüfung": check}


def _check(a, b):
    return "gleich" if a == b else "weicht ab"


def analyse(s: Settings) -> Analysis:
    rows, cols = effective_grid(s.task, s.rows, s.cols)
    notes, problems, ways = [], [], []
    if (rows, cols) != (s.rows, s.cols):
        notes.append(f"Für diese Aufgabe rechnet die App Gitter bis {C.SIDE_CAP[s.task]}×{C.SIDE_CAP[s.task]} und mit mindestens zwei Knoten: gerechnet wird mit {rows}×{cols}.")
    order_key, note = effective_order(s.order, rows, cols)
    if note:
        notes.append(note)
    width_slider = max(C.WIDTH_MIN, min(s.width, C.WIDTH_MAX))
    builder = {"Einfache Wege": A.path_diagram, "Perfekte Paarungen": A.matching_diagram, "Spannbäume": A.tree_diagram}[s.task]
    edges, layers, arcs = builder(rows, cols, order_key)
    nv = rows * cols
    states = sum(len(layer) for layer in layers)
    zdd = A.zdd_size(arcs)
    frontier = A.frontier_info(edges)[2]
    solutions = A.evaluate(arcs, [1] * len(edges), "zahl")
    sem = beam = None
    ways.append(_row("Zahl der Lösungen", "Diagramm (Frontier-Methode)", big_text(solutions)))
    if s.task == "Einfache Wege":
        wmap = A.edge_weights(rows, cols, s.seed)
        w = [wmap[e] for e in edges]
        mn, nmin = A.evaluate(arcs, w, "min+zahl")
        mx = A.evaluate(arcs, w, "max")
        dj = A.dijkstra_count(rows, cols, wmap)
        sem = {"min": mn, "n_min": nmin, "max": mx, "dijkstra": dj, "weights": w}
        if nv <= C.BRUTE_VERTEX_LIMIT:
            bc, bmin, bnmin, bmax = A.brute_paths(rows, cols, wmap)
            ways.append(_row("Zahl der Lösungen", f"Brute Force (Rückverfolgung aller {big_text(bc)} Wege)", big_text(bc), _check(bc, solutions)))
            ways.append(_row("Größtes Gewicht", "Brute Force", str(bmax), _check(bmax, mx)))
            if bc != solutions or bmax != mx or (bmin, bnmin) != (mn, nmin):
                problems.append("Diagramm und Brute Force weichen ab")
        else:
            ways.append(_row("Zahl der Lösungen", "Brute Force", "–", f"nur bis {C.BRUTE_VERTEX_LIMIT} Knoten"))
        if rows == cols and rows in C.KNOWN_PATHS:
            ways.append(_row("Zahl der Lösungen", "Folge der Wege im n×n-Gitter (aus dem Gedächtnis)", big_text(C.KNOWN_PATHS[rows]), _check(C.KNOWN_PATHS[rows], solutions)))
            if C.KNOWN_PATHS[rows] != solutions:
                problems.append("Die Zahl der Wege weicht von der bekannten Folge ab")
        ways.append(_row("Kleinstes Gewicht", "Diagramm (min, +)", str(mn)))
        ways.append(_row("Kleinstes Gewicht", "Dijkstra", str(dj[0]), _check(dj[0], mn)))
        ways.append(_row("Zahl der kürzesten Wege", "Diagramm (min, +, Zahl)", big_text(nmin)))
        ways.append(_row("Zahl der kürzesten Wege", "Dijkstra mit Zählung", big_text(dj[1]), _check(dj[1], nmin)))
        ways.append(_row("Größtes Gewicht", "Diagramm (max, +)", str(mx)))
        if dj != (mn, nmin):
            problems.append("Diagramm und Dijkstra weichen ab")
        lb, ub = A.beam_longest(edges, 0, nv - 1, w, width_slider)
        beam = {"width": width_slider, "lower": lb, "upper": ub, "exact": mx, "largest_layer": max(len(layer) for layer in layers)}
    elif s.task == "Perfekte Paarungen":
        k = A.kasteleyn(rows, cols)
        ways.append(_row("Zahl der Lösungen", "Kasteleyn (Kosinusformel)", big_text(k), _check(k, solutions)))
        if k != solutions:
            problems.append("Diagramm und Kasteleyn weichen ab")
    else:
        k = A.kirchhoff(rows, cols)
        ways.append(_row("Zahl der Lösungen", "Kirchhoff (Determinante der Laplace-Matrix)", big_text(k), _check(k, solutions)))
        if k != solutions:
            problems.append("Diagramm und Kirchhoff weichen ab")
    return Analysis(s, s.task, rows, cols, order_key, nv, len(edges), frontier, [len(layer) for layer in layers], states, zdd, solutions, ways, sem, beam, problems, notes)


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    what = {"Einfache Wege": "einfache Wege von Ecke zu Ecke", "Perfekte Paarungen": "perfekte Paarungen (Dominosteine)", "Spannbäume": "Spannbäume"}[a.task]
    order = C.ORDER_NAMES[a.order_key].split(" ")[0]
    text = (f"Im {a.rows}×{a.cols}-Gitter gibt es {big_text(a.solutions)} {what}; das Diagramm (Kantenordnung {order}, Frontier {a.frontier}) hat {big_text(a.zdd)} Knoten ({big_text(a.states)} Zustände vor der Reduktion)")
    text += f", {per_node_text(a.solutions, a.zdd)} Lösungen je Knoten." if a.solutions else "; es gibt keine Lösung (Knotenzahl ungerade)." if a.task == "Perfekte Paarungen" else "."
    if a.sem is not None:
        text += f" Auf demselben Diagramm: kleinstes Gewicht {a.sem['min']} ({big_text(a.sem['n_min'])} {'Weg' if a.sem['n_min'] == 1 else 'Wege'}), größtes Gewicht {a.sem['max']}, beides gleich Dijkstra und Brute Force."
        b = a.beam
        if b["lower"] is not None:
            tail = "die untere Schranke trifft das Optimum" if b["lower"] == b["exact"] else f"die untere Schranke liegt {b['exact'] - b['lower']} unter dem Optimum"
            text += f" Mit begrenzter Breite {b['width']} (größte Schicht {big_text(b['largest_layer'])}): untere Schranke {b['lower']}, obere Schranke {b['upper']}, exakt {b['exact']}; {tail}."
    return "success", text


# ----------------------------------------------------------------------------- Experiment 1: Diagramm gegen Lösungszahl

def _size_row(builder, rows, cols):
    edges, layers, arcs = builder(rows, cols)
    solutions = A.evaluate(arcs, [1] * len(edges), "zahl")
    zdd = A.zdd_size(arcs)
    return {"Gitter": f"{rows}×{cols}", "Kanten": len(edges), "Frontier": A.frontier_info(edges)[2], "Lösungen": solutions, "Zustände": sum(len(l) for l in layers), "Knoten": zdd, "je Knoten": solutions / zdd if zdd else 0.0, "ganz je Knoten": solutions // zdd if zdd else 0}


@functools.cache
def size_rows() -> dict:
    return {"paths": [_size_row(A.path_diagram, n, n) for n in C.EXP_SIZE_PATH_NS],
            "matchings": [_size_row(A.matching_diagram, r, c) for r, c in C.EXP_SIZE_MATCHINGS],
            "trees": [_size_row(A.tree_diagram, r, c) for r, c in C.EXP_SIZE_TREES]}


def verdict_size(res: dict):
    p = res["paths"]
    last, ratios = p[-1], [p[i + 1]["Knoten"] / p[i]["Knoten"] for i in range(2, len(p) - 1)]
    m8 = next(r for r in res["matchings"] if r["Gitter"] == "8×8")
    t7 = res["trees"][-1]
    return "success", (f"Das Diagramm ist weit kleiner als die Lösungszahl: Wege im {last['Gitter']}-Gitter {big_text(last['Lösungen'])} in {big_text(last['Knoten'])} Knoten, Dominosteine auf dem 8×8-Brett {big_text(m8['Lösungen'])} in {big_text(m8['Knoten'])}, "
                       f"Spannbäume des {t7['Gitter']}-Gitters {big_text(t7['Lösungen'])} in {big_text(t7['Knoten'])} Knoten. Die Knotenzahl wächst bei den Wegen um das {de(min(ratios), 1)}- bis {de(max(ratios), 1)}-Fache je Seitenlänge "
                       f"(exponentiell in n), die Lösungszahl wie exp(c·n²); ab n = 4 gewinnt das Diagramm, bei n = 8 kommen {sci_text(p[6]['Lösungen'] / p[6]['Knoten'], 2)} Wege auf einen Knoten.")


# ----------------------------------------------------------------------------- Experiment 2: dieselben Zahlen auf anderen Wegen

@functools.cache
def check_rows() -> list:
    rows = []
    for n in C.EXP_SIZE_PATH_NS:
        edges, layers, arcs = A.path_diagram(n, n)
        count = A.evaluate(arcs, [1] * len(edges), "zahl")
        rows.append({"Aufgabe": "Einfache Wege", "Gitter": f"{n}×{n}", "Diagramm": count, "Prüfweg": "Folge aus dem Gedächtnis", "Prüfwert": C.KNOWN_PATHS[n], "gleich": count == C.KNOWN_PATHS[n]})
        if n in C.EXP_CHECK_BRUTE_NS:
            b = A.brute_paths(n, n)[0]
            rows.append({"Aufgabe": "Einfache Wege", "Gitter": f"{n}×{n}", "Diagramm": count, "Prüfweg": "Brute Force", "Prüfwert": b, "gleich": count == b})
    for r, c in C.EXP_SIZE_MATCHINGS:
        count = A.evaluate(A.matching_diagram(r, c)[2], [1] * len(A.grid_edges(r, c)), "zahl")
        rows.append({"Aufgabe": "Perfekte Paarungen", "Gitter": f"{r}×{c}", "Diagramm": count, "Prüfweg": "Kasteleyn", "Prüfwert": A.kasteleyn(r, c), "gleich": count == A.kasteleyn(r, c)})
    for r, c in C.EXP_SIZE_TREES:
        count = A.evaluate(A.tree_diagram(r, c)[2], [1] * len(A.grid_edges(r, c)), "zahl")
        rows.append({"Aufgabe": "Spannbäume", "Gitter": f"{r}×{c}", "Diagramm": count, "Prüfweg": "Kirchhoff", "Prüfwert": A.kirchhoff(r, c), "gleich": count == A.kirchhoff(r, c)})
    return rows


def verdict_check(rows: list):
    ok = all(r["gleich"] for r in rows)
    kinds = sorted({r["Prüfweg"] for r in rows})
    return ("success" if ok else "error"), (f"In allen {len(rows)} Prüfungen stimmt die Zahl aus dem Diagramm mit einem unabhängigen Weg überein ({', '.join(kinds)}); die Folge der Wege im n×n-Gitter bis n = {max(C.EXP_SIZE_PATH_NS)} steht nur aus dem Gedächtnis, "
                                            f"bis n = {max(C.EXP_CHECK_BRUTE_NS)} gegen Brute Force.")


# ----------------------------------------------------------------------------- Experiment 3: Kantenordnung

@functools.cache
def order_rows() -> list:
    rows = []
    for task, builder, grids in (("Einfache Wege", A.path_diagram, C.EXP_ORDER_PATHS), ("Perfekte Paarungen", A.matching_diagram, C.EXP_ORDER_MATCHINGS), ("Spannbäume", A.tree_diagram, C.EXP_ORDER_TREES)):
        for r, c in grids:
            row = {"Aufgabe": task, "Gitter": f"{r}×{c}"}
            for key in ("zeile", "schlecht"):
                edges, layers, arcs = builder(r, c, key)
                row[key] = {"Frontier": A.frontier_info(edges)[2], "Zustände": sum(len(l) for l in layers), "Knoten": A.zdd_size(arcs), "Lösungen": A.evaluate(arcs, [1] * len(edges), "zahl")}
            rows.append(row)
    return rows


def verdict_order(rows: list):
    same = all(r["zeile"]["Lösungen"] == r["schlecht"]["Lösungen"] for r in rows)
    worst = max(rows, key=lambda r: r["schlecht"]["Zustände"] / r["zeile"]["Zustände"])
    return ("success" if same else "error"), (f"Die Kantenordnung ändert die Lösungen nicht, aber die Größe: beim {DIAGRAM_NAMES[worst['Aufgabe']]} {worst['Gitter']} hat die Zeilenordnung {big_text(worst['zeile']['Zustände'])} Zustände, "
                                             f"die schlechte Ordnung (Frontier {worst['schlecht']['Frontier']} statt {worst['zeile']['Frontier']}) {big_text(worst['schlecht']['Zustände'])}, reduziert {big_text(worst['schlecht']['Knoten'])} gegen {big_text(worst['zeile']['Knoten'])} Knoten. "
                                             "Im 5×5-Gitter sind es in der schlechten Ordnung schon über 6,5 Millionen Zustände (Phase 0, hier nicht gerechnet).")


# ----------------------------------------------------------------------------- Experiment 4: Semiring auf demselben Diagramm, Ziehen

@functools.cache
def semiring_rows() -> dict:
    rows = []
    for n in C.EXP_SEM_NS:
        edges, layers, arcs = A.path_diagram(n, n)
        wmap = A.edge_weights(n, n, C.EXP_SEM_SEED + n)
        w = [wmap[e] for e in edges]
        count = A.evaluate(arcs, [1] * len(edges), "zahl")
        mn, nmin = A.evaluate(arcs, w, "min+zahl")
        mx = A.evaluate(arcs, w, "max")
        dj = A.dijkstra_count(n, n, wmap)
        row = {"n": n, "Wege": count, "kleinstes": mn, "Zahl kleinste": nmin, "größtes": mx, "Dijkstra gleich": dj == (mn, nmin), "Brute gleich": None}
        if n <= 5:
            bc, bmin, bnmin, bmax = A.brute_paths(n, n, wmap)
            row["Brute gleich"] = (bc, bmin, bnmin, bmax) == (count, mn, nmin, mx)
        rows.append(row)
    n = C.EXP_SAMPLE_N
    edges, layers, arcs = A.path_diagram(n, n)
    counts = A.counts_per_node(arcs)
    rng = random.Random(C.EXP_SEM_SEED)
    seen = {}
    for _ in range(C.EXP_SAMPLE_DRAWS):
        p = A.sample_path(arcs, counts, rng)
        seen[p] = seen.get(p, 0) + 1
    total = counts[0][0]
    exp = C.EXP_SAMPLE_DRAWS / total
    chi = sum((c - exp) ** 2 / exp for c in seen.values()) + (total - len(seen)) * exp
    z = (chi - (total - 1)) / math.sqrt(2 * (total - 1))
    return {"rows": rows, "sample": {"n": n, "total": total, "drawn": len(seen), "chi": chi, "z": z, "draws": C.EXP_SAMPLE_DRAWS}}


def verdict_semiring(res: dict):
    ok = all(r["Dijkstra gleich"] and r["Brute gleich"] is not False for r in res["rows"]) and abs(res["sample"]["z"]) <= 4
    last = res["rows"][-1]
    s = res["sample"]
    return ("success" if ok else "error"), (f"Ein Diagramm, vier Auswertungen: Zahl der Wege, kleinstes Gewicht, Zahl der kürzesten und größtes Gewicht; bei n = {last['n']} {big_text(last['Wege'])} Wege, kleinstes Gewicht {last['kleinstes']} ({last['Zahl kleinste']} "
                                            f"{'Weg' if last['Zahl kleinste'] == 1 else 'Wege'}), größtes {last['größtes']}; gleich Dijkstra (n ≤ {last['n']}) und Brute Force (n ≤ 5). Gleichverteilt ziehen aus dem Diagramm: im {s['n']}×{s['n']}-Gitter wurden "
                                            f"alle {s['drawn']} von {s['total']} Wegen in {big_text(s['draws'])} Ziehungen gezogen, z = {de(s['z'], 2)}.")


# ----------------------------------------------------------------------------- Experiment 5: begrenzte Breite

@functools.cache
def beam_rows() -> list:
    out = []
    for n in C.EXP_BEAM_NS:
        edges, layers, arcs = A.path_diagram(n, n)
        wmap = A.edge_weights(n, n, C.EXP_SEM_SEED + n)
        w = [wmap[e] for e in edges]
        exact = A.evaluate(arcs, w, "max")
        series = []
        for width in C.EXP_BEAM_WIDTHS:
            lb, ub = A.beam_longest(edges, 0, n * n - 1, w, width)
            series.append({"Breite": width, "untere": lb, "obere": ub})
        out.append({"n": n, "exakt": exact, "größte Schicht": max(len(l) for l in layers), "Reihe": series})
    return out


def verdict_beam(rows: list):
    last = rows[-1]
    first_opt = next(r["Breite"] for r in last["Reihe"] if r["untere"] == last["exakt"])
    closing = next((r["Breite"] for r in last["Reihe"] if r["obere"] == last["exakt"]), None)
    ok = all(r["untere"] <= row["exakt"] <= r["obere"] for row in rows for r in row["Reihe"] if r["untere"] is not None)
    return ("success" if ok else "error"), (f"Mit begrenzter Breite entstehen Schranken für den längsten Weg (n = {last['n']}, exakt {last['exakt']}, größte Schicht {last['größte Schicht']}): die untere Schranke ist schon bei Breite {first_opt} das Optimum, "
                                            f"die einfache obere Schranke (abgeschnittene Zustände mit allen restlichen positiven Gewichten) schließt erst bei Breite {closing} und ist davor weit entfernt; echte relaxierte Diagramme, die ähnliche Zustände zusammenführen, wären stärker (hier nicht gebaut).")


# ----------------------------------------------------------------------------- Spielwiese: ein Gitter mit Seed

def play_grid(rows: int, cols: int, seed: int) -> dict:
    rows = max(2, min(rows, C.GRAPH_DRAW_MAX)) if rows * cols >= 2 else 2
    cols = max(2, min(cols, C.GRAPH_DRAW_MAX))
    edges, layers, arcs = A.path_diagram(rows, cols)
    wmap = A.edge_weights(rows, cols, seed)
    w = [wmap[e] for e in edges]
    counts = A.counts_per_node(arcs)
    rng = random.Random(seed)
    drawn = A.sample_path(arcs, counts, rng)
    short = A.best_edges(arcs, w, "min")
    long_ = A.best_edges(arcs, w, "max")

    def total(chosen):
        return sum(w[i] for i in chosen)

    return {"rows": rows, "cols": cols, "seed": seed, "solutions": counts[0][0], "drawn": {"edges": drawn, "weight": total(drawn), "art": A.grid_art(rows, cols, edges, drawn)},
            "shortest": {"edges": short, "weight": total(short), "art": A.grid_art(rows, cols, edges, short)}, "longest": {"edges": long_, "weight": total(long_), "art": A.grid_art(rows, cols, edges, long_)},
            "weights": w, "edges": edges}


def verdict_play(res: dict):
    return "success", (f"{res['rows']}×{res['cols']}-Gitter mit Gewichten 1 bis 9 (Seed {res['seed']}): {big_text(res['solutions'])} Wege; der gezogene Weg hat das Gewicht {res['drawn']['weight']}, "
                       f"der kürzeste {res['shortest']['weight']}, der längste {res['longest']['weight']}.")

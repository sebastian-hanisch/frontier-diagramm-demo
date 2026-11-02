"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Alles ist deterministisch; Zeiten kommen nicht vor."""

import re
from pathlib import Path

import fdg_algorithm as A
import fdg_constants as C
import fdg_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
S = ev.Settings


def _counts(builder, rows, cols, order="zeile"):
    edges, layers, arcs = builder(rows, cols, order)
    return A.evaluate(arcs, [1] * len(edges), "zahl"), sum(len(l) for l in layers), A.zdd_size(arcs), A.frontier_info(edges)[2]


def test_readme_hand_instance():
    edges, layers, arcs = A.path_diagram(2, 2)
    assert edges == [(0, 1), (0, 2), (1, 3), (2, 3)] and [len(l) for l in layers[:-1]] == [1, 2, 2, 2] and A.zdd_size(arcs) == 4 and A.frontier_info(edges)[2] == 3
    assert A.evaluate(arcs, [1] * 4, "zahl") == 2 and A.evaluate(arcs, [1, 4, 2, 3], "min+zahl") == (3, 1) and A.evaluate(arcs, [1, 4, 2, 3], "max") == 7
    assert _counts(A.matching_diagram, 2, 2)[0] == 2 and _counts(A.tree_diagram, 2, 2)[0] == 4


def test_readme_path_rows():
    rows = {int(r["Gitter"][0]) if len(r["Gitter"]) == 3 else 10: r for r in ev.size_rows()["paths"]}
    assert [rows[n]["Lösungen"] for n in range(2, 11)] == [2, 12, 184, 8512, 1262816, 575780564, 789360053252, 3266598486981642, 41044208702632496804]
    assert [rows[n]["Knoten"] for n in range(2, 11)] == [4, 27, 134, 583, 2323, 8729, 31481, 110189, 377106]
    assert [rows[n]["Zustände"] for n in range(2, 11)] == [7, 54, 285, 1246, 4926, 18271, 64993, 224462, 758682]
    assert [rows[n]["Frontier"] for n in range(2, 11)] == [n + 1 for n in range(2, 11)]
    assert [round(rows[n]["je Knoten"], 2) for n in (2, 4)] == [0.5, 1.37] and round(rows[5]["je Knoten"], 1) == 14.6 and round(rows[6]["je Knoten"], 1) == 543.6
    assert round(rows[7]["je Knoten"], 1) == 65961.8 and f"{rows[8]['je Knoten']:.2g}" == "2.5e+07"
    ratios = [rows[n + 1]["Knoten"] / rows[n]["Knoten"] for n in range(4, 10)]
    assert f"{min(ratios):.1f}" == "3.4" and f"{max(ratios):.1f}" == "4.4"


def test_readme_matching_rows():
    rows = {r["Gitter"]: r for r in ev.size_rows()["matchings"]}
    assert [(rows[g]["Lösungen"], rows[g]["Knoten"]) for g in ("2×8", "4×4", "6×6", "8×8", "8×10", "10×10")] == [(34, 120), (36, 48), (6728, 363), (12988816, 2298), (1031151241, 9385), (258584046368, 13159)]
    assert all(r["Lösungen"] == A.kasteleyn(*map(int, r["Gitter"].split("×"))) for r in rows.values()) and _counts(A.matching_diagram, 3, 3)[0] == 0


def test_readme_tree_rows():
    rows = {r["Gitter"]: r for r in ev.size_rows()["trees"]}
    assert [(rows[g]["Lösungen"], rows[g]["Knoten"]) for g in ("3×3", "4×4", "5×5", "6×6", "7×7")] == [
        (192, 39), (100352, 214), (557568000, 1078), (32565539635200, 5153), (19872369301840986112, 23788)]
    assert all(r["Lösungen"] == A.kirchhoff(*map(int, r["Gitter"].split("×"))) for r in rows.values())


def test_readme_order_rows():
    rows = {(r["Aufgabe"], r["Gitter"]): r for r in ev.order_rows()}
    zs = lambda k: (rows[k]["zeile"]["Zustände"], rows[k]["schlecht"]["Zustände"])
    assert [zs(("Einfache Wege", g)) for g in ("3×3", "3×5", "4×4")] == [(54, 308), (431, 23058), (285, 24430)]
    assert [zs(("Perfekte Paarungen", g)) for g in ("3×4", "4×4", "4×5")] == [(71, 568), (113, 3028), (230, 20227)]
    assert [zs(("Spannbäume", g)) for g in ("3×3", "3×4", "4×4")] == [(46, 263), (153, 2259), (251, 19283)]
    k = rows[("Einfache Wege", "4×4")]
    assert (k["zeile"]["Frontier"], k["schlecht"]["Frontier"], k["zeile"]["Knoten"], k["schlecht"]["Knoten"]) == (5, 16, 134, 822)
    k = rows[("Perfekte Paarungen", "4×5")]
    assert (k["zeile"]["Knoten"], k["schlecht"]["Knoten"]) == (93, 407)
    k = rows[("Spannbäume", "4×4")]
    assert (k["zeile"]["Knoten"], k["schlecht"]["Knoten"]) == (214, 7704) and all(r["zeile"]["Lösungen"] == r["schlecht"]["Lösungen"] for r in rows.values())


def test_readme_semiring_and_sampling_rows():
    res = ev.semiring_rows()
    assert [(r["n"], r["Wege"], r["kleinstes"], r["Zahl kleinste"], r["größtes"]) for r in res["rows"]] == [
        (4, 184, 19, 1, 57), (5, 8512, 29, 1, 129), (6, 1262816, 34, 1, 206), (7, 575780564, 38, 1, 263)]
    assert all(r["Dijkstra gleich"] for r in res["rows"]) and [r["Brute gleich"] for r in res["rows"]] == [True, True, None, None]
    s = res["sample"]
    assert (s["drawn"], s["total"], s["draws"], round(s["chi"], 2), round(s["z"], 2)) == (184, 184, 36800, 195.19, 0.64)


def test_readme_beam_rows():
    rows = {r["n"]: r for r in ev.beam_rows()}
    a, b = rows[6], rows[7]
    assert (a["exakt"], a["größte Schicht"], b["exakt"], b["größte Schicht"]) == (206, 136, 263, 348)
    lo6 = {x["Breite"]: x["untere"] for x in a["Reihe"]}
    up6 = {x["Breite"]: x["obere"] for x in a["Reihe"]}
    assert [lo6[w] for w in (1, 2, 4, 8, 16)] == [159, 192, 190, 191, 206] and (up6[1], up6[128], up6[256]) == (313, 248, 206)
    lo7 = {x["Breite"]: x["untere"] for x in b["Reihe"]}
    up7 = {x["Breite"]: x["obere"] for x in b["Reihe"]}
    assert [lo7[w] for w in (1, 2, 4, 8, 16, 32, 64)] == [228, 247, 255, 260, 260, 260, 263] and (up7[1], up7[256], up7[512]) == (396, 338, 263)
    assert min(w for w, v in up6.items() if v == 206) == 256 and min(w for w, v in up7.items() if v == 263) == 512 and min(w for w, v in lo7.items() if v == 263) == 64


def test_readme_preset_numbers():
    a = ev.analyse(S(**C.PRESETS["Wege im 5×5-Gitter, Seed 4"]))
    assert (a.sem["min"], a.sem["n_min"], a.sem["max"]) == (28, 2, 131)
    b = ev.analyse(S(**C.PRESETS["Längster Weg mit begrenzter Breite, 7×7"]))
    assert (b.beam["lower"], b.beam["upper"], b.beam["exact"], b.sem["min"], b.sem["n_min"]) == (269, 400, 278, 39, 2)
    c = ev.analyse(S(**C.PRESETS["Standardfall: einfache Wege im 6×6-Gitter"]))
    assert (c.beam["lower"], c.beam["upper"], c.beam["exact"], c.sem["min"], c.sem["n_min"]) == (180, 266, 186, 30, 2)


def test_readme_play_rows():
    g = ev.play_grid(4, 4, 5)
    assert (g["solutions"], g["drawn"]["weight"], g["shortest"]["weight"], g["longest"]["weight"]) == (184, 69, 18, 78)
    h = ev.play_grid(2, 3, 1)
    assert (h["solutions"], h["drawn"]["weight"], h["shortest"]["weight"], h["longest"]["weight"]) == (4, 25, 13, 25)


def test_preset_help_numbers_match_the_computation():
    p = lambda n: C.PRESET_HELP[n]
    n = ev.analyse(S(**C.PRESETS["Standardfall: einfache Wege im 6×6-Gitter"]))
    assert f"{n.solutions:,}".replace(",", ".") in p("Standardfall: einfache Wege im 6×6-Gitter") and f"{n.zdd:,}".replace(",", ".") in p("Standardfall: einfache Wege im 6×6-Gitter") and f"{n.states:,}".replace(",", ".") in p("Standardfall: einfache Wege im 6×6-Gitter")
    m = ev.analyse(S(**C.PRESETS["Dominosteine auf dem 8×8-Brett"]))
    assert "12.988.816" in p("Dominosteine auf dem 8×8-Brett") and m.solutions == 12988816 and "2.298" in p("Dominosteine auf dem 8×8-Brett") and m.zdd == 2298
    t = ev.analyse(S(**C.PRESETS["Spannbäume des 7×7-Gitters"]))
    assert "19.872.369.301.840.986.112" in p("Spannbäume des 7×7-Gitters") and t.solutions == 19872369301840986112 and "23.788" in p("Spannbäume des 7×7-Gitters") and t.zdd == 23788
    bad = ev.analyse(S(**C.PRESETS["Schlechte Kantenordnung, 4×4-Wege"]))
    good = ev.analyse(S("Einfache Wege", 4, 4, "Zeile", 7, 8))
    text = p("Schlechte Kantenordnung, 4×4-Wege")
    assert (bad.frontier, good.states, bad.states, bad.zdd, good.zdd, bad.solutions) == (16, 285, 24430, 822, 134, 184) and all(x in text for x in ("16 Knoten", "285 auf 24.430", "822 statt 134", "184 Wege"))
    s4 = ev.analyse(S(**C.PRESETS["Wege im 5×5-Gitter, Seed 4"]))
    assert s4.solutions == 8512 and "8.512" in p("Wege im 5×5-Gitter, Seed 4") and "kleinste Gewicht 28 genau zwei" in p("Wege im 5×5-Gitter, Seed 4") and (s4.sem["min"], s4.sem["n_min"]) == (28, 2)
    assert "4 besten Teilwege" in p("Längster Weg mit begrenzter Breite, 7×7") and C.PRESETS["Längster Weg mit begrenzter Breite, 7×7"]["width"] == 4


def test_phase_zero_claim_of_the_5x5_bad_order_is_only_stated_in_texts():
    """Die 6,5 Millionen Zustände der schlechten Ordnung im 5×5-Gitter stehen im Text, werden aber hier nicht gerechnet (zu groß); die kleine Folge davor ist gerechnet und wächst."""
    states = [_counts(A.path_diagram, n, n, "schlecht")[1] for n in (2, 3, 4)]
    assert states == [9, 308, 24430] and states[2] / states[1] > 79
    assert "6,5 Millionen" in README and "über 6,5 Millionen" in ev.verdict_order(ev.order_rows())[1]


def test_readme_mentions_every_module_file():
    root = Path(__file__).resolve().parent.parent
    for f in root.glob("fdg_*.py"):
        assert f"`{f.name}`" in README, f.name
    assert "`app.py`" in README and "Stück 13 von 16" in README

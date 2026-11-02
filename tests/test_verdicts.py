"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für alle Voreinstellungen und Experimente, damit jede Zahl darin geprüft ist."""

import fdg_constants as C
import fdg_evaluation as ev

S = ev.Settings


def answer(name):
    return ev.verdict_answers(ev.analyse(S(**C.PRESETS[name])))


def test_answer_standard_case_exact():
    assert answer("Standardfall: einfache Wege im 6×6-Gitter") == ("success",
        "Im 6×6-Gitter gibt es 1.262.816 einfache Wege von Ecke zu Ecke; das Diagramm (Kantenordnung Zeile, Frontier 7) hat 2.323 Knoten (4.926 Zustände vor der Reduktion), 543,6 Lösungen je Knoten. "
        "Auf demselben Diagramm: kleinstes Gewicht 30 (2 Wege), größtes Gewicht 186, beides gleich Dijkstra und Brute Force. "
        "Mit begrenzter Breite 8 (größte Schicht 136): untere Schranke 180, obere Schranke 266, exakt 186; die untere Schranke liegt 6 unter dem Optimum.")


def test_answer_matchings_and_trees_exact():
    assert answer("Dominosteine auf dem 8×8-Brett") == ("success",
        "Im 8×8-Gitter gibt es 12.988.816 perfekte Paarungen (Dominosteine); das Diagramm (Kantenordnung Zeile, Frontier 9) hat 2.298 Knoten (6.197 Zustände vor der Reduktion), 5.652,2 Lösungen je Knoten.")
    assert answer("Spannbäume des 7×7-Gitters") == ("success",
        "Im 7×7-Gitter gibt es 1,98·10¹⁹ (20 Stellen) Spannbäume; das Diagramm (Kantenordnung Zeile, Frontier 8) hat 23.788 Knoten (27.645 Zustände vor der Reduktion), 8,35·10¹⁴ Lösungen je Knoten.")


def test_answer_bad_order_exact():
    assert answer("Schlechte Kantenordnung, 4×4-Wege") == ("success",
        "Im 4×4-Gitter gibt es 184 einfache Wege von Ecke zu Ecke; das Diagramm (Kantenordnung Schlecht, Frontier 16) hat 822 Knoten (24.430 Zustände vor der Reduktion), 0,2 Lösungen je Knoten. "
        "Auf demselben Diagramm: kleinstes Gewicht 13 (1 Weg), größtes Gewicht 68, beides gleich Dijkstra und Brute Force.")


def test_answer_beam_and_seed_cases_exact():
    assert answer("Längster Weg mit begrenzter Breite, 7×7") == ("success",
        "Im 7×7-Gitter gibt es 575.780.564 einfache Wege von Ecke zu Ecke; das Diagramm (Kantenordnung Zeile, Frontier 8) hat 8.729 Knoten (18.271 Zustände vor der Reduktion), 65.961,8 Lösungen je Knoten. "
        "Auf demselben Diagramm: kleinstes Gewicht 39 (2 Wege), größtes Gewicht 278, beides gleich Dijkstra und Brute Force. "
        "Mit begrenzter Breite 4 (größte Schicht 348): untere Schranke 269, obere Schranke 400, exakt 278; die untere Schranke liegt 9 unter dem Optimum.")
    assert answer("Wege im 5×5-Gitter, Seed 4") == ("success",
        "Im 5×5-Gitter gibt es 8.512 einfache Wege von Ecke zu Ecke; das Diagramm (Kantenordnung Zeile, Frontier 6) hat 583 Knoten (1.246 Zustände vor der Reduktion), 14,6 Lösungen je Knoten. "
        "Auf demselben Diagramm: kleinstes Gewicht 28 (2 Wege), größtes Gewicht 131, beides gleich Dijkstra und Brute Force. "
        "Mit begrenzter Breite 8 (größte Schicht 54): untere Schranke 131, obere Schranke 172, exakt 131; die untere Schranke trifft das Optimum.")


def test_answer_error_when_the_ways_disagree():
    a = ev.analyse(S(**C.PRESETS["Standardfall: einfache Wege im 6×6-Gitter"]))
    a.problems.append("zwei Wege weichen ab")
    assert ev.verdict_answers(a) == ("error", "Die Rechenwege widersprechen sich: zwei Wege weichen ab")


def test_ways_table_of_the_standard_case_and_the_seed_case():
    a = ev.analyse(S(**C.PRESETS["Standardfall: einfache Wege im 6×6-Gitter"]))
    assert [(w["Frage"], w["Weg"], w["Ergebnis"], w["Prüfung"]) for w in a.ways] == [
        ("Zahl der Lösungen", "Diagramm (Frontier-Methode)", "1.262.816", ""), ("Zahl der Lösungen", "Brute Force", "–", "nur bis 25 Knoten"),
        ("Zahl der Lösungen", "Folge der Wege im n×n-Gitter (aus dem Gedächtnis)", "1.262.816", "gleich"), ("Kleinstes Gewicht", "Diagramm (min, +)", "30", ""), ("Kleinstes Gewicht", "Dijkstra", "30", "gleich"),
        ("Zahl der kürzesten Wege", "Diagramm (min, +, Zahl)", "2", ""), ("Zahl der kürzesten Wege", "Dijkstra mit Zählung", "2", "gleich"), ("Größtes Gewicht", "Diagramm (max, +)", "186", "")]
    b = ev.analyse(S(**C.PRESETS["Wege im 5×5-Gitter, Seed 4"]))
    assert [(w["Weg"], w["Ergebnis"], w["Prüfung"]) for w in b.ways if w["Frage"] == "Zahl der Lösungen"] == [
        ("Diagramm (Frontier-Methode)", "8.512", ""), ("Brute Force (Rückverfolgung aller 8.512 Wege)", "8.512", "gleich"), ("Folge der Wege im n×n-Gitter (aus dem Gedächtnis)", "8.512", "gleich")]


def test_size_verdict_exact():
    assert ev.verdict_size(ev.size_rows()) == ("success",
        "Das Diagramm ist weit kleiner als die Lösungszahl: Wege im 10×10-Gitter 4,10·10¹⁹ (20 Stellen) in 377.106 Knoten, Dominosteine auf dem 8×8-Brett 12.988.816 in 2.298, Spannbäume des 7×7-Gitters 1,98·10¹⁹ (20 Stellen) in 23.788 Knoten. "
        "Die Knotenzahl wächst bei den Wegen um das 3,4- bis 4,4-Fache je Seitenlänge (exponentiell in n), die Lösungszahl wie exp(c·n²); ab n = 4 gewinnt das Diagramm, bei n = 8 kommen 2,5·10⁷ Wege auf einen Knoten.")


def test_check_verdict_exact():
    rows = ev.check_rows()
    assert len(rows) == 26 and all(r["gleich"] for r in rows)
    assert ev.verdict_check(rows) == ("success",
        "In allen 26 Prüfungen stimmt die Zahl aus dem Diagramm mit einem unabhängigen Weg überein (Brute Force, Folge aus dem Gedächtnis, Kasteleyn, Kirchhoff); "
        "die Folge der Wege im n×n-Gitter bis n = 10 steht nur aus dem Gedächtnis, bis n = 5 gegen Brute Force.")


def test_order_verdict_exact():
    assert ev.verdict_order(ev.order_rows()) == ("success",
        "Die Kantenordnung ändert die Lösungen nicht, aber die Größe: beim Paarungsdiagramm 4×5 hat die Zeilenordnung 230 Zustände, die schlechte Ordnung (Frontier 20 statt 6) 20.227, reduziert 407 gegen 93 Knoten. "
        "Im 5×5-Gitter sind es in der schlechten Ordnung schon über 6,5 Millionen Zustände (Phase 0, hier nicht gerechnet).")


def test_semiring_verdict_exact():
    assert ev.verdict_semiring(ev.semiring_rows()) == ("success",
        "Ein Diagramm, vier Auswertungen: Zahl der Wege, kleinstes Gewicht, Zahl der kürzesten und größtes Gewicht; bei n = 7 575.780.564 Wege, kleinstes Gewicht 38 (1 Weg), größtes 263; gleich Dijkstra (n ≤ 7) und Brute Force (n ≤ 5). "
        "Gleichverteilt ziehen aus dem Diagramm: im 4×4-Gitter wurden alle 184 von 184 Wegen in 36.800 Ziehungen gezogen, z = 0,64.")


def test_beam_verdict_exact():
    assert ev.verdict_beam(ev.beam_rows()) == ("success",
        "Mit begrenzter Breite entstehen Schranken für den längsten Weg (n = 7, exakt 263, größte Schicht 348): die untere Schranke ist schon bei Breite 64 das Optimum, "
        "die einfache obere Schranke (abgeschnittene Zustände mit allen restlichen positiven Gewichten) schließt erst bei Breite 512 und ist davor weit entfernt; echte relaxierte Diagramme, die ähnliche Zustände zusammenführen, wären stärker (hier nicht gebaut).")


def test_play_verdict_exact():
    assert ev.verdict_play(ev.play_grid(4, 4, 5)) == ("success", "4×4-Gitter mit Gewichten 1 bis 9 (Seed 5): 184 Wege; der gezogene Weg hat das Gewicht 69, der kürzeste 18, der längste 78.")
    assert ev.verdict_play(ev.play_grid(2, 3, 1)) == ("success", "2×3-Gitter mit Gewichten 1 bis 9 (Seed 1): 4 Wege; der gezogene Weg hat das Gewicht 25, der kürzeste 13, der längste 25.")


def test_verdicts_turn_into_errors_when_a_check_fails():
    rows = [dict(r) for r in ev.check_rows()]
    rows[0]["gleich"] = False
    assert ev.verdict_check(rows)[0] == "error"
    order = [dict(r) for r in ev.order_rows()]
    order[0] = {**order[0], "schlecht": {**order[0]["schlecht"], "Lösungen": order[0]["schlecht"]["Lösungen"] + 1}}
    assert ev.verdict_order(order)[0] == "error"
    sem = ev.semiring_rows()
    broken = {"rows": [{**sem["rows"][0], "Dijkstra gleich": False}] + sem["rows"][1:], "sample": sem["sample"]}
    assert ev.verdict_semiring(broken)[0] == "error"
    skewed = {"rows": sem["rows"], "sample": {**sem["sample"], "z": 5.0}}
    assert ev.verdict_semiring(skewed)[0] == "error"

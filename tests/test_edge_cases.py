"""Randfälle: Klemmen der Eingaben, Hinweise, Fehler bei unbekannten Werten, Grenzen der Prüfwege."""

import pytest

import fdg_algorithm as A
import fdg_constants as C
import fdg_evaluation as ev

S = ev.Settings


def test_one_by_one_grid_is_widened_to_one_by_two_with_a_note():
    a = ev.analyse(S("Einfache Wege", 1, 1, "Zeile", 7, 8))
    assert (a.rows, a.cols) == (1, 2) and a.solutions == 1 and a.nedges == 1 and any("mindestens zwei Knoten" in n for n in a.notes)
    assert ev.effective_grid("Spannbäume", 1, 1) == (1, 2)


def test_caps_are_applied_per_task_with_a_note():
    for task, cap in C.SIDE_CAP.items():
        a = ev.analyse(S(task, 10, 10, "Zeile", 7, 8)) if task == "Perfekte Paarungen" else ev.analyse(S(task, 10, 3, "Zeile", 7, 8))
        assert max(a.rows, a.cols) <= cap
    a = ev.analyse(S("Spannbäume", 10, 2, "Zeile", 7, 8))
    assert (a.rows, a.cols) == (8, 2) and any("bis 8×8" in n for n in a.notes)
    a = ev.analyse(S("Einfache Wege", 10, 2, "Zeile", 7, 8))
    assert a.rows == 9 and any("bis 9×9" in n for n in a.notes)
    assert ev.analyse(S("Perfekte Paarungen", 10, 10, "Zeile", 7, 8)).notes == []


def test_bad_order_falls_back_to_the_row_order_above_the_edge_limit():
    a = ev.analyse(S("Einfache Wege", 5, 5, "Schlecht (erst alle waagerechten Kanten)", 7, 8))
    assert a.order_key == "zeile" and any("nur bis 24 Kanten" in n for n in a.notes) and a.solutions == 8512
    b = ev.analyse(S("Einfache Wege", 4, 4, "Schlecht (erst alle waagerechten Kanten)", 7, 8))
    assert b.order_key == "schlecht" and b.notes == [] and b.states == 24430 and b.solutions == 184
    assert len(A.grid_edges(4, 4)) == C.BAD_ORDER_EDGE_LIMIT


def test_unknown_task_and_order_raise():
    with pytest.raises(ValueError):
        ev.analyse(S("Zauberei", 4, 4, "Zeile", 7, 8))
    with pytest.raises(ValueError):
        ev.analyse(S("Einfache Wege", 4, 4, "Zickzack", 7, 8))
    with pytest.raises(ValueError):
        ev.effective_grid("Zauberei", 3, 3)


def test_width_is_clamped_to_the_slider_range():
    low = ev.analyse(S("Einfache Wege", 4, 4, "Zeile", 7, -5))
    high = ev.analyse(S("Einfache Wege", 4, 4, "Zeile", 7, 99999))
    assert low.beam["width"] == C.WIDTH_MIN and high.beam["width"] == C.WIDTH_MAX


def test_brute_force_row_is_skipped_above_the_vertex_limit():
    big = ev.analyse(S("Einfache Wege", 6, 5, "Zeile", 7, 8))
    assert [w["Prüfung"] for w in big.ways if w["Weg"] == "Brute Force"] == ["nur bis 25 Knoten"]
    small = ev.analyse(S("Einfache Wege", 5, 5, "Zeile", 7, 8))
    assert any(w["Weg"].startswith("Brute Force (Rückverfolgung aller 8.512") for w in small.ways)


def test_known_sequence_row_only_for_square_grids():
    rect = ev.analyse(S("Einfache Wege", 4, 5, "Zeile", 7, 8))
    assert not any("Folge" in w["Weg"] for w in rect.ways)
    assert any("Folge" in w["Weg"] for w in ev.analyse(S("Einfache Wege", 4, 4, "Zeile", 7, 8)).ways)


def test_odd_matching_grid_has_no_solution_and_a_clear_text():
    a = ev.analyse(S("Perfekte Paarungen", 3, 3, "Zeile", 7, 8))
    kind, text = ev.verdict_answers(a)
    assert a.solutions == 0 and kind == "success" and "keine Lösung (Knotenzahl ungerade)" in text and a.zdd == 0 and a.states == 30 and not a.problems


def test_only_the_path_task_has_semiring_and_beam():
    for task in ("Perfekte Paarungen", "Spannbäume"):
        a = ev.analyse(S(task, 4, 4, "Zeile", 7, 8))
        assert a.sem is None and a.beam is None


def test_beam_width_one_may_find_no_path_and_the_text_still_works():
    a = ev.analyse(S("Einfache Wege", 9, 9, "Zeile", 7, 1))
    kind, text = ev.verdict_answers(a)
    assert kind == "success" and a.beam == {"width": 1, "lower": 396, "upper": 712, "exact": 494, "largest_layer": 2377}
    assert "Mit begrenzter Breite 1 (größte Schicht 2.377): untere Schranke 396, obere Schranke 712, exakt 494; die untere Schranke liegt 98 unter dem Optimum." in text


def test_play_grid_clamps_its_sizes():
    g = ev.play_grid(99, 1, 3)
    assert (g["rows"], g["cols"]) == (C.GRAPH_DRAW_MAX, 2)
    h = ev.play_grid(1, 1, 3)
    assert (h["rows"], h["cols"]) == (2, 2)


def test_play_grid_is_reproducible_per_seed():
    a, b, c = ev.play_grid(4, 4, 5), ev.play_grid(4, 4, 5), ev.play_grid(4, 4, 6)
    assert a == b and a["weights"] != c["weights"] and a["drawn"]["edges"] != c["drawn"]["edges"]


def test_formatting_helpers():
    assert ev.de(1.5, 2) == "1,50" and ev.de(0.25, 1) == "0,2"
    assert ev.de(-2.5, 1) == "−2,5"
    assert ev.big_text(999999999999) == "999.999.999.999" and ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)" and ev.big_text(12345678901234567890) == "1,23·10¹⁹ (20 Stellen)"
    assert ev.sci_text(0) == "0" and ev.sci_text(0.5) == "0,50" and ev.sci_text(12345.0, 3) == "1,23·10⁴" and ev.sci_text(0.001, 2) == "1,0·10⁻³"
    assert ev.factor_text(3.456) == "3,46" and ev.factor_text(45.67) == "45,7" and ev.factor_text(12345.6) == "12.346"
    assert ev.per_node_text(5000, 4) == "1.250,0" and ev.per_node_text(1, 5) == "0,2" and ev.per_node_text(10 ** 30, 10 ** 10) == "1,00·10²⁰"

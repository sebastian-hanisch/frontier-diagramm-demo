"""Oberfläche: jede Aufgabe, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import fdg_constants as C
import fdg_evaluation as ev
import fdg_visualization as V

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_five_experiments_and_the_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == [
        "🔬 Experiment 1: Das Diagramm ist weit kleiner als die Lösungszahl", "🔬 Experiment 2: Dieselben Zahlen auf anderen Wegen", "🔬 Experiment 3: Die Kantenordnung entscheidet",
        "🔬 Experiment 4: Ein Diagramm, vier Auswertungen, und Ziehen", "🔬 Experiment 5: Begrenzte Breite, Schranken für den längsten Weg"]
    assert any(t.startswith("Im 6×6-Gitter gibt es 1.262.816 einfache Wege von Ecke zu Ecke") for t in _texts(at)) and not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    values = {m.label: m.value for m in at.metric}
    assert list(values.values())[:4] == ["1.262.816", "2.323", "543,6", "7"] and len(values) == 4


def test_every_preset_runs_and_shows_its_task():
    for name, p in C.PRESETS.items():
        at = _run(task_select=p["task"], rows_slider=p["rows"], cols_slider=p["cols"], order_select=p["order"], seed_slider=p["seed"], width_slider=p["width"])
        assert at.selectbox(key="task_select").value == p["task"], name
        assert not at.error, name


def test_every_task_runs_with_every_order_on_a_small_grid():
    for task in C.TASKS:
        for order in C.ORDERS:
            at = _run(task_select=task, rows_slider=3, cols_slider=4, order_select=order)
            assert not at.error, (task, order)


def test_odd_matching_grid_shows_the_no_solution_text():
    at = _run(task_select="Perfekte Paarungen", rows_slider=3, cols_slider=3)
    assert any("keine Lösung (Knotenzahl ungerade)" in t for t in _texts(at))


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"task": "Unsinn", "order": "Zauber", "rows": "abc", "cols": "99999", "seed": "-5", "width": "0"})
    assert at.selectbox(key="task_select").value == C.DEFAULT_TASK and at.selectbox(key="order_select").value == C.DEFAULT_ORDER
    assert at.slider(key="rows_slider").value == C.DEFAULT_ROWS and at.slider(key="cols_slider").value == C.SIDE_MAX
    assert at.slider(key="seed_slider").value == C.SEED_MIN and at.slider(key="width_slider").value == C.WIDTH_MIN


def test_cap_note_is_shown_for_trees_on_a_large_grid():
    at = _run(task_select="Spannbäume", rows_slider=10, cols_slider=3)
    assert any("gerechnet wird mit 8×3" in t for t in _texts(at))


def test_bad_order_note_is_shown_on_a_large_grid():
    at = _run(order_select=C.ORDER_NAMES["schlecht"], rows_slider=5, cols_slider=5)
    assert any("gerechnet wird mit der Zeilenordnung" in t for t in _texts(at))


def test_play_ground_shows_three_paths_for_the_default_seed():
    at = _run()
    assert any(t.startswith("4×4-Gitter mit Gewichten 1 bis 9 (Seed 5): 184 Wege") for t in _texts(at)) and len(at.get("code")) == 3
    at = _run(play_rows=2, play_cols=3, play_seed=1)
    assert any(t.startswith("2×3-Gitter mit Gewichten 1 bis 9 (Seed 1): 4 Wege") for t in _texts(at))


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("download_button")) == 1


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and {"main_chart", "size_chart", "order_chart", "beam_chart_6", "beam_chart_7"} == set(keys)


def test_pdf_builds_for_every_task_and_order():
    from fdg_pdf_export import build_pdf
    for task in C.TASKS:
        for order in C.ORDERS:
            a = ev.analyse(ev.Settings(task, 4, 4, order, 7, 8))
            assert build_pdf(a)[:4] == b"%PDF", (task, order)


def test_chart_builders_return_locked_axes():
    a = ev.analyse(ev.Settings("Einfache Wege", 5, 5, "Zeile", 7, 8))
    beam = ev.beam_rows()[0]
    for fig in (V.build_layers(a.layer_sizes), V.build_size(ev.size_rows()), V.build_order(ev.order_rows()), V.build_beam(beam)):
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange

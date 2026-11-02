"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import fdg_constants as C
import fdg_evaluation as ev
import fdg_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["task"] in C.TASKS and preset["order"] in C.ORDERS, name
        for field, key in P.PRESET_KEYS.items():
            lo, hi = P.SETTING_SPECS[key].lo, P.SETTING_SPECS[key].hi
            if lo is not None:
                assert lo <= preset[field] <= hi, (name, field)
        assert preset["rows"] <= C.SIDE_CAP[preset["task"]] and preset["cols"] <= C.SIDE_CAP[preset["task"]], name


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default
    assert first["task"] == C.DEFAULT_TASK and first["order"] == C.DEFAULT_ORDER


def test_every_preset_passes_the_checker_without_notes_or_problems():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [], name
        assert (a.rows, a.cols) == (preset["rows"], preset["cols"]), name


def test_presets_differ_from_each_other_in_the_visible_fields():
    seen = set()
    for name, preset in C.PRESETS.items():
        key = (preset["task"], preset["rows"], preset["cols"], preset["order"], preset["seed"], preset["width"])
        assert key not in seen, name
        seen.add(key)


def test_every_task_and_every_order_appears_in_a_preset():
    assert {p["task"] for p in C.PRESETS.values()} == set(C.TASKS)
    assert {C.ORDER_KEYS[p["order"]] for p in C.PRESETS.values()} >= {"zeile", "schlecht"}


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["task_select"].choices == C.TASKS and P.SETTING_SPECS["order_select"].choices == C.ORDERS

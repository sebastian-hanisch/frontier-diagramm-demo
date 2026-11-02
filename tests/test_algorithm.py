"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

import random
from fractions import Fraction

import pytest

import fdg_algorithm as A


def test_grid_edges_orders_and_errors():
    assert A.grid_edges(2, 2) == [(0, 1), (0, 2), (1, 3), (2, 3)]
    assert A.grid_edges(2, 2, "spalte") == [(0, 2), (0, 1), (2, 3), (1, 3)]
    assert A.grid_edges(2, 2, "schlecht") == [(0, 1), (2, 3), (0, 2), (1, 3)]
    assert [len(A.grid_edges(r, c)) for r, c in ((1, 1), (1, 5), (3, 3), (6, 6))] == [0, 4, 12, 60]
    assert sorted(A.grid_edges(3, 4)) == sorted(A.grid_edges(3, 4, "spalte")) == sorted(A.grid_edges(3, 4, "schlecht"))
    with pytest.raises(ValueError):
        A.grid_edges(2, 2, "zauber")
    with pytest.raises(ValueError):
        A.grid_edges(0, 3)


def test_frontier_info_hand(hand_grid_2x2):
    enter, leave, width = A.frontier_info(hand_grid_2x2["edges"])
    assert enter == [[0, 1], [2], [3], []] and leave == [[], [0], [1], [2, 3]] and width == hand_grid_2x2["frontier"]
    assert A.frontier_info(A.grid_edges(6, 6))[2] == 7 and A.frontier_info(A.grid_edges(4, 4, "schlecht"))[2] == 16


def test_path_diagram_hand(hand_grid_2x2):
    h = hand_grid_2x2
    edges, layers, arcs = A.path_diagram(2, 2)
    assert edges == h["edges"] and [len(l) for l in layers[:-1]] == h["layers"] and A.evaluate(arcs, [1] * 4, "zahl") == h["paths"]
    assert A.evaluate(arcs, h["weights"], "min") == h["min"] and A.evaluate(arcs, h["weights"], "max") == h["max"] and A.evaluate(arcs, h["weights"], "min+zahl") == (h["min"], h["n_min"])
    assert A.best_edges(arcs, h["weights"], "min") == h["min_edges"] and A.best_edges(arcs, h["weights"], "max") == h["max_edges"]
    assert A.zdd_size(arcs) == 4


def test_matching_and_tree_diagrams_hand(hand_grid_2x2):
    assert A.evaluate(A.matching_diagram(2, 2)[2], [1] * 4, "zahl") == hand_grid_2x2["matchings"]
    assert A.evaluate(A.tree_diagram(2, 2)[2], [1] * 4, "zahl") == hand_grid_2x2["trees"]


def test_strips(hand_strips):
    for n in range(2, 9):
        assert A.evaluate(A.path_diagram(1, n)[2], [1] * (n - 1), "zahl") == hand_strips["paths"]
        assert A.evaluate(A.tree_diagram(1, n)[2], [1] * (n - 1), "zahl") == hand_strips["trees"]
        assert A.evaluate(A.matching_diagram(1, n)[2], [1] * (n - 1), "zahl") == (hand_strips["matchings_even"] if n % 2 == 0 else hand_strips["matchings_odd"])


def test_evaluate_validation_and_empty_counts():
    arcs = A.matching_diagram(1, 3)[2]
    assert A.evaluate(arcs, [1, 1], "zahl") == 0 and A.evaluate_all(arcs, [1, 1], "min")[0][0] is None
    with pytest.raises(ValueError):
        A.evaluate(arcs, [1, 1], "zauber")
    with pytest.raises(ValueError):
        A.evaluate([], [], "zahl")
    with pytest.raises(ValueError):
        A.path_diagram(1, 1)


def test_counts_and_sampling_hand(hand_grid_2x2):
    arcs = A.path_diagram(2, 2)[2]
    counts = A.counts_per_node(arcs)
    assert counts[0] == [2] and sum(counts[1]) >= 2

    class Scripted:
        def __init__(self, values):
            self.values = list(values)

        def randrange(self, n):
            return self.values.pop(0) % n

    drawn = {A.sample_path(arcs, counts, Scripted([a, b, c, d])) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)}
    assert drawn == {hand_grid_2x2["min_edges"], hand_grid_2x2["max_edges"]}
    with pytest.raises(ValueError):
        A.sample_path(A.matching_diagram(1, 3)[2], A.counts_per_node(A.matching_diagram(1, 3)[2]), random.Random(1))


def test_beam_hand(hand_grid_2x2):
    h = hand_grid_2x2
    assert A.beam_longest(h["edges"], 0, 3, h["weights"], 8) == (7, 7)
    lb, ub = A.beam_longest(h["edges"], 0, 3, h["weights"], 1)
    assert lb is not None and lb <= 7 <= ub
    with pytest.raises(ValueError):
        A.beam_longest(h["edges"], 0, 3, h["weights"], 0)


def test_kasteleyn_and_kirchhoff_hand():
    assert [A.kasteleyn(2, n) for n in range(1, 8)] == [1, 2, 3, 5, 8, 13, 21] and A.kasteleyn(4, 4) == 36 and A.kasteleyn(3, 3) == 0 and A.kasteleyn(8, 8) == 12988816
    assert A.kirchhoff(2, 2) == 4 and A.kirchhoff(3, 3) == 192 and A.kirchhoff(1, 5) == 1 and A.kirchhoff(2, 3) == 15


def test_brute_force_and_dijkstra_hand(hand_grid_2x2):
    w = dict(zip(hand_grid_2x2["edges"], hand_grid_2x2["weights"]))
    assert A.brute_paths(2, 2, w) == (2, 3, 1, 7) and A.brute_paths(2, 2) == (2, None, 0, None) and A.dijkstra_count(2, 2, w) == (3, 1)
    assert A.dijkstra_count(2, 2, {(0, 1): 2, (0, 2): 2, (1, 3): 2, (2, 3): 2}) == (4, 2)


def test_edge_weights_are_independent_of_the_order_and_reproducible():
    a, b = A.edge_weights(4, 4, 7), A.edge_weights(4, 4, 7)
    assert a == b and a != A.edge_weights(4, 4, 8) and set(a.values()) <= set(range(1, 10)) and set(a) == set(A.grid_edges(4, 4, "schlecht"))
    edges = A.grid_edges(4, 4, "spalte")
    assert [a[e] for e in edges] == [A.edge_weights(4, 4, 7)[e] for e in edges]


def test_grid_art_hand(hand_art):
    assert A.grid_art(2, 2, A.grid_edges(2, 2), (0, 2)) == hand_art
    assert A.grid_art(1, 3, A.grid_edges(1, 3), (0, 1)) == "o──o──o"


def test_digit_count():
    assert [A.digit_count(x) for x in (0, 1, 9, 10, 10 ** 50 - 1, 10 ** 50)] == [1, 1, 1, 2, 50, 51]
    with pytest.raises(ValueError):
        A.digit_count(-1)

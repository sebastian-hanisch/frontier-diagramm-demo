"""Eigenschaften (Schicht 2): Gesetze, die für alle Gitter und Seeds gelten müssen, unabhängig von einzelnen Zahlen."""

import pytest

import fdg_algorithm as A
import fdg_constants as C
import fdg_evaluation as ev

BUILDERS = {"Einfache Wege": A.path_diagram, "Perfekte Paarungen": A.matching_diagram, "Spannbäume": A.tree_diagram}


def count(builder, rows, cols, order="zeile"):
    edges, layers, arcs = builder(rows, cols, order)
    return A.evaluate(arcs, [1] * len(edges), "zahl")


@pytest.mark.parametrize("task", C.TASKS)
def test_count_does_not_depend_on_the_edge_order(task):
    for rows, cols in ((2, 3), (3, 3), (3, 4)):
        values = {count(BUILDERS[task], rows, cols, order) for order in A.ORDERS}
        assert len(values) == 1, (task, rows, cols)


@pytest.mark.parametrize("task", C.TASKS)
def test_diagram_is_never_larger_than_the_state_count(task):
    for rows, cols in ((2, 2), (3, 3), (4, 4), (3, 6)):
        for order in A.ORDERS:
            edges, layers, arcs = BUILDERS[task](rows, cols, order)
            assert A.zdd_size(arcs) <= sum(len(layer) for layer in layers), (task, rows, cols, order)


def test_transposed_grid_has_the_same_numbers():
    for rows, cols in ((2, 5), (3, 4), (2, 7)):
        for builder in BUILDERS.values():
            assert count(builder, rows, cols) == count(builder, cols, rows)


def test_odd_vertex_count_has_no_perfect_matching():
    for rows, cols in ((1, 3), (3, 3), (3, 5), (5, 5), (1, 7)):
        assert count(A.matching_diagram, rows, cols) == 0 == A.kasteleyn(rows, cols)


def test_wide_order_is_not_smaller_than_the_row_order():
    for task, builder in BUILDERS.items():
        for rows, cols in ((3, 3), (3, 4), (4, 4)):
            good = builder(rows, cols, "zeile")
            bad = builder(rows, cols, "schlecht")
            assert A.frontier_info(bad[0])[2] >= A.frontier_info(good[0])[2], (task, rows, cols)
            assert sum(len(l) for l in bad[1]) >= sum(len(l) for l in good[1]), (task, rows, cols)


def test_frontier_of_row_order_is_the_side_plus_one():
    for rows, cols in ((2, 6), (4, 4), (6, 6), (3, 8)):
        assert A.frontier_info(A.grid_edges(rows, cols))[2] == cols + 1


def test_dijkstra_equals_the_diagram_minimum_over_seeds_and_grids():
    for rows, cols in ((2, 2), (3, 3), (3, 5), (4, 4), (5, 5), (6, 3)):
        edges, layers, arcs = A.path_diagram(rows, cols)
        for seed in (1, 2, 3, 17, 99):
            wmap = A.edge_weights(rows, cols, seed)
            w = [wmap[e] for e in edges]
            assert A.evaluate(arcs, w, "min+zahl") == A.dijkstra_count(rows, cols, wmap), (rows, cols, seed)


def test_min_le_any_sampled_weight_le_max_and_count_is_positive():
    import random
    for rows, cols in ((3, 3), (4, 4), (4, 5)):
        edges, layers, arcs = A.path_diagram(rows, cols)
        counts = A.counts_per_node(arcs)
        wmap = A.edge_weights(rows, cols, 11)
        w = [wmap[e] for e in edges]
        mn, nmin = A.evaluate(arcs, w, "min+zahl")
        mx = A.evaluate(arcs, w, "max")
        rng = random.Random(1)
        assert nmin >= 1 and mn <= mx
        for _ in range(50):
            total = sum(w[i] for i in A.sample_path(arcs, counts, rng))
            assert mn <= total <= mx


def test_beam_lower_le_exact_le_upper_and_monotone_with_the_width():
    for rows, cols, seed in ((5, 5, 2), (4, 6, 9), (6, 6, 7)):
        edges, layers, arcs = A.path_diagram(rows, cols)
        wmap = A.edge_weights(rows, cols, seed)
        w = [wmap[e] for e in edges]
        exact = A.evaluate(arcs, w, "max")
        full = max(len(l) for l in layers)
        uppers = []
        for width in (1, 2, 4, 8, 16, 32, 64, 128):
            lb, ub = A.beam_longest(edges, 0, rows * cols - 1, w, width)
            assert lb is None or lb <= exact <= ub, (rows, cols, width)
            uppers.append(ub)
        assert A.beam_longest(edges, 0, rows * cols - 1, w, full) == (exact, exact)
        assert uppers[-1] <= uppers[0]


def test_all_path_counts_grow_with_the_grid():
    values = [count(A.path_diagram, n, n) for n in range(2, 7)]
    assert values == sorted(values) and len(set(values)) == len(values)


def test_semiring_unit_weights_give_the_path_lengths():
    """Mit Gewicht 1 je Kante ist das kleinste Gewicht die Weglänge des kürzesten Wegs: 2(n−1) Kanten, in jedem Gitter."""
    for n in range(2, 7):
        edges, layers, arcs = A.path_diagram(n, n)
        mn, nmin = A.evaluate(arcs, [1] * len(edges), "min+zahl")
        assert mn == 2 * (n - 1)
        from math import comb
        assert nmin == comb(2 * (n - 1), n - 1)


def test_evaluation_state_sizes_match_the_analysis():
    for task, builder in BUILDERS.items():
        a = ev.analyse(ev.Settings(task, 4, 4, "Zeile", 7, 8))
        edges, layers, arcs = builder(4, 4, "zeile")
        assert a.states == sum(len(l) for l in layers) and a.zdd == A.zdd_size(arcs) and a.layer_sizes == [len(l) for l in layers] and a.nedges == len(edges)

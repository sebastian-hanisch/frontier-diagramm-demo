"""Unabhängige Orakel: jede Lösung des Diagramms wird gegen eine eigene Gültigkeitsprüfung geprüft, jede Zahl gegen einen zweiten Weg."""

import random
from fractions import Fraction

import pytest

import fdg_algorithm as A


def diagram_solutions(arcs):
    """Alle Lösungen des Diagramms als Mengen von Kantennummern (Pfade von der Wurzel zu ACCEPT)."""
    out = []

    def rec(i, node, chosen):
        lo, hi = arcs[i][node]
        for child, inc in ((lo, False), (hi, True)):
            c = chosen + [i] if inc else chosen
            if child == A.ACCEPT:
                out.append(frozenset(c))
            elif child != A.REJECT:
                rec(i + 1, child, c)

    rec(0, 0, [])
    return out


def degrees(edges, chosen, nv):
    d = [0] * nv
    for i in chosen:
        a, b = edges[i]
        d[a] += 1
        d[b] += 1
    return d


def components(edges, chosen, vertices):
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in chosen:
        a, b = edges[i]
        parent[find(a)] = find(b)
    return len({find(v) for v in vertices})


def is_simple_path(edges, chosen, nv):
    d = degrees(edges, chosen, nv)
    used = [v for v in range(nv) if d[v] > 0]
    return d[0] == 1 and d[nv - 1] == 1 and all(d[v] in (0, 2) for v in range(1, nv - 1)) and components(edges, chosen, used) == 1


def is_perfect_matching(edges, chosen, nv):
    return all(x == 1 for x in degrees(edges, chosen, nv))


def is_spanning_tree(edges, chosen, nv):
    return len(chosen) == nv - 1 and components(edges, chosen, range(nv)) == 1


def all_subsets(m):
    for mask in range(1 << m):
        yield frozenset(i for i in range(m) if mask >> i & 1)


@pytest.mark.parametrize("rows,cols", [(1, 2), (1, 4), (2, 2), (2, 3), (3, 3), (2, 4), (3, 2)])
def test_path_diagram_equals_all_valid_subsets(rows, cols):
    edges, layers, arcs = A.path_diagram(rows, cols)
    sols = diagram_solutions(arcs)
    brute = {s for s in all_subsets(len(edges)) if is_simple_path(edges, s, rows * cols)}
    assert len(sols) == len(set(sols)) == len(brute) and set(sols) == brute


@pytest.mark.parametrize("rows,cols", [(1, 2), (2, 2), (2, 3), (3, 4), (3, 3), (2, 6)])
def test_matching_diagram_equals_all_valid_subsets(rows, cols):
    edges, layers, arcs = A.matching_diagram(rows, cols)
    sols = diagram_solutions(arcs)
    brute = {s for s in all_subsets(len(edges)) if is_perfect_matching(edges, s, rows * cols)}
    assert len(sols) == len(set(sols)) == len(brute) and set(sols) == brute


@pytest.mark.parametrize("rows,cols", [(1, 3), (2, 2), (2, 3), (3, 3)])
def test_tree_diagram_equals_all_valid_subsets(rows, cols):
    edges, layers, arcs = A.tree_diagram(rows, cols)
    sols = diagram_solutions(arcs)
    brute = {s for s in all_subsets(len(edges)) if is_spanning_tree(edges, s, rows * cols)}
    assert len(sols) == len(set(sols)) == len(brute) and set(sols) == brute


def test_every_order_gives_the_same_solution_sets_as_edges():
    for builder, validator in ((A.path_diagram, is_simple_path), (A.matching_diagram, is_perfect_matching), (A.tree_diagram, is_spanning_tree)):
        sets = []
        for order in A.ORDERS:
            edges, layers, arcs = builder(3, 3, order)
            sols = diagram_solutions(arcs)
            assert all(validator(edges, s, 9) for s in sols)
            sets.append({frozenset(edges[i] for i in s) for s in sols})
        assert sets[0] == sets[1] == sets[2]


def test_path_counts_against_brute_force_for_rectangular_grids():
    for rows in range(1, 5):
        for cols in range(1, 6):
            if rows * cols < 2:
                continue
            count = A.evaluate(A.path_diagram(rows, cols)[2], [1] * len(A.grid_edges(rows, cols)), "zahl")
            assert count == A.brute_paths(rows, cols)[0], (rows, cols)


def test_ladder_has_two_to_the_n_minus_one_paths():
    for n in range(2, 9):
        assert A.evaluate(A.path_diagram(2, n)[2], [1] * len(A.grid_edges(2, n)), "zahl") == 2 ** (n - 1)


def tilings(rows, cols):
    """Dominosteinparkettierungen durch Rückverfolgung über die Felder (eigene Zählung, ohne Diagramm und ohne Formel)."""
    grid = [[False] * cols for _ in range(rows)]

    def rec(pos):
        while pos < rows * cols and grid[pos // cols][pos % cols]:
            pos += 1
        if pos == rows * cols:
            return 1
        r, c = divmod(pos, cols)
        total = 0
        if c + 1 < cols and not grid[r][c + 1]:
            grid[r][c] = grid[r][c + 1] = True
            total += rec(pos + 1)
            grid[r][c] = grid[r][c + 1] = False
        if r + 1 < rows:
            grid[r][c] = grid[r + 1][c] = True
            total += rec(pos + 1)
            grid[r][c] = grid[r + 1][c] = False
        return total

    return rec(0)


def test_matchings_against_domino_tilings_and_kasteleyn():
    for rows, cols in ((2, 2), (2, 5), (3, 4), (4, 4), (4, 5), (6, 6), (3, 3), (1, 6)):
        count = A.evaluate(A.matching_diagram(rows, cols)[2], [1] * len(A.grid_edges(rows, cols)), "zahl")
        assert count == tilings(rows, cols) == A.kasteleyn(rows, cols), (rows, cols)


def test_trees_against_kirchhoff_and_a_second_determinant():
    for rows, cols in ((2, 2), (2, 6), (3, 3), (3, 5), (4, 4), (5, 5)):
        count = A.evaluate(A.tree_diagram(rows, cols)[2], [1] * len(A.grid_edges(rows, cols)), "zahl")
        assert count == A.kirchhoff(rows, cols), (rows, cols)
    assert A.kirchhoff(2, 3) == 15 and A.kirchhoff(3, 4) == 2415


def test_semiring_values_against_dijkstra_and_brute_force():
    rng = random.Random(3)
    for _ in range(8):
        rows, cols = rng.randint(2, 4), rng.randint(2, 5)
        seed = rng.randint(1, 99)
        edges, layers, arcs = A.path_diagram(rows, cols)
        wmap = A.edge_weights(rows, cols, seed)
        w = [wmap[e] for e in edges]
        mn, nmin = A.evaluate(arcs, w, "min+zahl")
        mx = A.evaluate(arcs, w, "max")
        assert (mn, nmin) == A.dijkstra_count(rows, cols, wmap)
        count, bmin, bnmin, bmax = A.brute_paths(rows, cols, wmap)
        assert (count, bmin, bnmin, bmax) == (A.evaluate(arcs, [1] * len(edges), "zahl"), mn, nmin, mx)
        short, long_ = A.best_edges(arcs, w, "min"), A.best_edges(arcs, w, "max")
        assert sum(w[i] for i in short) == mn and sum(w[i] for i in long_) == mx and is_simple_path(edges, short, rows * cols) and is_simple_path(edges, long_, rows * cols)


def test_every_path_has_the_probability_one_over_total_under_the_sampler():
    """Der Sampler wählt an jedem Knoten das Kind mit (Lösungen darunter)/(Lösungen hier): das Produkt entlang jedes Wegs ist exakt 1/Gesamtzahl."""
    edges, layers, arcs = A.path_diagram(3, 3)
    counts = A.counts_per_node(arcs)
    total = counts[0][0]

    def cnt(i, child):
        return 0 if child == A.REJECT else 1 if child == A.ACCEPT else counts[i + 1][child]

    def walk(i, node, p):
        lo, hi = arcs[i][node]
        for child in (lo, hi):
            c = cnt(i, child)
            if c == 0:
                continue
            q = p * Fraction(c, counts[i][node])
            if child == A.ACCEPT:
                yield q
            else:
                yield from walk(i + 1, child, q)

    probs = list(walk(0, 0, Fraction(1)))
    assert len(probs) == total == 12 and all(q == Fraction(1, total) for q in probs)


def test_sampler_chi_square_band_on_a_fixed_seed():
    edges, layers, arcs = A.path_diagram(4, 4)
    counts = A.counts_per_node(arcs)
    rng = random.Random(5)
    seen = {}
    for _ in range(18400):
        p = A.sample_path(arcs, counts, rng)
        seen[p] = seen.get(p, 0) + 1
    exp = 18400 / 184
    chi = sum((c - exp) ** 2 / exp for c in seen.values()) + (184 - len(seen)) * exp
    assert len(seen) == 184 and abs((chi - 183) / (2 * 183) ** 0.5) < 4


def test_beam_bounds_enclose_the_optimum_and_meet_it_at_full_width():
    for rows, cols, seed in ((4, 4, 1), (4, 5, 2), (5, 5, 3)):
        edges, layers, arcs = A.path_diagram(rows, cols)
        wmap = A.edge_weights(rows, cols, seed)
        w = [wmap[e] for e in edges]
        exact = A.evaluate(arcs, w, "max")
        full = max(len(l) for l in layers)
        for width in (1, 2, 4, 8, 16, 32, full):
            lb, ub = A.beam_longest(edges, 0, rows * cols - 1, w, width)
            assert lb is None or lb <= exact <= ub
        assert A.beam_longest(edges, 0, rows * cols - 1, w, full) == (exact, exact)

"""Rechenkern: Frontier-Methode und Entscheidungsdiagramm. Teilgraphen eines Gitters mit Nebenbedingung (einfache Wege, perfekte Paarungen, Spannbäume) werden Kante für Kante entschieden;
der Zustand merkt sich nur, was die Frontier über den Rest wissen muss, gleiche Zustände fallen zusammen. Auf demselben Diagramm: Zählen, kleinstes und größtes Gewicht, Zahl der Optimalen, Ziehen, begrenzte Breite.

Alles mit `int` und `fractions.Fraction`, reines Python. Ein Diagramm ist (layers, arcs): layers[i] = {Zustand: Knoten}, arcs[i][Knoten] = (Kind bei „Kante nein“, Kind bei „Kante ja“),
ein Kind ist eine Knotennummer der nächsten Schicht oder REJECT / ACCEPT."""

import heapq
import math
from fractions import Fraction

REJECT, ACCEPT = -1, -2


# ----------------------------------------------------------------------------- Gitter und Kantenordnung

ORDERS = ("zeile", "spalte", "schlecht")


def grid_edges(rows: int, cols: int, order: str = "zeile") -> list:
    """Kanten des rows×cols-Gitters (Knoten r·cols + c). 'zeile': je Knoten die Kante nach rechts, dann nach unten (Frontier cols + 1); 'spalte': spaltenweise (Frontier rows + 1);
    'schlecht': erst alle waagerechten, dann alle senkrechten Kanten (Frontier = alle Knoten)."""
    if rows < 1 or cols < 1:
        raise ValueError("rows und cols müssen mindestens 1 sein")
    right = lambda r, c: (r * cols + c, r * cols + c + 1)
    down = lambda r, c: (r * cols + c, (r + 1) * cols + c)
    if order == "zeile":
        return [e for r in range(rows) for c in range(cols) for e in ((right(r, c),) if c + 1 < cols else ()) + ((down(r, c),) if r + 1 < rows else ())]
    if order == "spalte":
        return [e for c in range(cols) for r in range(rows) for e in ((down(r, c),) if r + 1 < rows else ()) + ((right(r, c),) if c + 1 < cols else ())]
    if order == "schlecht":
        return [right(r, c) for r in range(rows) for c in range(cols - 1)] + [down(r, c) for r in range(rows - 1) for c in range(cols)]
    raise ValueError(f"unbekannte Ordnung {order!r}")


def frontier_info(edges: list) -> tuple:
    """Je Kante: eintretende Knoten, austretende Knoten (nach der Kante) und größte Frontier."""
    first, last = {}, {}
    for i, (a, b) in enumerate(edges):
        for x in (a, b):
            first.setdefault(x, i)
            last[x] = i
    enter = [[x for x in (a, b) if first[x] == i] for i, (a, b) in enumerate(edges)]
    leave = [[x for x in (a, b) if last[x] == i] for i, (a, b) in enumerate(edges)]
    active, width = set(), 0
    for i in range(len(edges)):
        active |= set(enter[i])
        width = max(width, len(active))
        active -= set(leave[i])
    return enter, leave, width


def build(edges: list, step, init) -> tuple:
    """Diagramm von oben nach unten; gleiche Zustände einer Schicht werden zu einem Knoten."""
    layers = [{init: 0}]
    arcs = []
    for i in range(len(edges)):
        cur, nxt = layers[i], {}
        arc = [None] * len(cur)
        for state, idx in cur.items():
            kids = []
            for inc in (0, 1):
                ns = step(state, i, inc)
                if ns == REJECT or ns == ACCEPT:
                    kids.append(ns)
                else:
                    kids.append(nxt.setdefault(ns, len(nxt)))
            arc[idx] = tuple(kids)
        layers.append(nxt)
        arcs.append(arc)
    return layers, arcs


def zdd_size(arcs: list) -> int:
    """Knotenzahl des reduzierten ZDD (Knoten, deren Ja-Kind REJECT ist, entfallen; gleiche Knoten werden gemeinsam): von unten nach oben."""
    unique = {}
    nxt_ids = None
    for i in range(len(arcs) - 1, -1, -1):
        ids = []
        for lo, hi in arcs[i]:
            l = lo if lo in (REJECT, ACCEPT) else nxt_ids[lo]
            h = hi if hi in (REJECT, ACCEPT) else nxt_ids[hi]
            if h == REJECT:
                ids.append(l)
                continue
            key = (i, l, h)
            if key not in unique:
                unique[key] = len(unique)
            ids.append(("n", unique[key]))
        nxt_ids = ids
    return len(unique)


# ----------------------------------------------------------------------------- Auswertung auf demselben Diagramm

MODES = ("zahl", "min", "max", "min+zahl")


def evaluate_all(arcs: list, weights: list, mode: str) -> list:
    """Wert jedes Knotens, von unten nach oben (Semiring): 'zahl' (+, ×), 'min' (kleinstes Gewicht), 'max' (größtes Gewicht), 'min+zahl' (kleinstes Gewicht und Zahl der Wege mit diesem Gewicht).
    Rückgabe: Liste der Wertelisten je Schicht (Index 0 = Wurzelschicht); None heißt: unter dem Knoten gibt es keine Lösung."""
    if mode not in MODES:
        raise ValueError(f"unbekannter Modus {mode!r}")
    nxt = None
    per = [None] * (len(arcs) + 1)
    for i in range(len(arcs) - 1, -1, -1):
        w = weights[i]
        out = []
        for lo, hi in arcs[i]:
            vals = []
            for child, add in ((lo, 0), (hi, w)):
                if child == REJECT:
                    vals.append(None)
                    continue
                v = 1 if mode == "zahl" and child == ACCEPT else 0 if child == ACCEPT else nxt[child]
                if child == ACCEPT and mode == "min+zahl":
                    v = (0, 1)
                if v is None:
                    vals.append(None)
                elif mode == "zahl":
                    vals.append(v)
                elif mode == "min+zahl":
                    vals.append((v[0] + add, v[1]))
                else:
                    vals.append(v + add)
            a, b = vals
            if a is None or b is None:
                out.append(a if b is None else b)
            elif mode == "zahl":
                out.append(a + b)
            elif mode == "min":
                out.append(min(a, b))
            elif mode == "max":
                out.append(max(a, b))
            else:
                out.append(a if a[0] < b[0] else b if b[0] < a[0] else (a[0], a[1] + b[1]))
        per[i] = out
        nxt = out
    return per


def evaluate(arcs: list, weights: list, mode: str):
    """Wert der Wurzel (für 'zahl' 0, wenn es keine Lösung gibt)."""
    if not arcs:
        raise ValueError("leeres Diagramm")
    value = evaluate_all(arcs, weights, mode)[0][0]
    if value is None and mode == "zahl":
        return 0
    return value


def best_edges(arcs: list, weights: list, mode: str) -> tuple:
    """Die Kantennummern eines besten Wegs (mode 'min' oder 'max') durch Folgen der besseren Kinder."""
    per = evaluate_all(arcs, weights, mode)
    pick = min if mode == "min" else max
    node, chosen = 0, []
    for i in range(len(arcs)):
        lo, hi = arcs[i][node]
        cands = []
        for child, add, inc in ((lo, 0, 0), (hi, weights[i], 1)):
            if child == REJECT:
                continue
            base = 0 if child == ACCEPT else per[i + 1][child]
            if base is not None:
                cands.append((base + add, inc, child))
        if not cands:
            raise ValueError("keine Lösung")
        value, inc, child = pick(cands, key=lambda t: t[0])
        if inc:
            chosen.append(i)
        node = child
        if child == ACCEPT:
            break
    return tuple(chosen)


def counts_per_node(arcs: list) -> list:
    """Zahl der Lösungen unter jedem Knoten, je Schicht."""
    per = evaluate_all(arcs, [1] * len(arcs), "zahl")
    return [[0 if v is None else v for v in layer] if layer is not None else None for layer in per]


def sample_path(arcs: list, counts: list, rng) -> tuple:
    """Gleichverteilter Weg: an jedem Knoten das Kind mit Wahrscheinlichkeit (Lösungen darunter)/(Lösungen hier), ganzzahlig über `randrange`."""
    if counts[0][0] <= 0:
        raise ValueError("keine Lösung")
    node, chosen = 0, []
    for i in range(len(arcs)):
        lo, hi = arcs[i][node]

        def cnt(child, i=i):
            if child == REJECT:
                return 0
            if child == ACCEPT:
                return 1
            return counts[i + 1][child]

        cl, ch = cnt(lo), cnt(hi)
        if rng.randrange(cl + ch) < cl:
            node = lo
        else:
            node = hi
            chosen.append(i)
        if node in (REJECT, ACCEPT):
            break
    return tuple(chosen)


# ----------------------------------------------------------------------------- Frontier: einfache Wege (Simpath)

DONE, S_MARK, T_MARK, S_UNUSED, T_UNUSED = -1, -2, -3, -4, -5
FIN = ("fin",)


def make_path_step(edges: list, s: int, t: int):
    """Schritt für einfache Wege von s nach t. Zustand je Frontier-Knoten: sein Partner (anderes Ende des Teilwegs), er selbst (unbenutzt), S/T (anderes Ende ist der schon geschlossene Start oder das Ziel) oder DONE (Grad 2 oder geschlossenes Ende)."""
    enter, leave, _ = frontier_info(edges)
    last = len(edges) - 1

    def step(state, i, inc):
        if state == FIN:
            return REJECT if inc else (ACCEPT if i == last else FIN)
        mate = dict(state)
        for x in enter[i]:
            mate[x] = S_UNUSED if x == s else T_UNUSED if x == t else x
        u, v = edges[i]
        done_path = False
        if inc:
            if mate[u] == DONE or mate[v] == DONE:
                return REJECT

            def far(x):
                m = mate[x]
                return S_MARK if m == S_UNUSED else T_MARK if m == T_UNUSED else m

            fu, fv = far(u), far(v)
            if fu == v or fv == u:
                return REJECT                                   # schlösse einen Kreis
            if {fu, fv} == {S_MARK, T_MARK}:
                for x, m in mate.items():
                    if x not in (u, v) and m not in (x, DONE):
                        return REJECT                           # ein anderer Teilweg bliebe übrig
                done_path = True
                mate = dict(mate)
                mate[u] = DONE
                mate[v] = DONE
            else:
                new = dict(mate)
                if fu >= 0:
                    new[fu] = fv
                if fv >= 0:
                    new[fv] = fu
                if mate[u] != u:
                    new[u] = DONE
                if mate[v] != v:
                    new[v] = DONE
                mate = new
        for x in leave[i]:
            m = mate[x]
            if m not in (x, DONE):
                return REJECT                                   # offenes Ende verlässt die Frontier (auch ein unbenutzter Start oder ein unbenutztes Ziel)
            del mate[x]
        if done_path:
            return ACCEPT if i == last else FIN
        if i == last:
            return REJECT
        return tuple(sorted(mate.items()))

    return step


def path_diagram(rows: int, cols: int, order: str = "zeile") -> tuple:
    """Diagramm aller einfachen Wege von der oberen linken zur unteren rechten Ecke; Rückgabe (edges, layers, arcs)."""
    nv = rows * cols
    if nv < 2:
        raise ValueError("das Gitter braucht mindestens zwei Knoten")
    edges = grid_edges(rows, cols, order)
    layers, arcs = build(edges, make_path_step(edges, 0, nv - 1), ())
    return edges, layers, arcs


# ----------------------------------------------------------------------------- Frontier: perfekte Paarungen

def make_matching_step(edges: list):
    enter, leave, _ = frontier_info(edges)
    last = len(edges) - 1

    def step(state, i, inc):
        matched = set(state)
        u, v = edges[i]
        if inc:
            if u in matched or v in matched:
                return REJECT
            matched |= {u, v}
        for x in leave[i]:
            if x not in matched:
                return REJECT
            matched.discard(x)
        if i == last:
            return ACCEPT
        return tuple(sorted(matched))

    return step


def matching_diagram(rows: int, cols: int, order: str = "zeile") -> tuple:
    if rows * cols < 2:
        raise ValueError("das Gitter braucht mindestens zwei Knoten")
    edges = grid_edges(rows, cols, order)
    layers, arcs = build(edges, make_matching_step(edges), ())
    return edges, layers, arcs


def kasteleyn(m: int, n: int) -> int:
    """Zahl der Dominosteinparkettierungen des m×n-Bretts: Π_j Π_k (4cos²(πj/(m+1)) + 4cos²(πk/(n+1))) (Kasteleyn, Temperley, Fisher), auf die nächste ganze Zahl gerundet."""
    prod = 1.0
    for j in range(1, (m + 1) // 2 + 1):
        for k in range(1, (n + 1) // 2 + 1):
            prod *= 4 * math.cos(math.pi * j / (m + 1)) ** 2 + 4 * math.cos(math.pi * k / (n + 1)) ** 2
    return round(prod)


# ----------------------------------------------------------------------------- Frontier: Spannbäume

def make_tree_step(edges: list):
    """Zustand: Komponentenmarke je Frontier-Knoten (kanonisch durchnummeriert); ein Kreis entsteht, wenn beide Enden dieselbe Marke haben."""
    enter, leave, _ = frontier_info(edges)
    last = len(edges) - 1

    def canon(lab):
        seen, out = {}, []
        for x, l in sorted(lab.items()):
            out.append((x, seen.setdefault(l, len(seen))))
        return tuple(out)

    def step(state, i, inc):
        lab = dict(state)
        for x in enter[i]:
            lab[x] = 1000 + x
        u, v = edges[i]
        if inc:
            if lab[u] == lab[v]:
                return REJECT
            a, b = lab[u], lab[v]
            lab = {x: (a if l == b else l) for x, l in lab.items()}
        for x in leave[i]:
            l = lab[x]
            rest = [y for y in lab if y != x]
            if not any(lab[y] == l for y in rest):
                if rest or i != last:
                    return REJECT                               # die Komponente von x wäre abgeschlossen, aber es gibt noch Knoten oder Kanten
            del lab[x]
        if i == last:
            return ACCEPT
        return canon(lab)

    return step


def tree_diagram(rows: int, cols: int, order: str = "zeile") -> tuple:
    if rows * cols < 2:
        raise ValueError("das Gitter braucht mindestens zwei Knoten")
    edges = grid_edges(rows, cols, order)
    layers, arcs = build(edges, make_tree_step(edges), ())
    return edges, layers, arcs


def kirchhoff(rows: int, cols: int) -> int:
    """Zahl der Spannbäume des Gitters: Determinante des Laplace-Matrix ohne eine Zeile und Spalte, in Brüchen (Gauß)."""
    n = rows * cols
    L = [[Fraction(0)] * n for _ in range(n)]
    for a, b in grid_edges(rows, cols):
        L[a][a] += 1
        L[b][b] += 1
        L[a][b] -= 1
        L[b][a] -= 1
    M = [row[1:] for row in L[1:]]
    det = Fraction(1)
    m = n - 1
    for c in range(m):
        piv = next(r for r in range(c, m) if M[r][c] != 0)
        if piv != c:
            M[c], M[piv] = M[piv], M[c]
            det = -det
        det *= M[c][c]
        for r in range(c + 1, m):
            f = M[r][c] / M[c][c]
            for k in range(c, m):
                M[r][k] -= f * M[c][k]
    return int(det)


# ----------------------------------------------------------------------------- Orakel für Wege

def brute_paths(rows: int, cols: int, weights_by_edge: dict | None = None) -> tuple:
    """Alle einfachen Wege von der oberen linken zur unteren rechten Ecke durch Rückverfolgung: (Zahl, kleinstes Gewicht, Zahl der kleinsten, größtes Gewicht); Gewichte None ohne Gewichtsangabe."""
    nv = rows * cols
    adj = {v: [] for v in range(nv)}
    for a, b in grid_edges(rows, cols):
        w = weights_by_edge[(a, b)] if weights_by_edge is not None else 0
        adj[a].append((b, w))
        adj[b].append((a, w))
    count = 0
    best_min, n_min, best_max = None, 0, None
    visited = [False] * nv
    visited[0] = True

    def rec(v, w):
        nonlocal count, best_min, n_min, best_max
        if v == nv - 1:
            count += 1
            if weights_by_edge is not None:
                if best_min is None or w < best_min:
                    best_min, n_min = w, 1
                elif w == best_min:
                    n_min += 1
                if best_max is None or w > best_max:
                    best_max = w
            return
        for u, wu in adj[v]:
            if not visited[u]:
                visited[u] = True
                rec(u, w + wu)
                visited[u] = False

    rec(0, 0)
    return count, best_min, n_min, best_max


def dijkstra_count(rows: int, cols: int, weights_by_edge: dict) -> tuple:
    """Kleinstes Gewicht und Zahl der kürzesten Wege (positive Gewichte: jeder kürzeste Weg ist einfach)."""
    nv = rows * cols
    adj = {v: [] for v in range(nv)}
    for a, b in grid_edges(rows, cols):
        adj[a].append((b, weights_by_edge[(a, b)]))
        adj[b].append((a, weights_by_edge[(a, b)]))
    dist = {0: 0}
    cnt = {0: 1}
    heap = [(0, 0)]
    done = set()
    while heap:
        d, v = heapq.heappop(heap)
        if v in done:
            continue
        done.add(v)
        for u, w in adj[v]:
            nd = d + w
            if u not in dist or nd < dist[u]:
                dist[u], cnt[u] = nd, cnt[v]
                heapq.heappush(heap, (nd, u))
            elif nd == dist[u] and u not in done:
                cnt[u] += cnt[v]
    return dist[nv - 1], cnt[nv - 1]


def edge_weights(rows: int, cols: int, seed: int, low: int = 1, high: int = 9) -> dict:
    """Gewichte 1 bis 9 je Kante, unabhängig von der Kantenordnung: gezogen in Zeilenordnung mit dem Seed."""
    import random
    rng = random.Random(seed)
    return {e: rng.randint(low, high) for e in grid_edges(rows, cols, "zeile")}


# ----------------------------------------------------------------------------- begrenzte Breite

def beam_longest(edges: list, s: int, t: int, weights: list, width: int) -> tuple:
    """Begrenzte Breite für den längsten Weg: je Schicht höchstens `width` Zustände (die mit dem größten Teilgewicht). Die abgeschnittenen Zustände begrenzen die obere Schranke:
    ihr größtes Teilgewicht plus alle restlichen positiven Gewichte. Rückgabe (untere Schranke, obere Schranke); beide None, wenn nichts Zulässiges überlebt."""
    if width < 1:
        raise ValueError("width >= 1 verlangt")
    step = make_path_step(edges, s, t)
    remaining_pos = [sum(max(w, 0) for w in weights[i + 1:]) for i in range(len(edges))]
    layer = {(): 0}
    best_final = None
    ub = -math.inf
    for i in range(len(edges)):
        nxt = {}
        for state, val in layer.items():
            for inc in (0, 1):
                ns = step(state, i, inc)
                value = val + (weights[i] if inc else 0)
                if ns == REJECT:
                    continue
                if ns == ACCEPT:
                    best_final = value if best_final is None else max(best_final, value)
                    continue
                if ns not in nxt or value > nxt[ns]:
                    nxt[ns] = value
        if len(nxt) > width:
            ranked = sorted(nxt.items(), key=lambda kv: -kv[1])
            ub = max(ub, ranked[width][1] + remaining_pos[i])
            nxt = dict(ranked[:width])
        layer = nxt
    if best_final is None:
        return None, None
    return best_final, max(best_final, ub)


# ----------------------------------------------------------------------------- Textbild

def grid_art(rows: int, cols: int, edges: list, chosen) -> str:
    """Das Gitter als Text: o für Knoten, ─ und │ für gewählte Kanten (Kante = Position in `edges`), · für nicht gewählte."""
    chosen_set = {edges[i] for i in chosen}
    lines = []
    for r in range(rows):
        row = ""
        for c in range(cols):
            row += "o"
            if c + 1 < cols:
                a, b = r * cols + c, r * cols + c + 1
                row += "──" if (a, b) in chosen_set else "  "
        lines.append(row)
        if r + 1 < rows:
            row = ""
            for c in range(cols):
                a, b = r * cols + c, (r + 1) * cols + c
                row += ("│" if (a, b) in chosen_set else " ") + "  "
            lines.append(row.rstrip())
    return "\n".join(lines)


def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d

"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

TASKS = ("Einfache Wege", "Perfekte Paarungen", "Spannbäume")
DEFAULT_TASK = "Einfache Wege"
ORDER_NAMES = {"zeile": "Zeile", "spalte": "Spalte", "schlecht": "Schlecht (erst alle waagerechten Kanten)"}
ORDERS = tuple(ORDER_NAMES.values())
ORDER_KEYS = {v: k for k, v in ORDER_NAMES.items()}
DEFAULT_ORDER = "Zeile"

SIDE_MIN, SIDE_MAX, DEFAULT_ROWS, DEFAULT_COLS = 1, 10, 6, 6
SIDE_CAP = {"Einfache Wege": 9, "Perfekte Paarungen": 10, "Spannbäume": 8}   # größte Seitenlänge je Aufgabe
SEED_MIN, SEED_MAX, DEFAULT_SEED = 1, 99, 7
WIDTH_MIN, WIDTH_MAX, DEFAULT_WIDTH = 1, 512, 8

BAD_ORDER_EDGE_LIMIT = 24        # schlechte Kantenordnung nur bis zu so vielen Kanten (4×4-Gitter), sonst Zeilenordnung mit Hinweis
BRUTE_VERTEX_LIMIT = 25          # Brute Force der einfachen Wege bis zu so vielen Knoten (5×5)
GRAPH_DRAW_MAX = 6               # Spielwiese: Seitenlänge höchstens

KNOWN_PATHS = {2: 2, 3: 12, 4: 184, 5: 8512, 6: 1262816, 7: 575780564, 8: 789360053252, 9: 3266598486981642, 10: 41044208702632496804, 11: 1568758030464750013214100}   # aus dem Gedächtnis (A007764)

EXP_SIZE_PATH_NS = tuple(range(2, 11))
EXP_SIZE_MATCHINGS = ((2, 2), (2, 8), (4, 4), (6, 6), (8, 8), (8, 10), (10, 10))
EXP_SIZE_TREES = ((2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7))
EXP_CHECK_BRUTE_NS = (2, 3, 4, 5)
EXP_ORDER_PATHS = ((3, 3), (3, 5), (4, 4))
EXP_ORDER_MATCHINGS = ((3, 4), (4, 4), (4, 5))
EXP_ORDER_TREES = ((3, 3), (3, 4), (4, 4))
EXP_SEM_NS = (4, 5, 6, 7)
EXP_SEM_SEED = 20261102
EXP_SAMPLE_N, EXP_SAMPLE_DRAWS = 4, 36800
EXP_BEAM_NS = (6, 7)
EXP_BEAM_WIDTHS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)
PLAY_ROWS_DEFAULT, PLAY_COLS_DEFAULT, PLAY_SEED_DEFAULT = 4, 4, 5

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: einfache Wege im 6×6-Gitter": {"task": "Einfache Wege", "rows": 6, "cols": 6, "order": "Zeile", "seed": 7, "width": 8},
    "Dominosteine auf dem 8×8-Brett": {"task": "Perfekte Paarungen", "rows": 8, "cols": 8, "order": "Zeile", "seed": 7, "width": 8},
    "Spannbäume des 7×7-Gitters": {"task": "Spannbäume", "rows": 7, "cols": 7, "order": "Zeile", "seed": 7, "width": 8},
    "Schlechte Kantenordnung, 4×4-Wege": {"task": "Einfache Wege", "rows": 4, "cols": 4, "order": "Schlecht (erst alle waagerechten Kanten)", "seed": 7, "width": 8},
    "Längster Weg mit begrenzter Breite, 7×7": {"task": "Einfache Wege", "rows": 7, "cols": 7, "order": "Zeile", "seed": 7, "width": 4},
    "Wege im 5×5-Gitter, Seed 4": {"task": "Einfache Wege", "rows": 5, "cols": 5, "order": "Zeile", "seed": 4, "width": 8},
}
PRESET_HELP = {
    "Standardfall: einfache Wege im 6×6-Gitter": "1.262.816 einfache Wege von Ecke zu Ecke in einem Diagramm mit nur 2.323 Knoten (4.926 Zustände vor der Reduktion); dasselbe Diagramm liefert kleinstes und größtes Gewicht und die Zahl der kürzesten Wege.",
    "Dominosteine auf dem 8×8-Brett": "12.988.816 perfekte Paarungen (Dominosteinparkettierungen) in 2.298 Knoten; die Zahl ist gleich der Formel von Kasteleyn.",
    "Spannbäume des 7×7-Gitters": "19.872.369.301.840.986.112 Spannbäume in 23.788 Knoten; gleich der Determinante der Laplace-Matrix (Kirchhoff).",
    "Schlechte Kantenordnung, 4×4-Wege": "Erst alle waagerechten, dann alle senkrechten Kanten: die Frontier wächst auf 16 Knoten und das Diagramm von 285 auf 24.430 Zustände (822 statt 134 reduzierte Knoten), obwohl die 184 Wege dieselben sind.",
    "Längster Weg mit begrenzter Breite, 7×7": "Bei Breite 4 behält das Diagramm nur die 4 besten Teilwege je Schicht: untere und obere Schranke für den längsten Weg, der exakte Wert steht daneben.",
    "Wege im 5×5-Gitter, Seed 4": "8.512 Wege; mit diesen Gewichten (Seed 4) hat das kleinste Gewicht 28 genau zwei Wege; das Diagramm zählt sie mit.",
}

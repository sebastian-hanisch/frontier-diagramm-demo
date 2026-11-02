"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_grid_2x2():
    """2×2-Gitter, Knoten 0 1 / 2 3, Kanten in Zeilenordnung (0,1), (0,2), (1,3), (2,3). Einfache Wege 0 nach 3: 0-1-3 (Kanten 0 und 2) und 0-2-3 (Kanten 1 und 3), also 2;
    mit den Gewichten 1, 4, 2, 3 der vier Kanten: 1 + 2 = 3 und 4 + 3 = 7, kleinstes 3 (ein Weg), größtes 7. Perfekte Paarungen {(0,1), (2,3)} und {(0,2), (1,3)}: 2. Spannbäume: je eine Kante des Vierecks weglassen: 4.
    Frontier: Knoten 0 und 1 treten bei Kante 0 ein; die größte Frontier hat 3 Knoten (0, 1, 2 nach Kante 1)."""
    return {"edges": [(0, 1), (0, 2), (1, 3), (2, 3)], "paths": 2, "weights": [1, 4, 2, 3], "min": 3, "n_min": 1, "max": 7, "min_edges": (0, 2), "max_edges": (1, 3),
            "matchings": 2, "trees": 4, "frontier": 3, "layers": [1, 2, 2, 2]}


@pytest.fixture
def hand_strips():
    """1×n-Gitter (ein Pfad): ein Weg, ein Spannbaum; perfekte Paarung genau für gerade n."""
    return {"paths": 1, "trees": 1, "matchings_even": 1, "matchings_odd": 0}


@pytest.fixture
def hand_art():
    """2×2-Gitter mit den Kanten 0 und 2 (0-1, 1-3): oben o──o, rechts senkrecht │ unter dem zweiten Knoten, unten o  o."""
    return "o──o\n   │\no  o"

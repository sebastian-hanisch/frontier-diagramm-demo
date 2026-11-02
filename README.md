# Frontier und Diagramm – Lösungen zählen, ohne sie aufzuzählen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-frontier-diagramm-demo.streamlit.app/)** -->

Stück 13 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7), `zaehlen-nach-parameter-demo` (Stück 8), `asymptotik-demo` (Stück 9), `gleichverteilt-ziehen-demo` (Stück 10), `burnside-polya-demo` (Stück 11) und `isomorphieausschluss-demo` (Stück 12); das letzte hat die **Symmetrie** in der Suche gebrochen. Diese Demo fasst stattdessen **gleiche Teilprobleme** zusammen: Die **Frontier-Methode** (Knuths Simpath) baut für die Kanten eines Gitters ein **Entscheidungsdiagramm** Kante für Kante, und zwei Teilauswahlen mit demselben **Zustand** an der Frontier (den Knoten, die noch Kanten bekommen können) laufen im selben Diagrammknoten weiter. Das Diagramm zählt die einfachen Wege, die perfekten Paarungen (Dominosteine) und die Spannbäume des Gitters, ohne eine einzige Lösung aufzuzählen; auf demselben Diagramm läuft das Semiring aus Stück 4 (Zahl, kleinstes Gewicht, Zahl der kürzesten, größtes Gewicht) und das gleichverteilte Ziehen aus Stück 10.

## Warum dieses Problem

Die Zahl der einfachen Wege von einer Ecke zur gegenüberliegenden im n×n-Gitter wächst wie exp(c·n²), das Diagramm nur wie ein Vielfaches von 3,4 bis 4,4 je Seitenlänge: Im 10×10-Gitter stehen 41 Trillionen Wege in 377.106 Knoten. Wer so ein Diagramm hat, hat die ganze Lösungsmenge in der Hand: zählen, optimieren, gleichverteilt ziehen. Aber die Größe hängt an der **Kantenordnung**, und eine schlechte Ordnung macht aus dem Diagramm ein Wörterbuch aller Teilauswahlen. Die Demo misst beides.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt:** 1.262.816 einfache Wege im 6×6-Gitter stehen in einem Diagramm mit 2.323 Knoten (4.926 Zustände vor der Reduktion), 12.988.816 Dominosteinparkettierungen des 8×8-Bretts in 2.298 Knoten, 19.872.369.301.840.986.112 Spannbäume des 7×7-Gitters in 23.788 Knoten.
- **Die Kantenordnung entscheidet:** Dieselben 184 Wege im 4×4-Gitter brauchen in der Zeilenordnung 285 Zustände (134 Knoten), in der schlechten Ordnung (erst alle waagerechten Kanten) 24.430 Zustände (822 Knoten); beim 5×5-Gitter sind es in der schlechten Ordnung schon über 6,5 Millionen Zustände (nur in Phase 0 gerechnet, die App begrenzt die schlechte Ordnung auf 24 Kanten).
- **Die obere Schranke bei begrenzter Breite ist schwach:** Die untere Schranke für den längsten Weg ist schon bei Breite 16 (n = 6) und 64 (n = 7) das Optimum; die einfache obere Schranke (abgeschnittene Zustände mit allen restlichen positiven Gewichten) schließt erst, wenn nichts mehr abgeschnitten wird. Echte relaxierte Diagramme, die ähnliche Zustände zusammenführen, wären stärker; sie sind nicht gebaut.
- **Eigene Fehler im Bau (nicht in der Messung):** (1) Das Phase-0-Skript ließ nach einem fertigen s–t-Weg die Paarungen der beiden Endknoten ungesetzt und lehnte den Zustand beim Verlassen ab; die Zahlen waren erst nach der Korrektur gleich der Brute-Force-Zählung. (2) Zwei Zehnerpotenzen im Plan waren falsch (10²⁵ statt 10²⁴, 10²⁰ statt 10¹⁹); Plan und Merkzettel korrigiert. (3) Ein Handwert im Test (Spaltenordnung des 2×2-Gitters) war falsch, der Code richtig. (4) Der Test der Paarungen im 4×4-Gitter gegen alle 2²⁴ Teilmengen brauchte anderthalb Minuten; ersetzt durch 3×3, 3×4 und 2×6 (Teilmengen) plus 4×4 gegen Parkettierungen und Kasteleyn. (5) „Lösungen je Knoten“ hatte ab 1.000 keinen Tausenderpunkt.
- **Präfix `fdg_`, Port 9326:** `frd_` gehört `frontdoor-demo`.

## Modell

**Gitter:** Knoten zeilenweise nummeriert, Kanten nach einer von drei Ordnungen (`zeile`, `spalte`, `schlecht` = erst alle waagerechten, dann alle senkrechten). `frontier_info` liefert für jede Kante die Knoten, die eintreten und austreten, und die größte Frontier.

**Diagramm:** `build` läuft Kante für Kante durch die Schichten; ein Zustand je Frontier beschreibt, was die bisherige Auswahl für die Zukunft bedeutet. Für **einfache Wege** ist es die Paarung jedes Frontierknotens (unberührt, Endpunkt eines Teilwegs mit Partner, Start, Ziel, fertig); für **perfekte Paarungen** die Menge der schon gepaarten Frontierknoten; für **Spannbäume** die Zusammenhangskomponente jedes Frontierknotens. Ein Knoten, der die Frontier verlässt, muss dann in einem erlaubten Endzustand sein, sonst wird der Zustand verworfen. Die Reduktion lässt Knoten weg, deren Kante „nehmen“ ins Leere führt, und teilt identische Knoten. **Auswertung:** `evaluate` rechnet in vier Semiringen ((+, ×) Zahl, (min, +), (max, +) und (min, +, Zahl) als Paare), `counts_per_node` und `sample_path` ziehen gleichverteilt (Stück 10), `best_edges` liefert einen besten Weg.

**Prüfwege:** `brute_paths` verfolgt alle Wege zurück (bis 25 Knoten), `dijkstra_count` zählt kürzeste Wege mit, `kasteleyn` (Kosinusformel für Dominosteine, ohne Diagramm) und `kirchhoff` (Determinante der Laplace-Matrix mit `Fraction`) prüfen die Zahlen der Paarungen und Spannbäume; die Zahlen der Wege im n×n-Gitter bis n = 11 stehen als Folge aus dem Gedächtnis. `beam_longest` hält je Schicht nur die besten Zustände (untere Schranke: bester vollständiger Weg; obere Schranke: abgeschnittene Zustände mit allen restlichen positiven Gewichten).

## Methodik

- **Prüfungen in der App:** Das Diagramm gegen Brute Force und die Folge aus dem Gedächtnis (Wege), gegen Kasteleyn (Paarungen) und gegen Kirchhoff (Spannbäume); Semiring gegen Dijkstra mit Zählung. Ein Widerspruch ist ein Fehler.
- **Eingabe:** Aufgabe (drei), Zeilen und Spalten (1 bis 10; Obergrenze je Aufgabe 9 für Wege, 10 für Paarungen, 8 für Spannbäume, mindestens zwei Knoten), Kantenordnung (die schlechte nur bis 24 Kanten), Seed der Gewichte (1 bis 99), Breite für die Schranken (1 bis 512). Die Adresszeile spiegelt die Einstellung.
- **Fünf Experimente:** (1) Diagramm gegen Lösungszahl, (2) dieselben Zahlen auf anderen Wegen, (3) die Kantenordnung, (4) ein Diagramm, vier Auswertungen, und Ziehen, (5) begrenzte Breite. Dazu eine Spielwiese: ein Gitter bis 6×6 mit Gewichten, dem gezogenen, dem kürzesten und dem längsten Weg als Zeichnung.
- **Gewichte** 1 bis 9 je Kante, gezogen in einer festen Kantenreihenfolge (Zeilenordnung), damit sie von der Kantenordnung des Diagramms unabhängig sind. Alles ist deterministisch.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_fdg.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handinstanz 2×2 | Kanten (0,1), (0,2), (1,3), (2,3); 2 einfache Wege (0–1–3 und 0–2–3), 2 perfekte Paarungen, 4 Spannbäume; mit den Gewichten 1, 4, 2, 3 kleinstes Gewicht 3 (ein Weg), größtes 7; Frontier 3, Schichtgrößen 1, 2, 2, 2, Diagramm mit 4 Knoten |
| Wege im n×n-Gitter, n = 2 bis 10 | 2, 12, 184, 8.512, 1.262.816, 575.780.564, 789.360.053.252, 3.266.598.486.981.642, 41.044.208.702.632.496.804; Diagrammknoten 4, 27, 134, 583, 2.323, 8.729, 31.481, 110.189, 377.106; Zustände 7, 54, 285, 1.246, 4.926, 18.271, 64.993, 224.462, 758.682; Frontier n + 1 |
| Wege je Knoten | 0,5 (2×2), 1,37 (4×4), 14,6 (5×5), 543,6 (6×6), 65.961,8 (7×7), 2,5·10⁷ (8×8); Knotenzahl wächst um das 3,4- bis 4,4-Fache je Seitenlänge ab n = 4 |
| Perfekte Paarungen | 2×8: 34 in 120 Knoten; 4×4: 36 in 48; 6×6: 6.728 in 363; 8×8: 12.988.816 in 2.298; 8×10: 1.031.151.241 in 9.385; 10×10: 258.584.046.368 in 13.159; gleich Kasteleyn und Parkettierungen; ungerade Knotenzahl: 0 |
| Spannbäume | 3×3: 192 in 39; 4×4: 100.352 in 214; 5×5: 557.568.000 in 1.078; 6×6: 32.565.539.635.200 in 5.153; 7×7: 19.872.369.301.840.986.112 in 23.788; gleich Kirchhoff |
| Kantenordnung (Zustände Zeile / schlecht) | Wege 3×3: 54 / 308; 3×5: 431 / 23.058; 4×4: 285 / 24.430 (Frontier 5 / 16; Knoten 134 / 822); Paarungen 3×4: 71 / 568; 4×4: 113 / 3.028; 4×5: 230 / 20.227 (Knoten 93 / 407); Spannbäume 3×3: 46 / 263; 3×4: 153 / 2.259; 4×4: 251 / 19.283 (Knoten 214 / 7.704); die Lösungszahlen sind gleich |
| Semiring und Dijkstra | n = 4: 184 Wege, kleinstes Gewicht 19 (1 Weg), größtes 57; n = 5: 8.512, 29, 129; n = 6: 1.262.816, 34, 206; n = 7: 575.780.564, 38, 263; Dijkstra mit Zählung gleich, Brute Force gleich für n ≤ 5 |
| Gleichverteilt ziehen, 4×4 | in 36.800 Ziehungen alle 184 Wege, z = 0,64 (χ² = 195,19 bei 183 Freiheitsgraden); im Test jeder Weg mit der Wahrscheinlichkeit 1/12 im 3×3-Gitter, exakt über Brüche |
| Begrenzte Breite, n = 6 (exakt 206, größte Schicht 136) | untere Schranke 159, 192, 190, 191 bei Breite 1, 2, 4, 8; 206 ab Breite 16; obere Schranke 313 bei Breite 1, 248 bei 128, 206 ab 256 |
| Begrenzte Breite, n = 7 (exakt 263, größte Schicht 348) | untere Schranke 228, 247, 255, 260, 260, 260 bei Breite 1 bis 32; 263 ab Breite 64; obere Schranke 396 bei Breite 1, 338 bei 256, 263 bei 512 |
| Voreinstellungen | Seed 4, 5×5: kleinstes Gewicht 28 mit genau 2 Wegen, größtes 131; 7×7 bei Breite 4: untere Schranke 269, obere 400, exakt 278 (kleinstes 39 mit 2 Wegen); 6×6 bei Breite 8: 180, 266, 186 (kleinstes 30 mit 2 Wegen) |
| Spielwiese | 4×4, Seed 5: 184 Wege, gezogener Weg Gewicht 69, kürzester 18, längster 78; 2×3, Seed 1: 4 Wege, 25, 13, 25 |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Die Folge der Wege im n×n-Gitter (A007764) bis n = 11 und Knuths Frontier-Methode (Simpath) wurden nicht an einer Quelle gelesen. Brute Force bis n = 5, Dijkstra, Kasteleyn und Kirchhoff stützen die Ausgaben; die Folge bis n = 10 steht nur gegen das Diagramm, nicht gegen einen zweiten Weg.
- **Gitter, nicht allgemeine Graphen:** Die Frontier-Methode gilt für jeden Graphen; Größe und Kantenordnung sind hier nur für Gitter gemessen. Für allgemeine Graphen ist die Wahl der Ordnung selbst ein hartes Problem.
- **Die Reduktion ist einfach:** Knoten mit „nehmen“ ins Leere fallen weg, gleiche Knoten werden geteilt; weitergehende Verfahren (ZDD-Algebra, Zusammenführen ähnlicher Zustände) sind nicht gebaut. Die obere Schranke bei begrenzter Breite ist die einfachste, keine relaxierte Diagrammschranke.
- **Aufwand als Zustände und Knoten**, nicht als Zeit; der erste Aufruf braucht einige Sekunden, weil die Experimente einmal rechnen (danach zwischengespeichert).
- **Obergrenzen der App:** Wege bis 9×9, Paarungen bis 10×10, Spannbäume bis 8×8; die schlechte Kantenordnung nur bis 24 Kanten (4×4); Brute Force bis 25 Knoten.
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (2×2 für Wege, Paarungen, Spannbäume, Gewichte, Frontier, Schichten, Zeichnung), Streifen 1×n; Diagramm gegen **alle** Kantenteilmengen für kleine Gitter (jede Lösung des Diagramms mit eigener Gültigkeitsprüfung: einfacher s–t-Weg, perfekte Paarung, Spannbaum), alle drei Kantenordnungen mit denselben Lösungsmengen; Wege gegen Brute Force für alle Gitter bis 4×5, Leiter 2×n gleich 2ⁿ⁻¹; Paarungen gegen Parkettierungen durch Rückverfolgung und Kasteleyn; Spannbäume gegen Kirchhoff; Semiring gegen Dijkstra und Brute Force an zufälligen Gittern und Seeds; Ziehen exakt über Brüche und ein χ²-Band; Schranken gegen den exakten Wert.
- **Eigenschaften:** Lösungszahl unabhängig von der Kantenordnung; Diagramm nie größer als die Zustandszahl; Gitter und Transponiertes gleich; ungerade Knotenzahl keine Paarung; schlechte Ordnung nie besser als die Zeilenordnung; Frontier der Zeilenordnung gleich n + 1; Dijkstra gleich Diagramm für alle Gitter und Seeds; kleinstes Gewicht bei Einheitsgewichten 2(n − 1) mit C(2(n − 1), n − 1) Wegen; Schranken umschließen den exakten Wert.
- **Randfälle:** 1×1 wird 1×2, Obergrenzen je Aufgabe mit Hinweis, schlechte Ordnung über 24 Kanten, unbekannte Aufgabe und Ordnung, Breite außerhalb der Regler, Brute Force über 25 Knoten, Folge nur für quadratische Gitter, Aufgaben ohne Semiring, Spielwiese außerhalb der Grenzen, Formatierung.
- **Urteilstexte:** genauer Wortlaut für alle Voreinstellungen und Experimente.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jedes Preset, jede Aufgabe mit jeder Ordnung, Permalink mit Müll, Spielwiese, PDF für jede Aufgabe und Ordnung, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

135 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `fdg_algorithm.py` | Kern: Gitter, Frontier, Diagramm für Wege, Paarungen und Spannbäume, Semiring, Ziehen, Prüfwege, begrenzte Breite |
| `fdg_constants.py` | Regler-Grenzen, Experiment-Konstanten, Farben, Presets |
| `fdg_evaluation.py` | Analyse, Experimente, Urteilstexte, Formatierung |
| `fdg_layout.py` | Fester Kopf (Stylesheet) |
| `fdg_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `fdg_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `fdg_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Allgemeine Graphen und Ordnungssuche:** Gitter genügen, um zu zeigen, wie die Ordnung die Größe bestimmt.
- **ZDD-Algebra (Vereinigung, Schnitt, Mengen aus Mengen) und Zusammenführen ähnlicher Zustände (relaxierte Diagramme):** nur genannt.
- **Tutte-Polynom und chromatisches Polynom über dieselbe Methode:** Stück 14.
- **Schätzen, wo das Zählen aufhört (Monte Carlo, Importance Sampling):** Stück 15.
- **Verwandte Demos:** `gleichverteilt-ziehen-demo` (Ziehen aus Zählungen), `semiring-rekursion-demo` (Semiring), `burnside-polya-demo` und `isomorphieausschluss-demo` (Symmetrie); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).

# Sitzverteilung: Hamilton, Jefferson, Webster, Huntington–Hill – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-sitzverteilung-demo.streamlit.app/)** -->

Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“). Verwandt: [wahlregeln-demo](https://github.com/sebastian-hanisch/wahlregeln-demo) (Mehrheitsregeln bei Wahlen), [wahlaxiome-demo](https://github.com/sebastian-hanisch/wahlaxiome-demo) (welche Eigenschaften sich ausschließen), [gemeinsames-budget-demo](https://github.com/sebastian-hanisch/gemeinsames-budget-demo) (Verteilen mit Zustimmung) und [unteilbare-gueter-demo](https://github.com/sebastian-hanisch/unteilbare-gueter-demo) (ganze Güter fair verteilen).
Die Demo fragt: **Ein Beirat hat h Sitze und soll sie auf Verbände nach deren Mitgliederzahlen verteilen. Weil Sitze ganze Zahlen sind, bleibt ein Rest, und jedes Verfahren verteilt ihn anders. Wie oft macht das einen Unterschied, und was geht dabei schief?** Verglichen werden fünf Verfahren: **Hamilton** (größter Rest), **Jefferson** (D'Hondt), **Webster** (Sainte-Laguë), **Huntington–Hill** (jeder Verband bekommt zuerst einen Sitz) und die **Quotenmethode** von Balinski und Young. Gezeigt werden drei Fehler, an denen Verfahren scheitern können: ein Verband bekommt weniger als seine **abgerundete** oder mehr als seine **aufgerundete Quote** (**Quotenregel**), ein Verband **verliert einen Sitz, wenn das Haus wächst** (**Alabama-Paradox**), oder er verliert einen Sitz an einen Verband, **obwohl er stärker wächst** (**Bevölkerungsparadox**).

Der Kern ist eigener Code (`fractions` nur für die exakten Quoten und Divisor-Bereiche): alle Verteilungen werden mit **ganzen Zahlen** gerechnet (Kreuzmultiplikation statt Brüchen, Quadrate statt Wurzeln), es gibt keine Rundungsfehler. Unabhängige Orakel in den Tests rechnen mit exakten Brüchen, mit der **globalen Rangliste aller Ansprüche**, mit der **Aufzählung aller Verteilungen** und mit dem **Divisor aus der Rundungsregel**.

## Warum dieses Problem

Wer Sitze, Mandate oder Stellen nach einem Schlüssel verteilt, stößt auf das Rundungsproblem: 18,43 Sitze gibt es nicht. Die Demo zeigt, **dass die Wahl des Verfahrens meist etwas ändert** (bei acht Verbänden mit zufälligen Größen und 16 bis 64 Sitzen verteilen Hamilton und Jefferson in 91 % der Instanzen verschieden, Hamilton und Webster nur in 22 %), **was jedes Verfahren dafür opfert** und dass es **kein Verfahren ohne Opfer gibt**: Hamilton hält die Quotenregel, kann aber einem Verband Sitze nehmen, wenn das Haus wächst (in der Reihe mit 4 bis 12 Verbänden und Hausgrößen bis 150 in 6,8 % der Schritte „ein Sitz mehr“, je nach Verbandszahl 3,95 bis 8,88 %). Jefferson und die anderen Divisormethoden verlieren nie beim Wachsen und nie beim Bevölkerungsparadox, aber Jefferson verletzt die Quotenregel in **44,2 %** der Instanzen (acht Verbände mit zufälligen Größen, Hausgrößen 16 bis 80).
Dazu kommt die Antwort auf eine Frage, die Lehrbücher oft offenlassen: Die Verstöße von Huntington–Hill gegen die Quotenregel (11,2 %) treten fast nur auf, wenn ein Verband eine Quote unter 1 hat (131 von 135) – haben alle Verbände eine Quote von mindestens 1, sind es nur 4 von 420 Instanzen. Der **Mindestsitz** ist dabei ein wesentlicher Auslöser, die Teilung allein trennt ihn aber nicht von Hausgröße und Streuung der Größen.

## Modell

**Eingabe.** k Verbände mit Mitgliederzahlen p<sub>i</sub> (ganze Zahlen, erzeugt oder eingegeben, 2 bis 20 Verbände), h Sitze (5 bis 150). Die **Quote** ist q<sub>i</sub> = p<sub>i</sub> · h / Σ p; die **Quotenregel** verlangt ⌊q<sub>i</sub>⌋ ≤ s<sub>i</sub> ≤ ⌈q<sub>i</sub>⌉.
**Fünf Verfahren.** *Hamilton:* abgerundete Quote, die übrigen Sitze an die größten Reste. *Jefferson, Webster, Huntington–Hill:* die Sitze werden einzeln an den größten Rang vergeben, Mitglieder je (Sitze + 1), je (Sitze + ½) und je √(Sitze · (Sitze + 1)); bei Huntington–Hill hat jeder Verband zuerst einen Sitz (das Verfahren braucht h ≥ k und gibt sonst „nicht möglich“ zurück). Jedes dieser drei ist eine **Divisormethode**: es gibt (außer bei Gleichstand an der Sitzgrenze) einen Divisor d, sodass jeder Verband p<sub>i</sub>/d erhält, abgerundet (Jefferson), kaufmännisch gerundet (Webster) oder am geometrischen Mittel gerundet (Huntington–Hill). *Quotenmethode (eigene Ausführung des Verfahrens von Balinski und Young):* wie Jefferson, aber ein Verband bekommt den t-ten Sitz nur, wenn er danach höchstens ⌈p<sub>i</sub> · t / Σ p⌉ Sitze hat.
**Gleichstände** entscheidet die kleinere Verbandsnummer, bei Hamilton erst der größere Rest.
**Alabama-Paradox:** ein Verband hat bei h + 1 Sitzen weniger als bei h. Die Demo prüft jeden Schritt von h = k bis 150. **Bevölkerungsparadox:** ein Verband i wächst prozentual stärker als j, verliert aber einen Sitz, den j gewinnt (Mitgliederzahlen ein Jahr später, eingegeben oder erzeugt mit −4 % bis +8 % je Verband). Formeln im 📐-Expander der App.

## Methodik

- **Kern** (`sit_algorithm.py`): `hamilton`, `sequence` (alle Hausgrößen in einem Lauf), `apportion`, Quoten, Quotenverstöße, `loss_steps`/`alabama_steps`, `population_paradox`, `divisor_range` (Bereich der Divisoren als exakte Brüche).
- **Szenario und Auswertung** (`sit_scenario.py`, `sit_evaluation.py`): drei Erzeuger für Mitgliederzahlen (Zufall, ein großer Verband, ähnlich groß), Änderung nach einem Jahr, Texteingabe mit Prüfung, Tabellen, drei feste Reihen, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): sechs Schnellstart-Szenarien (alle von Hand nachgerechnet), Regler für Sitze und Zahl der Verbände, Auswahl der Größenverteilung, Zufalls-Seed, zwei Eingabefelder für eigene Mitgliederzahlen, Tabelle und zwei Abbildungen der Verteilung, Divisor-Tabelle, Verlauf über der Hausgröße, Bevölkerungsparadox, drei Reiter mit festen Reihen, Annahmen und Formeln.

## Befunde (gemessen, keine Behauptungen)

Die Verteilungen sind **exakt gerechnet**. Die drei Reihen zählen Anteile in je 300 Zufallsinstanzen (Mitgliederzahlen logarithmisch normalverteilt, wenige große und viele kleine Verbände) mit **festen Zufalls-Seeds**; die Tests prüfen die Zählungen exakt.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Hamilton gleich der Rechnung mit Brüchen und gleich der **Aufzählung aller Verteilungen** (kleinste Summe der Abweichungsquadrate); Jefferson, Webster, Huntington–Hill gleich der **globalen Rangliste aller Ansprüche**; der **Divisor-Bereich** aus der Rundungsregel reproduziert jede Verteilung (die obere Grenze gehört dazu, die untere nicht); Jefferson minimiert den größten Anspruch auf einen weiteren Sitz, Webster die gewichteten Abweichungsquadrate (Aufzählung); die Quotenmethode gleich ihrer Definition mit Brüchen. | `test_oracle_sitzverteilung.py`, `test_algorithm.py` |
| Wie oft verliert ein Verband, wenn das Haus wächst? | Nur **Hamilton**: in **14.481 von 213.000** Schritten „ein Sitz mehr“ (**6,80 %**). Je Zahl der Verbände (4, 6, 8, 10, 12): in 95, 99, 100, 100, 100 % der Instanzen mindestens einmal (285, 296, 299, 300, 300 von 300), in 3,95, 5,87, 7,37, 8,10, 8,88 % der Schritte. Jefferson, Webster, Huntington–Hill und die Quotenmethode: **nie** (Hausmonotonie, bei den Divisormethoden und der Quotenmethode durch den Bau, hier bestätigt). | `test_claims.py::test_alabama_*` |
| Wie oft wird die Quotenregel verletzt? | Über 1.200 Instanzen (acht Verbände, 16, 24, 48, 80 Sitze): **Jefferson 44,2 %** (530), Huntington–Hill 11,2 % (135), Webster 1,3 % (16), **Hamilton und Quotenmethode 0 %**. Jefferson verletzt nur nach oben (nie unter die abgerundete Quote). | `test_claims.py::test_quota_*`, `test_oracle_sitzverteilung.py::test_jefferson_never_falls_below_the_lower_quota_but_may_exceed_the_upper` |
| Kommen die Verstöße von Huntington–Hill vom Mindestsitz? | **Überwiegend ja.** Haben alle Verbände eine Quote von mindestens 1, sind es **4 von 420** Instanzen (1,0 %); sonst **131 von 780** (16,8 %). Die Teilung vermengt den Mindestsitz mit Hausgröße und Streuung der Größen; der Fall mit der Quote unter 1 zeigt aber den Mechanismus. Von Hand: 1.200, 300, 200, 100 Mitglieder, 6 Sitze: der große Verband hat die Quote 4, bekommt 3. | `test_claims.py::test_huntington_hill_violations_split_by_the_minimum_seat`, `test_algorithm.py::test_huntington_hill_minimum_seat_costs_the_big_association` |
| Bevölkerungsparadox? | Über 900 Instanzen (acht Verbände, 16, 32, 64 Sitze, Änderung −4 % bis +8 %): **Hamilton 17 (1,9 %)**, **Quotenmethode 11 (1,2 %)**, Jefferson, Webster, Huntington–Hill **nie**. Die Quotenmethode löst das Alabama-Paradox und hält die Quotenregel, zahlt aber mit dem Bevölkerungsparadox. | `test_claims.py::test_population_paradox_*` |
| Wie verschieden sind die Verfahren? | Anteil der Instanzen mit verschiedener Verteilung (900): Hamilton–Webster **22 %**, Jefferson–Quotenmethode 43 %, Webster–Huntington–Hill 48 %, Hamilton–Huntington–Hill 51 %, Webster–Quotenmethode 83 %, Hamilton–Quotenmethode 85 %, Jefferson–Webster 89 %, Hamilton–Jefferson **91 %**, Huntington–Hill–Quotenmethode 95 %, Jefferson–Huntington–Hill **96 %**. | `test_claims.py::test_full_disagreement_table`, `…::test_the_two_most_similar_pairs_are_hamilton_webster_and_jefferson_quota_method` |
| Standardinstanz | Acht Verbände (521, 840, 5.279, 1.933, 194, 995, 536, 1.160 Mitglieder), 40 Sitze: der größte Verband hat die Quote **18,43**, Jefferson gibt ihm **20** Sitze (erlaubt 18 bis 19) und dem kleinsten (Quote 0,68) keinen; Hamilton, Webster und Huntington–Hill stimmen überein; die Quotenmethode gibt dem größten 19. Hamilton verliert beim Schritt von 20 auf 21 Sitze bei V2 einen Sitz. | `test_algorithm.py::test_default_instance`, `test_claims.py::test_default_instance_has_alabama_loss_for_hamilton_only` |
| Schnellstart-Szenarien | Alle von Hand nachgerechnet: **Alabama-Paradox** (900, 600, 300, 100 Mitglieder: Hamilton gibt dem kleinsten bei 7 Sitzen einen, bei 8 keinen), **Jefferson verfehlt die Quote** (700, 400, 200, 100; 8 Sitze: Quote 4, Jefferson gibt 5), **Mindestsitz** (s. o.), **Bevölkerungsparadox** (330, 150, 100, 60 → 330, 170, 100, 70; 14 Sitze: der kleinste wächst um 16,7 %, der zweite um 13,3 %, Hamilton gibt dem zweiten einen Sitz mehr), **ein großer Verband** (Zufalls-Seed 1: alle fünf Verfahren verteilen verschieden). | `test_presets.py`, `test_algorithm.py` |
| Vormessung | Eine Vormessung vor dem Bau (anderer Zufallsstrom, 6 bis 13 Verbände) ergab dieselbe Rangfolge der Verfahren; **keine Zahl daraus** steht hier, alle Zahlen sind die der festen Reihen der Demo. | – |

## Ehrliche Grenzen

- **Die Hausgröße steht fest** und die **Mitgliederzahlen sind genau**; Zählfehler und Stichtage ändern die Verteilung. Bei mehreren Stichtagen kann Hamilton (und die Quotenmethode) einem wachsenden Verband einen Sitz nehmen.
- **Gleichstände** entscheidet die kleinere Verbandsnummer; Satzungen entscheiden meist per Los oder nach fester Regel. Gleichstände entstehen vor allem bei gleichen oder vielfachen Mitgliederzahlen; wie oft, hängt auch vom Verfahren ab. Gleiche Mitgliederzahlen sind in den Zufallsreihen selten.
- **Die Quotenmethode ist eine eigene Ausführung** des Verfahrens von Balinski und Young mit Jefferson als Rangfolge; andere Ausführungen können abweichen.
- **Huntington–Hill gibt jedem Verband einen Sitz** und rechnet nur für h ≥ k. Die anderen Verfahren lassen sehr kleine Verbände leer ausgehen; wer einen Mindestsitz verlangt, zahlt mit der Quotenregel (siehe Befunde).
- **Die Reihen sind Zählungen in Zufallsinstanzen** mit der Größenverteilung „Zufall“ und acht Verbänden (Reihe 1: 4 bis 12); bei anderen Verteilungen oder Hausgrößen können die Anteile abweichen. Das Alabama-Paradox wird nur für Hausgrößen ab der Zahl der Verbände gesucht (bis 150 Sitze).
- **Kein Verfahren kann alles.** Quotenregel und Bevölkerungsmonotonie lassen sich nach Balinski und Young nicht zugleich erfüllen (ab vier Verbänden; aus dem Gedächtnis); die Demo zeigt, welches Opfer jedes Verfahren bringt, ohne den Satz zu beweisen.
- **Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Balinski und Young, *Fair Representation* (1982); Pukelsheim, *Proportional Representation* (2014).

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9196.
- **Plan:** „Frage: Huntington–Hill-Verletzungen: Mindestsitz?“ – **beantwortet**: ja (4 von 420 gegen 131 von 780).
- **Neu gegenüber dem Plan:** die **Quotenmethode** als fünftes Verfahren (zeigt, dass Quotenregel und Hausmonotonie zugleich möglich sind und was dafür fehlt), der **Divisor-Bereich** als sichtbare Gleichwertigkeit der drei Divisormethoden mit „teilen und runden“, die Möglichkeit eigener Mitgliederzahlen und ein Verlaufsdiagramm über der Hausgröße.
- **Reglerspanne:** Sitze 5 bis 150, Verbände 3 bis 12 (eigene Eingabe 2 bis 20), Mitglieder je Verband 1 bis 10.000.000.

## Verifikation

- **Kern:** jede Einheit an Mini-Fällen von Hand (die Beispiele der Schnellstart-Szenarien, Gleichstände, Eingabeprüfung, Divisor-Bereiche von Hand, Folgen über die Hausgröße).
- **Orakel:** Fraction-Rechnung, Aufzählung aller Verteilungen, globale Rangliste, Divisor aus der Rundungsregel, Optimalität durch Aufzählung, Quotenmethode aus der Definition, Quotenregel, Hausmonotonie und Bevölkerungsparadox über Zufallsinstanzen.
- **Reihen und Texte:** jede Zahl dieser README in `tests/test_claims.py`; Verdikte, Tabellen und Eingabefehler als reine Funktionen (`tests/test_verdicts.py`), Randfälle und Adresszeile (`tests/test_edge_cases.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich, keines auf einem Rand von Sitzen und Verbänden, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern, Footer, Laufzeit-Importe).
- **Mutationsprüfung** (`tools/mutate_demo.py`): 117 Stellen im Kern `sit_algorithm.py`, **115 gefangen**, **2 als äquivalent festgehalten** (der Faktor 2 im Zähler des Webster-Rangs `2p / (2s + 1)`: jede gemeinsame Skalierung der Zähler ändert keinen Vergleich). Der erste Lauf ließ 7 überleben: **eine echte Lücke** (gleich starkes Wachstum zweier Verbände zählte nicht als Nicht-Paradox; neuer Test `test_equal_growth_is_not_a_population_paradox` mit Hamilton, 100/30/20/20 → 110/33/20/30 bei 15 Sitzen), **eine überflüssige Absicherung** in `population_paradox` (die Prüfung auf ein fehlendes Ergebnis beider Stichtage; sie wurde durch eine Prüfung gleicher Verbandszahl ersetzt) und drei Mutanten der Schleifengrenze der Huntington–Hill-Folge, die ein abschließendes Abschneiden `[:h_max]` verdeckte (die Folge wird jetzt ohne Abschneiden gebaut, `test_sequence_of_huntington_hill_has_exactly_h_max_entries`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `sit_algorithm.py` | Kern: fünf Verfahren, Quote, Verstöße, Alabama, Bevölkerungsparadox, Divisor-Bereich |
| `sit_constants.py` | Regler-Grenzen, feste Reihen, Farben, Presets |
| `sit_evaluation.py` | Analyse, Tabellen, Verdikte, drei feste Reihen |
| `sit_layout.py` | Fester Kopf (Stylesheet) |
| `sit_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `sit_scenario.py` | Mitgliederzahlen (drei Erzeuger), Änderung nach einem Jahr, Texteingabe |
| `sit_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Kern, Orakel, Reihen und Claims, Verdikte, Randfälle, Szenario, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Mehrere Ebenen** (erst Länder, dann Parteien; Überhang- und Ausgleichsmandate, Sperrklauseln): das ist die Sitzverteilung realer Wahlsysteme, hier geht es um das Rundungsproblem selbst.
- **Weitere Verfahren** (Droop-Quote, Adams, Dean, Imperiali): sie ändern das Bild nicht grundsätzlich; die fünf gezeigten decken die vier Bauarten ab (Rest, drei Rundungsregeln, Quotenbedingung).
- **Los bei Gleichstand** und **Mindestgrößen je Verband**: Satzungsfragen, die Demo nimmt die kleinere Verbandsnummer.
- **Beweise** der Unmöglichkeitssätze: die Demo zeigt nur Fälle und Zählungen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).

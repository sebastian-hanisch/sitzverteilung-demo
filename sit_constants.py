"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

METHODS = {
    "hamilton": "Hamilton (größter Rest)",
    "jefferson": "Jefferson (D'Hondt)",
    "webster": "Webster (Sainte-Laguë)",
    "hh": "Huntington–Hill",
    "quote": "Quotenmethode (Balinski–Young)",
}
METHOD_SHORT = {"hamilton": "Hamilton", "jefferson": "Jefferson", "webster": "Webster", "hh": "Huntington–Hill", "quote": "Quotenmethode"}
METHOD_TEXT = {
    "hamilton": "Jeder Verband bekommt die abgerundete Quote; die übrigen Sitze gehen an die größten Reste.",
    "jefferson": "Die Sitze werden einzeln vergeben, jeweils an den Verband mit der größten Zahl Mitglieder je (Sitze + 1).",
    "webster": "Wie Jefferson, aber mit Mitglieder je (Sitze + ½): rundet kaufmännisch.",
    "hh": "Jeder Verband bekommt zuerst einen Sitz; die übrigen gehen an die größte Zahl Mitglieder je √(Sitze · (Sitze + 1)) (geometrisches Mittel).",
    "quote": "Wie Jefferson, aber ein Verband darf einen weiteren Sitz nur bekommen, wenn er damit die aufgerundete Quote der neuen Hausgröße nicht überschreitet (eigene Ausführung des Verfahrens).",
}
METHOD_COLORS = {"hamilton": "#4c78a8", "jefferson": "#b04a3a", "webster": "#2F6B65", "hh": "#e8a838", "quote": "#7b6fa8"}
DIVISOR_METHODS = ("jefferson", "webster", "hh")

MODELS = {
    "zufall": "Zufall (unterschiedlich große Verbände)",
    "gross": "Ein großer Verband",
    "aehnlich": "Ähnlich große Verbände",
}
MODEL_SHORT = {"zufall": "Zufall", "gross": "Ein großer", "aehnlich": "Ähnlich groß"}
DEFAULT_MODEL = "zufall"

K_MIN, K_MAX, DEFAULT_K = 3, 12, 8                  # Verbände (bei „Zufall“ und den anderen Erzeugern)
H_MIN, H_MAX, DEFAULT_H = 5, 150, 40                # Hausgröße = zu vergebende Sitze
SEED_MAX, DEFAULT_SEED = 9999, 4
MEMBERS_MIN_COUNT, MEMBERS_MAX_COUNT = 2, 20        # eigene Eingabe: Zahl der Verbände
MEMBERS_MAX_VALUE = 10_000_000                      # eigene Eingabe: Mitglieder je Verband
SCAN_MAX = 150                                      # Hausgrößen bis hier werden auf Alabama-Paradoxe abgesucht

# Feste Reihen (Zufallsinstanzen mit festen Zufalls-Seeds; Anteile exakt gezählt, nicht gemessen)
SERIES_SEED = 100000
SERIES_RUNS = 300
SERIES_KS = (4, 6, 8, 10, 12)                       # Reihe 1: Zahl der Verbände
SERIES_RATIOS = (2, 3, 6, 10)                       # Reihe 2: Hausgröße = Verhältnis · Zahl der Verbände
SERIES_K_FOR_RATIOS = 8
SERIES_PARADOX_RATIOS = (2, 4, 8)                   # Reihe 3: Bevölkerungsparadox
POP_CHANGE = (-0.04, 0.08)                          # Änderung der Mitglieder je Verband, gleichverteilt (relativ)

COLOR_ALERT = "#c0392b"

PRESETS = {
    "Acht Verbände, 40 Sitze": {"k": 8, "h": 40, "model": "zufall", "seed": 4, "members": "", "members2": ""},
    "Alabama-Paradox": {"k": 4, "h": 7, "model": "zufall", "seed": 4, "members": "900, 600, 300, 100", "members2": ""},
    "Jefferson verfehlt die Quote": {"k": 4, "h": 8, "model": "zufall", "seed": 4, "members": "700, 400, 200, 100", "members2": ""},
    "Mindestsitz bei Huntington–Hill": {"k": 4, "h": 6, "model": "zufall", "seed": 4, "members": "1200, 300, 200, 100", "members2": ""},
    "Bevölkerungsparadox": {"k": 4, "h": 14, "model": "zufall", "seed": 4, "members": "330, 150, 100, 60", "members2": "330, 170, 100, 70"},
    "Ein großer Verband": {"k": 8, "h": 40, "model": "gross", "seed": 1, "members": "", "members2": ""},
}
PRESET_HELP = {
    "Acht Verbände, 40 Sitze": "Voreinstellung: acht Verbände mit unterschiedlicher Mitgliederzahl (Zufall, Zufalls-Seed 4), 40 Beiratssitze. Jefferson gibt dem größten Verband 20 Sitze bei einer Quote von 18,43.",
    "Alabama-Paradox": "Vier Verbände mit 900, 600, 300 und 100 Mitgliedern: Hamilton gibt dem kleinsten bei 7 Sitzen einen Sitz und bei 8 Sitzen keinen mehr. Das Haus wird größer, ein Verband verliert.",
    "Jefferson verfehlt die Quote": "Der größte Verband hat die Quote 4,0 und bekommt bei Jefferson 5 Sitze; der kleinste mit Quote 0,57 geht leer aus. Hamilton, Webster und Huntington–Hill geben dem größten genau 4.",
    "Mindestsitz bei Huntington–Hill": "Jeder Verband bekommt zuerst einen Sitz: bei 6 Sitzen bekommen die drei kleinen je einen, der große mit Quote 4,0 nur 3 und liegt unter seiner unteren Quote.",
    "Bevölkerungsparadox": "Der kleinste Verband wächst um 16,7 %, der zweite nur um 13,3 %; trotzdem gibt Hamilton bei 14 Sitzen dem zweiten einen Sitz mehr und dem kleinsten einen weniger.",
    "Ein großer Verband": "Ein Verband mit etwa 40 % der Mitglieder (Zufalls-Seed 1): hier verteilen alle fünf Verfahren verschieden.",
}

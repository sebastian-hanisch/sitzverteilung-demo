"""Szenario: Mitgliederzahlen der Verbände (erzeugt oder eingegeben) und die Änderung nach einem Jahr. Alles deterministisch aus (Modell, Zahl, Zufalls-Seed)."""

import re

import numpy as np

import sit_constants as C


def make_population(model: str, k: int, seed: int) -> list:
    """Mitgliederzahlen von k Verbänden als positive ganze Zahlen.

    Zufall: logarithmisch normalverteilt (Streuung 1, Mittel 1000), also wenige große und viele kleine Verbände. Ein großer Verband: der erste Verband hat 70 % der Summe der übrigen
    (etwa 41 % aller Mitglieder), die übrigen sind schwach gestreut (Streuung 0,4). Ähnlich groß: gleichverteilt zwischen 900 und 1100."""
    if model not in C.MODELS:
        raise ValueError(model)
    rng = np.random.default_rng(seed)
    if model == "zufall":
        raw = np.exp(rng.normal(0, 1.0, size=k)) * 1000
    elif model == "gross":
        rest = np.exp(rng.normal(0, 0.4, size=k - 1)) * 1000
        raw = np.concatenate([[0.7 * rest.sum()], rest])
    else:
        raw = rng.uniform(900, 1100, size=k)
    return [max(1, int(round(float(x)))) for x in raw]


def change_population(pop, seed: int) -> list:
    """Mitgliederzahlen nach einem Jahr: jeder Verband ändert sich unabhängig um einen Anteil, gleichverteilt zwischen POP_CHANGE[0] und POP_CHANGE[1]."""
    rng = np.random.default_rng(seed)
    lo, hi = C.POP_CHANGE
    return [max(1, int(round(p * (1 + float(rng.uniform(lo, hi)))))) for p in pop]


def parse_members(text: str):
    """Eingabe der Mitgliederzahlen: ganze Zahlen, getrennt durch Komma, Semikolon oder Leerzeichen. Rückgabe (Liste oder None, Fehlermeldung oder None); leerer Text: (None, None)."""
    text = (text or "").strip()
    if not text:
        return None, None
    parts = [t for t in re.split(r"[,;\s]+", text) if t]
    values = []
    for t in parts:
        if not re.fullmatch(r"\d+", t):
            return None, f"„{t}“ ist keine ganze Zahl (erlaubt: Ziffern, getrennt durch Komma, Semikolon oder Leerzeichen)."
        values.append(int(t))
    if not C.MEMBERS_MIN_COUNT <= len(values) <= C.MEMBERS_MAX_COUNT:
        return None, f"Es müssen {C.MEMBERS_MIN_COUNT} bis {C.MEMBERS_MAX_COUNT} Verbände sein (eingegeben: {len(values)})."
    if min(values) < 1 or max(values) > C.MEMBERS_MAX_VALUE:
        return None, f"Jede Mitgliederzahl muss zwischen 1 und {C.MEMBERS_MAX_VALUE:,}".replace(",", ".") + " liegen."
    return values, None

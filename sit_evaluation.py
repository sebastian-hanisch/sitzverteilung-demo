"""Auswertung: Einstellungen, Sitzverteilungen, Quotenverstöße, Alabama-Schritte, Bevölkerungsparadox, Tabellen, Verdikte als reine Funktionen (ohne Streamlit) und die festen Reihen."""

import math
from dataclasses import dataclass
from fractions import Fraction

import sit_algorithm as A
import sit_constants as C
import sit_scenario as S

METHODS = tuple(C.METHODS)


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x, digits: int = 1) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{100 * x:.{digits}f} %".replace(".", ",").replace("-", "−")      # echtes Minuszeichen


def thousands(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def names(methods) -> str:
    """Aufzählung der Kurznamen: „Hamilton“, „Hamilton und Jefferson“, „Hamilton, Jefferson und Webster“."""
    short = [C.METHOD_SHORT[m] for m in methods]
    if len(short) <= 1:
        return "".join(short)
    return ", ".join(short[:-1]) + " und " + short[-1]


@dataclass(frozen=True)
class Settings:
    k: int = C.DEFAULT_K
    h: int = C.DEFAULT_H
    model: str = C.DEFAULT_MODEL
    seed: int = C.DEFAULT_SEED
    members: str = ""
    members2: str = ""


@dataclass
class Analysis:
    settings: Settings
    pop: list            # Mitgliederzahlen der Verbände
    pop2: list           # Mitgliederzahlen nach einem Jahr
    source: str          # "eingegeben" oder "erzeugt"
    source2: str
    errors: list         # Hinweise zu ungültigen Eingaben (die Eingabe wird dann ignoriert)
    k: int
    h: int
    quotas: list         # exakte Quoten (Fraction)
    seats: dict          # Verfahren -> Sitzliste oder None (Huntington–Hill mit h < k)
    violations: dict     # Verfahren -> [(Verband, "unten"|"oben")]
    ranges: dict         # Divisormethode -> (unten, oben) oder None
    seqs: dict           # Verfahren -> Folge der Verteilungen für h = 1 … SCAN_MAX
    losses: dict         # Verfahren -> Alabama-Schritte von h = k bis SCAN_MAX
    paradox: dict        # Verfahren -> Paare (i, j), siehe A.population_paradox


def analyse(settings: Settings) -> Analysis:
    errors = []
    members, err = S.parse_members(settings.members)
    if err:
        errors.append("Eigene Mitgliederzahlen: " + err + " Die Eingabe wird ignoriert.")
    if members is not None:
        pop, source = members, "eingegeben"
    else:
        pop, source = S.make_population(settings.model, settings.k, settings.seed), "erzeugt"
    pop2, source2 = None, "erzeugt"
    members2, err2 = S.parse_members(settings.members2)
    if err2:
        errors.append("Mitgliederzahlen nach einem Jahr: " + err2 + " Die Eingabe wird ignoriert.")
    elif members2 is not None and len(members2) != len(pop):
        errors.append(f"Mitgliederzahlen nach einem Jahr: Es müssen {len(pop)} Zahlen sein, so viele wie Verbände (eingegeben: {len(members2)}). Die Eingabe wird ignoriert.")
    elif members2 is not None:
        pop2, source2 = members2, "eingegeben"
    if pop2 is None:
        pop2 = S.change_population(pop, settings.seed + 1)
    k, h = len(pop), settings.h
    seqs = {m: A.sequence(m, pop, C.SCAN_MAX) for m in METHODS}
    seats = {m: seqs[m][h - 1] for m in METHODS}
    return Analysis(
        settings=settings, pop=pop, pop2=pop2, source=source, source2=source2, errors=errors, k=k, h=h,
        quotas=A.quota(pop, h), seats=seats,
        violations={m: (A.quota_violations(pop, h, s) if s is not None else []) for m, s in seats.items()},
        ranges={m: A.divisor_range(m, pop, seats[m]) for m in C.DIVISOR_METHODS if seats[m] is not None},
        seqs=seqs, losses={m: A.loss_steps(seqs[m], k, C.SCAN_MAX) for m in METHODS},
        paradox={m: A.population_paradox(m, pop, pop2, h) for m in METHODS},
    )


def label(i: int) -> str:
    return f"V{i + 1}"


def deviation(a: Analysis, method: str, i: int, h: int):
    """Sitze minus Quote des Verbands i bei Hausgröße h (Fraction); None, wenn das Verfahren dort nichts liefert."""
    s = a.seqs[method][h - 1]
    return None if s is None else s[i] - Fraction(a.pop[i] * h, sum(a.pop))


def distinct_results(a: Analysis) -> list:
    """Gruppen von Verfahren mit gleicher Verteilung (nur Verfahren, die eine liefern), in der Reihenfolge ihres ersten Auftretens."""
    groups = []
    for m in METHODS:
        if a.seats[m] is None:
            continue
        for g in groups:
            if a.seats[g[0]] == a.seats[m]:
                g.append(m)
                break
        else:
            groups.append([m])
    return groups


# --- Tabellen --------------------------------------------------------------------------------------------------------------------------------

def seat_rows(a: Analysis) -> list:
    rows = []
    for i in range(a.k):
        row = {"Verband": label(i), "Mitglieder": thousands(a.pop[i]), "Quote": num(float(a.quotas[i]), 2)}
        for m in METHODS:
            s = a.seats[m]
            if s is None:
                row[C.METHOD_SHORT[m]] = "–"
                continue
            bad = dict(a.violations[m]).get(i)
            row[C.METHOD_SHORT[m]] = f"{s[i]}" + (" (über der Quote)" if bad == "oben" else " (unter der Quote)" if bad == "unten" else "")
        rows.append(row)
    return rows


def range_text(method: str, rng) -> str:
    if rng is None:
        return "kein Divisor trennt scharf (Gleichstand entschieden)"
    low, high = rng
    if method == "hh":
        low, high = math.sqrt(low), (math.sqrt(high) if high is not None else None)
    lo = num(float(low), 1)
    return f"{lo} < d" + ("" if high is None else f" ≤ {num(float(high), 1)}")


def divisor_rows(a: Analysis) -> list:
    return [{"Verfahren": C.METHOD_SHORT[m], "Rundungsregel für Mitglieder / d": {"jefferson": "abrunden", "webster": "kaufmännisch runden", "hh": "am geometrischen Mittel runden, mindestens 1"}[m],
             "Divisor d": range_text(m, a.ranges[m])} for m in C.DIVISOR_METHODS if m in a.ranges]


def loss_rows(a: Analysis) -> list:
    rows = []
    for m in METHODS:
        steps = a.losses[m]
        if steps:
            h, i, before, after = steps[0]
            first = f"bei {h} → {h + 1} Sitzen verliert {label(i)} einen Sitz ({before} → {after})"
        else:
            first = "–"
        rows.append({"Verfahren": C.METHOD_SHORT[m], f"Schritte mit Verlust (Hausgröße {a.k} bis {C.SCAN_MAX})": len(steps), "erster": first})
    return rows


def paradox_rows(a: Analysis) -> list:
    rows = []
    for m in METHODS:
        if a.seats[m] is None:
            rows.append({"Verfahren": C.METHOD_SHORT[m], "Befund": "–"})
            continue
        pairs = a.paradox[m]
        if pairs:
            i, j = pairs[0]
            rows.append({"Verfahren": C.METHOD_SHORT[m], "Befund": f"{label(i)} wächst stärker als {label(j)}, verliert aber einen Sitz an {label(j)} ({a.seats[m][i]} → {A.apportion(m, a.pop2, a.h)[i]} und {a.seats[m][j]} → {A.apportion(m, a.pop2, a.h)[j]})"})
        else:
            rows.append({"Verfahren": C.METHOD_SHORT[m], "Befund": "kein Paradox"})
    return rows


def paradox_growth(a: Analysis, i: int, j: int) -> str:
    return f"{label(i)}: {thousands(a.pop[i])} → {thousands(a.pop2[i])} ({pct(a.pop2[i] / a.pop[i] - 1)}), {label(j)}: {thousands(a.pop[j])} → {thousands(a.pop2[j])} ({pct(a.pop2[j] / a.pop[j] - 1)})"


# --- Verdikte --------------------------------------------------------------------------------------------------------------------------------

def verdict_state(a: Analysis):
    """Kernfrage: macht das Verfahren hier einen Unterschied, und was geht dabei schief? Rückgabe (st-Methode, Text)."""
    groups = distinct_results(a)
    avail = [m for m in METHODS if a.seats[m] is not None]
    bad_quota = [m for m in avail if a.violations[m]]
    bad_alabama = [m for m in avail if a.losses[m]]
    parts = []
    if len(groups) == 1:
        parts.append(f"Alle {len(avail)} rechnenden Verfahren geben dieselbe Verteilung: bei diesen Mitgliederzahlen und {a.h} Sitzen ist die Wahl des Verfahrens folgenlos.")
    else:
        parts.append(f"Die Verfahren geben {len(groups)} verschiedene Verteilungen: " + "; ".join(names(g) for g in groups) + ".")
    if a.seats["hh"] is None:
        parts.append(f"Huntington–Hill rechnet nicht, weil jeder der {a.k} Verbände zuerst einen Sitz bekommt und nur {a.h} Sitze da sind.")
    if bad_quota:
        first = bad_quota[0]
        i, _ = a.violations[first][0]
        lo, up = A.lower_upper(a.pop, a.h)
        parts.append(f"Gegen die Quotenregel verstoßen {names(bad_quota)}: zum Beispiel bekommt {label(i)} bei {C.METHOD_SHORT[first]} {a.seats[first][i]} Sitze bei einer Quote von {num(float(a.quotas[i]), 2)} (erlaubt {lo[i]} bis {up[i]}).")
    else:
        parts.append("Alle halten die Quotenregel (jeder Verband bekommt seine Quote auf- oder abgerundet).")
    if bad_alabama:
        parts.append(f"Beim Vergrößern des Hauses von {a.k} auf {C.SCAN_MAX} Sitze verliert bei {names(bad_alabama)} mindestens einmal ein Verband einen Sitz (Alabama-Paradox).")
    else:
        parts.append(f"Beim Vergrößern des Hauses von {a.k} auf {C.SCAN_MAX} Sitze verliert bei keinem Verfahren ein Verband einen Sitz.")
    bad_pop = [m for m in avail if a.paradox[m]]
    if bad_pop:
        parts.append(f"Bevölkerungsparadox bei der angenommenen Änderung nach einem Jahr: {names(bad_pop)}.")
    kind = "warning" if (bad_quota or bad_alabama or bad_pop) else "success"
    return kind, " ".join(parts)


def verdict_alabama(rows):
    """Reihe 1: wie oft verliert ein Verband beim Vergrößern des Hauses einen Sitz? Rückgabe (st-Methode, Text)."""
    tot_steps = sum(r["steps"] for r in rows)
    tot_loss = sum(r["loss"]["hamilton"] for r in rows)
    others = [m for m in METHODS if m != "hamilton" and sum(r["loss"][m] for r in rows) > 0]
    best = max(rows, key=lambda r: r["inst"]["hamilton"] / r["runs"])
    text = (f"Hamilton: in {thousands(tot_loss)} von {thousands(tot_steps)} Schritten „ein Sitz mehr im Haus“ ({pct(tot_loss / tot_steps, 2)}) verliert ein Verband einen Sitz; "
            f"in {pct(best['inst']['hamilton'] / best['runs'])} der Instanzen mit {best['k']} Verbänden kommt das mindestens einmal vor. ")
    text += "Alle übrigen Verfahren: nie, wie es ihre Bauweise erzwingt." if not others else f"Auch {names(others)} zeigen es."
    return ("warning" if tot_loss else "success"), text


def verdict_quota(rows):
    """Reihe 2: wie oft verletzt ein Verfahren die Quotenregel? Rückgabe (st-Methode, Text)."""
    tot = sum(r["runs"] for r in rows)
    share = {m: sum(r["viol"][m] for r in rows) / tot for m in METHODS}
    n_big = sum(r["n_big"] for r in rows)
    hh_big = sum(r["hh_viol_big"] for r in rows)
    text = (f"Quotenregel verletzt (über alle {thousands(tot)} Instanzen): Jefferson {pct(share['jefferson'])}, Huntington–Hill {pct(share['hh'])}, Webster {pct(share['webster'])}, "
            f"Hamilton {pct(share['hamilton'])}, Quotenmethode {pct(share['quote'])}. "
            f"Bei Huntington–Hill treten die Verstöße vor allem auf, wenn ein Verband eine Quote unter 1 hat: haben alle Verbände eine Quote von mindestens 1 ({thousands(n_big)} Instanzen), sind es {hh_big} Verstöße ({pct(hh_big / n_big if n_big else 0.0)}).")
    return "warning", text


def verdict_paradox(rows):
    """Reihe 3: Bevölkerungsparadox und Unterschiede zwischen den Verfahren. Rückgabe (st-Methode, Text)."""
    tot = sum(r["runs"] for r in rows)
    share = {m: sum(r["paradox"][m] for r in rows) / tot for m in METHODS}
    zero = [m for m in METHODS if share[m] == 0]
    text = (f"Bevölkerungsparadox (über alle {thousands(tot)} Instanzen): Hamilton {pct(share['hamilton'])}, Quotenmethode {pct(share['quote'])}"
            + (f"; {names(zero)}: nie." if zero else "."))
    return ("warning" if any(share.values()) else "success"), text


# --- Feste Reihen (Zufallsinstanzen mit festen Zufalls-Seeds; Anteile exakt gezählt) -----------------------------------------------------------

def series_alabama() -> list:
    """Je Zahl der Verbände: Anteil der Instanzen und der Schritte h → h + 1 (h = k … SCAN_MAX − 1) mit Sitzverlust, je Verfahren."""
    rows = []
    for k in C.SERIES_KS:
        inst = {m: 0 for m in METHODS}
        loss = {m: 0 for m in METHODS}
        for run in range(C.SERIES_RUNS):
            pop = S.make_population("zufall", k, C.SERIES_SEED + 1000 * k + run)
            for m in METHODS:
                steps = A.loss_steps(A.sequence(m, pop, C.SCAN_MAX), k, C.SCAN_MAX)
                inst[m] += bool(steps)
                loss[m] += len({h for h, *_ in steps})
        rows.append({"k": k, "runs": C.SERIES_RUNS, "steps": C.SERIES_RUNS * (C.SCAN_MAX - k), "inst": inst, "loss": loss})
    return rows


def series_quota() -> list:
    """Je Hausgröße (Verhältnis · k, k = SERIES_K_FOR_RATIOS): Instanzen mit Quotenverstoß je Verfahren; Huntington–Hill getrennt nach „alle Quoten ≥ 1“."""
    k = C.SERIES_K_FOR_RATIOS
    rows = []
    for ratio in C.SERIES_RATIOS:
        h = ratio * k
        viol = {m: 0 for m in METHODS}
        n_big = hh_big = 0
        for run in range(C.SERIES_RUNS):
            pop = S.make_population("zufall", k, C.SERIES_SEED + 50000 + 1000 * ratio + run)
            big = all(p * h >= sum(pop) for p in pop)
            for m in METHODS:
                bad = bool(A.quota_violations(pop, h, A.apportion(m, pop, h)))
                viol[m] += bad
                if m == "hh":
                    n_big += big
                    hh_big += bad and big
        rows.append({"ratio": ratio, "h": h, "k": k, "runs": C.SERIES_RUNS, "viol": viol, "n_big": n_big, "hh_viol_big": hh_big})
    return rows


def series_paradox() -> list:
    """Je Hausgröße: Instanzen mit Bevölkerungsparadox je Verfahren und Zahl der Instanzen, in denen zwei Verfahren verschieden verteilen."""
    k = C.SERIES_K_FOR_RATIOS
    rows = []
    for ratio in C.SERIES_PARADOX_RATIOS:
        h = ratio * k
        paradox = {m: 0 for m in METHODS}
        differ = {(m1, m2): 0 for i, m1 in enumerate(METHODS) for m2 in METHODS[i + 1:]}
        for run in range(C.SERIES_RUNS):
            seed = C.SERIES_SEED + 100000 + 1000 * ratio + run
            pop = S.make_population("zufall", k, seed)
            pop2 = S.change_population(pop, seed + 500000)
            res = {m: A.apportion(m, pop, h) for m in METHODS}
            for m in METHODS:
                paradox[m] += bool(A.population_paradox(m, pop, pop2, h))
            for (m1, m2) in differ:
                differ[(m1, m2)] += res[m1] != res[m2]
        rows.append({"ratio": ratio, "h": h, "k": k, "runs": C.SERIES_RUNS, "paradox": paradox, "differ": differ})
    return rows


def differ_matrix(rows) -> tuple:
    """Über alle Zeilen der dritten Reihe: ({(m1, m2): Anteil der Instanzen mit verschiedener Verteilung}, Zahl der Instanzen)."""
    tot = sum(r["runs"] for r in rows)
    return {pair: sum(r["differ"][pair] for r in rows) / tot for pair in rows[0]["differ"]}, tot


def alabama_table(rows) -> list:
    return [{"Verbände": r["k"], "Instanzen": r["runs"], **{C.METHOD_SHORT[m]: f"{pct(r['inst'][m] / r['runs'], 0)} der Instanzen, {pct(r['loss'][m] / r['steps'], 2)} der Schritte" for m in METHODS}} for r in rows]


def quota_table(rows) -> list:
    out = []
    for r in rows:
        row = {"Sitze": f"{r['h']} ({r['ratio']} je Verband)", "Instanzen": r["runs"], **{C.METHOD_SHORT[m]: pct(r["viol"][m] / r["runs"]) for m in METHODS}}
        row["Huntington–Hill, alle Quoten ≥ 1"] = f"{r['hh_viol_big']} von {r['n_big']}"
        out.append(row)
    return out


def paradox_table(rows) -> list:
    return [{"Sitze": f"{r['h']} ({r['ratio']} je Verband)", "Instanzen": r["runs"], **{C.METHOD_SHORT[m]: pct(r["paradox"][m] / r["runs"]) for m in METHODS}} for r in rows]


def differ_table(rows) -> list:
    share, _ = differ_matrix(rows)
    out = []
    for m1 in METHODS:
        row = {"Verfahren": C.METHOD_SHORT[m1]}
        for m2 in METHODS:
            if m1 == m2:
                row[C.METHOD_SHORT[m2]] = "–"
            else:
                row[C.METHOD_SHORT[m2]] = pct(share[(m1, m2)] if (m1, m2) in share else share[(m2, m1)], 0)
        out.append(row)
    return out

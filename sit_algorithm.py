"""Kern: Sitzverteilung auf Verbände nach Mitgliederzahlen. Alle Rechnungen sind GANZZAHLIG (Kreuzmultiplikation statt Brüche, Quadrate statt Wurzeln); es gibt keine Rundungsfehler.

Eingabe: Mitgliederzahlen `pop` (positive ganze Zahlen) und die Hausgröße h (Zahl der Sitze). Gleichstände entscheidet der kleinere Index (beim Verfahren von Hamilton: größerer Rest, dann kleinerer Index).
Die Quote eines Verbands ist pop_i · h / Σ pop; die untere Quote ihr abgerundeter, die obere Quote ihr aufgerundeter Wert.
"""

from fractions import Fraction

METHOD_NAMES = ("hamilton", "jefferson", "webster", "hh", "quote")


def check_input(pop, h: int) -> None:
    if not pop or any(int(p) != p or p < 1 for p in pop):
        raise ValueError("Mitgliederzahlen müssen positive ganze Zahlen sein")
    if h < 1 or int(h) != h:
        raise ValueError("Die Hausgröße muss eine positive ganze Zahl sein")


def quota(pop, h: int) -> list:
    """Quoten als exakte Brüche."""
    total = sum(pop)
    return [Fraction(p * h, total) for p in pop]


def lower_upper(pop, h: int) -> tuple:
    """Untere (abgerundete) und obere (aufgerundete) Quote je Verband."""
    total = sum(pop)
    return [p * h // total for p in pop], [-(-p * h // total) for p in pop]


def hamilton(pop, h: int) -> list:
    check_input(pop, h)
    total = sum(pop)
    seats = [p * h // total for p in pop]
    rest = [(p * h) % total for p in pop]
    for i in sorted(range(len(pop)), key=lambda i: (-rest[i], i))[: h - sum(seats)]:
        seats[i] += 1
    return seats


def _beats(a, b) -> bool:
    """Zähler/Nenner a gegen b: a größer als b (Kreuzmultiplikation)."""
    return a[0] * b[1] > b[0] * a[1]


def _priority(method: str, p: int, s: int) -> tuple:
    """Rang des nächsten Sitzes als Bruch (Zähler, Nenner): Jefferson p/(s+1), Webster p/(s+½) = 2p/(2s+1), Huntington–Hill p²/(s(s+1)) (der Rang ist das Quadrat von p/√(s(s+1)))."""
    if method == "jefferson":
        return p, s + 1
    if method == "webster":
        return 2 * p, 2 * s + 1
    if method == "hh":
        return p * p, s * (s + 1)
    raise ValueError(method)


def sequence(method: str, pop, h_max: int) -> list:
    """Die Sitzverteilung für jede Hausgröße 1 bis h_max (Liste der Längen h_max; Eintrag h − 1 ist die Verteilung bei Hausgröße h), Sitz für Sitz vergeben.

    Divisormethoden und die Quotenmethode vergeben den nächsten Sitz unabhängig von der Hausgröße (Quotenmethode: nur die Berechtigung hängt von ihr ab), die Folge liefert deshalb
    alle Hausgrößen in einem Lauf. Huntington–Hill beginnt mit einem Sitz je Verband (erst ab Hausgröße k definiert, davor None); Hamilton rechnet je Hausgröße neu."""
    check_input(pop, h_max)
    k = len(pop)
    out = []
    if method == "hamilton":
        return [hamilton(pop, h) for h in range(1, h_max + 1)]
    if method == "hh":
        if h_max < k:
            return [None] * h_max
        seats = [1] * k
        out = [None] * (k - 1) + [list(seats)]
        for _ in range(k + 1, h_max + 1):
            best = max_index(method, pop, seats)
            seats[best] += 1
            out.append(list(seats))
        return out
    seats = [0] * k
    total = sum(pop)
    for hp in range(1, h_max + 1):
        if method == "quote":
            eligible = [i for i in range(k) if seats[i] + 1 <= -(-pop[i] * hp // total)]
            best = max_index("jefferson", pop, seats, eligible)
        else:
            best = max_index(method, pop, seats)
        seats[best] += 1
        out.append(list(seats))
    return out


def max_index(method: str, pop, seats, candidates=None) -> int:
    """Verband mit dem größten Rang für den nächsten Sitz (Gleichstand: kleinerer Index)."""
    best = None
    for i in (range(len(pop)) if candidates is None else candidates):
        pr = _priority(method, pop[i], seats[i])
        if best is None or _beats(pr, best[1]):
            best = (i, pr)
    return best[0]


def apportion(method: str, pop, h: int):
    """Sitzverteilung bei Hausgröße h; None, wenn das Verfahren sie nicht kennt (Huntington–Hill mit weniger Sitzen als Verbänden)."""
    check_input(pop, h)
    if method not in METHOD_NAMES:
        raise ValueError(method)
    if method == "hamilton":
        return hamilton(pop, h)
    return sequence(method, pop, h)[h - 1]


def quota_violations(pop, h: int, seats) -> list:
    """Verstöße gegen die Quote: Liste (Verband, 'unten' oder 'oben') für Verbände unter der unteren oder über der oberen Quote."""
    lo, up = lower_upper(pop, h)
    out = []
    for i, s in enumerate(seats):
        if s < lo[i]:
            out.append((i, "unten"))
        elif s > up[i]:
            out.append((i, "oben"))
    return out


def loss_steps(seq, h_from: int, h_to: int) -> list:
    """Alle Schritte h → h + 1 (h von h_from bis h_to − 1) einer Folge aus `sequence`, in denen ein Verband Sitze verliert: Liste (h, Verband, Sitze bei h, Sitze bei h + 1)."""
    found = []
    for h in range(h_from, h_to):
        a, b = seq[h - 1], seq[h]
        if a is None or b is None:
            continue
        for i in range(len(a)):
            if b[i] < a[i]:
                found.append((h, i, a[i], b[i]))
    return found


def alabama_steps(method: str, pop, h_from: int, h_to: int) -> list:
    """Alle Schritte h → h + 1 (h von h_from bis h_to − 1), in denen ein Verband Sitze verliert (Alabama-Paradox, Verlust bei wachsendem Haus): Liste (h, Verband, Sitze bei h, Sitze bei h + 1)."""
    return loss_steps(sequence(method, pop, h_to), h_from, h_to)


def population_paradox(method: str, pop1, pop2, h: int) -> list:
    """Paare (i, j), bei denen Verband i relativ stärker gewachsen ist als j (pop2_i / pop1_i > pop2_j / pop1_j, echt größer), aber einen Sitz verliert, den j gewinnt."""
    if len(pop1) != len(pop2):
        raise ValueError("Beide Stichtage brauchen gleich viele Verbände")
    s1, s2 = apportion(method, pop1, h), apportion(method, pop2, h)
    if s1 is None:                                  # Huntington–Hill mit h < k; für pop2 gilt dasselbe, die Zahl der Verbände ist gleich
        return []
    out = []
    for i in range(len(pop1)):
        for j in range(len(pop1)):
            if i != j and pop2[i] * pop1[j] > pop2[j] * pop1[i] and s2[i] < s1[i] and s2[j] > s1[j]:
                out.append((i, j))
    return out


def divisor_range(method: str, pop, seats):
    """Divisor-Äquivalenz: der Bereich (unten, oben] der Divisoren d, bei denen Mitglieder/d nach der Rundungsregel des Verfahrens genau die Sitze ergibt; None, wenn es keinen gibt.

    Jefferson rundet ab (Sitze = ⌊p/d⌋), Webster kaufmännisch, Huntington–Hill am geometrischen Mittel √(s(s+1)) (jeder Verband hat mindestens einen Sitz). Rückgabe für Jefferson und Webster
    (Fraction, Fraction); für Huntington–Hill die Quadrate (Fraction, Fraction) des Divisors, weil die Schwellen Wurzeln enthalten. Die obere Grenze gehört dazu, die untere nicht."""
    lows, highs = [], []
    for p, s in zip(pop, seats):
        if method == "jefferson":
            lows.append(Fraction(p, s + 1))
            if s > 0:
                highs.append(Fraction(p, s))
        elif method == "webster":
            lows.append(Fraction(2 * p, 2 * s + 1))
            if s > 0:
                highs.append(Fraction(2 * p, 2 * s - 1))
        elif method == "hh":
            if s < 1:
                return None
            lows.append(Fraction(p * p, s * (s + 1)))
            if s > 1:
                highs.append(Fraction(p * p, (s - 1) * s))
        else:
            raise ValueError(method)
    low, high = max(lows), (min(highs) if highs else None)
    if high is not None and not low < high:
        return None
    return low, high

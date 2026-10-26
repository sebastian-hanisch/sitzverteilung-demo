"""Orakel (DEMO-PLAYBOOK §12): unabhängige Gegenrechnungen mit exakten Brüchen, anders gebaut als der Kern.

- Hamilton: Bruch-Quoten, Sortierung der Reste; außerdem die Aufzählung aller Verteilungen (kleinste Summe der Abweichungsquadrate).
- Jefferson, Webster, Huntington–Hill: „die h größten Ränge“ aus der Liste ALLER Ränge (globale Sortierung statt Sitz für Sitz); außerdem der Divisor aus der Rundungsregel
  und die Optimalitätseigenschaft (Jefferson: kleinster größter Anspruch auf einen weiteren Sitz; Webster: kleinste gewichtete Abweichungsquadrate) durch Aufzählung.
- Quotenmethode: Neuschreibung der Definition mit Brüchen und ceil.
- Eigenschaften über zufällige Instanzen: Quotenregel, Hausmonotonie, Bevölkerungsparadox, Alabama-Paradox."""

import itertools
import math
import random
from fractions import Fraction

import pytest

import sit_algorithm as A
import sit_scenario as S

ROUNDS = 300


def random_instances(seed, n, kmax=8, hmax=60, small=False):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        k = rng.randint(2, kmax)
        top = 12 if small else 5000
        pop = [rng.randint(1, top) for _ in range(k)]
        out.append((pop, rng.randint(1, hmax)))
    return out


def tie_free(method, pop, h):
    """Das Ergebnis ändert sich nicht, wenn die Verbände in umgekehrter Reihenfolge stehen: keine Gleichstandsentscheidung war nötig."""
    a = A.apportion(method, pop, h)
    b = A.apportion(method, pop[::-1], h)
    return (a is None and b is None) or a == b[::-1]


# --- Hamilton -------------------------------------------------------------------------------------------------------------------------------

def hamilton_oracle(pop, h):
    total = sum(pop)
    q = [Fraction(p * h, total) for p in pop]
    seats = [math.floor(x) for x in q]
    order = sorted(range(len(pop)), key=lambda i: (-(q[i] - seats[i]), i))
    for i in order[: h - sum(seats)]:
        seats[i] += 1
    return seats


@pytest.mark.parametrize("small", [False, True])
def test_hamilton_matches_the_fraction_oracle(small):
    for pop, h in random_instances(1, ROUNDS, small=small):
        assert A.hamilton(pop, h) == hamilton_oracle(pop, h), (pop, h)


def compositions(h, k):
    if k == 1:
        yield (h,)
        return
    for first in range(h + 1):
        for rest in compositions(h - first, k - 1):
            yield (first,) + rest


def test_hamilton_minimises_the_squared_deviations_among_all_distributions():
    rng = random.Random(2)
    checked = 0
    for _ in range(120):
        k, h = rng.randint(2, 4), rng.randint(2, 9)
        pop = [rng.randint(1, 40) for _ in range(k)]
        q = [Fraction(p * h, sum(pop)) for p in pop]
        cost = {c: sum((c[i] - q[i]) ** 2 for i in range(k)) for c in compositions(h, k)}
        best = min(cost.values())
        winners = [c for c, v in cost.items() if v == best]
        if len(winners) != 1:
            continue                                                         # Gleichstand zwischen Verteilungen: das Ergebnis ist Auslegung
        assert tuple(A.hamilton(pop, h)) == winners[0], (pop, h)
        checked += 1
    assert checked >= 60


# --- Divisormethoden: globale Rangliste ------------------------------------------------------------------------------------------------------

def rank_value(method, p, j):
    """Rang des j-ten Sitzes (j ≥ 1) eines Verbands als exakter Bruch; bei Huntington–Hill das QUADRAT des Rangs (gleiche Ordnung)."""
    if method == "jefferson":
        return Fraction(p, j)
    if method == "webster":
        return Fraction(2 * p, 2 * j - 1)
    return Fraction(p * p, (j - 1) * j)                                      # Huntington–Hill: Sitz j ≥ 2


def top_h_oracle(method, pop, h):
    k = len(pop)
    if method == "hh":
        if h < k:
            return None
        seats = [1] * k
        entries = [(rank_value("hh", p, j), i) for i, p in enumerate(pop) for j in range(2, h + 1)]
        want = h - k
    else:
        seats = [0] * k
        entries = [(rank_value(method, p, j), i) for i, p in enumerate(pop) for j in range(1, h + 1)]
        want = h
    entries.sort(key=lambda e: (-e[0], e[1]))
    for _, i in entries[:want]:
        seats[i] += 1
    return seats


@pytest.mark.parametrize("method", ["jefferson", "webster", "hh"])
@pytest.mark.parametrize("small", [False, True])
def test_divisor_methods_match_the_global_ranking(method, small):
    for pop, h in random_instances(3, ROUNDS, small=small):
        assert A.apportion(method, pop, h) == top_h_oracle(method, pop, h), (method, pop, h)


# --- Divisor aus der Rundungsregel -----------------------------------------------------------------------------------------------------------

def rounded(method, p, d):
    """Sitze nach der Rundungsregel für den Divisor d (bei Huntington–Hill ist d das QUADRAT des Divisors, damit alles rational bleibt)."""
    if method == "jefferson":
        return math.floor(Fraction(p) / d)
    if method == "webster":
        return math.floor(Fraction(p) / d + Fraction(1, 2))
    x2 = Fraction(p * p) / d
    s = 1
    while x2 >= s * (s + 1):
        s += 1
    return s


@pytest.mark.parametrize("method", ["jefferson", "webster", "hh"])
def test_divisor_range_reproduces_the_distribution_by_rounding(method):
    checked = 0
    for pop, h in random_instances(4, ROUNDS):
        seats = A.apportion(method, pop, h)
        if seats is None or not tie_free(method, pop, h):
            continue
        low, high = A.divisor_range(method, pop, seats)
        assert low < high if high is not None else True
        d_mid = (low + (high if high is not None else low + 1)) / 2
        assert [rounded(method, p, d_mid) for p in pop] == seats, (pop, h)
        if high is not None:
            assert [rounded(method, p, high) for p in pop] == seats                  # die obere Grenze gehört dazu
        assert [rounded(method, p, low) for p in pop] != seats                       # die untere nicht: bei ihr rundet ein Verband auf
        checked += 1
    assert checked > 150


# --- Optimalität durch Aufzählung ------------------------------------------------------------------------------------------------------------

def test_jefferson_minimises_the_largest_remaining_claim():
    rng = random.Random(5)
    checked = 0
    for _ in range(120):
        k, h = rng.randint(2, 4), rng.randint(2, 9)
        pop = [rng.randint(1, 40) for _ in range(k)]
        if not tie_free("jefferson", pop, h):
            continue

        def worst(c):                                                        # der größte Anspruch auf einen weiteren Sitz: Mitglieder je (Sitze + 1)
            return max(Fraction(p, s + 1) for p, s in zip(pop, c))

        best = min(worst(c) for c in compositions(h, k))
        assert worst(A.apportion("jefferson", pop, h)) == best, (pop, h)
        checked += 1
    assert checked >= 40


def test_webster_minimises_the_weighted_squared_deviations():
    rng = random.Random(6)
    checked = 0
    for _ in range(120):
        k, h = rng.randint(2, 4), rng.randint(2, 9)
        pop = [rng.randint(1, 40) for _ in range(k)]
        if not tie_free("webster", pop, h):
            continue
        lam = Fraction(h, sum(pop))

        def cost(c):
            return sum(Fraction((s - lam * p) ** 2) / p for p, s in zip(pop, c))

        best = min(cost(c) for c in compositions(h, k))
        assert cost(A.apportion("webster", pop, h)) == best, (pop, h)
        checked += 1
    assert checked >= 40


# --- Quotenmethode ---------------------------------------------------------------------------------------------------------------------------

def quota_oracle(pop, h):
    """Definition: Sitz t von 1 bis h an den größten Rang p/(s+1) unter den Verbänden, die mit dem Sitz die aufgerundete Quote für t nicht überschreiten."""
    total = sum(pop)
    seats = [0] * len(pop)
    for t in range(1, h + 1):
        allowed = [i for i in range(len(pop)) if seats[i] + 1 <= math.ceil(Fraction(pop[i] * t, total))]
        best = max(allowed, key=lambda i: (Fraction(pop[i], seats[i] + 1), -i))
        seats[best] += 1
    return seats


@pytest.mark.parametrize("small", [False, True])
def test_quota_method_matches_the_definition(small):
    for pop, h in random_instances(7, ROUNDS, small=small):
        assert A.apportion("quote", pop, h) == quota_oracle(pop, h), (pop, h)


def test_quota_method_always_finds_an_allowed_association():
    for pop, h in random_instances(8, ROUNDS, small=True):
        assert sum(A.apportion("quote", pop, h)) == h


# --- Eigenschaften über zufällige Instanzen --------------------------------------------------------------------------------------------------

def quota_ok(pop, h, seats):
    return all(math.floor(Fraction(p * h, sum(pop))) <= s <= math.ceil(Fraction(p * h, sum(pop))) for p, s in zip(pop, seats))


@pytest.mark.parametrize("method", ["hamilton", "quote"])
def test_hamilton_and_the_quota_method_obey_the_quota_rule(method):
    for pop, h in random_instances(9, ROUNDS, small=True) + random_instances(10, ROUNDS):
        assert quota_ok(pop, h, A.apportion(method, pop, h)), (pop, h)


def test_jefferson_never_falls_below_the_lower_quota_but_may_exceed_the_upper():
    over = 0
    for pop, h in random_instances(11, ROUNDS):
        s = A.apportion("jefferson", pop, h)
        lo, up = A.lower_upper(pop, h)
        assert all(x >= low for x, low in zip(s, lo)), (pop, h)
        over += any(x > u for x, u in zip(s, up))
    assert over > 0


def test_huntington_hill_violates_the_quota_mostly_through_the_minimum_seat():
    big = [0, 0]                                                                    # [Instanzen, Verstöße], alle Quoten ≥ 1
    small = [0, 0]                                                                  # mindestens eine Quote < 1: der Mindestsitz greift
    rng = random.Random(12)
    for seed in range(1500):
        k = rng.randint(4, 10)
        pop, h = S.make_population("zufall", k, seed), rng.randint(2, 8) * k                       # wenige große, viele kleine Verbände wie in der Demo
        s = A.apportion("hh", pop, h)
        target = big if all(p * h >= sum(pop) for p in pop) else small
        target[0] += 1
        target[1] += not quota_ok(pop, h, s)
    assert big[0] > 100 and small[0] > 100
    assert big[1] / big[0] < 0.03 and small[1] / small[0] > 0.08
    # Von Hand: der Mindestsitz eines Verbands mit Quote 1/3 kostet den großen Verband einen Sitz unter seiner Quote
    assert A.quota_violations([1200, 300, 200, 100], 6, A.apportion("hh", [1200, 300, 200, 100], 6)) == [(0, "unten")]


@pytest.mark.parametrize("method", ["jefferson", "webster", "hh", "quote"])
def test_house_monotone_methods_never_lose_a_seat_when_the_house_grows(method):
    for pop, _ in random_instances(13, 60):
        assert A.alabama_steps(method, pop, len(pop), 80) == [], (method, pop)


def test_hamilton_can_lose_a_seat_when_the_house_grows():
    found = sum(bool(A.alabama_steps("hamilton", pop, len(pop), 60)) for pop, _ in random_instances(14, 60))
    assert found >= 20


def paradox_oracle(method, pop1, pop2, h):
    s1, s2 = A.apportion(method, pop1, h), A.apportion(method, pop2, h)
    pairs = []
    for i, j in itertools.permutations(range(len(pop1)), 2):
        grows_more = Fraction(pop2[i], pop1[i]) > Fraction(pop2[j], pop1[j])
        if grows_more and s2[i] < s1[i] and s2[j] > s1[j]:
            pairs.append((i, j))
    return pairs


@pytest.mark.parametrize("method", A.METHOD_NAMES)
def test_population_paradox_matches_the_definition(method):
    rng = random.Random(15)
    for pop, h in random_instances(16, 120, kmax=6, hmax=40):
        if method == "hh" and h < len(pop):
            continue
        pop2 = [max(1, round(p * (1 + rng.uniform(-0.04, 0.08)))) for p in pop]
        assert A.population_paradox(method, pop, pop2, h) == paradox_oracle(method, pop, pop2, h)


@pytest.mark.parametrize("method", ["jefferson", "webster", "hh"])
def test_divisor_methods_have_no_population_paradox(method):
    rng = random.Random(17)
    for pop, h in random_instances(18, ROUNDS, kmax=8, hmax=60):
        if method == "hh" and h < len(pop):
            continue
        pop2 = [max(1, round(p * (1 + rng.uniform(-0.04, 0.08)))) for p in pop]
        assert A.population_paradox(method, pop, pop2, h) == [], (pop, pop2, h)


def test_hamilton_and_the_quota_method_do_show_a_population_paradox_somewhere():
    rng = random.Random(19)
    seen = {"hamilton": 0, "quote": 0}
    for pop, h in random_instances(20, 600, kmax=8, hmax=60):
        pop2 = [max(1, round(p * (1 + rng.uniform(-0.04, 0.08)))) for p in pop]
        for m in seen:
            seen[m] += bool(A.population_paradox(m, pop, pop2, h))
    assert seen["hamilton"] > 0 and seen["quote"] > 0


def test_quota_method_is_not_population_monotone_but_is_house_monotone_in_the_balinski_young_sense():
    # Hausmonotonie und Quotenregel zugleich: genau das, was Hamilton nicht kann; die Quotenmethode zahlt mit dem Bevölkerungsparadox (Beweis durch Beispiel in der Stichprobe oben)
    for pop, _ in random_instances(21, 40, kmax=6):
        prev = A.apportion("quote", pop, 1)
        for h in range(2, 70):
            cur = A.apportion("quote", pop, h)
            assert all(c >= p for c, p in zip(cur, prev)) and quota_ok(pop, h, cur)
            prev = cur

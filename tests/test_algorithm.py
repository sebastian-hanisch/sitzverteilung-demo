"""Kern von Hand gerechnet: kleine Beispiele mit bekanntem Ergebnis, Eingabeprüfung, Gleichstände, Folgen über die Hausgröße."""

from fractions import Fraction

import pytest

import sit_algorithm as A

# --- Beispiele der Presets, von Hand nachgerechnet ------------------------------------------------------------------------------------------------

ALABAMA = [900, 600, 300, 100]       # Summe 1900
JEFFERSON = [700, 400, 200, 100]     # Summe 1400, 8 Sitze: Quoten 4, 16/7, 8/7, 4/7
MINDESTSITZ = [1200, 300, 200, 100]  # Summe 1800, 6 Sitze: Quoten 4, 1, 2/3, 1/3
PARADOX1, PARADOX2 = [330, 150, 100, 60], [330, 170, 100, 70]
DEFAULT_POP = [521, 840, 5279, 1933, 194, 995, 536, 1160]


def test_hamilton_alabama_example():
    # 7 Sitze: Quoten 63/19, 42/19, 21/19, 7/19 -> abgerundet 3, 2, 1, 0; Reste 6/19, 4/19, 2/19, 7/19; der eine fehlende Sitz geht an den größten Rest (V4)
    assert A.hamilton(ALABAMA, 7) == [3, 2, 1, 1]
    # 8 Sitze: Quoten 72/19, 48/19, 24/19, 8/19 -> 3, 2, 1, 0; Reste 15, 10, 5, 8 (je /19); zwei fehlende Sitze gehen an V1 und V2, V4 verliert seinen Sitz
    assert A.hamilton(ALABAMA, 8) == [4, 3, 1, 0]
    assert A.alabama_steps("hamilton", ALABAMA, 7, 8) == [(7, 3, 1, 0)]


def test_alabama_example_other_methods_do_not_lose():
    for m in ("jefferson", "webster", "hh", "quote"):
        assert A.alabama_steps(m, ALABAMA, 4, 150) == [], m


def test_jefferson_breaks_the_quota_rule_in_the_preset():
    pop = JEFFERSON
    assert A.quota(pop, 8) == [4, Fraction(16, 7), Fraction(8, 7), Fraction(4, 7)]
    assert A.apportion("jefferson", pop, 8) == [5, 2, 1, 0]
    assert A.quota_violations(pop, 8, [5, 2, 1, 0]) == [(0, "oben")]
    assert A.apportion("hamilton", pop, 8) == [4, 2, 1, 1]
    assert A.apportion("webster", pop, 8) == [4, 2, 1, 1]
    assert A.apportion("hh", pop, 8) == [4, 2, 1, 1]
    assert A.apportion("quote", pop, 8) == [4, 3, 1, 0]


def test_huntington_hill_minimum_seat_costs_the_big_association():
    pop = MINDESTSITZ
    assert A.apportion("hh", pop, 6) == [3, 1, 1, 1]
    assert A.quota_violations(pop, 6, [3, 1, 1, 1]) == [(0, "unten")]      # Quote 4: abgerundet 4, bekommen 3
    assert A.apportion("hamilton", pop, 6) == [4, 1, 1, 0]
    assert A.apportion("jefferson", pop, 6) == [5, 1, 0, 0]


def test_population_paradox_example():
    assert A.apportion("hamilton", PARADOX1, 14) == [7, 3, 2, 2]
    assert A.apportion("hamilton", PARADOX2, 14) == [7, 4, 2, 1]
    # V4 wächst von 60 auf 70 (+16,7 %), V2 von 150 auf 170 (+13,3 %); V4 verliert einen Sitz an V2
    assert A.population_paradox("hamilton", PARADOX1, PARADOX2, 14) == [(3, 1)]
    for m in ("jefferson", "webster", "hh", "quote"):
        assert A.population_paradox(m, PARADOX1, PARADOX2, 14) == [], m


def test_equal_growth_is_not_a_population_paradox():
    # V1 und V2 wachsen beide um genau 10 %; Hamilton nimmt V1 einen Sitz und gibt ihn V2: eine Umverteilung, aber kein Paradox (V2 wächst nicht schwächer, V1 nicht stärker)
    pop1, pop2 = [100, 30, 20, 20], [110, 33, 20, 30]
    assert A.apportion("hamilton", pop1, 15) == [9, 2, 2, 2] and A.apportion("hamilton", pop2, 15) == [8, 3, 2, 2]
    assert A.population_paradox("hamilton", pop1, pop2, 15) == []


def test_population_paradox_needs_the_same_number_of_associations():
    with pytest.raises(ValueError):
        A.population_paradox("hamilton", [5, 4, 3], [5, 4], 6)


def test_population_paradox_is_empty_for_huntington_hill_with_too_few_seats():
    assert A.population_paradox("hh", [5, 4, 3], [5, 6, 3], 2) == []


def test_default_instance():
    assert A.apportion("hamilton", DEFAULT_POP, 40) == [2, 3, 18, 7, 1, 3, 2, 4]
    assert A.apportion("jefferson", DEFAULT_POP, 40) == [1, 3, 20, 7, 0, 3, 2, 4]
    assert A.apportion("webster", DEFAULT_POP, 40) == A.apportion("hamilton", DEFAULT_POP, 40)
    assert A.apportion("hh", DEFAULT_POP, 40) == A.apportion("hamilton", DEFAULT_POP, 40)
    assert A.apportion("quote", DEFAULT_POP, 40) == [2, 3, 19, 7, 0, 3, 2, 4]
    lo, up = A.lower_upper(DEFAULT_POP, 40)
    assert (lo[2], up[2]) == (18, 19)                                          # Quote 18,43
    assert A.quota_violations(DEFAULT_POP, 40, A.apportion("jefferson", DEFAULT_POP, 40)) == [(2, "oben")]


# --- Allgemeine Eigenschaften -----------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("method", A.METHOD_NAMES)
def test_seats_sum_to_h_and_scale_invariance(method):
    for h in (8, 17, 40, 150):
        s = A.apportion(method, DEFAULT_POP, h)
        assert sum(s) == h and all(x >= 0 for x in s)
        assert A.apportion(method, [p * 1000 for p in DEFAULT_POP], h) == s       # nur die Verhältnisse zählen


@pytest.mark.parametrize("method", A.METHOD_NAMES)
def test_single_association_gets_everything(method):
    assert A.apportion(method, [7], 12) == [12]


@pytest.mark.parametrize("method", A.METHOD_NAMES)
def test_equal_associations_ties_go_to_the_lowest_index(method):
    assert A.apportion(method, [10, 10, 10], 4) == [2, 1, 1]
    assert A.apportion(method, [10, 10, 10], 3) == [1, 1, 1]
    assert A.apportion(method, [10, 10, 10], 5) == [2, 2, 1]


def test_hamilton_tie_in_the_remainders_goes_to_the_lower_index():
    assert A.hamilton([1, 1], 3) == [2, 1]
    # Quoten 1/3, 2/3, 3: abgerundet 0, 0, 3; der eine freie Sitz geht an den größeren Rest (V2), nicht an den kleineren Index
    assert A.hamilton([1, 2, 9], 4) == [0, 1, 3]


def test_sequence_of_huntington_hill_has_exactly_h_max_entries():
    for h_max in (1, 2, 3, 4, 7):
        seq = A.sequence("hh", [5, 3, 2], h_max)
        assert len(seq) == h_max and seq[: min(2, h_max)] == [None] * min(2, h_max)
    assert A.sequence("hh", [5, 3, 2], 4)[3] == [2, 1, 1] and A.sequence("hh", [5, 3, 2], 3) == [None, None, [1, 1, 1]]


def test_huntington_hill_needs_at_least_one_seat_each():
    assert A.apportion("hh", [5, 3, 2], 2) is None
    assert A.apportion("hh", [5, 3, 2], 3) == [1, 1, 1]
    assert A.apportion("hh", [5, 3, 2], 4) == [2, 1, 1]
    seq = A.sequence("hh", [5, 3, 2], 6)
    assert seq[:2] == [None, None] and seq[2] == [1, 1, 1]
    assert A.alabama_steps("hh", [5, 3, 2], 1, 6) == []                          # Schritte vor h = k zählen nicht


def test_jefferson_may_leave_small_associations_empty_but_hh_never():
    assert A.apportion("jefferson", [1000, 1000, 1], 10) == [5, 5, 0]
    assert A.apportion("webster", [1000, 1000, 1], 10) == [5, 5, 0]
    assert A.apportion("hh", [1000, 1000, 1], 10) == [5, 4, 1]


def test_sequence_matches_apportion_for_every_house_size():
    pop = [310, 220, 140, 90, 40]
    for m in A.METHOD_NAMES:
        seq = A.sequence(m, pop, 30)
        assert len(seq) == 30
        for h in range(1, 31):
            if seq[h - 1] is None:
                assert m == "hh" and h < len(pop)
            else:
                assert seq[h - 1] == A.apportion(m, pop, h) and sum(seq[h - 1]) == h


def test_quota_are_exact_fractions_that_sum_to_h():
    q = A.quota([521, 840, 5279], 40)
    assert all(isinstance(x, Fraction) for x in q) and sum(q) == 40
    assert q[0] == Fraction(521 * 40, 521 + 840 + 5279)


def test_lower_upper_for_integer_and_fractional_quotas():
    lo, up = A.lower_upper([3, 1], 8)               # Quoten 6 und 2 (ganzzahlig)
    assert (lo, up) == ([6, 2], [6, 2])
    lo, up = A.lower_upper([2, 1], 4)               # Quoten 8/3 und 4/3
    assert (lo, up) == ([2, 1], [3, 2])


def test_quota_violations_detects_both_directions():
    pop = [3, 1]                                    # Quoten 6 und 2 bei h = 8
    assert A.quota_violations(pop, 8, [6, 2]) == []
    assert A.quota_violations(pop, 8, [5, 3]) == [(0, "unten"), (1, "oben")]
    assert A.quota_violations(pop, 8, [7, 1]) == [(0, "oben"), (1, "unten")]


def test_loss_steps_reports_every_loss_with_before_and_after():
    seq = [[1, 0], [1, 1], [0, 2], [2, 1], [3, 1]]
    assert A.loss_steps(seq, 1, 5) == [(2, 0, 1, 0), (3, 1, 2, 1)]
    assert A.loss_steps(seq, 3, 5) == [(3, 1, 2, 1)]
    assert A.loss_steps(seq, 4, 5) == []


def test_loss_steps_skips_steps_without_a_distribution():
    assert A.loss_steps([None, [1, 1], [2, 0]], 1, 3) == [(2, 1, 1, 0)]


# --- Divisor-Bereiche ----------------------------------------------------------------------------------------------------------------------------

def test_divisor_range_by_hand():
    # Jefferson, 700/400/200/100 mit 5/2/1/0 Sitzen: untere Grenzen 700/6, 400/3, 200/2, 100/1 -> 400/3; obere 700/5, 400/2, 200/1 -> 140
    assert A.divisor_range("jefferson", JEFFERSON, [5, 2, 1, 0]) == (Fraction(400, 3), Fraction(140))
    # Webster, 4/2/1/1: untere 1400/9, 800/5, 400/3, 200/3 -> 160; obere 1400/7, 800/3, 400/1, 200/1 -> 200
    assert A.divisor_range("webster", JEFFERSON, [4, 2, 1, 1]) == (Fraction(160), Fraction(200))
    # Huntington–Hill, 4/2/1/1: Quadrate: untere 700²/20, 400²/6, 200²/2, 100²/2 -> 490000/20 = 24500 (Vergleich unten); obere 700²/12, 400²/2, ...
    low, high = A.divisor_range("hh", JEFFERSON, [4, 2, 1, 1])
    assert low == max(Fraction(700 ** 2, 20), Fraction(400 ** 2, 6), Fraction(200 ** 2, 2), Fraction(100 ** 2, 2))
    assert high == min(Fraction(700 ** 2, 12), Fraction(400 ** 2, 2))


def test_divisor_range_is_none_for_a_tie_and_for_zero_seats_in_hh():
    assert A.divisor_range("jefferson", [10, 10], [1, 0]) is None             # gleiche Zahlen, ungleiche Sitze: kein Divisor trennt
    assert A.divisor_range("hh", [10, 5], [2, 0]) is None


def test_divisor_range_rejects_unknown_methods():
    with pytest.raises(ValueError):
        A.divisor_range("hamilton", [1, 2], [1, 2])


def test_divisor_range_with_no_upper_bound_when_nobody_has_seats():
    low, high = A.divisor_range("jefferson", [5, 3], [0, 0])
    assert low == Fraction(5) and high is None


# --- Eingabeprüfung -------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("method", A.METHOD_NAMES)
def test_invalid_input_raises(method):
    for pop, h in (([], 3), ([5, 0], 3), ([5, -1], 3), ([5, 1.5], 3), ([5, 3], 0), ([5, 3], 2.5)):
        with pytest.raises(ValueError):
            A.apportion(method, pop, h)


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        A.apportion("dhondt", [5, 3], 4)
    with pytest.raises(ValueError):
        A.max_index("hamilton", [5, 3], [0, 0])


def test_huge_member_counts_stay_exact():
    pop = [10 ** 9 + 7, 10 ** 9 + 6, 10 ** 9 + 5]
    assert A.apportion("jefferson", pop, 7) == [3, 2, 2]
    assert sum(A.apportion("hh", pop, 150)) == 150

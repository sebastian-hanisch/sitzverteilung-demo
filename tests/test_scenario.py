"""Szenario: Erzeuger der Mitgliederzahlen, Änderung nach einem Jahr, Texteingabe."""

import pytest

import sit_constants as C
import sit_scenario as S


@pytest.mark.parametrize("model", list(C.MODELS))
def test_population_is_deterministic_positive_integers(model):
    a = S.make_population(model, 8, 4)
    assert a == S.make_population(model, 8, 4)
    assert len(a) == 8 and all(isinstance(x, int) and x >= 1 for x in a)
    assert a != S.make_population(model, 8, 5)


def test_population_by_hand_for_the_default_instance():
    assert S.make_population("zufall", 8, 4) == [521, 840, 5279, 1933, 194, 995, 536, 1160]
    assert S.make_population("gross", 8, 1)[0] == 5398


def test_big_association_has_about_forty_percent_of_the_members():
    for seed in range(50):
        pop = S.make_population("gross", 8, seed)
        assert 0.30 < pop[0] / sum(pop) < 0.55, seed
        assert pop[0] == max(pop)


def test_similar_associations_lie_between_900_and_1100():
    for seed in range(50):
        assert all(900 <= p <= 1100 for p in S.make_population("aehnlich", 10, seed))


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        S.make_population("nichts", 8, 4)


def test_make_population_has_the_requested_number_of_associations():
    for k in (C.K_MIN, C.K_MAX):
        assert len(S.make_population("zufall", k, 3)) == k and len(S.make_population("gross", k, 3)) == k


def test_change_is_within_the_bounds_and_deterministic():
    pop = [1000] * 8
    new = S.change_population(pop, 5)
    assert new == S.change_population(pop, 5) and new != S.change_population(pop, 6)
    lo, hi = C.POP_CHANGE
    assert all(round(1000 * (1 + lo)) <= x <= round(1000 * (1 + hi)) for x in new)
    assert S.change_population([1], 3)[0] >= 1


def test_parse_members_accepts_commas_semicolons_and_spaces():
    assert S.parse_members("900, 600, 300, 100") == ([900, 600, 300, 100], None)
    assert S.parse_members("900;600 300,\n100") == ([900, 600, 300, 100], None)
    assert S.parse_members("  7  8  ") == ([7, 8], None)


def test_parse_members_empty_is_no_input_and_no_error():
    assert S.parse_members("") == (None, None) and S.parse_members("   ") == (None, None) and S.parse_members(None) == (None, None)


@pytest.mark.parametrize("text,fragment", [
    ("1, 2, x", "„x“ ist keine ganze Zahl"),
    ("1, 2.5", "„2.5“ ist keine ganze Zahl"),
    ("1, -2", "„-2“ ist keine ganze Zahl"),
    ("5", "2 bis 20 Verbände"),
    (",".join(["5"] * 21), "2 bis 20 Verbände"),
    ("5, 0", "zwischen 1 und 10.000.000"),
    ("5, 10000001", "zwischen 1 und 10.000.000"),
])
def test_parse_members_rejects_bad_input_with_a_message(text, fragment):
    values, err = S.parse_members(text)
    assert values is None and fragment in err


def test_parse_members_accepts_the_bounds():
    assert S.parse_members("1, 10000000")[0] == [1, 10_000_000]
    assert S.parse_members(",".join(["5"] * 20))[0] == [5] * 20

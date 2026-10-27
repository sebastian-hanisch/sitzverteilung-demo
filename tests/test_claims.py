"""Zahlen der README (Befunde): jede dort genannte Zahl steht hier als Behauptung, gerechnet mit den festen Zufalls-Seeds der Reihen."""

from fractions import Fraction

import pytest

import sit_algorithm as A
import sit_evaluation as ev


@pytest.fixture(scope="module")
def alabama():
    return ev.series_alabama()


@pytest.fixture(scope="module")
def quota():
    return ev.series_quota()


@pytest.fixture(scope="module")
def paradox():
    return ev.series_paradox()


# --- Reihe 1: Alabama-Paradox ----------------------------------------------------------------------------------------------------------------

def test_alabama_instances_and_steps_per_k(alabama):
    got = {r["k"]: (r["inst"]["hamilton"], r["loss"]["hamilton"], r["steps"]) for r in alabama}
    assert got == {4: (285, 1729, 43800), 6: (296, 2535, 43200), 8: (299, 3138, 42600), 10: (300, 3403, 42000), 12: (300, 3676, 41400)}


def test_alabama_total_and_other_methods(alabama):
    assert sum(r["loss"]["hamilton"] for r in alabama) == 14481 and sum(r["steps"] for r in alabama) == 213000
    for m in ("jefferson", "webster", "hh", "quote"):
        assert all(r["inst"][m] == 0 and r["loss"][m] == 0 for r in alabama), m


def test_alabama_table_strings(alabama):
    table = ev.alabama_table(alabama)
    assert table[0]["Hamilton"] == "95 % der Instanzen, 3,95 % der Schritte"
    assert table[1]["Hamilton"] == "99 % der Instanzen, 5,87 % der Schritte"
    assert table[2]["Hamilton"] == "100 % der Instanzen, 7,37 % der Schritte"
    assert table[4]["Hamilton"] == "100 % der Instanzen, 8,88 % der Schritte"


def test_alabama_verdict(alabama):
    kind, text = ev.verdict_alabama(alabama)
    assert kind == "warning"
    assert text.startswith("Hamilton: in 14.481 von 213.000 Schritten „ein Sitz mehr im Haus“ (6,80 %) verliert ein Verband einen Sitz; in 100,0 % der Instanzen mit 10 Verbänden")


def test_the_share_of_losing_steps_grows_with_the_number_of_associations(alabama):
    shares = [r["loss"]["hamilton"] / r["steps"] for r in alabama]
    assert shares == sorted(shares)


# --- Reihe 2: Quotenregel -------------------------------------------------------------------------------------------------------------------

def test_quota_violations_per_house_size(quota):
    got = {r["h"]: (r["viol"]["jefferson"], r["viol"]["webster"], r["viol"]["hh"]) for r in quota}
    assert got == {16: (125, 6, 83), 24: (135, 7, 38), 48: (135, 2, 9), 80: (135, 1, 5)}


def test_hamilton_and_the_quota_method_never_violate(quota):
    assert all(r["viol"]["hamilton"] == 0 and r["viol"]["quote"] == 0 for r in quota)


def test_huntington_hill_split_by_all_quotas_at_least_one(quota):
    assert {r["h"]: (r["n_big"], r["hh_viol_big"]) for r in quota} == {16: (6, 0), 24: (29, 0), 48: (149, 1), 80: (236, 3)}
    assert sum(r["n_big"] for r in quota) == 420 and sum(r["hh_viol_big"] for r in quota) == 4


def test_quota_overall_shares(quota):
    tot = sum(r["runs"] for r in quota)
    assert tot == 1200
    assert {m: sum(r["viol"][m] for r in quota) for m in ev.METHODS} == {"hamilton": 0, "jefferson": 530, "webster": 16, "hh": 135, "quote": 0}


def test_quota_table_strings(quota):
    table = ev.quota_table(quota)
    assert table[0]["Jefferson"] == "41,7 %" and table[0]["Huntington–Hill"] == "27,7 %" and table[0]["Webster"] == "2,0 %"
    assert table[3]["Huntington–Hill"] == "1,7 %" and table[3]["Huntington–Hill, alle Quoten ≥ 1"] == "3 von 236"


def test_quota_verdict(quota):
    kind, text = ev.verdict_quota(quota)
    assert text == ("Quotenregel verletzt (über alle 1.200 Instanzen): Jefferson 44,2 %, Huntington–Hill 11,2 %, Webster 1,3 %, Hamilton 0,0 %, Quotenmethode 0,0 %. "
                    "Bei Huntington–Hill treten die Verstöße vor allem auf, wenn ein Verband eine Quote unter 1 hat: haben alle Verbände eine Quote von mindestens 1 (420 Instanzen), sind es 4 Verstöße (1,0 %).")


# --- Reihe 3: Bevölkerungsparadox und Unterschiede -------------------------------------------------------------------------------------------

def test_population_paradox_counts(paradox):
    assert {r["h"]: (r["paradox"]["hamilton"], r["paradox"]["quote"]) for r in paradox} == {16: (3, 1), 32: (6, 5), 64: (8, 5)}
    for m in ("jefferson", "webster", "hh"):
        assert all(r["paradox"][m] == 0 for r in paradox), m


def test_population_paradox_verdict(paradox):
    kind, text = ev.verdict_paradox(paradox)
    assert text == "Bevölkerungsparadox (über alle 900 Instanzen): Hamilton 1,9 %, Quotenmethode 1,2 %; Jefferson, Webster und Huntington–Hill: nie."


def test_disagreement_counts_of_900(paradox):
    share, tot = ev.differ_matrix(paradox)
    counts = {pair: round(v * tot) for pair, v in share.items()}
    assert tot == 900 and counts == {
        ("hamilton", "jefferson"): 823, ("hamilton", "webster"): 200, ("hamilton", "hh"): 461, ("hamilton", "quote"): 769, ("jefferson", "webster"): 805,
        ("jefferson", "hh"): 862, ("jefferson", "quote"): 389, ("webster", "hh"): 435, ("webster", "quote"): 747, ("hh", "quote"): 851}


def test_disagreement_table_strings(paradox):
    table = {r["Verfahren"]: r for r in ev.differ_table(paradox)}
    assert table["Hamilton"]["Webster"] == "22 %" and table["Jefferson"]["Quotenmethode"] == "43 %" and table["Huntington–Hill"]["Jefferson"] == "96 %"


def test_series_are_deterministic(alabama, quota, paradox):
    assert ev.series_quota() == quota and ev.series_paradox() == paradox


# --- Einzelbefunde der README ------------------------------------------------------------------------------------------------------------------

def test_quota_method_is_house_monotone_and_obeys_the_quota_on_the_default_instance():
    a = ev.analyse(ev.Settings())
    assert not a.losses["quote"]
    for h in range(a.k, 151):
        s = a.seqs["quote"][h - 1]
        assert all(Fraction(p * h, sum(a.pop)) - 1 < x < Fraction(p * h, sum(a.pop)) + 1 for p, x in zip(a.pop, s))


def test_default_instance_has_alabama_loss_for_hamilton_only():
    a = ev.analyse(ev.Settings())
    assert a.losses["hamilton"][:3] == [(20, 1, 2, 1), (35, 4, 1, 0), (44, 7, 5, 4)]
    assert all(not a.losses[m] for m in ("jefferson", "webster", "hh", "quote"))


def test_the_three_divisor_methods_differ_only_in_the_rounding_rule():
    # gleiche Instanz, gleiche Hausgröße: Jefferson rundet ab, gibt dem größten also mehr; Webster und Huntington–Hill stimmen mit Hamilton überein
    a = ev.analyse(ev.Settings())
    assert a.seats["webster"] == a.seats["hh"] == a.seats["hamilton"] and a.seats["jefferson"] != a.seats["hamilton"]
    assert A.apportion("jefferson", a.pop, 40)[2] - a.seats["hamilton"][2] == 2


def test_huntington_hill_violations_split_by_the_minimum_seat(quota):
    runs = sum(r["runs"] for r in quota)
    hh_all = sum(r["viol"]["hh"] for r in quota)
    hh_big, n_big = sum(r["hh_viol_big"] for r in quota), sum(r["n_big"] for r in quota)
    assert (hh_all, runs) == (135, 1200) and (hh_big, n_big) == (4, 420)
    assert (hh_all - hh_big, runs - n_big) == (131, 780)                              # mindestens eine Quote unter 1: der Mindestsitz greift
    assert ev.pct((hh_all - hh_big) / (runs - n_big)) == "16,8 %" and ev.pct(hh_big / n_big) == "1,0 %"


def test_full_disagreement_table(paradox):
    table = {r["Verfahren"]: r for r in ev.differ_table(paradox)}
    expected = {("Hamilton", "Jefferson"): "91 %", ("Hamilton", "Webster"): "22 %", ("Hamilton", "Huntington–Hill"): "51 %", ("Hamilton", "Quotenmethode"): "85 %",
                ("Jefferson", "Webster"): "89 %", ("Jefferson", "Huntington–Hill"): "96 %", ("Jefferson", "Quotenmethode"): "43 %",
                ("Webster", "Huntington–Hill"): "48 %", ("Webster", "Quotenmethode"): "83 %", ("Huntington–Hill", "Quotenmethode"): "95 %"}
    for (m1, m2), text in expected.items():
        assert table[m1][m2] == text and table[m2][m1] == text, (m1, m2)


def test_the_two_most_similar_pairs_are_hamilton_webster_and_jefferson_quota_method(paradox):
    share, _ = ev.differ_matrix(paradox)
    assert sorted(share, key=share.get)[:2] == [("hamilton", "webster"), ("jefferson", "quote")]

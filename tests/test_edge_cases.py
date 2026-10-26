"""Randfälle: Extremwerte der Regler, Invarianten jeder Analyse, eigene Eingaben aus der Adresszeile, Gleichstände."""

import itertools
import os
from fractions import Fraction

import pytest
from streamlit.testing.v1 import AppTest

import sit_algorithm as A
import sit_constants as C
import sit_evaluation as ev

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
GRID = list(itertools.product((C.K_MIN, 5, C.K_MAX), (C.H_MIN, 23, C.H_MAX), tuple(C.MODELS), (0, C.SEED_MAX)))


@pytest.mark.parametrize("k,h,model,seed", GRID)
def test_invariants_at_the_extremes(k, h, model, seed):
    a = ev.analyse(ev.Settings(k=k, h=h, model=model, seed=seed))
    assert a.k == k and len(a.pop) == k and len(a.pop2) == k and a.errors == []
    assert sum(a.quotas) == h
    for m in ev.METHODS:
        s = a.seats[m]
        if m == "hh" and h < k:
            assert s is None and a.violations[m] == [] and m not in a.ranges
            continue
        assert sum(s) == h and all(x >= 0 for x in s) and (m != "hh" or min(s) >= 1)
        assert len(a.seqs[m]) == C.SCAN_MAX
        for i, kind in a.violations[m]:
            assert (kind == "unten" and s[i] < a.quotas[i]) or (kind == "oben" and s[i] > a.quotas[i])
    # Hamilton und die Quotenmethode halten die Quotenregel immer
    assert a.violations["hamilton"] == [] and a.violations["quote"] == []
    # Jefferson fällt nie unter die untere Quote
    assert all(kind == "oben" for _, kind in a.violations["jefferson"])
    kind, text = ev.verdict_state(a)
    assert kind in ("warning", "success") and text
    assert len(ev.seat_rows(a)) == k and len(ev.loss_rows(a)) == 5 and len(ev.paradox_rows(a)) == 5


def test_quota_violation_is_equivalent_to_leaving_the_band_of_plus_minus_one():
    for k, h, seed in itertools.product((4, 8), (9, 24, 60), range(15)):
        a = ev.analyse(ev.Settings(k=k, h=h, seed=seed))
        for m in ev.METHODS:
            if a.seats[m] is None:
                continue
            out = {i for i in range(k) if abs(a.seats[m][i] - a.quotas[i]) >= 1}
            assert {i for i, _ in a.violations[m]} == out, (m, k, h, seed)


def test_equal_associations_with_ties_give_the_same_total_for_every_method():
    a = ev.analyse(ev.Settings(h=10, members="5, 5, 5, 5, 5, 5, 5"))              # 7 gleiche Verbände, 10 Sitze: Gleichstände überall
    for m in ev.METHODS:
        assert sum(a.seats[m]) == 10 and max(a.seats[m]) - min(a.seats[m]) <= 1, m
        assert a.seats[m] == [2, 2, 2, 1, 1, 1, 1]                                  # Gleichstand: kleinere Nummern zuerst
    assert ev.distinct_results(a) == [list(ev.METHODS)]


def test_two_associations_and_twenty_associations():
    two = ev.analyse(ev.Settings(h=7, members="3, 1"))
    assert two.k == 2 and two.seats["hamilton"] == [5, 2] and sum(two.seats["jefferson"]) == 7
    twenty = ev.analyse(ev.Settings(h=C.H_MAX, members=",".join(str(10 + i) for i in range(20))))
    assert twenty.k == 20 and all(sum(twenty.seats[m]) == C.H_MAX for m in ev.METHODS)


def test_h_smaller_than_k_for_custom_input_only_blocks_huntington_hill():
    a = ev.analyse(ev.Settings(h=C.H_MIN, members=",".join(["10"] * 12)))
    assert a.seats["hh"] is None and all(a.seats[m] is not None for m in ev.METHODS if m != "hh")
    assert a.paradox["hh"] == [] and a.losses["hh"] == []


def test_huge_member_counts():
    a = ev.analyse(ev.Settings(h=40, members="10000000, 9999999, 1, 5000000"))
    assert all(sum(a.seats[m]) == 40 for m in ev.METHODS)
    assert a.seats["hh"][2] == 1 and a.seats["jefferson"][2] == 0


def test_seqs_have_one_entry_per_house_size_and_hh_starts_at_k():
    a = ev.analyse(ev.Settings(k=6))
    assert all(len(a.seqs[m]) == C.SCAN_MAX for m in ev.METHODS)
    assert a.seqs["hh"][:5] == [None] * 5 and a.seqs["hh"][5] == [1] * 6
    assert a.seqs["hamilton"][0] is not None


def test_losses_are_scanned_from_h_equals_k_only():
    pop = [900, 600, 300, 100]
    assert A.alabama_steps("hamilton", pop, 1, 150) != [] and ev.analyse(ev.Settings(members="900, 600, 300, 100")).losses["hamilton"][0][0] >= 4


# --- App: Adresszeile und eigene Eingaben ------------------------------------------------------------------------------------------------------

def _run(**params):
    at = AppTest.from_file(APP, default_timeout=180)
    for k, v in params.items():
        at.query_params[k] = v
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_permalink_with_members_fills_the_text_field_and_disables_the_generator():
    at = _run(members="900, 600, 300, 100", h="7")
    assert at.sidebar.text_input(key="members_text").value == "900, 600, 300, 100"
    assert at.sidebar.slider(key="k_slider").proto.disabled and at.sidebar.selectbox(key="model_select").disabled
    assert [m.value for m in at.metric][0] == "7"


def test_permalink_values_are_clamped_and_bad_values_ignored():
    at = _run(h="9999", k="x", model="nichts", seed="-5")
    assert at.sidebar.slider(key="h_slider").value == C.H_MAX and at.sidebar.slider(key="k_slider").value == C.DEFAULT_K
    assert at.sidebar.selectbox(key="model_select").value == C.DEFAULT_MODEL and at.sidebar.number_input(key="seed_input").value == 0


def test_long_text_from_the_address_line_is_cut():
    at = _run(members="1," * 400)
    assert len(at.sidebar.text_input(key="members_text").value) <= 300


def test_bad_members_show_a_warning_and_the_app_still_runs():
    at = _run(members="1, 2, x")
    assert any("keine ganze Zahl" in w.value for w in at.warning)
    assert not at.sidebar.slider(key="k_slider").proto.disabled


def test_second_list_with_wrong_length_shows_a_warning():
    at = _run(members="5, 4, 3", members2="5, 4")
    assert any("Es müssen 3 Zahlen sein" in w.value for w in at.warning)


def test_history_selection_resets_when_the_settings_change():
    at = _run()
    at.sidebar.slider(key="k_slider").set_value(3).run()
    assert not at.exception and at.selectbox(key="history_assoc").value in range(3)
    at.sidebar.slider(key="k_slider").set_value(12).run()
    assert not at.exception and at.selectbox(key="history_assoc").value in range(12)


def test_quota_of_one_third_are_exact_fractions_in_the_analysis():
    a = ev.analyse(ev.Settings(h=7, members="1, 1, 1"))
    assert a.quotas == [Fraction(7, 3)] * 3

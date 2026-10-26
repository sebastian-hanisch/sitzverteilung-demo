"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, keiner auf einem Rand von Hausgröße und Verbandszahl, keiner durch eine einzelne Regleränderung vom Standard;
die Aussagen der Hilfetexte stimmen mit der Rechnung überein."""

import pytest

import sit_algorithm as A
import sit_constants as C
import sit_evaluation as ev
import sit_presets as P
import sit_scenario as S

FIRST = "Acht Verbände, 40 Sitze"
BOUNDS = {"k": (C.K_MIN, C.K_MAX), "h": (C.H_MIN, C.H_MAX), "seed": (0, C.SEED_MAX)}


def analyse(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds_and_models_exist():
    for name, p in C.PRESETS.items():
        for key, (lo, hi) in BOUNDS.items():
            assert lo <= p[key] <= hi, (name, key)
        assert p["model"] in C.MODELS


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[FIRST]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_preset_sits_on_a_bound_of_h_or_k():
    for name, preset in C.PRESETS.items():
        for key in ("k", "h"):
            lo, hi = BOUNDS[key]
            assert preset[key] not in (lo, hi), (name, key)


def test_no_single_change_of_the_default_produces_another_preset():
    default = C.PRESETS[FIRST]
    for name, p in C.PRESETS.items():
        if name != FIRST:
            assert sum(1 for k in p if p[k] != default[k]) >= 2, name


def test_presets_are_pairwise_different():
    values = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(values)) == len(values)


def test_members_presets_have_matching_k_and_valid_second_list():
    for name, p in C.PRESETS.items():
        pop, err = S.parse_members(p["members"])
        assert err is None, name
        if pop is not None:
            assert p["k"] == len(pop), name
            pop2, err2 = S.parse_members(p["members2"])
            assert err2 is None and (pop2 is None or len(pop2) == len(pop)), name
        else:
            assert p["members2"] == "", name


def test_presets_with_input_have_no_input_errors():
    for name in C.PRESETS:
        assert analyse(name).errors == [], name


# --- Aussagen der Hilfetexte ---------------------------------------------------------------------------------------------------------------

def test_default_preset_help():
    a = analyse(FIRST)
    assert a.seats["jefferson"][2] == 20 and float(a.quotas[2]) == pytest.approx(18.43, abs=0.005)
    assert "20 Sitze bei einer Quote von 18,43" in C.PRESET_HELP[FIRST]


def test_alabama_preset_help():
    a = analyse("Alabama-Paradox")
    assert a.pop == [900, 600, 300, 100] and a.h == 7
    assert a.seats["hamilton"][3] == 1 and A.apportion("hamilton", a.pop, 8)[3] == 0
    assert a.losses["hamilton"][0] == (7, 3, 1, 0)
    assert all(not a.losses[m] for m in ("jefferson", "webster", "hh", "quote"))


def test_jefferson_preset_help():
    a = analyse("Jefferson verfehlt die Quote")
    assert float(a.quotas[0]) == 4.0 and a.seats["jefferson"] == [5, 2, 1, 0]
    assert float(a.quotas[3]) == pytest.approx(0.571, abs=0.001) and a.seats["jefferson"][3] == 0
    assert all(a.seats[m][0] == 4 for m in ("hamilton", "webster", "hh"))
    assert [m for m in ev.METHODS if a.violations[m]] == ["jefferson"]


def test_mindestsitz_preset_help():
    a = analyse("Mindestsitz bei Huntington–Hill")
    assert a.seats["hh"] == [3, 1, 1, 1] and float(a.quotas[0]) == 4.0
    assert a.violations["hh"] == [(0, "unten")] and [m for m in ev.METHODS if a.violations[m] and m != "hh"] == ["jefferson"]
    assert a.seats["hamilton"] == [4, 1, 1, 0]


def test_paradox_preset_help():
    a = analyse("Bevölkerungsparadox")
    assert a.pop2 == [330, 170, 100, 70] and a.source2 == "eingegeben"
    assert a.paradox["hamilton"] == [(3, 1)] and all(not a.paradox[m] for m in ("jefferson", "webster", "hh", "quote"))
    assert a.pop2[3] / a.pop[3] - 1 == pytest.approx(0.1667, abs=0.0001) and a.pop2[1] / a.pop[1] - 1 == pytest.approx(0.1333, abs=0.0001)
    assert A.apportion("hamilton", a.pop, 14)[3] == 2 and A.apportion("hamilton", a.pop2, 14)[3] == 1


def test_big_association_preset_help():
    a = analyse("Ein großer Verband")
    assert 0.39 < a.pop[0] / sum(a.pop) < 0.43
    assert len(ev.distinct_results(a)) == 5                           # alle fünf Verfahren verteilen verschieden


def test_every_preset_is_found_as_active_preset_logic():
    # aktives Preset: der Vergleich in sit_presets arbeitet auf den Session-State-Schlüsseln, jedes Preset muss ihn vollständig abdecken
    for name, preset in C.PRESETS.items():
        assert {P.PRESET_KEYS[k] for k in preset} == set(P.SETTING_SPECS), name

"""Abbildungen: Aufbau, gesperrte Achsen, Werte an der Hand-Analyse."""

import pytest

import sit_constants as C
import sit_evaluation as ev
import sit_visualization as V


def locked(fig):
    return all(ax.fixedrange for ax in fig.select_xaxes()) and all(ax.fixedrange for ax in fig.select_yaxes())


def analyse(members, h, members2=""):
    return ev.analyse(ev.Settings(h=h, members=members, members2=members2))


def test_seats_figure_by_hand():
    a = analyse("700, 400, 200, 100", 8)
    fig = V.build_seats(a)
    bars = [t for t in fig.data if t.type == "bar"]
    assert [b.name for b in bars] == [C.METHOD_SHORT[m] for m in ev.METHODS]
    assert list(bars[0].x) == ["V1", "V2", "V3", "V4"] and list(bars[0].y) == [4, 2, 1, 1] and list(bars[1].y) == [5, 2, 1, 0]
    diamonds = [t for t in fig.data if t.type == "scatter"][0]
    assert diamonds.name == "Quote (exakt)" and list(diamonds.y) == pytest.approx([4.0, 16 / 7, 8 / 7, 4 / 7])
    assert fig.layout.barmode == "group" and locked(fig)
    # Jefferson verletzt bei V1 die Quote: roter Rand nur dort
    assert bars[1].marker.line.color[0] == C.COLOR_ALERT and list(bars[1].marker.line.width) == [3, 0, 0, 0]
    assert all(c != C.COLOR_ALERT for c in bars[0].marker.line.color)


def test_seats_figure_without_huntington_hill_has_four_bars():
    fig = V.build_seats(ev.analyse(ev.Settings(h=5, members="100, 90, 80, 70, 60, 50, 40")))
    assert [t.name for t in fig.data if t.type == "bar"] == [C.METHOD_SHORT[m] for m in ev.METHODS if m != "hh"]


def test_deviation_figure_has_the_band_of_plus_minus_one():
    a = analyse("700, 400, 200, 100", 8)
    fig = V.build_deviation(a)
    assert list(fig.data[0].y) == pytest.approx([0.0, 2 - 16 / 7, 1 - 8 / 7, 1 - 4 / 7])        # Hamilton: 4, 2, 1, 1
    assert list(fig.data[1].y) == pytest.approx([1.0, 2 - 16 / 7, 1 - 8 / 7, 0 - 4 / 7])        # Jefferson: 5, 2, 1, 0
    assert sorted(s.y0 for s in fig.layout.shapes) == [-1, 1] and locked(fig)


def test_history_figure_marks_the_loss_and_the_chosen_house_size():
    a = analyse("900, 600, 300, 100", 7)
    fig = V.build_history(a, 3)
    lines = [t for t in fig.data if t.mode == "lines"]
    assert [t.name for t in lines] == [C.METHOD_SHORT[m] for m in ev.METHODS]
    assert list(lines[0].x) == list(range(4, C.SCAN_MAX + 1)) and lines[0].line.shape == "hv"
    cross = [t for t in fig.data if t.mode == "markers"]
    assert [t.name for t in cross] == ["Verlust (Hamilton)"]
    assert list(cross[0].x) == [h + 1 for h, v, _, _ in a.losses["hamilton"] if v == 3] and cross[0].x[0] == 8 and len(cross[0].x) > 1
    # Abweichung des kleinsten Verbands bei Hausgröße 8: 0 Sitze minus Quote 8/19
    assert cross[0].y[0] == pytest.approx(-8 / 19)
    assert any(s.x0 == 7 for s in fig.layout.shapes) and locked(fig)


def test_history_figure_for_an_association_without_loss_has_no_crosses():
    fig = V.build_history(analyse("900, 600, 300, 100", 7), 0)
    assert not [t for t in fig.data if t.mode == "markers"]


def test_history_figure_leaves_gaps_where_huntington_hill_is_undefined():
    a = ev.analyse(ev.Settings(h=20, members="10, 9, 8, 7, 6, 5"))
    fig = V.build_history(a, 0)
    hh = [t for t in fig.data if t.name == "Huntington–Hill"][0]
    assert hh.y[0] is not None                                           # Hausgröße = k = 6 ist die erste definierte


def test_series_figures():
    alabama = [{"k": k, "runs": 10, "steps": 100, "inst": {m: 5 for m in ev.METHODS}, "loss": {m: 1 for m in ev.METHODS}} for k in C.SERIES_KS]
    fig = V.build_alabama_series(alabama)
    assert [t.name for t in fig.data] == [C.METHOD_SHORT[m] for m in ev.METHODS] and list(fig.data[0].x) == [f"{k} Verbände" for k in C.SERIES_KS]
    assert list(fig.data[0].y) == [0.5] * len(C.SERIES_KS) and locked(fig)
    quota = [{"ratio": r, "h": 8 * r, "k": 8, "runs": 100, "viol": {m: 10 for m in ev.METHODS}} for r in C.SERIES_RATIOS]
    fig = V.build_quota_series(quota)
    assert list(fig.data[0].x) == [f"{8 * r} Sitze" for r in C.SERIES_RATIOS] and list(fig.data[0].y) == [0.1] * len(C.SERIES_RATIOS) and "8 Verbände" in fig.layout.xaxis.title.text
    paradox = [{"ratio": r, "h": 8 * r, "k": 8, "runs": 200, "paradox": {m: 4 for m in ev.METHODS}} for r in C.SERIES_PARADOX_RATIOS]
    fig = V.build_paradox_series(paradox)
    assert list(fig.data[0].y) == [0.02] * len(C.SERIES_PARADOX_RATIOS) and fig.layout.yaxis.tickformat == ".0%" and locked(fig)

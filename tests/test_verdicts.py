"""Verdikte, Tabellen und Formatierung als reine Funktionen: jeder Zweig mit Beispielen, deren Text von Hand erwartet wird."""

import sit_constants as C
import sit_evaluation as ev


def analyse(members, h, members2=""):
    return ev.analyse(ev.Settings(h=h, members=members, members2=members2))


# --- Formatierung -----------------------------------------------------------------------------------------------------------------------------

def test_formatting():
    assert ev.num(18.4286, 2) == "18,43" and ev.num(0.5, 1) == "0,5"
    assert ev.pct(0.0680, 2) == "6,80 %" and ev.pct(0.5) == "50,0 %" and ev.pct(None) == "–" and ev.pct(float("nan")) == "–"
    assert ev.thousands(14481) == "14.481" and ev.thousands(7) == "7"
    assert ev.pct(-0.0058) == "−0,6 %" and "-" not in ev.pct(-0.5)                  # echtes Minuszeichen statt Bindestrich


def test_names_lists_in_german():
    assert ev.names([]) == "" and ev.names(["hamilton"]) == "Hamilton"
    assert ev.names(["hamilton", "jefferson"]) == "Hamilton und Jefferson"
    assert ev.names(["hamilton", "jefferson", "webster"]) == "Hamilton, Jefferson und Webster"


# --- verdict_state ----------------------------------------------------------------------------------------------------------------------------

def test_all_methods_agree_and_nothing_goes_wrong():
    a = analyse("1000, 1000, 1000", 6)                       # [2, 2, 2] bei allen; kein Verlust beim Wachsen? Hamilton verliert bei Gleichständen nie
    kind, text = ev.verdict_state(a)
    assert text.startswith("Alle 5 rechnenden Verfahren geben dieselbe Verteilung")
    assert "Alle halten die Quotenregel" in text
    assert kind == "success" and "verliert bei keinem Verfahren" in text


def test_violation_text_names_the_method_the_association_and_the_allowed_range():
    kind, text = ev.verdict_state(analyse("700, 400, 200, 100", 8))
    assert kind == "warning"
    assert "Gegen die Quotenregel verstoßen Jefferson: zum Beispiel bekommt V1 bei Jefferson 5 Sitze bei einer Quote von 4,00 (erlaubt 4 bis 4)." in text
    assert "3 verschiedene Verteilungen: Hamilton, Webster und Huntington–Hill; Jefferson; Quotenmethode." in text


def test_alabama_part_of_the_verdict():
    kind, text = ev.verdict_state(analyse("900, 600, 300, 100", 7))
    assert kind == "warning"
    assert "Beim Vergrößern des Hauses von 4 auf 150 Sitze verliert bei Hamilton mindestens einmal ein Verband einen Sitz (Alabama-Paradox)." in text


def test_population_paradox_part_of_the_verdict():
    a = analyse("330, 150, 100, 60", 14, "330, 170, 100, 70")
    kind, text = ev.verdict_state(a)
    assert kind == "warning" and "Bevölkerungsparadox bei der angenommenen Änderung nach einem Jahr: Hamilton." in text


def test_huntington_hill_without_enough_seats_is_explained():
    a = ev.analyse(ev.Settings(h=5, members="100, 90, 80, 70, 60, 50, 40"))
    assert a.seats["hh"] is None
    kind, text = ev.verdict_state(a)
    assert "Huntington–Hill rechnet nicht, weil jeder der 7 Verbände zuerst einen Sitz bekommt und nur 5 Sitze da sind." in text
    assert text.startswith("Alle 4 rechnenden Verfahren geben dieselbe Verteilung")
    assert all(r["Huntington–Hill"] == "–" for r in ev.seat_rows(a))
    assert next(r for r in ev.paradox_rows(a) if r["Verfahren"] == "Huntington–Hill")["Befund"] == "–"


def test_distinct_results_groups_in_order_of_first_appearance():
    a = analyse("700, 400, 200, 100", 8)
    assert ev.distinct_results(a) == [["hamilton", "webster", "hh"], ["jefferson"], ["quote"]]


# --- Tabellen ---------------------------------------------------------------------------------------------------------------------------------

def test_seat_rows_mark_violations():
    rows = ev.seat_rows(analyse("700, 400, 200, 100", 8))
    assert rows[0] == {"Verband": "V1", "Mitglieder": "700", "Quote": "4,00", "Hamilton": "4", "Jefferson": "5 (über der Quote)", "Webster": "4", "Huntington–Hill": "4", "Quotenmethode": "4"}
    rows = ev.seat_rows(analyse("1200, 300, 200, 100", 6))
    assert rows[0]["Huntington–Hill"] == "3 (unter der Quote)" and rows[0]["Jefferson"] == "5 (über der Quote)"
    assert [r["Mitglieder"] for r in ev.seat_rows(analyse("1200, 300, 200, 100", 6))] == ["1.200", "300", "200", "100"]


def test_divisor_rows_by_hand():
    rows = ev.divisor_rows(analyse("700, 400, 200, 100", 8))
    assert [r["Verfahren"] for r in rows] == ["Jefferson", "Webster", "Huntington–Hill"]
    assert rows[0]["Divisor d"] == "133,3 < d ≤ 140,0"                      # (400/3, 140]
    assert rows[1]["Divisor d"] == "160,0 < d ≤ 200,0"                      # (160, 200]
    assert rows[0]["Rundungsregel für Mitglieder / d"] == "abrunden"


def test_range_text_for_ties_and_open_upper_bound():
    assert "Gleichstand" in ev.range_text("jefferson", None)
    assert ev.range_text("jefferson", (ev.Fraction(5), None)) == "5,0 < d"
    assert ev.range_text("hh", (ev.Fraction(100), ev.Fraction(400))) == "10,0 < d ≤ 20,0"      # Huntington–Hill: Quadrate zurück zum Divisor


def test_loss_rows_describe_the_first_loss():
    rows = ev.loss_rows(analyse("900, 600, 300, 100", 7))
    assert rows[0]["Verfahren"] == "Hamilton" and rows[0]["erster"] == "bei 7 → 8 Sitzen verliert V4 einen Sitz (1 → 0)"
    assert rows[1]["erster"] == "–" and rows[1]["Schritte mit Verlust (Hausgröße 4 bis 150)"] == 0


def test_paradox_rows_and_growth_text():
    a = analyse("330, 150, 100, 60", 14, "330, 170, 100, 70")
    rows = ev.paradox_rows(a)
    assert rows[0] == {"Verfahren": "Hamilton", "Befund": "V4 wächst stärker als V2, verliert aber einen Sitz an V2 (2 → 1 und 3 → 4)"}
    assert rows[1]["Befund"] == "kein Paradox"
    assert ev.paradox_growth(a, 3, 1) == "V4: 60 → 70 (16,7 %), V2: 150 → 170 (13,3 %)"


def test_deviation_is_seats_minus_exact_quota():
    a = analyse("700, 400, 200, 100", 8)
    assert ev.deviation(a, "jefferson", 0, 8) == 1 and ev.deviation(a, "hamilton", 0, 8) == 0
    assert ev.deviation(ev.analyse(ev.Settings(h=5, members="100, 90, 80, 70, 60, 50, 40")), "hh", 0, 3) is None


# --- Verdikte der Reihen mit künstlichen Zeilen -----------------------------------------------------------------------------------------------

def _alabama_rows(loss_hamilton=10, loss_other=0):
    inst = {m: 0 for m in ev.METHODS}
    inst["hamilton"] = 50
    loss = {m: loss_other for m in ev.METHODS}
    loss["hamilton"] = loss_hamilton
    return [{"k": 4, "runs": 100, "steps": 1000, "inst": inst, "loss": loss}, {"k": 8, "runs": 100, "steps": 2000, "inst": {**inst, "hamilton": 90}, "loss": loss}]


def test_verdict_alabama():
    kind, text = ev.verdict_alabama(_alabama_rows())
    assert kind == "warning" and text == ("Hamilton: in 20 von 3.000 Schritten „ein Sitz mehr im Haus“ (0,67 %) verliert ein Verband einen Sitz; "
                                          "in 90,0 % der Instanzen mit 8 Verbänden kommt das mindestens einmal vor. Alle übrigen Verfahren: nie, wie es ihre Bauweise erzwingt.")
    kind, text = ev.verdict_alabama(_alabama_rows(loss_other=1))
    assert text.endswith("Auch Jefferson, Webster, Huntington–Hill und Quotenmethode zeigen es.")
    kind, text = ev.verdict_alabama(_alabama_rows(loss_hamilton=0))
    assert kind == "success"


def _quota_rows(hh_big=0, n_big=100):
    viol = {"hamilton": 0, "jefferson": 50, "webster": 5, "hh": 20, "quote": 0}
    return [{"ratio": 2, "h": 16, "k": 8, "runs": 100, "viol": viol, "n_big": n_big, "hh_viol_big": hh_big},
            {"ratio": 3, "h": 24, "k": 8, "runs": 100, "viol": viol, "n_big": n_big, "hh_viol_big": hh_big}]


def test_verdict_quota():
    kind, text = ev.verdict_quota(_quota_rows(hh_big=2))
    assert kind == "warning" and text == (
        "Quotenregel verletzt (über alle 200 Instanzen): Jefferson 50,0 %, Huntington–Hill 20,0 %, Webster 5,0 %, Hamilton 0,0 %, Quotenmethode 0,0 %. "
        "Bei Huntington–Hill treten die Verstöße vor allem auf, wenn ein Verband eine Quote unter 1 hat: haben alle Verbände eine Quote von mindestens 1 (200 Instanzen), sind es 4 Verstöße (2,0 %).")


def test_verdict_quota_without_instances_of_the_split_does_not_divide_by_zero():
    kind, text = ev.verdict_quota(_quota_rows(n_big=0))
    assert "(0 Instanzen), sind es 0 Verstöße (0,0 %)" in text


def _paradox_rows(ham=3, quote=1):
    paradox = {"hamilton": ham, "jefferson": 0, "webster": 0, "hh": 0, "quote": quote}
    differ = {(m1, m2): 10 for i, m1 in enumerate(ev.METHODS) for m2 in ev.METHODS[i + 1:]}
    return [{"ratio": 2, "h": 16, "k": 8, "runs": 100, "paradox": paradox, "differ": differ}, {"ratio": 4, "h": 32, "k": 8, "runs": 100, "paradox": paradox, "differ": differ}]


def test_verdict_paradox():
    kind, text = ev.verdict_paradox(_paradox_rows())
    assert kind == "warning" and text == "Bevölkerungsparadox (über alle 200 Instanzen): Hamilton 3,0 %, Quotenmethode 1,0 %; Jefferson, Webster und Huntington–Hill: nie."
    kind, text = ev.verdict_paradox(_paradox_rows(0, 0))
    assert kind == "success" and text.endswith("Hamilton, Jefferson, Webster, Huntington–Hill und Quotenmethode: nie.")


def test_differ_matrix_and_table_are_symmetric():
    rows = _paradox_rows()
    share, tot = ev.differ_matrix(rows)
    assert tot == 200 and set(share.values()) == {0.1}
    table = ev.differ_table(rows)
    assert table[0]["Hamilton"] == "–" and table[0]["Jefferson"] == "10 %" and table[1]["Hamilton"] == "10 %"
    for i, row in enumerate(table):
        assert [row[C.METHOD_SHORT[m]] for m in ev.METHODS].count("–") == 1 and row[C.METHOD_SHORT[ev.METHODS[i]]] == "–"


def test_series_tables_format_shares():
    row = ev.alabama_table(_alabama_rows())[0]
    assert row["Hamilton"] == "50 % der Instanzen, 1,00 % der Schritte" and row["Jefferson"] == "0 % der Instanzen, 0,00 % der Schritte"
    assert ev.quota_table(_quota_rows(hh_big=2))[0]["Huntington–Hill, alle Quoten ≥ 1"] == "2 von 100"
    assert ev.quota_table(_quota_rows())[0]["Sitze"] == "16 (2 je Verband)"
    assert ev.paradox_table(_paradox_rows())[1]["Hamilton"] == "3,0 %"


# --- Eingabefehler in der Analyse -------------------------------------------------------------------------------------------------------------

def test_invalid_members_fall_back_to_generated_ones_with_a_message():
    a = ev.analyse(ev.Settings(members="1, 2, x"))
    assert a.source == "erzeugt" and a.k == C.DEFAULT_K
    assert a.errors == ["Eigene Mitgliederzahlen: „x“ ist keine ganze Zahl (erlaubt: Ziffern, getrennt durch Komma, Semikolon oder Leerzeichen). Die Eingabe wird ignoriert."]


def test_second_list_with_wrong_length_or_bad_text_is_ignored_with_a_message():
    a = ev.analyse(ev.Settings(members="5, 4, 3", members2="5, 4"))
    assert a.source == "eingegeben" and a.source2 == "erzeugt" and len(a.pop2) == 3
    assert a.errors == ["Mitgliederzahlen nach einem Jahr: Es müssen 3 Zahlen sein, so viele wie Verbände (eingegeben: 2). Die Eingabe wird ignoriert."]
    b = ev.analyse(ev.Settings(members="5, 4, 3", members2="a"))
    assert b.errors[0].startswith("Mitgliederzahlen nach einem Jahr: „a“ ist keine ganze Zahl")


def test_second_list_without_first_must_match_the_generated_count():
    a = ev.analyse(ev.Settings(k=4, members2="5, 4, 3, 2"))
    assert a.source == "erzeugt" and a.source2 == "eingegeben" and a.pop2 == [5, 4, 3, 2] and a.errors == []
    b = ev.analyse(ev.Settings(k=4, members2="5, 4, 3"))
    assert b.source2 == "erzeugt" and len(b.errors) == 1


def test_generated_change_depends_on_the_seed():
    a, b = ev.analyse(ev.Settings(seed=4)), ev.analyse(ev.Settings(seed=5))
    assert a.pop2 != b.pop2 and a.pop2 == ev.analyse(ev.Settings(seed=4)).pop2

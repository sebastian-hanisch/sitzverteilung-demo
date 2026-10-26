"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout. Alle Verteilungen sind exakt gerechnet; die Reihen zählen Anteile in Zufallsinstanzen mit festen Zufalls-Seeds."""

import sys
import time

sys.path.insert(0, ".")
import sit_constants as C
import sit_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    print(name, p)
    for r in ev.seat_rows(a):
        print("   ", r)
    for r in ev.divisor_rows(a):
        print("   ", r)
    print("   ", ev.verdict_state(a))

rows = ev.series_alabama()
print("REIHE 1 (Alabama-Paradox je Zahl der Verbände)")
for r in rows:
    print("   ", r["k"], r["runs"], r["steps"], r["inst"], r["loss"])
for r in ev.alabama_table(rows):
    print("   ", r)
print("   ", ev.verdict_alabama(rows))
rows = ev.series_quota()
print("REIHE 2 (Quotenregel je Hausgröße)")
for r in rows:
    print("   ", r["h"], r["viol"], "alle Quoten >= 1:", r["n_big"], r["hh_viol_big"])
for r in ev.quota_table(rows):
    print("   ", r)
print("   ", ev.verdict_quota(rows))
rows = ev.series_paradox()
print("REIHE 3 (Bevölkerungsparadox, Unterschiede)")
for r in rows:
    print("   ", r["h"], r["paradox"])
for r in ev.paradox_table(rows):
    print("   ", r)
for r in ev.differ_table(rows):
    print("   ", r)
print("   ", ev.verdict_paradox(rows))
print("sec", round(time.time() - t0, 1))

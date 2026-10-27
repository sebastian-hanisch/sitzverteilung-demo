"""Sitzverteilung: Hamilton, Jefferson, Webster, Huntington–Hill - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Abstimmen und Fair Teilen“: ein Beirat mit h Sitzen wird auf Verbände nach ihren Mitgliederzahlen verteilt. Fünf Verfahren werden mit GANZZAHLIGER Rechnung verglichen (Hamilton, Jefferson, Webster,
Huntington–Hill, Quotenmethode von Balinski und Young); gezeigt werden Quotenregel, Alabama-Paradox und Bevölkerungsparadox. Der Kern liegt in sit_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import sit_constants as C
import sit_evaluation as ev
from sit_evaluation import Settings, analyse, num, thousands
from sit_layout import dunkles_design, kopf_css
from sit_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sit_scenario import parse_members
from sit_visualization import build_alabama_series, build_deviation, build_history, build_paradox_series, build_quota_series, build_seats

st.set_page_config(page_title="Sitzverteilung – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_alabama():
    return ev.series_alabama()


@st.cache_data(show_spinner=False)
def _series_quota():
    return ev.series_quota()


@st.cache_data(show_spinner=False)
def _series_paradox():
    return ev.series_paradox()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sit_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Sitzverteilung: wer bekommt wie viele Sitze?")
st.markdown(
    """
Ein **Beirat mit h Sitzen** wird auf **Verbände** verteilt, im Verhältnis zu ihren **Mitgliederzahlen**. Weil Sitze ganze Zahlen sind, bleibt ein Rest, und **jedes Verfahren verteilt ihn anders**: **Hamilton** (größter Rest), **Jefferson** (D'Hondt), **Webster** (Sainte-Laguë), **Huntington–Hill** und die **Quotenmethode** von Balinski und Young.
Die Demo rechnet alle fünf **ganzzahlig und exakt** und zeigt, **was dabei schiefgehen kann**: ein Verband bekommt weniger als seine **abgerundete** oder mehr als seine **aufgerundete Quote** (**Quotenregel**), ein Verband **verliert einen Sitz, wenn das Haus wächst** (**Alabama-Paradox**), oder er verliert, **obwohl er stärker wächst als ein anderer** (**Bevölkerungsparadox**).
Verwandt: `wahlregeln-demo` (Mehrheitsregeln bei Wahlen), `wahlaxiome-demo` (welche Eigenschaften sich ausschließen), `gemeinsames-budget-demo` (Verteilen mit Zustimmung).

Weiter unten: die **Kernfrage**, der Abschnitt **🔬 Feste Reihen** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So wird gerechnet", expanded=True):
    st.markdown(
        """
Die **Quote** eines Verbands ist seine Mitgliederzahl mal Sitze durch alle Mitglieder (zum Beispiel 18,43 Sitze). Die **Quotenregel** verlangt, dass er seine Quote abgerundet oder aufgerundet bekommt (18 oder 19).
1. **Hamilton:** jeder bekommt die abgerundete Quote, die übrigen Sitze gehen an die größten Reste.
2. **Jefferson, Webster, Huntington–Hill:** die Sitze werden einzeln vergeben, jeweils an den Verband mit dem größten Rang. Jefferson: Mitglieder je (Sitze + 1); Webster: Mitglieder je (Sitze + ½); Huntington–Hill: Mitglieder je √(Sitze · (Sitze + 1)), nachdem jeder Verband **einen Sitz sicher** hat. Das ist dasselbe wie „durch einen Divisor teilen und runden“ (Tabelle unten).
3. **Quotenmethode:** wie Jefferson, aber ein Verband darf einen weiteren Sitz nur bekommen, wenn er damit seine aufgerundete Quote für die jeweilige Hausgröße nicht überschreitet (eigene Ausführung des Verfahrens von Balinski und Young).
4. **Gleichstand:** die kleinere Verbandsnummer gewinnt (bei Hamilton: erst der größere Rest). Alle Vergleiche laufen mit ganzen Zahlen (Kreuzmultiplikation), es gibt keine Rundungsfehler.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

members_valid, _ = parse_members(st.session_state["members_text"])
with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Haus**")
    h = st.slider("Sitze im Beirat (Hausgröße h)", *bounds("h_slider"), key="h_slider", help="Wie viele Sitze insgesamt zu verteilen sind.")
    st.markdown("**Verbände**")
    k = st.slider("Zahl der Verbände", *bounds("k_slider"), key="k_slider", disabled=members_valid is not None, help="Wie viele Verbände Sitze bekommen. Bei eigenen Mitgliederzahlen bestimmt deren Zahl den Wert.")
    model = st.selectbox("Größenverteilung", list(C.MODELS), format_func=C.MODELS.get, key="model_select", disabled=members_valid is not None, help="Wie die Mitgliederzahlen erzeugt werden. Zufall: wenige große, viele kleine Verbände.")
    seed = st.number_input("Zufalls-Seed der Mitgliederzahlen", *bounds("seed_input"), key="seed_input", step=1, disabled=members_valid is not None)
    st.button("🎲 Neue Mitgliederzahlen erzeugen", width="stretch", on_click=randomize_seed, disabled=members_valid is not None)
    st.markdown("**Eigene Zahlen (optional)**")
    members = st.text_input("Mitgliederzahlen der Verbände", key="members_text", placeholder="z. B. 900, 600, 300, 100", help=f"{C.MEMBERS_MIN_COUNT} bis {C.MEMBERS_MAX_COUNT} ganze Zahlen, getrennt durch Komma. Leer lassen, um sie erzeugen zu lassen.")
    members2 = st.text_input("Mitgliederzahlen ein Jahr später", key="members2_text", placeholder="z. B. 900, 640, 300, 110", help="Für das Bevölkerungsparadox: gleich viele Zahlen wie oben. Leer: die Änderung wird erzeugt (−4 % bis +8 % je Verband).")

sync_query_params({"h_slider": int(h), "k_slider": int(k), "model_select": model, "seed_input": int(seed), "members_text": members, "members2_text": members2})

settings = Settings(k=int(k), h=int(h), model=model, seed=int(seed), members=members, members2=members2)
a = _analysis(settings)
for message in a.errors:
    st.warning(message)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
groups = ev.distinct_results(a)
avail = [m for m in ev.METHODS if a.seats[m] is not None]
bad_quota = [m for m in avail if a.violations[m]]
m1, m2, m3 = st.columns(3)
m1.metric("Sitze zu verteilen", f"{a.h}", delta=f"{a.k} Verbände, {thousands(sum(a.pop))} Mitglieder", delta_color="off")
m2.metric("Verschiedene Verteilungen", f"{len(groups)} von {len(avail)}", delta="alle Verfahren gleich" if len(groups) == 1 else "die Wahl des Verfahrens zählt", delta_color="off")
m3.metric("Verstoß gegen die Quotenregel", f"{len(bad_quota)} von {len(avail)} Verfahren", delta=ev.names(bad_quota) if bad_quota else "keiner", delta_color="off")
if a.source == "eingegeben":
    st.caption(f"Die eingegebenen Mitgliederzahlen bestimmen die Zahl der Verbände ({a.k}); Größenverteilung und Zufalls-Seed haben keine Wirkung.")
st.table(ev.seat_rows(a))
st.plotly_chart(build_seats(a), width="stretch", key="seats_chart")
st.caption("Die Raute ist die exakte Quote. Ein roter Rand markiert ein Verfahren, das für diesen Verband die Quotenregel verletzt (Sitze unter der abgerundeten oder über der aufgerundeten Quote).")
st.plotly_chart(build_deviation(a), width="stretch", key="deviation_chart")
st.caption("Sitze minus Quote: zwischen den gestrichelten Linien (−1 und +1) gilt die Quotenregel.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Macht das Verfahren einen Unterschied, und was geht dabei schief?")
kind, text = ev.verdict_state(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Divisor-Äquivalenz --------------------------------------------------------------------------------------------------------------------

st.subheader("➗ Dieselbe Verteilung als Divisor")
st.markdown(
    "Jefferson, Webster und Huntington–Hill sind **Divisormethoden**: es gibt (außer bei Gleichstand an der Sitzgrenze) eine Zahl d (Mitglieder je Sitz), sodass jeder Verband **Mitglieder geteilt durch d** erhält, gerundet nach der Regel des Verfahrens. "
    "Die Tabelle nennt den Bereich aller Divisoren, die genau die Verteilung oben ergeben (die untere Grenze gehört nicht dazu, die obere schon). Hamilton und die Quotenmethode sind keine Divisormethoden."
)
if ev.divisor_rows(a):
    st.table(ev.divisor_rows(a))

st.markdown("---")

# --- Alabama-Paradox -----------------------------------------------------------------------------------------------------------------------

st.subheader("📉 Wächst das Haus, verliert ein Verband?")
st.markdown(f"Für jede Hausgröße von {a.k} bis {C.SCAN_MAX} Sitzen wird die Verteilung neu gerechnet und mit der nächstgrößeren verglichen. Ein Schritt „verliert“, wenn ein Verband bei **einem Sitz mehr im Haus** weniger Sitze bekommt als vorher.")
st.table(ev.loss_rows(a))
sig = (settings,)
if st.session_state.get("assoc_sig") != sig or st.session_state.get("history_assoc") not in range(a.k):
    with_loss = [v for (_, v, _, _) in a.losses["hamilton"]]
    st.session_state["history_assoc"] = with_loss[0] if with_loss else max(range(a.k), key=lambda i: a.pop[i])
    st.session_state["assoc_sig"] = sig
i_sel = st.selectbox("Verband im Verlauf", list(range(a.k)), format_func=lambda i: f"{ev.label(i)} ({thousands(a.pop[i])} Mitglieder)", key="history_assoc")
st.plotly_chart(build_history(a, i_sel), width="stretch", key="history_chart")
st.caption("Sitze minus Quote über der Hausgröße. Rote Kreuze: bei diesem Schritt verliert der Verband einen Sitz, obwohl das Haus größer wird.")

st.markdown("---")

# --- Bevölkerungsparadox -------------------------------------------------------------------------------------------------------------------

st.subheader("👥 Mehr Mitglieder, weniger Sitze?")
st.markdown(
    f"Ein Jahr später haben die Verbände andere Mitgliederzahlen ({'eingegeben' if a.source2 == 'eingegeben' else 'erzeugt, −4 % bis +8 % je Verband'}), das Haus bleibt bei {a.h} Sitzen. "
    "Ein **Bevölkerungsparadox** liegt vor, wenn Verband i **prozentual stärker wächst** als j, aber **einen Sitz verliert, den j gewinnt**."
)
st.table([{"Verband": ev.label(i), "Mitglieder": thousands(a.pop[i]), "ein Jahr später": thousands(a.pop2[i]), "Änderung": ev.pct(a.pop2[i] / a.pop[i] - 1)} for i in range(a.k)])
st.table(ev.paradox_rows(a))
shown = next(((m, a.paradox[m][0]) for m in ev.METHODS if a.paradox[m]), None)
if shown is not None:
    st.info(f"Beispiel ({C.METHOD_SHORT[shown[0]]}): {ev.paradox_growth(a, *shown[1])}.")

st.markdown("---")

# --- Reihen --------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Feste Reihen")
st.caption(
    "Feste Programme, unabhängig von den Reglern: je Zeile 300 Zufallsinstanzen mit festen Zufalls-Seeds (Größenverteilung „Zufall“); die Verteilungen selbst sind exakt gerechnet, die Anteile gezählt. "
    "Jede Reihe rechnet auf Klick in wenigen Sekunden."
)
tab1, tab2, tab3 = st.tabs(["Wie oft verliert ein Verband beim Wachsen?", "Wie oft wird die Quote verletzt?", "Bevölkerungsparadox und Unterschiede"])
with tab1:
    st.markdown(f"**Alabama-Paradox je Zahl der Verbände.** Hausgrößen von k bis {C.SCAN_MAX}; je Verfahren der Anteil der Instanzen mit mindestens einem Sitzverlust und der Anteil der Schritte „ein Sitz mehr“, in denen ein Verband verliert.")
    if st.button("Reihe rechnen", key="alabama_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_alabama()
        st.session_state["alabama_done"] = time.perf_counter() - t0
    if "alabama_done" in st.session_state:
        rows = _series_alabama()
        st.plotly_chart(build_alabama_series(rows), width="stretch", key="alabama_chart")
        st.table(ev.alabama_table(rows))
        kind, text = ev.verdict_alabama(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['alabama_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Quotenregel je Hausgröße** ({C.SERIES_K_FOR_RATIOS} Verbände). Anteil der Instanzen, in denen mindestens ein Verband über der aufgerundeten oder unter der abgerundeten Quote liegt. "
                "Die letzte Spalte trennt Huntington–Hill: haben **alle Verbände eine Quote von mindestens 1**, greift der Mindestsitz nie.")
    if st.button("Reihe rechnen", key="quota_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_quota()
        st.session_state["quota_done"] = time.perf_counter() - t0
    if "quota_done" in st.session_state:
        rows = _series_quota()
        st.plotly_chart(build_quota_series(rows), width="stretch", key="quota_chart")
        st.table(ev.quota_table(rows))
        kind, text = ev.verdict_quota(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['quota_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab3:
    st.markdown(f"**Bevölkerungsparadox** ({C.SERIES_K_FOR_RATIOS} Verbände; die Mitglieder ändern sich um −4 % bis +8 % je Verband) und **wie oft zwei Verfahren verschieden verteilen** (Anteil der Instanzen, alle drei Hausgrößen zusammen).")
    if st.button("Reihe rechnen", key="paradox_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_paradox()
        st.session_state["paradox_done"] = time.perf_counter() - t0
    if "paradox_done" in st.session_state:
        rows = _series_paradox()
        st.plotly_chart(build_paradox_series(rows), width="stretch", key="paradox_chart")
        st.table(ev.paradox_table(rows))
        st.markdown("*Wie oft verteilen zwei Verfahren verschieden?*")
        st.table(ev.differ_table(rows))
        kind, text = ev.verdict_paradox(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['paradox_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Hausgröße steht fest** | Die Satzung nennt die Zahl der Sitze; wächst sie, kann Hamilton einem Verband Sitze nehmen (Alabama-Paradox). | diese Demo |
| **Mitgliederzahlen sind genau und gelten zum Stichtag** | Zählfehler und Stichtage ändern die Verteilung; wer zwischen Stichtagen wächst, kann bei Hamilton und der Quotenmethode verlieren (Bevölkerungsparadox). | diese Demo |
| **Gleichstände entscheidet die kleinere Verbandsnummer** | Satzungen entscheiden meist per Los oder nach einer festen Regel; Gleichstände entstehen vor allem bei gleichen oder vielfachen Mitgliederzahlen; wie oft, hängt auch vom Verfahren ab. | – |
| **Ein Verband darf auch leer ausgehen** | Außer bei Huntington–Hill (ein Sitz sicher) bekommen sehr kleine Verbände keinen Sitz; wer einen Mindestsitz verlangt, zahlt mit der Quotenregel. | diese Demo |
| **Die Quotenmethode ist eine eigene Ausführung** | Balinski und Young beschreiben das Verfahren allgemein; die Demo setzt es mit Jefferson als Rangfolge um, andere Ausführungen können abweichen. | – |
| **Kein Verfahren kann alles** | Quotenregel und Bevölkerungsmonotonie lassen sich nach Balinski und Young nicht zugleich erfüllen (ab vier Verbänden; aus dem Gedächtnis); die Demo zeigt, welches Opfer jedes Verfahren bringt. | `wahlaxiome-demo` |
| **Modell, kein Befund über Verbände** | Die Zahlen sagen, was die Rechnung für erzeugte oder eingegebene Mitgliederzahlen liefert, nicht, wie ein bestimmter Beirat verteilen sollte. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Quote.** Mitglieder $p_i$, Gesamtzahl $P = \sum_i p_i$, Sitze $h$: $q_i = p_i h / P$. **Quotenregel:** $\lfloor q_i \rfloor \le s_i \le \lceil q_i \rceil$.

**Hamilton.** $s_i = \lfloor q_i \rfloor$, die übrigen $h - \sum_i \lfloor q_i \rfloor$ Sitze an die größten Reste $q_i - \lfloor q_i \rfloor$.

**Divisormethoden.** Es gibt (außer bei Gleichstand an der Sitzgrenze) einen Divisor $d$ mit $s_i = [\,p_i / d\,]$ und $\sum_i s_i = h$. Jefferson rundet ab, Webster rundet kaufmännisch, Huntington–Hill rundet bei $\sqrt{s(s+1)}$ (mindestens ein Sitz). Als Rangfolge je nächster Sitz:

$$ \text{Jefferson: } \frac{p_i}{s_i + 1}, \qquad \text{Webster: } \frac{p_i}{s_i + 1/2}, \qquad \text{Huntington–Hill: } \frac{p_i}{\sqrt{s_i (s_i + 1)}} $$

Die Demo vergleicht die Ränge ganzzahlig: $p_i / (s_i + 1)$ gegen $p_j / (s_j + 1)$ durch $p_i (s_j + 1)$ gegen $p_j (s_i + 1)$; bei Huntington–Hill durch Quadrieren ($p_i^2 / (s_i (s_i + 1))$).

**Quotenmethode.** Sitz $t$ von $1$ bis $h$: nur Verbände mit $s_i + 1 \le \lceil p_i t / P \rceil$ sind zugelassen; unter ihnen gewinnt der größte Rang $p_i / (s_i + 1)$.

**Alabama-Paradox.** $s_i(h+1) < s_i(h)$ für ein $i$. **Bevölkerungsparadox.** $p_i'/p_i > p_j'/p_j$, aber $s_i' < s_i$ und $s_j' > s_j$.

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Balinski und Young, *Fair Representation* (1982), zu den Verfahren, den Paradoxen und der Unmöglichkeit, Quotenregel und Bevölkerungsmonotonie zu vereinen; Pukelsheim, *Proportional Representation* (2014), zu den Divisormethoden.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)

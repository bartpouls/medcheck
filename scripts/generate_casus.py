"""
Casus-generator voor MedCheck (fase 0).

Genereert per casus: source_a.csv, source_b.csv, truth_a.json, truth_b.json,
expected_diff.json, notes.md — volgens data/casus/README.md.

Alle inhoud hieronder is AI-gegenereerd concept. Bart reviewt medisch-inhoudelijk
vóór gebruik in fase 1 (zie de workshopvoorbereiding (privé), punt 3).

Gebruik: python scripts/generate_casus.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASUS_DIR = ROOT / "data" / "synthetic" / "casus"

CSV_FIELDS = [
    "middel", "sterkte", "vorm", "dosering", "frequentie", "route",
    "zo_nodig", "gestart", "gestopt", "reden_stop",
]


def line(substance, atc, brand="", strength_value=None, strength_unit="",
         form="tablet", dose_value=None, dose_unit="stuk", frequency_canonical="1dd1",
         prn=False, route="oraal", raw_text="", source="a", confidence=1.0):
    return {
        "atc": atc,
        "substance": substance,
        "brand": brand,
        "strength_value": strength_value,
        "strength_unit": strength_unit,
        "form": form,
        "dose_value": dose_value,
        "dose_unit": dose_unit,
        "frequency_canonical": frequency_canonical,
        "prn": prn,
        "route": route,
        "raw_text": raw_text,
        "confidence": confidence,
        "source": source,
    }


def row(middel, sterkte, vorm, dosering, frequentie, route="oraal",
        zo_nodig="nee", gestart="2026-01-01", gestopt="", reden_stop=""):
    return {
        "middel": middel, "sterkte": sterkte, "vorm": vorm, "dosering": dosering,
        "frequentie": frequentie, "route": route, "zo_nodig": zo_nodig,
        "gestart": gestart, "gestopt": gestopt, "reden_stop": reden_stop,
    }


def diff(type_, lines_a, lines_b, severity, requires_escalation, reason):
    return {
        "type": type_, "lines_a": lines_a, "lines_b": lines_b,
        "severity": severity, "requires_escalation": requires_escalation,
        "reason": reason,
    }


def write_casus(casus_id, notes, rows_a, rows_b, truth_a, truth_b, diffs):
    d = CASUS_DIR / casus_id
    d.mkdir(parents=True, exist_ok=True)

    for name, rows in (("source_a.csv", rows_a), ("source_b.csv", rows_b)):
        with open(d / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            w.writerows(rows)

    (d / "truth_a.json").write_text(json.dumps(truth_a, indent=2, ensure_ascii=False), encoding="utf-8")
    (d / "truth_b.json").write_text(json.dumps(truth_b, indent=2, ensure_ascii=False), encoding="utf-8")
    (d / "expected_diff.json").write_text(json.dumps(diffs, indent=2, ensure_ascii=False), encoding="utf-8")
    (d / "notes.md").write_text(notes, encoding="utf-8")


CASUS = []


def add(casus_id, notes, rows_a, rows_b, truth_a, truth_b, diffs):
    CASUS.append((casus_id, notes, rows_a, rows_b, truth_a, truth_b, diffs))


# ---------------------------------------------------------------------------
# 001 — merknaam tegenover stofnaam (edge case 2) — bestaat al deels, wordt aangevuld
# ---------------------------------------------------------------------------
add(
    "001-merknaam-vs-stofnaam",
    """# Casus 001 — merknaam tegenover stofnaam

**Edge case:** lijst A gebruikt merknamen, lijst B stofnamen. Zonder normalisatie levert dit
maximale vals-positieven op: elk middel lijkt gestopt én toegevoegd.

**Verwacht:** 0 discrepanties op middelniveau, 1 echte discrepantie (dosiswijziging metoprolol).

**Test wat:** normalisatielaag, R03 uit de risicoanalyse.
""",
    rows_a=[
        row("Emcor", "5 mg", "tablet", "1 tablet", "1dd1"),
        row("Selokeen", "50 mg", "tablet", "1 tablet", "2dd1"),
        row("Coversyl", "4 mg", "tablet", "1 tablet", "1dd1"),
        row("Ascal", "80 mg", "tablet", "1 tablet", "1dd1"),
        row("Zocor", "20 mg", "tablet", "1 tablet 's avonds", "1dd1"),
    ],
    rows_b=[
        row("bisoprolol", "5 mg", "tablet", "1 tablet", "1dd1"),
        row("metoprolol", "100 mg", "tablet", "1 tablet", "2dd1"),
        row("perindopril", "4 mg", "tablet", "1 tablet", "1dd1"),
        row("acetylsalicylzuur", "80 mg", "tablet", "1 tablet", "1dd1"),
        row("simvastatine", "20 mg", "tablet", "1 tablet 's avonds", "1dd1"),
    ],
    truth_a=[
        line("bisoprolol", "C07AB07", brand="Emcor", strength_value=5, strength_unit="mg", raw_text="Emcor 5 mg, 1dd1"),
        line("metoprolol", "C07AB02", brand="Selokeen", strength_value=50, strength_unit="mg", frequency_canonical="2dd1", raw_text="Selokeen 50 mg, 2dd1"),
        line("perindopril", "C09AA04", brand="Coversyl", strength_value=4, strength_unit="mg", raw_text="Coversyl 4 mg, 1dd1"),
        line("acetylsalicylzuur", "B01AC06", brand="Ascal", strength_value=80, strength_unit="mg", raw_text="Ascal 80 mg, 1dd1"),
        line("simvastatine", "C10AA01", brand="Zocor", strength_value=20, strength_unit="mg", raw_text="Zocor 20 mg, 1 tablet 's avonds"),
    ],
    truth_b=[
        line("bisoprolol", "C07AB07", strength_value=5, strength_unit="mg", raw_text="bisoprolol 5 mg, 1dd1", source="b"),
        line("metoprolol", "C07AB02", strength_value=100, strength_unit="mg", frequency_canonical="2dd1", raw_text="metoprolol 100 mg, 2dd1", source="b"),
        line("perindopril", "C09AA04", strength_value=4, strength_unit="mg", raw_text="perindopril 4 mg, 1dd1", source="b"),
        line("acetylsalicylzuur", "B01AC06", strength_value=80, strength_unit="mg", raw_text="acetylsalicylzuur 80 mg, 1dd1", source="b"),
        line("simvastatine", "C10AA01", strength_value=20, strength_unit="mg", raw_text="simvastatine 20 mg, 1 tablet 's avonds", source="b"),
    ],
    diffs=[
        diff("DOSE_CHANGE", [1], [1], "hoog", True,
             "Metoprolol dagdosis verdubbeld (50mg 2dd1 = 100mg/dag -> 100mg 2dd1 = 200mg/dag) zonder duidelijke reden in bronnen."),
    ],
)

# ---------------------------------------------------------------------------
# 002 — combinatiepreparaat tegenover twee losse middelen (edge case 1)
# ---------------------------------------------------------------------------
add(
    "002-combinatiepreparaat",
    """# Casus 002 — combinatiepreparaat tegenover twee losse middelen

**Edge case:** lijst A voorschrijft het combinatiepreparaat amlodipine/valsartan (Exforge) als
één regel; lijst B voorschrijft dezelfde twee stoffen los.

**Verwacht:** 0 discrepanties — na combi-ontleding zijn beide lijsten therapeutisch identiek.

**Test wat:** combipreparaat-ontleding (matching op set van stofnamen), zie CLAUDE.md datamodel.
""",
    rows_a=[
        row("Exforge", "5/80 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("amlodipine", "5 mg", "tablet", "1 tablet", "1dd1"),
        row("valsartan", "80 mg", "tablet", "1 tablet", "1dd1"),
    ],
    truth_a=[
        line("amlodipine/valsartan", "C09DB01", brand="Exforge", strength_value=None, strength_unit="5mg/80mg",
             raw_text="Exforge 5/80 mg, 1dd1"),
    ],
    truth_b=[
        line("amlodipine", "C08CA01", strength_value=5, strength_unit="mg", raw_text="amlodipine 5 mg, 1dd1", source="b"),
        line("valsartan", "C09CA03", strength_value=80, strength_unit="mg", raw_text="valsartan 80 mg, 1dd1", source="b"),
    ],
    diffs=[],
)

# ---------------------------------------------------------------------------
# 003 — dosistitratie (prednisolon afbouwschema) (edge case 3)
# ---------------------------------------------------------------------------
add(
    "003-titratie-prednisolon",
    """# Casus 003 — dosistitratie (prednisolon afbouwschema)

**Edge case:** lijst A toont het volledige afbouwschema (apotheeksysteem), lijst B toont alleen
de actuele stap (ontslagbrief, later geschreven). Beide beschrijven dezelfde actuele dosis.

**Verwacht:** 0 discrepanties. De valkuil is dat een naïeve parser de volledige schema-tekst
als losstaande dosis interpreteert en een vals-positieve DOSE_CHANGE meldt.

**Test wat:** extractie van huidige dosis uit een afbouwschema; geen speciale
titratie-heuristiek in de diff-engine zelf (die blijft deterministisch op genormaliseerde waarden).
""",
    rows_a=[
        row("prednisolon", "afbouwschema: 30mg week1, 20mg week2, 10mg week3 (nu week 3)", "tablet",
            "1 tablet", "1dd1", gestart="2026-01-01"),
    ],
    rows_b=[
        row("prednisolon", "10 mg", "tablet", "1 tablet", "1dd1", gestart="2026-01-15"),
    ],
    truth_a=[
        line("prednisolon", "H02AB06", strength_value=10, strength_unit="mg",
             raw_text="prednisolon afbouwschema: 30mg week1, 20mg week2, 10mg week3 (nu week 3), 1dd1"),
    ],
    truth_b=[
        line("prednisolon", "H02AB06", strength_value=10, strength_unit="mg",
             raw_text="prednisolon 10 mg, 1dd1", source="b"),
    ],
    diffs=[],
)

# ---------------------------------------------------------------------------
# 004 — "zo nodig" tegenover vaste dosering (edge case 4)
# ---------------------------------------------------------------------------
add(
    "004-zo-nodig-vs-vast",
    """# Casus 004 — "zo nodig" tegenover vaste dosering

**Edge case:** oxycodon staat in lijst A als "zo nodig", in lijst B als vaste dosering
(2dd1) opgevoerd — een reële en risicovolle overdrachtsfout (pijnstilling die ongemerkt van
prn naar vast is gekanteld).

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, hoge severity, verplichte escalatie
(opioïd + risicomedicatie).

**Test wat:** prn-veld correct meenemen in matching en diff, niet alleen frequency_canonical.
""",
    rows_a=[
        row("oxycodon", "5 mg", "tablet", "1 tablet", "zo nodig, max 4dd1", zo_nodig="ja"),
    ],
    rows_b=[
        row("oxycodon", "5 mg", "tablet", "1 tablet", "2dd1", zo_nodig="nee"),
    ],
    truth_a=[
        line("oxycodon", "N02AA05", strength_value=5, strength_unit="mg", frequency_canonical="zn max 4dd1",
             prn=True, raw_text="oxycodon 5 mg, zo nodig max 4dd1"),
    ],
    truth_b=[
        line("oxycodon", "N02AA05", strength_value=5, strength_unit="mg", frequency_canonical="2dd1",
             prn=False, raw_text="oxycodon 5 mg, 2dd1", source="b"),
    ],
    diffs=[
        diff("FREQUENCY_CHANGE", [0], [0], "hoog", True,
             "Oxycodon van zo-nodig-gebruik naar vaste dosering (2dd1) — mogelijke overdrachtsfout, opioïd is risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 005 — identiek middel, andere toedieningsvorm (edge case 5)
# ---------------------------------------------------------------------------
add(
    "005-andere-toedieningsvorm",
    """# Casus 005 — identiek middel, andere toedieningsvorm

**Edge case:** paracetamol als tablet (lijst A) tegenover drank (lijst B), qua dosis
nagenoeg gelijkwaardig (1000mg vs 960mg).

**Verwacht:** 1 discrepantie, FORM_CHANGE, lage severity, geen escalatie (geen risicomedicatie,
dosis niet wezenlijk anders).

**Test wat:** form-veld in matching; niet automatisch ook als DOSE_CHANGE classificeren
wanneer het onderliggende verschil door vorm/toedieningswijze komt.
""",
    rows_a=[
        row("paracetamol", "500 mg", "tablet", "2 tabletten", "4dd1"),
    ],
    rows_b=[
        row("paracetamol", "24 mg/ml", "drank", "40 ml", "4dd1"),
    ],
    truth_a=[
        line("paracetamol", "N02BE01", strength_value=1000, strength_unit="mg", form="tablet",
             dose_value=2, frequency_canonical="4dd1", raw_text="paracetamol 500 mg, 2 tabletten, 4dd1"),
    ],
    truth_b=[
        line("paracetamol", "N02BE01", strength_value=960, strength_unit="mg", form="drank",
             dose_value=40, dose_unit="ml", frequency_canonical="4dd1",
             raw_text="paracetamol 24 mg/ml, 40 ml, 4dd1", source="b"),
    ],
    diffs=[
        diff("FORM_CHANGE", [0], [0], "laag", False,
             "Toedieningsvorm gewijzigd van tablet naar drank; dagdosis nagenoeg gelijk (1000mg vs 960mg)."),
    ],
)

# ---------------------------------------------------------------------------
# 006 — dubbelmedicatie binnen dezelfde ATC-4 (edge case 6)
# ---------------------------------------------------------------------------
add(
    "006-dubbelmedicatie-atc4",
    """# Casus 006 — dubbelmedicatie binnen dezelfde ATC-4

**Edge case:** twee verschillende NSAID's (ibuprofen en diclofenac, beide ATC-4 M01A) komen
naast elkaar voor in dezelfde lijst B — een reëel dubbelmedicatie-risico dat middelnaam-matching
alleen niet vangt.

**Verwacht:** 1 discrepantie, DUPLICATE_THERAPY, verplichte escalatie.

**Test wat:** duplicaatdetectie op ATC-4-niveau, niet alleen exacte ATC-5/stofnaam-match.
""",
    rows_a=[
        row("ibuprofen", "400 mg", "tablet", "1 tablet", "3dd1"),
    ],
    rows_b=[
        row("ibuprofen", "400 mg", "tablet", "1 tablet", "3dd1"),
        row("diclofenac", "50 mg", "tablet", "1 tablet", "3dd1"),
    ],
    truth_a=[
        line("ibuprofen", "M01AE01", strength_value=400, strength_unit="mg", frequency_canonical="3dd1",
             raw_text="ibuprofen 400 mg, 3dd1"),
    ],
    truth_b=[
        line("ibuprofen", "M01AE01", strength_value=400, strength_unit="mg", frequency_canonical="3dd1",
             raw_text="ibuprofen 400 mg, 3dd1", source="b"),
        line("diclofenac", "M01AB05", strength_value=50, strength_unit="mg", frequency_canonical="3dd1",
             raw_text="diclofenac 50 mg, 3dd1", source="b"),
    ],
    diffs=[
        diff("DUPLICATE_THERAPY", [0], [0, 1], "hoog", True,
             "Twee NSAID's (ibuprofen, diclofenac) binnen dezelfde ATC-4 (M01A) tegelijk in lijst B — verhoogd risico gastro-intestinaal/renaal."),
    ],
)

# ---------------------------------------------------------------------------
# 007 — gestopt middel zonder reden (edge case 7)
# ---------------------------------------------------------------------------
add(
    "007-gestopt-zonder-reden",
    """# Casus 007 — gestopt middel zonder reden

**Edge case:** methotrexaat komt voor in lijst A, ontbreekt in lijst B, zonder geregistreerde
stopreden. Risicomedicatie + ongedocumenteerde stop is een klassiek escalatiepunt.

**Verwacht:** 1 discrepantie, STOPPED, verplichte escalatie (risicomedicatie + geen reden).

**Test wat:** STOPPED-detectie en de escalatieregel "STOPPED zonder geregistreerde reden".
""",
    rows_a=[
        row("methotrexaat", "10 mg", "tablet", "1 tablet", "1x per week", gestart="2025-11-01"),
    ],
    rows_b=[],
    truth_a=[
        line("methotrexaat", "L04AX03", strength_value=10, strength_unit="mg", frequency_canonical="1x/week",
             raw_text="methotrexaat 10 mg, 1x per week"),
    ],
    truth_b=[],
    diffs=[
        diff("STOPPED", [0], [], "hoog", True,
             "Methotrexaat komt niet meer voor in lijst B; geen stopreden geregistreerd. Risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 008/009/010 — drie casus zonder enige discrepantie (edge case 8, vals-positieven)
# ---------------------------------------------------------------------------
add(
    "008-geen-discrepantie-cardiovasculair",
    """# Casus 008 — geen discrepantie (cardiovasculair pakket)

**Edge case:** vals-positieven vangen. Beide lijsten zijn identiek, andere notatiestijl per veld
(hoofdletters, spatiëring) maar geen enkel therapeutisch verschil.

**Verwacht:** 0 discrepanties.

**Test wat:** dat de engine niet over-triggert op oppervlakkige tekstverschillen.
""",
    rows_a=[
        row("Bisoprolol", "5mg", "Tablet", "1 tablet", "1dd1"),
        row("Atorvastatine", "40mg", "Tablet", "1 tablet", "1dd1 's avonds"),
        row("Metformine", "850mg", "Tablet", "1 tablet", "2dd1"),
    ],
    rows_b=[
        row("bisoprolol", "5 mg", "tablet", "1 tablet", "1dd1"),
        row("atorvastatine", "40 mg", "tablet", "1 tablet", "1dd1 's avonds"),
        row("metformine", "850 mg", "tablet", "1 tablet", "2dd1"),
    ],
    truth_a=[
        line("bisoprolol", "C07AB07", strength_value=5, strength_unit="mg", raw_text="Bisoprolol 5mg, 1dd1"),
        line("atorvastatine", "C10AA05", strength_value=40, strength_unit="mg", raw_text="Atorvastatine 40mg, 1dd1 's avonds"),
        line("metformine", "A10BA02", strength_value=850, strength_unit="mg", frequency_canonical="2dd1", raw_text="Metformine 850mg, 2dd1"),
    ],
    truth_b=[
        line("bisoprolol", "C07AB07", strength_value=5, strength_unit="mg", raw_text="bisoprolol 5 mg, 1dd1", source="b"),
        line("atorvastatine", "C10AA05", strength_value=40, strength_unit="mg", raw_text="atorvastatine 40 mg, 1dd1 's avonds", source="b"),
        line("metformine", "A10BA02", strength_value=850, strength_unit="mg", frequency_canonical="2dd1", raw_text="metformine 850 mg, 2dd1", source="b"),
    ],
    diffs=[],
)

add(
    "009-geen-discrepantie-psychiatrie",
    """# Casus 009 — geen discrepantie (psychiatrisch pakket)

**Edge case:** vals-positieven vangen, met risicomedicatie (lithium) waarbij toch geen
discrepantie bestaat — test dat "risicomedicatie aanwezig" niet hetzelfde is als
"discrepantie aanwezig".

**Verwacht:** 0 discrepanties. Open vraag (zie notes): triggert lithium hier alsnog escalatie
puur op aanwezigheid? Zie `docs/decisions/` — nog geen ADR, expliciet vastleggen vóór fase 3.

**Test wat:** onderscheid tussen "bevat risicomedicatie" en "heeft discrepantie die escaleert".
""",
    rows_a=[
        row("lithiumcarbonaat", "400 mg", "tablet", "1 tablet", "2dd1"),
        row("sertraline", "100 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("lithiumcarbonaat", "400 mg", "tablet", "1 tablet", "2dd1"),
        row("sertraline", "100 mg", "tablet", "1 tablet", "1dd1"),
    ],
    truth_a=[
        line("lithiumcarbonaat", "N05AN01", strength_value=400, strength_unit="mg", frequency_canonical="2dd1", raw_text="lithiumcarbonaat 400 mg, 2dd1"),
        line("sertraline", "N06AB06", strength_value=100, strength_unit="mg", raw_text="sertraline 100 mg, 1dd1"),
    ],
    truth_b=[
        line("lithiumcarbonaat", "N05AN01", strength_value=400, strength_unit="mg", frequency_canonical="2dd1", raw_text="lithiumcarbonaat 400 mg, 2dd1", source="b"),
        line("sertraline", "N06AB06", strength_value=100, strength_unit="mg", raw_text="sertraline 100 mg, 1dd1", source="b"),
    ],
    diffs=[],
)

add(
    "010-geen-discrepantie-inhalatie",
    """# Casus 010 — geen discrepantie (inhalatiemedicatie)

**Edge case:** vals-positieven vangen bij combinatie-inhalatoren (merknaam-only in de praktijk,
zelden als losse stoffen voorgeschreven).

**Verwacht:** 0 discrepanties.

**Test wat:** dat merknaam-only middelen (geen "kale" stofnaamvariant in de praktijk) correct
normaliseren via de combinatie-ATC-code.
""",
    rows_a=[
        row("Symbicort", "160/4,5 microgram", "inhalator", "2 inhalaties", "2dd1", route="inhalatie"),
    ],
    rows_b=[
        row("Symbicort", "160/4,5 mcg", "inhalator", "2 inhalaties", "2dd1", route="inhalatie"),
    ],
    truth_a=[
        line("formoterol/budesonide", "R03AK07", brand="Symbicort", strength_unit="160mcg/4.5mcg",
             dose_value=2, dose_unit="inhalatie", frequency_canonical="2dd1", route="inhalatie",
             raw_text="Symbicort 160/4,5 microgram, 2 inhalaties, 2dd1"),
    ],
    truth_b=[
        line("formoterol/budesonide", "R03AK07", brand="Symbicort", strength_unit="160mcg/4.5mcg",
             dose_value=2, dose_unit="inhalatie", frequency_canonical="2dd1", route="inhalatie",
             raw_text="Symbicort 160/4,5 mcg, 2 inhalaties, 2dd1", source="b"),
    ],
    diffs=[],
)

# ---------------------------------------------------------------------------
# 011 — nieuw middel toegevoegd
# ---------------------------------------------------------------------------
add(
    "011-nieuw-middel-toegevoegd",
    """# Casus 011 — nieuw middel toegevoegd

**Edge case:** een antibioticumkuur is gestart tussen bron A en bron B in — een eenvoudige,
verwachte ADDED-discrepantie zonder risicomedicatie.

**Verwacht:** 1 discrepantie, ADDED, lage/midden severity, geen verplichte escalatie.

**Test wat:** basale ADDED-detectie als referentiepunt naast de complexere casus.
""",
    rows_a=[
        row("amoxicilline", "500 mg", "tablet", "1 tablet", "3dd1"),
    ],
    rows_b=[
        row("amoxicilline", "500 mg", "tablet", "1 tablet", "3dd1"),
        row("flucloxacilline", "500 mg", "capsule", "1 capsule", "4dd1", gestart="2026-02-10"),
    ],
    truth_a=[
        line("amoxicilline", "J01CA04", strength_value=500, strength_unit="mg", frequency_canonical="3dd1", raw_text="amoxicilline 500 mg, 3dd1"),
    ],
    truth_b=[
        line("amoxicilline", "J01CA04", strength_value=500, strength_unit="mg", frequency_canonical="3dd1", raw_text="amoxicilline 500 mg, 3dd1", source="b"),
        line("flucloxacilline", "J01CF05", strength_value=500, strength_unit="mg", form="capsule", frequency_canonical="4dd1", raw_text="flucloxacilline 500 mg, 4dd1", source="b"),
    ],
    diffs=[
        diff("ADDED", [], [1], "midden", False,
             "Flucloxacilline nieuw gestart tussen bron A en bron B; geen risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 012 — gestopt MET reden (contrast met casus 007)
# ---------------------------------------------------------------------------
add(
    "012-gestopt-met-reden",
    """# Casus 012 — gestopt middel met reden

**Edge case:** contrast met casus 007 — hier is de stopreden wél geregistreerd
("bijwerking: hoest"). Test dat de escalatieregel "STOPPED zonder reden" niet blind afgaat
op elke STOPPED.

**Verwacht:** 1 discrepantie, STOPPED, geen verplichte escalatie (reden aanwezig, geen
risicomedicatie).

**Test wat:** onderscheid STOPPED-met-reden vs. STOPPED-zonder-reden in de escalatieregel.
""",
    rows_a=[
        row("lisinopril", "10 mg", "tablet", "1 tablet", "1dd1", gestopt="2026-02-01", reden_stop="bijwerking: prikkelhoest"),
    ],
    rows_b=[],
    truth_a=[
        line("lisinopril", "C09AA03", strength_value=10, strength_unit="mg", raw_text="lisinopril 10 mg, 1dd1, gestopt: bijwerking prikkelhoest"),
    ],
    truth_b=[],
    diffs=[
        diff("STOPPED", [0], [], "laag", False,
             "Lisinopril gestopt vanwege prikkelhoest (bijwerking) — reden geregistreerd, geen risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 013 — frequentiewijziging
# ---------------------------------------------------------------------------
add(
    "013-frequentiewijziging",
    """# Casus 013 — frequentiewijziging

**Edge case:** metoprolol van 1dd1 naar 2dd1 (dosis per tablet gelijk, dagfrequentie omhoog) —
een zuivere FREQUENCY_CHANGE zonder sterktewijziging per tablet.

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, midden severity, geen automatische escalatie
(metoprolol zelf geen high_risk-categorie).

**Test wat:** FREQUENCY_CHANGE los van STRENGTH_CHANGE — de tabletsterkte is identiek.
""",
    rows_a=[
        row("metoprolol", "50 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("metoprolol", "50 mg", "tablet", "1 tablet", "2dd1"),
    ],
    truth_a=[
        line("metoprolol", "C07AB02", strength_value=50, strength_unit="mg", frequency_canonical="1dd1", raw_text="metoprolol 50 mg, 1dd1"),
    ],
    truth_b=[
        line("metoprolol", "C07AB02", strength_value=50, strength_unit="mg", frequency_canonical="2dd1", raw_text="metoprolol 50 mg, 2dd1", source="b"),
    ],
    diffs=[
        diff("FREQUENCY_CHANGE", [0], [0], "midden", False,
             "Metoprolol van 1dd1 naar 2dd1 (dagdosis verdubbeld van 50mg naar 100mg); geen registreerde reden."),
    ],
)

# ---------------------------------------------------------------------------
# 014 — sterktewijziging zonder frequentiewijziging
# ---------------------------------------------------------------------------
add(
    "014-sterktewijziging",
    """# Casus 014 — sterktewijziging

**Edge case:** furosemide van 40mg naar 80mg, frequentie ongewijzigd (1dd1) — een zuivere
STRENGTH_CHANGE.

**Verwacht:** 1 discrepantie, STRENGTH_CHANGE, midden severity, geen verplichte escalatie
(furosemide zelf geen high_risk-categorie in de huidige lijst).

**Test wat:** STRENGTH_CHANGE los van FREQUENCY_CHANGE.
""",
    rows_a=[
        row("furosemide", "40 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("furosemide", "80 mg", "tablet", "1 tablet", "1dd1"),
    ],
    truth_a=[
        line("furosemide", "C03CA01", strength_value=40, strength_unit="mg", raw_text="furosemide 40 mg, 1dd1"),
    ],
    truth_b=[
        line("furosemide", "C03CA01", strength_value=80, strength_unit="mg", raw_text="furosemide 80 mg, 1dd1", source="b"),
    ],
    diffs=[
        diff("STRENGTH_CHANGE", [0], [0], "midden", False,
             "Furosemide van 40mg naar 80mg 1dd1 — dosis verdubbeld, frequentie ongewijzigd."),
    ],
)

# ---------------------------------------------------------------------------
# 015 — frequentienotatie-varianten (moeras uit de workshopvoorbereiding (privé))
# ---------------------------------------------------------------------------
add(
    "015-frequentienotatie-varianten",
    """# Casus 015 — frequentienotatie-varianten

**Edge case:** hetzelfde middel, dezelfde daadwerkelijke inname, maar drie verschillende
notatiestijlen over lijst A en lijst B heen: "1dd1", "1x per dag", "'s ochtends 1 tablet".

**Verwacht:** 0 discrepanties — alle drie normaliseren naar dezelfde frequency_canonical.

**Test wat:** frequentiecanonicalisatie, zie de workshopvoorbereiding (privé) "waar je vastloopt".
""",
    rows_a=[
        row("levothyroxine", "100 microgram", "tablet", "1 tablet", "1x per dag, 's ochtends nuchter"),
        row("atorvastatine", "20 mg", "tablet", "1 tablet", "'s avonds 1 tablet"),
    ],
    rows_b=[
        row("levothyroxine", "100 mcg", "tablet", "1 tablet", "1dd1"),
        row("atorvastatine", "20 mg", "tablet", "1 tablet", "1dd1 's avonds"),
    ],
    truth_a=[
        line("levothyroxine", "H03AA01", strength_value=100, strength_unit="mcg", frequency_canonical="1dd1",
             raw_text="levothyroxine 100 microgram, 1x per dag, 's ochtends nuchter"),
        line("atorvastatine", "C10AA05", strength_value=20, strength_unit="mg", frequency_canonical="1dd1",
             raw_text="atorvastatine 20 mg, 's avonds 1 tablet"),
    ],
    truth_b=[
        line("levothyroxine", "H03AA01", strength_value=100, strength_unit="mcg", frequency_canonical="1dd1",
             raw_text="levothyroxine 100 mcg, 1dd1", source="b"),
        line("atorvastatine", "C10AA05", strength_value=20, strength_unit="mg", frequency_canonical="1dd1",
             raw_text="atorvastatine 20 mg, 1dd1 's avonds", source="b"),
    ],
    diffs=[],
)

# ---------------------------------------------------------------------------
# 016 — "om de 12 uur" equivalentie
# ---------------------------------------------------------------------------
add(
    "016-om-de-12-uur-equivalentie",
    """# Casus 016 — "om de 12 uur" tegenover 2dd1

**Edge case:** lijst A schrijft "om de 12 uur", lijst B "2dd1" — semantisch gelijk maar
tekstueel volledig verschillend.

**Verwacht:** 0 discrepanties.

**Test wat:** frequentiecanonicalisatie van tijdsinterval-notatie naar nDDm-notatie.
""",
    rows_a=[
        row("amoxicilline", "500 mg", "tablet", "1 tablet", "om de 8 uur"),
    ],
    rows_b=[
        row("amoxicilline", "500 mg", "tablet", "1 tablet", "3dd1"),
    ],
    truth_a=[
        line("amoxicilline", "J01CA04", strength_value=500, strength_unit="mg", frequency_canonical="3dd1",
             raw_text="amoxicilline 500 mg, om de 8 uur"),
    ],
    truth_b=[
        line("amoxicilline", "J01CA04", strength_value=500, strength_unit="mg", frequency_canonical="3dd1",
             raw_text="amoxicilline 500 mg, 3dd1", source="b"),
    ],
    diffs=[],
)

# ---------------------------------------------------------------------------
# 017 — insulineschema meervoudig
# ---------------------------------------------------------------------------
add(
    "017-insulineschema-meervoudig",
    """# Casus 017 — insulineschema met meerdere insulines

**Edge case:** basaal-bolusschema (glargine 1dd + aspart 3dd) waarbij de bolusinsuline-dosis
in lijst B is gewijzigd. Twee verschillende insulines mogen niet met elkaar matchen (andere
ATC-5 ondanks zelfde ATC-4 A10A).

**Verwacht:** 1 discrepantie (DOSE_CHANGE op aspart), 0 op glargine.
Beide insulines zijn risicomedicatie -> escalatie verplicht op de gewijzigde regel.

**Test wat:** matching op ATC-5 (niet ATC-4) binnen dezelfde stofklasse insuline.
""",
    rows_a=[
        row("insuline glargine", "100 E/ml", "pen", "20 eenheden", "1dd1", route="subcutaan"),
        row("insuline aspart", "100 E/ml", "pen", "8 eenheden", "3dd1", route="subcutaan"),
    ],
    rows_b=[
        row("insuline glargine", "100 E/ml", "pen", "20 eenheden", "1dd1", route="subcutaan"),
        row("insuline aspart", "100 E/ml", "pen", "12 eenheden", "3dd1", route="subcutaan"),
    ],
    truth_a=[
        line("insuline glargine", "A10AE04", strength_unit="100E/ml", dose_value=20, dose_unit="eenheden",
             frequency_canonical="1dd1", route="subcutaan", raw_text="insuline glargine 100E/ml, 20 eenheden, 1dd1"),
        line("insuline aspart", "A10AB05", strength_unit="100E/ml", dose_value=8, dose_unit="eenheden",
             frequency_canonical="3dd1", route="subcutaan", raw_text="insuline aspart 100E/ml, 8 eenheden, 3dd1"),
    ],
    truth_b=[
        line("insuline glargine", "A10AE04", strength_unit="100E/ml", dose_value=20, dose_unit="eenheden",
             frequency_canonical="1dd1", route="subcutaan", raw_text="insuline glargine 100E/ml, 20 eenheden, 1dd1", source="b"),
        line("insuline aspart", "A10AB05", strength_unit="100E/ml", dose_value=12, dose_unit="eenheden",
             frequency_canonical="3dd1", route="subcutaan", raw_text="insuline aspart 100E/ml, 12 eenheden, 3dd1", source="b"),
    ],
    diffs=[
        diff("DOSE_CHANGE", [1], [1], "hoog", True,
             "Insuline aspart van 8 naar 12 eenheden per bolus — risicomedicatie, geen registreerde reden."),
    ],
)

# ---------------------------------------------------------------------------
# 018 — anticoagulantia-switch
# ---------------------------------------------------------------------------
add(
    "018-anticoagulantia-switch",
    """# Casus 018 — anticoagulantia-switch

**Edge case:** acenocoumarol (VKA) in lijst A vervangen door rivaroxaban (DOAC) in lijst B.
Het datamodel kent geen apart type "SWITCH" — dit wordt daarom gedetecteerd als STOPPED +
ADDED, elk apart. Bewust zo gelaten: de triage-laag mag hier eventueel een gecombineerde
weergave van maken, maar dat is fase 3, geen diff-engine-verantwoordelijkheid.

**Verwacht:** 2 discrepanties (STOPPED acenocoumarol, ADDED rivaroxaban), beide escaleren
(antistolling is risicomedicatie).

**Test wat:** dat de engine geen "slimme" switch-detectie doet — dat zou een klinische
interpretatie zijn die niet in de deterministische laag thuishoort (zie CLAUDE.md regel 2).
""",
    rows_a=[
        row("acenocoumarol", "1 mg", "tablet", "volgens doseerschema", "wisselend", gestopt="2026-02-05", reden_stop="switch naar DOAC"),
    ],
    rows_b=[
        row("rivaroxaban", "20 mg", "tablet", "1 tablet", "1dd1", gestart="2026-02-05"),
    ],
    truth_a=[
        line("acenocoumarol", "B01AA07", dose_unit="wisselend", frequency_canonical="wisselend (INR-gestuurd)",
             raw_text="acenocoumarol 1 mg, volgens doseerschema, gestopt: switch naar DOAC"),
    ],
    truth_b=[
        line("rivaroxaban", "B01AF01", strength_value=20, strength_unit="mg", frequency_canonical="1dd1",
             raw_text="rivaroxaban 20 mg, 1dd1", source="b"),
    ],
    diffs=[
        diff("STOPPED", [0], [], "hoog", True,
             "Acenocoumarol gestopt met reden (switch naar DOAC) — antistolling is risicomedicatie, escalatie ter verificatie ondanks geregistreerde reden."),
        diff("ADDED", [], [0], "hoog", True,
             "Rivaroxaban nieuw gestart als vervanger van acenocoumarol — antistolling is risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 019 — lithium, risicomedicatie met echte discrepantie
# ---------------------------------------------------------------------------
add(
    "019-lithium-risicomedicatie",
    """# Casus 019 — lithium dosiswijziging

**Edge case:** lithiumcarbonaat (smalle therapeutische breedte) met een dosiswijziging tussen
lijst A en lijst B. In tegenstelling tot casus 009 (lithium zonder discrepantie) triggert dit
hier onvoorwaardelijk escalatie: risicomedicatie + echte discrepantie.

**Verwacht:** 1 discrepantie, DOSE_CHANGE, hoog, verplichte escalatie.

**Test wat:** samenspel van risicoklasse-escalatie en discrepantie-detectie.
""",
    rows_a=[
        row("lithiumcarbonaat", "400 mg", "tablet", "1 tablet", "2dd1"),
    ],
    rows_b=[
        row("lithiumcarbonaat", "400 mg", "tablet", "2 tabletten", "2dd1"),
    ],
    truth_a=[
        line("lithiumcarbonaat", "N05AN01", strength_value=400, strength_unit="mg", frequency_canonical="2dd1",
             raw_text="lithiumcarbonaat 400 mg, 1 tablet, 2dd1"),
    ],
    truth_b=[
        line("lithiumcarbonaat", "N05AN01", strength_value=400, strength_unit="mg", dose_value=2, frequency_canonical="2dd1",
             raw_text="lithiumcarbonaat 400 mg, 2 tabletten, 2dd1", source="b"),
    ],
    diffs=[
        diff("DOSE_CHANGE", [0], [0], "hoog", True,
             "Lithiumcarbonaat dagdosis verdubbeld (1600mg -> 3200mg/dag) — smalle therapeutische breedte, geen registreerde reden."),
    ],
)

# ---------------------------------------------------------------------------
# 020 — digoxine dosiswijziging
# ---------------------------------------------------------------------------
add(
    "020-digoxine-dosiswijziging",
    """# Casus 020 — digoxine dosiswijziging

**Edge case:** digoxine sterkte gehalveerd (0.25mg -> 0.125mg) — een reductie, niet verhoging;
test dat escalatie niet alleen bij dosisverhoging geldt.

**Verwacht:** 1 discrepantie, STRENGTH_CHANGE, hoog, verplichte escalatie (risicomedicatie).

**Test wat:** dat richting van de wijziging (omlaag) de escalatieregel niet buiten werking stelt.
""",
    rows_a=[
        row("digoxine", "0,25 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("digoxine", "0,125 mg", "tablet", "1 tablet", "1dd1"),
    ],
    truth_a=[
        line("digoxine", "C01AA05", strength_value=0.25, strength_unit="mg", raw_text="digoxine 0,25 mg, 1dd1"),
    ],
    truth_b=[
        line("digoxine", "C01AA05", strength_value=0.125, strength_unit="mg", raw_text="digoxine 0,125 mg, 1dd1", source="b"),
    ],
    diffs=[
        diff("STRENGTH_CHANGE", [0], [0], "hoog", True,
             "Digoxine gehalveerd van 0,25mg naar 0,125mg 1dd1 — risicomedicatie, geen registreerde reden (mogelijk nierfunctie-gerelateerd, te verifiëren door apotheker)."),
    ],
)

# ---------------------------------------------------------------------------
# 021 — opioïdtitratie
# ---------------------------------------------------------------------------
add(
    "021-opioid-titratie",
    """# Casus 021 — opioïdtitratie (fentanylpleister)

**Edge case:** fentanylpleister sterkte opgehoogd (25 -> 50 microgram/uur) — verwachte titratie
bij chronische pijn, maar wel risicomedicatie dus altijd escaleren ter verificatie.

**Verwacht:** 1 discrepantie, STRENGTH_CHANGE, hoog, verplichte escalatie.

**Test wat:** eenheidsnormalisatie voor transdermale afgiftesnelheid (microgram/uur), niet
hetzelfde als een orale sterkte-eenheid.
""",
    rows_a=[
        row("fentanyl", "25 microgram/uur", "pleister", "1 pleister", "om de 72 uur", route="transdermaal"),
    ],
    rows_b=[
        row("fentanyl", "50 microgram/uur", "pleister", "1 pleister", "om de 72 uur", route="transdermaal"),
    ],
    truth_a=[
        line("fentanyl", "N02AB03", strength_value=25, strength_unit="mcg/uur", form="pleister",
             frequency_canonical="om de 72u", route="transdermaal", raw_text="fentanyl 25 microgram/uur pleister, om de 72 uur"),
    ],
    truth_b=[
        line("fentanyl", "N02AB03", strength_value=50, strength_unit="mcg/uur", form="pleister",
             frequency_canonical="om de 72u", route="transdermaal", raw_text="fentanyl 50 microgram/uur pleister, om de 72 uur", source="b"),
    ],
    diffs=[
        diff("STRENGTH_CHANGE", [0], [0], "hoog", True,
             "Fentanylpleister opgehoogd van 25 naar 50 microgram/uur — opioïd is risicomedicatie, altijd verifiëren ondanks aannemelijke titratie."),
    ],
)

# ---------------------------------------------------------------------------
# 022 — methotrexaat weekdosering-fout
# ---------------------------------------------------------------------------
add(
    "022-methotrexaat-weekdosering-fout",
    """# Casus 022 — methotrexaat: weekdosering fout overgenomen als dagdosering

**Edge case:** klassieke, potentieel fatale overdrachtsfout. Lijst A: correct "1x per week".
Lijst B: abusievelijk overgenomen als "1dd1" (dagelijks) — een 7x overdosering.

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, hoogst mogelijke severity, verplichte
escalatie. Dit is een van de sterkste bouwlog-/workshopvoorbeelden: een AI-extractie die
"1dd1" en "1x per week" als plausibele varianten van elkaar zou normaliseren, is precies de
stille fout die regel 4 in CLAUDE.md (geen stille fixes) moet voorkomen.

**Test wat:** dat frequentiecanonicalisatie "1dd1" en "1x/week" nooit samenvoegt, en dat de
diff-engine dit als kritieke FREQUENCY_CHANGE markeert, niet als ruis.
""",
    rows_a=[
        row("methotrexaat", "10 mg", "tablet", "1 tablet", "1x per week, elke maandag", gestart="2025-09-01"),
    ],
    rows_b=[
        row("methotrexaat", "10 mg", "tablet", "1 tablet", "1dd1", gestart="2025-09-01"),
    ],
    truth_a=[
        line("methotrexaat", "L04AX03", strength_value=10, strength_unit="mg", frequency_canonical="1x/week",
             raw_text="methotrexaat 10 mg, 1x per week, elke maandag"),
    ],
    truth_b=[
        line("methotrexaat", "L04AX03", strength_value=10, strength_unit="mg", frequency_canonical="1dd1",
             raw_text="methotrexaat 10 mg, 1dd1", source="b"),
    ],
    diffs=[
        diff("FREQUENCY_CHANGE", [0], [0], "kritiek", True,
             "Methotrexaat frequentie 1x/week (correct) tegenover 1dd1 (bron B) — 7x overdosering indien juist overgenomen; direct escaleren, risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 023 — duplicaat andere ATC-5, zelfde ATC-4 (variant op casus 006)
# ---------------------------------------------------------------------------
add(
    "023-duplicaat-benzodiazepines",
    """# Casus 023 — dubbelmedicatie benzodiazepines (andere stofklasse dan casus 006)

**Edge case:** oxazepam en temazepam (beide ATC-4 N05B/N05C-achtig, valbeleid-relevant bij
ouderen) naast elkaar in lijst B — tweede voorbeeld van ATC-4-duplicaatdetectie, met een
andere farmacologische klasse dan casus 006 om te testen dat de regel generiek is en niet
toevallig alleen op NSAID's werkt.

**Verwacht:** 1 discrepantie, DUPLICATE_THERAPY, hoog, verplichte escalatie.

**Test wat:** generiekheid van de ATC-4-duplicaatregel over meerdere stofklassen.
""",
    rows_a=[
        row("oxazepam", "10 mg", "tablet", "1 tablet", "1dd1 's avonds"),
    ],
    rows_b=[
        row("oxazepam", "10 mg", "tablet", "1 tablet", "1dd1 's avonds"),
        row("temazepam", "10 mg", "tablet", "1 tablet", "1dd1 's avonds", gestart="2026-02-01"),
    ],
    truth_a=[
        line("oxazepam", "N05BA04", strength_value=10, strength_unit="mg", raw_text="oxazepam 10 mg, 1dd1 's avonds"),
    ],
    truth_b=[
        line("oxazepam", "N05BA04", strength_value=10, strength_unit="mg", raw_text="oxazepam 10 mg, 1dd1 's avonds", source="b"),
        line("temazepam", "N05CD07", strength_value=10, strength_unit="mg", raw_text="temazepam 10 mg, 1dd1 's avonds", source="b"),
    ],
    diffs=[
        diff("DUPLICATE_THERAPY", [0], [0, 1], "hoog", True,
             "Oxazepam en temazepam (beide sedativa/hypnotica) tegelijk in lijst B — verhoogd valrisico, met name bij ouderen."),
    ],
)

# ---------------------------------------------------------------------------
# 024 — meervoudige discrepanties, gemengd
# ---------------------------------------------------------------------------
add(
    "024-meervoudige-discrepanties-gemengd",
    """# Casus 024 — meervoudige discrepanties in één patiënt

**Edge case:** realistische overdracht met meerdere gelijktijdige discrepantietypes: één
toegevoegd middel, één gestopt zonder reden, één dosiswijziging, en twee ongewijzigde
middelen als ruis. Test dat de engine per middel onafhankelijk classificeert zonder
kruisbesmetting tussen regels.

**Verwacht:** 3 discrepanties (ADDED, STOPPED, DOSE_CHANGE); 2 middelen zonder discrepantie.

**Test wat:** samengestelde casus dicht bij een echte overdrachtssituatie.
""",
    rows_a=[
        row("amlodipine", "5 mg", "tablet", "1 tablet", "1dd1"),
        row("simvastatine", "40 mg", "tablet", "1 tablet 's avonds", "1dd1"),
        row("pantoprazol", "40 mg", "tablet", "1 tablet", "1dd1", gestopt="2026-02-03"),
        row("metformine", "500 mg", "tablet", "1 tablet", "2dd1"),
    ],
    rows_b=[
        row("amlodipine", "10 mg", "tablet", "1 tablet", "1dd1"),
        row("simvastatine", "40 mg", "tablet", "1 tablet 's avonds", "1dd1"),
        row("metformine", "500 mg", "tablet", "1 tablet", "2dd1"),
        row("candesartan", "8 mg", "tablet", "1 tablet", "1dd1", gestart="2026-02-10"),
    ],
    truth_a=[
        line("amlodipine", "C08CA01", strength_value=5, strength_unit="mg", raw_text="amlodipine 5 mg, 1dd1"),
        line("simvastatine", "C10AA01", strength_value=40, strength_unit="mg", raw_text="simvastatine 40 mg, 1 tablet 's avonds, 1dd1"),
        line("pantoprazol", "A02BC02", strength_value=40, strength_unit="mg", raw_text="pantoprazol 40 mg, 1dd1, gestopt (geen reden geregistreerd)"),
        line("metformine", "A10BA02", strength_value=500, strength_unit="mg", frequency_canonical="2dd1", raw_text="metformine 500 mg, 2dd1"),
    ],
    truth_b=[
        line("amlodipine", "C08CA01", strength_value=10, strength_unit="mg", raw_text="amlodipine 10 mg, 1dd1", source="b"),
        line("simvastatine", "C10AA01", strength_value=40, strength_unit="mg", raw_text="simvastatine 40 mg, 1 tablet 's avonds, 1dd1", source="b"),
        line("metformine", "A10BA02", strength_value=500, strength_unit="mg", frequency_canonical="2dd1", raw_text="metformine 500 mg, 2dd1", source="b"),
        line("candesartan", "C09CA06", strength_value=8, strength_unit="mg", raw_text="candesartan 8 mg, 1dd1", source="b"),
    ],
    diffs=[
        diff("DOSE_CHANGE", [0], [0], "midden", False,
             "Amlodipine van 5mg naar 10mg 1dd1 — geen risicomedicatie, wel te verifiëren."),
        diff("STOPPED", [2], [], "midden", True,
             "Pantoprazol niet meer aanwezig in lijst B, geen stopreden geregistreerd."),
        diff("ADDED", [], [3], "laag", False,
             "Candesartan nieuw gestart, geen risicomedicatie."),
    ],
)

# ---------------------------------------------------------------------------
# 025 — eenheidsnormalisatie mcg/mg
# ---------------------------------------------------------------------------
add(
    "025-eenheidsnormalisatie-mcg-mg",
    """# Casus 025 — eenheidsnormalisatie microgram versus milligram

**Edge case:** levothyroxine in lijst A als "0,1 mg", in lijst B als "100 microgram" —
dezelfde dosis, andere eenheid. Zonder eenheidsnormalisatie lijkt dit een STRENGTH_CHANGE.

**Verwacht:** 0 discrepanties na correcte eenheidsnormalisatie (mg -> mcg).

**Test wat:** eenheidsnormalisatie (mg/g/mcg) uit backlog fase 1, expliciet voor dit
grensgeval (factor 1000, makkelijk fout te normaliseren).
""",
    rows_a=[
        row("levothyroxine", "0,1 mg", "tablet", "1 tablet", "1dd1"),
    ],
    rows_b=[
        row("levothyroxine", "100 microgram", "tablet", "1 tablet", "1dd1"),
    ],
    truth_a=[
        line("levothyroxine", "H03AA01", strength_value=100, strength_unit="mcg", raw_text="levothyroxine 0,1 mg, 1dd1"),
    ],
    truth_b=[
        line("levothyroxine", "H03AA01", strength_value=100, strength_unit="mcg", raw_text="levothyroxine 100 microgram, 1dd1", source="b"),
    ],
    diffs=[],
)


if __name__ == "__main__":
    for casus_id, notes, rows_a, rows_b, truth_a, truth_b, diffs in CASUS:
        write_casus(casus_id, notes, rows_a, rows_b, truth_a, truth_b, diffs)
    print(f"{len(CASUS)} casus geschreven naar {CASUS_DIR}")

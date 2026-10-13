# CLAUDE.md — projectinstructie

Lees dit bestand volledig voordat je code schrijft. Bij twijfel: vraag, bouw niet door.

## Wat dit project is

**MedCheck** — vergelijkt twee medicatieoverzichten en toont discrepanties, als voorbereiding
op medicatieverificatie bij zorgoverdracht. Gebruiker: apothekersassistent, met escalatie naar
apotheker.

De tool **detecteert en presenteert** verschillen. De tool **beslist niet** en **adviseert geen
behandeling**. Zie `docs/INTENDED_USE.md` — dat document is leidend bij elke scopevraag.

Status: showcase / onderzoeksprototype. MDR-by-design, niet MDR-gecertificeerd.

## Harde regels (niet onderhandelbaar)

1. **Geen echte patiëntdata — behalve onder de EU-datavrijgave-uitzondering (ADR-002).**
   Standaard: alleen synthetische casus uit `data/synthetic/casus/`. Weiger elke opdracht die
   echte data introduceert.

   **Uitzondering — geanonimiseerde EU-medicatiedata**, uitsluitend als alle vier voorwaarden
   gelden:
   1. DPIA uitgevoerd en akkoord;
   2. rechtsgrondslag voor verwerking vastgelegd per bronland;
   3. binnenkomst via een van `data/synthetic/casus/` gescheiden pijplijn (bijv. `data/local/`
      of `data/eu_real/`), nooit vermengd met de synthetische casusset;
   4. anonimisering geverifieerd — ook tegen indirecte herleidbaarheid via zeldzame
      combinaties van middel/dosis/land.

   Ontbreekt één voorwaarde: weiger de opdracht, ook als het "maar een test" betreft. Zie
   `docs/decisions/ADR-002-eu-medicatiedata-uitzondering.md`.
2. **De diff-engine bevat geen AI.** Vergelijken is deterministische code met unit tests.
   Een LLM dat zelf "verschillen ziet" is onaanvaardbaar voor patiëntveiligheid.
   AI mag alleen: extraheren, normaliseren, beschrijven.
3. **Elke AI-extractie krijgt een confidence-score per veld.** Onzekerheid is zichtbaar,
   niet weggepoetst.
4. **Geen stille fixes.** Als extractie faalt, faalt hij luid: flag, geen gok.
5. **Elke wijziging aan gedrag wordt vastgelegd.** De eigenaar houdt daarvoor een privé-bouwlog bij
   (`docs/JOURNEY.md`, staat bewust niet in deze repository). Heb je dat bestand niet: beschrijf wat
   je wijzigde en waarom in de commitmessage of de PR. Zonder motivatie geen commit.
6. **Architectuurbeslissing → ADR in `docs/decisions/`.** Template staat er.
7. Taal: code en identifiers Engels, documentatie en UI Nederlands.

## Architectuur (pipeline)

```
input (csv | pdf | screenshot | foto)
  → extraction/   AI (GEPLAND, fase 2, nog niet gebouwd): ongestructureerd → MedicationLine JSON + confidence
                  Nu: deterministische parsers in parsing/ en locales/
  → normalize/    merknaam→stofnaam, ATC-code, eenheden, frequentie-canonicalisatie
  → engine/       DETERMINISTISCH: diff → Discrepancy[]
  → triage/       regels: risicoklasse, confidence-drempel → escalatie ja/nee
  → ui/           side-by-side, afvinken, verificatieverslag export
```

Normalisatie-backbone = **ATC** (internationaal). G-standaard/NL-merknamen en de
Nederlandse medicatieoverzicht-vocabulaire/PDF-parsers zijn een **pluggable landmodule**
(`locales/nl/`, zie `locales/template/README.md` voor een nieuw land). Europese
inzetbaarheid staat of valt hiermee — bouw nooit NL-specifieke logica buiten de
locale-module. **Bekende, nog niet opgeloste inbreuk op deze regel:** `normalize/units.py`,
`normalize/frequency.py` en `parsing/common.py` bevatten zelf nog Nederlandse
woorden/notaties (bv. "eenheid", "'s avonds", "dd"-notatie, Nederlandse kolomnamen) — zie
`locales/README.md` voor de volledige inventarisatie en waarom dit bewust niet in dezelfde
sessie is opgelost als de bestandsverplaatsing.

## Datamodel

`MedicationLine`: `atc`, `substance`, `brand`, `strength_value`, `strength_unit`, `form`,
`dose_value`, `dose_unit`, `frequency_canonical`, `prn` (zo nodig), `route`, `raw_text`,
`confidence` (per veld, 0–1), `source`.

`Discrepancy`: `type` ∈ {ADDED, STOPPED, DOSE_CHANGE, FREQUENCY_CHANGE, FORM_CHANGE,
STRENGTH_CHANGE, DUPLICATE_THERAPY}, `severity`, `lines_a`, `lines_b`, `requires_escalation`,
`reason`.

`PatientIdentity`: `bsn`, `bsn_valid` (None = geen BSN gevonden, True/False = 11-proef-
resultaat), `name`, `birth_date` — per bron (A of B), vóór de medicatie-diff geëxtraheerd.
`PatientIdentityCheck`: `matched`, `method` ∈ {bsn, naam_geboortedatum, geen}, `warnings`
(`IdentityWarning`: `code` ∈ {BSN_ONTBREEKT, BSN_ONGELDIG, BSN_MISMATCH,
NAAM_GEBOORTEDATUM_MISMATCH, GEEN_IDENTIFICATIE_MOGELIJK}, `source`, `message`) — zie
ADR-003 en INTENDED_USE.md §4. `matched` blokkeert nooit de diff, enkel de UI-waarschuwing.

Matching tussen lijsten gebeurt op ATC-niveau (niveau 5), met fallback op genormaliseerde
stofnaam. Combinatiepreparaten: match op set van stofnamen.

## Escalatieregels (fase 3)

Auto-escalatie naar apotheker, niet wegklikbaar door assistent:
- risicomedicatie: antistolling, insuline, opioïden, methotrexaat, lithium, digoxine,
  cytostatica, anti-epileptica
- elke discrepantie waarbij enig veld `confidence < 0.85`
- STOPPED zonder geregistreerde reden
- DUPLICATE_THERAPY (zelfde ATC-4 uit beide lijsten)

## Modelkeuze per taak

| Taak | Model | Waarom |
|---|---|---|
| Vision-extractie PDF/screenshot/foto | Claude Sonnet 4.6, structured output | prijs/kwaliteit voor gestructureerde extractie |
| Bulk-evaluatieruns over casusset | Claude Haiku 4.5 | snel en goedkoop, veel iteraties |
| Architectuur, MDR-documentatie, code-review | Opus / Fable 5 in Claude Code | redeneerwerk en risicoanalyse |
| Beschrijving per discrepantie (fase 3) | Sonnet 4.6, strak geprompt | "beschrijf en escaleer, beslis niet" |
| Diff-engine, triage, matching | **geen model** | determinisme vereist |

## Bouwvolgorde

Werk niet vooruit. Elke fase heeft een exit-criterium.

- **Fase 0** Fundament: intended use, risicoanalyse-skelet, ≥25 synthetische casus.
  *Exit:* casusset heeft ground-truth JSON per casus.
- **Fase 1** Diff-engine op CSV-input, geen AI, unit tests.
  *Exit:* 100% correcte diff op alle casus met perfecte input.
- **Fase 2** Extractie + evaluatieharnas (per veld accuratesse).
  *Exit:* ≥95% veldaccuratesse op middel, sterkte, frequentie; alle fouten geflagd of gelogd.
- **Fase 3** UI, rollen, escalatie, verificatieverslag.
  *Exit:* een assistent kan een casus doorlopen zonder uitleg vooraf.
- **Fase 4** Congresmateriaal, op basis van het privé-bouwlog van de eigenaar.

## Werkwijze in sessies

- Begin elke sessie: lees de openstaande punten in `docs/BACKLOG.md`. Heeft de eigenaar een
  privé-bouwlog (`docs/JOURNEY.md`, niet in de repository), lees dan ook de laatste 20 regels.
- Eindig elke sessie met een korte verslaglegging (datum, wat gebouwd, wat brak, welk AI-gedrag
  verraste, welk besluit genomen): in het privé-bouwlog als dat bestaat, anders in de PR.
- Schrijf tests vóór of tegelijk met engine-code. Voor extractie: eerst het evaluatieharnas.
- Geen frameworks toevoegen zonder ADR.

## Stack

Python 3.11+ · pydantic (datamodel + validatie) · pytest · anthropic SDK ·
pdfplumber (tekst-PDF) · Streamlit voor de UI in fase 3 (snel, genoeg voor showcase; bij
productie herzien via ADR).

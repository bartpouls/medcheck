# MVP-opzet — fase 1 diff-engine

Status: concept · basis voor bouwsessie · afgeleid uit CLAUDE.md, INTENDED_USE.md v1.0,
BACKLOG.md fase 1, WORKSHOP_26AUG.md, ADR-001.

## Scope-bepaling

MVP = fase 1 uit CLAUDE.md: **deterministische diff-engine op CSV- en tekst-PDF-input, geen AI
in de diff zelf, aanroepbaar via een minimale upload-UI, geen verificatie-UI.**
Exit-criterium (ongewijzigd overgenomen): 100% correcte diff op alle 25 casus met perfecte
input (CSV of tekst-PDF, geen extractie-onzekerheid).

**Wel** in deze MVP, als uitbreiding op CSV-only:
- **Tekst-PDF-input** (selecteerbare tekst, tabel/lijst-achtig — bv. EPD-/apotheeksysteemexport):
  parsen met `pdfplumber`, **geen AI**. Dit blijft binnen ADR-001/CLAUDE.md regel 2, omdat het
  geen extractie uit ongestructureerde vrije tekst is maar tekst-onttrekking uit een vaste
  lay-out, gevolgd door dezelfde parsing-/normalisatiestap als CSV.
- **Minimale upload-UI** om twee bestanden te koppelen: Streamlit-app met twee file-uploaders
  (bestand A, bestand B), een knop "vergelijk", en de gevonden discrepanties als lijst/tabel
  eronder. Geen afvinken, geen escalatieregels, geen verificatieverslag-export, geen
  rolonderscheid — dat blijft fase 3. Dit scherm is puur invocatie (bestanden aanwijzen, diff
  tonen), geen scope-vooruitloop op de verificatie-UI.

Expliciet **niet** in deze MVP (fase 2/3, of buiten scope per INTENDED_USE.md §5):
- vrije-tekst PDF (ontslagbrief-/telegramstijl, CASUS_FORMAAT_PROMPTS.md groep 2/5) en
  gescande/foto-PDF — vereisen AI-(vision-)extractie, dat is fase 2. Casus 006–010, 021–025 en
  de foto-casus (011–020) draaien in de MVP dus vanaf `source_a.csv`/`source_b.csv`, niet vanaf
  hun `formats/`-variant.
- confidence-scores, escalatieregels, verificatie-UI — die veronderstellen extractie-onzekerheid,
  die bij tekst-PDF/CSV niet bestaat
- elke vorm van klinisch oordeel (bedoeld/onbedoeld, behandeladvies) — buiten scope van het hele
  product, niet alleen van de MVP

## Openstaand vóór bouwstart (blokkerend of risicovol als genegeerd)

1. **25 casus medisch-inhoudelijk reviewen** — nog niet gedaan (BACKLOG.md, JOURNEY 2026-08-25).
   Ground truth is nog AI-gegenereerd. Besluit: bouwen gaat pragmatisch door tegen de huidige
   `expected_diff.json`, expliciet gelogd als open risico in JOURNEY.md — niet blokkerend voor
   de bouwsessie, wel voor "af".
2. **Codeine-ATC-code voor pijnstillergebruik** — R05DA04 verwijderd zonder vervanging
   (BACKLOG.md). Blokkeert alleen volledige opioïden-dekking, niet de rest van de engine.
3. **STRENGTH_CHANGE-classificatie bevestigen** — moet 1x STRENGTH_CHANGE zijn, niet een
   ADDED+STOPPED-paar (INTENDED_USE.md v0.3, BACKLOG.md fase 1). Kernregel, eerst vastzetten
   voordat de diff-regels geschreven worden — een latere herclassificatie raakt elke test.
4. **GitHub-repo** — WORKSHOP_26AUG.md noemt dit als vereiste vooraf-punt, bewust uitgesteld.
   Geen technische blocker voor lokaal bouwen, wel voor delen/samenwerken.

## Modules (volgorde = bouwvolgorde, elke stap eindigt groen)

```
medcheck/
  models.py          MedicationLine, Discrepancy (pydantic)
  parsing/
    csv.py            CSV → MedicationLine[], kolomvolgorde-onafhankelijk (zie CASUS_FORMAAT_PROMPTS.md groep 1)
    pdf_text.py        Tekst-PDF → dezelfde structuur als csv.py, via pdfplumber, geen AI
  ui/app.py            Streamlit: twee file-uploaders, knop "vergelijk", discrepanties als lijst/tabel
  normalize/
    frequency.py      "3dd1" | "3x daags" | "om de 8 uur" | "q72u" → canonieke vorm
    units.py           mg/g/mcg, ml, IE → canonieke eenheid
    locales/nl.py       merknaam → stofnaam, NL-specifiek (CLAUDE.md: nooit buiten deze module)
  matching.py          ATC-5 matching, fallback stofnaam, combipreparaat → stofnaamset
  engine/
    diff.py             regels per Discrepancy.type
    duplicates.py       ATC-4 duplicaatdetectie
  reference/           atc_subset.json, high_risk.json (al aanwezig, deels ongeverifieerd — zie punt 1/2)
tests/
  test_casus_<id>.py of parametrized test over data/synthetic/casus/*/expected_diff.json
```

### 1. Datamodel (`models.py`)
Exact zoals gespecificeerd in CLAUDE.md — geen velden toevoegen die fase 2/3 vooruitlopen
(bijv. geen `confidence`-gebruik in fase 1, wel het veld laten bestaan voor forward-compat met
fase 2's schema).

### 2. CSV-parser en tekst-PDF-parser
CSV: alleen `data/synthetic/casus/*/source_a.csv` / `source_b.csv` (fase 1-fixtures). Tekst-PDF: Bart
levert de tabel-achtige PDF-fixtureset zelf aan (geen vrije tekst) — de bestaande `formats/`-PDF's
uit CASUS_FORMAAT_PROMPTS.md groep 2/5 zijn vrije-tekst en dus niet bruikbaar als MVP-fixture; die
blijven gereserveerd voor fase 2. `pdf_text.py` wordt gebouwd zodra deze fixtures beschikbaar
zijn. Beide parsers leveren dezelfde `MedicationLine[]`-vorm op, zodat normalisatie/matching/diff
bestandstype-onafhankelijk zijn.

### 3. Upload-UI (`ui/app.py`)
Dunne Streamlit-laag: twee file-uploaders, detecteert bestandstype op extensie, roept de juiste
parser aan, voert normalisatie → matching → diff → duplicaatcheck uit en toont de discrepanties
als tabel, plus een downloadknop (`st.download_button`) voor diezelfde tabel als JSON/CSV — ruwe
export, geen verificatieverslag. Geen state tussen sessies, geen afvinken, geen escalatie — die
logica hoort in de engine-modules, niet in de UI-laag, zodat fase 3 dit scherm kan uitbreiden
zonder de engine aan te raken.

### 4. Normalisatie
Frequentie en eenheden eerst, apart getest, vóór matching — matching-bugs zijn onmogelijk te
debuggen als normalisatie nog fout kan zijn.

### 5. Matching
ATC-5 primair, stofnaam-fallback. Combipreparaat: ontleed naar stofnaamset (casus 002 in
CASUS_FORMAAT_PROMPTS.md is het referentievoorbeeld).

### 6. Diff-regels
Eén regel per `Discrepancy.type`. Matching-key bevat **geen** sterkte/dosis/frequentie — alleen
stof (of stofnaamset bij combipreparaat), vorm en route; dat zijn precies de velden die je ná het
matchen per gematcht paar vergelijkt. Ongematchte regel alleen-in-A → STOPPED, alleen-in-B →
ADDED. Bij een gematcht paar: sterkte anders → STRENGTH_CHANGE, dosis anders → DOSE_CHANGE,
frequentie anders → FREQUENCY_CHANGE, vorm anders → FORM_CHANGE — als meerdere velden tegelijk
wijzigen (casus 024), levert dat meerdere aparte `Discrepancy`-objecten op dezelfde
`lines_a`/`lines_b`, niet één samengevoegde blob (houdt types apart telbaar, relevant voor de
tellertjes-wens in BACKLOG.md nice-to-have). Elke regel direct tegen de bijbehorende casus
testen — niet alle regels eerst schrijven en dan pas testen.

### 7. Duplicaatdetectie
ATC-4, apart van de hoofd-diff (los toetsbaar, casus 023).

### 8. Tests
Eén test per casus tegen `expected_diff.json` (CSV-pad), plus losse unit tests per
normalisatiefunctie. Voor het tekst-PDF-pad apart: parsertest die verifieert dat `pdf_text.py`
op de nieuwe tabel-achtige PDF-fixtures (stap 2) dezelfde `MedicationLine[]` oplevert als de
CSV-variant van diezelfde casus — dat isoleert parserfouten van diff-fouten. De Streamlit-laag
zelf blijft dun genoeg om buiten de geautomatiseerde tests te houden (geen UI-testframework in de
MVP); de onderliggende functie die `ui/app.py` aanroept (parser → normalisatie → matching → diff)
wordt wél end-to-end getest, los van Streamlit. Rode/groene status is het enige
acceptatiecriterium — geen "ongeveer goed".

## Wat de engine bewust NIET beslist (ADR-001, INTENDED_USE §5)

Geen AI in dit pad. Elke poging om een discrepantie te "wegen" op klinische relevantie
(bijv. "dit is waarschijnlijk een fout, dus...") hoort niet in `engine/` — dat is fase 3/
mensenwerk. Signaal om op te letten tijdens het bouwen (WORKSHOP_26AUG.md): Claude die uit
behulpzaamheid heuristieken voorstelt die eigenlijk klinische beslissingen zijn.

## Volgende stap

Zodra bovenstaande openstaande punten (vooral 1 en 3) zijn afgehandeld: bouwsessie starten
volgens het blokschema in `docs/WORKSHOP_26AUG.md`, beginnend bij `models.py`.
</content>
</invoke>

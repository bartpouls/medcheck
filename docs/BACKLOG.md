# Backlog

Status: [ ] open · [~] bezig · [x] klaar. Verplaats niets naar een latere fase zonder ADR.

## Fase 0 — fundament (vóór 25 aug)
- [x] Intended use statement afronden en dateren — v1.0, akkoord Bart Pouls 2026-07-27
- [x] Risicoanalyse startlijst doorlopen, eigen aanvullingen — R13/R14 toegevoegd (basis v1.0 §4/§5),
      E/K-scores bevestigd door Bart (2026-08-25): R13 4×3=12, R14 5×3=15
- [x] 25-30 synthetische casus met ground-truth JSON — 25 stuks gegenereerd, **nog niet medisch-inhoudelijk gereviewd**
- [x] Casus-generator script (Claude genereert, jij reviewt medisch-inhoudelijk) — `scripts/generate_casus.py`
- [x] ATC-referentietabel (172 middelen) in data/reference/ — Bart's eigen steekproef gedaan
      (2026-08-25): "willekeurig gecheckt, klopt". **Uitzondering:** de 4 op 2026-08-25
      toegevoegde middelen (capecitabine, tacrolimus, ciclosporine, mycofenolaat mofetil) vielen
      buiten deze steekproef en zijn nog ongeverifieerd — kort meenemen in een vervolgcheck.
- [x] Risicomedicatielijst (high_risk.json) — Bart's eigen steekproef gedaan (2026-08-25): "klopt",
      met vier gevonden en gecorrigeerde fouten: opioïden-ATC-regel (R05DA04 onterecht als
      triggercode voor codeine-als-pijnstiller), cytostatica-voorbeelden tamoxifen/letrozol
      (verkeerde ATC-prefix, L02 i.p.v. L01), antipsychotica ontbrak als categorie, immunomodulantia
      (azathioprine e.a.) ontbrak als categorie. Zie JOURNEY.md 2026-08-25 voor volledige diff.
- [ ] Codeine: correcte ATC-5-code(s) voor codeine-als-pijnstiller bepalen — R05DA04 (hoestmiddel-
      indicatie) is verwijderd zonder vervanging; codeine triggert nu alleen nog via stofnaam-
      fallback in `high_risk.json`. **Blokkerend voor volledige opioïden-dekking, niet voor de
      workshop zelf.**
- [ ] Repo op GitHub, VS Code + Claude Code werkend — lokaal git-repo + venv + deps werken;
      GitHub-remote bewust uitgesteld, nog onduidelijk hoe "officieel" dit project wordt.
      **Let op: WORKSHOP_26AUG.md noemt dit als vereiste vooraf-punt — met de workshop op 26
      augustus moet uitstel vandaag een bewuste keuze worden, geen automatisme meer.**
- [x] JOURNEY.md eerste entry — inmiddels 6 sessie-entries, zie docs/JOURNEY.md
- [x] Related work-scan (te laat uitgevoerd) — pas gedaan bij GitHub-publicatievoorbereiding
      (2026-08-26), niet vóór de eerste werkende versie. Resultaat: `RELATED_WORK.md`.
      Zie `docs/JOURNEY.md` 2026-08-26 voor het leermoment. Vult ook fase 4's openstaande
      "Prior-art-check voor MedCheck zelf" gedeeltelijk in — die blijft open voor de
      bredere GitHub-zoekactie.

## Fase 1 — diff-engine (25 aug, ochtend)
- [x] pydantic-model MedicationLine en Discrepancy — `models.py`. Let op: twee extra velden
      (`stop_date`, `stop_reason`) toegevoegd t.o.v. CLAUDE.md's veldenlijst, nodig voor de
      STOPPED-escalatieregel; Bart akkoord nodig of dit in CLAUDE.md overgenomen wordt.
- [x] CSV-parser (medicatierol-formaat) — `parsing/csv_parser.py`, kolomvolgorde-/
      taal-onafhankelijk (ondersteunt zowel de NL- als de EN-headerset uit de casusset)
- [x] Frequentiecanonicalisatie ("3dd1", "3x daags", "om de 8 uur" -> canoniek) —
      `normalize/frequency.py`, core (doseerinstructie) en modifier (gebruiksinstructie)
      expliciet gescheiden per INTENDED_USE.md §4
- [x] Eenheidsnormalisatie (mg/g/mcg, ml, IE) — `normalize/units.py`, incl. een deterministische
      titratieschema-extractie ("nu week N") voor casus 003
- [x] Matching op stofnaam (met merknaam-fallback via de NL-landmodule) — `matching.py`.
      Let op: ATC-5-matching zoals oorspronkelijk hier genoemd bleek niet nodig/haalbaar
      gezien de referentiedata; matcht nu op genormaliseerde stofnaam + route, sterkte/
      dosis/vorm worden ná het matchen vergeleken (vorm zat aanvankelijk fout in de
      matching-key, zie JOURNEY.md 2026-08-26)
- [x] Diff-regels per discrepantietype — `engine/diff.py`
- [x] Diff-regel: sterktewijziging (oude sterkte stopt, nieuwe start) classificeren als 1x
      STRENGTH_CHANGE, niet als los ADDED+STOPPED-paar — zie INTENDED_USE.md v0.3.
      Casus 024 is hier een bekende, nog te reviewen ground-truth-uitzondering (xfail).
- [x] Unit tests per casus — `tests/test_casus.py`, parametrized, 24/25 casus groen
      (casus 001 uitgesloten, casus 024 xfail — beide met reden gelogd)
- [x] Combipreparaat-ontleding — `normalize/locales/nl.py:COMBO_BRANDS`, klein en
      uitbreidbaar (nu alleen Exforge, per de huidige casusset)
- [x] Duplicaatdetectie — bleek NIET haalbaar op kale ATC-4-prefix (zie JOURNEY.md
      2026-08-26 voor de volledige onderbouwing); vervangen door een expliciete
      therapeutische-klassetabel `data/reference/duplicate_classes.json`, zelfde
      concept/ongeverifieerd-status als de bestaande referentiebestanden — Bart's
      steekproef hier ook nog nodig
- [x] Tekst-PDF-pad — `parsing/pdf_text.py` (tabel + kommagescheiden tekst) en
      `parsing/prose_nl.py` (sjabloon-specifieke ontslagbrief-parser, Sint Barbara
      Ziekenhuis-formaat). Geverifieerd tegen echte PDF's in casus 002/006/007/008/013/017.
      Casus 009/010 nog met oude lege placeholder-PDF's, bewust overgeslagen — Bart
      vervangt met casus uit echte systemen.
- [x] Generieke, vocab-gedreven PDF-parser — `parsing/generic_nl.py` +
      `parsing/nl_medication_vocab.py` (NHG/KNMP-begrippenset), vervangt de eerdere
      losse `parsing/hix.py`/`parsing/cgm_apotheek.py` (casus 026/027, testpatiënten;
      zie JOURNEY.md 2026-08-26 sessie 8 (bouw) en sessie 9 (samenvoeging)). Extractie
      geverifieerd, ground truth nog niet — zie punt hieronder.
- [ ] CLAUDE.md regel 4 — Bart gaf aan het er niet meer mee eens te zijn (sessie 9).
      Bewust nog NIET zelf aangepast; mijn lezing (breder vocabulaire ≠ gokken, wel een
      reële verzwakking in de sectie-einde-heuristiek) staat in JOURNEY.md 2026-08-26
      sessie 9 onder "Besluit" — Bart's bevestiging/concrete formulering nodig, net als
      destijds bij regel 1/ADR-002.
- [ ] Casus 026/027 ground truth — human check door Bart op de daadwerkelijke
      discrepanties tussen HIX en CGM Apotheek per testpatiënt, dan
      `truth_a/b.json`/`expected_diff.json` toevoegen. Voorlopige, ongeverifieerde
      engine-output staat als uitgangspunt in de notes.md van beide casus.
- [ ] Casus 009/010 — nog met oude lege placeholder-PDF's, bewust uitgesteld tot na
      026/027 (Bart's verzoek 2026-08-26).
- [x] Minimale upload-UI — `ui/app.py` (Streamlit), draait op localhost:8511, door Bart
      zelf getest tegen meerdere casus. Sinds sessie 13 (2026-08-28): "Was"/"Wordt"
      i.p.v. "Bron A"/"Bron B", incl. de identiteitswaarschuwingen in `identity.py`.

## Nieuwe bronsystemen (toegevoegd 2026-08-28, sessie 12-14)
- [x] ASP-tabelexport (openbare apotheek, casus 028) — koprij-detectie verruimd
      voor titelrij-los-van-koprij-sjablonen, `_header_row_field_map`-inversiebug
      gefixt, "." → expliciet "geen dosering geregistreerd", "maal" als synoniem
      voor "x". Stofnaam/sterkte/vorm/dosering-leegte bevestigd tegen echte bytes.
- [ ] ASP-tabelexport: kolomvermenging route/toelichting/voorschrijver in het
      positionele pad (`locales/nl/pdf_parser.py::_parse_positional`/
      `_find_word_label_anchors`) — Toelichting-kolom heeft geen kolomlabel en "valt"
      in Dosering, en het anker voor een tweewoordig koplabel ("Actuele
      Voorschrijver") ligt te ver naar rechts. Zichtbaar fout, niet stilzwijgend,
      maar nog niet gefixt. Zie `data/local/casus/028.../notes.md`.
- [x] ASP patiëntportaaloverzicht ("Uw medicatie", casus 029) — nieuwe parser
      `locales/nl/patient_portal_parser.py` gebouwd en unit-getest. **Akkoord Bart
      (2026-08-28)** op de aanname dat een "Stop deze medicatie"-regel zonder
      datum/reden wél in de output komt (leeg stop_date/stop_reason, escaleert via
      bestaande triage-regel) i.p.v. uitgesloten wordt.
      **Blijkt niet toepasbaar op het aangeleverde bronbestand** (sessie 16,
      `scripts/diagnose_pdf_layout.py`): dat "Uw medicatie"-overzicht staat op
      pagina 1-2 van een 3-pagina's-PDF als ingesloten AFBEELDING (0 tekens
      doorzoekbare tekst, ~88% van de pagina één image) — geen tekst-parseerbaar
      probleem, valt buiten fase 1 (vision-extractie nodig, fase 2, met ADR-002-
      implicaties bij echte patiëntdata). Parser blijft staan voor een eventuele
      écht tekst-gebaseerde bron met hetzelfde sjabloon. Zie
      `data/local/casus/029.../notes.md`.
- [ ] Zelfde bronbestand, pagina 0 (AMO/tabel-weergave, wél 1043 tekens échte
      tekst): nog steeds niet herkend door de generieke parser (0 kolomankers) —
      een apart, nog te onderzoeken vocabulaireprobleem, los van het
      afbeeldingsvraagstuk hierboven. Kolomkop-tekst van die tabel nog nodig om
      verder te komen (zelfde aanpak als casus 028).

## Patiëntidentiteitscontrole (toegevoegd 2026-08-26, ADR-003)
- [x] BSN-elfproef, generieke identiteitsvergelijking (BSN primair, naam+geboortedatum-
      fallback, nooit blokkerend) — `locales/nl/patient_id.py`, `identity.py`, gewired
      door `compare.py`/`ui/app.py`. Dekt het CSV-pad en de twee generieke tabel/tekst-
      PDF-paden (`_rows_from_table`/`_rows_from_text` in `parsing/pdf_text.py`).
- [ ] Patiëntidentiteit-extractie voor het briefsjabloon-PDF-pad
      (`locales/nl/prose_parser.py`) — laaghangend fruit: de koptekst heeft een vaste
      `Patiënt: <naam>` / `Geboortedatum: dd-mm-jjjj` regel (zie casus 006-008), geen
      BSN in dit sjabloon. Zelfde regex-aanpak als de rest van dat bestand, geen
      structurele belemmering.
- [ ] Patiëntidentiteit-extractie voor het vocab-gedreven PDF-pad
      (`locales/nl/pdf_parser.py`) — bewust NIET meegenomen bij ADR-003 (2026-08-26),
      op basis van de twee echte testpatiënt-PDF's in `data/local/casus/026.../`:
      HIX' koptekst is een meerkolommenlayout die bij platte tekstextractie door
      elkaar loopt (vereist dezelfde x/y-positionele aanpak als nu al voor de
      medicatietabel, maar dan op de koptekst — nieuwe logica, geen hergebruik) en het
      BSN-veld staat er in die praktijkfixture leeg bij; CGM Apotheek gebruikt een
      compleet andere koptekst (ander label voor de naam, andere datumnotatie, geen
      zichtbaar BSN-veld). Op basis van deze 2 sterk uiteenlopende samples nu al een
      generieke koptekst-extractor bouwen is gokken naar wat generiek genoeg is —
      zelfde afweging als eerder bij de normalize/parsing-ontkoppeling
      (`locales/README.md`). Oppakken zodra er een derde praktijkvoorbeeld is om tegen
      te toetsen, of zodra Bart besluit dat 2 samples genoeg basis zijn.
- [x] INTENDED_USE.md v1.1 (§4-aanvulling patiëntidentiteitscontrole) — akkoord Bart
      Pouls 2026-08-26, document weer definitief.
- [x] CLAUDE.md's "Datamodel"-sectie aangevuld met `PatientIdentity`/
      `PatientIdentityCheck` — akkoord Bart Pouls 2026-08-26.

## Fase 2 — extractie + evaluatie (25 aug, middag + sept)
- [ ] Evaluatieharnas: per veld accuratesse tegen ground truth
- [ ] Extractieprompt v1 + structured output schema
- [ ] PDF-tekst pad (pdfplumber) vs vision pad, beslissen via meting
- [ ] Confidence per veld
- [ ] Foutanalyse: top-5 foutcategorieen documenteren in JOURNEY
- [ ] Regressietest: casusset draait automatisch bij elke wijziging

## Fase 3 — UI en escalatie (september)
- [ ] Streamlit side-by-side, bron naast output
- [ ] Afvinken per discrepantie: bedoeld / onbedoeld / onduidelijk
- [ ] Escalatieregels en apothekersweergave
- [ ] Verificatieverslag export (md of pdf) met audit trail
- [ ] Waarschuwing "geen echte patientdata"
- [x] VALIDATION.md invullen met gemeten cijfers — vervroegd naar 2026-08-26
      (GitHub-publicatievoorbereiding) i.p.v. pas in fase 3: per-discrepantietype
      gevonden/gemist/vals-alarm op de synthetische casusset. AI-extractie-veldaccuratesse
      (het eigenlijke fase 2-exit-criterium) staat nog als "nog niet gemeten" in
      `VALIDATION.md` — dat is wél nog open.

## Fase 4 — congres (oktober)
- [ ] Workshopdraaiboek 120 min uitwerken
- [ ] Hosted demo of lokale kloon-instructie voor deelnemers
- [ ] 3 opzettelijk falende casus als leermoment
- [ ] Slides uit JOURNEY.md
- [ ] Prior-art-check voor MedCheck zelf — nooit gedaan (les uit workshop 26 aug, zie
      `docs/WORKSHOP_12OKT.md` "Lessen uit de workshop van 26 augustus"); alsnog uitvoeren op
      GitHub en resultaat loggen in JOURNEY.md. Ook bruikbaar als concreet voorbeeld in de
      workshop van 12 oktober (les 1).

## Nice to have (bewust geparkeerd)
- [ ] Foto van verpakking -> identificatie middel + sterkte
- [ ] Interactiecheck
- [ ] Tweede landmodule (BE of DE) als EU-bewijs
- [ ] Tellertjes discrepanties in UI (totaal, gestart, dosering gewijzigd, gestopt) — hangt af van
      de STRENGTH_CHANGE-classificatie hierboven, anders tellen sterktewijzigingen dubbel

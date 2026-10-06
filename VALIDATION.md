# Validatie

Wat hieronder staat is gemeten, met de commando's om het zelf te reproduceren. Wat niet
gemeten is, staat expliciet als "nog niet gemeten" — geen schatting.

**Reproduceren:** `python scripts/validate.py` (schrijft een rapport per discrepantietype),
of `pytest tests/test_casus.py -v` voor de ruwe pytest-output.

## Wat er getest is

24 van de 25 synthetische casus in `data/synthetic/casus/` hebben een `expected_diff.json`
en zijn tegen de diff-engine getest via CSV-input (`tests/test_casus.py`). Casus
001-merknaam-vs-stofnaam is uitgesloten: `source_a.csv`/`expected_diff.json` gebruiken een
ander, niet-compatibel schema (representation-diff, geen `Discrepancy`-vergelijking) en zijn
niet in deze testrun meegenomen.

**Dit meet de diff-engine op schone, handmatig samengestelde CSV-input — niet de
AI-extractiestap.** Een casus die hier slaagt, zegt niets over hoe de engine presteert op
een echte, rommelige PDF- of foto-extractie met extractiefouten.

## Resultaat per discrepantietype (gemeten 2026-08-26)

| Type | Dekkende casus | Resultaat |
|---|---|---|
| ADDED | 011 | geslaagd |
| STOPPED (met reden) | 012 | geslaagd |
| STOPPED (zonder reden, verplichte escalatie) | 007 | geslaagd |
| DOSE_CHANGE | 003, 017, 020, 021 | geslaagd |
| FREQUENCY_CHANGE | 013, 015, 016 | geslaagd |
| FORM_CHANGE | 005 | geslaagd |
| STRENGTH_CHANGE | 014, 025 (eenheidsnormalisatie mcg/mg) | geslaagd |
| DUPLICATE_THERAPY | 006, 023 | geslaagd |
| Geen discrepantie (true negative) | 008, 009, 010 | geslaagd |
| Combinatiepreparaat-matching | 002 | geslaagd |
| Zo-nodig vs. vast schema | 004 | geslaagd |
| Risicomedicatie-escalatie (antistolling, lithium, digoxine, opioïden, methotrexaat) | 018, 019, 020, 021, 022 | geslaagd |
| Meervoudige discrepanties op één regel | 024 | **xfail — bekende ground-truth-fout, geen enginefout** |

**23 van 24 bruikbare casus slagen exact tegen ground truth.** De ene uitzondering (024) is
gedocumenteerd in `tests/test_casus.py` als een inconsistentie in de fixture zelf (een
sterktewijziging is per ongeluk als DOSE_CHANGE gelabeld i.p.v. STRENGTH_CHANGE, in
tegenspraak met de andere 8 sterkte/dosis-casus) — geen falende engine-logica. Zolang dit
niet gecorrigeerd is, telt casus 024 niet mee als bewijs dat de engine dit geval goed
afhandelt.

## Wat de tool aantoonbaar mist of niet dekt

- **Ongematchte regels:** de matching-fallback (ATC-5 → genormaliseerde stofnaam) is niet
  los gestress-test op fuzzy/foutieve stofnamen buiten de 25 casus. Hoeveel regels bij
  echte, rommelige input onterecht ongematcht blijven — nog niet gemeten.
- **Casus 024-type situaties** (meerdere discrepantietypen op dezelfde regel) hebben één
  bekende ground-truth-fout; de engine zelf is hier niet apart bevestigd correct.
- **Combinatiepreparaten met gedeeltelijke overlap** (bv. twee van drie stoffen matchen):
  niet gedekt door de huidige casusset.

## Wat helemaal niet gemeten is

- **Veldaccuratesse van AI-extractie** (merk/stofnaam, sterkte, frequentie) op PDF/foto-input.
  Dit is het expliciete fase 2-exit-criterium in `CLAUDE.md` (≥95% veldaccuratesse) — er is
  nog geen evaluatieharnas dat dit meet. `eval/` bestaat als lege map, geen resultaten.
- **Sensitiviteit/specificiteit op de praktijkcasus** 026/027 (echte HIX/CGM-exports,
  `data/local/casus/`): de extractie is functioneel getest (`tests/test_praktijkcasus_extractie.py`,
  loopt alleen lokaal), maar de klinische ground truth (welke gevonden verschillen
  daadwerkelijk discrepanties zijn) is nog niet vastgesteld — zie `notes.md` in beide
  casusmappen. Geen cijfers totdat die human check klaar is.
- **Fout-positief-percentage** (ten onrechte gemelde discrepantie) op realistische,
  variabele invoer buiten de 25 synthetische casus.
- **Prestatie op andere talen/landmodules.** Alleen `locales/nl/` bestaat; er is geen andere
  locale om tegen te valideren. Zie ook: de kern (`normalize/units.py`, `normalize/frequency.py`,
  `parsing/common.py`) bevat zelf nog Nederlandse woorden/notaties — nog niet volledig
  taal-agnostisch, zie `locales/README.md`.
- **Interbeoordelaarsbetrouwbaarheid** van de synthetische ground truth zelf (één
  samensteller, geen tweede reviewer per casus, behalve waar `notes.md` dat vermeldt).

## Voor een overnemende partij

Deze cijfers zijn niet overdraagbaar naar een andere instelling zonder eigen validatie:
andere brondocumenten, ander G-standaard-versiegebruik, andere extractiekwaliteit. Zie
`SAFETY.md` voor wat een organisatie zelf moet doen vóór inzet.

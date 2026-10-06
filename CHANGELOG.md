# Changelog

Formaat volgens [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/). Dit project
is pre-1.0: output en interface kunnen tussen versies breken zonder deprecatiepad.

## [0.1.0] — 2026-08-26

Eerste versie die als publiceerbare repository is voorbereid.

### Toegevoegd
- Diff-engine (fase 1): CSV-input, deterministisch, geen AI (ADR-001). 23/24 bruikbare
  synthetische casus slagen exact tegen ground truth — zie `VALIDATION.md`.
- Tekst-PDF-extractie voor Nederlandse medicatieoverzichten (vocab-gedreven, NHG/KNMP-
  begrippenset) en het Sint Barbara Ziekenhuis-briefsjabloon.
- Triage-/escalatieregels voor risicomedicatie, STOPPED-zonder-reden en
  DUPLICATE_THERAPY.
- Minimale Streamlit-UI (`ui/app.py`) voor upload en vergelijking.
- `locales/nl/` — Nederlandse landmodule losgetrokken van de kern (nog niet volledig,
  zie `locales/README.md`).
- `data/local/` / `data/synthetic/` datascheiding: echte systeemexports (praktijkcasus
  026/027) nooit gecommit, alleen synthetische casus in de repository.
- `SAFETY.md`, `VALIDATION.md`, `scripts/validate.py` voor inzetvoorwaarden en gemeten
  (en expliciet niet-gemeten) prestaties.
- Licentie: Apache-2.0.

### Bekende beperkingen
- Fase 2 (AI-extractie met per-veld confidence) en fase 3 (rollen, verificatieverslag)
  nog niet gebouwd — zie `docs/BACKLOG.md`.
- `normalize/units.py`/`normalize/frequency.py`/`parsing/common.py` bevatten nog
  Nederlandse aannames buiten `locales/nl/` — zie `locales/README.md`.
- Casus 024 heeft een bekende, ongecorrigeerde ground-truth-inconsistentie (xfail).

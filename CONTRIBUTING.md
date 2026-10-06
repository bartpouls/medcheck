# Bijdragen

MedCheck is een onderzoeks- en onderwijsprototype (`docs/INTENDED_USE.md`), pre-1.0.
Lees dat document en `SAFETY.md` voordat je een wijziging voorstelt die de scope raakt.

## Harde regels — niet onderhandelbaar

Zie `CLAUDE.md` voor de volledige lijst. De belangrijkste voor bijdragers:

1. **Geen echte patiëntdata**, behalve onder de ADR-002-uitzondering (DPIA, eigen
   pijplijn, geverifieerde anonimisering). Twijfel je: vraag het eerst, dien geen PR in.
2. **De diff-engine (`engine/`) bevat geen AI.** Vergelijken is deterministische code
   met unit tests. Stel geen wijziging voor die een LLM zelf discrepanties laat bepalen.
3. **Geen stille fixes.** Als extractie/parsing faalt, moet dat luid falen (een
   exception, geen gok naar een plausibele waarde).
4. **Elke gedragswijziging wordt gemotiveerd in de PR-beschrijving.** Bart houdt zelf een
   privé-bouwlog bij (niet in deze repository) — beschrijf voor een PR wat je wijzigde
   en waarom, alsof die log er niet is.
5. **Een architectuurbeslissing krijgt een ADR** in `docs/decisions/` (sjabloon:
   `docs/decisions/ADR-000-template.md`).
6. **Taal:** code en identifiers Engels, documentatie en UI Nederlands — behalve
   locale-specifieke terminologie die inherent in de doeltaal van die locale hoort.

## Voordat je een PR opent

- `pytest` moet slagen. Nieuwe engine-/matching-/normalisatielogica krijgt een test
  vóór of tegelijk met de code, niet erna.
- Nieuwe synthetische casus: volg `docs/CASUS_FORMAAT_PROMPTS.md`, zet ze in
  `data/synthetic/casus/`. Nooit in `data/local/` — dat pad is voor bronsysteemdata en
  wordt nooit gecommit (`.gitignore`).
- Een wijziging aan `normalize/`, `matching.py` of `engine/` die de uitkomst van
  bestaande casus verandert: motiveer dat expliciet in de PR en check of het een ADR
  verdient.

## Een nieuwe locale toevoegen

Zie `locales/template/README.md` voor het volledige stappenplan en
`locales/README.md` voor wat er in de huidige kern nog niet locale-onafhankelijk is.
Open eerst een issue met `.github/ISSUE_TEMPLATE/new-locale.md`.

## Vragen

Open een issue. Dit is een eenmansproject naast een onderwijsaanstelling (zie
`docs/INTENDED_USE.md`) — reactietijd is niet gegarandeerd.

# Een nieuwe locale toevoegen

Dit is geen werkende module, alleen een stappenplan. Zie `locales/nl/` als het enige
bestaande, volledige voorbeeld — kopieer de structuur vandaar, niet vanuit deze map.

**Lees eerst `locales/README.md`.** De kern (`normalize/units.py`,
`normalize/frequency.py`, `parsing/common.py`) bevat op dit moment nog Nederlandse
aannames die eigenlijk ook naar een locale hadden gemoeten. Zolang dat niet is opgelost,
moet een nieuwe locale die aannames zelf ondervangen (zie stap 4 hieronder) — niet
doen alsof de kern al taal-agnostisch is.

## Stap 1 — merknaam- en combinatiepreparaat-mapping

Maak `locales/<land>/brands.py`, naar het voorbeeld van `locales/nl/brands.py`:
- `resolve_substance(name) -> (stofnaam, atc)`: merknaam of stofnaam → (stofnaam, ATC).
  Onbekende termen geven `(naam.lower(), None)` terug — nooit gokken (CLAUDE.md regel 4).
- `combo_components(name) -> list | None`: samenstellende stoffen van een
  combinatiepreparaat, of `None`.

Je hebt hiervoor een geneesmiddelendatabase van het betreffende land nodig (voor
Nederland: de G-standaard). Documenteer de bronversie in je eigen `locales/<land>/README.md`.

## Stap 2 — terminologie-vocabulaire (alleen nodig voor PDF/tekst-extractie)

Maak `locales/<land>/vocab.py`, naar het voorbeeld van `locales/nl/vocab.py`:
kolomlabel-synoniemen (`COLUMN_LABELS`), sectiemarkers (`SECTION_MARKERS`),
vormwoorden (`VORM_PATTERNS` — hernoem naar iets taalneutraals als je toch aan het
herstructureren bent) en eventuele zoutvorm-woorden.

Alleen nodig als je ook PDF-extractie voor dat land wilt ondersteunen. Voor CSV-only
inzet (fase 1) volstaat stap 1.

## Stap 3 — parsers

Maak `locales/<land>/pdf_parser.py` (vocab-gedreven, generiek binnen het land) en/of
`locales/<land>/prose_parser.py` (sjabloonspecifiek, per briefformaat). Registreer ze
in `parsing/pdf_text.py`'s val-terug-keten — dat bestand hoort zelf taal-agnostisch te
blijven, het roept alleen locale-parsers aan.

## Stap 4 — units/frequency (tijdelijke stap, zie locales/README.md)

Er is nog geen schone locale-interface voor eenheden- en frequentienormalisatie. Twee
opties, allebei tijdelijk:
1. Fork `normalize/units.py`/`normalize/frequency.py` naar je eigen locale en pas
   `compare.py` aan om de juiste versie te gebruiken — werkt, maar duplicaat-onderhoud.
2. Wacht op de locale-interface uit `locales/README.md` en bouw je module daartegen.

Documenteer welke route je kiest in een eigen ADR — dit is precies het soort stille
afwijking die CLAUDE.md regel 6 wil voorkomen.

## Stap 5 — reference-data en tests

`data/reference/` (ATC-subset, high-risk-lijst, duplicaatklassen) is internationaal
opgezet (ATC-codes, generieke stofnamen) — waarschijnlijk herbruikbaar, maar controleer
of de voorbeelden/synoniemen er niet stiekem Nederlandstalig zijn.

Voeg tests toe naar het voorbeeld van `tests/test_locale_nl_pdf_parser.py` en
`tests/test_locale_nl_prose_parser.py`. Voeg minstens een paar synthetische casus toe
in `data/synthetic/casus/` (of een aparte submap) om de nieuwe locale tegen de
diff-engine te toetsen — zie `docs/CASUS_FORMAAT_PROMPTS.md`.

## Issue-sjabloon

Gebruik `.github/ISSUE_TEMPLATE/new-locale.md` om een nieuwe-locale-bijdrage aan te
kondigen vóórdat je begint — dan kan er meegedacht worden over wat er in stap 4 nog
ontbreekt.

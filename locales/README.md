# Locales — status en wat nog moet verplaatsen

**Gedaan (2026-08-26):** `locales/nl/` bevat nu de vier bestanden die zichzelf al als
NL-specifiek documenteerden:
- `brands.py` (was `normalize/locales/nl.py`) — merknaam→stofnaam, combinatiepreparaten
- `vocab.py` (was `parsing/nl_medication_vocab.py`) — NHG/KNMP-kolomlabels, vormwoorden
- `pdf_parser.py` (was `parsing/generic_nl.py`) — vocab-gedreven PDF-parser
- `prose_parser.py` (was `parsing/prose_nl.py`) — Sint Barbara Ziekenhuis-briefsjabloon

Alle imports zijn bijgewerkt, volledige testsuite (72 passed, 1 xfailed) blijft groen.

**Niet gedaan, bewust:** de code die CLAUDE.md als "kern zonder NL-aannames"
beschrijft — `normalize/units.py`, `normalize/frequency.py`, `parsing/common.py` —
bevat zelf nog Nederlandse woorden en notatieconventies. Dat is geen nieuwe bug, het
was er al vóór deze sessie; deze sessie maakt het alleen zichtbaar door de duidelijke
scheiding elders. Dit **niet** in dezelfde sessie meegenomen, om twee redenen: (1) het
raakt `frequency_core`/`strengths_equal`/`doses_equal`, precies de functies die
`engine/diff.py` gebruikt om DOSE_CHANGE/FREQUENCY_CHANGE/STRENGTH_CHANGE te bepalen —
een gedragswijziging daar is patiëntveiligheidsrelevant en verdient een eigen
test-eerst-traject, niet een bijproduct van een publicatie-voorbereiding; (2) er is nog
geen tweede locale om een echt pluggable ontwerp tegen te toetsen — een interface nu
vastleggen zonder een tweede implementatie is gokken naar wat generiek genoeg is.

## Inventarisatie: wat moet verplaatsen (of achter een locale-interface komen)

### `normalize/units.py`
- `_UNIT_WORD_ALIASES`: "microgram", "milligram", "gram", "milliliter", "eenheden",
  "eenheid", "ie" (Nederlandse afkorting voor Internationale Eenheden — Engels: "IU").
- `_DOSE_UNIT_ALIASES`: "eenheid"/"eenheden" (NL voor "unit"), "pleister"/"pleisters"
  (NL voor "patch"). "tablet"/"capsule"/"ml"/"stuk" zijn toevallig NL-Engels gelijk of
  taalneutraal genoeg, maar zitten in dezelfde hardgecodeerde dict.

### `normalize/frequency.py`
- `_MODIFIER_PATTERNS`: volledig Nederlandstalig — `'s avonds`, `'s ochtends/morgens`,
  `'s middags`, `'s nachts`, `nuchter`.
- `_canonical_core`: Nederlandse notatieconventies — `Ndd1`/`dd`-notatie (NL
  apotheekjargon voor "maal daags"), `"x per dag"`/`"daags"`, `"om de N uur"`,
  `"1 tablet"` als letterlijke Nederlandse string-match.

### `parsing/common.py`
- `HEADER_ALIASES`: mengt Nederlandse kolomnamen (`middel`, `sterkte`, `vorm`,
  `dosering`, `frequentie`, `gestart`, `gestopt`, `reden_stop`) met Engelse
  (`drug_name`, `strength`, `form`, ...) in één dict zonder scheiding.
- Importeert `locales.nl.brands` direct (`from locales.nl import brands as locale_nl`,
  regel 11) — dit is de kern die naar een specifieke locale wijst, in plaats van een
  locale die bij de kern wordt aangesloten. Omgekeerde afhankelijkheidsrichting van wat
  CLAUDE.md's architectuurregel bedoelt.

## Wat een echte oplossing vergt

Een injecteerbare locale (bijv. een klasse/protocol met `unit_aliases`,
`dose_unit_aliases`, `frequency_modifier_patterns`, `header_aliases`,
`resolve_substance`, `combo_components` als methoden/attributen), die `compare.py` als
parameter doorgeeft in plaats van dat `normalize`/`parsing` een vaste module
importeren. Dat is een interface-ontwerp met impact op vrijwel elk bestand in de
pipeline — een aparte ADR en een test-eerst-traject, geen mechanische
bestandsverplaatsing zoals hierboven.

## Voor wie een tweede land toevoegt vóór die interface er is

Kopieer `locales/template/` (zie `locales/template/README.md`) voor de merknaam-/
vocab-/parserlaag. Voor units/frequency: je zult tijdelijk zelf moeten patchen wat er
in `normalize/units.py`/`normalize/frequency.py` staat, of die twee bestanden zelf naar
een eigen locale-versie forken — er is nog geen schone aansluiting. Documenteer dat
forken in een ADR zodat het niet als stille afwijking blijft staan.

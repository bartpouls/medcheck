---
name: Nieuwe locale
about: Voorstel om MedCheck te ondersteunen voor een ander land/taalgebied
title: "locale: <landcode/naam>"
labels: locale
---

Lees eerst `locales/template/README.md` en `locales/README.md` (wat nu nog niet
locale-onafhankelijk is in de kern) voordat je dit invult.

## Land/taalgebied

<!-- bijv. Duitsland, Vlaanderen (aparte casus wegens NL-taal-overlap met bestaande locale?) -->

## Geneesmiddelendatabase

Welke nationale/regionale database gebruik je voor merknaam→stofnaam→ATC (het
equivalent van de Nederlandse G-standaard)? Is die vrij te gebruiken/redistribueren,
of alleen als lookup zonder de brondata zelf te committen?

## Brondocumenten die je wilt ondersteunen

CSV-only, of ook PDF-extractie? Zo ja: welke systemen/formaten (vergelijkbaar met hoe
`locales/nl/` HIX en CGM Apotheek dekt via één vocab-gedreven parser, niet twee
vendor-specifieke)?

## Stap 4 uit locales/template/README.md

`normalize/units.py`/`normalize/frequency.py` bevatten nog Nederlandse aannames
(eenheden, `'s avonds`-achtige modifiers, `dd`-notatie). Ga je die forken naar een
eigen locale-versie, of wacht je op de locale-interface? Wat heb je daarvoor nodig van
de kern van dit project?

## Testdata

Ben je van plan synthetische casus aan te leveren (`data/synthetic/casus/`, zie
`docs/CASUS_FORMAAT_PROMPTS.md`)? Echte brondata hoort nooit in een PR — zie
`CLAUDE.md` regel 1 en `SAFETY.md`.

# Casus 018 — anticoagulantia-switch

**Edge case:** acenocoumarol (VKA) in lijst A vervangen door rivaroxaban (DOAC) in lijst B.
Het datamodel kent geen apart type "SWITCH" — dit wordt daarom gedetecteerd als STOPPED +
ADDED, elk apart. Bewust zo gelaten: de triage-laag mag hier eventueel een gecombineerde
weergave van maken, maar dat is fase 3, geen diff-engine-verantwoordelijkheid.

**Verwacht:** 2 discrepanties (STOPPED acenocoumarol, ADDED rivaroxaban), beide escaleren
(antistolling is risicomedicatie).

**Test wat:** dat de engine geen "slimme" switch-detectie doet — dat zou een klinische
interpretatie zijn die niet in de deterministische laag thuishoort (zie CLAUDE.md regel 2).

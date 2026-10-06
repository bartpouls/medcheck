# Casus 009 — geen discrepantie (psychiatrisch pakket)

**Edge case:** vals-positieven vangen, met risicomedicatie (lithium) waarbij toch geen
discrepantie bestaat — test dat "risicomedicatie aanwezig" niet hetzelfde is als
"discrepantie aanwezig".

**Verwacht:** 0 discrepanties. Open vraag (zie notes): triggert lithium hier alsnog escalatie
puur op aanwezigheid? Zie `docs/decisions/` — nog geen ADR, expliciet vastleggen vóór fase 3.

**Test wat:** onderscheid tussen "bevat risicomedicatie" en "heeft discrepantie die escaleert".

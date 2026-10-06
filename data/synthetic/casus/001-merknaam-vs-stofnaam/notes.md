# Casus 001 — merknaam tegenover stofnaam

**Edge case:** lijst A gebruikt merknamen, lijst B stofnamen. Zonder normalisatie levert dit
maximale vals-positieven op: elk middel lijkt gestopt én toegevoegd.

**Verwacht:** 0 discrepanties op middelniveau, 1 echte discrepantie (dosiswijziging metoprolol).

**Test wat:** normalisatielaag, R03 uit de risicoanalyse.

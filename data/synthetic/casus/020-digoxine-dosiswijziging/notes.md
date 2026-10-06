# Casus 020 — digoxine dosiswijziging

**Edge case:** digoxine sterkte gehalveerd (0.25mg -> 0.125mg) — een reductie, niet verhoging;
test dat escalatie niet alleen bij dosisverhoging geldt.

**Verwacht:** 1 discrepantie, STRENGTH_CHANGE, hoog, verplichte escalatie (risicomedicatie).

**Test wat:** dat richting van de wijziging (omlaag) de escalatieregel niet buiten werking stelt.

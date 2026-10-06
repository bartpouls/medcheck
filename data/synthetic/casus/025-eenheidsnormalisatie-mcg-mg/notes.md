# Casus 025 — eenheidsnormalisatie microgram versus milligram

**Edge case:** levothyroxine in lijst A als "0,1 mg", in lijst B als "100 microgram" —
dezelfde dosis, andere eenheid. Zonder eenheidsnormalisatie lijkt dit een STRENGTH_CHANGE.

**Verwacht:** 0 discrepanties na correcte eenheidsnormalisatie (mg -> mcg).

**Test wat:** eenheidsnormalisatie (mg/g/mcg) uit backlog fase 1, expliciet voor dit
grensgeval (factor 1000, makkelijk fout te normaliseren).

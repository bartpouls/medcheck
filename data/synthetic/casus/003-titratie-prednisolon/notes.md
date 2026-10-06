# Casus 003 — dosistitratie (prednisolon afbouwschema)

**Edge case:** lijst A toont het volledige afbouwschema (apotheeksysteem), lijst B toont alleen
de actuele stap (ontslagbrief, later geschreven). Beide beschrijven dezelfde actuele dosis.

**Verwacht:** 0 discrepanties. De valkuil is dat een naïeve parser de volledige schema-tekst
als losstaande dosis interpreteert en een vals-positieve DOSE_CHANGE meldt.

**Test wat:** extractie van huidige dosis uit een afbouwschema; geen speciale
titratie-heuristiek in de diff-engine zelf (die blijft deterministisch op genormaliseerde waarden).

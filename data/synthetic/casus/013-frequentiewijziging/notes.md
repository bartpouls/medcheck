# Casus 013 — frequentiewijziging

**Edge case:** metoprolol van 1dd1 naar 2dd1 (dosis per tablet gelijk, dagfrequentie omhoog) —
een zuivere FREQUENCY_CHANGE zonder sterktewijziging per tablet.

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, midden severity, geen automatische escalatie
(metoprolol zelf geen high_risk-categorie).

**Test wat:** FREQUENCY_CHANGE los van STRENGTH_CHANGE — de tabletsterkte is identiek.

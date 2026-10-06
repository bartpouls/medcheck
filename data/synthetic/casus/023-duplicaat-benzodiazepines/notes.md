# Casus 023 — dubbelmedicatie benzodiazepines (andere stofklasse dan casus 006)

**Edge case:** oxazepam en temazepam (beide ATC-4 N05B/N05C-achtig, valbeleid-relevant bij
ouderen) naast elkaar in lijst B — tweede voorbeeld van ATC-4-duplicaatdetectie, met een
andere farmacologische klasse dan casus 006 om te testen dat de regel generiek is en niet
toevallig alleen op NSAID's werkt.

**Verwacht:** 1 discrepantie, DUPLICATE_THERAPY, hoog, verplichte escalatie.

**Test wat:** generiekheid van de ATC-4-duplicaatregel over meerdere stofklassen.

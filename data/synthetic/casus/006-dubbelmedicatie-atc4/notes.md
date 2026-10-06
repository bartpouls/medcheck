# Casus 006 — dubbelmedicatie binnen dezelfde ATC-4

**Edge case:** twee verschillende NSAID's (ibuprofen en diclofenac, beide ATC-4 M01A) komen
naast elkaar voor in dezelfde lijst B — een reëel dubbelmedicatie-risico dat middelnaam-matching
alleen niet vangt.

**Verwacht:** 1 discrepantie, DUPLICATE_THERAPY, verplichte escalatie.

**Test wat:** duplicaatdetectie op ATC-4-niveau, niet alleen exacte ATC-5/stofnaam-match.

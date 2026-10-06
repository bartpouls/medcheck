# Casus 024 — meervoudige discrepanties in één patiënt

**Edge case:** realistische overdracht met meerdere gelijktijdige discrepantietypes: één
toegevoegd middel, één gestopt zonder reden, één dosiswijziging, en twee ongewijzigde
middelen als ruis. Test dat de engine per middel onafhankelijk classificeert zonder
kruisbesmetting tussen regels.

**Verwacht:** 3 discrepanties (ADDED, STOPPED, DOSE_CHANGE); 2 middelen zonder discrepantie.

**Test wat:** samengestelde casus dicht bij een echte overdrachtssituatie.

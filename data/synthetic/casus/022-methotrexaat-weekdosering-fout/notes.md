# Casus 022 — methotrexaat: weekdosering fout overgenomen als dagdosering

**Edge case:** klassieke, potentieel fatale overdrachtsfout. Lijst A: correct "1x per week".
Lijst B: abusievelijk overgenomen als "1dd1" (dagelijks) — een 7x overdosering.

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, hoogst mogelijke severity, verplichte
escalatie. Dit is een van de sterkste JOURNEY/workshop-voorbeelden: een AI-extractie die
"1dd1" en "1x per week" als plausibele varianten van elkaar zou normaliseren, is precies de
stille fout die regel 4 in CLAUDE.md (geen stille fixes) moet voorkomen.

**Test wat:** dat frequentiecanonicalisatie "1dd1" en "1x/week" nooit samenvoegt, en dat de
diff-engine dit als kritieke FREQUENCY_CHANGE markeert, niet als ruis.

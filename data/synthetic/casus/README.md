# Synthetische casus

Elke casus = map met:
- `source_a.csv|pdf|png`  bron 1 (bv. apotheeksysteem)
- `source_b.csv|pdf|png`  bron 2 (bv. ontslagbrief)
- `truth_a.json`, `truth_b.json`  ground truth per bron, handmatig geverifieerd
- `expected_diff.json`  verwachte discrepanties
- `notes.md`  waarom deze casus bestaat, welke edge case hij dekt

Ground truth is door een mens geverifieerd. Een door AI gegenereerde ground truth die door AI
wordt geëvalueerd meet niets.

**Geen echte patiëntgegevens. Namen, geboortedata en BSN zijn verzonnen en herkenbaar fictief
(gebruik "Testpatiënt 001", niet een realistisch ogende naam).**

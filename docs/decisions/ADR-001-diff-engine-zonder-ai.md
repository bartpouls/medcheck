# ADR-001 — Diff-engine bevat geen AI

Datum: <JJJJ-MM-DD> · Status: geaccepteerd

## Context
Een LLM kan direct twee medicatielijsten vergelijken. Dat is sneller te bouwen, maar
niet-deterministisch en niet toetsbaar.

## Overwogen opties
1. LLM vergelijkt beide lijsten en produceert discrepanties.
2. LLM extraheert en normaliseert; vergelijking gebeurt in code.

## Besluit
Optie 2.

## Gevolgen
+ Diff is reproduceerbaar, unit-testbaar en uitlegbaar aan een toezichthouder.
+ Fouten zijn lokaliseerbaar: extractiefout of regelfout, nooit "het model deed iets".
- Meer bouwwerk: matchinglogica, eenheden, frequentiecanonicalisatie.
- Combinatiepreparaten en titratieschema's vragen expliciete regels.

## Relatie tot intended use en risicoanalyse
Draagt R02, R05, R09. Zonder dit besluit is restrisico op R09 niet te beheersen.

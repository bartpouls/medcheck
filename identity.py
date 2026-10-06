"""Patiëntidentiteit vóór medicatievergelijking.

Bewaakt dat bron A en bron B over dezelfde patiënt gaan, vóórdat de medicatie-diff
draait. Voorkeursvolgorde: BSN (exacte match, na 11-proef-validatie in
locales/nl/patient_id.py), met naam + geboortedatum als fallback zodra BSN in één van
beide bronnen ontbreekt of ongeldig is.

Bart's expliciete keuze (2026-08-26): bij twijfel (mismatch, geen enkele bruikbare
identificator) NOOIT blokkeren -- doorlaten met een prominente waarschuwing, de
apothekersassistent/apotheker beoordeelt (CLAUDE.md: geen autonome actie, MedCheck
beslist niet). "BSN niet gevonden" en "BSN ongeldig" zijn bewust twee aparte
waarschuwingscodes, geen samengevoegde "kon niet valideren" -- dat is een expliciete
wens, geen toeval.

Deze module is zelf taal-agnostisch: ze vergelijkt alleen strings die al door de
locale-laag (parsing/common.py + locales/nl/patient_id.py) zijn geëxtraheerd en
gevalideerd, net zoals matching.py generiek blijft en de NL-specifieke merknaam-
resolutie aan locales/nl/brands.py overlaat.
"""

from models import IdentityWarning, PatientIdentity, PatientIdentityCheck

# Weergavelabel per bron, alleen voor waarschuwingsteksten -- de interne "a"/"b"-tags
# (models.py, matching.py, engine/) blijven ongewijzigd, dit is puur UI-taal (was/wordt
# i.p.v. bron A/B, zie ui/app.py).
_BRON_LABEL = {"a": "Was", "b": "Wordt"}


def _bsn_warnings(a: PatientIdentity, b: PatientIdentity) -> tuple[list[IdentityWarning], bool]:
    """Geeft (waarschuwingen, bruikbaar) terug. bruikbaar = beide bronnen hebben een
    aanwezig én geldig BSN, dus een echte BSN-vergelijking mogelijk is (los van of ze
    matchen)."""
    warnings: list[IdentityWarning] = []
    for source, identity in (("a", a), ("b", b)):
        if not identity.bsn:
            warnings.append(
                IdentityWarning(
                    code="BSN_ONTBREEKT",
                    source=source,
                    message=f"Geen BSN gevonden in {_BRON_LABEL[source]}.",
                )
            )
        elif identity.bsn_valid is False:
            warnings.append(
                IdentityWarning(
                    code="BSN_ONGELDIG",
                    source=source,
                    message=(
                        f"BSN in {_BRON_LABEL[source]} is ongeldig "
                        "(voldoet niet aan de 11-proef)."
                    ),
                )
            )
    bruikbaar = bool(a.bsn and b.bsn and a.bsn_valid and b.bsn_valid)
    return warnings, bruikbaar


def check_identity(a: PatientIdentity, b: PatientIdentity) -> PatientIdentityCheck:
    bsn_warnings, bsn_bruikbaar = _bsn_warnings(a, b)

    if bsn_bruikbaar:
        if a.bsn == b.bsn:
            return PatientIdentityCheck(matched=True, method="bsn", warnings=[])
        return PatientIdentityCheck(
            matched=False,
            method="bsn",
            warnings=[
                IdentityWarning(
                    code="BSN_MISMATCH",
                    message=(
                        "BSN van Was en Wordt komen niet overeen -- controleer of "
                        "dit dezelfde patiënt is."
                    ),
                )
            ],
        )

    name_a, dob_a = a.name.strip().lower(), a.birth_date.strip()
    name_b, dob_b = b.name.strip().lower(), b.birth_date.strip()
    if name_a and dob_a and name_b and dob_b:
        if name_a == name_b and dob_a == dob_b:
            return PatientIdentityCheck(matched=True, method="naam_geboortedatum", warnings=bsn_warnings)
        return PatientIdentityCheck(
            matched=False,
            method="naam_geboortedatum",
            warnings=bsn_warnings
            + [
                IdentityWarning(
                    code="NAAM_GEBOORTEDATUM_MISMATCH",
                    message="Naam en/of geboortedatum van Was en Wordt komen niet overeen.",
                )
            ],
        )

    return PatientIdentityCheck(
        matched=False,
        method="geen",
        warnings=bsn_warnings
        + [
            IdentityWarning(
                code="GEEN_IDENTIFICATIE_MOGELIJK",
                message=(
                    "Geen bruikbare patiëntidentificatie (BSN, of naam + geboortedatum) "
                    "in beide bronnen."
                ),
            )
        ],
    )

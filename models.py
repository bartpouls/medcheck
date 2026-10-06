"""Kernmodel voor MedCheck: MedicationLine en Discrepancy.

Velden en types exact volgens CLAUDE.md. Geen velden toegevoegd die op fase 2/3
vooruitlopen (bv. confidence bestaat als veld, maar wordt in fase 1 altijd 1.0
gezet — er is geen extractie-onzekerheid bij CSV/tekst-PDF-input).
"""

from typing import Literal, Optional

from pydantic import BaseModel

DiscrepancyType = Literal[
    "ADDED",
    "STOPPED",
    "DOSE_CHANGE",
    "FREQUENCY_CHANGE",
    "FORM_CHANGE",
    "STRENGTH_CHANGE",
    "DUPLICATE_THERAPY",
]

Severity = Literal["laag", "midden", "hoog", "kritiek"]


class MedicationLine(BaseModel):
    atc: Optional[str] = None
    substance: str
    brand: str = ""
    strength_value: Optional[float] = None
    strength_unit: str = ""
    form: str = ""
    dose_value: Optional[float] = None
    dose_unit: str = "stuk"
    frequency_canonical: str = ""
    prn: bool = False
    route: str = ""
    raw_text: str = ""
    confidence: float = 1.0
    source: Literal["a", "b"] = "a"
    # Niet in CLAUDE.md's oorspronkelijke veldenlijst, maar nodig voor de triage-regel
    # "STOPPED zonder geregistreerde reden" (casus 007 vs 012 vs 018) -- zie MVP-bouwrapport.
    stop_date: Optional[str] = None
    stop_reason: str = ""


class Discrepancy(BaseModel):
    type: DiscrepancyType
    lines_a: list[int] = []
    lines_b: list[int] = []
    severity: Severity
    requires_escalation: bool
    reason: str = ""


IdentityWarningCode = Literal[
    "BSN_ONTBREEKT",
    "BSN_ONGELDIG",
    "BSN_MISMATCH",
    "NAAM_GEBOORTEDATUM_MISMATCH",
    "GEEN_IDENTIFICATIE_MOGELIJK",
]

IdentityMatchMethod = Literal["bsn", "naam_geboortedatum", "geen"]


class PatientIdentity(BaseModel):
    """Patiëntidentiteit zoals uit één bron (A of B) geëxtraheerd. bsn_valid is None
    als er geen BSN gevonden is, en True/False als er wel een BSN is gevonden en de
    11-proef (locales/nl/patient_id.py) is uitgevoerd -- dat onderscheid is precies
    waarom "niet gevonden" en "ongeldig" twee aparte waarschuwingscodes zijn."""

    bsn: str = ""
    bsn_valid: Optional[bool] = None
    name: str = ""
    birth_date: str = ""


class IdentityWarning(BaseModel):
    code: IdentityWarningCode
    source: Optional[Literal["a", "b"]] = None
    message: str


class PatientIdentityCheck(BaseModel):
    """Resultaat van de patiëntidentiteitscontrole (identity.py). `matched` bepaalt
    NOOIT of de diff wordt uitgevoerd -- Bart's expliciete keuze: bij twijfel doorlaten
    met een prominente waarschuwing, nooit blokkeren (CLAUDE.md: geen autonome actie)."""

    matched: bool
    method: IdentityMatchMethod
    warnings: list[IdentityWarning] = []


class CompareResult(BaseModel):
    discrepancies: list[Discrepancy] = []
    identity: PatientIdentityCheck

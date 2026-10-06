"""Orchestratie: bestand A + bestand B -> lijst Discrepancy.

Eén functie, los van UI/CLI, zodat zowel tests als ui/app.py hem rechtstreeks kunnen
aanroepen (zie MVP_OPZET.md sectie 8: de compare-functie wordt end-to-end getest,
los van Streamlit)."""

from pathlib import Path

from engine.diff import diff
from engine.duplicates import apply_duplicate_overlay
from errors import DiagnosableError
from identity import check_identity
from matching import match_lines
from models import CompareResult, Discrepancy, MedicationLine, PatientIdentity
from parsing.csv_parser import parse_csv, parse_csv_identity
from parsing.pdf_text import parse_pdf, parse_pdf_identity
from triage.escalation import apply_triage


class UnsupportedFileTypeError(DiagnosableError, ValueError):
    pass


def _unsupported_file_type_error(suffix: str) -> UnsupportedFileTypeError:
    return UnsupportedFileTypeError(
        f"Bestandstype '{suffix}' wordt niet ondersteund.",
        "Alleen .csv en tekst-.pdf worden ondersteund in de MVP (zie MVP_OPZET.md).",
    )


def parse_file(path: Path, source: str) -> list[MedicationLine]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return parse_csv(path, source)
    if suffix == ".pdf":
        return parse_pdf(path, source)
    raise _unsupported_file_type_error(suffix)


def parse_identity(path: Path) -> PatientIdentity:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return parse_csv_identity(path)
    if suffix == ".pdf":
        return parse_pdf_identity(path)
    raise _unsupported_file_type_error(suffix)


def compare_lines(lines_a: list[MedicationLine], lines_b: list[MedicationLine]) -> list[Discrepancy]:
    pairs = match_lines(lines_a, lines_b)
    discrepancies = diff(lines_a, lines_b, pairs)
    discrepancies = apply_duplicate_overlay(discrepancies, pairs, lines_a, lines_b)
    discrepancies = apply_triage(discrepancies, lines_a, lines_b)
    return discrepancies


def compare_files(path_a: Path, path_b: Path) -> CompareResult:
    path_a, path_b = Path(path_a), Path(path_b)
    lines_a = parse_file(path_a, "a")
    lines_b = parse_file(path_b, "b")
    identity_check = check_identity(parse_identity(path_a), parse_identity(path_b))
    discrepancies = compare_lines(lines_a, lines_b)
    return CompareResult(discrepancies=discrepancies, identity=identity_check)

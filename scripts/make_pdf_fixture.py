"""Genereert een tabel-achtige tekst-PDF uit een casus-CSV, zonder externe
PDF-bibliotheek (geen reportlab/fpdf in requirements.txt -- nieuwe dependency vraagt
overleg per CLAUDE.md). Rauwe PDF-1.4-syntax met de ingebouwde Helvetica-basisfont
(geen font-embedding nodig). Elke rij wordt als kommagescheiden tekstregel geschreven,
zodat parsing/pdf_text.py::_rows_from_text hem oppikt -- dat is precies het
"tekst-PDF met selecteerbare, tabel/lijst-achtige inhoud" pad uit MVP_OPZET.md.

Gebruik: python scripts/make_pdf_fixture.py <casus-map> [a|b|beide]
Voorbeeld: python scripts/make_pdf_fixture.py data/synthetic/casus/006-dubbelmedicatie-atc4 beide
"""

import csv
import sys
from pathlib import Path


def _escape(text: str) -> bytes:
    encoded = text.encode("cp1252", errors="replace")
    escaped = encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    return escaped


def _content_stream(lines: list[str]) -> bytes:
    parts = [b"BT", b"/F1 10 Tf", b"12 TL", b"50 780 Td"]
    for i, line in enumerate(lines):
        if i > 0:
            parts.append(b"T*")
        parts.append(b"(" + _escape(line) + b") Tj")
    parts.append(b"ET")
    return b"\n".join(parts)


def csv_to_pdf(csv_path: Path, pdf_path: Path) -> None:
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = [",".join(cell for cell in row) for row in reader]

    stream = _content_stream(rows)

    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 595 842] /Contents 5 0 R >>"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")

    out = [b"%PDF-1.4\n"]
    offsets = [0]
    body = bytearray()
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out[0]) + len(body))
        body += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(out[0]) + len(body)
    xref = [f"xref\n0 {len(objects) + 1}\n".encode(), b"0000000000 65535 f \n"]
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode())
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )

    pdf_bytes = out[0] + bytes(body) + b"".join(xref) + trailer
    pdf_path.write_bytes(pdf_bytes)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    casus_dir = Path(sys.argv[1])
    which = sys.argv[2] if len(sys.argv) > 2 else "beide"

    targets = []
    if which in ("a", "beide"):
        targets.append(("source_a.csv", "source_a.pdf"))
    if which in ("b", "beide"):
        targets.append(("source_b.csv", "source_b.pdf"))

    for csv_name, pdf_name in targets:
        csv_path = casus_dir / csv_name
        pdf_path = casus_dir / pdf_name
        csv_to_pdf(csv_path, pdf_path)
        print(f"geschreven: {pdf_path}")


if __name__ == "__main__":
    main()

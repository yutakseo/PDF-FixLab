from __future__ import annotations
from pathlib import Path
from typing import Iterable, List

from PyPDF2 import PdfReader, PdfWriter


def merge(pdf_paths: Iterable[str | Path], output_pdf: str | Path) -> None:
    pdf_paths = [Path(p) for p in pdf_paths]
    output_pdf = Path(output_pdf)

    existing: List[Path] = [p for p in pdf_paths if p.is_file()]
    if not existing:
        raise FileNotFoundError("병합할 PDF 파일이 없습니다.")

    writer = PdfWriter()

    for p in existing:
        print(f"[MERGE] {p}")
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"[DONE] Saved merged PDF to: {output_pdf}")

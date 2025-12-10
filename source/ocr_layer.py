from __future__ import annotations
from pathlib import Path

import ocrmypdf


def add_ocr(
    input_pdf: str | Path,
    output_pdf: str | Path,
    lang: str = "kor+eng",
    deskew: bool = False,
) -> None:
    """
    기존 PDF에 OCR 텍스트 레이어를 추가.
    (Tesseract, Ghostscript, qpdf 등이 PATH에 있어야 함)
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    ocrmypdf.ocr(
        str(input_pdf),
        str(output_pdf),
        language=lang,
        output_type="pdf",
        deskew=deskew,
        rotate_pages=False,
        skip_text=True,
    )

    print(f"[DONE] OCR layer PDF saved to {output_pdf}")

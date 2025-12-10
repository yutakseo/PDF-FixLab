from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def rotate_even_pages(input_pdf: str | Path, output_pdf: str | Path) -> None:
    """
    입력 PDF의 짝수 페이지(2,4,6,...)만 180도 회전해서 출력 PDF로 저장.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, start=1):
        if page_num % 2 == 0:
            page.rotate(180)
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)


def rotate_all(input_pdf: str | Path, output_pdf: str | Path, degrees: int) -> None:
    """
    모든 페이지를 degrees만큼 회전 (시계 방향).
    - 오른쪽으로 90도 누운 PDF를 바로 세우려면 degrees=270.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    if degrees % 90 != 0:
        raise ValueError("degrees must be multiple of 90 (e.g. 90, 180, 270)")

    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()

    for idx, page in enumerate(reader.pages, start=1):
        page.rotate(degrees)
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)

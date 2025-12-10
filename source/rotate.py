from __future__ import annotations
from pathlib import Path
from typing import Literal

from pypdf import PdfReader, PdfWriter


def rotate(
    input_pdf: str | Path,
    output_pdf: str | Path,
    degrees: int,
    target: Literal["all", "even", "odd"] = "all",
    start_page: int | None = None,
    end_page: int | None = None,
) -> None:
    """
    PDF 페이지 회전 유틸리티.

    Parameters
    ----------
    input_pdf : str | Path
        입력 PDF 경로
    output_pdf : str | Path
        출력 PDF 경로
    degrees : int
        회전 각도 (시계 방향). 90의 배수만 허용 (예: 90, 180, 270, -90, ...).
    target : {"all", "even", "odd"}, default "all"
        - "all"  : 모든 페이지 대상
        - "even" : 짝수 페이지(2,4,6,...)만 대상
        - "odd"  : 홀수 페이지(1,3,5,...)만 대상
    start_page : int | None, optional
        회전 적용 시작 페이지 (1-based). None이면 1페이지부터.
    end_page : int | None, optional
        회전 적용 끝 페이지 (1-based, inclusive). None이면 마지막 페이지까지.

    Notes
    -----
    - 페이지 번호는 1부터라고 가정.
    - target 조건(even/odd/all) AND start/end 범위 조건을 동시에 만족하는
      페이지만 회전한다.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    # 회전 각도 유효성 검사
    if degrees % 90 != 0:
        raise ValueError("degrees must be multiple of 90 (e.g. 90, 180, 270, -90)")

    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()

    num_pages = len(reader.pages)

    # start/end 기본값 보정
    if start_page is None:
        start_page = 1
    if end_page is None:
        end_page = num_pages

    if not (1 <= start_page <= num_pages):
        raise ValueError(f"start_page must be between 1 and {num_pages}")
    if not (1 <= end_page <= num_pages):
        raise ValueError(f"end_page must be between 1 and {num_pages}")
    if start_page > end_page:
        raise ValueError("start_page must be <= end_page")

    for page_num, page in enumerate(reader.pages, start=1):
        # 1) 페이지 범위 조건
        in_range = (start_page <= page_num <= end_page)

        # 2) 대상(even/odd/all) 조건
        if target == "all":
            match_target = True
        elif target == "even":
            match_target = (page_num % 2 == 0)
        elif target == "odd":
            match_target = (page_num % 2 == 1)
        else:
            raise ValueError("target must be 'all', 'even', or 'odd'")

        # 두 조건을 모두 만족하는 페이지만 회전
        if in_range and match_target:
            page.rotate(degrees)

        writer.add_page(page)

    # 메타데이터 유지
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)


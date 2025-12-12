from __future__ import annotations
from pathlib import Path
from typing import Literal, List

import fitz  # PyMuPDF
from PIL import Image


def rotate(
    input_pdf: str | Path,
    output_pdf: str | Path,
    degrees: int,
    target: Literal["all", "even", "odd"] = "all",
    start_page: int | None = None,
    end_page: int | None = None,
) -> None:
    """
    스캔 PDF를 실제로 회전(픽셀 레벨)해서 새 PDF로 저장.

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
      페이지만 실제 이미지 회전을 수행한다.
    - PyMuPDF로 페이지를 이미지로 렌더링 후, Pillow로 회전 → 다시 PDF로 저장하므로
      벡터 정보는 사라지고 래스터(이미지) PDF가 된다. 스캔본 전용 처리용으로 생각하면 된다.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    # 회전 각도 유효성 검사
    if degrees % 90 != 0:
        raise ValueError("degrees must be multiple of 90 (e.g. 90, 180, 270, -90)")

    # PyMuPDF로 PDF 열기
    doc = fitz.open(str(input_pdf))
    num_pages = len(doc)

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

    pil_pages: List[Image.Image] = []

    # Pillow는 양수 각도를 "반시계 방향"으로 돌리기 때문에
    # 시계 방향 degrees를 전달받으면 부호를 반대로 바꿔준다.
    ccw_angle = -degrees

    for page_num, page in enumerate(doc, start=1):
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

        # 페이지를 래스터 이미지로 렌더링 (72dpi 기준, 필요하면 확대 가능)
        pix = page.get_pixmap(alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # 실제 회전이 필요한 페이지인지 체크
        if in_range and match_target:
            # expand=True로 이미지 캔버스를 새 각도에 맞춰 확장
            img = img.rotate(ccw_angle, expand=True)

        pil_pages.append(img)

    doc.close()

    # 출력 경로 생성
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    # 여러 장을 하나의 PDF로 저장
    first, *rest = pil_pages
    first.save(str(output_pdf), "PDF", save_all=True, append_images=rest)

    print(f"[DONE] rotated PDF saved to {output_pdf}")

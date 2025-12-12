import fitz  # PyMuPDF

def resize(
    input_pdf: str,
    output_pdf: str,
    size: tuple | None = None,
    allow_upscale: bool = False,
) -> None:
    """
    PDF의 모든 페이지를 지정한 크기로 리사이즈하는 함수.

    Parameters
    ----------
    input_pdf : str
        원본 PDF 경로
    output_pdf : str
        결과 PDF 저장 경로
    size : tuple | None
        (width_pt, height_pt) 형식의 튜플 (단위: pt)
        - 예) A4: fitz.paper_size("a4")  → (≈595, ≈842)
        - None 이면 기본값으로 A4 사용
    allow_upscale : bool
        - False (기본): 원본 페이지가 더 작을 때는 확대하지 않음 (스케일 ≤ 1.0)
        - True        : 타겟 사이즈에 꽉 차도록 확대/축소 (업스케일 허용)
    """
    # 타겟 페이지 크기 결정
    if size is None:
        target_w, target_h = fitz.paper_size("a4")
    else:
        if not (isinstance(size, tuple) and len(size) == 2):
            raise ValueError("size는 (width_pt, height_pt) 형식의 튜플이어야 합니다.")
        target_w, target_h = size

    src_doc = fitz.open(input_pdf)
    dst_doc = fitz.open()

    for page in src_doc:
        src_rect = page.rect  # 원본 페이지 크기 (pt)

        # 1) 타겟 크기에 맞추는 스케일 계산 (비율 유지)
        scale_x = target_w / src_rect.width
        scale_y = target_h / src_rect.height
        scale = min(scale_x, scale_y)

        # 업스케일 방지 옵션
        if not allow_upscale and scale > 1.0:
            scale = 1.0

        # 2) 스케일 적용 후 컨텐츠 크기
        new_w = src_rect.width * scale
        new_h = src_rect.height * scale

        # 3) 타겟 페이지 안에서 중앙 정렬을 위한 위치 계산
        left = (target_w - new_w) / 2
        top = (target_h - new_h) / 2
        right = left + new_w
        bottom = top + new_h

        # 4) 새 페이지(A4 또는 지정 크기) 만들기
        new_page = dst_doc.new_page(width=target_w, height=target_h)

        # 5) 원본 페이지를 타겟 직사각형에 맞춰 그려 넣기
        #    show_pdf_page가 src_rect -> dest_rect로 스케일/이동 변환을 알아서 처리
        dest_rect = fitz.Rect(left, top, right, bottom)
        new_page.show_pdf_page(
            dest_rect,      # 타겟 영역 (중앙에 배치된 사각형)
            src_doc,        # 원본 문서
            page.number,    # 원본 페이지 번호
        )

    # 6) 저장
    dst_doc.save(output_pdf)
    dst_doc.close()
    src_doc.close()


# 사용 예시 1) 기본 A4로 리사이즈 (업스케일 X)
if __name__ == "__main__":
    resize("input.pdf", "output_a4.pdf")

    # 사용 예시 2) A3 사이즈로 리사이즈 (업스케일 허용)
    a3_size = fitz.paper_size("a3")
    resize("input.pdf", "output_a3_upscale.pdf", size=a3_size, allow_upscale=True)

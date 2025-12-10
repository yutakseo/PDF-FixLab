from __future__ import annotations
from pathlib import Path
from typing import List

import fitz  # pymupdf
import cv2
import numpy as np
from PIL import Image


def estimate_skew_angle(gray: np.ndarray, max_skew_deg: float) -> float:
    """
    흑백 이미지(gray)에서 글자 영역 기반으로
    '작은 기울기(±max_skew_deg)'만 추정해서 반환.
    """
    # 블러 + OTSU 이진화
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 글자 후보 영역 좌표 추출
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 50:
        # 글자 영역이 거의 없으면 회전 보정 안 함
        return 0.0

    # 최소 외접 사각형으로 기울기 추정
    (cx, cy), (w, h), raw_angle = cv2.minAreaRect(coords)

    # 세로가 더 긴 경우 각도를 +90 해서 0 근처로 맞추기
    if w < h:
        raw_angle = raw_angle + 90

    angle = -raw_angle

    # -45 ~ 45 범위로 정규화
    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90

    # 허용 각도 초과하면 보정하지 않음
    if abs(angle) > max_skew_deg:
        return 0.0

    return float(angle)


def deskew(
    input_pdf: str | Path,
    output_pdf: str | Path,
    dpi: int = 300,
    max_skew_deg: float = 3.0,
) -> None:
    """
    스캔된 PDF에서 각 페이지별로
    '소량 기울기(±max_skew_deg)'만 보정해서 새 PDF로 저장.

    Parameters
    ----------
    input_pdf : str | Path
        원본 PDF 경로
    output_pdf : str | Path
        결과 PDF 경로
    dpi : int, optional
        페이지 렌더링 해상도 (기본 300 dpi)
    max_skew_deg : float, optional
        허용할 최대 기울기 보정 각도(도 단위).
        이 값보다 큰 기울기는 노이즈로 보고 보정하지 않음.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    doc = fitz.open(str(input_pdf))
    pil_pages: List[Image.Image] = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        # PDF 페이지를 래스터 이미지로 렌더링
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 기울기 추정
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        angle = estimate_skew_angle(gray, max_skew_deg=max_skew_deg)
        print(f"[DESKEW] page {page_index + 1}: {angle:.2f} deg")

        # 보정이 필요한 경우에만 회전
        if abs(angle) > 0.01:
            h, w = img_bgr.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img_bgr = cv2.warpAffine(
                img_bgr,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )

        # 다시 PIL 이미지로 변환해서 리스트에 저장
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_pages.append(Image.fromarray(img_rgb))

    doc.close()

    # 출력 경로 생성
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    # PIL이 여러 장을 한 번에 PDF로 저장
    first, *rest = pil_pages
    first.save(str(output_pdf), "PDF", save_all=True, append_images=rest)

    print(f"[DONE] deskewed PDF saved to {output_pdf}")

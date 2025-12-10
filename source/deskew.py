from __future__ import annotations
from pathlib import Path
from typing import List

import fitz  # pymupdf
import cv2
import numpy as np
from PIL import Image

MAX_SKEW_DEG = 3.0  # 허용할 최대 기울기 보정 각도 (도)


def estimate_skew_angle(gray: np.ndarray) -> float:
    """
    흑백 이미지(gray)에서 글자 영역 기반으로 '작은 기울기(±MAX_SKEW_DEG)'만 추정해서 반환.
    """
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 50:
        return 0.0

    (cx, cy), (w, h), raw_angle = cv2.minAreaRect(coords)

    # 세로가 더 길게 잡힌 경우 각도를 +90 해서 0 근처로 맞추기
    if w < h:
        raw_angle = raw_angle + 90

    angle = -raw_angle

    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90

    if abs(angle) > MAX_SKEW_DEG:
        return 0.0

    return float(angle)


def deskew_pdf(
    input_pdf: str | Path,
    output_pdf: str | Path,
    dpi: int = 300,
) -> None:
    """
    스캔된 PDF에서 각 페이지별로 '소량 기울기(±MAX_SKEW_DEG)'만 보정해서 새 PDF로 저장.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    doc = fitz.open(str(input_pdf))
    pil_pages: List[Image.Image] = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        angle = estimate_skew_angle(gray)
        print(f"[DESKEW] page {page_index + 1}: {angle:.2f} deg")

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

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_pages.append(Image.fromarray(img_rgb))

    doc.close()

    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    first, *rest = pil_pages
    first.save(str(output_pdf), "PDF", save_all=True, append_images=rest)

    print(f"[DONE] deskewed PDF saved to {output_pdf}")

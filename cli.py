from __future__ import annotations
import argparse

from source import rotate, deskew, ocr_layer, merge, resize


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pdffix",  # 콘솔에서 호출하는 이름과 맞춤
        description="pdfFixLab: toolkit for fixing scanned PDFs (rotate, deskew, OCR, merge, resize).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------
    # rotate-even : 짝수 페이지만 180도 회전 (편의용 레거시 커맨드)
    # ------------------------------------------------------------------
    p_even = subparsers.add_parser("rotate-even", help="짝수 페이지를 180도 회전")
    p_even.add_argument("input", help="입력 PDF 경로")
    p_even.add_argument("output", help="출력 PDF 경로")

    # ------------------------------------------------------------------
    # rotate-all : 모든 페이지를 지정 각도만큼 회전 (레거시 커맨드)
    # ------------------------------------------------------------------
    p_all = subparsers.add_parser("rotate-all", help="모든 페이지를 지정 각도만큼 회전")
    p_all.add_argument("input", help="입력 PDF 경로")
    p_all.add_argument("output", help="출력 PDF 경로")
    p_all.add_argument(
        "--deg",
        type=int,
        default=270,
        help="시계 방향 회전 각도 (기본: 270 = 왼쪽으로 90도)",
    )

    # ------------------------------------------------------------------
    # rotate : 짝수/홀수/범위까지 지정 가능한 범용 회전 커맨드
    # ------------------------------------------------------------------
    p_rot = subparsers.add_parser(
        "rotate",
        help="페이지 회전 (짝수/홀수/페이지 범위 지정 가능)",
    )
    p_rot.add_argument("input", help="입력 PDF 경로")
    p_rot.add_argument("output", help="출력 PDF 경로")
    p_rot.add_argument(
        "--deg",
        type=int,
        default=270,
        help="시계 방향 회전 각도 (기본: 270 = 왼쪽으로 90도)",
    )
    p_rot.add_argument(
        "--target",
        choices=["all", "even", "odd"],
        default="all",
        help="회전 대상 페이지 (기본: all)",
    )
    p_rot.add_argument(
        "--start-page",
        type=int,
        default=None,
        help="회전 적용 시작 페이지 (1부터, 기본: 전체)",
    )
    p_rot.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="회전 적용 끝 페이지 (포함, 기본: 전체)",
    )

    # ------------------------------------------------------------------
    # deskew : 기울기 보정
    # ------------------------------------------------------------------
    p_deskew = subparsers.add_parser("deskew", help="페이지별 소량 기울기 보정")
    p_deskew.add_argument("input", help="입력 PDF 경로")
    p_deskew.add_argument("output", help="출력 PDF 경로")
    p_deskew.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="렌더링 DPI (기본: 300)",
    )
    p_deskew.add_argument(
        "--max-skew-deg",
        type=float,
        default=3.0,
        help="허용할 최대 기울기 보정 각도(도) (기본: 3.0)",
    )

    # ------------------------------------------------------------------
    # ocr : OCR 텍스트 레이어 추가
    # ------------------------------------------------------------------
    p_ocr = subparsers.add_parser("ocr", help="PDF에 OCR 텍스트 레이어 추가")
    p_ocr.add_argument("input", help="입력 PDF 경로")
    p_ocr.add_argument("output", help="출력 PDF 경로")
    p_ocr.add_argument(
        "--lang",
        default="kor+eng",
        help="Tesseract 언어 (기본: kor+eng)",
    )
    p_ocr.add_argument(
        "--deskew",
        action="store_true",
        help="ocrmypdf에서 자체 deskew 사용 (기본: 사용 안함)",
    )

    # ------------------------------------------------------------------
    # merge : 여러 PDF를 하나로 병합
    # ------------------------------------------------------------------
    p_merge = subparsers.add_parser("merge", help="여러 PDF를 하나로 병합")
    p_merge.add_argument("output", help="출력 PDF 경로")
    p_merge.add_argument("inputs", nargs="+", help="병합할 PDF 경로들 (순서대로)")

    # ------------------------------------------------------------------
    # resize-a4 : 페이지 크기를 A4로 맞추는 커맨드
    # ------------------------------------------------------------------
    p_resize_a4 = subparsers.add_parser(
        "resize-a4",
        help="페이지 크기를 A4로 리사이즈 (기본: 축소만, 업스케일 없음)",
    )
    p_resize_a4.add_argument("input", help="입력 PDF 경로")
    p_resize_a4.add_argument("output", help="출력 PDF 경로")
    p_resize_a4.add_argument(
        "--allow-upscale",
        action="store_true",
        help="A4보다 작은 페이지도 확대해서 꽉 채움 (기본: 확대 안함)",
    )

    # ==================================================================
    # 디스패치
    # ==================================================================
    args = parser.parse_args()

    if args.command == "rotate-even":
        rotate.rotate(
            args.input,
            args.output,
            degrees=180,
            target="even",
            start_page=None,
            end_page=None,
        )

    elif args.command == "rotate-all":
        rotate.rotate(
            args.input,
            args.output,
            degrees=args.deg,
            target="all",
            start_page=None,
            end_page=None,
        )

    elif args.command == "rotate":
        rotate.rotate(
            args.input,
            args.output,
            degrees=args.deg,
            target=args.target,
            start_page=args.start_page,
            end_page=args.end_page,
        )

    elif args.command == "deskew":
        deskew.deskew(
            args.input,
            args.output,
            dpi=args.dpi,
            max_skew_deg=args.max_skew_deg,
        )

    elif args.command == "ocr":
        ocr_layer.add_ocr_layer(
            args.input,
            args.output,
            lang=args.lang,
            deskew=args.deskew,
        )

    elif args.command == "merge":
        merge.merge_pdfs(args.inputs, args.output)

    elif args.command == "resize-a4":
        import fitz
        a4_w, a4_h = fitz.paper_size("a4")
        resize.resize(
            args.input,
            args.output,
            size=(a4_w, a4_h),
            allow_upscale=args.allow_upscale,
        )


if __name__ == "__main__":
    main()

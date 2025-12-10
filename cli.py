from __future__ import annotations
import argparse

from source import rotate, deskew, ocr_layer, merge 



def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pdffixlab",
        description="pdfFixLab: toolkit for fixing scanned PDFs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # rotate-even
    p_even = subparsers.add_parser("rotate-even", help="짝수 페이지를 180도 회전")
    p_even.add_argument("input", help="입력 PDF 경로")
    p_even.add_argument("output", help="출력 PDF 경로")

    # rotate-all
    p_all = subparsers.add_parser("rotate-all", help="모든 페이지를 지정 각도만큼 회전")
    p_all.add_argument("input", help="입력 PDF 경로")
    p_all.add_argument("output", help="출력 PDF 경로")
    p_all.add_argument(
        "--deg",
        type=int,
        default=270,
        help="시계 방향 회전 각도 (기본: 270 = 왼쪽으로 90도)",
    )

    # deskew
    p_deskew = subparsers.add_parser("deskew", help="페이지별 소량 기울기 보정")
    p_deskew.add_argument("input", help="입력 PDF 경로")
    p_deskew.add_argument("output", help="출력 PDF 경로")
    p_deskew.add_argument("--dpi", type=int, default=300, help="렌더링 DPI (기본: 300)")

    # ocr
    p_ocr = subparsers.add_parser("ocr", help="PDF에 OCR 텍스트 레이어 추가")
    p_ocr.add_argument("input", help="입력 PDF 경로")
    p_ocr.add_argument("output", help="출력 PDF 경로")
    p_ocr.add_argument("--lang", default="kor+eng", help="Tesseract 언어 (기본: kor+eng)")
    p_ocr.add_argument(
        "--deskew",
        action="store_true",
        help="ocrmypdf에서 자체 deskew 사용 (기본: 사용 안함)",
    )

    # merge
    p_merge = subparsers.add_parser("merge", help="여러 PDF를 하나로 병합")
    p_merge.add_argument("output", help="출력 PDF 경로")
    p_merge.add_argument("inputs", nargs="+", help="병합할 PDF 경로들 (순서대로)")

    args = parser.parse_args()

    if args.command == "rotate-even":
        rotate.rotate_even_pages(args.input, args.output)
    elif args.command == "rotate-all":
        rotate.rotate_all(args.input, args.output, args.deg)
    elif args.command == "deskew":
        deskew.deskew_pdf(args.input, args.output, dpi=args.dpi)
    elif args.command == "ocr":
        ocr_layer.add_ocr_layer(
            args.input,
            args.output,
            lang=args.lang,
            deskew=args.deskew,
        )
    elif args.command == "merge":
        merge.merge_pdfs(args.inputs, args.output)

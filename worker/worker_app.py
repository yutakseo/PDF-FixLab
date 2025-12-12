# worker/worker_app.py
import uuid
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse

from source.resize import resize

app = FastAPI(title="PDF Worker Service")


@app.post("/process")
async def process(
    file: UploadFile = File(...),
    max_width: float | None = Form(default=None),
    max_height: float | None = Form(default=None),
    allow_upscale: bool = Form(default=False),
):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"detail": "PDF only"})

    # ★ TemporaryDirectory 컨텍스트를 쓰지 않고, 실제 디렉터리만 하나 만든다
    tmpdir = Path(tempfile.mkdtemp(prefix="pdf_worker_"))

    input_path = tmpdir / f"input_{uuid.uuid4()}.pdf"
    output_path = tmpdir / "output.pdf"

    # 업로드 파일 저장
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # max_width / max_height -> size 튜플 변환 (옵션)
    if max_width is not None and max_height is not None:
        size = (max_width, max_height)
    else:
        size = None  # resize()에서 A4 기본값 사용

    try:
        resize(
            input_pdf=str(input_path),
            output_pdf=str(output_path),
            size=size,
            allow_upscale=allow_upscale,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    # 안전하게 한 번 더 존재 여부 체크 (디버깅 도움용)
    if not output_path.exists():
        return JSONResponse(
            status_code=500,
            content={"detail": f"output file not found: {output_path}"},
        )

    # 여기서는 tmpdir이 아직 살아 있으므로 FileResponse가 파일을 읽을 수 있다
    return FileResponse(
        str(output_path),
        media_type="application/pdf",
        filename="processed.pdf",
    )

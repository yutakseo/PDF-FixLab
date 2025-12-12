# worker/worker_app.py
import uuid
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse


from source.resize import resize
from source.rotate import rotate
from source.deskew import deskew
from source.ocr_layer import add_ocr
from source.merge import merge


app = FastAPI(title="PDF Worker Service")

@app.post("/process")
async def process(
    file: UploadFile = File(...),
    max_width: float | None = Form(default=595),
    max_height: float | None = Form(default=842),
    auto_rotate: bool = Form(default=True),
):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"detail": "PDF only"})

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        input_path = tmp / f"input_{uuid.uuid4()}.pdf"
        output_path = tmp / "output.pdf"

        with open(input_path, "wb") as f:
            f.write(await file.read())

        try:
            process_pdf(str(input_path), str(output_path),
                        max_width=max_width,
                        max_height=max_height,
                        auto_rotate=auto_rotate)
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": str(e)})

        return FileResponse(str(output_path), media_type="application/pdf",
                            filename="processed.pdf")

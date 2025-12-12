# web/web_app.py
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles        
from fastapi.templating import Jinja2Templates      
import httpx

app = FastAPI(title="PDF Web Frontend")


app.mount("/static", StaticFiles(directory="uiux/static"), name="static")
templates = Jinja2Templates(directory="uiux/templates")
WORKER_URL = "http://pdf_worker:9000/process"



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    max_width: float | None = Form(default=595),
    max_height: float | None = Form(default=842),
    auto_rotate: bool | None = Form(default=True),
):
    if file.content_type != "application/pdf":
        return HTMLResponse("<h3>PDF 파일만 업로드 가능합니다.</h3>", status_code=400)

    # worker 컨테이너로 그대로 proxy
    file_bytes = await file.read()

    data = {
        "max_width": str(max_width) if max_width is not None else "",
        "max_height": str(max_height) if max_height is not None else "",
        "auto_rotate": "true" if auto_rotate else "false",
    }

    files = {
        "file": (
            file.filename or "input.pdf",
            file_bytes,
            file.content_type or "application/pdf",
        )
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(WORKER_URL, data=data, files=files)

    if resp.status_code != 200:
        return HTMLResponse(
            f"<h3>Worker 오류 발생: {resp.status_code}</h3><pre>{resp.text}</pre>",
            status_code=500,
        )

    # worker에서 받은 PDF를 바로 브라우저 다운로드로 전달
    out_bytes = resp.content
    out_filename = f"processed_{file.filename or 'output.pdf'}"

    return StreamingResponse(
        BytesIO(out_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{out_filename}"'
        },
    )

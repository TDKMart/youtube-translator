from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from worker import process_video
import os
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

RESULTS = {}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
def process(url: str = Form(...), target_lang: str = Form(...)):
    job_id = str(uuid.uuid4())
    task = process_video.delay(url, target_lang, job_id)
    RESULTS[job_id] = "processing"
    return JSONResponse({"job_id": job_id})

@app.get("/result/{job_id}")
def get_result(job_id: str):
    status = RESULTS.get(job_id, "not_found")
    if status == "done":
        return JSONResponse({"status": "done", "url": f"/download/{job_id}"})
    elif status == "error":
        return JSONResponse({"status": "error"})
    return JSONResponse({"status": "processing"})

@app.get("/download/{job_id}")
def download(job_id: str):
    path = f"/tmp/{job_id}/output.mp4"
    if os.path.exists(path):
        return FileResponse(path, media_type="video/mp4", filename="translated_video.mp4")
    return JSONResponse({"error": "File not ready"})
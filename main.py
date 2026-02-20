import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.background import BackgroundTask

from config import DOWNLOADS_DIR, HOST, PORT, QUALITY_FORMATS
from downloader import Job, download_video, get_video_info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# In-memory Job-Store (reicht für lokale Nutzung)
jobs: dict[str, Job] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    logger.info("RedditLink gestartet auf http://%s:%s", HOST, PORT)
    yield
    for f in os.listdir(DOWNLOADS_DIR):
        try:
            os.remove(os.path.join(DOWNLOADS_DIR, f))
        except OSError:
            pass
    logger.info("RedditLink beendet, Temp-Dateien bereinigt")


app = FastAPI(title="RedditLink", lifespan=lifespan)

# CORS: nur Chrome-Extensions dürfen die API aufrufen.
# allow_origins=["*"] wäre unsicher — jede Website könnte sonst Downloads triggern.
# chrome-extension:// blockiert reguläre Webseiten komplett.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


# ── Request Models ────────────────────────────────────────────────────────────

class InfoRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    quality: str = "best"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/info")
async def info(request: InfoRequest):
    """Gibt Metadaten zurück (Titel, Thumbnail, Dauer) ohne Download."""
    try:
        data = await asyncio.to_thread(get_video_info, request.url.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return data


@app.post("/download")
async def start_download(request: DownloadRequest):
    """Erstellt einen Download-Job und gibt sofort eine job_id zurück."""
    url = request.url.strip()
    quality = request.quality

    if quality not in QUALITY_FORMATS:
        raise HTTPException(status_code=400, detail=f"Ungültige Qualität: {quality!r}")

    job = Job(id=str(uuid.uuid4()))
    jobs[job.id] = job

    # Download läuft in einem Thread — blockiert den Event-Loop nicht
    asyncio.create_task(_run_download(job, url, quality))

    return {"job_id": job.id}


@app.get("/progress/{job_id}")
async def progress(job_id: str):
    """Server-Sent Events Stream mit Echtzeit-Fortschritt."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")

    async def event_stream():
        while True:
            job = jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'Job nicht gefunden'})}\n\n"
                break
            yield f"data: {json.dumps(job.to_dict())}\n\n"
            if job.status in ("done", "error"):
                break
            await asyncio.sleep(0.4)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/file/{job_id}")
async def get_file(job_id: str):
    """Gibt die fertige Datei zurück und räumt danach auf."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    if job.status != "done":
        raise HTTPException(status_code=400, detail="Job noch nicht abgeschlossen")
    if not job.filepath or not os.path.exists(job.filepath):
        raise HTTPException(status_code=404, detail="Datei nicht mehr vorhanden")

    ext = os.path.splitext(job.filepath)[1].lower()
    media_type = "audio/mpeg" if ext == ".mp3" else "video/mp4"
    download_name = f"video{ext}"

    def cleanup():
        try:
            os.remove(job.filepath)
        except OSError:
            pass
        jobs.pop(job_id, None)

    return FileResponse(
        path=job.filepath,
        media_type=media_type,
        filename=download_name,
        background=BackgroundTask(cleanup),
    )


# ── Internal ──────────────────────────────────────────────────────────────────

async def _run_download(job: Job, url: str, quality: str):
    try:
        filepath = await asyncio.to_thread(download_video, url, quality, job)
        job.filepath = filepath
        job.filename = os.path.basename(filepath)
        job.status = "done"
        job.progress = 100
        job.message = "Fertig!"
        logger.info("Job %s abgeschlossen: %s", job.id, filepath)
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        logger.error("Job %s fehlgeschlagen: %s", job.id, e)


# Statische Dateien nach den API-Routen mounten
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

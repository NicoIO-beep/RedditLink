import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.background import BackgroundTask

from config import DOWNLOADS_DIR, HOST, PORT
from downloader import download_reddit_video

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    logger.info("RedditLink gestartet auf http://%s:%s", HOST, PORT)
    yield
    # Beim Beenden: übrige Temp-Dateien bereinigen
    for f in os.listdir(DOWNLOADS_DIR):
        try:
            os.remove(os.path.join(DOWNLOADS_DIR, f))
        except OSError:
            pass
    logger.info("RedditLink beendet, Temp-Dateien bereinigt")


app = FastAPI(title="RedditLink", lifespan=lifespan)


class DownloadRequest(BaseModel):
    url: str


@app.post("/download")
async def download(request: DownloadRequest):
    """
    Nimmt eine Reddit-URL, lädt das Video herunter und gibt es als MP4 zurück.
    Die temporäre Datei wird nach dem Senden automatisch gelöscht.
    """
    url = request.url.strip()

    try:
        filepath = download_reddit_video(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    def delete_file():
        try:
            os.remove(filepath)
            logger.info("Temp-Datei gelöscht: %s", filepath)
        except OSError:
            pass

    return FileResponse(
        path=filepath,
        media_type="video/mp4",
        filename="reddit_video.mp4",
        background=BackgroundTask(delete_file),
    )


# Statische Dateien (index.html) unter / ausliefern — muss nach den API-Routen stehen
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

import glob
import logging
import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import imageio_ffmpeg
import yt_dlp

from config import ALLOWED_DOMAINS, DOWNLOADS_DIR, QUALITY_FORMATS

logger = logging.getLogger(__name__)


@dataclass
class Job:
    id: str
    status: str = "pending"   # pending | downloading | merging | done | error
    progress: int = 0
    message: str = "Warte..."
    filepath: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "filename": self.filename,
            "error": self.error,
        }


def make_progress_hook(job: Job):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                # Max 90% — 90-100 ist für Merge reserviert
                pct = min(int(downloaded / total * 100), 89)
                job.progress = pct
                job.message = f"Herunterladen {pct}%..."
            else:
                job.message = "Herunterladen..."
        elif d["status"] == "finished":
            job.status = "merging"
            job.progress = 90
            job.message = "Video + Audio werden zusammengeführt..."
    return hook


def download_video(url: str, quality: str, job: Job) -> str:
    """
    Lädt ein Video herunter. Gibt den Pfad zur fertigen Datei zurück.
    Unterstützt Reddit, YouTube, Twitter/X.
    """
    _validate_url(url)

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    is_audio = quality == "audio"
    # %(ext)s damit yt-dlp die richtige Extension setzt (mp4, mp3, etc.)
    output_template = os.path.join(DOWNLOADS_DIR, f"{job.id}.%(ext)s")

    ydl_opts = {
        "format": QUALITY_FORMATS[quality],
        "outtmpl": output_template,
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [make_progress_hook(job)],
    }

    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        ydl_opts["merge_output_format"] = "mp4"

    job.status = "downloading"
    logger.info("Starte Download (quality=%s): %s", quality, url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"Download fehlgeschlagen: {e}") from e

    # Datei finden (Extension wird von yt-dlp gesetzt)
    matches = glob.glob(os.path.join(DOWNLOADS_DIR, f"{job.id}.*"))
    if not matches:
        raise RuntimeError("Datei nach Download nicht gefunden")

    return matches[0]


def get_video_info(url: str) -> dict:
    """Gibt Metadaten zurück ohne zu downloaden (für die Vorschau)."""
    _validate_url(url)
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title", "Unbekannt"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader") or info.get("channel"),
    }


def _validate_url(url: str) -> None:
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Ungültige URL")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Nur HTTP/HTTPS URLs erlaubt")

    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(
            f"URL nicht unterstützt. Erlaubt: Reddit, YouTube, Twitter/X. "
            f"Erhalten: {parsed.netloc!r}"
        )

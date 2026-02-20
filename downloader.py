import logging
import os
import uuid
from urllib.parse import urlparse

import imageio_ffmpeg
import yt_dlp

from config import ALLOWED_DOMAINS, DOWNLOADS_DIR

logger = logging.getLogger(__name__)


def download_reddit_video(url: str) -> str:
    """
    Downloads a Reddit video (with audio) to the downloads folder.
    Returns the absolute path to the merged MP4 file.

    Raises:
        ValueError: if the URL is not a valid Reddit URL
        RuntimeError: if the download fails
    """
    _validate_reddit_url(url)

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    output_path = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}.mp4")

    ydl_opts = {
        # Beste Video- + Audioqualität, zusammengemergt als MP4
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": ffmpeg_path,
        # Erzwinge MP4 als Container (mergt via FFmpeg)
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    logger.info("Starte Download: %s", url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        logger.error("Download fehlgeschlagen: %s", e)
        raise RuntimeError(f"Download fehlgeschlagen: {e}") from e

    if not os.path.exists(output_path):
        raise RuntimeError("Datei nach Download nicht gefunden")

    logger.info("Download abgeschlossen: %s", output_path)
    return output_path


def _validate_reddit_url(url: str) -> None:
    """
    Prüft ob die URL wirklich eine Reddit-URL ist.
    Nutzt urlparse statt String-Contains — verhindert Bypasses wie evil.com?x=reddit.com
    """
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Ungültige URL")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Nur HTTP/HTTPS URLs erlaubt")

    # netloc ist der echte Hostname, nicht Query-Parameter oder Pfad
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(
            f"URL muss von Reddit kommen (reddit.com, redd.it). Erhalten: {parsed.netloc!r}"
        )

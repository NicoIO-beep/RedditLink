import os

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Erlaubte Domains
ALLOWED_DOMAINS = {
    # Reddit
    "reddit.com", "www.reddit.com", "old.reddit.com", "redd.it",
    # YouTube
    "youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com",
    # Twitter/X
    "twitter.com", "x.com", "t.co",
}

# yt-dlp Format-Strings pro Qualitätsstufe
QUALITY_FORMATS = {
    "best":  "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "audio": "bestaudio/best",
}

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "downloads")

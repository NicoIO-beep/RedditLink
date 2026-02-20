import os

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Erlaubte Reddit-Domains (erweiterbar)
ALLOWED_DOMAINS = {"reddit.com", "www.reddit.com", "old.reddit.com", "redd.it"}

# Temp-Ordner für Downloads
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "downloads")

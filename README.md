# RedditLink

Lokale Web-App zum Herunterladen von Videos von Reddit, YouTube und Twitter/X als MP4 (oder MP3).

Kein Account, kein Cloud-Upload — läuft komplett auf deinem Rechner.

---

## Features

- Reddit, YouTube, Twitter/X Videos herunterladen
- Qualitätsauswahl: Beste / 1080p / 720p / 480p / Nur Audio (MP3)
- Vorschau mit Thumbnail, Titel und Dauer vor dem Download
- Echtzeit-Fortschrittsbalken während des Downloads
- Temporäre Dateien werden automatisch gelöscht

---

## Voraussetzungen

- Python 3.10+
- FFmpeg wird automatisch mitinstalliert (kein manuelles Setup nötig)

---

## Installation

```bash
git clone https://github.com/NicoIO-beep/RedditLink
cd RedditLink
pip install -r requirements.txt
```

## Starten

```bash
python main.py
```

Dann im Browser öffnen: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Konfiguration (optional)

Standardmäßig läuft der Server auf `127.0.0.1:8000`. Das kann über Umgebungsvariablen geändert werden:

```bash
# Beispiel: anderen Port nutzen
PORT=9000 python main.py
```

Alle verfügbaren Variablen stehen in `.env.example`.

@echo off
cd /d "%~dp0"

:: Prüfen ob Python verfügbar ist
where python >nul 2>&1
if errorlevel 1 (
    echo Python nicht gefunden. Bitte Python installieren.
    pause
    exit /b 1
)

:: Prüfen ob Port 8000 schon belegt ist
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo Server läuft bereits. Öffne Browser...
    start "" "http://127.0.0.1:8000"
    exit /b 0
)

:: Server starten (im Hintergrund)
echo RedditLink wird gestartet...
start /b python main.py

:: Kurz warten bis Server hochgefahren ist
timeout /t 3 /nobreak >nul

:: Browser öffnen
start "" "http://127.0.0.1:8000"

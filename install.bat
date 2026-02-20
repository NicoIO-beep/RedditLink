@echo off
cd /d "%~dp0"
title RedditLink Setup

echo.
echo  RedditLink - Ersteinrichtung
echo  ============================
echo.

:: Python prüfen
where python >nul 2>&1
if errorlevel 1 (
    echo  [FEHLER] Python nicht gefunden.
    echo.
    echo  Bitte Python installieren: https://www.python.org/downloads/
    echo  Haken setzen bei "Add Python to PATH"!
    echo.
    pause
    exit /b 1
)

echo  Python gefunden. Installiere Abhängigkeiten...
echo.
python -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo  [FEHLER] Installation fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo  Erstellung der Extension-Icons...
python make_icons.py

echo.
echo  ============================
echo  Installation abgeschlossen!
echo.
echo  Naechste Schritte:
echo  1. start.bat doppelklicken um den Server zu starten
echo  2. Chrome Extension installieren:
echo     - chrome://extensions aufrufen
echo     - Entwicklermodus einschalten
echo     - "Entpackte Erweiterung laden" - Ordner: extension\
echo.
pause

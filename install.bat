@echo off
title Bricklet Project - Installer
echo ==========================================
echo  Bricklet Project - Installer
echo ==========================================
echo.
echo [1/3] Erstelle virtuelle Umgebung...
python -m venv venv
echo.
echo [2/3] Aktiviere Umgebung...
call venv\Scripts\activate
echo.
echo [3/3] Installiere Abhaengigkeiten...
pip install -r requirements.txt
echo.
echo ==========================================
echo  Installation abgeschlossen!
echo  Starte GUI:     run_gui.bat
echo  Starte Konsole: run_monitor.bat
echo ==========================================
pause

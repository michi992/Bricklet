Kopieren

@echo off
title Bricklet Project - Installer
echo ==========================================
echo  Bricklet Project - Installer
echo ==========================================
 
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte Python von https://python.org installieren.
    pause
    exit /b
)
 
echo Installiere tinkerforge und weitere Module...
pip install tinkerforge Pillow numpy
 
echo.
echo Fertig! Starte jetzt run_gui.bat
pause
 
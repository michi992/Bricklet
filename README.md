# Serverraum-Überwachung – Tinkerforge Bricklet Project

## Projektübersicht
Automatisierte Serverraum-Überwachung mit Tinkerforge-Hardware (IHK-Projekt).

## Hardware-Konfiguration
| Komponente         | UID  | Funktion                        |
|--------------------|------|---------------------------------|
| PTC Bricklet 2.0   | Wcg  | Temperaturmessung               |
| Ambient Light 3.0  | Pdw  | Helligkeitsmessung              |
| Humidity 2.0       | ViW  | Feuchtigkeitsmessung            |
| Motion Detector 2.0| ML4  | Bewegungserkennung              |
| RGB LED Button     | 23Qx | Eingabe + farbige LED           |
| Dual Button 2.0    | Vd8  | Manueller Abruf / Full Reset    |
| NFC Bricklet       | 22ND | Zugangskontrolle                |
| Piezo Speaker 2.0  | R7M  | Alarm-Töne / Imperial March     |
| E-Paper 296x128    | 24KJ | Statusanzeige / NFC-Prompt      |
| Segment Display 4x7| Tre  | Uhr- / Datumsanzeige            |
| LCD 128x64         | 24Rh | Sensordaten + Flappy Bird       |

**Master Brick IDs:** 68WXq6, 62D7kk, 6nCVXX  
**Host:** 172.20.10.242 | **Port:** 4223

## Installation
1. Python 3.x installieren
2. `install.bat` doppelklicken
3. GUI starten: `run_gui.bat`

## Dateistruktur
```
bricklet_project/
├── config.py          – IPs, UIDs, Schwellenwerte
├── sensors.py         – Temperatur, Licht, Feuchte
├── display_manager.py – LCD, Segment, E-Paper
├── alarm_system.py    – Piezo Speaker / Melodien
├── nfc_auth.py        – Zugangskontrolle per NFC
├── flappy_logic.py    – Easter Egg (Flappy Bird)
├── ip_pool.py         – IP-Slot-Verwaltung
├── gui_control.py     – Admin Dashboard (tkinter)
├── main.py            – Konsolenmodus
├── requirements.txt   – Python-Abhängigkeiten
├── install.bat        – Einmalige Installation
├── run_gui.bat        – GUI starten
└── run_monitor.bat    – Konsolenmodus starten
```

## Easter Egg
**Aktivierung:** RGB-Button + Dual-Links + Dual-Rechts gleichzeitig drücken  
**Beenden:** Dual-Links, dann Dual-Rechts drücken  
→ Flappy Bird läuft auf dem LCD-Display!

## NFC-Karte registrieren
Beim ersten Start von `nfc_auth.py` die Karte scannen –
die ID wird automatisch als Admin-Karte gespeichert.

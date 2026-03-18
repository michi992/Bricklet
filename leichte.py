#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "172.20.10.242"
PORT = 4223
UID = "R7M"

import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2

# Ludwig van Beethoven - Fuer Elise (WoO 59)
# Tonart: A-Moll
# Klassiker - klingt auf jedem Piezo-Speaker perfekt
# (frequency_hz, duration_ms)

FUER_ELISE = [
    # Hauptthema
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (494, 125),   # B4
    (587, 125),   # D5
    (523, 125),   # C5
    (440, 250),   # A4
    (0,   125),
    (261, 125),   # C3
    (330, 125),   # E3
    (440, 125),   # A3
    (494, 250),   # B4
    (0,   125),
    (330, 125),   # E3
    (415, 125),   # Ab3
    (494, 125),   # B4
    (523, 250),   # C5
    (0,   125),
    (330, 125),   # E3
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (494, 125),   # B4
    (587, 125),   # D5
    (523, 125),   # C5
    (440, 250),   # A4
    (0,   125),
    (261, 125),   # C3
    (330, 125),   # E3
    (440, 125),   # A3
    (494, 250),   # B4
    (0,   125),
    (330, 125),   # E3
    (523, 125),   # C5
    (494, 125),   # B4
    (440, 375),   # A4
    (0,   250),

    # Mittelteil A
    (494, 125),   # B4
    (523, 125),   # C5
    (587, 125),   # D5
    (659, 250),   # E5
    (0,   125),
    (392, 125),   # G4
    (415, 125),   # Ab4 (Fis)
    (440, 125),   # A4  (eigentl. Gis)
    (494, 250),   # B4
    (0,   125),
    (330, 125),   # E4
    (440, 125),   # A4
    (494, 125),   # B4
    (523, 250),   # C5
    (0,   125),
    (330, 125),   # E4
    (494, 125),   # B4
    (523, 125),   # C5
    (587, 250),   # D5
    (0,   125),
    (330, 125),   # E4
    (659, 250),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (494, 125),   # B4
    (587, 125),   # D5
    (523, 125),   # C5
    (440, 250),   # A4
    (0,   125),
    (261, 125),   # C3
    (330, 125),   # E3
    (440, 125),   # A3
    (494, 250),   # B4
    (0,   125),
    (330, 125),   # E3
    (415, 125),   # Ab3
    (494, 125),   # B4
    (523, 250),   # C5
    (0,   125),
    (330, 125),   # E3
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (622, 125),   # Eb5
    (659, 125),   # E5
    (494, 125),   # B4
    (587, 125),   # D5
    (523, 125),   # C5
    (440, 250),   # A4
    (0,   125),
    (261, 125),   # C3
    (330, 125),   # E3
    (440, 125),   # A3
    (494, 250),   # B4
    (0,   125),
    (330, 125),   # E3
    (523, 125),   # C5
    (494, 125),   # B4
    (440, 500),   # A4 - Schlusston
    (0,   500),
]

def play_note(ps, freq, duration_ms):
    if freq == 0:
        time.sleep(duration_ms / 1000.0)
    else:
        ps.set_beep(freq, 0, duration_ms)
        time.sleep(duration_ms / 1000.0 + 0.02)

if __name__ == "__main__":
    ipcon = IPConnection()
    ps = BrickletPiezoSpeakerV2(UID, ipcon)

    ipcon.connect(HOST, PORT)

    print("Spiele Fuer Elise - Beethoven...")
    for freq, duration in FUER_ELISE:
        play_note(ps, freq, duration)

    print("Fertig.")
    input("Druecke Enter zum Beenden\n")
    ipcon.disconnect()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "172.20.10.242"
PORT = 4223
UID = "R7M"

import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2

# John Williams - Duel of the Fates (Star Wars Episode I)
# Tonart: D-Moll
# (frequency_hz, duration_ms)

DUEL_OF_FATES = [
    # Hauptthema - "KOH-ruh SAH-vah..."
    (293, 125),   # D4
    (329, 125),   # E4
    (349, 125),   # F4
    (440, 375),   # A4
    (0,   125),
    (415, 125),   # Ab4
    (0,   125),
    (440, 375),   # A4
    (0,   125),
    (349, 125),   # F4
    (0,   125),
    (440, 500),   # A4
    (0,   250),

    # Wiederholung Hauptthema
    (293, 125),   # D4
    (329, 125),   # E4
    (349, 125),   # F4
    (440, 375),   # A4
    (0,   125),
    (415, 125),   # Ab4
    (0,   125),
    (440, 375),   # A4
    (0,   125),
    (349, 125),   # F4
    (0,   125),
    (440, 500),   # A4
    (0,   250),

    # Mittelteil - aufsteigend dramatisch
    (440, 125),   # A4
    (494, 125),   # B4
    (523, 125),   # C5
    (587, 250),   # D5
    (523, 125),   # C5
    (494, 125),   # B4
    (440, 250),   # A4
    (0,   125),

    (392, 125),   # G4
    (440, 125),   # A4
    (494, 125),   # B4
    (523, 250),   # C5
    (494, 125),   # B4
    (440, 125),   # A4
    (392, 250),   # G4
    (0,   125),

    # Dramatischer Abstieg
    (349, 125),   # F4
    (392, 125),   # G4
    (440, 125),   # A4
    (494, 250),   # B4
    (440, 125),   # A4
    (392, 125),   # G4
    (349, 250),   # F4
    (0,   125),

    (330, 125),   # E4
    (349, 125),   # F4
    (392, 125),   # G4
    (440, 250),   # A4
    (392, 125),   # G4
    (349, 125),   # F4
    (329, 375),   # E4
    (0,   250),

    # Hauptthema - Reprise, eine Oktave hoeher (intensiver)
    (587, 125),   # D5
    (659, 125),   # E5
    (698, 125),   # F5
    (880, 375),   # A5
    (0,   125),
    (831, 125),   # Ab5
    (0,   125),
    (880, 375),   # A5
    (0,   125),
    (698, 125),   # F5
    (0,   125),
    (880, 500),   # A5
    (0,   250),

    # Wiederholung hoch
    (587, 125),   # D5
    (659, 125),   # E5
    (698, 125),   # F5
    (880, 375),   # A5
    (0,   125),
    (831, 125),   # Ab5
    (0,   125),
    (880, 375),   # A5
    (0,   125),
    (698, 125),   # F5
    (0,   125),
    (880, 500),   # A5
    (0,   250),

    # Brücke - schnelle Sechzehntel
    (880, 125),   # A5
    (831, 125),   # Ab5
    (784, 125),   # G5
    (740, 125),   # F#5
    (698, 125),   # F5
    (659, 125),   # E5
    (622, 125),   # Eb5
    (587, 125),   # D5
    (0,   125),

    (554, 125),   # Db5
    (523, 125),   # C5
    (494, 125),   # B4
    (466, 125),   # Bb4
    (440, 125),   # A4
    (415, 125),   # Ab4
    (392, 125),   # G4
    (349, 125),   # F4
    (0,   250),

    # Finale - Hauptthema mit langen Schlusstönen
    (293, 125),   # D4
    (329, 125),   # E4
    (349, 125),   # F4
    (440, 375),   # A4
    (0,   125),
    (415, 125),   # Ab4
    (0,   125),
    (440, 375),   # A4
    (0,   125),
    (349, 125),   # F4
    (0,   125),
    (440, 750),   # A4 - lang ausklingen
    (0,   125),
    (415, 375),   # Ab4
    (0,   125),
    (392, 375),   # G4
    (0,   125),
    (349, 1000),  # F4 - Schlussnote

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

    print("Spiele Duel of the Fates...")
    for freq, duration in DUEL_OF_FATES:
        play_note(ps, freq, duration)

    print("Fertig.")
    input("Druecke Enter zum Beenden\n")
    ipcon.disconnect()
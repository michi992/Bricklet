#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Ist für schwere Probleme gedacht


HOST = "172.20.10.242"
PORT = 4223
UID = "R7M"

import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2

# Imperial March notes: (frequency_hz, duration_ms)
IMPERIAL_MARCH = [
    # "Dum dum dum, dum da-dum..."
    (440, 500),   # A4
    (440, 500),   # A4
    (440, 500),   # A4
    (349, 375),   # F4
    (523, 125),   # C5
    (440, 500),   # A4
    (349, 375),   # F4
    (523, 125),   # C5
    (440, 750),   # A4

    (0,   250),   # pause

    (659, 500),   # E5
    (659, 500),   # E5
    (659, 500),   # E5
    (698, 375),   # F5
    (523, 125),   # C5
    (415, 500),   # Ab4
    (349, 375),   # F4
    (523, 125),   # C5
    (440, 750),   # A4

    (0,   250),   # pause

    (880, 500),   # A5
    (440, 375),   # A4
    (440, 125),   # A4
    (880, 500),   # A5
    (831, 375),   # Ab5
    (784, 125),   # G5
    (740, 125),   # F#5
    (698, 125),   # F5
    (740, 250),   # F#5

    (0,   250),   # pause

    (455, 250),   # Bb4
    (622, 500),   # Eb5
    (587, 375),   # D5
    (554, 125),   # Db5
    (523, 125),   # C5
    (494, 125),   # B4
    (523, 250),   # C5

    (0,   250),   # pause

    (349, 250),   # F4
    (415, 500),   # Ab4
    (349, 375),   # F4
    (415, 125),   # Ab4 (leicht versetzt fuer Swing)
    (523, 500),   # C5
    (440, 375),   # A4
    (523, 125),   # C5
    (659, 750),   # E5
]

def play_note(ps, freq, duration_ms):
    if freq == 0:
        time.sleep(duration_ms / 1000.0)
    else:
        ps.set_beep(freq, 0, duration_ms)
        time.sleep(duration_ms / 1000.0 + 0.02)  # kleine Pause zwischen Noten

if __name__ == "__main__":
    ipcon = IPConnection()
    ps = BrickletPiezoSpeakerV2(UID, ipcon)

    ipcon.connect(HOST, PORT)

    print("Spielet den Imperialen Marsch...")
    for freq, duration in IMPERIAL_MARCH:
        play_note(ps, freq, duration)

    print("Fertig.")
    input("Druecke Enter zum Beenden\n")
    ipcon.disconnect()
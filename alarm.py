#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "172.20.10.242"
PORT = 4223
UID = "R7M"

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    ps = BrickletPiezoSpeakerV2(UID, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # 10 seconds of loud annoying fast alarm
    ps.set_alarm(800, 2000, 10, 1, 10, 10000)

    input("Press key to exit\n") # Use raw_input() in Python 2
    ipcon.disconnect()
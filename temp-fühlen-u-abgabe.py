#Abgabe der Daten vom Temeparatur fühler an DV1 zur analyise und weiterverarbeitung, bei dem Algorythmus Diablo um die Veränderungenb über längere Zeit zu Dokumentieren undWarnungen rauzugeben, wenn ein möglicher defekt der Klimation enthalten ist oder wenn die Werte an bestimmten Uhrzeiten immer steiegn
#/usr/bin/env python
# -*- coding: utf-8 -*-

#=============================================================
# Dokumentation: des Fühler und Daten weiter leitung an ein Algorthmus Diablo, um die Veränderungen über längere Zeit zu Dokumentieren und Warnungen rauszugeben, wenn ein möglicher defekt der Klimation enthalten ist oder wenn die Werte an bestimmten Uhrzeiten immer steiegn
#gefährunf der Umgebungstemparatur besteht. 
#============================================================= 


from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc_v2 import BrickletPTCV2
import subprocess

HOST = "172.20.10.242"
PORT = 4223
UID = "Wcg"

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    ptc = BrickletPTCV2(UID, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # Get current temperature
    temperature = ptc.get_temperature()
    print("Temperature: " + str(temperature/100.0) + " °C")

    input("Press key to exit\n") # Use raw_input() in Python 2
    ipcon.disconnect()


def verarbeiten(daten):
    subprocess.run(["python", "diablo.py", str(daten)])
    return "Daten verarbeitet und an Diablo weitergeleitet"

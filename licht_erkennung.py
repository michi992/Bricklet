from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc_v2 import BrickletPTCV2
from ki import PORT
from ki import HOST
UID = "Pdw"

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    ptc = BrickletPTCV2(UID, ipcon) # Create device object
    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected
    # Get current Illuminace
    illuminance = ptc.get_illuminance()
    print("Illuminance: " + str(illuminance) + " lx")
    daten = illuminance
    dateiname = "licht_daten.txt"
    with open(dateiname, "a") as datei:
        datei.write(str(daten) + "\n")
    ipcon.disconnect()

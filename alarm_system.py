from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2
import config
import time

# Imperial March Noten: (Frequenz Hz, Dauer ms)
IMPERIAL_MARCH = [
    (440, 500), (440, 500), (440, 500), (349, 375), (523, 125),
    (440, 500), (349, 375), (523, 125), (440, 1000),
    (659, 500), (659, 500), (659, 500), (698, 375), (523, 125),
    (415, 500), (349, 375), (523, 125), (440, 1000),
]

VOLUME = 1  # Max laut Tinkerforge API

def play_alarm():
    """Einfacher Alarm-Beep."""
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ps = BrickletPiezoSpeakerV2(config.UIDS["SPEAKER"], ipcon)
        for _ in range(3):
            ps.set_beep(880, VOLUME, 300)
            time.sleep(0.4)
            ps.set_beep(440, VOLUME, 300)
            time.sleep(0.4)
    finally:
        ipcon.disconnect()

def play_imperial_march():
    """Spielt den Imperial March."""
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ps = BrickletPiezoSpeakerV2(config.UIDS["SPEAKER"], ipcon)
        for freq, dur in IMPERIAL_MARCH:
            ps.set_beep(freq, VOLUME, dur)
            time.sleep(dur / 1000.0 + 0.05)
    finally:
        ipcon.disconnect()

if __name__ == "__main__":
    play_alarm()
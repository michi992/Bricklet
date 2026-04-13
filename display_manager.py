from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_e_paper_296x128 import BrickletEPaper296x128
import config
import time

def show_on_segment(mode="time"):
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        sd = BrickletSegmentDisplay4x7V2(config.UIDS["SEGMENT"], ipcon)
        now = time.localtime()
        if mode == "time":
            digits = [now.tm_hour // 10, now.tm_hour % 10,
                      now.tm_min // 10,  now.tm_min % 10]
        else:
            digits = [now.tm_mday // 10, now.tm_mday % 10,
                      now.tm_mon // 10,  now.tm_mon % 10]
        for i, d in enumerate(digits):
            sd.set_selected_segment(i, d)
    finally:
        ipcon.disconnect()

def update_lcd(metrics):
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        lcd.clear_display()
        lcd.write_line(0, 0, f"Temp:  {metrics['temp']:.1f} C")
        lcd.write_line(1, 0, f"Licht: {metrics['lux']:.1f} lx")
        lcd.write_line(2, 0, f"Hum:   {metrics['hum']:.1f} %")
        lcd.write_line(4, 0, time.strftime("Zeit: %H:%M:%S"))
    finally:
        ipcon.disconnect()

def epaper_show_status(text_lines):
    """Zeigt bis zu 3 Zeilen auf dem E-Paper an."""
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ep = BrickletEPaper296x128(config.UIDS["EPAPER"], ipcon)
        ep.fill_display(BrickletEPaper296x128.COLOR_WHITE)
        for i, line in enumerate(text_lines[:3]):
            ep.draw_text(10, 10 + i * 30, BrickletEPaper296x128.FONT_18X32,
                         BrickletEPaper296x128.COLOR_BLACK, line)
        ep.draw()
    finally:
        ipcon.disconnect()

def epaper_scan_prompt():
    epaper_show_status(["Bewegung erkannt!", "Bitte NFC-Karte", "scannen..."])

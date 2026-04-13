import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_e_paper_296x128 import BrickletEPaper296x128
import config

_segment_mode = "time"

def toggle_segment_mode():
    global _segment_mode
    _segment_mode = "date" if _segment_mode == "time" else "time"
    return _segment_mode

def show_on_segment():
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        sd = BrickletSegmentDisplay4x7V2(config.UIDS["SEGMENT"], ipcon)
        now = time.localtime()
        if _segment_mode == "time":
            h1 = now.tm_hour // 10
            h2 = now.tm_hour % 10
            m1 = now.tm_min // 10
            m2 = now.tm_min % 10
        else:
            h1 = now.tm_mday // 10
            h2 = now.tm_mday % 10
            m1 = now.tm_mon // 10
            m2 = now.tm_mon % 10

        # Segmente: 0=oben, 1=oben-rechts, 2=unten-rechts, 3=unten,
        #           4=unten-links, 5=oben-links, 6=mitte
        DIGITS = {
            0: [True, True, True, True, True, True, False],
            1: [False, True, True, False, False, False, False],
            2: [True, True, False, True, True, False, True],
            3: [True, True, True, True, False, False, True],
            4: [False, True, True, False, False, True, True],
            5: [True, False, True, True, False, True, True],
            6: [True, False, True, True, True, True, True],
            7: [True, True, True, False, False, False, False],
            8: [True, True, True, True, True, True, True],
            9: [True, True, True, True, False, True, True],
        }

        sd.set_segments(DIGITS[h1], DIGITS[h2], DIGITS[m1], DIGITS[m2], True)
    except Exception as e:
        print(f"[Segment] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass

def update_lcd(metrics, extra_line=None):
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        lcd.clear_display()
        lcd.write_line(0, 0, f"Temp:  {metrics['temp']} C")
        lcd.write_line(1, 0, f"Licht: {metrics['lux']} lx")
        lcd.write_line(2, 0, f"Feuch: {metrics['hum']} %")
        if extra_line:
            lcd.write_line(3, 0, extra_line[:22])
    except Exception as e:
        print(f"[LCD] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass

def epaper_show_scan_prompt():
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ep = BrickletEPaper296x128(config.UIDS["EPAPER"], ipcon)
        ep.fill_display(ep.COLOR_WHITE)
        ep.draw_text(10, 50, ep.FONT_24X32, ep.COLOR_BLACK, ep.COLOR_WHITE, "NFC Karte scannen")
        ep.draw()
    except Exception as e:
        print(f"[EPaper] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass

def epaper_show_status(title, line2=""):
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ep = BrickletEPaper296x128(config.UIDS["EPAPER"], ipcon)
        ep.fill_display(ep.COLOR_WHITE)
        ep.draw_text(10, 20, ep.FONT_24X32, ep.COLOR_BLACK, ep.COLOR_WHITE, title[:12])
        if line2:
            ep.draw_text(10, 70, ep.FONT_12X16, ep.COLOR_BLACK, ep.COLOR_WHITE, line2[:24])
        ep.draw()
    except Exception as e:
        print(f"[EPaper] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass

def lcd_show_game_screen(bird_y, score, pipes=None):
    """Flappy Bird auf dem LCD 128x64 (8 Zeilen à 6px, 22 Zeichen breit)"""
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        lcd.clear_display()

        # Zeile 0: Score
        lcd.write_line(0, 0, f"FLAPPY  Score:{score:03d}")

        # Zeilen 1-7 = Spielfeld (7 Zeilen)
        bird_row = max(1, min(7, 1 + int(bird_y / (64 / 7))))

        # Pipes zeichnen
        pipe_cols = []
        if pipes:
            for (px, gap_y) in pipes:
                col = int(px / (128 / 22))
                gap_row_top = max(1, int(gap_y / (64 / 7)))
                gap_row_bot = min(7, gap_row_top + 2)
                pipe_cols.append((col, gap_row_top, gap_row_bot))

        for row in range(1, 8):
            line = [" "] * 22
            # Vogel
            if row == bird_row:
                line[2] = ">"
            # Pipes
            for (col, gt, gb) in pipe_cols:
                if 0 <= col < 22:
                    if row < gt or row > gb:
                        line[col] = "|"
            lcd.write_line(row, 0, "".join(line))
    except Exception as e:
        print(f"[LCD-Game] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass
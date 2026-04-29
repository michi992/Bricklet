import os
import time
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_e_paper_296x128 import BrickletEPaper296x128
import config

_segment_mode = "time"
_segment_running = False


def toggle_segment_mode():
    global _segment_mode
    _segment_mode = "date" if _segment_mode == "time" else "time"
    return _segment_mode


def show_on_segment():
    """Aktualisiert die Segmentanzeige einmal."""
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ipcon.set_timeout(3000)
        sd = BrickletSegmentDisplay4x7V2(config.UIDS["SEGMENT"], ipcon)
        now = time.localtime()

        if _segment_mode == "time":
            d1 = now.tm_hour // 10
            d2 = now.tm_hour % 10
            d3 = now.tm_min  // 10
            d4 = now.tm_min  % 10
        else:
            d1 = now.tm_mday // 10
            d2 = now.tm_mday % 10
            d3 = now.tm_mon  // 10
            d4 = now.tm_mon  % 10

        DIGITS = {
            0: [True,  True,  True,  True,  True,  True,  False, False],
            1: [False, True,  True,  False, False, False, False, False],
            2: [True,  True,  False, True,  True,  False, True,  False],
            3: [True,  True,  True,  True,  False, False, True,  False],
            4: [False, True,  True,  False, False, True,  True,  False],
            5: [True,  False, True,  True,  False, True,  True,  False],
            6: [True,  False, True,  True,  True,  True,  True,  False],
            7: [True,  True,  True,  False, False, False, False, False],
            8: [True,  True,  True,  True,  True,  True,  True,  False],
            9: [True,  True,  True,  True,  False, True,  True,  False],
        }

        colon = [True, True] if (now.tm_sec % 2 == 0) else [False, False]
        tick  = False
        sd.set_segments(DIGITS[d1], DIGITS[d2], DIGITS[d3], DIGITS[d4], colon, tick)

    except Exception as e:
        print(f"[Segment] Fehler: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass


def start_segment_loop():
    global _segment_running
    if _segment_running:
        return
    _segment_running = True

    def _loop():
        while _segment_running:
            show_on_segment()
            time.sleep(1)

    threading.Thread(target=_loop, daemon=True).start()


def stop_segment_loop():
    global _segment_running
    _segment_running = False


# ---------------------------------------------------------------------------
# E-Paper: Gollum-Bild anzeigen
# ---------------------------------------------------------------------------

def _load_image_as_bitmap(path, width=296, height=128):
    """
    Lädt ein Bild, skaliert es auf 296x128 und konvertiert es in eine
    1-bit Schwarz/Weiß-Liste (True = schwarz, False = weiß), die das
    E-Paper Bricklet über write_black_white() erwartet.
    Benötigt Pillow: pip install Pillow
    """
    from PIL import Image

    img = Image.open(path).convert("L")          # Graustufen
    img = img.resize((width, height), Image.LANCZOS)
    img = img.point(lambda p: 0 if p < 128 else 255)  # Schwellwert-Dithering

    pixels = list(img.getdata())
    # True = schwarz (Pixel dunkel), False = weiß
    return [p < 128 for p in pixels]


def epaper_show_gollum():
    """
    Zeigt das Gollum-Bild dauerhaft auf dem E-Paper Display.
    Sucht zuerst nach 'gollum_mittelfinger_preview.png',
    dann nach 'middle_finger_preview.png' im Skriptverzeichnis.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "gollum_mittelfinger_preview.png"),
        os.path.join(base_dir, "middle_finger_preview.png"),
    ]

    img_path = None
    for c in candidates:
        if os.path.exists(c):
            img_path = c
            break

    if img_path is None:
        print("[EPaper] Gollum-Bild nicht gefunden – übersprungen.")
        return

    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ipcon.set_timeout(5000)
        ep = BrickletEPaper296x128(config.UIDS["EPAPER"], ipcon)

        bitmap = _load_image_as_bitmap(img_path, width=296, height=128)

        ep.fill_display(ep.COLOR_WHITE)
        # write_black_white erwartet eine Liste von bools (296*128 = 37888 Einträge)
        ep.write_black_white(0, 0, 295, 127, bitmap)
        ep.draw()

        print(f"[EPaper] Gollum angezeigt ({img_path})")

    except Exception as e:
        print(f"[EPaper] Fehler beim Anzeigen von Gollum: {e}")
    finally:
        try:
            ipcon.disconnect()
        except:
            pass


# ---------------------------------------------------------------------------
# LCD & E-Paper Hilfsfunktionen (unverändert)
# ---------------------------------------------------------------------------

def update_lcd(metrics, extra_line=None):
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ipcon.set_timeout(3000)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        lcd.clear_display()
        lcd.write_line(0, 0, f"Temp: {metrics['temp']:.1f} C")
        lcd.write_line(1, 0, f"Licht: {metrics['lux']:.1f} lx")
        lcd.write_line(2, 0, f"Feuch: {metrics['hum']:.1f} %")
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
        ipcon.set_timeout(3000)
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
        ipcon.set_timeout(3000)
        ep = BrickletEPaper296x128(config.UIDS["EPAPER"], ipcon)
        ep.fill_display(ep.COLOR_WHITE)
        ep.draw_text(10, 20,  ep.FONT_24X32, ep.COLOR_BLACK, ep.COLOR_WHITE, title[:12])
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
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ipcon.set_timeout(3000)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        lcd.clear_display()
        lcd.write_line(0, 0, f"FLAPPY Score:{score:03d}")

        bird_row = max(1, min(7, 1 + int(bird_y / (64 / 7))))
        pipe_cols = []
        if pipes:
            for (px, gap_y) in pipes:
                col          = int(px / (128 / 22))
                gap_row_top  = max(1, int(gap_y / (64 / 7)))
                gap_row_bot  = min(7, gap_row_top + 2)
                pipe_cols.append((col, gap_row_top, gap_row_bot))

        for row in range(1, 8):
            line = [" "] * 22
            if row == bird_row:
                line[2] = ">"
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

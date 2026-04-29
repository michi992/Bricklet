"""
RGB LED Button – schaltet Segment-Modus (Zeit/Datum) beim Drücken um.
Start: rgb_button.start_rgb_listener() aus gui_control.py aufrufen.
"""

import threading
import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_rgb_led_button import BrickletRGBLEDButton
import config
import display_manager

_ipcon = None
_rgb = None
_running = False


def _on_button_state_changed(button_state):
    """Callback: wird automatisch aufgerufen wenn Button gedrückt/losgelassen wird."""
    if button_state == BrickletRGBLEDButton.BUTTON_STATE_PRESSED:
        mode = display_manager.toggle_segment_mode()
        # LED-Farbe zeigt aktuellen Modus: blau = Zeit, grün = Datum
        if mode == "time":
            _rgb.set_color(0, 0, 200)
        else:
            _rgb.set_color(0, 200, 0)
        print(f"[RGB-Button] Segment-Modus gewechselt → {mode}")


def start_rgb_listener():
    """Startet den RGB-Button-Listener als Hintergrund-Thread."""
    global _running
    if _running:
        return
    _running = True

    def _worker():
        global _ipcon, _rgb
        try:
            _ipcon = IPConnection()
            _ipcon.connect(config.HOST, config.PORT)
            _rgb = BrickletRGBLEDButton(config.UIDS["RGB_BUTTON"], _ipcon)

            # Startzustand: blau = Zeit-Modus
            _rgb.set_color(0, 0, 200)

            # Callback registrieren
            _rgb.register_callback(
                BrickletRGBLEDButton.CALLBACK_BUTTON_STATE_CHANGED,
                _on_button_state_changed,
            )

            print("[RGB-Button] Listener gestartet (blau = Zeit, grün = Datum)")

            # Verbindung offen halten – Callbacks laufen im Hintergrund
            while _running:
                time.sleep(1)

        except Exception as e:
            print(f"[RGB-Button] Fehler: {e}")
        finally:
            try:
                _ipcon.disconnect()
            except Exception:
                pass

    threading.Thread(target=_worker, daemon=True).start()


def stop_rgb_listener():
    """Stoppt den Listener und trennt die Verbindung."""
    global _running
    _running = False

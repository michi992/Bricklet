"""
Serverraum-Ueberwachung - Hauptprogramm (ohne GUI)
Startet mit: python main.py
"""
import time

import config
import sensors
import display_manager
import alarm_system
import easter_egg
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_rgb_led_button import BrickletRGBLEDButton
from tinkerforge.bricklet_dual_button_v2 import BrickletDualButtonV2


def _normalize_pressed(value):
    if isinstance(value, (list, tuple)):
        if not value:
            return False
        return _normalize_pressed(value[0])
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _read_rgb_pressed(rgb_btn):
    try:
        return _normalize_pressed(rgb_btn.get_button_state())
    except Exception:
        return False


def _read_dual_pressed(dual_btn, button_side):
    try:
        state = dual_btn.get_button_state(button_side)
    except TypeError:
        state = dual_btn.get_button_state()
    except Exception:
        return False

    if isinstance(state, (list, tuple)):
        # Some bindings can return both sides at once.
        button_r = getattr(BrickletDualButtonV2, "BUTTON_R",
                           getattr(BrickletDualButtonV2, "BUTTON_RIGHT", 1))
        idx = 1 if button_side == button_r else 0
        if len(state) > idx:
            return _normalize_pressed(state[idx])
        return False

    return _normalize_pressed(state)


def monitoring_loop():
    segment_mode = "time"
    sensor_interval_s = 5.0
    input_tick_s = 0.2
    next_sensor_ts = 0.0
    prev_rgb_pressed = False

    game_mgr = easter_egg.EasterEggManager()
    ipcon_controls = None
    rgb_btn = None
    dual_btn = None

    button_l = getattr(BrickletDualButtonV2, "BUTTON_L",
                       getattr(BrickletDualButtonV2, "BUTTON_LEFT", 0))
    button_r = getattr(BrickletDualButtonV2, "BUTTON_R",
                       getattr(BrickletDualButtonV2, "BUTTON_RIGHT", 1))

    try:
        ipcon_controls = IPConnection()
        ipcon_controls.connect(config.HOST, config.PORT)
        try:
            lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon_controls)
            game_mgr.set_lcd(lcd)
        except Exception as e:
            print(f"Warnung: LCD fuer Flappy nicht verbunden ({e}).")

        try:
            rgb_btn = BrickletRGBLEDButton(config.UIDS["RGB_BUTTON"], ipcon_controls)
        except Exception as e:
            print(f"Warnung: RGB-Button nicht verbunden ({e}).")

        try:
            dual_btn = BrickletDualButtonV2(config.UIDS["DUAL_BUTTON"], ipcon_controls)
        except Exception as e:
            print(f"Warnung: Dual-Button nicht verbunden ({e}).")

        if rgb_btn and dual_btn:
            print("Hardware-Input aktiv: RGB + Dual Buttons verbunden.")
    except Exception as e:
        print(f"Warnung: Hardware-Input nicht verbunden ({e}).")

    print("Serverraum-Ueberwachung gestartet. Strg+C zum Beenden.")
    while True:
        try:
            rgb_pressed = False
            dual_l_pressed = False
            dual_r_pressed = False

            if rgb_btn and dual_btn:
                rgb_pressed = _read_rgb_pressed(rgb_btn)
                dual_l_pressed = _read_dual_pressed(dual_btn, button_l)
                dual_r_pressed = _read_dual_pressed(dual_btn, button_r)
                game_mgr.update_inputs(rgb_pressed, dual_l_pressed, dual_r_pressed)
                game_mgr.tick()

                # RGB button alone toggles segment time/date when game is not active.
                if (rgb_pressed and not prev_rgb_pressed and not game_mgr.is_active
                        and not dual_l_pressed and not dual_r_pressed):
                    segment_mode = "date" if segment_mode == "time" else "time"
                    print(f"Segmentanzeige gewechselt: {segment_mode}")
                prev_rgb_pressed = rgb_pressed

            now = time.time()
            if now >= next_sensor_ts:
                data = sensors.get_all_metrics()
                print(f"[{time.strftime('%H:%M:%S')}] "
                      f"Temp: {data['temp']:.1f}C | "
                      f"Licht: {data['lux']:.1f}lx | "
                      f"Feucht: {data['hum']:.1f}%")

                if not game_mgr.is_active:
                    display_manager.update_lcd(data)
                display_manager.show_on_segment(segment_mode)

                if data["temp"] >= config.TEMP_CRIT:
                    print("!!! KRITISCHER ALARM: Temperatur zu hoch !!!")
                    alarm_system.play_imperial_march()
                elif data["temp"] >= config.TEMP_WARN:
                    print("!!! WARNUNG: Temperatur erhoeht !!!")
                    alarm_system.play_alarm()

                next_sensor_ts = now + sensor_interval_s
        except KeyboardInterrupt:
            print("Programm beendet.")
            break
        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(1)

        time.sleep(input_tick_s)

    if game_mgr.is_active:
        game_mgr.game.stop()
    if ipcon_controls:
        try:
            ipcon_controls.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    monitoring_loop()

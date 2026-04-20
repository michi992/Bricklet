"""
Flappy Bird Easter Egg
Linker Dual-Button  = Flap (fliegen)
Rechter Dual-Button = Beenden
Nach Game Over: automatischer Neustart
"""
import time
import random
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from tinkerforge.bricklet_dual_button_v2 import BrickletDualButtonV2
import config

class FlappyBird:
    COLS = 18
    ROWS = 8

    def __init__(self):
        self.active = False
        self._stop_requested = False
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)
        self._thread = None

    def start(self):
        """Startet das Spiel in einem eigenen Thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_requested = False
        self._thread = threading.Thread(target=self._session_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_requested = True
        self.active = False

    def flap(self):
        if self.active:
            self.bird_row = max(0, self.bird_row - 2)

    def _reset(self):
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)

    def _session_loop(self):
        ipcon = IPConnection()
        try:
            ipcon.connect(config.HOST, config.PORT)
            lcd  = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
            dual = BrickletDualButtonV2(config.UIDS["DUAL_BUTTON"], ipcon)

            # Callback aktivieren (WICHTIG: muss explizit eingeschaltet werden)
            dual.set_state_changed_callback_configuration(True)

            # Callback Signatur: button_l, button_r, led_l, led_r
            # BUTTON_STATE_PRESSED = 0, BUTTON_STATE_RELEASED = 1
            def _on_button(button_l, button_r, led_l, led_r):
                if button_l == BrickletDualButtonV2.BUTTON_STATE_PRESSED:
                    self.flap()
                if button_r == BrickletDualButtonV2.BUTTON_STATE_PRESSED:
                    self.stop()

            dual.register_callback(
                BrickletDualButtonV2.CALLBACK_STATE_CHANGED,
                _on_button
            )

            # Spielschleife: läuft bis Beenden gedrückt
            while not self._stop_requested:
                self._reset()
                self.active = True
                self._show_start(lcd)
                self._game_loop(lcd)
                if not self._stop_requested:
                    self._show_game_over(lcd)

            # Aufräumen
            dual.set_state_changed_callback_configuration(False)
            lcd.clear_display()
            lcd.write_line(0, 0, "Ueberwachung aktiv")

        except Exception as e:
            print(f"[Flappy] Fehler: {e}")
        finally:
            try:
                ipcon.disconnect()
            except:
                pass

    def _show_start(self, lcd):
        lcd.clear_display()
        lcd.write_line(0, 0, "  FLAPPY BIRD!  ")
        lcd.write_line(2, 0, " Links  = Flap  ")
        lcd.write_line(3, 0, " Rechts = Ende  ")
        time.sleep(2)

    def _game_loop(self, lcd):
        while self.active and not self._stop_requested:
            self.bird_row = min(self.ROWS - 1, self.bird_row + 1)
            self.pipe_col -= 1

            if self.pipe_col < 0:
                self.pipe_col = self.COLS - 1
                self.pipe_gap_row = random.randint(1, self.ROWS - 3)
                self.score += 1

            # Kollision
            if self.pipe_col == 2:
                if not (self.pipe_gap_row <= self.bird_row <= self.pipe_gap_row + 2):
                    self.active = False
                    return

            self._draw(lcd)
            time.sleep(0.2)

    def _draw(self, lcd):
        lcd.clear_display()
        for row in range(self.ROWS):
            line = [" "] * self.COLS
            if row == self.bird_row:
                line[2] = ">"
            if 0 <= self.pipe_col < self.COLS:
                if not (self.pipe_gap_row <= row <= self.pipe_gap_row + 2):
                    line[self.pipe_col] = "|"
            lcd.write_line(row, 0, "".join(line))
        lcd.write_line(0, 0, f"Score:{self.score:04d}")

    def _show_game_over(self, lcd):
        lcd.clear_display()
        lcd.write_line(0, 0, "  GAME OVER!    ")
        lcd.write_line(1, 0, f"  Score: {self.score:<8}")
        lcd.write_line(3, 0, "Neustart in 3s..")
        time.sleep(3)
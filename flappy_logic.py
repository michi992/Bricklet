"""
Flappy Bird Easter Egg
Aktivierung: RGB-Button + Dual-Button-Links + Dual-Button-Rechts gleichzeitig
Beenden: Dual-Links allein, dann Dual-Rechts allein
"""
import time
import random
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
import config

class FlappyBird:
    COLS = 18
    ROWS = 8

    def __init__(self):
        self.active = False
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)
        self._thread = None

    def _get_lcd(self):
        """Verbindet sich mit dem LCD und gibt es zurück."""
        ipcon = IPConnection()
        ipcon.connect(config.HOST, config.PORT)
        lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
        return ipcon, lcd

    def start(self):
        if self.active:
            return
        self.active = True
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)
        # Game-Loop in eigenem Thread starten
        self._thread = threading.Thread(target=self._game_loop, daemon=True)
        self._thread.start()

    def flap(self):
        if self.active:
            self.bird_row = max(0, self.bird_row - 2)

    def stop(self):
        self.active = False
        try:
            ipcon, lcd = self._get_lcd()
            lcd.clear_display()
            lcd.write_line(0, 0, "Ueberwachung aktiv")
            ipcon.disconnect()
        except Exception as e:
            print(f"[Flappy] Stop-Fehler: {e}")

    def _game_loop(self):
        """Läuft im Hintergrund und aktualisiert das Spiel alle 200ms."""
        try:
            ipcon, lcd = self._get_lcd()
            # Startbildschirm
            lcd.clear_display()
            lcd.write_line(0, 0, "  FLAPPY BIRD!  ")
            lcd.write_line(1, 0, "Dual-L = Flap   ")
            lcd.write_line(2, 0, "Dual-R = Beenden")
            time.sleep(2)

            while self.active:
                # Schwerkraft
                self.bird_row = min(self.ROWS - 1, self.bird_row + 1)
                self.pipe_col -= 1

                if self.pipe_col < 0:
                    self.pipe_col = self.COLS - 1
                    self.pipe_gap_row = random.randint(1, self.ROWS - 3)
                    self.score += 1

                # Kollision prüfen
                if self.pipe_col == 2:
                    if not (self.pipe_gap_row <= self.bird_row <= self.pipe_gap_row + 2):
                        self._game_over(lcd)
                        ipcon.disconnect()
                        return

                # Zeichnen
                self._draw(lcd)
                time.sleep(0.2)

            ipcon.disconnect()

        except Exception as e:
            print(f"[Flappy] Fehler: {e}")
            self.active = False

    def _draw(self, lcd):
        lcd.clear_display()
        for row in range(self.ROWS):
            line = [" "] * self.COLS
            if row == self.bird_row:
                line[2] = ">"
            if self.pipe_col < self.COLS:
                if not (self.pipe_gap_row <= row <= self.pipe_gap_row + 2):
                    line[self.pipe_col] = "|"
            lcd.write_line(row, 0, "".join(line))
        lcd.write_line(0, 0, f"Score:{self.score:04d}")

    def _game_over(self, lcd):
        self.active = False
        lcd.clear_display()
        lcd.write_line(0, 0, "  GAME OVER!    ")
        lcd.write_line(1, 0, f"  Score: {self.score}      ")
        lcd.write_line(3, 0, "Dual-R=Beenden  ")
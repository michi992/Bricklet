"""
Flappy Bird Easter Egg
Aktivierung: RGB-Button + Dual-Button-Links + Dual-Button-Rechts gleichzeitig
Beenden:     Dual-Links allein, dann Dual-Rechts allein
"""
import time
import random

class FlappyBird:
    COLS = 18   # LCD hat ~18 Zeichen pro Zeile
    ROWS = 8    # LCD 128x64 ~ 8 Textzeilen

    def __init__(self):
        self.active = False
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)
        self._lcd = None

    def set_lcd(self, lcd_bricklet):
        self._lcd = lcd_bricklet

    def start(self):
        self.active = True
        self.bird_row = 4
        self.score = 0
        self.pipe_col = self.COLS - 1
        self.pipe_gap_row = random.randint(1, self.ROWS - 3)
        if self._lcd:
            self._lcd.clear_display()
            self._lcd.write_line(0, 0, "  FLAPPY BIRD!  ")
            self._lcd.write_line(1, 0, "Drueck Dual-L=flap")
            time.sleep(1.5)

    def flap(self):
        if self.active:
            self.bird_row = max(0, self.bird_row - 2)

    def tick(self):
        """Ein Spielschritt. Aufruf ca. alle 200ms."""
        if not self.active:
            return
        # Schwerkraft
        self.bird_row = min(self.ROWS - 1, self.bird_row + 1)
        self.pipe_col -= 1
        if self.pipe_col < 0:
            self.pipe_col = self.COLS - 1
            self.pipe_gap_row = random.randint(1, self.ROWS - 3)
            self.score += 1

        # Kollision
        if self.pipe_col == 2:
            if not (self.pipe_gap_row <= self.bird_row <= self.pipe_gap_row + 2):
                self._game_over()
                return

        self._draw()

    def _draw(self):
        if not self._lcd:
            return
        self._lcd.clear_display()
        # Spielfeld aufbauen
        for row in range(self.ROWS):
            line = [" "] * self.COLS
            # Vogel
            if row == self.bird_row:
                line[2] = ">"
            # Röhre
            if self.pipe_col < self.COLS:
                if not (self.pipe_gap_row <= row <= self.pipe_gap_row + 2):
                    line[self.pipe_col] = "|"
            self._lcd.write_line(row, 0, "".join(line))
        self._lcd.write_line(0, 0, f"Score:{self.score:04d}")

    def _game_over(self):
        self.active = False
        if self._lcd:
            self._lcd.clear_display()
            self._lcd.write_line(0, 0, "  GAME OVER!    ")
            self._lcd.write_line(1, 0, f"  Score: {self.score}      ")
            self._lcd.write_line(3, 0, "Dual-R zum Beenden")

    def stop(self):
        self.active = False
        if self._lcd:
            self._lcd.clear_display()
            self._lcd.write_line(0, 0, "Ueberwachung aktiv")

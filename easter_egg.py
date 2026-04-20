"""
Easter Egg Manager – verwaltet den Triple-Press-Trigger für Flappy Bird.

Aktivierung:  RGB Button + Dual Button Links + Dual Button Rechts gleichzeitig
Beenden:      Dual Links + Dual Rechts gleichzeitig (während Spiel aktiv)
"""

import time

import flappy_logic

class EasterEggManager:
    COMBO_WINDOW_S = 1.0

    def __init__(self):
        self.game = flappy_logic.FlappyBird()
        self._pressed = {
            "rgb": False,
            "dual_l": False,
            "dual_r": False,
        }
        self._pressed_ts = {
            "rgb": 0.0,
            "dual_l": 0.0,
            "dual_r": 0.0,
        }
        self._prev_rgb = False

    def set_lcd(self, lcd_bricklet):
        self.game.set_lcd(lcd_bricklet)

    def set_button(self, btn: str, state: bool):
        """
        btn: "rgb" | "dual_l" | "dual_r"
        state: True = gedrückt, False = losgelassen
        """
        if btn not in self._pressed:
            return
        self._pressed[btn] = state
        if state:
            self._pressed_ts[btn] = time.time()

        # --- Aktivierung ---
        now = time.time()
        combo_in_window = all(
            now - self._pressed_ts[name] <= self.COMBO_WINDOW_S
            for name in ("rgb", "dual_l", "dual_r")
        )
        if combo_in_window and not self.game.active:
            self.game.start()

        # --- Beenden (Dual L + Dual R während Spiel) ---
        if self.game.active and self._pressed["dual_l"] and self._pressed["dual_r"]:
            if not self._pressed["rgb"]:
                self.game.stop()

    def flap(self):
        """Weiterleitung an das Spiel (z.B. durch RGB Button im Spiel-Modus)."""
        self.game.flap()

    def update_inputs(self, rgb_pressed: bool, dual_l_pressed: bool, dual_r_pressed: bool):
        """
        Aktualisiert den Button-Status fuer den Trigger
        und erkennt im Spiel einen RGB-Press als Flap.
        """
        self.set_button("rgb", rgb_pressed)
        self.set_button("dual_l", dual_l_pressed)
        self.set_button("dual_r", dual_r_pressed)

        # Rising edge on RGB button -> flap while game is active.
        if self.game.active and rgb_pressed and not self._prev_rgb:
            self.flap()
        self._prev_rgb = rgb_pressed

    def tick(self):
        """Fuehrt einen Spielschritt aus, falls aktiv."""
        if self.game.active:
            self.game.tick()

    @property
    def is_active(self):
        return self.game.active

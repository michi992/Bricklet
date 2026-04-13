"""
Easter Egg Manager – verwaltet den Triple-Press-Trigger für Flappy Bird.

Aktivierung:  RGB Button + Dual Button Links + Dual Button Rechts gleichzeitig
Beenden:      Dual Links + Dual Rechts gleichzeitig (während Spiel aktiv)
"""

import flappy_logic

class EasterEggManager:
    def __init__(self):
        self.game = flappy_logic.FlappyBird()
        self._pressed = {
            "rgb": False,
            "dual_l": False,
            "dual_r": False,
        }

    def set_button(self, btn: str, state: bool):
        """
        btn: "rgb" | "dual_l" | "dual_r"
        state: True = gedrückt, False = losgelassen
        """
        if btn not in self._pressed:
            return
        self._pressed[btn] = state

        # --- Aktivierung ---
        if all(self._pressed.values()) and not self.game.active:
            self.game.start()

        # --- Beenden (Dual L + Dual R während Spiel) ---
        if self.game.active and self._pressed["dual_l"] and self._pressed["dual_r"]:
            if not self._pressed["rgb"]:
                self.game.stop()

    def flap(self):
        """Weiterleitung an das Spiel (z.B. durch RGB Button im Spiel-Modus)."""
        self.game.flap()

    @property
    def is_active(self):
        return self.game.active

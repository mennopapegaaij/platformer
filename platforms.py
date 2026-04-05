# platform.py
# De Platform klasse — een stuk grond of een zwevend platform.

import arcade
from instellingen import GROND_KLEUR


class Platform:
    """Een platform (een stuk grond waar je op kunt staan)."""

    def __init__(self, x, y, breedte, hoogte):
        # Positie en grootte opslaan
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte

    def teken(self):
        """Teken het platform als een groen rechthoek."""
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y, self.y + self.hoogte,
            GROND_KLEUR
        )
        # Lichtere rand bovenop voor een 3D-effect
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y + self.hoogte - 6, self.y + self.hoogte,
            arcade.color.GREEN
        )

    def raakt(self, px, py, pw, ph):
        """Controleer of de speler dit platform raakt van bovenaf."""
        speler_links = px
        speler_rechts = px + pw
        speler_onder = py
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_boven = self.y + self.hoogte

        # De speler staat op het platform als hij van bovenaf landt
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_onder <= platform_boven and
                speler_boven > platform_boven):
            return True
        return False

    def raakt_van_onder(self, px, py, pw, ph):
        """Controleer of de speler met zijn hoofd tegen de onderkant stoot."""
        speler_links = px
        speler_rechts = px + pw
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_onder = self.y  # Onderkant van het platform

        # Hoofd van de speler raakt de onderkant van het platform
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_boven >= platform_onder and
                py < platform_onder):
            return True
        return False

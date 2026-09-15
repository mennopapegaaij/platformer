# powerup.py
# Power-ups voor de speler.
# Elke power-up heeft een eigen kleur, vorm en effect!

import arcade
import math

# Hoelang een power-up effect duurt (in frames, bij 60fps)
# 1800 frames = 30 seconden
EFFECT_DUUR = 1800


class PowerUp:
    """Basisklasse voor alle power-ups. Wordt opgepakt als de speler eroverheen loopt."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.breedte = 28
        self.hoogte = 28
        self.opgepakt = False   # Is de power-up al opgepakt?
        self._teller = 0        # Telt op voor het wiebel-animatietje

    def bijwerken(self):
        """Laat de power-up een beetje op en neer wiebelen."""
        self._teller += 0.1

    def raakt_speler(self, px, py, pw, ph):
        """Controleer of de speler de power-up aanraakt."""
        return (px < self.x + self.breedte and
                px + pw > self.x and
                py < self.y + self.hoogte and
                py + ph > self.y)

    def toepassen(self, speler):
        """Pas het effect van de power-up toe op de speler."""
        pass

    def teken(self):
        """Teken de power-up."""
        pass

    def _wiebel_y(self):
        """Geeft een kleine op-en-neer beweging terug voor het zweven."""
        return math.sin(self._teller) * 4


class Kogel:
    """Een kogel die de speler schiet. Vliegt horizontaal en raakt vijanden."""

    SNELHEID = 10   # Hoe snel de kogel vliegt (pixels per frame)
    STRAAL = 5      # Grootte van de kogel

    def __init__(self, x, y, richting):
        # Richting: +1 = naar rechts, -1 = naar links
        self.x = x
        self.y = y
        self.richting = richting
        self.actief = True   # False = wegdoen

    def bijwerken(self, level_breedte):
        """Beweeg de kogel en check of hij buiten het scherm is."""
        self.x += self.SNELHEID * self.richting
        if self.x < 0 or self.x > level_breedte:
            self.actief = False

    def raakt_vijand(self, vijand):
        """Controleer of de kogel een vijand raakt."""
        return (self.x + self.STRAAL > vijand.x and
                self.x - self.STRAAL < vijand.x + vijand.breedte and
                self.y + self.STRAAL > vijand.y and
                self.y - self.STRAAL < vijand.y + vijand.hoogte)

    def teken(self):
        """Teken de kogel als een glanzend bolletje."""
        arcade.draw_circle_filled(self.x, self.y, self.STRAAL, arcade.color.YELLOW)
        arcade.draw_circle_filled(self.x, self.y, self.STRAAL - 2, arcade.color.WHITE)


class GroottePowerUp(PowerUp):
    """📏 Word GROOT of KLEIN voor een tijdje.

    soort 'groot' = je wordt groter; soort 'klein' = je wordt kleiner (past door
    smalle gaatjes). Na een tijdje word je weer normaal."""

    def __init__(self, x, y, soort="groot"):
        super().__init__(x, y)
        self.soort = soort

    def toepassen(self, speler):
        if self.soort == "klein":
            speler.zet_grootte(0.6, EFFECT_DUUR)
        else:
            speler.zet_grootte(1.6, EFFECT_DUUR)

    def teken(self):
        y_extra = self._wiebel_y()
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2 + y_extra
        if self.soort == "klein":
            kleur = (90, 190, 255)
            arcade.draw_lrbt_rectangle_outline(cx - 11, cx + 11, cy - 11, cy + 11, kleur, 3)
            # pijltjes naar BINNEN (krimpen)
            arcade.draw_triangle_filled(cx - 2, cy, cx - 8, cy - 5, cx - 8, cy + 5, kleur)
            arcade.draw_triangle_filled(cx + 2, cy, cx + 8, cy - 5, cx + 8, cy + 5, kleur)
        else:
            kleur = (255, 170, 40)
            arcade.draw_lrbt_rectangle_outline(cx - 11, cx + 11, cy - 11, cy + 11, kleur, 3)
            # pijltjes naar BUITEN (groeien)
            arcade.draw_triangle_filled(cx - 9, cy, cx - 3, cy - 5, cx - 3, cy + 5, kleur)
            arcade.draw_triangle_filled(cx + 9, cy, cx + 3, cy - 5, cx + 3, cy + 5, kleur)


class ExtraLevenPowerUp(PowerUp):
    """❤️ Extra leven — je krijgt een extra kans!"""

    def toepassen(self, speler):
        speler.levens += 1

    def teken(self):
        y_extra = self._wiebel_y()
        cx = self.x + self.breedte // 2
        cy = self.y + self.hoogte // 2 + y_extra

        # Teken een hartje (twee cirkels + driehoek)
        arcade.draw_circle_filled(cx - 5, cy + 4, 8, arcade.color.RED)
        arcade.draw_circle_filled(cx + 5, cy + 4, 8, arcade.color.RED)
        arcade.draw_triangle_filled(
            cx - 12, cy + 2,
            cx + 12, cy + 2,
            cx, cy - 10,
            arcade.color.RED
        )

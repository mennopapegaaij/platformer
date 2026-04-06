# powerup.py
# Power-ups voor de speler.
# Elke power-up heeft een eigen kleur, vorm en effect!

import arcade
import math

# Hoelang een power-up effect duurt (in frames, bij 60fps = 5 seconden)
EFFECT_DUUR = 300


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


class SterPowerUp(PowerUp):
    """⭐ Ster — tijdelijk onkwetsbaar! Vijanden kunnen je niet pakken."""

    def toepassen(self, speler):
        speler.onkwetsbaar_timer = EFFECT_DUUR

    def teken(self):
        y_extra = self._wiebel_y()
        cx = self.x + self.breedte // 2
        cy = self.y + self.hoogte // 2 + y_extra

        # Teken een ster als 10 punten (5 punten, afwisselend buiten/binnen)
        punten = []
        for i in range(10):
            hoek = math.radians(i * 36 - 90)
            straal = 14 if i % 2 == 0 else 6
            punten.append(cx + straal * math.cos(hoek))
            punten.append(cy + straal * math.sin(hoek))
        arcade.draw_polygon_filled(
            [(punten[i], punten[i+1]) for i in range(0, len(punten), 2)],
            arcade.color.YELLOW
        )
        arcade.draw_polygon_outline(
            [(punten[i], punten[i+1]) for i in range(0, len(punten), 2)],
            arcade.color.ORANGE, 2
        )


class SnelheidPowerUp(PowerUp):
    """💨 Snelheid — je rent tijdelijk dubbel zo snel!"""

    def toepassen(self, speler):
        speler.snelheid_boost_timer = EFFECT_DUUR

    def teken(self):
        y_extra = self._wiebel_y()
        x = self.x
        y = self.y + y_extra

        # Teken een bliksemschicht (geel/oranje)
        arcade.draw_polygon_filled([
            (x + 18, y + 28),
            (x + 10, y + 16),
            (x + 16, y + 16),
            (x + 8,  y + 0),
            (x + 22, y + 13),
            (x + 15, y + 13),
        ], arcade.color.YELLOW)
        arcade.draw_polygon_outline([
            (x + 18, y + 28),
            (x + 10, y + 16),
            (x + 16, y + 16),
            (x + 8,  y + 0),
            (x + 22, y + 13),
            (x + 15, y + 13),
        ], arcade.color.ORANGE, 2)


class DubbelSprongPowerUp(PowerUp):
    """🦘 Dubbel springen — je kunt nog een keer springen in de lucht!"""

    def toepassen(self, speler):
        speler.dubbel_sprong_timer = EFFECT_DUUR
        speler.heeft_dubbel_gesprongen = False  # Reset zodat hij meteen mag springen

    def teken(self):
        y_extra = self._wiebel_y()
        cx = self.x + self.breedte // 2
        cy = self.y + self.hoogte // 2 + y_extra

        # Teken twee pijlen omhoog (blauw)
        for dx in [-6, 6]:
            arcade.draw_triangle_filled(
                cx + dx - 6, cy + 2,
                cx + dx + 6, cy + 2,
                cx + dx, cy + 14,
                arcade.color.CYAN
            )
            arcade.draw_lrbt_rectangle_filled(
                cx + dx - 3, cx + dx + 3, cy - 10, cy + 2,
                arcade.color.CYAN
            )
        arcade.draw_text("2x", cx - 8, cy - 12, arcade.color.BLUE, 9, bold=True)


class SchietPowerUp(PowerUp):
    """🔫 Schieten — druk op Z om kogels te schieten!"""

    def toepassen(self, speler):
        speler.schiet_timer = EFFECT_DUUR

    def teken(self):
        y_extra = self._wiebel_y()
        x = self.x
        y = self.y + y_extra

        # Teken een simpel pistool-silhouet (oranje/rood)
        # Loop (cilinder)
        arcade.draw_lrbt_rectangle_filled(x + 2, x + 24, y + 12, y + 19, arcade.color.ORANGE)
        # Handvat
        arcade.draw_lrbt_rectangle_filled(x + 14, x + 22, y + 3, y + 13, arcade.color.ORANGE)
        # Rand
        arcade.draw_lrbt_rectangle_outline(x + 2, x + 24, y + 12, y + 19, arcade.color.RED, 2)
        arcade.draw_lrbt_rectangle_outline(x + 14, x + 22, y + 3, y + 13, arcade.color.RED, 2)
        # Klein bolletje als kogel voor het pistool
        arcade.draw_circle_filled(x + 3, y + 15, 4, arcade.color.YELLOW)


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

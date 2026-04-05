# powerup.py
# Power-ups voor de speler.
# Dit bestand is alvast klaargezet voor de toekomst!

import arcade


class PowerUp:
    """Basisklasse voor alle power-ups. Wordt opgepakt als de speler eroverheen loopt."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.breedte = 24
        self.hoogte = 24
        self.opgepakt = False   # Is de power-up al opgepakt?

    def raakt_speler(self, px, py, pw, ph):
        """Controleer of de speler de power-up aanraakt."""
        return (px < self.x + self.breedte and
                px + pw > self.x and
                py < self.y + self.hoogte and
                py + ph > self.y)

    def toepassen(self, speler):
        """Pas het effect van de power-up toe op de speler."""
        pass  # Dit vullen we in bij elke specifieke power-up

    def teken(self):
        """Teken de power-up."""
        pass  # Dit vullen we in bij elke specifieke power-up


# =============================================================
# Hier kun je later power-ups toevoegen! Bijvoorbeeld:
#
# class ExtraLevenPowerUp(PowerUp):
#     """Geeft de speler een extra leven."""
#
#     def teken(self):
#         # Teken een roze hartje
#         arcade.draw_circle_filled(self.x + 12, self.y + 12, 12, arcade.color.PINK)
#
#     def toepassen(self, speler):
#         speler.levens += 1
#
#
# class SnelheidPowerUp(PowerUp):
#     """Maakt de speler tijdelijk sneller."""
#
#     def teken(self):
#         # Teken een geel bliksemschichtje
#         arcade.draw_circle_filled(self.x + 12, self.y + 12, 12, arcade.color.YELLOW)
#
#     def toepassen(self, speler):
#         speler.snelheid_boost = True
# =============================================================

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


class BlokPlatform(Platform):
    """Een blok waar je gewoon OP kunt staan (net als een platform),
    maar het ziet eruit als een stenen blok. Handig voor de racemodus."""

    def teken(self):
        """Teken het blok als een bruin bakstenen blok."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 110, 80))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 60, 40), 3)
        # Voegen (streepjes) voor een bakstenen-look
        arcade.draw_line(x, y + h / 2, x + w, y + h / 2, (90, 60, 40), 2)
        arcade.draw_line(x + w / 2, y, x + w / 2, y + h / 2, (90, 60, 40), 2)
        arcade.draw_line(x + w / 4, y + h / 2, x + w / 4, y + h, (90, 60, 40), 2)
        arcade.draw_line(x + 3 * w / 4, y + h / 2, x + 3 * w / 4, y + h, (90, 60, 40), 2)


class SchuinBlok:
    """Een schuin blok (helling): je loopt er soepel overheen omhoog of omlaag.

    richting "op"  -> loopt omhoog naar rechts  (/)
    richting "af"  -> loopt omhoog naar links   (\\)
    """

    is_schuin = True   # zo weet de speler: hier loop je schuin overheen

    def __init__(self, x, y, breedte, hoogte, richting="op"):
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte
        self.richting = richting

    def hoogte_op(self, px):
        """De hoogte van het loop-oppervlak op wereld-x = px."""
        t = (px - self.x) / self.breedte
        t = max(0.0, min(1.0, t))
        if self.richting == "op":
            return self.y + self.hoogte * t          # links laag, rechts hoog
        return self.y + self.hoogte * (1 - t)        # links hoog, rechts laag

    # De gewone (rechte) botsingen slaan we over — de speler regelt de helling zelf
    def raakt(self, px, py, pw, ph):
        return False

    def raakt_van_onder(self, px, py, pw, ph):
        return False

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        if self.richting == "op":
            punten = [(x, y), (x + w, y), (x + w, y + h)]     # driehoek /
        else:
            punten = [(x, y), (x + w, y), (x, y + h)]         # driehoek \
        arcade.draw_polygon_filled(punten, (150, 110, 80))
        arcade.draw_polygon_outline(punten, (90, 60, 40), 3)


# De soorten blokken die je in de bouwmodus kunt kiezen
BLOK_SOORTEN = ["gewoon", "schuinop", "schuinaf", "half"]
BLOK_NAAM = {"gewoon": "Blok", "schuinop": "Schuin /", "schuinaf": "Schuin \\", "half": "Half"}

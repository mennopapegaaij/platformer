# teleport.py
# Een TELEPORTER: raak je een blauwe aan, dan kom je uit de oranje (en andersom).
# Ze werken in paren: blauw <-> oranje. Zo kun je heen én terug springen!

import arcade

# Bij elke kleur horen twee tinten (buitenring, binnenring)
TELE_KLEUREN = {
    "blauw":  ((40, 120, 230), (150, 200, 255)),
    "oranje": ((230, 130, 30), (255, 200, 120)),
}


class Teleporter:
    """Een teleporter-poortje. `kleur` is "blauw" of "oranje"."""

    def __init__(self, x, y, kleur):
        self.x = x
        self.y = y
        self.breedte = 30
        self.hoogte = 60
        self.kleur = kleur

    def raakt_speler(self, sx, sy, sb, sh):
        """Geeft True als de speler (deels) in de teleporter staat."""
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        """Teken de teleporter als een gekleurde ring met sterretjes erin."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        buiten, binnen = TELE_KLEUREN.get(self.kleur, TELE_KLEUREN["blauw"])
        # Twee ringen over elkaar (zo lijkt het een draaikolk)
        arcade.draw_ellipse_outline(cx, cy, self.breedte, self.hoogte, buiten, 6)
        arcade.draw_ellipse_outline(cx, cy, self.breedte - 12, self.hoogte - 18, binnen, 3)
        # Een paar sterretjes in het midden
        for dy in (-12, 0, 12):
            arcade.draw_circle_filled(cx, cy + dy, 2.5, binnen)


def teken_tele_icoon(kleur, cx, cy):
    """Teken een klein teleporter-icoontje (ook gebruikt in de bouwmodus)."""
    buiten, binnen = TELE_KLEUREN.get(kleur, TELE_KLEUREN["blauw"])
    arcade.draw_ellipse_outline(cx, cy, 18, 26, buiten, 3)
    arcade.draw_circle_filled(cx, cy, 3, binnen)

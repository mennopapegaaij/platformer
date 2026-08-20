# portaal.py
# Een PORTAAL zoals in Geometry Dash!
# Vlieg je er doorheen, dan verander je van vorm:
#   - soort "vlucht" -> je wordt een vliegtuig (vliegen)
#   - soort "blok"   -> je wordt weer het gewone blokje (lopen/springen)

import arcade


class Portaal:
    """Een poortje waar je doorheen gaat om van vorm te wisselen."""

    def __init__(self, x, y, soort):
        self.x = x
        self.y = y
        self.breedte = 30
        self.hoogte = 80          # lekker hoog, zodat je er makkelijk doorheen gaat
        self.soort = soort        # "vlucht" of "blok"

    def raakt_speler(self, sx, sy, sb, sh):
        """Geeft True als de speler (deels) door het portaal heen gaat."""
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        """Teken het portaal als een gekleurde ovale ring met een icoontje."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # Kleur hangt af van het soort portaal
        if self.soort == "vlucht":
            buiten, binnen = (150, 90, 220), (200, 150, 255)   # paars = vliegen
        else:
            buiten, binnen = (60, 170, 90), (150, 230, 170)    # groen = blokje

        # Twee ringen over elkaar
        arcade.draw_ellipse_outline(cx, cy, self.breedte, self.hoogte, buiten, 6)
        arcade.draw_ellipse_outline(cx, cy, self.breedte - 10, self.hoogte - 14, binnen, 3)

        # Icoontje in het midden: een vliegtuigje (driehoek) of een blokje (vierkant)
        if self.soort == "vlucht":
            arcade.draw_triangle_filled(cx - 8, cy - 8, cx - 8, cy + 8, cx + 10, cy,
                                        arcade.color.WHITE)
        else:
            arcade.draw_lrbt_rectangle_filled(cx - 9, cx + 9, cy - 9, cy + 9, (240, 230, 90))

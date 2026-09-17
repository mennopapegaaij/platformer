# checkpoint.py
# Een CHECKPOINT (tussenpunt): raak je het aan tijdens het spelen, dan begin je
# daar weer verder als je doodgaat — je hoeft dan niet helemaal opnieuw!

import arcade


class Checkpoint:
    """Een vlaggetje-tussenpunt. Grijs = nog niet aangeraakt, groen = actief (jouw startpunt)."""

    def __init__(self, x, y, grootte=40):
        self.x = x
        self.y = y
        self.breedte = grootte
        self.hoogte = grootte
        self.actief = False        # aangeraakt? dan is dit je nieuwe startplek

    def raakt_speler(self, sx, sy, sb, sh):
        """Geeft True als de speler dit checkpoint aanraakt."""
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        """Teken een vlaggenmast met een vlaggetje (groen als hij aanstaat)."""
        paal_x = self.x + 8
        onder = self.y + 2
        top = self.y + self.hoogte - 2
        # De mast
        arcade.draw_line(paal_x, onder, paal_x, top, (210, 210, 220), 3)
        # Het wapperende vlaggetje (grijs = uit, felgroen = aan)
        vlag_kleur = (60, 220, 120) if self.actief else (150, 150, 160)
        vt = top - 2
        arcade.draw_triangle_filled(paal_x, vt, paal_x + 18, vt - 6, paal_x, vt - 13, vlag_kleur)
        arcade.draw_triangle_outline(paal_x, vt, paal_x + 18, vt - 6, paal_x, vt - 13, (60, 60, 70), 1)
        # Bolletje bovenop de mast
        arcade.draw_circle_filled(paal_x, top, 3, (255, 230, 90))
        # Een gloed-ring als het checkpoint aanstaat
        if self.actief:
            arcade.draw_circle_outline(paal_x + 6, vt - 6, 15, (120, 255, 170), 1)

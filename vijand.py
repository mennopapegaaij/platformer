# vijand.py
# Alle vijand-klassen.
# Wil je een nieuw soort vijand toevoegen? Doe dat dan hier!

import arcade
from instellingen import VIJAND_SNELHEID, VIJAND_KLEUR, OOG_KLEUR


class Vijand:
    """Een vijand die heen en weer loopt op de grond of een platform."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=VIJAND_SNELHEID):
        self.x = x            # Huidige x-positie
        self.y = y            # Huidige y-positie
        self.breedte = 30     # Breedte van de vijand
        self.hoogte = 30      # Hoogte van de vijand
        self.snelheid = snelheid
        self.links_grens = links_grens    # Tot hier beweegt hij naar links
        self.rechts_grens = rechts_grens  # Tot hier beweegt hij naar rechts

    def bijwerken(self):
        """Beweeg de vijand heen en weer."""
        self.x += self.snelheid

        # Als de vijand een grens bereikt, draai hij om
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid  # Omgekeerde richting

    def teken(self):
        """Teken de vijand als een rood vierkantje met een boos gezicht."""
        # Lijf
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y, self.y + self.hoogte,
            VIJAND_KLEUR
        )
        # Linker oog
        arcade.draw_circle_filled(self.x + 8, self.y + 20, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(self.x + 22, self.y + 20, 4, OOG_KLEUR)
        # Boze wenkbrauwen
        arcade.draw_line(self.x + 4, self.y + 26, self.x + 12, self.y + 23, OOG_KLEUR, 2)
        arcade.draw_line(self.x + 18, self.y + 23, self.x + 26, self.y + 26, OOG_KLEUR, 2)
        # Fronsende mond
        arcade.draw_arc_outline(self.x + 15, self.y + 9, 10, 6, OOG_KLEUR, 190, 350, 2)

    def raakt_speler(self, px, py, pw, ph):
        """Controleer of de vijand de speler raakt (zijkant of van onder)."""
        return (px < self.x + self.breedte and
                px + pw > self.x and
                py < self.y + self.hoogte and
                py + ph > self.y)

    def speler_springt_erop(self, px, py, pw, ph):
        """Controleer of de speler van bovenaf op de vijand springt."""
        speler_onder = py
        vijand_boven = self.y + self.hoogte
        # De speler springt erop als zijn voeten de bovenkant raken
        return (px + pw > self.x + 4 and
                px < self.x + self.breedte - 4 and
                speler_onder <= vijand_boven and
                speler_onder >= vijand_boven - 12)


# =============================================================
# Hier kun je later nieuwe vijanden toevoegen!
# Bijvoorbeeld:
#
# class VliegendVijand(Vijand):
#     """Een vijand die op en neer vliegt."""
#     pass
#
# class SchietendVijand(Vijand):
#     """Een vijand die kogels afvuurt."""
#     pass
# =============================================================

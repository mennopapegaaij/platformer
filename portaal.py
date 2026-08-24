# portaal.py
# Een PORTAAL zoals in Geometry Dash!
# Vlieg je er doorheen, dan verander je van vorm:
#   - soort "vlucht" -> je wordt een vliegtuig (knop vasthouden = omhoog)
#   - soort "blok"   -> je wordt weer het gewone blokje (lopen/springen)
#   - soort "ufo"    -> UFO: elke tik een sprongetje omhoog
#   - soort "bal"    -> bal: elke tik draait de zwaartekracht om
#   - soort "golf"   -> golf: vasthouden = schuin omhoog, loslaten = schuin omlaag

import arcade

# Bij elk soort portaal hoort een kleur (buitenring, binnenring)
PORTAAL_KLEUREN = {
    "vlucht": ((150, 90, 220), (200, 150, 255)),   # paars = vliegtuig
    "blok":   ((60, 170, 90), (150, 230, 170)),    # groen = blokje
    "ufo":    ((40, 150, 210), (150, 210, 255)),   # blauw = UFO
    "bal":    ((230, 140, 40), (255, 200, 120)),   # oranje = bal
    "golf":   ((220, 60, 120), (255, 150, 190)),   # roze = golf
    "robot":  ((90, 140, 70), (170, 210, 130)),    # groen = robot
    "spin":   ((150, 40, 40), (220, 110, 110)),    # donkerrood = spin
    # Snelheid-portalen (veranderen niet je vorm, maar hoe snel je gaat)
    "x0.5":   ((40, 110, 200), (150, 200, 255)),   # blauw = langzaam
    "x1":     ((110, 110, 120), (200, 200, 210)),  # grijs = gewoon
    "x2":     ((60, 170, 90), (150, 230, 170)),    # groen = 2x
    "x5":     ((230, 140, 40), (255, 200, 120)),   # oranje = 5x
    "x10":    ((210, 50, 50), (255, 150, 150)),    # rood = 10x (super snel!)
}

# Snelheid-portalen: welke keer-factor hoort bij welk soort
SNELHEID_FACTOR = {"x0.5": 0.5, "x1": 1.0, "x2": 2.0, "x5": 5.0, "x10": 10.0}


class Portaal:
    """Een poortje waar je doorheen gaat om van vorm te wisselen."""

    def __init__(self, x, y, soort, hoogte=80):
        self.x = x
        self.y = y
        self.breedte = 30
        self.hoogte = hoogte      # hoog genoeg om er makkelijk doorheen te gaan
        self.soort = soort        # "vlucht"/"blok"/"ufo"/... of een snelheid zoals "x2"

    def raakt_speler(self, sx, sy, sb, sh):
        """Geeft True als de speler (deels) door het portaal heen gaat."""
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        """Teken het portaal als een gekleurde ovale ring met een icoontje."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        buiten, binnen = PORTAAL_KLEUREN.get(self.soort, PORTAAL_KLEUREN["blok"])

        # Twee ringen over elkaar
        arcade.draw_ellipse_outline(cx, cy, self.breedte, self.hoogte, buiten, 6)
        arcade.draw_ellipse_outline(cx, cy, self.breedte - 10, self.hoogte - 14, binnen, 3)

        # Een icoontje in het midden dat past bij het soort
        teken_portaal_icoon(self.soort, cx, cy)


def teken_portaal_icoon(soort, cx, cy):
    """Teken het icoontje in het midden van een portaal (ook gebruikt in de bouwmodus)."""
    if soort == "vlucht":
        # Vliegtuigje (driehoek)
        arcade.draw_triangle_filled(cx - 8, cy - 8, cx - 8, cy + 8, cx + 10, cy, arcade.color.WHITE)
    elif soort == "blok":
        # Blokje (vierkant)
        arcade.draw_lrbt_rectangle_filled(cx - 9, cx + 9, cy - 9, cy + 9, (240, 230, 90))
    elif soort == "ufo":
        # UFO (platte ovaal met een bolletje erop)
        arcade.draw_ellipse_filled(cx, cy - 2, 22, 10, arcade.color.WHITE)
        arcade.draw_circle_filled(cx, cy + 5, 6, (200, 240, 255))
    elif soort == "bal":
        # Bal (rondje met een streepje)
        arcade.draw_circle_filled(cx, cy, 10, arcade.color.WHITE)
        arcade.draw_line(cx - 8, cy, cx + 8, cy, (230, 140, 40), 2)
    elif soort == "golf":
        # Golfje (een zigzag-lijntje)
        arcade.draw_line(cx - 10, cy - 6, cx - 3, cy + 6, arcade.color.WHITE, 3)
        arcade.draw_line(cx - 3, cy + 6, cx + 4, cy - 6, arcade.color.WHITE, 3)
        arcade.draw_line(cx + 4, cy - 6, cx + 11, cy + 6, arcade.color.WHITE, 3)
    elif soort == "robot":
        # Robotkopje (vierkant met een antenne)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 7, cy + 7, arcade.color.WHITE)
        arcade.draw_circle_filled(cx - 3, cy, 2, (90, 100, 120))
        arcade.draw_circle_filled(cx + 3, cy, 2, (90, 100, 120))
        arcade.draw_line(cx, cy + 7, cx, cy + 11, arcade.color.WHITE, 2)
    elif soort == "spin":
        # Spinnetje (rondje met pootjes)
        for dx in (-10, 10):
            arcade.draw_line(cx, cy, cx + dx, cy + 8, arcade.color.WHITE, 2)
            arcade.draw_line(cx, cy, cx + dx, cy - 8, arcade.color.WHITE, 2)
        arcade.draw_circle_filled(cx, cy, 7, arcade.color.WHITE)
    elif soort in SNELHEID_FACTOR:
        # Snelheid-portaal: laat de keer-factor zien (bv. "x2")
        arcade.draw_text(soort, cx, cy - 6, arcade.color.WHITE, 11, bold=True, anchor_x="center")

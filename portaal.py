# portaal.py
# Een PORTAAL zoals in Geometry Dash!
# Vlieg je er doorheen, dan verander je van vorm:
#   - soort "vlucht" -> je wordt een vliegtuig (knop vasthouden = omhoog)
#   - soort "blok"   -> je wordt weer het gewone blokje (lopen/springen)
#   - soort "ufo"    -> UFO: elke tik een sprongetje omhoog
#   - soort "bal"    -> bal: elke tik draait de zwaartekracht om
#   - soort "golf"   -> golf: vasthouden = schuin omhoog, loslaten = schuin omlaag

import arcade
import math

# Bij elk soort portaal hoort een kleur (buitenring, binnenring)
PORTAAL_KLEUREN = {
    "vlucht": ((150, 90, 220), (200, 150, 255)),   # paars = vliegtuig
    "blok":   ((60, 170, 90), (150, 230, 170)),    # groen = blokje
    "ufo":    ((40, 150, 210), (150, 210, 255)),   # blauw = UFO
    "bal":    ((230, 140, 40), (255, 200, 120)),   # oranje = bal
    "golf":   ((220, 60, 120), (255, 150, 190)),   # roze = golf
    "robot":  ((90, 140, 70), (170, 210, 130)),    # groen = robot
    "spin":   ((150, 40, 40), (220, 110, 110)),    # donkerrood = spin
    "heli":   ((40, 130, 180), (150, 210, 240)),   # lichtblauw = helikopter
    "draaibol": ((30, 150, 140), (120, 230, 210)), # groenblauw = draaibol
    "ballon": ((220, 90, 130), (255, 170, 200)),   # rozerood = ballon
    "raket":  ((200, 50, 50), (255, 140, 90)),     # vuurrood = raket
    "kolibrie": ((30, 160, 140), (140, 235, 210)), # turkoois = kolibrie
    "draak":  ((50, 150, 70), (150, 220, 150)),    # drakengroen = draak
    "ijs":    ((90, 170, 220), (190, 235, 255)),   # ijsblauw = ijsblokje
    "ninja":  ((60, 60, 80), (150, 150, 180)),     # donkergrijs = ninja
    "spiegel": ((120, 150, 190), (210, 230, 250)), # spiegelzilver = spiegel
    "magneet": ((200, 60, 60), (255, 160, 160)),   # magneetrood = magneet
    "flits":  ((220, 200, 40), (255, 245, 150)),   # bliksemgeel = flits
    "dobbelsteen": ((230, 230, 240), (255, 255, 255)),  # wit = dobbelsteen
    "vertraagd": ((190, 160, 90), (235, 215, 160)),     # klok-bruin = vertraagd
    "chaos":  ((150, 60, 200), (210, 150, 250)),        # chaos-paars = chaos
    "dronken": ((90, 180, 90), (170, 230, 170)),        # duizelig groen = dronken
    "turbo":  ((230, 60, 50), (255, 160, 120)),         # racerood = turbo
    "ritme":  ((90, 130, 230), (170, 200, 255)),        # ritmeblauw = ritme-flip
    "stuiteraar": ((255, 140, 40), (255, 210, 150)),    # stuiter-oranje = stuiteraar
    "klimmer": ((130, 90, 200), (200, 170, 245)),       # klimpaars = klimmer
    "dubbel": ((200, 60, 200), (255, 150, 255)),   # magenta = twee van jou
    "enkel":  ((90, 90, 150), (170, 170, 220)),    # blauwgrijs = weer één
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
        verf = getattr(self, "verf_kleur", None)   # verf-kleur (of None)
        if verf:
            buiten = binnen = verf                 # verf vervangt de ring-kleuren

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
    elif soort == "heli":
        # Helikoptertje (bolletje met een rotor-balk erboven en twee pijltjes)
        arcade.draw_line(cx - 10, cy + 6, cx + 10, cy + 6, arcade.color.WHITE, 2)
        arcade.draw_circle_filled(cx, cy - 1, 6, arcade.color.WHITE)
        arcade.draw_line(cx, cy + 5, cx, cy + 6, arcade.color.WHITE, 2)
    elif soort == "draaibol":
        # Bolletje met een draai-pijl eromheen (zwaartekracht draait)
        arcade.draw_circle_filled(cx, cy, 5, arcade.color.WHITE)
        arcade.draw_arc_outline(cx, cy, 20, 20, arcade.color.WHITE, 20, 300, 3)
        arcade.draw_triangle_filled(cx + 8, cy + 6, cx + 12, cy + 2, cx + 4, cy + 2, arcade.color.WHITE)
    elif soort == "ballon":
        # Ballonnetje met een touwtje
        arcade.draw_circle_filled(cx, cy + 3, 7, arcade.color.WHITE)
        arcade.draw_line(cx, cy - 4, cx, cy - 9, arcade.color.WHITE, 2)
    elif soort == "raket":
        # Raketje met een vlammetje eronder
        arcade.draw_lrbt_rectangle_filled(cx - 4, cx + 4, cy - 4, cy + 6, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 4, cy + 6, cx + 4, cy + 6, cx, cy + 12, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 4, cy - 4, cx + 4, cy - 4, cx, cy - 11, (255, 200, 90))
    elif soort == "kolibrie":
        # Vogeltje met een lange snavel
        arcade.draw_ellipse_filled(cx - 2, cy, 10, 7, arcade.color.WHITE)
        arcade.draw_line(cx + 3, cy, cx + 12, cy, arcade.color.WHITE, 2)
        arcade.draw_line(cx - 2, cy, cx - 8, cy + 6, arcade.color.WHITE, 2)
    elif soort == "draak":
        # Drakenkopje met een vlammetje
        arcade.draw_circle_filled(cx, cy, 7, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 7, cy + 4, cx - 12, cy + 10, cx - 3, cy + 8, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 6, cy - 2, cx + 6, cy + 2, cx + 13, cy, (255, 150, 40))
    elif soort == "ijs":
        # IJsblokje met glinstering
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 8, cy + 8, arcade.color.WHITE)
        arcade.draw_line(cx - 5, cy + 5, cx + 2, cy - 2, (150, 210, 240), 2)
    elif soort == "ninja":
        # Ninjakopje met een hoofdband
        arcade.draw_circle_filled(cx, cy, 8, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy, cy + 4, (200, 40, 40))
        arcade.draw_circle_filled(cx - 3, cy - 2, 1.5, (60, 60, 80))
        arcade.draw_circle_filled(cx + 3, cy - 2, 1.5, (60, 60, 80))
    elif soort == "spiegel":
        # Twee pijltjes die naar buiten wijzen (omgedraaide besturing)
        arcade.draw_triangle_filled(cx - 10, cy, cx - 3, cy - 5, cx - 3, cy + 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 10, cy, cx + 3, cy - 5, cx + 3, cy + 5, arcade.color.WHITE)
    elif soort == "magneet":
        # Hoefijzer-magneetje (U-vorm)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 4, cy + 9, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx - 4, cx + 4, cy, cy + 11, (200, 60, 60))
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx - 4, cy - 10, cy - 4, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx + 4, cx + 8, cy - 10, cy - 4, arcade.color.WHITE)
    elif soort == "flits":
        # Bliksemschichtje (zigzag)
        arcade.draw_polygon_filled([(cx + 3, cy + 10), (cx - 5, cy), (cx, cy),
                                    (cx - 4, cy - 10), (cx + 6, cy + 1), (cx + 1, cy + 1)],
                                   arcade.color.WHITE)
    elif soort == "dobbelsteen":
        # Dobbelsteentje met stippen
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 8, cy + 8, arcade.color.WHITE)
        for dx, dy in [(-4, 4), (4, 4), (0, 0), (-4, -4), (4, -4)]:
            arcade.draw_circle_filled(cx + dx, cy + dy, 1.5, (40, 40, 55))
    elif soort == "vertraagd":
        # Klokje
        arcade.draw_circle_filled(cx, cy, 9, arcade.color.WHITE)
        arcade.draw_line(cx, cy, cx, cy + 6, (90, 60, 30), 2)
        arcade.draw_line(cx, cy, cx + 4, cy, (90, 60, 30), 2)
    elif soort == "chaos":
        # Wilde vonkjes
        arcade.draw_circle_filled(cx, cy, 5, arcade.color.WHITE)
        for hoek in (0.4, 1.6, 2.8, 4.0, 5.2):
            arcade.draw_line(cx, cy, cx + math.cos(hoek) * 11, cy + math.sin(hoek) * 11,
                             arcade.color.WHITE, 2)
    elif soort == "dronken":
        # Duizelig gezichtje met spiraal-oogjes
        arcade.draw_circle_outline(cx - 4, cy + 1, 3, arcade.color.WHITE, 1)
        arcade.draw_circle_outline(cx + 4, cy + 1, 3, arcade.color.WHITE, 1)
        arcade.draw_line(cx - 5, cy - 6, cx, cy - 4, arcade.color.WHITE, 2)
        arcade.draw_line(cx, cy - 4, cx + 5, cy - 6, arcade.color.WHITE, 2)
    elif soort == "turbo":
        # Snelheidspijl met streepjes
        arcade.draw_triangle_filled(cx + 8, cy, cx - 2, cy - 8, cx - 2, cy + 8, arcade.color.WHITE)
        arcade.draw_line(cx - 10, cy + 4, cx - 4, cy + 4, arcade.color.WHITE, 2)
        arcade.draw_line(cx - 10, cy - 4, cx - 4, cy - 4, arcade.color.WHITE, 2)
    elif soort == "ritme":
        # Pijl omhoog + pijl omlaag (zwaartekracht flipt op de maat)
        arcade.draw_triangle_filled(cx, cy + 10, cx - 6, cy + 2, cx + 6, cy + 2, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx, cy - 10, cx - 6, cy - 2, cx + 6, cy - 2, arcade.color.WHITE)
    elif soort == "stuiteraar":
        # Stuiterbal met een boogje eronder
        arcade.draw_circle_filled(cx, cy + 2, 7, arcade.color.WHITE)
        arcade.draw_arc_outline(cx, cy - 8, 16, 10, arcade.color.WHITE, 180, 360, 2)
    elif soort == "klimmer":
        # Poppetje tussen twee muurtjes
        arcade.draw_lrbt_rectangle_filled(cx - 11, cx - 8, cy - 10, cy + 10, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx + 8, cx + 11, cy - 10, cy + 10, arcade.color.WHITE)
        arcade.draw_circle_filled(cx, cy, 5, arcade.color.WHITE)
    elif soort in SNELHEID_FACTOR:
        # Snelheid-portaal: laat de keer-factor zien (bv. "x2")
        arcade.draw_text(soort, cx, cy - 6, arcade.color.WHITE, 11, bold=True, anchor_x="center")
    elif soort == "dubbel":
        arcade.draw_text("2", cx, cy - 8, arcade.color.WHITE, 16, bold=True, anchor_x="center")
    elif soort == "enkel":
        arcade.draw_text("1", cx, cy - 8, arcade.color.WHITE, 16, bold=True, anchor_x="center")

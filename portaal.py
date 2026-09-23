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
    "draaisturing": ((60, 100, 190), (150, 180, 240)),  # stuurblauw = draaibesturing
    "boemerang": ((200, 130, 40), (245, 195, 120)),     # hout-oranje = boemerang
    "stamper": ((100, 100, 120), (170, 170, 190)),      # zwaar grijs = stamper
    "zweefspringer": ((120, 190, 240), (200, 230, 255)),# luchtblauw = zweefspringer
    "groeier": ((80, 180, 80), (170, 230, 170)),        # groeigroen = groeier
    "zwaargewicht": ((80, 80, 95), (150, 150, 165)),    # rotsgrijs = zwaargewicht
    "versneller": ((50, 130, 210), (150, 200, 250)),    # snelblauw = versneller
    "wind": ((150, 200, 220), (210, 240, 250)),         # windlichtblauw = wind
    "plakker": ((90, 190, 110), (170, 235, 180)),       # gekkogroen = plakker
    "metronoom": ((200, 160, 40), (250, 220, 120)),     # metronoom-goud = metronoom
    "katapult": ((150, 110, 70), (220, 180, 130)),      # hout-bruin = katapult
    "krimpsprong": ((40, 170, 140), (150, 230, 200)),   # krimp-groenblauw = krimpsprong
    "tegendraads": ((160, 80, 190), (225, 160, 245)),   # tegen-paars = tegendraads
    "turboflip": ((210, 70, 130), (255, 160, 190)),     # turbo-roze = turbo-flip
    "spiegelkatapult": ((120, 140, 180), (200, 215, 240)),  # spiegel-zilver = spiegel-katapult
    "schaduw": ((70, 60, 100), (150, 140, 190)),        # schaduw-paars = schaduw
    "pingpong": ((230, 230, 240), (255, 255, 255)),     # pingpong-wit = ping-pong
    "spook": ((90, 90, 130), (210, 210, 245)),          # spookwit = spook
    "vleermuis": ((60, 40, 90), (150, 110, 190)),       # nachtpaars = vleermuis
    "zombie": ((80, 120, 60), (160, 200, 120)),         # zombiegroen = zombie
    "pompoenkop": ((220, 110, 20), (255, 180, 80)),     # pompoen-oranje = pompoenkop
    "voorspeller": ((70, 110, 200), (170, 200, 250)),   # tijd-blauw = voorspeller
    "pendel": ((200, 120, 60), (245, 190, 140)),        # slinger-bruin = pendel
    "blinde": ((40, 40, 50), (120, 120, 140)),          # donker = blinde
    "dubbelflip": ((150, 60, 120), (230, 150, 210)),    # flip-paars = dubbelflip
    "vijfkamp": ((200, 170, 40), (255, 230, 120)),      # goud = vijfkamp (5 in 1)
    "tienkamp": ((60, 40, 20), (230, 190, 50)),         # zwart-goud = tienkamp (10 in 1)
    "vijftienkamp": ((60, 30, 90), (160, 110, 230)),    # donkerpaars = vijftienkamp (15 in 1)
    "twintigkamp": ((20, 90, 90), (60, 200, 200)),      # turkoois = twintigkamp (20 in 1)
    "element": ((120, 60, 160), (230, 180, 255)),       # paars = elementmeester
    "eigen": ((255, 150, 40), (255, 210, 130)),         # oranje = zelfgemaakt poppetje
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
    elif soort == "draaisturing":
        # Kompas met een ronddraaiende pijl
        arcade.draw_circle_outline(cx, cy, 9, arcade.color.WHITE, 2)
        arcade.draw_line(cx, cy, cx + 7, cy + 5, arcade.color.WHITE, 2)
        arcade.draw_circle_filled(cx + 7, cy + 5, 2, arcade.color.WHITE)
    elif soort == "boemerang":
        # V-vorm van een boemerang
        arcade.draw_line(cx, cy - 5, cx - 9, cy + 8, arcade.color.WHITE, 3)
        arcade.draw_line(cx, cy - 5, cx + 9, cy + 8, arcade.color.WHITE, 3)
    elif soort == "stamper":
        # Dikke pijl naar beneden
        arcade.draw_lrbt_rectangle_filled(cx - 3, cx + 3, cy - 2, cy + 9, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 8, cy - 2, cx + 8, cy - 2, cx, cy - 11, arcade.color.WHITE)
    elif soort == "zweefspringer":
        # Blokje met vleugeltjes
        arcade.draw_lrbt_rectangle_filled(cx - 5, cx + 5, cy - 5, cy + 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 5, cy, cx - 12, cy + 6, cx - 5, cy + 6, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 5, cy, cx + 12, cy + 6, cx + 5, cy + 6, arcade.color.WHITE)
    elif soort == "groeier":
        # Klein blokje met een groter blokje ernaast (groeien)
        arcade.draw_lrbt_rectangle_outline(cx - 10, cx - 3, cy - 4, cy + 3, arcade.color.WHITE, 2)
        arcade.draw_lrbt_rectangle_outline(cx + 1, cx + 11, cy - 8, cy + 8, arcade.color.WHITE, 2)
    elif soort == "zwaargewicht":
        # Gewichtje (kg)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 7, cy + 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 5, cy + 5, cx + 5, cy + 5, cx, cy + 10, arcade.color.WHITE)
    elif soort == "versneller":
        # Snelheidspijl met streepjes
        arcade.draw_triangle_filled(cx + 8, cy, cx - 2, cy - 7, cx - 2, cy + 7, arcade.color.WHITE)
        arcade.draw_line(cx - 10, cy + 3, cx - 4, cy + 3, arcade.color.WHITE, 2)
        arcade.draw_line(cx - 10, cy - 3, cx - 4, cy - 3, arcade.color.WHITE, 2)
    elif soort == "wind":
        # Windvlaagjes (golvende lijntjes)
        for dy in (-4, 4):
            arcade.draw_line(cx - 9, cy + dy, cx + 7, cy + dy, arcade.color.WHITE, 2)
            arcade.draw_line(cx + 7, cy + dy, cx + 3, cy + dy + 3, arcade.color.WHITE, 2)
    elif soort == "plakker":
        # Gekko-oogjes (plakt aan muren)
        arcade.draw_circle_filled(cx - 5, cy + 2, 4, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 5, cy + 2, 4, arcade.color.WHITE)
        arcade.draw_circle_filled(cx - 5, cy + 2, 2, (40, 90, 50))
        arcade.draw_circle_filled(cx + 5, cy + 2, 2, (40, 90, 50))
    elif soort == "metronoom":
        # Metronoom: een driehoekje met een schuine wijzer
        arcade.draw_triangle_outline(cx, cy + 9, cx - 7, cy - 8, cx + 7, cy - 8, arcade.color.WHITE, 2)
        arcade.draw_line(cx, cy - 6, cx + 5, cy + 7, arcade.color.WHITE, 2)
    elif soort == "katapult":
        # Katapult: een boogje met een pijlpunt (wordt weggeschoten)
        arcade.draw_arc_outline(cx, cy - 3, 20, 18, arcade.color.WHITE, 20, 160, 2)
        arcade.draw_triangle_filled(cx + 10, cy + 5, cx + 4, cy + 5, cx + 8, cy + 11, arcade.color.WHITE)
    elif soort == "krimpsprong":
        # Krimpsprong: drie pijltjes omhoog die steeds kleiner worden
        for i, gr in enumerate((7, 5, 3)):
            ax = cx - 8 + i * 8
            arcade.draw_triangle_filled(ax, cy + gr - 2, ax - gr / 2, cy - 2,
                                        ax + gr / 2, cy - 2, arcade.color.WHITE)
    elif soort == "tegendraads":
        # Tegendraads: een pijl naar links en een pijl naar rechts
        arcade.draw_triangle_filled(cx - 11, cy, cx - 4, cy - 5, cx - 4, cy + 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 11, cy, cx + 4, cy - 5, cx + 4, cy + 5, arcade.color.WHITE)
    elif soort == "turboflip":
        # Turbo-flip: een pijl vooruit met flip-pijltjes boven en onder
        arcade.draw_triangle_filled(cx + 9, cy, cx - 1, cy - 6, cx - 1, cy + 6, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 6, cy + 9, cx - 9, cy + 4, cx - 3, cy + 4, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 6, cy - 9, cx - 9, cy - 4, cx - 3, cy - 4, arcade.color.WHITE)
    elif soort == "spiegelkatapult":
        # Spiegel-katapult: een boogje met een spiegel-streep erdoorheen
        arcade.draw_arc_outline(cx, cy - 3, 20, 18, arcade.color.WHITE, 20, 160, 2)
        arcade.draw_line(cx - 7, cy + 7, cx + 7, cy - 7, arcade.color.WHITE, 2)
    elif soort == "schaduw":
        # Schaduw: twee blokjes achter elkaar (jij + je schaduw)
        arcade.draw_lrbt_rectangle_filled(cx - 10, cx + 2, cy - 6, cy + 6, (120, 120, 160))
        arcade.draw_lrbt_rectangle_filled(cx - 2, cx + 10, cy - 8, cy + 8, arcade.color.WHITE)
    elif soort == "pingpong":
        # Ping-pong: een balletje met een pijl omhoog en omlaag
        arcade.draw_circle_filled(cx, cy, 6, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx, cy + 11, cx - 4, cy + 6, cx + 4, cy + 6, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx, cy - 11, cx - 4, cy - 6, cx + 4, cy - 6, arcade.color.WHITE)
    elif soort == "spook":
        # Spookje (rond kopje met golvende onderrand)
        arcade.draw_circle_filled(cx, cy + 2, 8, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 6, cy + 2, arcade.color.WHITE)
        for i in range(3):
            arcade.draw_circle_filled(cx - 6 + i * 6, cy - 6, 3, arcade.color.WHITE)
        arcade.draw_circle_filled(cx - 3, cy + 3, 1.5, (40, 40, 70))
        arcade.draw_circle_filled(cx + 3, cy + 3, 1.5, (40, 40, 70))
    elif soort == "vleermuis":
        # Vleermuisje (lijfje met twee vleugel-driehoeken)
        arcade.draw_circle_filled(cx, cy, 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 3, cy, cx - 12, cy + 6, cx - 12, cy - 4, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 3, cy, cx + 12, cy + 6, cx + 12, cy - 4, arcade.color.WHITE)
    elif soort == "zombie":
        # Zombiekopje (vierkant met scheve oogjes)
        arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 8, cy + 8, arcade.color.WHITE)
        arcade.draw_circle_filled(cx - 4, cy + 2, 2, (40, 60, 30))
        arcade.draw_circle_filled(cx + 4, cy, 2, (40, 60, 30))
    elif soort == "pompoenkop":
        # Pompoentje met driehoek-oogjes
        arcade.draw_circle_filled(cx, cy - 1, 8, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(cx - 1, cx + 1, cy + 7, cy + 11, (90, 150, 40))
        arcade.draw_triangle_filled(cx - 6, cy + 3, cx - 1, cy + 3, cx - 3, cy - 2, (220, 110, 20))
        arcade.draw_triangle_filled(cx + 6, cy + 3, cx + 1, cy + 3, cx + 3, cy - 2, (220, 110, 20))
    elif soort == "voorspeller":
        # Zandlopertje
        arcade.draw_triangle_filled(cx - 7, cy + 9, cx + 7, cy + 9, cx, cy, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx - 7, cy - 9, cx + 7, cy - 9, cx, cy, arcade.color.WHITE)
    elif soort == "pendel":
        # Pijl naar links en naar rechts met een lijntje ertussen
        arcade.draw_line(cx - 7, cy, cx + 7, cy, arcade.color.WHITE, 2)
        arcade.draw_triangle_filled(cx - 11, cy, cx - 5, cy - 5, cx - 5, cy + 5, arcade.color.WHITE)
        arcade.draw_triangle_filled(cx + 11, cy, cx + 5, cy - 5, cx + 5, cy + 5, arcade.color.WHITE)
    elif soort == "blinde":
        # Een dicht oogje (streepje met wimpers)
        arcade.draw_arc_outline(cx, cy + 2, 18, 10, arcade.color.WHITE, 180, 360, 2)
        for dx in (-5, 0, 5):
            arcade.draw_line(cx + dx, cy - 3, cx + dx, cy - 7, arcade.color.WHITE, 2)
    elif soort == "dubbelflip":
        # Vier pijltjes (op, neer, links, rechts)
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            px, py = cx + dx * 10, cy + dy * 10
            arcade.draw_triangle_filled(px, py, px - dy * 4 - dx * 5, py - dx * 4 - dy * 5,
                                        px + dy * 4 - dx * 5, py + dx * 4 - dy * 5, arcade.color.WHITE)
    elif soort == "vijfkamp":
        # Een grote 5
        arcade.draw_text("5", cx, cy - 8, arcade.color.WHITE, 16, bold=True, anchor_x="center")
    elif soort == "tienkamp":
        # Een grote 10
        arcade.draw_text("10", cx, cy - 8, arcade.color.WHITE, 14, bold=True, anchor_x="center")
    elif soort == "vijftienkamp":
        # Een grote 15
        arcade.draw_text("15", cx, cy - 8, arcade.color.WHITE, 14, bold=True, anchor_x="center")
    elif soort == "twintigkamp":
        # Een grote 20
        arcade.draw_text("20", cx, cy - 8, arcade.color.WHITE, 14, bold=True, anchor_x="center")
    elif soort == "element":
        # Vier gekleurde bolletjes: vuur, water, lucht en aarde
        for (dx, dy), kl in zip(((-5, 5), (5, 5), (-5, -5), (5, -5)),
                                ((255, 110, 30), (60, 150, 255), (220, 240, 255), (150, 105, 60))):
            arcade.draw_circle_filled(cx + dx, cy + dy, 5, kl)
    elif soort == "eigen":
        # Zelfgemaakt poppetje: een sterretje/blokje met een plusje
        arcade.draw_lrbt_rectangle_filled(cx - 7, cx + 7, cy - 7, cy + 7, arcade.color.WHITE)
        arcade.draw_line(cx - 3, cy, cx + 3, cy, (255, 150, 40), 2)
        arcade.draw_line(cx, cy - 3, cx, cy + 3, (255, 150, 40), 2)
    elif soort in SNELHEID_FACTOR:
        # Snelheid-portaal: laat de keer-factor zien (bv. "x2")
        arcade.draw_text(soort, cx, cy - 6, arcade.color.WHITE, 11, bold=True, anchor_x="center")
    elif soort == "dubbel":
        arcade.draw_text("2", cx, cy - 8, arcade.color.WHITE, 16, bold=True, anchor_x="center")
    elif soort == "enkel":
        arcade.draw_text("1", cx, cy - 8, arcade.color.WHITE, 16, bold=True, anchor_x="center")

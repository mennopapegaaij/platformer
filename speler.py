# speler.py
# De Speler klasse — alles over het poppetje dat jij bestuurt.

import arcade
import math
from instellingen import (SPELER_SNELHEID, SPRING_KRACHT, ZWAARTEKRACHT,
                           SPELER_KLEUR, OOG_KLEUR)

LEVENS_BEGIN = 3  # Hoeveel levens de speler krijgt bij het begin

# --- Vliegtuig-modus (Geometry Dash raket) ---
VLIEG_STUW = 0.9       # Hoeveel duw omhoog als je de knop vasthoudt
VLIEG_ZWAARTE = 0.45   # Hoe hard je zakt als je loslaat
VLIEG_MAX = 6          # Hoogste omhoog/omlaag snelheid (zo blijft het bestuurbaar)
VLIEG_PLAFOND = 460    # Zo hoog mag je maximaal vliegen (net onder de balk bovenin)

# --- UFO-modus: bij elke tik een sprongetje omhoog (zoals Flappy Bird) ---
FLAP_KRACHT = 7        # Hoe groot het sprongetje is bij een tik

# --- Robot-modus: hoe langer je vasthoudt, hoe hoger je springt ---
ROBOT_START = 7        # Beginkracht van de sprong
ROBOT_EXTRA = 0.7      # Extra duw omhoog per frame terwijl je vasthoudt
ROBOT_BOOST_FRAMES = 16  # Hoeveel frames je kunt blijven duwen (langer = hoger)


class Speler:
    """Het poppetje dat de speler bestuurt: een geel vierkantje met een gezichtje."""

    def __init__(self):
        # Startpositie
        self.x = 50
        self.y = 100
        self.breedte = 32
        self.hoogte = 32

        # Bewegingssnelheid
        self.snelheid_x = 0
        self.snelheid_y = 0

        # Is de speler op de grond? (nodig voor springen)
        self.staat_op_grond = False

        # Welke toetsen zijn ingedrukt?
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

        # --- Levens ---
        self.levens = LEVENS_BEGIN

        # --- Power-up timers (tellen af per frame) ---
        self.onkwetsbaar_timer = 0      # ⭐ Ster: niet geraakt kunnen worden
        self.snelheid_boost_timer = 0   # 💨 Snelheid: dubbel zo snel
        self.dubbel_sprong_timer = 0    # 🦘 Dubbel springen: nog een keer springen
        self.schiet_timer = 0           # 🔫 Schieten: kogels afschieten met Z

        # Heeft de speler zijn extra sprong al gebruikt?
        self.heeft_dubbel_gesprongen = False

        # Richting waar de speler naar kijkt (True = rechts, False = links)
        self.kijkt_rechts = True

        # Extra snelheid en spronghoogte door punten (elke 10 punten = +1)
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

        # Knippercyclus voor als de speler onkwetsbaar is
        self._knippering = 0

        # Draai-stand (graden) — voor de tollende kubus in de racemodus
        self.rotatie = 0

        # Kleur van het poppetje (standaard geel; bij 2 spelers blauw/rood)
        self.kleur = SPELER_KLEUR

        # --- Speciale modi (Geometry Dash): blok/vliegtuig/ufo/bal/golf/robot/spin ---
        self.modus = "blok"              # in welke vorm ben je nu?
        self.vlieg_omhoog = False        # knop-vasthouden (vliegtuig, golf, robot)
        self.zwaartekracht_richting = 1  # 1 = omlaag, -1 = omhoog (bal en spin)
        self._robot_boost = 0            # hoeveel frames de robot nog omhoog mag duwen
        self.snelheid_factor = 1.0       # snelheid-portaal (x0.5 / x1 / x2 / x5 / x10)

    def reset(self):
        """Zet de speler terug naar de beginpositie (bij het opnieuw spelen van een level)."""
        self.x = 50
        self.y = 100
        self.snelheid_x = 0
        self.snelheid_y = 0
        self.staat_op_grond = False
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False
        # Power-up effecten stoppen bij het herstarten
        self.onkwetsbaar_timer = 0
        self.snelheid_boost_timer = 0
        self.dubbel_sprong_timer = 0
        self.schiet_timer = 0
        self.heeft_dubbel_gesprongen = False
        self.rotatie = 0
        self.vlieg_omhoog = False           # knop-vasthouden reset
        self.modus = "blok"                 # begin weer als gewoon blokje
        self.zwaartekracht_richting = 1     # zwaartekracht weer gewoon omlaag
        self._robot_boost = 0               # robot-duw reset
        self.snelheid_factor = 1.0          # snelheid weer normaal

    def volledig_reset(self):
        """Reset alles inclusief levens (voor een nieuw spel)."""
        self.reset()
        self.levens = LEVENS_BEGIN
        # Bonussen ook resetten — anders is de speler na game over nog steeds snel
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

    def bijwerken(self, level_breedte, platforms):
        """Beweeg de speler en controleer botsingen met platforms."""

        # Timers aftikken
        if self.onkwetsbaar_timer > 0:
            self.onkwetsbaar_timer -= 1
            self._knippering = (self._knippering + 1) % 6
        if self.snelheid_boost_timer > 0:
            self.snelheid_boost_timer -= 1
        if self.dubbel_sprong_timer > 0:
            self.dubbel_sprong_timer -= 1
            if self.dubbel_sprong_timer == 0:
                self.heeft_dubbel_gesprongen = False
        if self.schiet_timer > 0:
            self.schiet_timer -= 1

        # Bepaal de snelheid: normaal + snelheidsboost power-up + punten-bonus
        snelheid = SPELER_SNELHEID + self.snelheid_bonus
        if self.snelheid_boost_timer > 0:
            snelheid *= 2   # Dubbel bij snelheidsboost power-up
        snelheid *= self.snelheid_factor   # snelheid-portaal (x0.5 / x2 / x10 ...)

        # Horizontale beweging
        if self.links_ingedrukt:
            self.snelheid_x = -snelheid
            self.kijkt_rechts = False   # Speler kijkt naar links
        elif self.rechts_ingedrukt:
            self.snelheid_x = snelheid
            self.kijkt_rechts = True    # Speler kijkt naar rechts
        else:
            self.snelheid_x = 0

        self.x += self.snelheid_x

        # Niet buiten het level lopen
        if self.x < 0:
            self.x = 0
        if self.x + self.breedte > level_breedte:
            self.x = level_breedte - self.breedte

        # Verticale beweging hangt af van de modus
        if self.modus == "vliegtuig":
            # Vliegtuig: knop vasthouden = stuw omhoog, anders zak je langzaam
            if self.vlieg_omhoog:
                self.snelheid_y += VLIEG_STUW
            self.snelheid_y -= VLIEG_ZWAARTE
            self.snelheid_y = max(-VLIEG_MAX, min(VLIEG_MAX, self.snelheid_y))
        elif self.modus == "golf":
            # Golf: schuin omhoog als je vasthoudt, anders schuin omlaag (45 graden)
            self.snelheid_y = snelheid if self.vlieg_omhoog else -snelheid
        elif self.modus in ("bal", "spin"):
            # Bal/spin: zwaartekracht in de huidige richting (kan omgedraaid zijn)
            self.snelheid_y -= ZWAARTEKRACHT * 1.3 * self.zwaartekracht_richting
            self.snelheid_y = max(-11, min(11, self.snelheid_y))
        elif self.modus == "robot":
            # Robot: terwijl je vasthoudt blijf je omhoog duwen (langer = hoger)
            if self.vlieg_omhoog and self._robot_boost > 0 and self.snelheid_y > 0:
                self.snelheid_y += ROBOT_EXTRA
                self._robot_boost -= 1
            self.snelheid_y -= ZWAARTEKRACHT
        else:
            # Blok en UFO: gewone zwaartekracht. De richting kan omgedraaid zijn door
            # een draai-bol (dan val je juist naar BOVEN).
            self.snelheid_y -= ZWAARTEKRACHT * self.zwaartekracht_richting
        self.y += self.snelheid_y
        self.staat_op_grond = False
        omgedraaid = self.zwaartekracht_richting == -1

        # Botsingen met platforms
        for platform in platforms:
            # Landen op het platform (van bovenaf)
            if platform.raakt(self.x, self.y, self.breedte, self.hoogte):
                self.y = platform.y + platform.hoogte
                self.heeft_dubbel_gesprongen = False  # Op de grond: extra sprong herlaadbaar
                self._robot_boost = 0                 # robot mag pas na een nieuwe tik duwen
                # Verdwijnblok: laat het weten dat je erop staat (het gaat dan verdwijnen)
                if hasattr(platform, "aangeraakt"):
                    platform.aangeraakt()
                # Stuiterblok: stuiter omhoog i.p.v. blijven staan
                stuiter = getattr(platform, "stuiter", 0)
                if stuiter and not omgedraaid:
                    self.snelheid_y = stuiter
                else:
                    self.snelheid_y = 0
                    if not omgedraaid:
                        self.staat_op_grond = True
            # Hoofd stoot tegen onderkant platform
            elif (self.snelheid_y > 0 and
                  platform.raakt_van_onder(self.x, self.y, self.breedte, self.hoogte)):
                self.y = platform.y - self.hoogte
                self.snelheid_y = 0
                # Met omgekeerde zwaartekracht 'sta' je ONDER een platform
                if omgedraaid:
                    self.staat_op_grond = True

        # Schuine blokken (hellingen): loop er soepel overheen omhoog/omlaag
        if not omgedraaid:
            midden = self.x + self.breedte / 2
            for platform in platforms:
                if not getattr(platform, "is_schuin", False):
                    continue
                if platform.x <= midden <= platform.x + platform.breedte:
                    opp = platform.hoogte_op(midden)      # hoogte van de helling hier
                    if self.snelheid_y <= 0 and self.y <= opp and self.y + self.hoogte > opp:
                        self.y = opp
                        self.snelheid_y = 0
                        self.staat_op_grond = True
                        self.heeft_dubbel_gesprongen = False
                        self._robot_boost = 0

        # In de speciale modi (of bij omgedraaide zwaartekracht): niet door het plafond
        if (self.modus in ("vliegtuig", "ufo", "bal", "golf", "spin") or omgedraaid) \
                and self.y + self.hoogte > VLIEG_PLAFOND:
            self.y = VLIEG_PLAFOND - self.hoogte
            if self.snelheid_y > 0:
                self.snelheid_y = 0
                if omgedraaid or self.modus in ("bal", "spin"):
                    self.staat_op_grond = True   # je 'ligt' tegen het plafond

    def flap(self):
        """UFO-modus: geef een klein sprongetje omhoog (bij elke tik)."""
        self.snelheid_y = FLAP_KRACHT

    def flip_zwaartekracht(self):
        """Bal-modus: draai de zwaartekracht om (van vloer naar plafond en terug)."""
        self.zwaartekracht_richting *= -1

    def robot_sprong(self):
        """Robot-modus: begin een sprong (vasthouden maakt hem hoger)."""
        if self.staat_op_grond:
            # Bij omgekeerde zwaartekracht spring je juist naar beneden
            self.snelheid_y = ROBOT_START * self.zwaartekracht_richting
            self._robot_boost = ROBOT_BOOST_FRAMES

    def spring(self):
        """Laat de speler springen — hoger naarmate je meer punten hebt!

        Bij omgekeerde zwaartekracht (na een draai-bol) spring je juist naar BENEDEN,
        zodat je van het plafond af komt."""
        sprongkracht = (SPRING_KRACHT + self.sprong_bonus) * self.zwaartekracht_richting
        if self.staat_op_grond:
            self.snelheid_y = sprongkracht
        elif (self.dubbel_sprong_timer > 0 and not self.heeft_dubbel_gesprongen):
            self.snelheid_y = sprongkracht
            self.heeft_dubbel_gesprongen = True

    def is_gevallen(self):
        """Geeft True terug als de speler te ver naar beneden is gevallen."""
        return self.y < -50

    def is_onkwetsbaar(self):
        """Geeft True terug als de speler nu onkwetsbaar is (ster-effect)."""
        return self.onkwetsbaar_timer > 0

    def teken(self):
        """Teken de speler — elke modus heeft zijn eigen poppetje!"""
        # Knipperen als de speler onkwetsbaar is
        if self.onkwetsbaar_timer > 0 and self._knippering < 3:
            return  # Niet tekenen = onzichtbaar in de knippercyclus

        # Elke speciale modus heeft zijn eigen vorm
        if self.modus == "vliegtuig":
            self._teken_vliegtuig()
            return
        if self.modus == "ufo":
            self._teken_ufo()
            return
        if self.modus == "bal":
            self._teken_bal()
            return
        if self.modus == "golf":
            self._teken_golf()
            return
        if self.modus == "robot":
            self._teken_robot()
            return
        if self.modus == "spin":
            self._teken_spin()
            return

        # Gewoon blokje: in de racemodus tolt het door de lucht → teken het gedraaid
        if self.rotatie != 0:
            self._teken_gedraaid()
            return

        x = self.x
        y = self.y
        w = self.breedte
        h = self.hoogte

        # Lijf (geel, of goudgeel bij snelheidsboost)
        lijf_kleur = (255, 220, 0) if self.snelheid_boost_timer > 0 else self.kleur
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, lijf_kleur)

        # Rand: oranje normaal, rood bij dubbel-sprong, lichtblauw bij onkwetsbaar
        if self.onkwetsbaar_timer > 0:
            rand_kleur = arcade.color.YELLOW
        elif self.dubbel_sprong_timer > 0:
            rand_kleur = arcade.color.CYAN
        else:
            rand_kleur = arcade.color.ORANGE
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, rand_kleur, 3)

        # Linker oog
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        # Lachend mondje
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

    def _teken_gedraaid(self):
        """Teken het blokje gedraaid (de tollende kubus van Geometry Dash)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        hoek = math.radians(self.rotatie)
        cos_h, sin_h = math.cos(hoek), math.sin(hoek)

        def draai(dx, dy):
            # Draai een punt (dx, dy) rond het midden van het blokje
            return (cx + dx * cos_h - dy * sin_h, cy + dx * sin_h + dy * cos_h)

        hw, hh = self.breedte / 2, self.hoogte / 2
        hoeken = [draai(-hw, -hh), draai(hw, -hh), draai(hw, hh), draai(-hw, hh)]

        # Lijf (geel, of goudgeel bij snelheidsboost)
        lijf_kleur = (255, 220, 0) if self.snelheid_boost_timer > 0 else self.kleur
        arcade.draw_polygon_filled(hoeken, lijf_kleur)
        arcade.draw_polygon_outline(hoeken, arcade.color.ORANGE, 3)

        # Oogjes draaien mee
        for ox in (-7, 7):
            ex, ey = draai(ox, 5)
            arcade.draw_circle_filled(ex, ey, 3, OOG_KLEUR)

    def _draai(self, dx, dy):
        """Hulpje: draai een punt (dx, dy) rond het midden van de speler.

        Gebruikt de huidige rotatie (voor het vliegtuig, de bal en de golf).
        """
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        hoek = math.radians(self.rotatie)
        c, s = math.cos(hoek), math.sin(hoek)
        return (cx + dx * c - dy * s, cy + dx * s + dy * c)

    def _teken_vliegtuig(self):
        """Teken een raket/vliegtuigje dat mee kantelt met de neus (paars)."""
        romp = [self._draai(*p) for p in [(-14, -8), (8, -8), (18, 0), (8, 8), (-14, 8)]]
        arcade.draw_polygon_filled(romp, self.kleur)
        arcade.draw_polygon_outline(romp, (150, 90, 220), 3)
        # Vinnen achteraan
        arcade.draw_polygon_filled([self._draai(*p) for p in [(-14, 6), (-22, 13), (-10, 2)]],
                                   (150, 90, 220))
        arcade.draw_polygon_filled([self._draai(*p) for p in [(-14, -6), (-22, -13), (-10, -2)]],
                                   (150, 90, 220))
        # Raampje
        rx, ry = self._draai(3, 1)
        arcade.draw_circle_filled(rx, ry, 4, (150, 220, 255))

    def _teken_ufo(self):
        """Teken een UFO: een schotel met een koepel en lichtjes (blauw)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # Schotel
        arcade.draw_ellipse_filled(cx, cy - 2, 34, 14, self.kleur)
        arcade.draw_ellipse_outline(cx, cy - 2, 34, 14, (40, 150, 210), 3)
        # Koepel bovenop
        arcade.draw_ellipse_filled(cx, cy + 4, 18, 14, (150, 210, 255))
        # Lichtjes eronder
        for dx in (-10, 0, 10):
            arcade.draw_circle_filled(cx + dx, cy - 8, 2.5, (255, 240, 120))

    def _teken_bal(self):
        """Teken een bal die rolt (oranje strepen die meedraaien)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        r = 15
        arcade.draw_circle_filled(cx, cy, r, self.kleur)
        arcade.draw_circle_outline(cx, cy, r, (230, 140, 40), 3)
        # Twee strepen die meedraaien -> je ziet hem rollen
        a, b = self._draai(-r + 2, 0), self._draai(r - 2, 0)
        arcade.draw_line(a[0], a[1], b[0], b[1], (230, 140, 40), 3)
        c, d = self._draai(0, -r + 2), self._draai(0, r - 2)
        arcade.draw_line(c[0], c[1], d[0], d[1], (230, 140, 40), 2)

    def _teken_golf(self):
        """Teken een pijltje/ruit dat schuin omhoog of omlaag wijst (roze)."""
        ruit = [self._draai(*p) for p in [(15, 0), (0, 10), (-12, 0), (0, -10)]]
        arcade.draw_polygon_filled(ruit, self.kleur)
        arcade.draw_polygon_outline(ruit, (220, 60, 120), 3)
        # Puntje aan de voorkant
        px, py = self._draai(15, 0)
        arcade.draw_circle_filled(px, py, 3, (255, 150, 190))

    def _teken_robot(self):
        """Teken een klein robotje: pootjes, een lijf en een kop met antenne (grijs)."""
        x = self.x
        y = self.y
        w = self.breedte
        cx = x + w / 2
        romp = (120, 190, 90)   # groen-grijs lijf
        metaal = (90, 100, 120)
        # Pootjes
        arcade.draw_lrbt_rectangle_filled(x + 4, x + 12, y, y + 8, metaal)
        arcade.draw_lrbt_rectangle_filled(x + w - 12, x + w - 4, y, y + 8, metaal)
        # Lijf
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 7, y + 24, self.kleur)
        arcade.draw_lrbt_rectangle_outline(x + 3, x + w - 3, y + 7, y + 24, metaal, 2)
        # Kop
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + 24, y + 32, romp)
        arcade.draw_lrbt_rectangle_outline(x + 6, x + w - 6, y + 24, y + 32, metaal, 2)
        # Oogje en antenne
        arcade.draw_circle_filled(cx, y + 28, 3, OOG_KLEUR)
        arcade.draw_line(cx, y + 32, cx, y + 37, metaal, 2)
        arcade.draw_circle_filled(cx, y + 38, 2, (255, 80, 80))

    def _teken_spin(self):
        """Teken een spinnetje: een rond lijf met acht pootjes (donkerrood)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        poot = (60, 30, 40)
        # Acht pootjes
        for dx in (-15, -11, 11, 15):
            arcade.draw_line(cx, cy, cx + dx, cy + 12, poot, 2)
            arcade.draw_line(cx, cy, cx + dx, cy - 12, poot, 2)
        # Lijf
        arcade.draw_circle_filled(cx, cy, 11, self.kleur)
        arcade.draw_circle_outline(cx, cy, 11, (150, 40, 40), 3)
        # Twee oogjes
        arcade.draw_circle_filled(cx - 4, cy + 3, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy + 3, 2, OOG_KLEUR)

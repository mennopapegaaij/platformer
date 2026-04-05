# vijand.py
# Alle vijand-klassen.
# Wil je een nieuw soort vijand toevoegen? Doe dat dan hier!

import arcade
import math
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
        self.levens = 1       # Hoeveel keer moet je hem stompen?

    def bijwerken(self, speler_x=None):
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
        return (px + pw > self.x + 4 and
                px < self.x + self.breedte - 4 and
                speler_onder <= vijand_boven and
                speler_onder >= vijand_boven - 12)


# =============================================
# 🐝 VLIEGENDE VIJAND
# Vliegt heen en weer in de lucht — pas op als je springt!
# =============================================
class VliegendVijand(Vijand):
    """Een bij die heen en weer vliegt op een vaste hoogte."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=3):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 34
        self.hoogte = 24
        self._teller = 0   # Voor de vleugel-animatie

    def bijwerken(self, speler_x=None):
        """Vliegt heen en weer — geen zwaartekracht."""
        self._teller += 0.2
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

    def teken(self):
        """Teken een gele bij met vleugels."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2

        # Vleugels (bewegen op en neer)
        vleugel_y = cy + 8 + math.sin(self._teller * 3) * 4
        arcade.draw_ellipse_filled(cx - 12, vleugel_y, 18, 10, (200, 230, 255, 180))
        arcade.draw_ellipse_filled(cx + 12, vleugel_y, 18, 10, (200, 230, 255, 180))

        # Lijf (geel met zwarte strepen)
        arcade.draw_ellipse_filled(cx, cy, w - 4, h - 2, arcade.color.YELLOW)
        arcade.draw_ellipse_outline(cx, cy, w - 4, h - 2, arcade.color.BLACK, 2)
        # Strepen
        for dx in [-6, 0, 6]:
            arcade.draw_line(cx + dx, cy - 8, cx + dx, cy + 8, arcade.color.BLACK, 2)

        # Ogen
        arcade.draw_circle_filled(cx - 7, cy + 4, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 7, cy + 4, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx - 6, cy + 5, 1, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 8, cy + 5, 1, arcade.color.WHITE)

        # Angel
        arcade.draw_triangle_filled(cx - 3, cy - 9, cx + 3, cy - 9,
                                     cx, cy - 17, arcade.color.ORANGE)


# =============================================
# 🐸 SPRINGENDE VIJAND
# Staat stil en springt dan omhoog — moeilijk om te ontwijken!
# =============================================
class SpringendVijand(Vijand):
    """Een groene kikker die periodiek omhoog springt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 32
        self.hoogte = 28
        self._grond_y = y           # De y-positie op de grond
        self._snelheid_y = 0        # Verticale snelheid
        self._spring_teller = 0     # Telt tot de volgende sprong
        self._spring_interval = 80  # Frames tussen sprongen

    def bijwerken(self, speler_x=None):
        """Loopt een beetje heen en weer en springt periodiek."""
        # Horizontaal bewegen
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

        # Springlogica
        self._spring_teller += 1
        if self._spring_teller >= self._spring_interval and self.y <= self._grond_y:
            self._snelheid_y = 10   # Springkracht
            self._spring_teller = 0

        # Zwaartekracht
        self._snelheid_y -= 0.5
        self.y += self._snelheid_y

        # Niet verder vallen dan de grond
        if self.y <= self._grond_y:
            self.y = self._grond_y
            self._snelheid_y = 0

    def teken(self):
        """Teken een groene kikker — platgedrukt op de grond, rond in de lucht."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2

        # Is de kikker in de lucht? Dan is hij ronder
        in_lucht = self.y > self._grond_y + 2
        breedte_factor = 0.8 if in_lucht else 1.2
        hoogte_factor = 1.2 if in_lucht else 0.8

        # Lijf
        arcade.draw_ellipse_filled(cx, cy, w * breedte_factor, h * hoogte_factor,
                                   (50, 180, 50))
        arcade.draw_ellipse_outline(cx, cy, w * breedte_factor, h * hoogte_factor,
                                    (30, 120, 30), 2)

        # Buik (lichtgroen)
        arcade.draw_ellipse_filled(cx, cy - 3, w * breedte_factor * 0.6,
                                   h * hoogte_factor * 0.6, (100, 220, 100))

        # Ogen (boven op het hoofd)
        oog_y = cy + h * hoogte_factor * 0.4
        arcade.draw_circle_filled(cx - 8, oog_y, 6, (80, 200, 80))
        arcade.draw_circle_filled(cx + 8, oog_y, 6, (80, 200, 80))
        arcade.draw_circle_filled(cx - 8, oog_y, 3, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 8, oog_y, 3, OOG_KLEUR)


# =============================================
# 💜 GROTE VIJAND
# Groot, paars en langzaam — maar je moet hem 2x stompen!
# Na de eerste stomp wordt hij kleiner en sneller!
# =============================================
class GroteVijand(Vijand):
    """Een grote paarse vijand die twee keer gestompt moet worden."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=1.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 50
        self.hoogte = 50
        self.levens = 2             # Heeft 2 levens!
        self._woede = 0             # Knippert rood als hij geraakt is

    def word_gestompt(self):
        """Wordt aangeroepen als de speler er bovenop springt."""
        self.levens -= 1
        self._woede = 30  # 30 frames knipperen
        if self.levens == 1:
            # Helft kleiner na de eerste stomp, maar nu sneller en feller!
            self.breedte = 38
            self.hoogte = 38
            self.snelheid = self.snelheid * 1.8 if self.snelheid > 0 else self.snelheid * 1.8

    def bijwerken(self, speler_x=None):
        """Beweegt heen en weer, langzaam."""
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        if self._woede > 0:
            self._woede -= 1

    def teken(self):
        """Teken een grote paarse vijand met een eng gezicht."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2

        # Knippert oranje als hij net geraakt is
        kleur = (255, 120, 0) if self._woede % 6 < 3 else (140, 40, 180)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (80, 0, 120), 3)

        # Groot gezicht
        oog_y = y + h - 15
        oog_r = 7 if self.levens == 2 else 5
        arcade.draw_circle_filled(cx - 10, oog_y, oog_r, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 10, oog_y, oog_r, OOG_KLEUR)
        arcade.draw_circle_filled(cx - 8, oog_y + 1, 2, arcade.color.RED)
        arcade.draw_circle_filled(cx + 12, oog_y + 1, 2, arcade.color.RED)

        # Wenkbrauwen (extra boos na 1e stomp)
        dikte = 4 if self.levens == 1 else 2
        arcade.draw_line(cx - 17, oog_y + 10, cx - 3, oog_y + 6, OOG_KLEUR, dikte)
        arcade.draw_line(cx + 3,  oog_y + 6,  cx + 17, oog_y + 10, OOG_KLEUR, dikte)

        # Mond
        arcade.draw_arc_outline(cx, y + 12, 18, 10, OOG_KLEUR, 200, 340, 3)

        # Levens-indicator (kleine rode stipjes boven het hoofd)
        for i in range(self.levens):
            arcade.draw_circle_filled(cx - 5 + i * 10, y + h + 8, 4, arcade.color.RED)


# =============================================
# 👻 GEEST VIJAND
# Zweeft in een golvende beweging — moeilijk te ontwijken!
# =============================================
class GeestVijand(Vijand):
    """Een witte geest die in een golvende baan vliegt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 32
        self.hoogte = 36
        self._midden_y = y          # De middenpositie van de golfbeweging
        self._golf_teller = 0       # Telt voor de sinusbeweging

    def bijwerken(self, speler_x=None):
        """Zweeft heen en weer in een golvende baan."""
        self._golf_teller += 0.06
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

        # Golfbeweging omhoog en omlaag
        self.y = self._midden_y + math.sin(self._golf_teller) * 50

    def teken(self):
        """Teken een spookachtige witte geest."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2

        # Lichtblauw gloeien eromheen
        arcade.draw_ellipse_filled(cx, cy, w + 10, h + 8, (180, 200, 255, 60))

        # Lijf (wit/lichtblauw)
        arcade.draw_ellipse_filled(cx, cy + 4, w, h - 4, (230, 235, 255))
        # Onderkant met golvende rand
        for i in range(4):
            golf_x = x + i * (w // 3)
            arcade.draw_circle_filled(golf_x + 5, y + 2, 6, (230, 235, 255))

        # Grote ronde ogen
        arcade.draw_circle_filled(cx - 7, cy + 8, 7, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 7, cy + 8, 7, OOG_KLEUR)
        # Pupillen (kijken naar links of rechts afhankelijk van bewegingsrichting)
        pupil_dx = 2 if self.snelheid > 0 else -2
        arcade.draw_circle_filled(cx - 7 + pupil_dx, cy + 8, 3, (50, 80, 200))
        arcade.draw_circle_filled(cx + 7 + pupil_dx, cy + 8, 3, (50, 80, 200))
        # Lichtpuntjes in de ogen
        arcade.draw_circle_filled(cx - 5, cy + 10, 1, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 9, cy + 10, 1, arcade.color.WHITE)

        # Kleine open mond
        arcade.draw_ellipse_filled(cx, cy - 2, 8, 6, OOG_KLEUR)


# =============================================
# 🦊 JAGER VIJAND
# Staat stil totdat jij te dichtbij komt — dan rent hij op je af!
# =============================================
class JagerVijand(Vijand):
    """Een oranje vos die stilstaat, maar op je afjaagt als je te dichtbij bent."""

    JACHT_AFSTAND = 250     # Binnen hoeveel pixels begint hij te jagen?

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=3.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 34
        self.hoogte = 32
        self._jaagt = False         # Jaagt hij nu op de speler?
        self._richting = 1          # 1 = rechts, -1 = links
        self._stap_teller = 0       # Voor de loop-animatie

    def bijwerken(self, speler_x=None):
        """Staat stil, maar jaagt als de speler dichtbij is."""
        if speler_x is not None:
            afstand = abs((self.x + self.breedte / 2) - speler_x)
            self._jaagt = afstand < self.JACHT_AFSTAND
        else:
            self._jaagt = False

        if self._jaagt and speler_x is not None:
            # Ren naar de speler toe
            if speler_x > self.x + self.breedte / 2:
                self._richting = 1
            else:
                self._richting = -1
            self.x += self._richting * self.snelheid
            self._stap_teller += 1
        else:
            self._stap_teller = 0

        # Niet buiten de grenzen lopen
        if self.x < self.links_grens:
            self.x = self.links_grens
        if self.x + self.breedte > self.rechts_grens:
            self.x = self.rechts_grens - self.breedte

    def teken(self):
        """Teken een oranje vos met puntige oren en een staart."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2

        # Loopanimatie: beweeg een beetje op en neer als hij jaagt
        bob = math.sin(self._stap_teller * 0.4) * 2 if self._jaagt else 0
        y = y + bob

        # Staart (wit/oranje)
        if self._richting > 0:
            arcade.draw_ellipse_filled(x - 8, y + 12, 18, 12, (240, 140, 30))
            arcade.draw_ellipse_filled(x - 10, y + 12, 10, 8, arcade.color.WHITE)
        else:
            arcade.draw_ellipse_filled(x + w + 8, y + 12, 18, 12, (240, 140, 30))
            arcade.draw_ellipse_filled(x + w + 10, y + 12, 10, 8, arcade.color.WHITE)

        # Lijf
        kleur = (220, 100, 20) if self._jaagt else (240, 140, 30)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (160, 70, 0), 2)

        # Puntige oren
        arcade.draw_triangle_filled(x + 4, y + h, x + 12, y + h, x + 8, y + h + 14,
                                    kleur)
        arcade.draw_triangle_filled(x + w - 12, y + h, x + w - 4, y + h,
                                    x + w - 8, y + h + 14, kleur)
        # Wit binnenin de oren
        arcade.draw_triangle_filled(x + 6, y + h + 1, x + 10, y + h + 1,
                                    x + 8, y + h + 9, arcade.color.WHITE)
        arcade.draw_triangle_filled(x + w - 10, y + h + 1, x + w - 6, y + h + 1,
                                    x + w - 8, y + h + 9, arcade.color.WHITE)

        # Snoet (wit)
        arcade.draw_ellipse_filled(cx, y + 10, 16, 10, (255, 220, 180))
        # Neus
        arcade.draw_circle_filled(cx, y + 14, 3, OOG_KLEUR)

        # Ogen
        oog_kleur = arcade.color.RED if self._jaagt else OOG_KLEUR
        arcade.draw_circle_filled(cx - 8, y + h - 8, 4, oog_kleur)
        arcade.draw_circle_filled(cx + 8, y + h - 8, 4, oog_kleur)

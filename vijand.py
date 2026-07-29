# vijand.py
# Alle vijand-klassen.
# Wil je een nieuw soort vijand toevoegen? Doe dat dan hier!

import arcade
import math
import random
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


# =============================================
# 👑 EINDBAAS
# Een reusachtige baas die voor je WEGRENT als je dichtbij komt!
# Je hebt minimaal 70 punten nodig om hem bij te houden.
# Stomp hem 3 keer om te winnen!
# =============================================
class EindBaas(Vijand):
    """
    De grote eindbaas! Hij is enorm, heeft 3 levens,
    en rent weg als de speler te dichtbij komt.
    Met meer punten (hogere snelheid) kun je hem inhalen!
    """

    VLUCHT_AFSTAND = 350    # Binnen hoeveel pixels begint hij te vluchten?
    VLUCHT_SNELHEID = 11    # Hoe snel hij wegrent (speler heeft 70+ punten nodig!)
    WANDEL_SNELHEID = 1.5   # Hoe snel hij rondloopt als je ver weg bent

    def __init__(self, x, y, links_grens, rechts_grens):
        super().__init__(x, y, links_grens, rechts_grens, snelheid=self.WANDEL_SNELHEID)
        self.breedte = 80       # Heel groot!
        self.hoogte = 80
        self.levens = 3         # Moet 3 keer gestompt worden
        self._vlucht_modus = False      # Vlucht hij nu?
        self._woede = 0                 # Knippert als hij geraakt is
        self._adem_teller = 0           # Voor de animatie (hijgt/beweegt)
        self._richting = 1              # 1 = rechts, -1 = links

    def word_gestompt(self):
        """Verliest een leven — wordt sneller en bozer na elke treffer!"""
        self.levens -= 1
        self._woede = 45   # Knippert 45 frames lang
        # Na elk leven iets sneller wegrennen!
        extra = (3 - self.levens) * 1.5
        self.VLUCHT_SNELHEID = 11 + extra

    def bijwerken(self, speler_x=None):
        """
        Wandelt rustig als de speler ver weg is.
        Rent weg als de speler te dichtbij komt!
        """
        self._adem_teller += 0.08

        if speler_x is not None:
            midden_x = self.x + self.breedte / 2
            afstand = speler_x - midden_x   # Positief = speler rechts van baas

            if abs(afstand) < self.VLUCHT_AFSTAND:
                # VLUCHTEN! Ren de andere kant op
                self._vlucht_modus = True
                if afstand > 0:
                    # Speler rechts → baas rent naar links
                    self._richting = -1
                    self.x -= self.VLUCHT_SNELHEID
                else:
                    # Speler links → baas rent naar rechts
                    self._richting = 1
                    self.x += self.VLUCHT_SNELHEID
            else:
                # Wandel rustig heen en weer
                self._vlucht_modus = False
                self.x += self._richting * self.WANDEL_SNELHEID

        # Omdraaien bij de grenzen
        if self.x <= self.links_grens:
            self.x = self.links_grens
            self._richting = 1
        if self.x + self.breedte >= self.rechts_grens:
            self.x = self.rechts_grens - self.breedte
            self._richting = -1

        # Woede-timer aftikken
        if self._woede > 0:
            self._woede -= 1

    def teken(self):
        """Teken de grote eindbaas — donkerpaars met een kroon en een eng gezicht."""
        x, y = self.x, self.y
        w, h = self.breedte, self.hoogte
        cx = x + w // 2

        # Lichte ademhalingsanimatie (groter/kleiner)
        adem = math.sin(self._adem_teller) * 2

        # Gloeien als hij vlucht (rode gloed rondom hem)
        if self._vlucht_modus:
            arcade.draw_ellipse_filled(cx, y + h / 2, w + 20 + adem, h + 20 + adem,
                                       (200, 0, 0, 60))

        # Lijf — donkerpaars, knippert oranje als hij geraakt is
        if self._woede > 0 and self._woede % 6 < 3:
            kleur = (255, 100, 0)
        else:
            kleur = (100, 0, 160)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (60, 0, 100), 4)

        # Poten (kleine blokjes onderaan)
        poot_kleur = (80, 0, 130)
        arcade.draw_lrbt_rectangle_filled(x + 8, x + 24, y - 10, y + 4, poot_kleur)
        arcade.draw_lrbt_rectangle_filled(x + w - 24, x + w - 8, y - 10, y + 4, poot_kleur)

        # Armen (steken opzij uit)
        arcade.draw_lrbt_rectangle_filled(x - 14, x + 2, y + h - 30, y + h - 16, poot_kleur)
        arcade.draw_lrbt_rectangle_filled(x + w - 2, x + w + 14, y + h - 30, y + h - 16, poot_kleur)

        # Buik (lichte vlek in het midden)
        arcade.draw_ellipse_filled(cx, y + h // 2 - 5, w * 0.5, h * 0.4, (130, 20, 200))

        # Kroon boven op het hoofd 👑
        kroon_y = y + h
        arcade.draw_lrbt_rectangle_filled(x + 10, x + w - 10, kroon_y, kroon_y + 12,
                                          (255, 215, 0))
        # Punten van de kroon
        for px_k in [x + 12, cx - 10, cx, cx + 10, x + w - 12]:
            arcade.draw_triangle_filled(px_k - 6, kroon_y + 12,
                                        px_k + 6, kroon_y + 12,
                                        px_k, kroon_y + 24,
                                        (255, 215, 0))
        # Juwelen op de kroon
        for px_k, kleur_j in [(cx - 18, arcade.color.RED),
                               (cx, arcade.color.BLUE),
                               (cx + 18, arcade.color.GREEN)]:
            arcade.draw_circle_filled(px_k, kroon_y + 6, 4, kleur_j)

        # Ogen (groot en eng — kijken altijd naar de speler via _richting)
        oog_y = y + h - 18
        oog_r = 10
        arcade.draw_circle_filled(cx - 18, oog_y, oog_r, (255, 255, 200))
        arcade.draw_circle_filled(cx + 18, oog_y, oog_r, (255, 255, 200))
        # Pupillen kijken de speler aan
        pupil_dx = 3 * (-self._richting)   # Kijkt altijd NAAR de speler
        arcade.draw_circle_filled(cx - 18 + pupil_dx, oog_y, 5, (180, 0, 0))
        arcade.draw_circle_filled(cx + 18 + pupil_dx, oog_y, 5, (180, 0, 0))
        # Lichtpuntjes
        arcade.draw_circle_filled(cx - 16 + pupil_dx, oog_y + 2, 1, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 20 + pupil_dx, oog_y + 2, 1, arcade.color.WHITE)

        # Wenkbrauwen — super boos!
        dikte = 4
        arcade.draw_line(cx - 28, oog_y + 14, cx - 8, oog_y + 8, OOG_KLEUR, dikte)
        arcade.draw_line(cx + 8, oog_y + 8, cx + 28, oog_y + 14, OOG_KLEUR, dikte)

        # Mond — grote grijnzende tanden
        arcade.draw_arc_outline(cx, y + 14, 30, 16, OOG_KLEUR, 200, 340, 3)
        # Tanden
        for tx in [cx - 10, cx - 2, cx + 6]:
            arcade.draw_lrbt_rectangle_filled(tx, tx + 6, y + 7, y + 16, arcade.color.WHITE)

        # Levens-indicator boven de kroon (rode hartjes)
        for i in range(self.levens):
            hx = cx - (self.levens - 1) * 10 + i * 20
            arcade.draw_circle_filled(hx - 4, y + h + 40, 5, arcade.color.RED)
            arcade.draw_circle_filled(hx + 4, y + h + 40, 5, arcade.color.RED)
            arcade.draw_triangle_filled(hx - 9, y + h + 40, hx + 9, y + h + 40,
                                        hx, y + h + 32, arcade.color.RED)

        # "VLUCHT!"-tekst als hij rent (erboven)
        if self._vlucht_modus:
            arcade.draw_text("VLUCHT!", cx - 28, y + h + 52,
                             arcade.color.YELLOW, 12, bold=True)


# =============================================
# 🟢 SLIJMBAL
# Een groene blob die stuiterend heen en weer wiebelt.
# =============================================
class SlijmVijand(Vijand):
    """Een groene slijmbal die wiebelend over de grond glijdt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 34
        self.hoogte = 26
        self._teller = 0   # Voor het wiebel-animatietje

    def bijwerken(self, speler_x=None):
        self._teller += 0.2
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        # Wiebel: nu eens breed en plat, dan smal en hoog
        wobble = math.sin(self._teller) * 4
        bw = w + wobble
        bh = h - wobble
        cy = y + bh / 2
        arcade.draw_ellipse_filled(cx, cy, bw, bh, (80, 200, 90))
        arcade.draw_ellipse_outline(cx, cy, bw, bh, (40, 140, 50), 2)
        # Lichtvlek zodat hij glimt
        arcade.draw_ellipse_filled(cx - bw * 0.2, cy + bh * 0.15, bw * 0.25, bh * 0.2,
                                   (170, 240, 170))
        # Ogen
        arcade.draw_circle_filled(cx - 7, cy + 2, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 7, cy + 2, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx - 6, cy + 3, 1, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 8, cy + 3, 1, arcade.color.WHITE)
        # Mondje
        arcade.draw_arc_outline(cx, cy - 4, 10, 6, OOG_KLEUR, 200, 340, 2)


# =============================================
# 🦔 STEKELEGEL
# LET OP: hier kun je NIET op springen! Alleen ontwijken of overheen springen.
# =============================================
class StekelVijand(Vijand):
    """Een egel vol stekels. Springen op zijn rug doet PIJN — ontwijk hem!"""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 34
        self.hoogte = 26

    def speler_springt_erop(self, px, py, pw, ph):
        """Door de stekels kun je hem NOOIT stompen (altijd False)."""
        return False

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2
        richting = 1 if self.snelheid > 0 else -1
        # Stekels bovenop (grijze driehoekjes)
        for i in range(5):
            sx = x + 5 + i * (w - 10) / 4
            arcade.draw_triangle_filled(sx - 5, y + h - 4, sx + 5, y + h - 4,
                                        sx, y + h + 12, (120, 120, 140))
        # Lijf
        arcade.draw_ellipse_filled(cx, cy, w, h, (110, 80, 60))
        arcade.draw_ellipse_outline(cx, cy, w, h, (60, 40, 30), 2)
        # Snoetje aan de voorkant
        snoet_x = cx + (w // 2 - 4) * richting
        arcade.draw_circle_filled(snoet_x, cy - 2, 5, (240, 210, 190))
        arcade.draw_circle_filled(snoet_x + 2 * richting, cy - 2, 2, OOG_KLEUR)
        # Oog
        arcade.draw_circle_filled(cx + 5 * richting, cy + 4, 3, OOG_KLEUR)


# =============================================
# 🔥 VUURMONSTER
# Een zwevend vlammetje dat flikkert in de lucht.
# =============================================
class VuurVijand(Vijand):
    """Een vurig monster dat flikkerend door de lucht zweeft."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 28
        self.hoogte = 34
        self._teller = 0
        self._midden_y = y

    def bijwerken(self, speler_x=None):
        self._teller += 0.3
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        # Zweeft zachtjes op en neer
        self.y = self._midden_y + math.sin(self._teller * 0.5) * 12

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h / 2
        flikker = math.sin(self._teller) * 3
        # Buitenvlam (rood/oranje, doorschijnend)
        arcade.draw_ellipse_filled(cx, cy, w + flikker, h + flikker, (230, 60, 20, 180))
        # Binnenvlam (geel)
        arcade.draw_ellipse_filled(cx, cy - 2, w - 8, h - 10, (255, 200, 40))
        # Ogen
        arcade.draw_circle_filled(cx - 6, cy + 4, 3, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 6, cy + 4, 3, OOG_KLEUR)


# =============================================
# ❄️ SNEEUWPOP
# Heel langzaam — maar koud en gevaarlijk!
# =============================================
class IJsVijand(Vijand):
    """Een ijskoude sneeuwpop die langzaam heen en weer schuift."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=1.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 30
        self.hoogte = 38

    def teken(self):
        x, y, w = self.x, self.y, self.breedte
        cx = x + w // 2
        # Twee sneeuwballen
        arcade.draw_circle_filled(cx, y + 12, 14, (235, 245, 255))
        arcade.draw_circle_filled(cx, y + 30, 10, (235, 245, 255))
        arcade.draw_circle_outline(cx, y + 12, 14, (170, 200, 230), 2)
        arcade.draw_circle_outline(cx, y + 30, 10, (170, 200, 230), 2)
        # Ogen
        arcade.draw_circle_filled(cx - 4, y + 32, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, y + 32, 2, OOG_KLEUR)
        # Wortelneus
        arcade.draw_triangle_filled(cx, y + 29, cx, y + 33, cx + 10, y + 31, arcade.color.ORANGE)
        # Knopen
        arcade.draw_circle_filled(cx, y + 14, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx, y + 8, 2, OOG_KLEUR)


# =============================================
# 💣 WANDELENDE BOM
# Loopt rond met een sissende lont.
# =============================================
class BomVijand(Vijand):
    """Een wandelende bom met een sissende, vonkende lont."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 30
        self.hoogte = 30
        self._teller = 0

    def bijwerken(self, speler_x=None):
        self._teller += 0.3
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2 - 2
        # Ronde zwarte bom
        arcade.draw_circle_filled(cx, cy, w // 2, (40, 40, 50))
        arcade.draw_circle_outline(cx, cy, w // 2, (10, 10, 20), 2)
        arcade.draw_circle_filled(cx - 5, cy + 5, 3, (120, 120, 140))  # glimlicht
        # Lont
        arcade.draw_line(cx + 6, y + h - 4, cx + 12, y + h + 8, (150, 100, 40), 3)
        # Vonk (flikkert tussen geel en oranje)
        vonk = arcade.color.YELLOW if int(self._teller * 4) % 2 == 0 else arcade.color.ORANGE
        arcade.draw_circle_filled(cx + 12, y + h + 9, 4, vonk)
        # Boze ogen
        arcade.draw_circle_filled(cx - 5, cy, 3, arcade.color.RED)
        arcade.draw_circle_filled(cx + 5, cy, 3, arcade.color.RED)


# =============================================
# 🦇 VLEERMUIS
# Fladdert in scherpe golfjes door de lucht.
# =============================================
class VleermuisVijand(Vijand):
    """Een vleermuis die in scherpe golven op en neer door de lucht fladdert."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=3):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 34
        self.hoogte = 20
        self._teller = 0
        self._midden_y = y

    def bijwerken(self, speler_x=None):
        self._teller += 0.25
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        self.y = self._midden_y + math.sin(self._teller) * 30

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2
        flap = math.sin(self._teller * 4) * 6
        # Vleugels (fladderen)
        arcade.draw_triangle_filled(cx, cy, x - 2, cy + flap, x + 6, cy - 8, (90, 60, 120))
        arcade.draw_triangle_filled(cx, cy, x + w + 2, cy + flap, x + w - 6, cy - 8, (90, 60, 120))
        # Lijf
        arcade.draw_ellipse_filled(cx, cy, 16, 18, (60, 40, 90))
        # Oortjes
        arcade.draw_triangle_filled(cx - 6, cy + 8, cx - 1, cy + 8, cx - 4, cy + 16, (60, 40, 90))
        arcade.draw_triangle_filled(cx + 1, cy + 8, cx + 6, cy + 8, cx + 4, cy + 16, (60, 40, 90))
        # Rode oogjes
        arcade.draw_circle_filled(cx - 4, cy + 2, 2, arcade.color.RED)
        arcade.draw_circle_filled(cx + 4, cy + 2, 2, arcade.color.RED)


# =============================================
# 🐍 SLANG
# Kronkelt over de grond met een golvend lichaam.
# =============================================
class SlangVijand(Vijand):
    """Een slang die kronkelend over de grond glijdt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 44
        self.hoogte = 20
        self._teller = 0

    def bijwerken(self, speler_x=None):
        self._teller += 0.3
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid

    def teken(self):
        x, y, w = self.x, self.y, self.breedte
        richting = 1 if self.snelheid > 0 else -1
        # Kronkelend lichaam: een rij bolletjes die golven
        for i in range(6):
            seg_x = x + i * (w / 6) + w / 12
            seg_y = y + 8 + math.sin(self._teller + i * 0.7) * 4
            r = 8 - i * 0.6
            arcade.draw_circle_filled(seg_x, seg_y, r, (70, 170, 70))
        # Kop aan de voorkant
        kop_x = x + (w - 6 if richting > 0 else 6)
        kop_y = y + 8 + math.sin(self._teller) * 4
        arcade.draw_circle_filled(kop_x, kop_y, 9, (90, 190, 90))
        arcade.draw_circle_filled(kop_x + 3 * richting, kop_y + 2, 2, OOG_KLEUR)
        # Tong
        arcade.draw_line(kop_x + 6 * richting, kop_y, kop_x + 12 * richting, kop_y,
                         arcade.color.RED, 2)


# =============================================
# 🤖 ROBOT
# Stevig van metaal — je moet hem TWEE keer stompen!
# =============================================
class RobotVijand(Vijand):
    """Een metalen robot met 2 levens: na de eerste stomp wordt hij sneller!"""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 32
        self.hoogte = 40
        self.levens = 2
        self._woede = 0

    def word_gestompt(self):
        self.levens -= 1
        self._woede = 25
        if self.levens == 1:
            self.snelheid = self.snelheid * 1.7   # Boos en sneller!

    def bijwerken(self, speler_x=None):
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        if self._woede > 0:
            self._woede -= 1

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        kleur = (255, 120, 0) if (self._woede > 0 and self._woede % 6 < 3) else (150, 160, 175)
        # Lijf
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h - 12, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h - 12, (80, 90, 100), 2)
        # Hoofd
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + h - 12, y + h, (185, 195, 205))
        # Antenne
        arcade.draw_line(cx, y + h, cx, y + h + 8, (80, 90, 100), 2)
        arcade.draw_circle_filled(cx, y + h + 9, 3, arcade.color.RED)
        # Led-ogen (rood als hij al 1x geraakt is, anders blauw)
        oog_kleur = arcade.color.RED if self.levens == 1 else (0, 200, 255)
        arcade.draw_circle_filled(cx - 6, y + h - 6, 3, oog_kleur)
        arcade.draw_circle_filled(cx + 6, y + h - 6, 3, oog_kleur)
        # Knopjes op de buik
        for i in range(2):
            arcade.draw_circle_filled(cx - 6 + i * 12, y + 12, 2, (80, 90, 100))
        # Levens-stipjes erboven
        for i in range(self.levens):
            arcade.draw_circle_filled(cx - 5 + i * 10, y + h + 16, 3, arcade.color.RED)


# =============================================
# 🐦 KRAAI
# Duikt op en neer terwijl hij door de lucht vliegt.
# =============================================
class KraaiVijand(Vijand):
    """Een zwarte kraai die in grote duikbewegingen door de lucht vliegt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=3.5):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 32
        self.hoogte = 24
        self._teller = 0
        self._midden_y = y

    def bijwerken(self, speler_x=None):
        self._teller += 0.15
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        self.y = self._midden_y + math.sin(self._teller) * 40   # Grote duik-golf

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2
        richting = 1 if self.snelheid > 0 else -1
        flap = math.sin(self._teller * 5) * 8
        # Lijf
        arcade.draw_ellipse_filled(cx, cy, w - 8, h - 6, (30, 30, 40))
        # Vleugels (fladderen)
        arcade.draw_triangle_filled(cx, cy, cx - 16, cy + flap, cx - 4, cy - 6, (20, 20, 30))
        arcade.draw_triangle_filled(cx, cy, cx + 16, cy + flap, cx + 4, cy - 6, (20, 20, 30))
        # Kop en snavel
        kop_x = cx + 10 * richting
        arcade.draw_circle_filled(kop_x, cy + 2, 6, (30, 30, 40))
        arcade.draw_triangle_filled(kop_x + 4 * richting, cy + 4, kop_x + 4 * richting, cy,
                                    kop_x + 12 * richting, cy + 2, arcade.color.ORANGE)
        arcade.draw_circle_filled(kop_x + 2 * richting, cy + 4, 2, arcade.color.YELLOW)


# =============================================
# 🍄 PADDENSTOEL
# Wipt vrolijk op en neer terwijl hij rondloopt.
# =============================================
class PaddenstoelVijand(Vijand):
    """Een boze paddenstoel die op en neer wipt terwijl hij loopt."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.breedte = 32
        self.hoogte = 30
        self._grond_y = y
        self._teller = 0

    def bijwerken(self, speler_x=None):
        self._teller += 0.2
        self.x += self.snelheid
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid
        # Wipt op en neer (altijd positief met abs)
        self.y = self._grond_y + abs(math.sin(self._teller)) * 6

    def teken(self):
        x, y, w = self.x, self.y, self.breedte
        cx = x + w // 2
        # Steel (crème-wit)
        arcade.draw_lrbt_rectangle_filled(cx - 7, cx + 7, y, y + 16, (240, 230, 210))
        # Hoed (rood)
        arcade.draw_ellipse_filled(cx, y + 20, w, 22, (210, 40, 40))
        arcade.draw_ellipse_outline(cx, y + 20, w, 22, (150, 20, 20), 2)
        # Witte stippen op de hoed
        for dx in [-9, 0, 9]:
            arcade.draw_circle_filled(cx + dx, y + 22, 3, arcade.color.WHITE)
        # Ogen op de steel
        arcade.draw_circle_filled(cx - 4, y + 9, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, y + 9, 2, OOG_KLEUR)


# =============================================
# 😈 ARENA-EINDBAAS
# De grote baas van de vechtmodus, met SPECIALE KRACHTEN:
#   1. Teleporteren (springt ineens naar een andere plek)
#   2. Een schild (dan kun je hem NIET stompen)
#   3. Kleine monsters oproepen
# Hoe hoger 'kracht', hoe sterker en gevaarlijker hij is!
# =============================================
class ArenaBaas(Vijand):
    """De eindbaas van de vechtmodus, met speciale krachten die sterker
    worden naarmate 'kracht' hoger is."""

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2.5, kracht=1):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.kracht = kracht
        self.breedte = 76
        self.hoogte = 76
        self.levens = 4 + kracht * 2      # flink meer levens bij hogere kracht
        self._grond_y = y
        self._woede = 0                   # knippert na een treffer
        self._adem = 0                    # voor de adem-animatie
        self._richting = 1 if snelheid >= 0 else -1
        # Schild (dan onkwetsbaar)
        self._schild = False
        self._schild_teller = 0
        # Teleporteren
        self._teleport_teller = 0
        self._flits = 0                   # witte flits vlak na een teleport
        # Monsters oproepen
        self.nieuwe_monsters = []         # spel.py leest deze uit en maakt ze echt
        self._spawn_teller = 0
        self._gespawnd = 0
        self._max_minions = 2 + kracht    # hoeveel hij er in totaal mag oproepen

    def word_gestompt(self):
        """Verliest een leven — zet meteen zijn schild aan en teleporteert weg!"""
        self.levens -= 1
        self._woede = 40
        self._schild = True
        self._schild_teller = 90          # ongeveer 1,5 seconde beschermd
        self._teleporteer()

    def _teleporteer(self):
        """Spring ineens naar een willekeurige plek binnen de arena."""
        self.x = random.randint(int(self.links_grens),
                                int(self.rechts_grens - self.breedte))
        self._flits = 12

    def speler_springt_erop(self, px, py, pw, ph):
        """Met het schild aan kun je hem NIET stompen."""
        if self._schild:
            return False
        return super().speler_springt_erop(px, py, pw, ph)

    def _roep_monster_op(self):
        """Roep een klein monster op dat de speler helpt lastigvallen."""
        soort = random.choice([Vijand, SpringendVijand, VleermuisVijand, SlijmVijand])
        mx = random.randint(int(self.links_grens), int(self.rechts_grens - 30))
        my = self._grond_y + (120 if soort is VleermuisVijand else 0)
        snel = 2 + self.kracht * 0.5
        self.nieuwe_monsters.append(
            soort(mx, my, self.links_grens, self.rechts_grens, snel))

    def bijwerken(self, speler_x=None):
        self._adem += 0.08
        if self._woede > 0:
            self._woede -= 1
        if self._flits > 0:
            self._flits -= 1

        # Schild-timer aftikken
        if self._schild:
            self._schild_teller -= 1
            if self._schild_teller <= 0:
                self._schild = False

        # Heen en weer bewegen
        self.x += self._richting * self.snelheid
        if self.x <= self.links_grens:
            self.x = self.links_grens
            self._richting = 1
        if self.x + self.breedte >= self.rechts_grens:
            self.x = self.rechts_grens - self.breedte
            self._richting = -1

        # SPECIALE KRACHT 1: af en toe teleporteren
        self._teleport_teller += 1
        if self._teleport_teller >= 200:
            self._teleport_teller = 0
            self._teleporteer()

        # SPECIALE KRACHT 2: kleine monsters oproepen
        self._spawn_teller += 1
        spawn_snelheid = max(60, 160 - self.kracht * 20)
        if self._spawn_teller >= spawn_snelheid and self._gespawnd < self._max_minions:
            self._spawn_teller = 0
            self._gespawnd += 1
            self._roep_monster_op()

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        adem = math.sin(self._adem) * 2

        # Dreigende gloed eromheen
        arcade.draw_circle_filled(cx, y + h / 2, w / 1.4 + adem, (150, 0, 40, 60))

        # Lijf: donkerrood, wit bij teleport-flits, oranje bij woede
        if self._flits > 0:
            kleur = (255, 255, 255)
        elif self._woede > 0 and self._woede % 6 < 3:
            kleur = (255, 120, 0)
        else:
            kleur = (120, 10, 30)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (60, 0, 15), 4)

        # Horens
        arcade.draw_triangle_filled(x + 6, y + h, x + 20, y + h, x + 4, y + h + 22, (40, 0, 10))
        arcade.draw_triangle_filled(x + w - 20, y + h, x + w - 6, y + h, x + w - 4, y + h + 22, (40, 0, 10))

        # Grote gele ogen met rode pupillen (kijken naar de speler)
        oog_y = y + h - 24
        for dx in (-18, 18):
            arcade.draw_circle_filled(cx + dx, oog_y, 11, (255, 240, 150))
            arcade.draw_circle_filled(cx + dx + 3 * self._richting, oog_y, 5, (200, 0, 0))
        # Boze wenkbrauwen
        arcade.draw_line(cx - 28, oog_y + 14, cx - 8, oog_y + 6, (30, 0, 10), 5)
        arcade.draw_line(cx + 8, oog_y + 6, cx + 28, oog_y + 14, (30, 0, 10), 5)
        # Grijns met tanden
        arcade.draw_arc_outline(cx, y + 18, 40, 20, (30, 0, 10), 200, 340, 4)
        for tx in (cx - 14, cx - 4, cx + 6, cx + 16):
            arcade.draw_lrbt_rectangle_filled(tx - 3, tx + 3, y + 10, y + 22, arcade.color.WHITE)

        # Levens-hartjes boven de baas
        for i in range(self.levens):
            hx = cx - (self.levens - 1) * 10 + i * 20
            arcade.draw_circle_filled(hx - 3, y + h + 30, 4, arcade.color.RED)
            arcade.draw_circle_filled(hx + 3, y + h + 30, 4, arcade.color.RED)
            arcade.draw_triangle_filled(hx - 7, y + h + 30, hx + 7, y + h + 30, hx, y + h + 22, arcade.color.RED)

        # Schild-bubbel als hij beschermd is
        if self._schild:
            straal = w / 1.3 + math.sin(self._adem * 4) * 3
            arcade.draw_circle_filled(cx, y + h / 2, straal, (120, 210, 255, 40))
            arcade.draw_circle_outline(cx, y + h / 2, straal, (80, 200, 255), 3)

        # "BAAS"-label erboven
        arcade.draw_text("BAAS", cx - 22, y + h + 44, arcade.color.YELLOW, 14, bold=True)


# =============================================
# 👾 ARENA-VECHTER
# Het ENE monster van een gewoon arena-level.
# Hoe hoger 'niveau', hoe sterker: meer levens, sneller, én steeds meer
# krachten erbij. Ook verandert steeds zijn uiterlijk (nieuwe monsters!).
# =============================================
class ArenaVechter(Vijand):
    """Het ene monster van een arena-level. Krijgt steeds MEER krachten
    naarmate 'niveau' hoger is. Er zijn 12 verschillende krachten die in
    willekeurige combinaties voorkomen — meer dan 4000 mogelijkheden!"""

    # Alle krachten die een arena-monster kan hebben
    ALLE_KRACHTEN = ['teleport', 'schild', 'springen', 'dashen', 'vliegen',
                     'snel', 'taai', 'groot', 'flikker', 'zigzag', 'woede', 'spook',
                     'oproepen']

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=2, niveau=1):
        super().__init__(x, y, links_grens, rechts_grens, snelheid)
        self.niveau = niveau
        self.breedte = 34
        self.hoogte = 34
        # Basis-levens: meer naarmate je verder komt
        self.levens = 1 + niveau // 4

        # Kies willekeurig WELKE krachten dit monster heeft (vast per niveau).
        # Hoe hoger het niveau, hoe MEER krachten tegelijk → steeds moeilijker.
        rng = random.Random(niveau * 7 + 3)
        aantal = min(niveau // 2, len(self.ALLE_KRACHTEN))
        self.krachten = set(rng.sample(self.ALLE_KRACHTEN, aantal))

        # Handige vlaggen voor de krachten die iets 'doen'
        self.kan_teleport = 'teleport' in self.krachten
        self.kan_schild = 'schild' in self.krachten
        self.kan_springen = 'springen' in self.krachten
        self.kan_dashen = 'dashen' in self.krachten
        self.kan_vliegen = 'vliegen' in self.krachten
        self.kan_oproepen = 'oproepen' in self.krachten   # roept kleine hulpjes op!

        # Passieve krachten meteen toepassen
        if 'snel' in self.krachten:
            self.snelheid *= 1.6          # rent sneller
        if 'taai' in self.krachten:
            self.levens += 2              # extra taai
        if 'groot' in self.krachten:
            self.breedte = 46             # groter én steviger
            self.hoogte = 46
            self.levens += 1
        self.max_levens = self.levens

        # Uiterlijk: elke 2 niveaus een andere gedaante, feller bij hoger tier
        self.vorm = (niveau // 2) % 5
        self.tier = niveau // 10
        # Animatie- en kracht-timers
        self._teller = 0
        self._woede = 0
        self._flits = 0
        self._richting = 1 if snelheid >= 0 else -1
        self._grond_y = y
        self._schild = False
        self._schild_teller = 0
        self._teleport_teller = 0
        self._spring_teller = 0
        self._spring_vy = 0
        self._dash_teller = 0
        self._dash_actief = False
        self._dash_tijd = 0
        self._dash_richting = 1
        # Voor de oproep-kracht: kleine hulpjes maken (spel.py leest 'nieuwe_monsters')
        self.nieuwe_monsters = []
        self._spawn_teller = 0
        self._gespawnd = 0
        self._max_minions = min(1 + niveau // 6, 4)   # hoeveel hulpjes hij mag oproepen

    def _teleporteer(self):
        self.x = random.randint(int(self.links_grens),
                                int(self.rechts_grens - self.breedte))
        self._flits = 12

    def _roep_monster_op(self):
        """Roep een klein hulpje op (alleen als hij de oproep-kracht heeft)."""
        soort = random.choice([Vijand, SlijmVijand, SpringendVijand, VleermuisVijand])
        mx = random.randint(int(self.links_grens), int(self.rechts_grens - 30))
        my = self._grond_y + (110 if soort is VleermuisVijand else 0)
        snel = 2 + self.niveau * 0.05
        self.nieuwe_monsters.append(
            soort(mx, my, self.links_grens, self.rechts_grens, snel))

    def word_gestompt(self):
        """Verliest een leven en zet (als hij dat kan) meteen zijn krachten in."""
        self.levens -= 1
        self._woede = 30
        if self.kan_schild:
            self._schild = True
            self._schild_teller = 70
        if self.kan_teleport and self.levens > 0:
            self._teleporteer()

    def speler_springt_erop(self, px, py, pw, ph):
        """Met schild aan kun je hem NIET stompen."""
        if self._schild:
            return False
        return super().speler_springt_erop(px, py, pw, ph)

    def bijwerken(self, speler_x=None):
        self._teller += 0.2
        if self._woede > 0:
            self._woede -= 1
        if self._flits > 0:
            self._flits -= 1

        # KRACHT 'woede': razend (sneller) als hij gewond is
        factor = 1.0
        if 'woede' in self.krachten and self.levens <= self.max_levens / 2:
            factor = 1.7
        snel = self.snelheid * factor

        # Schild-timer
        if self._schild:
            self._schild_teller -= 1
            if self._schild_teller <= 0:
                self._schild = False

        # --- Horizontaal bewegen (dashen of gewoon lopen) ---
        if self.kan_dashen and self._dash_actief:
            self.x += self._dash_richting * snel * 2.5
            self._dash_tijd -= 1
            if self._dash_tijd <= 0:
                self._dash_actief = False
        else:
            self.x += self._richting * snel
        # Binnen de grenzen blijven
        if self.x <= self.links_grens:
            self.x = self.links_grens
            self._richting = 1
            self._dash_actief = False
        if self.x + self.breedte >= self.rechts_grens:
            self.x = self.rechts_grens - self.breedte
            self._richting = -1
            self._dash_actief = False

        # KRACHT: teleporteren
        if self.kan_teleport:
            self._teleport_teller += 1
            if self._teleport_teller >= max(80, 220 - self.niveau * 4):
                self._teleport_teller = 0
                self._teleporteer()

        # KRACHT: dashen naar de speler
        if self.kan_dashen and not self._dash_actief:
            self._dash_teller += 1
            if self._dash_teller >= max(110, 260 - self.niveau * 4):
                self._dash_teller = 0
                self._dash_actief = True
                self._dash_tijd = 22
                doel = speler_x if speler_x is not None else self.x
                self._dash_richting = 1 if doel > self.x else -1

        # KRACHT: kleine hulpjes oproepen (spawn)
        if self.kan_oproepen:
            self._spawn_teller += 1
            if self._spawn_teller >= 150 and self._gespawnd < self._max_minions:
                self._spawn_teller = 0
                self._gespawnd += 1
                self._roep_monster_op()

        # --- Verticaal bewegen: vliegen > springen > zigzag > gewoon ---
        if self.kan_vliegen:
            self.y = self._grond_y + 60 + math.sin(self._teller) * 25
        elif self.kan_springen:
            self._spring_teller += 1
            if self._spring_teller >= 70 and self.y <= self._grond_y:
                self._spring_vy = 11
                self._spring_teller = 0
            self._spring_vy -= 0.5
            self.y += self._spring_vy
            if self.y <= self._grond_y:
                self.y = self._grond_y
                self._spring_vy = 0
        elif 'zigzag' in self.krachten:
            # Wipt op en neer terwijl hij loopt
            self.y = self._grond_y + (math.sin(self._teller * 2) + 1) * 10
        else:
            self.y = self._grond_y

    # ---------- Tekenen ----------
    def _basis_kleur(self):
        """Kleur per gedaante, feller bij een hoger tier."""
        kleuren = [(90, 200, 90), (150, 90, 200), (230, 235, 255),
                   (240, 120, 40), (80, 200, 220)]
        r, g, b = kleuren[self.vorm]
        # Feller maken bij hogere tiers
        extra = min(self.tier * 15, 60)
        return (min(r + extra, 255), min(g + extra, 255), min(b + extra, 255))

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w // 2
        cy = y + h // 2

        # Doorzichtigheid door de krachten 'spook' en 'flikker'
        alpha = 255
        if 'spook' in self.krachten:
            alpha = 170
        if 'flikker' in self.krachten and int(self._teller * 3) % 2 == 0:
            alpha = 80

        # Gloed rondom (groter bij meer krachten)
        aantal_krachten = len(self.krachten)
        if aantal_krachten > 0:
            arcade.draw_circle_filled(cx, cy, w / 2 + 4 + aantal_krachten * 2,
                                      (255, 240, 120, 40))

        # Kleur: wit bij teleport-flits, oranje bij woede, anders zijn eigen kleur
        if self._flits > 0:
            kleur = (255, 255, 255)
        elif self._woede > 0 and self._woede % 6 < 3:
            kleur = (255, 140, 0)
        else:
            r, g, b = self._basis_kleur()
            kleur = (r, g, b, alpha)

        # De gedaante (5 verschillende uiterlijken)
        if self.vorm == 0:
            # Ronde blob
            arcade.draw_ellipse_filled(cx, cy, w, h, kleur)
            arcade.draw_ellipse_outline(cx, cy, w, h, OOG_KLEUR, 2)
        elif self.vorm == 1:
            # Stekelbal
            for i in range(8):
                hoek = math.radians(i * 45)
                arcade.draw_triangle_filled(
                    cx + math.cos(hoek) * (w / 2 - 2) - 3, cy + math.sin(hoek) * (h / 2 - 2),
                    cx + math.cos(hoek) * (w / 2 - 2) + 3, cy + math.sin(hoek) * (h / 2 - 2),
                    cx + math.cos(hoek) * (w / 2 + 8), cy + math.sin(hoek) * (h / 2 + 8), kleur)
            arcade.draw_circle_filled(cx, cy, w / 2 - 2, kleur)
        elif self.vorm == 2:
            # Spookachtig
            arcade.draw_ellipse_filled(cx, cy + 3, w, h - 3, kleur)
            for i in range(4):
                arcade.draw_circle_filled(x + i * (w // 3) + 5, y + 2, 5, kleur)
        elif self.vorm == 3:
            # Vlam
            arcade.draw_ellipse_filled(cx, cy, w, h + 6, kleur)
            arcade.draw_ellipse_filled(cx, cy - 2, w - 10, h - 8, (255, 230, 120))
        else:
            # Kristal/robot (hoekig)
            arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
            arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, OOG_KLEUR, 2)

        # Boze ogen (bij alle vormen)
        arcade.draw_circle_filled(cx - 7, cy + 3, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 7, cy + 3, 4, OOG_KLEUR)
        arcade.draw_circle_filled(cx - 6, cy + 4, 1, arcade.color.WHITE)
        arcade.draw_circle_filled(cx + 8, cy + 4, 1, arcade.color.WHITE)

        # Schild-bubbel als hij beschermd is
        if self._schild:
            straal = w / 1.4 + math.sin(self._teller * 4) * 2
            arcade.draw_circle_filled(cx, cy, straal, (120, 210, 255, 50))
            arcade.draw_circle_outline(cx, cy, straal, (80, 200, 255), 2)

        # Levens-stipjes boven het monster
        if self.max_levens > 1:
            for i in range(self.levens):
                arcade.draw_circle_filled(cx - (self.levens - 1) * 5 + i * 10,
                                          y + h + 14, 3, arcade.color.RED)

        # Eén gekleurd puntje per kracht die hij heeft (onderaan)
        kleur_per_kracht = {
            'teleport': (255, 100, 255), 'schild': (80, 200, 255),
            'springen': (120, 255, 120), 'dashen': (255, 160, 40),
            'vliegen': (255, 255, 255), 'snel': (255, 255, 0),
            'taai': (210, 90, 90), 'groot': (170, 110, 230),
            'flikker': (255, 180, 255), 'zigzag': (100, 255, 210),
            'woede': (255, 0, 0), 'spook': (210, 225, 255),
            'oproepen': (255, 120, 120),
        }
        aanwezig = [k for k in self.ALLE_KRACHTEN if k in self.krachten]
        start_x = cx - (len(aanwezig) - 1) * 3
        for i, k in enumerate(aanwezig):
            arcade.draw_circle_filled(start_x + i * 6, y - 6, 2.5, kleur_per_kracht[k])

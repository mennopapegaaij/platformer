# platform.py
# De Platform klasse — een stuk grond of een zwevend platform.

import arcade
from instellingen import GROND_KLEUR


def verf_of(obj, standaard):
    """Geef de verf-kleur van dit voorwerp als die er is, anders de standaardkleur.

    Zo krijgt een voorwerp waar je verf op deed helemaal de nieuwe kleur (je ziet
    de oude kleur niet meer), maar alleen op de plek waar het voorwerp echt is."""
    return getattr(obj, "verf_kleur", None) or standaard


class Platform:
    """Een platform (een stuk grond waar je op kunt staan)."""

    def __init__(self, x, y, breedte, hoogte):
        # Positie en grootte opslaan
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte

    def teken(self):
        """Teken het platform als een groen rechthoek."""
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y, self.y + self.hoogte,
            verf_of(self, GROND_KLEUR)
        )
        # Lichtere rand bovenop voor een 3D-effect (alleen zonder verf)
        if getattr(self, "verf_kleur", None) is None:
            arcade.draw_lrbt_rectangle_filled(
                self.x, self.x + self.breedte,
                self.y + self.hoogte - 6, self.y + self.hoogte,
                arcade.color.GREEN
            )

    def raakt(self, px, py, pw, ph):
        """Controleer of de speler dit platform raakt van bovenaf."""
        speler_links = px
        speler_rechts = px + pw
        speler_onder = py
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_boven = self.y + self.hoogte

        # De speler staat op het platform als hij van bovenaf landt
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_onder <= platform_boven and
                speler_boven > platform_boven):
            return True
        return False

    def raakt_van_onder(self, px, py, pw, ph):
        """Controleer of de speler met zijn hoofd tegen de onderkant stoot."""
        speler_links = px
        speler_rechts = px + pw
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_onder = self.y  # Onderkant van het platform

        # Hoofd van de speler raakt de onderkant van het platform
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_boven >= platform_onder and
                py < platform_onder):
            return True
        return False


class BlokPlatform(Platform):
    """Een blok waar je gewoon OP kunt staan (net als een platform),
    maar het ziet eruit als een stenen blok. Handig voor de racemodus."""

    def teken(self):
        """Teken het blok als een bruin bakstenen blok."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, verf_of(self, (150, 110, 80)))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 60, 40), 3)
        # Voegen (streepjes) voor een bakstenen-look
        arcade.draw_line(x, y + h / 2, x + w, y + h / 2, (90, 60, 40), 2)
        arcade.draw_line(x + w / 2, y, x + w / 2, y + h / 2, (90, 60, 40), 2)
        arcade.draw_line(x + w / 4, y + h / 2, x + w / 4, y + h, (90, 60, 40), 2)
        arcade.draw_line(x + 3 * w / 4, y + h / 2, x + 3 * w / 4, y + h, (90, 60, 40), 2)


class SchuinBlok:
    """Een schuin blok (helling): je loopt er soepel overheen omhoog of omlaag.

    richting "op"  -> loopt omhoog naar rechts  (/)
    richting "af"  -> loopt omhoog naar links   (\\)
    """

    is_schuin = True   # zo weet de speler: hier loop je schuin overheen

    def __init__(self, x, y, breedte, hoogte, richting="op"):
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte
        self.richting = richting

    def hoogte_op(self, px):
        """De hoogte van het loop-oppervlak op wereld-x = px."""
        t = (px - self.x) / self.breedte
        t = max(0.0, min(1.0, t))
        if self.richting == "op":
            return self.y + self.hoogte * t          # links laag, rechts hoog
        return self.y + self.hoogte * (1 - t)        # links hoog, rechts laag

    # De gewone (rechte) botsingen slaan we over — de speler regelt de helling zelf
    def raakt(self, px, py, pw, ph):
        return False

    def raakt_van_onder(self, px, py, pw, ph):
        return False

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        if self.richting == "op":
            punten = [(x, y), (x + w, y), (x + w, y + h)]     # driehoek /
        else:
            punten = [(x, y), (x + w, y), (x, y + h)]         # driehoek \
        arcade.draw_polygon_filled(punten, verf_of(self, (150, 110, 80)))
        arcade.draw_polygon_outline(punten, (90, 60, 40), 3)


STUITER_KRACHT = 15   # hoe hoog je stuitert op een stuiterblok


class StuiterBlok(BlokPlatform):
    """Een blok waar je bovenop stuitert (als een trampoline)."""

    stuiter = STUITER_KRACHT   # de speler leest dit uit bij het landen

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, verf_of(self, (60, 180, 90)))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (30, 120, 50), 3)
        # pijltje omhoog erop (zo zie je: hier stuiter je)
        cx = x + w / 2
        arcade.draw_triangle_filled(cx - 9, y + h * 0.45, cx + 9, y + h * 0.45,
                                    cx, y + h * 0.85, (230, 255, 230))


class VerdwijnBlok(BlokPlatform):
    """Een blok dat verdwijnt als je erop gaat staan, en na een tijdje terugkomt."""

    def __init__(self, x, y, breedte, hoogte):
        super().__init__(x, y, breedte, hoogte)
        self._staat = "heel"    # "heel" / "aftellen" / "weg"
        self._teller = 0

    @property
    def vast(self):
        return self._staat != "weg"   # als het weg is, is het niet meer vast

    def aangeraakt(self):
        """Wordt aangeroepen als de speler erop gaat staan."""
        if self._staat == "heel":
            self._staat = "aftellen"
            self._teller = 25

    def bijwerken(self):
        if self._staat == "aftellen":
            self._teller -= 1
            if self._teller <= 0:
                self._staat = "weg"
                self._teller = 110       # zo lang blijft het weg
        elif self._staat == "weg":
            self._teller -= 1
            if self._teller <= 0:
                self._staat = "heel"     # komt weer terug

    def raakt(self, *a):
        return self._staat != "weg" and super().raakt(*a)

    def raakt_van_onder(self, *a):
        return self._staat != "weg" and super().raakt_van_onder(*a)

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        if self._staat == "weg":
            arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (150, 150, 160), 1)
            return
        # Knippert oranje als het bijna verdwijnt
        if self._staat == "aftellen" and (self._teller // 4) % 2 == 0:
            kleur = (230, 120, 60)
        else:
            kleur = (200, 160, 90)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, verf_of(self, kleur))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (120, 80, 40), 3)
        # barstjes (zodat je ziet dat het kan breken)
        arcade.draw_line(x + w * 0.3, y + h, x + w * 0.42, y, (120, 80, 40), 1)
        arcade.draw_line(x + w * 0.7, y + h, x + w * 0.58, y, (120, 80, 40), 1)


class Deur(BlokPlatform):
    """Een deur: dicht = vast (je komt er niet door). Heb je een sleutel en raak je
    hem aan, dan gaat hij open en kun je erdoor."""

    is_deur = True

    def __init__(self, x, y, breedte, hoogte):
        super().__init__(x, y, breedte, hoogte)
        self.open = False

    def raakt(self, *a):
        return (not self.open) and super().raakt(*a)

    def raakt_van_onder(self, *a):
        return (not self.open) and super().raakt_van_onder(*a)

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        if self.open:
            # Open deur: alleen een dunne lijst, je kunt erdoor
            arcade.draw_lrbt_rectangle_outline(x + 2, x + w - 2, y, y + h, (150, 120, 70), 2)
            return
        # Dichte deur: bruin met een slot
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, verf_of(self, (140, 90, 50)))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 55, 25), 3)
        cx = x + w / 2
        # Slot (geel) met sleutelgat
        arcade.draw_circle_filled(cx, y + h * 0.55, 6, (240, 200, 40))
        arcade.draw_circle_filled(cx, y + h * 0.55, 2, (90, 60, 10))
        arcade.draw_lrbt_rectangle_filled(cx - 1.5, cx + 1.5, y + h * 0.4, y + h * 0.55, (90, 60, 10))


class BewegendBlok(BlokPlatform):
    """Een blok dat vanzelf heen-en-weer (hor) of op-en-neer (vert) beweegt.

    Je kunt erop staan en meerijden. Spring op het juiste moment over!"""

    def __init__(self, x, y, breedte, hoogte, richting="hor", afstand=120, snelheid=2):
        super().__init__(x, y, breedte, hoogte)
        self.start_x = x
        self.start_y = y
        self.richting = richting     # "hor" = links/rechts, "vert" = omhoog/omlaag
        self.afstand = afstand       # hoe ver het blok heen en weer gaat
        self.snelheid = snelheid
        self._d = 1                  # bewegingsrichting (1 of -1)
        self.dx = 0                  # hoeveel het dit stapje verschoof (om mee te rijden)
        self.dy = 0

    def bijwerken(self):
        self.dx = 0
        self.dy = 0
        if self.richting == "hor":
            self.x += self.snelheid * self._d
            self.dx = self.snelheid * self._d
            if self.x >= self.start_x + self.afstand:
                self.x = self.start_x + self.afstand
                self._d = -1
            elif self.x <= self.start_x:
                self.x = self.start_x
                self._d = 1
        else:
            self.y += self.snelheid * self._d
            self.dy = self.snelheid * self._d
            if self.y >= self.start_y + self.afstand:
                self.y = self.start_y + self.afstand
                self._d = -1
            elif self.y <= self.start_y:
                self.y = self.start_y
                self._d = 1

    def teken(self):
        super().teken()              # het gewone bruine blok
        # Twee pijltjes die de bewegingsrichting laten zien
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        wit = (245, 235, 210)
        if self.richting == "hor":
            arcade.draw_triangle_filled(cx - 8, cy, cx - 2, cy - 5, cx - 2, cy + 5, wit)
            arcade.draw_triangle_filled(cx + 8, cy, cx + 2, cy - 5, cx + 2, cy + 5, wit)
        else:
            arcade.draw_triangle_filled(cx, cy + 8, cx - 5, cy + 2, cx + 5, cy + 2, wit)
            arcade.draw_triangle_filled(cx, cy - 8, cx - 5, cy - 2, cx + 5, cy - 2, wit)


# De soorten blokken die je in de bouwmodus kunt kiezen
BLOK_SOORTEN = ["gewoon", "schuinop", "schuinaf", "half", "stuiter", "verdwijn",
                "beweeghor", "beweegvert", "deur"]
BLOK_NAAM = {"gewoon": "Blok", "schuinop": "Schuin /", "schuinaf": "Schuin \\",
             "half": "Half", "stuiter": "Stuiter", "verdwijn": "Verdwijn",
             "beweeghor": "Beweeg ↔", "beweegvert": "Beweeg ↕", "deur": "Deur"}

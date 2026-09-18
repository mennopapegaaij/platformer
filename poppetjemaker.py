# poppetjemaker.py
# De POPPETJES-MAKER: stel met knoppen je eigen poppetje samen.
# Kies de VORM, de KLEUR, of het OGEN heeft, en welke KUNSTJES het kan.
# Test het daarna in de testruimte (kies 'Mijn poppetje').

import arcade
from speler import Speler
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE
import voortgang as voortgang_module

# De vormen waar je uit kunt kiezen
VORMEN = ["blok", "rond", "driehoek", "ster", "hart", "ei", "diamant", "zeshoek"]
VORM_NAAM = {"blok": "Blok", "rond": "Rond", "driehoek": "Driehoek", "ster": "Ster",
             "hart": "Hart", "ei": "Ei", "diamant": "Diamant", "zeshoek": "Zeshoek"}

# De kunstjes (aan/uit) die je poppetje kan krijgen
KUNSTJES = [
    ("snel", "Snel"),
    ("hoog", "Hoog springen"),
    ("dubbel", "Dubbelsprong"),
    ("zweef", "Zweven"),
    ("muur", "Muursprong"),
    ("superhoog", "Superhoog"),
    ("zwaar", "Zwaar"),
    ("stuiter", "Stuiteren"),
    ("groeien", "Groeien"),
    ("groot", "Groot"),
    ("klein", "Klein"),
    ("draaien", "Draaien"),
    ("glad", "Glad"),
    ("magneet", "Magneet"),
    ("wind", "Wind"),
    ("spiegel", "Spiegel"),
    ("schild", "Schild"),
    ("driesprong", "Driesprong"),
    ("plakken", "Plakken"),
    ("turbo", "Turbo"),
]

# De kleuren waar je uit kunt kiezen
KLEUREN = [(255, 120, 60), (230, 60, 60), (60, 120, 230), (60, 190, 90),
           (240, 210, 40), (255, 120, 190), (160, 90, 220), (60, 200, 210),
           (255, 255, 255), (40, 40, 55), (120, 80, 40), (255, 90, 90),
           (90, 230, 140), (200, 140, 255), (255, 200, 60)]

# De standaard-instellingen als je nog nooit een poppetje hebt gemaakt
STANDAARD = {"vorm": "blok", "kleur": [255, 120, 60], "ogen": True}

KNOP_L = 380
KNOP_R = 780


class PoppetjeMaker(arcade.View):
    """Maak je eigen poppetje met knoppen (vorm, kleur, ogen en kunstjes)."""

    def __init__(self, terug):
        super().__init__()
        self.terug = terug
        # Laad je vorige poppetje, of begin met de standaard
        opgeslagen = voortgang_module.laad_voortgang().get("eigen_poppetje")
        self.instel = dict(STANDAARD)
        if opgeslagen:
            self.instel.update(opgeslagen)
        self._demo = Speler()
        self._demo.modus = "eigen"
        self._demo.breedte = 64
        self._demo.hoogte = 64

    def on_show_view(self):
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
        arcade.set_background_color((45, 45, 75))

    def _bewaar(self):
        voortgang_module.sla_eigen_poppetje_op(self.instel)

    # ---------- knop-plekken ----------
    def _knop_rect(self, i):
        """De plek (l, r, b, t) van knop i in het knoppen-raster (2 kolommen)."""
        kol = i % 2
        rij = i // 2
        l = 388 + kol * 200
        t = SCHERM_HOOGTE - 66 - rij * 34
        return (l, l + 190, t - 30, t)

    def _kleur_rect(self, i):
        """De plek van kleurvakje i (twee rijtjes onder het voorbeeld)."""
        maat = 24
        kol = i % 8
        rij = i // 8
        l = 30 + kol * (maat + 5)
        b = 74 - rij * (maat + 5)
        return (l, l + maat, b, b + maat)

    def _terug_rect(self):
        return (16, 150, SCHERM_HOOGTE - 40, SCHERM_HOOGTE - 12)

    # ---------- tekenen ----------
    def on_draw(self):
        self.clear()
        arcade.draw_text("🛠️  Poppetjes-maker", SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 34,
                         arcade.color.WHITE, 22, bold=True, anchor_x="center")

        # Terug-knop
        tl, tr, tb, tt = self._terug_rect()
        arcade.draw_lrbt_rectangle_filled(tl, tr, tb, tt, (100, 100, 120))
        arcade.draw_lrbt_rectangle_outline(tl, tr, tb, tt, arcade.color.WHITE, 2)
        arcade.draw_text("← Terug (ESC)", (tl + tr) // 2, (tb + tt) // 2 - 6,
                         arcade.color.WHITE, 11, bold=True, anchor_x="center")

        # Voorbeeld-vak (links)
        arcade.draw_lrbt_rectangle_filled(30, 350, 120, 430, (30, 30, 55))
        arcade.draw_lrbt_rectangle_outline(30, 350, 120, 430, (120, 120, 160), 2)
        arcade.draw_text("Voorbeeld", 40, 408, (180, 180, 210), 11, bold=True)
        # Teken het poppetje in het midden van het vak
        self._demo.eigen_instel = self.instel
        self._demo.x = 190 - self._demo.breedte / 2
        self._demo.y = 150
        try:
            self._demo.teken()
        except Exception:
            pass
        # Hoeveel kunstjes staan aan?
        aantal = sum(1 for s, _ in KUNSTJES if self.instel.get(s))
        arcade.draw_text("Kunstjes aan: %d van %d" % (aantal, len(KUNSTJES)),
                         40, 128, arcade.color.YELLOW, 12, bold=True)

        # Kleur-kiezer (onder het voorbeeld)
        arcade.draw_text("Kleur:", 30, 104, arcade.color.WHITE, 11, bold=True)
        for i, kleur in enumerate(KLEUREN):
            l, r, b, t = self._kleur_rect(i)
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, kleur)
            gekozen = (list(kleur) == list(self.instel["kleur"]))
            arcade.draw_lrbt_rectangle_outline(l, r, b, t,
                                               arcade.color.WHITE if gekozen else (70, 70, 70),
                                               3 if gekozen else 1)

        # De knoppen (rechts): vorm, ogen en de kunstjes
        self._teken_knop(0, "Vorm: " + VORM_NAAM[self.instel["vorm"]], (70, 110, 170), True)
        self._teken_knop(1, "Ogen: " + ("aan" if self.instel["ogen"] else "uit"),
                         (70, 110, 170), self.instel["ogen"])
        for j, (sleutel, naam) in enumerate(KUNSTJES):
            aan = bool(self.instel.get(sleutel))
            kleur = (40, 160, 70) if aan else (90, 70, 70)
            self._teken_knop(2 + j, naam + ("  ✓" if aan else ""), kleur, aan)

        arcade.draw_text("Klik op de knoppen om je poppetje te maken  •  "
                         "test het in de Testruimte (kies 'Mijn poppetje')",
                         SCHERM_BREEDTE // 2, 20, (190, 190, 210), 10, anchor_x="center")

    def _teken_knop(self, i, tekst, kleur, aan):
        l, r, b, t = self._knop_rect(i)
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, kleur)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t,
                                           (255, 220, 120) if aan else (120, 120, 140), 2)
        arcade.draw_text(tekst, (l + r) // 2, (b + t) // 2 - 6, arcade.color.WHITE, 11,
                         bold=True, anchor_x="center")

    # ---------- klikken ----------
    def on_mouse_press(self, x, y, knop, modifiers):
        # Terug?
        tl, tr, tb, tt = self._terug_rect()
        if tl <= x <= tr and tb <= y <= tt:
            self.window.show_view(self.terug)
            return
        # Kleur gekozen?
        for i, kleur in enumerate(KLEUREN):
            l, r, b, t = self._kleur_rect(i)
            if l <= x <= r and b <= y <= t:
                self.instel["kleur"] = list(kleur)
                self._bewaar()
                return
        # Knoppen?
        for i in range(2 + len(KUNSTJES)):
            l, r, b, t = self._knop_rect(i)
            if l <= x <= r and b <= y <= t:
                if i == 0:
                    # Vorm doorklikken
                    idx = (VORMEN.index(self.instel["vorm"]) + 1) % len(VORMEN)
                    self.instel["vorm"] = VORMEN[idx]
                elif i == 1:
                    self.instel["ogen"] = not self.instel["ogen"]
                else:
                    sleutel = KUNSTJES[i - 2][0]
                    self.instel[sleutel] = not self.instel.get(sleutel)
                self._bewaar()
                return

    def on_key_press(self, toets, modifiers):
        if toets in (arcade.key.ESCAPE, arcade.key.ENTER, arcade.key.NUM_ENTER):
            self.window.show_view(self.terug)

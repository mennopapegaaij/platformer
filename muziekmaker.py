# muziekmaker.py
# Een klein scherm waar je je EIGEN deuntje maakt: klik noten in een raster.
# Het deuntje speelt daarna steeds rond in je zelfgebouwde level.

import arcade
import muziek
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE

STAPPEN = 16                 # hoeveel noten je deuntje lang is
RIJEN = len(muziek.NOOT_NAMEN)   # 8 noten (do..do)

# Elke noot krijgt een eigen kleur (laag -> hoog)
NOOT_KLEUR = [(230, 80, 80), (240, 150, 40), (240, 220, 60), (90, 200, 90),
              (60, 170, 200), (70, 110, 230), (160, 90, 220), (230, 90, 180)]


class MuziekMaker(arcade.View):
    """Maak je eigen deuntje door noten in een raster te klikken."""

    def __init__(self, bouwer, noten=None):
        super().__init__()
        self.bouwer = bouwer                    # om naar terug te gaan en op te slaan
        # noten: een lijst van STAPPEN getallen (-1 = stilte, 0..7 = een noot)
        self.noten = list(noten) if noten else [-1] * STAPPEN
        while len(self.noten) < STAPPEN:
            self.noten.append(-1)
        # Speel-aan-het-afspelen?
        self._speelt = False
        self._stap = 0
        self._teller = 0.0
        # Rooster-afmetingen berekenen
        self.rand_l = 70                        # ruimte links voor de noot-namen
        self.rand_o = 70                        # ruimte onderaan voor de knoppen
        self.cel_b = (SCHERM_BREEDTE - self.rand_l - 20) / STAPPEN
        self.cel_h = (SCHERM_HOOGTE - self.rand_o - 40) / RIJEN
        # Knoppen onderaan
        self.knoppen = {"speel": (20, 170), "wis": (185, 305), "klaar": (SCHERM_BREEDTE - 175, SCHERM_BREEDTE - 20)}

    def on_show_view(self):
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
        arcade.set_background_color((30, 30, 50))
        muziek.laad_tonen()                     # maak de toontjes vast klaar

    def _cel_xy(self, stap, rij):
        """Scherm-plek (links-onder) van vakje (stap, rij). rij 0 = onderste noot (do)."""
        x = self.rand_l + stap * self.cel_b
        y = self.rand_o + rij * self.cel_h
        return x, y

    def on_draw(self):
        self.clear()
        arcade.draw_text("🎹 Maak je eigen deuntje!", SCHERM_BREEDTE / 2, SCHERM_HOOGTE - 32,
                         arcade.color.WHITE, 18, bold=True, anchor_x="center")

        # Noot-namen links + rasterlijnen
        for rij in range(RIJEN):
            x, y = self._cel_xy(0, rij)
            arcade.draw_text(muziek.NOOT_NAMEN[rij], 10, y + self.cel_h / 2 - 8,
                             NOOT_KLEUR[rij], 13, bold=True)
        # Vakjes tekenen
        for stap in range(STAPPEN):
            for rij in range(RIJEN):
                x, y = self._cel_xy(stap, rij)
                rand = (90, 90, 120)
                # licht om de beat (elke 4 stappen) te zien
                vul = (55, 55, 80) if (stap // 4) % 2 == 0 else (45, 45, 70)
                arcade.draw_lrbt_rectangle_filled(x + 1, x + self.cel_b - 1,
                                                  y + 1, y + self.cel_h - 1, vul)
                arcade.draw_lrbt_rectangle_outline(x + 1, x + self.cel_b - 1,
                                                   y + 1, y + self.cel_h - 1, rand, 1)
                # is hier een noot gezet?
                if self.noten[stap] == rij:
                    arcade.draw_lrbt_rectangle_filled(x + 3, x + self.cel_b - 3,
                                                      y + 3, y + self.cel_h - 3, NOOT_KLEUR[rij])

        # Speel-lijntje (waar we nu zijn tijdens afspelen)
        if self._speelt:
            lx = self.rand_l + (self._stap + 0.5) * self.cel_b
            arcade.draw_line(lx, self.rand_o, lx, SCHERM_HOOGTE - 40, (255, 255, 255), 2)

        # Knoppen onderaan
        namen = {"speel": ("⏸ Stop" if self._speelt else "▶ Speel", (40, 160, 60)),
                 "wis": ("🗑 Wissen", (170, 60, 60)),
                 "klaar": ("✓ Klaar", (40, 110, 180))}
        for naam, (l, r) in self.knoppen.items():
            tekst, kleur = namen[naam]
            arcade.draw_lrbt_rectangle_filled(l, r, 15, 55, kleur)
            arcade.draw_lrbt_rectangle_outline(l, r, 15, 55, arcade.color.WHITE, 2)
            arcade.draw_text(tekst, (l + r) / 2, 28, arcade.color.WHITE, 14,
                             bold=True, anchor_x="center")

    def on_mouse_press(self, x, y, knop, modifiers):
        # Knop aangeklikt?
        if 15 <= y <= 55:
            for naam, (l, r) in self.knoppen.items():
                if l <= x <= r:
                    if naam == "speel":
                        self._speelt = not self._speelt
                        self._stap = 0
                        self._teller = 0.0
                    elif naam == "wis":
                        self.noten = [-1] * STAPPEN
                    elif naam == "klaar":
                        self._klaar()
                    return
        # Anders: een vakje in het raster aan/uit zetten
        if x < self.rand_l or y < self.rand_o:
            return
        stap = int((x - self.rand_l) // self.cel_b)
        rij = int((y - self.rand_o) // self.cel_h)
        if 0 <= stap < STAPPEN and 0 <= rij < RIJEN:
            if self.noten[stap] == rij:
                self.noten[stap] = -1           # zelfde noot -> weer stilte
            else:
                self.noten[stap] = rij          # deze noot zetten
                muziek.speel_noot(rij)          # even voorspelen

    def on_update(self, dt):
        if not self._speelt:
            return
        self._teller += dt
        if self._teller >= 0.22:                # tempo van het afspelen
            self._teller -= 0.22
            noot = self.noten[self._stap]
            if noot != -1:
                muziek.speel_noot(noot)
            self._stap = (self._stap + 1) % STAPPEN

    def on_key_press(self, toets, modifiers):
        if toets in (arcade.key.ESCAPE, arcade.key.ENTER, arcade.key.NUM_ENTER):
            self._klaar()

    def _klaar(self):
        """Sla het deuntje op bij de bouwer en ga terug."""
        self.bouwer.muziek = list(self.noten)
        self.window.show_view(self.bouwer)

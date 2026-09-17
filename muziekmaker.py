# muziekmaker.py
# Een klein scherm waar je je EIGEN deuntje maakt: klik noten in een raster.
# Je kunt zoveel noten maken als je wilt: scroll met ◀ ▶ (of de pijltjes) naar rechts.
# Het deuntje speelt daarna steeds rond in je zelfgebouwde level.

import arcade
import muziek
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE

ZICHT = 16                   # hoeveel stappen je tegelijk ziet
STAPPEN = ZICHT              # begin-lengte van een nieuw deuntje
RIJEN = len(muziek.NOOT_NAMEN)   # 8 noten (do..do)

# Elke noot krijgt een eigen kleur (laag -> hoog)
NOOT_KLEUR = [(230, 80, 80), (240, 150, 40), (240, 220, 60), (90, 200, 90),
              (60, 170, 200), (70, 110, 230), (160, 90, 220), (230, 90, 180)]


class MuziekMaker(arcade.View):
    """Maak je eigen deuntje door noten in een raster te klikken (zo lang als je wilt)."""

    def __init__(self, bouwer, noten=None):
        super().__init__()
        self.bouwer = bouwer                    # om naar terug te gaan en op te slaan
        # noten: lijst getallen (-1 = stilte, 0..7 = een noot). Mag oneindig lang!
        self.noten = list(noten) if noten else [-1] * STAPPEN
        self._zorg_lengte(ZICHT)
        self.scroll_stap = 0                    # eerste stap die je in beeld ziet
        # Afspelen?
        self._speelt = False
        self._stap = 0
        self._teller = 0.0
        # Kant-en-klare liedjes kiezen
        self._kies_index = -1        # welk kant-en-klaar liedje is gekozen (-1 = geen)
        self._kies_naam = ""         # naam van het gekozen liedje (voor op het scherm)
        # Rooster-afmetingen
        self.rand_l = 70                        # ruimte links voor de noot-namen
        self.rand_o = 70                        # ruimte onderaan voor de knoppen
        self.rand_b = 70                        # ruimte bovenaan (titel + scroll-knoppen)
        self.cel_b = (SCHERM_BREEDTE - self.rand_l - 20) / ZICHT
        self.cel_h = (SCHERM_HOOGTE - self.rand_o - self.rand_b) / RIJEN
        # Knoppen onderaan
        self.knoppen = {"speel": (20, 170), "wis": (185, 305), "kies": (320, 470),
                        "klaar": (SCHERM_BREEDTE - 175, SCHERM_BREEDTE - 20)}
        # Scroll-knoppen bovenaan (◀ en ▶)
        self.scroll_knoppen = {"links": (SCHERM_BREEDTE - 130, SCHERM_BREEDTE - 95),
                               "rechts": (SCHERM_BREEDTE - 90, SCHERM_BREEDTE - 55)}
        self._sk_b, self._sk_t = SCHERM_HOOGTE - 40, SCHERM_HOOGTE - 12

    # ---------- lengte-beheer ----------
    def _zorg_lengte(self, n):
        """Zorg dat het deuntje minstens n stappen lang is (vul aan met stilte)."""
        while len(self.noten) < n:
            self.noten.append(-1)

    def on_show_view(self):
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
        arcade.set_background_color((30, 30, 50))
        muziek.laad_tonen()                     # maak de toontjes vast klaar

    def _cel_xy(self, kol, rij):
        """Scherm-plek (links-onder) van zicht-kolom kol (0..ZICHT-1) en rij."""
        x = self.rand_l + kol * self.cel_b
        y = self.rand_o + rij * self.cel_h
        return x, y

    # ---------- tekenen ----------
    def on_draw(self):
        self.clear()
        arcade.draw_text("🎹 Maak je eigen deuntje!", 20, SCHERM_HOOGTE - 34,
                         arcade.color.WHITE, 18, bold=True)
        if self._kies_naam:
            arcade.draw_text("♪ %s" % self._kies_naam, 340, SCHERM_HOOGTE - 30,
                             (200, 180, 255), 13, bold=True)

        # Noot-namen links
        for rij in range(RIJEN):
            x, y = self._cel_xy(0, rij)
            arcade.draw_text(muziek.NOOT_NAMEN[rij], 10, y + self.cel_h / 2 - 8,
                             NOOT_KLEUR[rij], 13, bold=True)

        # Vakjes (alleen het zichtbare stuk)
        for kol in range(ZICHT):
            stap = self.scroll_stap + kol
            for rij in range(RIJEN):
                x, y = self._cel_xy(kol, rij)
                vul = (55, 55, 80) if (stap // 4) % 2 == 0 else (45, 45, 70)
                arcade.draw_lrbt_rectangle_filled(x + 1, x + self.cel_b - 1,
                                                  y + 1, y + self.cel_h - 1, vul)
                arcade.draw_lrbt_rectangle_outline(x + 1, x + self.cel_b - 1,
                                                   y + 1, y + self.cel_h - 1, (90, 90, 120), 1)
                if stap < len(self.noten) and self.noten[stap] == rij:
                    arcade.draw_lrbt_rectangle_filled(x + 3, x + self.cel_b - 3,
                                                      y + 3, y + self.cel_h - 3, NOOT_KLEUR[rij])
            # stap-nummer onderaan de kolom
            arcade.draw_text(str(stap + 1), x + self.cel_b / 2, self.rand_o - 16,
                             (150, 150, 170), 9, anchor_x="center")

        # Speel-lijntje (alleen als de huidige stap in beeld is)
        if self._speelt and self.scroll_stap <= self._stap < self.scroll_stap + ZICHT:
            lx = self.rand_l + (self._stap - self.scroll_stap + 0.5) * self.cel_b
            arcade.draw_line(lx, self.rand_o, lx, SCHERM_HOOGTE - self.rand_b,
                             (255, 255, 255), 2)

        # Scroll-knoppen + hoeveel noten er zijn
        for naam, (l, r) in self.scroll_knoppen.items():
            arcade.draw_lrbt_rectangle_filled(l, r, self._sk_b, self._sk_t, (70, 70, 100))
            arcade.draw_lrbt_rectangle_outline(l, r, self._sk_b, self._sk_t, arcade.color.WHITE, 2)
            pijl = "◀" if naam == "links" else "▶"
            arcade.draw_text(pijl, (l + r) / 2, self._sk_b + 6, arcade.color.WHITE, 14,
                             bold=True, anchor_x="center")
        arcade.draw_text("noten: %d" % len(self.noten), SCHERM_BREEDTE - 300, self._sk_b + 6,
                         arcade.color.WHITE, 12, bold=True)

        # Knoppen onderaan
        namen = {"speel": ("⏸ Stop" if self._speelt else "▶ Speel", (40, 160, 60)),
                 "wis": ("🗑 Wissen", (170, 60, 60)),
                 "kies": ("🎵 Kies liedje", (150, 90, 190)),
                 "klaar": ("✓ Klaar", (40, 110, 180))}
        for naam, (l, r) in self.knoppen.items():
            tekst, kleur = namen[naam]
            arcade.draw_lrbt_rectangle_filled(l, r, 15, 55, kleur)
            arcade.draw_lrbt_rectangle_outline(l, r, 15, 55, arcade.color.WHITE, 2)
            arcade.draw_text(tekst, (l + r) / 2, 28, arcade.color.WHITE, 14,
                             bold=True, anchor_x="center")

        arcade.draw_text("◀ ▶ of pijltjes = meer noten zien (zo lang als je wilt!)",
                         20, 60, (170, 170, 190), 10)

    # ---------- muis ----------
    def on_mouse_press(self, x, y, knop, modifiers):
        # Scroll-knoppen?
        if self._sk_b <= y <= self._sk_t:
            for naam, (l, r) in self.scroll_knoppen.items():
                if l <= x <= r:
                    self._scroll(-1 if naam == "links" else 1)
                    return
        # Onderste knoppen?
        if 15 <= y <= 55:
            for naam, (l, r) in self.knoppen.items():
                if l <= x <= r:
                    if naam == "speel":
                        self._speelt = not self._speelt
                        self._stap = 0
                        self._teller = 0.0
                    elif naam == "wis":
                        self.noten = [-1] * ZICHT
                        self.scroll_stap = 0
                        self._kies_naam = ""
                    elif naam == "kies":
                        self._kies_liedje()
                    elif naam == "klaar":
                        self._klaar()
                    return
        # Een vakje aan/uit zetten
        if x < self.rand_l or y < self.rand_o or y > SCHERM_HOOGTE - self.rand_b:
            return
        kol = int((x - self.rand_l) // self.cel_b)
        rij = int((y - self.rand_o) // self.cel_h)
        if 0 <= kol < ZICHT and 0 <= rij < RIJEN:
            stap = self.scroll_stap + kol
            self._zorg_lengte(stap + 1)
            if self.noten[stap] == rij:
                self.noten[stap] = -1           # zelfde noot -> weer stilte
            else:
                self.noten[stap] = rij          # deze noot zetten
                muziek.speel_noot(rij)          # even voorspelen

    def _kies_liedje(self):
        """Laad het volgende kant-en-klare liedje in het raster (klik nog eens = volgende)."""
        liedjes = muziek.KLAAR_LIEDJES
        if not liedjes:
            return
        self._kies_index = (self._kies_index + 1) % len(liedjes)
        naam, noten = liedjes[self._kies_index]
        self.noten = list(noten)                # het gekozen liedje in het raster zetten
        self._zorg_lengte(ZICHT)
        self.scroll_stap = 0
        self._kies_naam = naam
        self._speelt = False                    # begin netjes opnieuw

    def _scroll(self, richting):
        """Schuif een stapje naar links (-1) of rechts (+1)."""
        self.scroll_stap = max(0, self.scroll_stap + richting)
        self._zorg_lengte(self.scroll_stap + ZICHT)   # ruimte maken voor nieuwe noten

    # ---------- update ----------
    def on_update(self, dt):
        if not self._speelt:
            return
        self._teller += dt
        if self._teller >= 0.22:                # tempo van het afspelen
            self._teller -= 0.22
            noot = self.noten[self._stap] if self._stap < len(self.noten) else -1
            if noot != -1:
                muziek.speel_noot(noot)
            self._stap = (self._stap + 1) % max(1, len(self.noten))

    def on_key_press(self, toets, modifiers):
        if toets == arcade.key.LEFT:
            self._scroll(-1)
        elif toets == arcade.key.RIGHT:
            self._scroll(1)
        elif toets in (arcade.key.ESCAPE, arcade.key.ENTER, arcade.key.NUM_ENTER):
            self._klaar()

    def _klaar(self):
        """Sla het deuntje op bij de bouwer en ga terug (stilte aan het eind eraf)."""
        noten = list(self.noten)
        while noten and noten[-1] == -1:        # onnodige stilte aan het eind weghalen
            noten.pop()
        self.bouwer.muziek = noten
        self.window.show_view(self.bouwer)

# bouwer.py
# De BOUWMODUS: maak je eigen level!
# Je plaatst met de muis grond, blokken, spikes, vijanden, hartjes en een
# finishvlag op een raster. Daarna kun je je eigen level spelen.

import arcade
import json
import os
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE

CEL = 40                       # grootte van één raster-vakje
BESTAND = "eigen_level.json"   # hier wordt je level opgeslagen

# De dingen die je kunt plaatsen (op volgorde in het palet)
ITEMS = ["grond", "blok", "spike", "vijand", "hart", "vlag", "gum"]
ITEM_NAAM = {
    "grond": "Grond", "blok": "Blok", "spike": "Spike", "vijand": "Vijand",
    "hart": "Hartje", "vlag": "Finish", "gum": "Gum",
}

# Waar de bovenbalk (met knoppen) begint
BALK_Y = 442


def teken_item(soort, x, y, grootte):
    """Teken een klein plaatje van een item in een vakje op scherm (x, y)."""
    g = grootte
    if soort == "grond":
        arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (60, 160, 60))
        arcade.draw_lrbt_rectangle_filled(x, x + g, y + g - 5, y + g, (90, 200, 90))
    elif soort == "blok":
        arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (150, 110, 80))
        arcade.draw_lrbt_rectangle_outline(x, x + g, y, y + g, (90, 60, 40), 2)
    elif soort == "spike":
        for i in range(2):
            sx = x + 4 + i * (g // 2)
            arcade.draw_triangle_filled(sx, y + 3, sx + g // 2 - 4, y + 3,
                                        sx + g // 4 - 2, y + g - 6, (185, 185, 200))
    elif soort == "vijand":
        arcade.draw_lrbt_rectangle_filled(x + 5, x + g - 5, y + 5, y + g - 5, (220, 40, 40))
        arcade.draw_circle_filled(x + g // 2 - 6, y + g - 12, 3, arcade.color.BLACK)
        arcade.draw_circle_filled(x + g // 2 + 6, y + g - 12, 3, arcade.color.BLACK)
    elif soort == "hart":
        cx, cy = x + g // 2, y + g // 2
        arcade.draw_circle_filled(cx - 5, cy + 3, 6, arcade.color.RED)
        arcade.draw_circle_filled(cx + 5, cy + 3, 6, arcade.color.RED)
        arcade.draw_triangle_filled(cx - 10, cy + 2, cx + 10, cy + 2, cx, cy - 9, arcade.color.RED)
    elif soort == "vlag":
        arcade.draw_line(x + 8, y + 4, x + 8, y + g - 2, arcade.color.WHITE, 3)
        arcade.draw_triangle_filled(x + 8, y + g - 2, x + g - 4, y + g - 8,
                                    x + 8, y + g - 16, arcade.color.GREEN)
    elif soort == "gum":
        arcade.draw_lrbt_rectangle_filled(x + 5, x + g - 5, y + 8, y + g - 8, (255, 180, 200))
        arcade.draw_lrbt_rectangle_outline(x + 5, x + g - 5, y + 8, y + g - 8, (200, 100, 130), 2)


class BouwerView(arcade.View):
    """Het bouwscherm — maak hier je eigen level."""

    # Knoppen in de bovenbalk: naam -> (links, rechts)
    def __init__(self, voltooid_levels, punten=0, levens=None,
                 arena_record=0, race_record=0, vlucht_record=0):
        super().__init__()
        self.voltooid = voltooid_levels
        self.punten = punten
        self.levens = levens
        self.arena_record = arena_record
        self.race_record = race_record
        self.vlucht_record = vlucht_record

        self.grid = {}                 # (kol, rij) -> soort
        self.gekozen = "grond"         # welk item je nu plaatst
        # Type van je level: "gewoon" (lopen), "race" (auto-run), "vlucht" (vliegen)
        self.mode = "gewoon"
        self.scroll = 0                # hoe ver je naar rechts hebt geschoven
        self._scroll_richting = 0      # -1 links, +1 rechts (met pijltjestoetsen)
        self._melding = ""             # kort berichtje (bv. "Opgeslagen!")
        self._melding_teller = 0

        # Palet-knoppen (links) en actie-knoppen (rechts) uitrekenen
        self.palet_knoppen = {}        # soort -> (l, r)
        for i, soort in enumerate(ITEMS):
            l = 8 + i * 50
            self.palet_knoppen[soort] = (l, l + 46)
        self.actie_knoppen = {         # naam -> (l, r)
            "spelen": (356, 428),
            "opslaan": (432, 512),
            "wissen": (516, 584),
            "kaart": (588, 650),
            "type": (656, 792),
        }

        self._laad()

    # ---------- Opslaan en laden ----------
    def _laad(self):
        """Laad een opgeslagen level, of maak een klein start-level."""
        if os.path.exists(BESTAND):
            try:
                with open(BESTAND, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    tiles = data.get("tiles", [])
                    # Nieuw formaat heeft "mode"; oud formaat had alleen "race" (True/False)
                    if "mode" in data:
                        self.mode = data["mode"]
                    elif data.get("race", False):
                        self.mode = "race"
                    else:
                        self.mode = "gewoon"
                else:
                    tiles = data   # oud formaat (alleen een lijst met vakjes)
                self.grid = {(int(k), int(r)): s for k, r, s in tiles}
                return
            except Exception:
                pass
        # Start-level: een stukje grond en een finishvlag als voorbeeld
        for kol in range(0, 10):
            self.grid[(kol, 0)] = "grond"
        self.grid[(12, 1)] = "vlag"

    def _opslaan(self):
        data = {"tiles": [[k, r, s] for (k, r), s in self.grid.items()],
                "mode": self.mode}
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self._melding = "💾 Opgeslagen!"
        self._melding_teller = 120

    # ---------- Tekenen ----------
    def on_show_view(self):
        arcade.set_background_color((120, 190, 230))   # lichtblauwe lucht

    def on_draw(self):
        self.clear()
        self._teken_raster()
        self._teken_items()
        self._teken_startmarker()
        self._teken_balk()

    def _teken_raster(self):
        """Teken lichte rasterlijnen in het bouwgebied."""
        # Verticale lijnen
        eerste_kol = int(self.scroll // CEL)
        for kol in range(eerste_kol, eerste_kol + SCHERM_BREEDTE // CEL + 2):
            sx = kol * CEL - self.scroll
            arcade.draw_line(sx, 0, sx, BALK_Y, (255, 255, 255, 40), 1)
        # Horizontale lijnen
        for rij in range(0, BALK_Y // CEL + 1):
            arcade.draw_line(0, rij * CEL, SCHERM_BREEDTE, rij * CEL, (255, 255, 255, 40), 1)
        # De grondlijn wat duidelijker
        arcade.draw_line(0, CEL, SCHERM_BREEDTE, CEL, (255, 255, 255, 110), 2)

    def _teken_items(self):
        """Teken alle geplaatste items (alleen die in beeld zijn)."""
        for (kol, rij), soort in self.grid.items():
            sx = kol * CEL - self.scroll
            if sx < -CEL or sx > SCHERM_BREEDTE:
                continue
            teken_item(soort, sx, rij * CEL, CEL)

    def _teken_startmarker(self):
        """Teken waar de speler begint (linksonder)."""
        sx = 50 - self.scroll
        if -40 < sx < SCHERM_BREEDTE:
            arcade.draw_lrbt_rectangle_filled(sx, sx + 32, CEL, CEL + 32, arcade.color.YELLOW)
            arcade.draw_text("start", sx - 4, CEL + 34, arcade.color.BLACK, 9, bold=True)

    def _teken_balk(self):
        """Teken de bovenbalk met het palet en de knoppen."""
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, BALK_Y, SCHERM_HOOGTE, (30, 30, 45))

        # Palet-knoppen (kies wat je plaatst)
        for soort, (l, r) in self.palet_knoppen.items():
            gekozen = (soort == self.gekozen)
            rand = arcade.color.YELLOW if gekozen else (90, 90, 110)
            arcade.draw_lrbt_rectangle_filled(l, r, BALK_Y + 6, SCHERM_HOOGTE - 18, (60, 60, 80))
            arcade.draw_lrbt_rectangle_outline(l, r, BALK_Y + 6, SCHERM_HOOGTE - 18, rand, 3 if gekozen else 1)
            teken_item(soort, l + 3, BALK_Y + 10, 40)
            arcade.draw_text(ITEM_NAAM[soort], (l + r) // 2, BALK_Y + 1,
                             arcade.color.WHITE, 8, anchor_x="center")

        # Kleur en tekst van de Type-knop hangen af van het gekozen type
        type_kleur = {"gewoon": (150, 100, 30), "race": (40, 110, 180),
                      "vlucht": (120, 60, 170)}[self.mode]
        type_tekst = {"gewoon": "🚶 Gewoon", "race": "🏁 Race",
                      "vlucht": "✈️ Vliegen"}[self.mode]
        # Actie-knoppen
        kleuren = {"spelen": (40, 160, 60), "opslaan": (40, 110, 180),
                   "wissen": (170, 60, 60), "kaart": (100, 100, 120),
                   "type": type_kleur}
        teksten = {"spelen": "▶ Spelen", "opslaan": "💾 Opslaan",
                   "wissen": "🗑 Wissen", "kaart": "🗺 Kaart",
                   "type": type_tekst}
        for naam, (l, r) in self.actie_knoppen.items():
            arcade.draw_lrbt_rectangle_filled(l, r, BALK_Y + 8, SCHERM_HOOGTE - 8, kleuren[naam])
            arcade.draw_lrbt_rectangle_outline(l, r, BALK_Y + 8, SCHERM_HOOGTE - 8, arcade.color.WHITE, 2)
            if naam == "type":
                arcade.draw_text("Type:", (l + r) // 2, SCHERM_HOOGTE - 20,
                                 arcade.color.WHITE, 9, anchor_x="center")
                arcade.draw_text(teksten[naam], (l + r) // 2, BALK_Y + 14,
                                 arcade.color.WHITE, 12, bold=True, anchor_x="center")
            else:
                arcade.draw_text(teksten[naam], (l + r) // 2, BALK_Y + 20,
                                 arcade.color.WHITE, 11, bold=True, anchor_x="center")

        # Uitleg / melding onderin het bouwgebied
        if self._melding_teller > 0:
            arcade.draw_text(self._melding, SCHERM_BREEDTE // 2, 10,
                             arcade.color.YELLOW, 16, bold=True, anchor_x="center")
        else:
            arcade.draw_text("Kies een blokje en klik om te plaatsen  •  ←→ = schuiven  •  "
                             "Type-knop: gewoon, race of vliegen", SCHERM_BREEDTE // 2, 8,
                             arcade.color.WHITE, 10, anchor_x="center")

    # ---------- Muis ----------
    def on_mouse_press(self, x, y, knop, modifiers):
        if y >= BALK_Y:
            self._klik_balk(x, y)
            return
        # In het bouwgebied: plaats of gum het gekozen item
        wereld_x = x + self.scroll
        kol = int(wereld_x // CEL)
        rij = int(y // CEL)
        if self.gekozen == "gum":
            self.grid.pop((kol, rij), None)
        else:
            if self.gekozen == "vlag":
                # Er mag maar één finishvlag zijn
                for cel in [c for c, s in self.grid.items() if s == "vlag"]:
                    del self.grid[cel]
            self.grid[(kol, rij)] = self.gekozen

    def _klik_balk(self, x, y):
        for soort, (l, r) in self.palet_knoppen.items():
            if l <= x <= r:
                self.gekozen = soort
                return
        for naam, (l, r) in self.actie_knoppen.items():
            if l <= x <= r:
                if naam == "spelen":
                    self._speel()
                elif naam == "opslaan":
                    self._opslaan()
                elif naam == "wissen":
                    self.grid = {}
                elif naam == "kaart":
                    self._naar_kaart()
                elif naam == "type":
                    # Klik door de types heen: gewoon -> race -> vlucht -> gewoon
                    volgende = {"gewoon": "race", "race": "vlucht", "vlucht": "gewoon"}
                    self.mode = volgende[self.mode]
                return

    # ---------- Toetsen ----------
    def on_key_press(self, toets, modifiers):
        if toets == arcade.key.LEFT:
            self._scroll_richting = -1
        elif toets == arcade.key.RIGHT:
            self._scroll_richting = 1
        elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
            self._speel()
        elif toets == arcade.key.S:
            self._opslaan()
        elif toets == arcade.key.K or toets == arcade.key.ESCAPE:
            self._naar_kaart()

    def on_key_release(self, toets, modifiers):
        if toets in (arcade.key.LEFT, arcade.key.RIGHT):
            self._scroll_richting = 0

    def on_update(self, dt):
        if self._scroll_richting != 0:
            self.scroll = max(0, self.scroll + self._scroll_richting * 9)
        if self._melding_teller > 0:
            self._melding_teller -= 1

    # ---------- Je level bouwen en spelen ----------
    def _bouw_level(self):
        """Zet het raster om in echte level-gegevens voor het spel."""
        from platforms import Platform, BlokPlatform
        from vijand import Vijand, Spikes
        from powerup import ExtraLevenPowerUp

        platforms = [Platform(0, 0, 100, 40)]   # altijd een klein startstukje grond
        vijanden = []
        powerups = []
        vlag_x, vlag_y = None, None
        max_x = 300

        for (kol, rij), soort in self.grid.items():
            wx, wy = kol * CEL, rij * CEL
            max_x = max(max_x, wx + CEL)
            if soort == "grond":
                platforms.append(Platform(wx, wy, CEL, CEL))
            elif soort == "blok":
                platforms.append(BlokPlatform(wx, wy, CEL, CEL))
            elif soort == "spike":
                vijanden.append(Spikes(wx + 4, wy, 2))
            elif soort == "vijand":
                vijanden.append(Vijand(wx, wy, wx - 80, wx + CEL + 80, 2))
            elif soort == "hart":
                powerups.append(ExtraLevenPowerUp(wx + 6, wy + 6))
            elif soort == "vlag":
                vlag_x, vlag_y = wx, wy

        if vlag_x is None:                       # geen vlag geplaatst? zet er een aan het eind
            vlag_x, vlag_y = max_x + 60, 40
            max_x += 200
        level_breedte = max_x + 200
        return platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte

    def _speel(self):
        """Sla het level op en speel het."""
        self._opslaan()
        from spel import PlatformerSpel
        data = self._bouw_level()
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None,
                              eigen_level=data, race=(self.mode == "race"),
                              vlucht=(self.mode == "vlucht"),
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _naar_kaart(self):
        from levelkaart import LevelKaartView
        kaart = LevelKaartView(self.voltooid, self.punten, self.levens,
                               self.arena_record, self.race_record, self.vlucht_record)
        self.window.show_view(kaart)

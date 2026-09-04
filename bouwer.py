# bouwer.py
# De BOUWMODUS: maak je eigen level!
# Je plaatst met de muis grond, blokken, spikes, vijanden, hartjes en een
# finishvlag op een raster. Daarna kun je je eigen level spelen.

import arcade
import json
import os
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE
from decoratie import teken_deco, DECO_SOORTEN, DECO_NAAM
from vijand import SPIKE_SOORTEN, SPIKE_NAAM, SPIKE_INFO
from platforms import BLOK_SOORTEN, BLOK_NAAM

CEL = 40                       # grootte van één raster-vakje
BESTAND = "eigen_level.json"   # hier wordt je level opgeslagen

# De dingen die je kunt plaatsen (op volgorde in het palet)
ITEMS = ["grond", "blok", "spike", "vijand", "hart", "vlag", "portaal", "snel",
         "deco", "spring", "gum"]
ITEM_NAAM = {
    "grond": "Grond", "blok": "Blok", "spike": "Spike", "vijand": "Vijand",
    "hart": "Hartje", "vlag": "Finish", "portaal": "Portaal", "snel": "Snel",
    "deco": "Deco", "spring": "Spring", "gum": "Gum",
}

# De spring-dingen waar je met de Spring-knop doorheen klikt:
# bol1..bol5 en mat1..mat5 (kracht 1 t/m 5), en "neer" (paarse bol waarmee je valt)
SPRING_SOORTEN = ["bol1", "bol2", "bol3", "bol4", "bol5",
                  "mat1", "mat2", "mat3", "mat4", "mat5", "neer", "draai"]
SPRING_NAAM = {"neer": "Neer", "draai": "Draai"}
for _n in range(1, 6):
    SPRING_NAAM["bol%d" % _n] = "Bol%d" % _n
    SPRING_NAAM["mat%d" % _n] = "Mat%d" % _n

# De vorm-portalen waar je met de Portaal-knop doorheen klikt
PORTAAL_SOORTEN = ["vlucht", "blok", "ufo", "bal", "golf", "robot", "spin", "heli", "dubbel", "enkel"]
PORTAAL_NAAM = {"vlucht": "Vlieg", "blok": "Blok", "ufo": "UFO", "bal": "Bal",
                "golf": "Golf", "robot": "Robot", "spin": "Spin", "heli": "Heli",
                "dubbel": "Dubbel", "enkel": "Enkel"}

# De snelheid-portalen waar je met de Snel-knop doorheen klikt
SNELHEID_SOORTEN = ["x0.5", "x1", "x2", "x5", "x10"]

# Waar de bovenbalk (met knoppen) begint (net onder de bovenrand)
BALK_Y = SCHERM_HOOGTE - 58


def teken_item(soort, x, y, grootte, rotatie=0):
    """Teken een klein plaatje van een item in een vakje op scherm (x, y).

    rotatie (0/90/180/270) draait spikes en decoratie rond het midden van het vakje.
    """
    g = grootte
    mx, my = x + g / 2, y + g / 2

    def d(px, py):
        dx, dy = px - mx, py - my
        r = rotatie % 360
        if r == 90:
            return (mx - dy, my + dx)
        if r == 180:
            return (mx - dx, my - dy)
        if r == 270:
            return (mx + dy, my - dx)
        return (px, py)

    if soort == "grond":
        arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (60, 160, 60))
        arcade.draw_lrbt_rectangle_filled(x, x + g, y + g - 5, y + g, (90, 200, 90))
    elif soort == "blok" or soort.startswith("blok_"):
        s = soort.split("_", 1)[1] if "_" in soort else "gewoon"
        if s == "schuinop":
            arcade.draw_triangle_filled(x, y, x + g, y, x + g, y + g, (150, 110, 80))
            arcade.draw_triangle_outline(x, y, x + g, y, x + g, y + g, (90, 60, 40), 2)
        elif s == "schuinaf":
            arcade.draw_triangle_filled(x, y, x + g, y, x, y + g, (150, 110, 80))
            arcade.draw_triangle_outline(x, y, x + g, y, x, y + g, (90, 60, 40), 2)
        elif s == "half":
            arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g // 2, (150, 110, 80))
            arcade.draw_lrbt_rectangle_outline(x, x + g, y, y + g // 2, (90, 60, 40), 2)
        elif s == "stuiter":
            arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (60, 180, 90))
            arcade.draw_lrbt_rectangle_outline(x, x + g, y, y + g, (30, 120, 50), 2)
            cx = x + g // 2
            arcade.draw_triangle_filled(cx - 7, y + g * 0.45, cx + 7, y + g * 0.45,
                                        cx, y + g * 0.8, (230, 255, 230))
        elif s == "verdwijn":
            arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (200, 160, 90))
            arcade.draw_lrbt_rectangle_outline(x, x + g, y, y + g, (120, 80, 40), 2)
            arcade.draw_line(x + g * 0.35, y + g, x + g * 0.45, y, (120, 80, 40), 1)
            arcade.draw_line(x + g * 0.65, y + g, x + g * 0.55, y, (120, 80, 40), 1)
        else:  # gewoon
            arcade.draw_lrbt_rectangle_filled(x, x + g, y, y + g, (150, 110, 80))
            arcade.draw_lrbt_rectangle_outline(x, x + g, y, y + g, (90, 60, 40), 2)
    elif soort == "spike" or soort.startswith("spike_"):
        s = soort.split("_", 1)[1] if "_" in soort else "gewoon"
        aantal, kleur = SPIKE_INFO.get(s, SPIKE_INFO["gewoon"])
        n = min(aantal, 3)
        bw = (g - 6) / n
        for i in range(n):
            bx = x + 3 + i * bw
            p1, p2, p3 = d(bx, y + 3), d(bx + bw - 1, y + 3), d(bx + bw / 2, y + g - 5)
            arcade.draw_triangle_filled(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], kleur)
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
    elif soort.startswith("portaal"):
        # "portaal_vlucht", "portaal_bal", enz. -> teken een gekleurde ring + icoon
        from portaal import PORTAAL_KLEUREN, teken_portaal_icoon
        p_soort = soort.split("_", 1)[1] if "_" in soort else "vlucht"
        buiten = PORTAAL_KLEUREN.get(p_soort, PORTAAL_KLEUREN["blok"])[0]
        cx, cy = x + g // 2, y + g // 2
        arcade.draw_ellipse_outline(cx, cy, g - 10, g - 4, buiten, 3)
        teken_portaal_icoon(p_soort, cx, cy)
    elif soort.startswith("deco_"):
        # "deco_bloem", "deco_boom", enz. -> teken de decoratie
        teken_deco(soort.split("_", 1)[1], x, y, g, rotatie)
    elif soort.startswith("spring_"):
        # "spring_bol3", "spring_mat5", "spring_neer"
        from springers import KRACHT_PER_STAND, NEER_KRACHT, spring_kleur
        s = soort.split("_", 1)[1]
        cx, cy = x + g // 2, y + g // 2
        if s == "draai":
            # Draai-bol: blauwe ring met twee pijltjes (omhoog + omlaag)
            arcade.draw_circle_outline(cx, cy, g * 0.30, (70, 150, 255), 3)
            arcade.draw_triangle_filled(cx - 7, cy + 1, cx - 3, cy + 1, cx - 5, cy + 6, (70, 150, 255))
            arcade.draw_triangle_filled(cx + 3, cy - 1, cx + 7, cy - 1, cx + 5, cy - 6, (70, 150, 255))
        elif s == "neer":
            kleur = spring_kleur(NEER_KRACHT)
            arcade.draw_circle_outline(cx, cy, g * 0.30, kleur, 3)
            arcade.draw_triangle_filled(cx - 5, cy + 3, cx + 5, cy + 3, cx, cy - 5, kleur)
        elif s.startswith("mat"):
            niveau = int(s[3:]) if s[3:].isdigit() else 3   # oud "mat" -> kracht 3
            kleur = spring_kleur(KRACHT_PER_STAND[niveau])
            arcade.draw_lrbt_rectangle_filled(cx - g * 0.4, cx + g * 0.4, y + 6, y + 13, kleur)
            arcade.draw_triangle_filled(cx - 5, y + 13, cx + 5, y + 13, cx, y + 21, kleur)
            arcade.draw_text(str(niveau), cx, y - 1, arcade.color.BLACK, 8, bold=True, anchor_x="center")
        else:  # bolN (of oud "bol")
            niveau = int(s[3:]) if s[3:].isdigit() else 3   # oud "bol" -> kracht 3
            kleur = spring_kleur(KRACHT_PER_STAND[niveau])
            arcade.draw_circle_outline(cx, cy, g * 0.30, kleur, 3)
            arcade.draw_triangle_filled(cx - 5, cy - 3, cx + 5, cy - 3, cx, cy + 5, kleur)
            arcade.draw_text(str(niveau), cx, y - 1, arcade.color.BLACK, 8, bold=True, anchor_x="center")
    elif soort == "gum":
        arcade.draw_lrbt_rectangle_filled(x + 5, x + g - 5, y + 8, y + g - 8, (255, 180, 200))
        arcade.draw_lrbt_rectangle_outline(x + 5, x + g - 5, y + 8, y + g - 8, (200, 100, 130), 2)


class BouwerView(arcade.View):
    """Het bouwscherm — maak hier je eigen level."""

    # Knoppen in de bovenbalk: naam -> (links, rechts)
    def __init__(self, voltooid_levels, punten=0, levens=None,
                 arena_record=0, race_record=0, vlucht_record=0, aantal_spelers=1):
        super().__init__()
        self.voltooid = voltooid_levels
        self.punten = punten
        self.levens = levens
        self.arena_record = arena_record
        self.race_record = race_record
        self.vlucht_record = vlucht_record
        self.aantal_spelers = aantal_spelers   # met hoeveel spelers je je level speelt (1-4)

        self.grid = {}                 # (kol, rij) -> soort
        self.rotaties = {}             # (kol, rij) -> draai-hoek (0/90/180/270)
        self.deco = {}                 # decoratie zit in een APARTE laag (kan bovenop een blok)
        self.deco_rotaties = {}        # (kol, rij) -> draai-hoek van de decoratie
        self.rotatie = 0               # de draai-stand waarmee je nu plaatst
        self.gekozen = "grond"         # welk item je nu plaatst
        self.portaal_soort = "vlucht"  # welk vorm-portaal je plaatst (klik op Portaal)
        self.snel_soort = "x2"         # welk snelheid-portaal je plaatst (klik op Snel)
        self.deco_soort = "bloem"      # welke decoratie je plaatst (klik op Deco)
        self.spring_soort = "bol3"     # welk spring-ding je plaatst (klik op Spring)
        self.spike_soort = "gewoon"    # welke spike je plaatst (klik op Spike)
        self.blok_soort = "gewoon"     # welk blok je plaatst (klik op Blok)
        # Type van je level: "gewoon" (lopen), "race" (auto-run), "vlucht" (vliegen)
        self.mode = "gewoon"
        self.scroll = 0                # hoe ver je naar rechts hebt geschoven
        self._scroll_richting = 0      # -1 links, +1 rechts (met pijltjestoetsen)
        self._melding = ""             # kort berichtje (bv. "Opgeslagen!")
        self._melding_teller = 0

        # Palet-knoppen (links) en actie-knoppen (rechts) uitrekenen
        self.palet_knoppen = {}        # soort -> (l, r)
        for i, soort in enumerate(ITEMS):
            l = 6 + i * 36
            self.palet_knoppen[soort] = (l, l + 34)
        self.actie_knoppen = {         # naam -> (l, r)
            "spelen": (410, 460),
            "opslaan": (464, 524),
            "wissen": (528, 582),
            "kaart": (586, 628),
            "draai": (632, 688),
            "type": (692, 792),
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
                    for kr in data.get("rotaties", []):
                        self.rotaties[(int(kr[0]), int(kr[1]))] = int(kr[2])
                    # De aparte decoratie-laag inlezen (nieuw formaat)
                    for kr in data.get("deco", []):
                        self.deco[(int(kr[0]), int(kr[1]))] = kr[2]
                    for kr in data.get("deco_rotaties", []):
                        self.deco_rotaties[(int(kr[0]), int(kr[1]))] = int(kr[2])
                else:
                    tiles = data   # oud formaat (alleen een lijst met vakjes)
                self.grid = {(int(k), int(r)): s for k, r, s in tiles}
                # Oude levels: decoratie zat in het gewone raster -> verhuis naar de deco-laag
                for cel in [c for c, s in self.grid.items() if s.startswith("deco_")]:
                    self.deco[cel] = self.grid.pop(cel)
                    if cel in self.rotaties:
                        self.deco_rotaties[cel] = self.rotaties.pop(cel)
                return
            except Exception:
                pass
        # Start-level: een stukje grond en een finishvlag als voorbeeld
        for kol in range(0, 10):
            self.grid[(kol, 0)] = "grond"
        self.grid[(12, 1)] = "vlag"

    def _opslaan(self):
        data = {"tiles": [[k, r, s] for (k, r), s in self.grid.items()],
                "mode": self.mode,
                "rotaties": [[k, r, rot] for (k, r), rot in self.rotaties.items()],
                "deco": [[k, r, s] for (k, r), s in self.deco.items()],
                "deco_rotaties": [[k, r, rot] for (k, r), rot in self.deco_rotaties.items()]}
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self._melding = "💾 Opgeslagen!"
        self._melding_teller = 120

    # ---------- Tekenen ----------
    def on_show_view(self):
        # De bouwmodus is altijd op de gewone (kleine) maat
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
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
            teken_item(soort, sx, rij * CEL, CEL, self.rotaties.get((kol, rij), 0))
        # Decoratie ligt in een aparte laag, dus die tekenen we BOVENOP de blokken
        for (kol, rij), soort in self.deco.items():
            sx = kol * CEL - self.scroll
            if sx < -CEL or sx > SCHERM_BREEDTE:
                continue
            teken_item(soort, sx, rij * CEL, CEL, self.deco_rotaties.get((kol, rij), 0))

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
            # De Portaal-, Snel- en Deco-knop tonen welk soort je nu plaatst
            if soort == "portaal":
                teken_item("portaal_" + self.portaal_soort, l + 2, BALK_Y + 10, 34)
                naam = "P:" + PORTAAL_NAAM[self.portaal_soort]
            elif soort == "snel":
                teken_item("portaal_" + self.snel_soort, l + 2, BALK_Y + 10, 34)
                naam = self.snel_soort
            elif soort == "deco":
                teken_item("deco_" + self.deco_soort, l + 2, BALK_Y + 10, 34, self.rotatie)
                naam = DECO_NAAM[self.deco_soort]
            elif soort == "spring":
                teken_item("spring_" + self.spring_soort, l + 2, BALK_Y + 10, 34)
                naam = SPRING_NAAM[self.spring_soort]
            elif soort == "spike":
                teken_item("spike_" + self.spike_soort, l + 2, BALK_Y + 10, 34, self.rotatie)
                naam = SPIKE_NAAM[self.spike_soort]
            elif soort == "blok":
                teken_item("blok_" + self.blok_soort, l + 2, BALK_Y + 10, 34)
                naam = BLOK_NAAM[self.blok_soort]
            else:
                teken_item(soort, l + 2, BALK_Y + 10, 34)
                naam = ITEM_NAAM[soort]
            arcade.draw_text(naam, (l + r) // 2, BALK_Y + 1,
                             arcade.color.WHITE, 8, anchor_x="center")

        # Kleur en tekst van de Type-knop hangen af van het gekozen type
        type_kleur = {"gewoon": (150, 100, 30), "race": (40, 110, 180),
                      "vlucht": (120, 60, 170)}[self.mode]
        type_tekst = {"gewoon": "🚶 Gewoon", "race": "🏁 Race",
                      "vlucht": "✈️ Vliegen"}[self.mode]
        # Actie-knoppen
        kleuren = {"spelen": (40, 160, 60), "opslaan": (40, 110, 180),
                   "wissen": (170, 60, 60), "kaart": (100, 100, 120),
                   "draai": (150, 110, 40), "type": type_kleur}
        teksten = {"spelen": ("▶ %dP Spelen" % self.aantal_spelers) if self.aantal_spelers > 1 else "▶ Spelen",
                   "opslaan": "💾 Opslaan", "wissen": "🗑 Wissen", "kaart": "🗺 Kaart",
                   "draai": "↻ %d°" % self.rotatie, "type": type_tekst}
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
            arcade.draw_text("Klik om te plaatsen  •  ←→ = schuiven  •  Draai-knop of D = draaien"
                             "  •  Klik nog eens op Portaal/Snel/Deco voor een ander soort",
                             SCHERM_BREEDTE // 2, 8, arcade.color.WHITE, 10, anchor_x="center")

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
            # Gum wist eerst de decoratie (die ligt bovenop), anders het gewone item
            if (kol, rij) in self.deco:
                self.deco.pop((kol, rij), None)
                self.deco_rotaties.pop((kol, rij), None)
            else:
                self.grid.pop((kol, rij), None)
                self.rotaties.pop((kol, rij), None)
        elif self.gekozen == "deco":
            # Decoratie in de aparte laag -> die kan dus BOVENOP een blok liggen
            self.deco[(kol, rij)] = "deco_" + self.deco_soort
            if self.rotatie:
                self.deco_rotaties[(kol, rij)] = self.rotatie
            else:
                self.deco_rotaties.pop((kol, rij), None)
        else:
            if self.gekozen == "vlag":
                # Er mag maar één finishvlag zijn
                for cel in [c for c, s in self.grid.items() if s == "vlag"]:
                    del self.grid[cel]
            # Bij een portaal onthouden we ook welk soort (vorm of snelheid)
            if self.gekozen == "portaal":
                self.grid[(kol, rij)] = "portaal_" + self.portaal_soort
            elif self.gekozen == "snel":
                self.grid[(kol, rij)] = "portaal_" + self.snel_soort
            elif self.gekozen == "spring":
                self.grid[(kol, rij)] = "spring_" + self.spring_soort
            elif self.gekozen == "spike":
                self.grid[(kol, rij)] = "spike_" + self.spike_soort
            elif self.gekozen == "blok":
                self.grid[(kol, rij)] = "blok_" + self.blok_soort
            else:
                self.grid[(kol, rij)] = self.gekozen
            # Onthoud de draai-stand voor dit vakje (0 = niet onthouden)
            if self.rotatie:
                self.rotaties[(kol, rij)] = self.rotatie
            else:
                self.rotaties.pop((kol, rij), None)

    def _klik_balk(self, x, y):
        for soort, (l, r) in self.palet_knoppen.items():
            if l <= x <= r:
                if soort == "portaal" and self.gekozen == "portaal":
                    # Nog een keer op Portaal klikken: door de vorm-soorten wisselen
                    i = PORTAAL_SOORTEN.index(self.portaal_soort)
                    self.portaal_soort = PORTAAL_SOORTEN[(i + 1) % len(PORTAAL_SOORTEN)]
                elif soort == "snel" and self.gekozen == "snel":
                    # Nog een keer op Snel klikken: door de snelheden wisselen
                    i = SNELHEID_SOORTEN.index(self.snel_soort)
                    self.snel_soort = SNELHEID_SOORTEN[(i + 1) % len(SNELHEID_SOORTEN)]
                elif soort == "deco" and self.gekozen == "deco":
                    # Nog een keer op Deco klikken: door de decoratie-soorten wisselen
                    i = DECO_SOORTEN.index(self.deco_soort)
                    self.deco_soort = DECO_SOORTEN[(i + 1) % len(DECO_SOORTEN)]
                elif soort == "spring" and self.gekozen == "spring":
                    # Nog een keer op Spring klikken: wissel tussen bol en mat
                    i = SPRING_SOORTEN.index(self.spring_soort)
                    self.spring_soort = SPRING_SOORTEN[(i + 1) % len(SPRING_SOORTEN)]
                elif soort == "spike" and self.gekozen == "spike":
                    # Nog een keer op Spike klikken: door de 5 spike-soorten wisselen
                    i = SPIKE_SOORTEN.index(self.spike_soort)
                    self.spike_soort = SPIKE_SOORTEN[(i + 1) % len(SPIKE_SOORTEN)]
                elif soort == "blok" and self.gekozen == "blok":
                    # Nog een keer op Blok klikken: door de blok-soorten wisselen
                    i = BLOK_SOORTEN.index(self.blok_soort)
                    self.blok_soort = BLOK_SOORTEN[(i + 1) % len(BLOK_SOORTEN)]
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
                    self.rotaties = {}
                    self.deco = {}
                    self.deco_rotaties = {}
                elif naam == "kaart":
                    self._naar_kaart()
                elif naam == "draai":
                    # Draai de plaats-stand een kwartslag verder (0 -> 90 -> 180 -> 270 -> 0)
                    self.rotatie = (self.rotatie + 90) % 360
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
        elif toets == arcade.key.D:
            # D = draaien (kwartslag verder)
            self.rotatie = (self.rotatie + 90) % 360
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
        from platforms import Platform, BlokPlatform, SchuinBlok, StuiterBlok, VerdwijnBlok
        from vijand import Vijand, Spikes, maak_spike
        from powerup import ExtraLevenPowerUp
        from portaal import Portaal
        from decoratie import Decoratie
        from springers import SpringBol, SpringMat, KRACHT_PER_STAND, NEER_KRACHT

        platforms = [Platform(0, 0, 100, 40)]   # altijd een klein startstukje grond
        vijanden = []
        powerups = []
        portalen = []
        decoraties = []
        springers = []
        vlag_x, vlag_y = None, None
        max_x = 300

        for (kol, rij), soort in self.grid.items():
            wx, wy = kol * CEL, rij * CEL
            rot = self.rotaties.get((kol, rij), 0)
            max_x = max(max_x, wx + CEL)
            if soort == "grond":
                platforms.append(Platform(wx, wy, CEL, CEL))
            elif soort == "blok" or soort.startswith("blok_"):
                s = soort.split("_", 1)[1] if "_" in soort else "gewoon"
                if s == "schuinop":
                    platforms.append(SchuinBlok(wx, wy, CEL, CEL, "op"))
                elif s == "schuinaf":
                    platforms.append(SchuinBlok(wx, wy, CEL, CEL, "af"))
                elif s == "half":
                    platforms.append(BlokPlatform(wx, wy, CEL, CEL // 2))
                elif s == "stuiter":
                    platforms.append(StuiterBlok(wx, wy, CEL, CEL))
                elif s == "verdwijn":
                    platforms.append(VerdwijnBlok(wx, wy, CEL, CEL))
                else:
                    platforms.append(BlokPlatform(wx, wy, CEL, CEL))
            elif soort == "spike" or soort.startswith("spike_"):
                s = soort.split("_", 1)[1] if "_" in soort else "gewoon"
                vijanden.append(maak_spike(s, wx + 4, wy, rot))   # 5 soorten, met draaiing
            elif soort == "vijand":
                vijanden.append(Vijand(wx, wy, wx - 80, wx + CEL + 80, 2))
            elif soort == "hart":
                powerups.append(ExtraLevenPowerUp(wx + 6, wy + 6))
            elif soort.startswith("portaal_"):
                # "portaal_vlucht" -> Portaal met soort "vlucht", enz.
                portalen.append(Portaal(wx + 5, wy, soort.split("_", 1)[1]))
            elif soort.startswith("deco_"):
                # "deco_bloem" -> Decoratie met soort "bloem", enz. (geen botsing)
                decoraties.append(Decoratie(wx, wy, soort.split("_", 1)[1], rot))
            elif soort == "spring_draai":
                springers.append(SpringBol(wx + 3, wy + 3, draai=True))    # blauwe draai-bol
            elif soort == "spring_neer":
                springers.append(SpringBol(wx + 3, wy + 3, NEER_KRACHT))   # paarse neer-bol
            elif soort.startswith("spring_bol"):
                n = soort[10:]
                springers.append(SpringBol(wx + 3, wy + 3,
                                           KRACHT_PER_STAND[int(n) if n.isdigit() else 3]))
            elif soort.startswith("spring_mat"):
                n = soort[10:]
                springers.append(SpringMat(wx, wy,
                                           KRACHT_PER_STAND[int(n) if n.isdigit() else 3]))
            elif soort == "vlag":
                vlag_x, vlag_y = wx, wy

        # Decoratie uit de aparte laag (ligt bovenop blokken, geen botsing)
        for (kol, rij), soort in self.deco.items():
            wx, wy = kol * CEL, rij * CEL
            rot = self.deco_rotaties.get((kol, rij), 0)
            max_x = max(max_x, wx + CEL)
            decoraties.append(Decoratie(wx, wy, soort.split("_", 1)[1], rot))

        if vlag_x is None:                       # geen vlag geplaatst? zet er een aan het eind
            vlag_x, vlag_y = max_x + 60, 40
            max_x += 200
        level_breedte = max_x + 200
        return (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte,
                portalen, decoraties, springers)

    def _speel(self):
        """Sla het level op en speel het."""
        self._opslaan()
        from spel import PlatformerSpel
        data = self._bouw_level()
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None,
                              eigen_level=data, race=(self.mode == "race"),
                              vlucht=(self.mode == "vlucht"), aantal_spelers=self.aantal_spelers,
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _naar_kaart(self):
        from levelkaart import LevelKaartView
        kaart = LevelKaartView(self.voltooid, self.punten, self.levens,
                               self.arena_record, self.race_record, self.vlucht_record)
        self.window.show_view(kaart)

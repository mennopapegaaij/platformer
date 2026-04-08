# levelkaart.py
# De overzichtskaart — net als bij Mario!
# Hier kun je kiezen welk level je wilt spelen.
# Levels die je nog niet gehaald hebt zijn op slot.

import arcade
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE, AANTAL_LEVELS, LEVEL_NAMEN

# Posities van de level-bolletjes op de kaart (x, y)
# Het pad slingert als een slang: rechts → omhoog → links → omhoog → rechts
LEVEL_POSITIES = {
    1: (150,  80),   # Rij 1 (onderaan), van links naar rechts
    2: (370,  80),
    3: (590,  80),
    4: (590, 220),   # Rij 2 (midden), van rechts naar links
    5: (370, 220),
    6: (150, 220),
    7: (150, 360),   # Rij 3 (bovenaan), van links naar rechts
    8: (370, 360),
    9: (590, 360),
}

# De verbindingen tussen de levels op het pad
PADEN = [
    (1, 2), (2, 3),         # Onderste rij: naar rechts
    (3, 4),                  # Omhoog
    (4, 5), (5, 6),         # Middelste rij: naar links
    (6, 7),                  # Omhoog
    (7, 8), (8, 9),         # Bovenste rij: naar rechts
]


class LevelKaartView(arcade.View):
    """De levelkaart — hier kies je welk level je wilt spelen."""

    def __init__(self, voltooid_levels):
        super().__init__()
        self.voltooid = voltooid_levels  # Set met voltooide level-nummers

        # Begin bij het eerste level dat nog niet gehaald is
        self.geselecteerd = self._bereken_start()

    def _bereken_start(self):
        """Zoek het eerste level dat nog niet gehaald is."""
        for i in range(1, AANTAL_LEVELS + 1):
            if i not in self.voltooid:
                return i
        return AANTAL_LEVELS  # Alles gehaald!

    def _is_ontgrendeld(self, nummer):
        """Controleer of een level gespeeld mag worden (het vorige moet gehaald zijn)."""
        return nummer == 1 or (nummer - 1) in self.voltooid

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        arcade.set_background_color((60, 160, 60))  # Groen gras

    def on_draw(self):
        """Teken de kaart."""
        self.clear()

        # --- Achtergrond decoraties ---
        self._teken_achtergrond()

        # --- Teken de paden (verbindingen tussen levels) ---
        for (van, naar) in PADEN:
            x1, y1 = LEVEL_POSITIES[van]
            x2, y2 = LEVEL_POSITIES[naar]
            # Vergrendeld pad = grijs, beschikbaar pad = bruin/zand
            if self._is_ontgrendeld(naar):
                arcade.draw_line(x1, y1, x2, y2, (180, 120, 60), 10)
                arcade.draw_line(x1, y1, x2, y2, (220, 180, 100), 5)
            else:
                arcade.draw_line(x1, y1, x2, y2, (80, 80, 80), 10)

        # --- Teken de level-bolletjes ---
        for nummer in range(1, AANTAL_LEVELS + 1):
            x, y = LEVEL_POSITIES[nummer]
            self._teken_level_knoop(nummer, x, y)

        # --- Teken het poppetje op het geselecteerde level ---
        px, py = LEVEL_POSITIES[self.geselecteerd]
        self._teken_poppetje(px, py + 38)

        # --- Titel bovenaan ---
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, SCHERM_HOOGTE - 60,
                                          SCHERM_HOOGTE, (0, 0, 0, 160))
        arcade.draw_text("🗺️  Levelkaart",
                         SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 38,
                         arcade.color.WHITE, 26, bold=True, anchor_x="center")

        # --- Uitleg onderaan ---
        naam = LEVEL_NAMEN.get(self.geselecteerd, "")
        if not self._is_ontgrendeld(self.geselecteerd):
            extra = f"  🔒  Haal level {self.geselecteerd - 1} eerst!"
            tekst_kleur = arcade.color.LIGHT_GRAY
        elif self.geselecteerd in self.voltooid:
            extra = "  ⭐  Al gehaald!"
            tekst_kleur = arcade.color.GOLD
        else:
            extra = "  ←→ bewegen  •  ENTER om te starten"
            tekst_kleur = arcade.color.WHITE

        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, 0, 50, (0, 0, 0, 160))
        arcade.draw_text(f"Level {self.geselecteerd}: {naam}{extra}",
                         SCHERM_BREEDTE // 2, 16,
                         tekst_kleur, 15, bold=True, anchor_x="center")

    def _teken_level_knoop(self, nummer, x, y):
        """Teken één level-bolletje op de kaart."""
        ontgrendeld = self._is_ontgrendeld(nummer)
        voltooid = nummer in self.voltooid
        geselecteerd = nummer == self.geselecteerd

        # Kies de kleur van het bolletje
        if not ontgrendeld:
            kleur_binnen = (90, 90, 90)
            kleur_rand = (130, 130, 130)
        elif voltooid:
            kleur_binnen = (220, 180, 20)   # Goud = gehaald
            kleur_rand = (255, 220, 60)
        else:
            kleur_binnen = (40, 100, 200)   # Blauw = beschikbaar
            kleur_rand = (80, 160, 255)

        # Geselecteerd bolletje is groter
        straal = 30 if geselecteerd else 24

        # Teken het bolletje
        arcade.draw_circle_filled(x, y, straal, kleur_rand)
        arcade.draw_circle_filled(x, y, straal - 4, kleur_binnen)
        if geselecteerd:
            # Extra witte rand voor het geselecteerde level
            arcade.draw_circle_outline(x, y, straal + 4, arcade.color.WHITE, 3)

        # Levelnummer in het bolletje
        tekst_kleur = arcade.color.WHITE if not ontgrendeld else arcade.color.BLACK
        arcade.draw_text(str(nummer), x, y - 8, tekst_kleur, 14,
                         bold=True, anchor_x="center")

        # Sterretje bovenop als het level gehaald is
        if voltooid:
            arcade.draw_text("⭐", x - 8, y + straal - 4, arcade.color.YELLOW, 14)

        # Slotje als het level vergrendeld is
        if not ontgrendeld:
            arcade.draw_text("🔒", x - 8, y + straal - 4, arcade.color.LIGHT_GRAY, 12)

    def _teken_poppetje(self, x, y):
        """Teken een klein geel poppetje (de speler op de kaart)."""
        # Lichaam
        arcade.draw_rectangle_filled(x, y, 18, 18, arcade.color.YELLOW)
        # Hoofd
        arcade.draw_circle_filled(x, y + 14, 10, arcade.color.YELLOW)
        # Ogen
        arcade.draw_circle_filled(x - 3, y + 16, 2, arcade.color.BLACK)
        arcade.draw_circle_filled(x + 3, y + 16, 2, arcade.color.BLACK)

    def _teken_achtergrond(self):
        """Teken wat decoraties op de achtergrond van de kaart."""
        # Wolkjes
        for cx, cy in [(100, 440), (320, 460), (550, 450), (720, 435)]:
            arcade.draw_ellipse_filled(cx, cy, 80, 30, arcade.color.WHITE)
            arcade.draw_ellipse_filled(cx - 20, cy + 10, 50, 25, arcade.color.WHITE)
            arcade.draw_ellipse_filled(cx + 20, cy + 10, 50, 25, arcade.color.WHITE)

        # Boompjes
        for tx, ty in [(50, 150), (700, 150), (50, 290), (700, 290), (730, 120), (60, 390)]:
            # Stam (lrbt = left, right, bottom, top)
            arcade.draw_lrbt_rectangle_filled(tx - 5, tx + 5, ty - 25, ty - 5, (100, 60, 20))
            # Bladeren (driehoek)
            arcade.draw_triangle_filled(tx - 18, ty - 5, tx + 18, ty - 5,
                                        tx, ty + 28, (30, 120, 30))
            arcade.draw_triangle_filled(tx - 14, ty + 10, tx + 14, ty + 10,
                                        tx, ty + 38, (50, 160, 50))

    def on_key_press(self, toets, modifiers):
        """Navigeer op de kaart met de pijltjestoetsen, start met ENTER."""
        if toets == arcade.key.LEFT:
            # Ga naar het vorige level (als dat bestaat)
            if self.geselecteerd > 1:
                self.geselecteerd -= 1
        elif toets == arcade.key.RIGHT:
            # Ga naar het volgende level (als dat ontgrendeld is)
            if self.geselecteerd < AANTAL_LEVELS and self._is_ontgrendeld(self.geselecteerd + 1):
                self.geselecteerd += 1
        elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
            # Start het level als het ontgrendeld is
            if self._is_ontgrendeld(self.geselecteerd):
                self._start_level(self.geselecteerd)

    def _start_level(self, nummer):
        """Start het gekozen level."""
        from spel import PlatformerSpel
        spel = PlatformerSpel(nummer, self.voltooid)
        self.window.show_view(spel)

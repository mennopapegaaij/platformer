# levelkaart.py
# De overzichtskaart — net als bij Mario!
# Hier kun je kiezen welk level je wilt spelen.
# Levels die je nog niet gehaald hebt zijn op slot.
# De kaart is ONEINDIG: er komen steeds nieuwe bolletjes bij (10, 11, 12...).

import arcade
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE, AANTAL_LEVELS, LEVEL_NAMEN

# De drie kolommen (x-posities) waar de bolletjes op staan (meegeschaald met de breedte)
KOL_X = [int(SCHERM_BREEDTE * 0.19), int(SCHERM_BREEDTE * 0.46), int(SCHERM_BREEDTE * 0.73)]

# Elke rij is 140 pixels hoger dan de vorige
RIJ_HOOGTE = 140
# De onderste rij staat op deze hoogte
BASIS_Y = 80


def _rij_en_kolom(nummer):
    """Reken uit in welke rij en kolom een level hoort (level 1 = rij 0, kolom 0)."""
    rij = (nummer - 1) // 3
    kolom = (nummer - 1) % 3
    return rij, kolom


def _basis_positie(nummer):
    """De positie van een level op de kaart, nog zonder scrollen.

    De rijen slingeren als een slang: even rijen van links naar rechts,
    oneven rijen van rechts naar links.
    """
    rij, kolom = _rij_en_kolom(nummer)
    if rij % 2 == 0:
        x = KOL_X[kolom]          # even rij: links → rechts
    else:
        x = KOL_X[2 - kolom]      # oneven rij: rechts → links
    y = BASIS_Y + rij * RIJ_HOOGTE
    return x, y


class LevelKaartView(arcade.View):
    """De levelkaart — hier kies je welk level je wilt spelen."""

    # Knoppen aan de rechterkant: (links, rechts, onder, boven) — vijf stuks
    _KL = SCHERM_BREEDTE - 152           # linkerkant van de knoppen
    _KR = SCHERM_BREEDTE - 8             # rechterkant van de knoppen
    ARENA_KNOP = (_KL, _KR, 556, 660)   # vechtmodus (bovenste knop)
    VLUCHT_KNOP = (_KL, _KR, 442, 546)  # vliegtuig-modus
    RACE_KNOP = (_KL, _KR, 328, 432)    # racemodus
    TWEE_KNOP = (_KL, _KR, 214, 318)    # 2 spelers (split-screen)
    BOUWER_KNOP = (_KL, _KR, 100, 204)  # bouwmodus (onderste knop)

    def __init__(self, voltooid_levels, punten=0, levens=None, arena_record=0,
                 race_record=0, vlucht_record=0):
        super().__init__()
        self.voltooid = voltooid_levels  # Set met voltooide level-nummers
        self.punten = punten             # Punten uit het vorige level
        self.levens = levens             # Levens uit het vorige level (None = standaard)
        self.arena_record = arena_record # Hoogste vechtmodus-level dat je haalde
        self.race_record = race_record   # Hoogste race-baan die je haalde
        self.vlucht_record = vlucht_record  # Hoogste vliegtuig-baan die je haalde

        # Begin bij het eerste level dat nog niet gehaald is
        self.geselecteerd = self._bereken_start()

    def _bereken_start(self):
        """Zoek het eerste level dat nog niet gehaald is (kan ook level 10+ zijn!)."""
        i = 1
        while i in self.voltooid:
            i += 1
        return i

    def _hoogste_level(self):
        """Het hoogste level dat op de kaart getekend mag worden.

        Altijd minstens de 9 handgemaakte levels, en daarna steeds ééntje
        meer dan je hoogste gehaalde level (het volgende dat je kunt spelen).
        """
        behaald = max(self.voltooid) if self.voltooid else 0
        return max(AANTAL_LEVELS, behaald + 1)

    def _is_ontgrendeld(self, nummer):
        """Controleer of een level gespeeld mag worden (het vorige moet gehaald zijn)."""
        return nummer == 1 or (nummer - 1) in self.voltooid

    # --- Scrollen: de kaart schuift omhoog als je hoger komt ---
    def _scroll(self):
        """Hoeveel de kaart omhoog geschoven is.

        De geselecteerde rij blijft mooi in beeld. In het begin (rij 0 en 1)
        schuift er nog niets.
        """
        doel_rij = (self.geselecteerd - 1) // 3
        return max(0, (doel_rij - 1) * RIJ_HOOGTE)

    def _scherm_positie(self, nummer):
        """De positie van een level op het scherm (mét scrollen meegerekend)."""
        x, y = _basis_positie(nummer)
        return x, y - self._scroll()

    def _zichtbaar(self, nummer):
        """Staat dit bolletje op dit moment in beeld?"""
        _, y = self._scherm_positie(nummer)
        return 30 <= y <= SCHERM_HOOGTE - 85

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        arcade.set_background_color((60, 160, 60))  # Groen gras

    def on_draw(self):
        """Teken de kaart."""
        self.clear()

        # --- Achtergrond decoraties ---
        self._teken_achtergrond()

        hoogste = self._hoogste_level()

        # --- Teken de paden (verbindingen tussen levels) ---
        for van in range(1, hoogste):
            naar = van + 1
            # Alleen tekenen als tenminste één van de twee bolletjes in beeld is
            if not (self._zichtbaar(van) or self._zichtbaar(naar)):
                continue
            x1, y1 = self._scherm_positie(van)
            x2, y2 = self._scherm_positie(naar)
            # Vergrendeld pad = grijs, beschikbaar pad = bruin/zand
            if self._is_ontgrendeld(naar):
                arcade.draw_line(x1, y1, x2, y2, (180, 120, 60), 10)
                arcade.draw_line(x1, y1, x2, y2, (220, 180, 100), 5)
            else:
                arcade.draw_line(x1, y1, x2, y2, (80, 80, 80), 10)

        # --- Teken de level-bolletjes ---
        for nummer in range(1, hoogste + 1):
            if not self._zichtbaar(nummer):
                continue
            x, y = self._scherm_positie(nummer)
            self._teken_level_knoop(nummer, x, y)

        # --- Teken het poppetje op het geselecteerde level ---
        px, py = self._scherm_positie(self.geselecteerd)
        self._teken_poppetje(px, py + 38)

        # --- Titel bovenaan ---
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, SCHERM_HOOGTE - 60,
                                          SCHERM_HOOGTE, (0, 0, 0, 160))
        arcade.draw_text("🗺️  Levelkaart",
                         SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 38,
                         arcade.color.WHITE, 26, bold=True, anchor_x="center")

        # --- Uitleg onderaan ---
        naam = LEVEL_NAMEN.get(self.geselecteerd) or f"Oneindig Level {self.geselecteerd}"
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

        # --- De vier knoppen (vechten, vliegen, racen, bouwen) ---
        arena_record = f"record: lvl {self.arena_record}" if self.arena_record > 0 else ""
        self._teken_zij_knop(self.ARENA_KNOP, (180, 40, 40), (210, 70, 40),
                             "⚔️", "VECHTEN", arena_record, "(klik of V)")
        vlucht_record = f"record: baan {self.vlucht_record}" if self.vlucht_record > 0 else ""
        self._teken_zij_knop(self.VLUCHT_KNOP, (120, 60, 170), (150, 90, 200),
                             "✈️", "VLIEGEN", vlucht_record, "(klik of F)")
        race_record = f"record: baan {self.race_record}" if self.race_record > 0 else ""
        self._teken_zij_knop(self.RACE_KNOP, (40, 110, 180), (40, 150, 210),
                             "🏁", "RACEN", race_record, "(klik of R)")
        self._teken_zij_knop(self.TWEE_KNOP, (200, 120, 30), (230, 160, 40),
                             "👬", "2 SPELERS", "samen racen!", "(klik of 2)")
        self._teken_zij_knop(self.BOUWER_KNOP, (150, 100, 30), (190, 140, 40),
                             "🔨", "BOUWEN", "", "(klik of B)")

    def _teken_zij_knop(self, rect, hoofd_kleur, top_kleur, emoji, naam,
                        record_tekst, hint):
        """Teken een knop aan de zijkant (voor vecht-, vlucht-, race- of bouwmodus)."""
        l, r, b, t = rect
        cx = (l + r) // 2
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, hoofd_kleur)
        arcade.draw_lrbt_rectangle_filled(l, r, b, t - 6, top_kleur)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, (255, 220, 120), 3)
        arcade.draw_text(emoji, cx, t - 32, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(naam, cx, t - 56, arcade.color.WHITE, 14, bold=True, anchor_x="center")
        if record_tekst:
            arcade.draw_text(record_tekst, cx, b + 20, arcade.color.YELLOW, 9,
                             bold=True, anchor_x="center")
        arcade.draw_text(hint, cx, b + 6, (255, 230, 180), 9, anchor_x="center")

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
        arcade.draw_lrbt_rectangle_filled(x - 9, x + 9, y - 9, y + 9, arcade.color.YELLOW)
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
            # Ga naar het volgende level (als dat ontgrendeld is). Geen bovengrens:
            # zolang je levels haalt, komen er steeds nieuwe bij!
            if self._is_ontgrendeld(self.geselecteerd + 1):
                self.geselecteerd += 1
        elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
            # Start het level als het ontgrendeld is
            if self._is_ontgrendeld(self.geselecteerd):
                self._start_level(self.geselecteerd)
        elif toets == arcade.key.V:
            # V = start de vechtmodus (arena)
            self._start_arena()
        elif toets == arcade.key.R:
            # R = start de racemodus
            self._start_race()
        elif toets == arcade.key.F:
            # F = start de vliegtuig-modus
            self._start_vlucht()
        elif toets == arcade.key.KEY_2:
            # 2 = start de 2-spelers-modus (split-screen race)
            self._start_twee()
        elif toets == arcade.key.B:
            # B = start de bouwmodus
            self._start_bouwer()

    def on_mouse_press(self, x, y, knop, modifiers):
        """Start de vecht-, vlucht-, race- of bouwmodus bij een klik op een zij-knop."""
        al, ar, ab, at = self.ARENA_KNOP
        vl, vr, vb, vt = self.VLUCHT_KNOP
        rl, rr, rb, rt = self.RACE_KNOP
        tl, tr, tb, tt = self.TWEE_KNOP
        bl, br, bb, bt = self.BOUWER_KNOP
        if al <= x <= ar and ab <= y <= at:
            self._start_arena()
        elif vl <= x <= vr and vb <= y <= vt:
            self._start_vlucht()
        elif rl <= x <= rr and rb <= y <= rt:
            self._start_race()
        elif tl <= x <= tr and tb <= y <= tt:
            self._start_twee()
        elif bl <= x <= br and bb <= y <= bt:
            self._start_bouwer()

    def _start_level(self, nummer):
        """Start het gekozen level — met de huidige punten en levens."""
        from spel import PlatformerSpel
        spel = PlatformerSpel(nummer, self.voltooid, self.punten, self.levens)
        self.window.show_view(spel)

    def _start_arena(self):
        """Start de vechtmodus (arena) bij level 1 — begint helemaal fris."""
        from spel import PlatformerSpel
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None, arena=True,
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _start_race(self):
        """Start de racemodus bij baan 1 — je rent vanzelf vooruit!"""
        from spel import PlatformerSpel
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None, race=True,
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _start_vlucht(self):
        """Start de vliegtuig-modus bij baan 1 — je vliegt vanzelf vooruit!"""
        from spel import PlatformerSpel
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None, vlucht=True,
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _start_twee(self):
        """Start de 2-spelers-modus: het scherm gaat doormidden (split-screen race)."""
        from spel import PlatformerSpel
        spel = PlatformerSpel(1, self.voltooid, punten=0, levens=None, twee=True,
                              kaart_punten=self.punten, kaart_levens=self.levens)
        self.window.show_view(spel)

    def _start_bouwer(self):
        """Open de bouwmodus om je eigen level te maken."""
        from bouwer import BouwerView
        b = BouwerView(self.voltooid, self.punten, self.levens,
                       self.arena_record, self.race_record, self.vlucht_record)
        self.window.show_view(b)

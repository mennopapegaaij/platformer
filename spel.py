# spel.py
# Het hoofdspel — brengt alles samen.
# De PlatformerSpel klasse beheert de game loop: tekenen, bijwerken, toetsen.

import arcade
import copy   # om bij een herstart verse kopieën van je eigen level te maken
import levels as levels_module
import achtergrond as achtergrond_module
from geluid import geluid as geluid_manager
from instellingen import (SCHERM_BREEDTE, SCHERM_HOOGTE, TWEE_BREEDTE, TWEE_HOOGTE,
                           SPRING_KRACHT, LUCHT_KLEUR, VLAG_KLEUR,
                           VLAG_DOEK_KLEUR, LEVEL_NAMEN, AANTAL_LEVELS)
from speler import Speler, VLIEG_PLAFOND
from portaal import SNELHEID_FACTOR
from springers import SpringBol, SpringMat
from powerup import Kogel
import voortgang as voortgang_module


class PlatformerSpel(arcade.View):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self, level_nummer, voltooid_levels, punten=0, levens=None,
                 arena=False, kaart_punten=0, kaart_levens=None, race=False,
                 eigen_level=None, vlucht=False, twee=False):
        super().__init__()
        # Eigen (zelfgebouwd) level uit de bouwmodus (of None)
        self.eigen = eigen_level is not None
        self.eigen_level_data = eigen_level
        # Onthoud welk level we starten en welke al gehaald zijn
        self.start_level = level_nummer
        self.voltooid = voltooid_levels
        # Bewaar punten en levens van het vorige level
        self.start_punten = punten
        self.start_levens = levens   # None = gebruik het standaard aantal levens
        # Vechtmodus (arena): aparte levels waar je alle monsters moet verslaan
        self.arena = arena
        # Racemodus: je rent vanzelf vooruit en springt over gaten/spikes/blokken
        self.race = race
        # Vliegtuig-modus: je vliegt vanzelf vooruit en houdt de knop vast om te stijgen
        self.vlucht = vlucht
        self._vlieg_omhoog = False   # of speler 1 nu de vlieg-knop vasthoudt
        # 2-spelers-modus (split-screen): een tweede speler doet mee. Werkt samen
        # met de gekozen modus (race, vliegen of vechten).
        self.twee = twee
        self._vlieg_omhoog2 = False  # of speler 2 nu de knop vasthoudt
        # De punten/levens van de gewone kaart, om terug te zetten na de arena
        self.kaart_punten = kaart_punten
        self.kaart_levens = kaart_levens
        # Maak een camera aan die de speler volgt
        self.camera = arcade.camera.Camera2D()
        self.camera2 = arcade.camera.Camera2D()   # tweede camera (rechterhelft)
        self.speler = Speler()
        self.speler2 = Speler()                   # de tweede speler
        # Hoogste arena-level dat je mag kiezen met de pijltjes (groeit als je wint)
        self._arena_top = 1

    # Klik-vlakken voor de arena-pijltjes bovenin: (links, rechts, onder, boven)
    ARENA_PIJL_LINKS = (SCHERM_BREEDTE // 2 - 78, SCHERM_BREEDTE // 2 - 44,
                        SCHERM_HOOGTE - 42, SCHERM_HOOGTE - 14)
    ARENA_PIJL_RECHTS = (SCHERM_BREEDTE // 2 + 44, SCHERM_BREEDTE // 2 + 78,
                         SCHERM_HOOGTE - 42, SCHERM_HOOGTE - 14)
    # Klik-vlak voor de reset-knop rechtsboven
    ARENA_RESET_KNOP = (SCHERM_BREEDTE - 100, SCHERM_BREEDTE - 8,
                        SCHERM_HOOGTE - 70, SCHERM_HOOGTE - 44)

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        # Bij 2 spelers wordt het scherm groot (split-screen); anders de gewone maat
        gewenst = (TWEE_BREEDTE, TWEE_HOOGTE) if self.twee else (SCHERM_BREEDTE, SCHERM_HOOGTE)
        if (self.window.width, self.window.height) != gewenst:
            self.window.set_size(*gewenst)
        arcade.set_background_color(LUCHT_KLEUR)
        self.huidig_level = self.start_level
        # Herstel punten van het vorige level
        self.punten = self.start_punten
        # Reset de speler (power-ups weg, positie terug naar start)
        self.speler.volledig_reset()
        if self.twee:
            self.speler2.volledig_reset()
        # Herstel levens als die meegegeven zijn
        if self.start_levens is not None:
            self.speler.levens = self.start_levens
        # Herstel de snelheids- en sprongbonus die je met punten verdiend had
        # (in de vechtmodus geen bonus: daar speel je gewoon normaal)
        bonus = 0 if (self.arena or self.race or self.vlucht) else self.punten // 10
        self.speler.snelheid_bonus = bonus
        self.speler.sprong_bonus = bonus
        # In de arena: met de pijltjes mag je tot je hoogste bereikte level terug/vooruit
        if self.arena:
            record = voortgang_module.laad_voortgang().get("arena_record", 0)
            self._arena_top = max(self.start_level, record)
        self.maak_level(self.start_level)

    def maak_level(self, nummer):
        """Laad een level op basis van het nummer (1 t/m AANTAL_LEVELS)."""

        # Zet de speler terug naar de beginpositie (levens blijven bewaard!)
        self.speler.reset()

        # Spelstatus resetten
        self.gewonnen = False
        self.dood = False
        self.level_gehaald = False
        self.game_over = False

        # Punten worden NIET gereset bij level wisselen — alleen bij nieuw spel!
        if not hasattr(self, 'punten'):
            self.punten = 0

        # Haal de level-gegevens op: eigen level, racebaan, arena of gewone levels
        if self.eigen:
            # Verse kopie, zodat verslagen monsters en opgepakte hartjes bij een
            # herstart weer terug zijn (het opgeslagen level blijft ongewijzigd).
            data = copy.deepcopy(self.eigen_level_data)
            if self.race or self.vlucht:
                # Een zelfgebouwde race-/vliegbaan: je gaat vanzelf op rustige snelheid
                self.speler.snelheid_bonus = 1
                self.speler.sprong_bonus = 0
        elif self.vlucht:
            data = levels_module.maak_vlucht(nummer)
            # In de vliegtuig-modus vlieg je vanzelf vooruit (iets sneller per baan)
            self.speler.snelheid_bonus = levels_module.vlucht_snelheid_bonus(nummer)
            self.speler.sprong_bonus = 0
        elif self.race:
            data = levels_module.maak_race(nummer)
            # In de racemodus ren je vanzelf steeds sneller (past bij de blok-afstanden)
            self.speler.snelheid_bonus = levels_module.race_snelheid_bonus(nummer)
            self.speler.sprong_bonus = 0
        elif self.arena:
            data = levels_module.maak_arena(nummer)
        else:
            data = levels_module.maak_level(nummer)
        platforms = data[0]
        vijanden = data[1]
        powerups = data[2]
        vlag_x = data[3]
        vlag_y = data[4]
        level_breedte = data[5]
        # Portalen zijn optioneel (een 7e onderdeel); niet elk level heeft ze
        self.portalen = list(data[6]) if len(data) > 6 else []
        # Decoratie is optioneel (een 8e onderdeel); alleen zelfgebouwde levels hebben het
        self.decoraties = list(data[7]) if len(data) > 7 else []
        # Spring-bollen en spring-matten (een 9e onderdeel)
        self.springers = list(data[8]) if len(data) > 8 else []
        self.platforms = platforms
        # Zet de begin-modus: vliegtuig in de vluchtmodus, anders het gewone blokje.
        # Portalen kunnen dit tijdens het spelen nog omzetten (ufo/bal/golf)!
        self.speler.modus = "vliegtuig" if self.vlucht else "blok"
        self.speler.zwaartekracht_richting = 1
        # Onthoud de vorige x van de speler (voor de snelheid-portaal 'sweep'-check)
        self._vorige_speler_x = self.speler.x
        # --- 2-spelers-modus: zet speler 2 ook klaar en verdeel het scherm ---
        if self.twee:
            self._zet_twee_klaar()
        # Onthoud welke blokken je kunnen doden als je tegen de ZIJKANT aan botst
        # (net als Geometry Dash). In de race-, vlucht- en bouwmodus tellen ALLE
        # blokken mee (ook de grasblokken); in de gewone levels doen we dit niet,
        # anders zou springen op zwevende platforms ineens dodelijk zijn.
        if self.race or self.vlucht or self.eigen:
            self._blokken = list(platforms)          # alle blokken, ook gras
        else:
            self._blokken = []                       # gewone levels: geen zijkant-dood
        self.vijanden = vijanden
        self.powerups = powerups
        self.vlag_x = vlag_x
        self.vlag_y = vlag_y
        self.level_breedte = level_breedte
        self.kogels = []   # Lijst van actieve kogels

        # Bepaal of de speler genoeg punten heeft voor dit bonus-level
        # (in de arena bestaat deze waarschuwing niet)
        benodigde_punten = {} if (self.arena or self.race or self.eigen) else {6: 10, 7: 20, 8: 30, 9: 70}
        if nummer in benodigde_punten and self.punten < benodigde_punten[nummer]:
            self._waarschuwing = (f"⚠️  Let op! Dit level heeft minimaal "
                                  f"{benodigde_punten[nummer]} punten nodig. "
                                  f"Jij hebt er {self.punten}. Verslaan monsters voor meer punten!")
            self._waarschuwing_teller = 300   # 5 seconden zichtbaar
        else:
            self._waarschuwing = ""
            self._waarschuwing_teller = 0

        # Start de juiste muziek voor dit level
        geluid_manager.speel_muziek(nummer)

    def on_draw(self):
        """Teken alles op het scherm."""
        self.clear()

        # In de 2-spelers-modus tekenen we het scherm (groot) in twee helften
        if self.twee:
            achtergrond_module.teken_achtergrond(self.huidig_level,
                                                 self.window.width, self.window.height)
            self._teken_twee()
            return

        # --- Teken eerst de achtergrond (altijd op vaste plek, schuift niet mee) ---
        achtergrond_module.teken_achtergrond(self.huidig_level, SCHERM_BREEDTE, SCHERM_HOOGTE)

        # --- Alleen tekenen wat in beeld is (scheelt heel veel bij lange banen!) ---
        cam_x = max(SCHERM_BREEDTE / 2,
                    min(self.speler.x + self.speler.breedte / 2,
                        self.level_breedte - SCHERM_BREEDTE / 2))
        links_zicht = cam_x - SCHERM_BREEDTE / 2 - 60
        rechts_zicht = cam_x + SCHERM_BREEDTE / 2 + 60

        def in_beeld(obj, breedte=0):
            # Staat dit object (deels) in het zichtbare stuk?
            return obj.x + breedte >= links_zicht and obj.x <= rechts_zicht

        # --- Teken de spelwereld met de camera ---
        # Alles binnen dit blok beweegt mee met de camera
        with self.camera.activate():

            # Teken eerst de decoratie (achtergrond, geen botsing)
            for deco in self.decoraties:
                if in_beeld(deco, deco.breedte):
                    deco.teken()

            # Teken alleen de platforms die in beeld zijn
            for platform in self.platforms:
                if in_beeld(platform, platform.breedte):
                    platform.teken()

            # Teken alleen de vijanden die in beeld zijn
            for vijand in self.vijanden:
                if in_beeld(vijand, vijand.breedte):
                    vijand.teken()

            # Teken de spring-bollen en spring-matten
            for springer in self.springers:
                if in_beeld(springer, springer.breedte):
                    springer.teken()

            # Teken de power-ups die nog niet opgepakt zijn en in beeld zijn
            for powerup in self.powerups:
                if not powerup.opgepakt and in_beeld(powerup, powerup.breedte):
                    powerup.teken()

            # Teken de vlag (in de arena is er geen vlag)
            if not self.arena:
                self._teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de portalen die in beeld zijn (vorm-wissel poortjes)
            for portaal in self.portalen:
                if in_beeld(portaal, portaal.breedte):
                    portaal.teken()

            # Teken de kogels
            for kogel in self.kogels:
                kogel.teken()

            # Teken de speler
            self.speler.teken()

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---

        # Levelnaam altijd bovenin (arena krijgt een korte naam + pijltjes in het midden)
        if self.eigen:
            naam_tekst = "🔨 Jouw eigen level"
        elif self.vlucht:
            naam_tekst = f"✈️ Vlucht — Baan {self.huidig_level}"
        elif self.race:
            naam_tekst = f"🏁 {levels_module.race_naam(self.huidig_level)}"
        elif self.arena:
            naam_tekst = "⚔️ Vechtmodus"
        else:
            naam = LEVEL_NAMEN.get(self.huidig_level) or f"Oneindig Level {self.huidig_level}"
            naam_tekst = f"Level {self.huidig_level}: {naam}"
        arcade.draw_text(naam_tekst,
                         10, SCHERM_HOOGTE - 30, arcade.color.WHITE, 16, bold=True)

        # Pijltjes bovenin het midden om van monster-level te wisselen (alleen arena)
        if self.arena:
            self._teken_arena_pijltjes()

        # Race- en vliegtuig-modus: voortgangsbalk bovenin (zoals in Geometry Dash!)
        if self.race or self.vlucht:
            self._teken_voortgangsbalk()
        elif not self.eigen:
            # Punten rechtsboven (niet in de race- of bouwmodus)
            snelheid_extra = self.speler.snelheid_bonus
            punten_tekst = f"⭐ {self.punten} punten"
            if snelheid_extra > 0:
                punten_tekst += f"  💨 +{snelheid_extra} snelheid"
            arcade.draw_text(punten_tekst, SCHERM_BREEDTE - 280, SCHERM_HOOGTE - 30,
                             arcade.color.YELLOW, 16, bold=True)

        # Levens weergeven (hartjes)
        self._teken_levens_hud()

        # Power-up icoontjes als een effect actief is
        self._teken_actieve_effecten()

        # Waarschuwing voor bonus-levels (als speler te weinig punten heeft)
        if self._waarschuwing_teller > 0:
            arcade.draw_lrbt_rectangle_filled(20, SCHERM_BREEDTE - 20, 60, 110, (80, 40, 0))
            arcade.draw_lrbt_rectangle_outline(20, SCHERM_BREEDTE - 20, 60, 110,
                                               arcade.color.ORANGE, 2)
            arcade.draw_text(self._waarschuwing, 30, 78,
                             arcade.color.ORANGE, 11, width=SCHERM_BREEDTE - 60,
                             multiline=True)

        # K-toets hint linksonder
        arcade.draw_text("K = kaart", 10, 10, arcade.color.WHITE, 13)

        # De berichten staan altijd netjes in het midden van het scherm
        mx = SCHERM_BREEDTE // 2
        my = SCHERM_HOOGTE // 2

        def bericht_box(kleur):
            arcade.draw_lrbt_rectangle_filled(mx - 300, mx + 300, my - 90, my + 90, kleur)

        def bericht(tekst, dy, kleur=arcade.color.WHITE, grootte=18, vet=False):
            arcade.draw_text(tekst, mx, my + dy, kleur, grootte, bold=vet, anchor_x="center")

        if self.game_over:
            bericht_box((80, 0, 0))
            bericht("💀 Game Over! 💀", 20, grootte=28, vet=True)
            if self.arena:
                bericht(f"Je haalde arena-level {self.huidig_level}!", -12,
                        arcade.color.YELLOW, 16, True)
                bericht("Druk op R om terug naar de kaart te gaan", -45, grootte=16)
            else:
                bericht("Druk op R om opnieuw te beginnen", -40)
        elif self.gewonnen:
            bericht_box(arcade.color.DARK_GREEN)
            bericht("🎉 Je hebt het hele spel uitgespeeld! 🎉", 20, grootte=22, vet=True)
            bericht("Druk op R om terug naar de kaart te gaan", -40)
        elif self.level_gehaald:
            bericht_box(arcade.color.DARK_BLUE)
            if self.eigen:
                bericht("🎉 Je eigen level gehaald! 🎉", 20, grootte=22, vet=True)
                bericht("ENTER of K = terug naar bouwen", -40, grootte=16)
            elif self.vlucht:
                bericht("✈️ Finish! Baan gevlogen! ✈️", 20, grootte=24, vet=True)
                bericht("ENTER = volgende baan  •  K = kaart", -40, grootte=16)
            elif self.race:
                bericht("🏁 Finish! Baan gehaald! 🏁", 20, grootte=24, vet=True)
                bericht("ENTER = volgende baan  •  K = kaart", -40, grootte=16)
            elif self.arena:
                bericht("Alle monsters verslagen! 🎉", 20, grootte=24, vet=True)
                bericht("ENTER = volgend monster-level  •  K = kaart", -40, grootte=16)
            else:
                bericht(f"Level {self.huidig_level} gehaald! 🎉", 20, grootte=26, vet=True)
                bericht("Druk op ENTER om terug naar de kaart te gaan", -40)
        elif self.dood:
            bericht_box(arcade.color.DARK_RED)
            bericht("Oeps! Je ging af!", 20, grootte=26, vet=True)
            if self.arena or self.race or self.eigen:
                bericht("Maar je verliest GEEN leven! 😎", -12, arcade.color.YELLOW, 16, True)
                if self.race:
                    herstart = "Druk op R om deze baan opnieuw te racen"
                elif self.eigen:
                    herstart = "Druk op R om je eigen level opnieuw te spelen"
                else:
                    herstart = "Druk op R om dit monster-level opnieuw te doen"
                bericht(herstart, -45, grootte=16)
            else:
                bericht("Druk op R om dit level opnieuw te spelen", -40)

    def _teken_vlag(self, x, y):
        """Teken een vlag op de gegeven positie."""
        # Vlaggestok
        arcade.draw_line(x, y, x, y + 60, VLAG_KLEUR, 3)
        # Vlagdoek (groen driehoekje)
        arcade.draw_triangle_filled(x, y + 60, x + 30, y + 48, x, y + 36, VLAG_DOEK_KLEUR)

    def _teken_levens_hud(self):
        """Teken de levens als hartjes rechtsboven in het scherm."""
        # In de vecht-, race- en bouwmodus heb je oneindig levens: toon één hartje met ∞
        if self.arena or self.race or self.eigen:
            cx = SCHERM_BREEDTE - 34
            cy = SCHERM_HOOGTE - 20
            arcade.draw_circle_filled(cx - 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_circle_filled(cx + 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_triangle_filled(cx - 10, cy + 2, cx + 10, cy + 2, cx, cy - 8,
                                        arcade.color.RED)
            arcade.draw_text("∞", cx + 14, cy - 10, arcade.color.WHITE, 20, bold=True)
            return
        for i in range(self.speler.levens):
            cx = SCHERM_BREEDTE - 30 - i * 36
            cy = SCHERM_HOOGTE - 20
            # Hartje (twee cirkeltjes + driehoekje)
            arcade.draw_circle_filled(cx - 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_circle_filled(cx + 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_triangle_filled(cx - 10, cy + 2, cx + 10, cy + 2, cx, cy - 8,
                                        arcade.color.RED)

    def _teken_actieve_effecten(self):
        """Teken kleine icoontjes voor actieve power-up effecten."""
        x = 10
        y = SCHERM_HOOGTE - 60
        if self.speler.onkwetsbaar_timer > 0:
            arcade.draw_text("⭐", x, y, arcade.color.YELLOW, 18)
            x += 30
        if self.speler.snelheid_boost_timer > 0:
            arcade.draw_text("💨", x, y, arcade.color.WHITE, 18)
            x += 30
        if self.speler.dubbel_sprong_timer > 0:
            arcade.draw_text("🦘", x, y, arcade.color.WHITE, 18)
            x += 30
        if self.speler.schiet_timer > 0:
            arcade.draw_text("🔫", x, y, arcade.color.WHITE, 18)

    def _teken_arena_pijltjes(self):
        """Teken de klikbare pijltjes ◀ ▶ bovenin het midden (alleen vechtmodus)."""
        ll, lr, lb, lt = self.ARENA_PIJL_LINKS
        rl, rr, rb, rt = self.ARENA_PIJL_RECHTS
        lcy = (lb + lt) / 2
        rcy = (rb + rt) / 2
        kan_links = self.huidig_level > 1
        kan_rechts = self.huidig_level < self._arena_top

        # Knop-achtergrondjes
        arcade.draw_lrbt_rectangle_filled(ll, lr, lb, lt, (0, 0, 0, 150))
        arcade.draw_lrbt_rectangle_filled(rl, rr, rb, rt, (0, 0, 0, 150))

        # Linker pijl (wijst naar links) — grijs als je al op level 1 bent
        kleur_l = arcade.color.WHITE if kan_links else (110, 110, 110)
        arcade.draw_triangle_filled(ll + 8, lcy, lr - 7, lt - 6, lr - 7, lb + 6, kleur_l)

        # Rechter pijl (wijst naar rechts) — grijs als je al op je hoogste level bent
        kleur_r = arcade.color.WHITE if kan_rechts else (110, 110, 110)
        arcade.draw_triangle_filled(rr - 8, rcy, rl + 7, rt - 6, rl + 7, rb + 6, kleur_r)

        # Het levelnummer tussen de pijltjes
        arcade.draw_text(f"Level {self.huidig_level}", SCHERM_BREEDTE // 2, lb + 7,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

        # Reset-knop rechtsboven: begin helemaal opnieuw bij level 1
        # (dezelfde rode kleur als het hartje)
        pl, pr, pb, pt = self.ARENA_RESET_KNOP
        arcade.draw_lrbt_rectangle_filled(pl, pr, pb, pt, arcade.color.RED)
        arcade.draw_lrbt_rectangle_outline(pl, pr, pb, pt, (255, 220, 150), 2)
        arcade.draw_text("🔄 Reset", (pl + pr) / 2, pb + 6,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

    def _teken_voortgangsbalk(self):
        """Teken bovenin een balk die laat zien hoe ver je in de baan bent."""
        doel = self.vlag_x if self.vlag_x > 0 else self.level_breedte
        voortgang = max(0.0, min(self.speler.x / doel, 1.0))
        l, r = SCHERM_BREEDTE // 2 - 520, SCHERM_BREEDTE // 2 + 520
        b, t = SCHERM_HOOGTE - 24, SCHERM_HOOGTE - 9
        # Achtergrond van de balk
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, (40, 40, 55))
        # Het groene gevulde deel (hoe ver je bent)
        if voortgang > 0:
            arcade.draw_lrbt_rectangle_filled(l, l + (r - l) * voortgang, b, t, (80, 220, 90))
        # Wit randje
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
        # Percentage in het midden
        arcade.draw_text(f"{int(voortgang * 100)}%", (l + r) / 2, b,
                         arcade.color.WHITE, 11, bold=True, anchor_x="center")

    def on_update(self, delta_time):
        """Werk het spel bij — dit wordt heel snel herhaald."""

        # 2-spelers-modus heeft zijn eigen (split-screen) update
        if self.twee:
            self._update_twee()
            return

        # Als het spel voorbij is, doe niets meer
        if self.gewonnen or self.game_over or self.level_gehaald:
            return

        # Als de speler dood is, wacht op toetsinvoer (wordt hierboven al getekend)
        if self.dood:
            return

        # In de race- én vliegtuig-modus ga je VANZELF naar rechts
        if self.race or self.vlucht:
            self.speler.rechts_ingedrukt = True
            self.speler.links_ingedrukt = False

        # In de vasthoud-modi (vliegtuig, golf, robot): geef door of de knop vastgehouden wordt
        if self.speler.modus in ("vliegtuig", "golf", "robot"):
            self.speler.vlieg_omhoog = self._vlieg_omhoog

        # Laat de speler bewegen en botsingen controleren
        self.speler.bijwerken(self.level_breedte, self.platforms)

        # Ging de speler door een portaal? Dan wisselt zijn vorm of zijn snelheid
        self._pas_portalen_toe(self.speler, self._vorige_speler_x)
        self._vorige_speler_x = self.speler.x   # onthouden voor de volgende stap

        # Spring-matten (vanzelf) en spring-bollen (onthoud dat je erop staat)
        self._check_springers(self.speler)

        # Draaien hangt af van de modus
        self._pas_rotatie_toe(self.speler)

        # Botste de speler tegen de zijkant van een blok? Dan ga je dood.
        if self._check_blok_zijkant():
            return

        # Waarschuwingstimer aftellen
        if self._waarschuwing_teller > 0:
            self._waarschuwing_teller -= 1

        # Is de speler in een kuil gevallen?
        if self.speler.is_gevallen():
            self._speler_geraakt()
            return

        # --- Camera laten meebewegen met de speler ---
        cam_x = self.speler.x + self.speler.breedte / 2
        cam_x = max(SCHERM_BREEDTE / 2, min(cam_x, self.level_breedte - SCHERM_BREEDTE / 2))
        cam_y = SCHERM_HOOGTE / 2
        self.camera.position = cam_x, cam_y

        # --- Power-ups bijwerken en oppakken ---
        for powerup in self.powerups:
            if not powerup.opgepakt:
                powerup.bijwerken()
                if powerup.raakt_speler(self.speler.x, self.speler.y,
                                        self.speler.breedte, self.speler.hoogte):
                    powerup.toepassen(self.speler)
                    powerup.opgepakt = True
                    geluid_manager.speel_powerup()  # 🎵 Power-up geluid!

        # --- Vijanden bijwerken en controleren ---
        vijanden_weg = []
        nieuwe_vijanden = []   # monsters die de arena-baas oproept
        speler_cx = self.speler.x + self.speler.breedte / 2
        for vijand in self.vijanden:
            vijand.bijwerken(speler_cx)

            # De arena-baas kan kleine monsters oproepen
            if getattr(vijand, 'nieuwe_monsters', None):
                nieuwe_vijanden.extend(vijand.nieuwe_monsters)
                vijand.nieuwe_monsters = []

            # Landt de speler van bovenaf op de vijand?
            # Eerlijk: het telt als een stomp zodra je naar beneden valt,
            # OF als je voeten in de bovenste helft van het monster zitten.
            # Zo ga je niet meer 'af' als een monster omhoog in je springt.
            speler_voeten = self.speler.y
            vijand_midden = vijand.y + vijand.hoogte / 2
            van_boven = (self.speler.snelheid_y < 0) or (speler_voeten >= vijand_midden)
            if (van_boven and
                    vijand.speler_springt_erop(self.speler.x, self.speler.y,
                                               self.speler.breedte, self.speler.hoogte)):
                if hasattr(vijand, 'word_gestompt'):
                    vijand.word_gestompt()
                    if vijand.levens <= 0:
                        vijanden_weg.append(vijand)
                        self._voeg_punt_toe()   # 🏆 Punt voor stompen!
                else:
                    vijanden_weg.append(vijand)
                    self._voeg_punt_toe()       # 🏆 Punt voor stompen!
                self.speler.snelheid_y = SPRING_KRACHT / 2
                geluid_manager.speel_vijand_dood()  # 🎵 Boing!

            # Raakt de vijand de speler? Alleen gevaarlijk als de speler NIET onkwetsbaar is!
            elif (not self.speler.is_onkwetsbaar() and
                  vijand.raakt_speler(self.speler.x, self.speler.y,
                                      self.speler.breedte, self.speler.hoogte)):
                self._speler_geraakt()

        # Verwijder de dode vijanden uit de lijst
        for vijand in vijanden_weg:
            self.vijanden.remove(vijand)

        # Voeg de door de baas opgeroepen monsters toe
        self.vijanden.extend(nieuwe_vijanden)

        # --- Kogels bijwerken en vijanden raken ---
        for kogel in self.kogels:
            kogel.bijwerken(self.level_breedte)
            for vijand in self.vijanden[:]:
                if getattr(vijand, 'is_spike', False):
                    continue   # spikes kun je niet kapotschieten
                if kogel.actief and kogel.raakt_vijand(vijand):
                    kogel.actief = False
                    if hasattr(vijand, 'word_gestompt'):
                        vijand.word_gestompt()
                        if vijand.levens <= 0:
                            self.vijanden.remove(vijand)
                            self._voeg_punt_toe()   # 🏆 Punt voor kogel!
                    else:
                        self.vijanden.remove(vijand)
                        self._voeg_punt_toe()       # 🏆 Punt voor kogel!
                    geluid_manager.speel_vijand_dood()

        # Verwijder kogels die niet meer actief zijn
        self.kogels = [k for k in self.kogels if k.actief]

        # --- Eigen (zelfgebouwd) level: win als je de finishvlag bereikt ---
        if self.eigen:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    self.speler.y < self.vlag_y + 60 and not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
            return

        # --- Vliegtuig-modus: win als je de finishvlag bereikt ---
        if self.vlucht:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                voortgang_module.sla_vlucht_record_op(self.huidig_level)  # record bewaren
            return

        # --- Racemodus: win als je de finishvlag bereikt ---
        if self.race:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    self.speler.y < self.vlag_y + 60 and not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                voortgang_module.sla_race_record_op(self.huidig_level)   # record bewaren
            return

        # --- Arena/vechtmodus: win als ALLE monsters verslagen zijn ---
        # (spikes tellen niet mee — die kun je toch niet doden!)
        if self.arena:
            levende = [v for v in self.vijanden if not getattr(v, 'is_spike', False)]
            if len(levende) == 0 and not self.level_gehaald:
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                # Bewaar het record (hoogste gehaalde arena-level)
                voortgang_module.sla_arena_record_op(self.huidig_level)
            return

        # --- In level 9: win als de eindbaas verslagen is ---
        if self.huidig_level == AANTAL_LEVELS and len(self.vijanden) == 0:
            self.voltooid = voortgang_module.markeer_level_voltooid(
                self.huidig_level, self.voltooid, self.punten, self.speler.levens)
            self.gewonnen = True
            geluid_manager.speel_level_gehaald()
            return

        # --- Heeft de speler de vlag bereikt? ---
        if (self.speler.x + self.speler.breedte > self.vlag_x and
                self.speler.x < self.vlag_x + 10 and
                self.speler.y < self.vlag_y + 60):
            # Markeer dit level als voltooid (sla op in het bestand)
            self.voltooid = voortgang_module.markeer_level_voltooid(
                self.huidig_level, self.voltooid, self.punten, self.speler.levens)
            # In een oneindig spel is er geen 'laatste' level:
            # elke vlag betekent gewoon "level gehaald, door naar het volgende!"
            self.level_gehaald = True
            geluid_manager.speel_level_gehaald()  # 🎵 Fanfare!

    def _voeg_punt_toe(self):
        """Geef de speler 1 punt. Elke 10 punten: sneller én hoger springen!"""
        self.punten += 1
        # De speciale modi (vecht/race/vlucht/bouw) tellen apart: geen bonus, geen opslaan.
        if not (self.arena or self.race or self.vlucht or self.eigen):
            bonus = self.punten // 10
            self.speler.snelheid_bonus = bonus
            self.speler.sprong_bonus = bonus  # Elke 10 punten ook iets hoger springen
            try:
                voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
            except Exception:
                pass

    # Welke modus hoort bij welk portaal-soort
    PORTAAL_MODUS = {"vlucht": "vliegtuig", "blok": "blok",
                     "ufo": "ufo", "bal": "bal", "golf": "golf",
                     "robot": "robot", "spin": "spin"}

    def _pas_rotatie_toe(self, sp):
        """Zet de draai-stand van een speler op basis van zijn modus."""
        modus = sp.modus
        if modus == "vliegtuig":
            sp.rotatie = max(-35, min(35, sp.snelheid_y * 5))     # neus kantelt
        elif modus == "golf":
            sp.rotatie = 35 if sp.vlieg_omhoog else -35            # schuin omhoog/omlaag
        elif modus == "bal":
            sp.rotatie = (sp.rotatie - 7) % 360                    # rollen
        elif modus in ("ufo", "robot", "spin"):
            sp.rotatie = 0                                         # recht
        elif self.race or self.vlucht:
            if sp.staat_op_grond:
                sp.rotatie = round(sp.rotatie / 90) * 90 % 360
            else:
                sp.rotatie = (sp.rotatie + 8) % 360                # tollen in de lucht

    def _spin_teleport(self, sp):
        """Spin-modus: draai de zwaartekracht om en teleporteer naar de andere kant."""
        sp.zwaartekracht_richting *= -1
        sp.snelheid_y = 0
        overlap = lambda p: p.x < sp.x + sp.breedte and p.x + p.breedte > sp.x
        if sp.zwaartekracht_richting == -1:
            # Zwaartekracht omhoog: zoek een platform boven je (of ga naar het plafond)
            doel = VLIEG_PLAFOND - sp.hoogte
            for p in self.platforms:
                if overlap(p) and p.y >= sp.y + sp.hoogte:
                    doel = min(doel, p.y - sp.hoogte)
            sp.y = doel
        else:
            # Zwaartekracht omlaag: zoek een platform onder je (of blijf staan)
            doel = None
            for p in self.platforms:
                if overlap(p) and p.y + p.hoogte <= sp.y:
                    top = p.y + p.hoogte
                    doel = top if doel is None else max(doel, top)
            if doel is not None:
                sp.y = doel

    def _raakt_portaal(self, sp, vorige_x, portaal):
        """Ging deze speler dit frame door het portaal? (Ook bij hoge snelheid via 'sweep'.)"""
        links = min(vorige_x, sp.x)
        rechts = max(vorige_x, sp.x) + sp.breedte
        horizontaal = rechts > portaal.x and links < portaal.x + portaal.breedte
        verticaal = sp.y + sp.hoogte > portaal.y and sp.y < portaal.y + portaal.hoogte
        return horizontaal and verticaal

    def _pas_portalen_toe(self, sp, vorige_x):
        """Ga je door een portaal? Dan verander je van vorm OF van snelheid."""
        for portaal in self.portalen:
            if not self._raakt_portaal(sp, vorige_x, portaal):
                continue
            if portaal.soort in SNELHEID_FACTOR:
                # Snelheid-portaal: ga langzamer of sneller (x0.5 ... x10)
                factor = SNELHEID_FACTOR[portaal.soort]
                if sp.snelheid_factor != factor:
                    sp.snelheid_factor = factor
                    geluid_manager.speel_powerup()
            else:
                # Vorm-portaal: verander van poppetje
                nieuwe_modus = self.PORTAAL_MODUS.get(portaal.soort, "blok")
                if sp.modus != nieuwe_modus:
                    sp.modus = nieuwe_modus
                    sp.snelheid_y = 0                # netjes overschakelen (geen wilde sprong)
                    sp.vlieg_omhoog = False
                    sp.zwaartekracht_richting = 1    # zwaartekracht weer gewoon omlaag
                    if nieuwe_modus != "vliegtuig":
                        sp.rotatie = 0               # weer recht (behalve vliegtuig kantelt)
                    geluid_manager.speel_powerup()   # 🎵 vorm-wissel geluidje

    def _check_springers(self, sp):
        """Spring-matten (vanzelf springen) en spring-bollen (onthoud dat je erop staat)."""
        sp._bol_kracht = None
        sp._draai_bol = False
        for s in self.springers:
            if not s.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                continue
            if isinstance(s, SpringMat):
                # Mat: spring VANZELF omhoog (alleen als je niet al omhoog schiet)
                if sp.snelheid_y <= 0.5:
                    sp.snelheid_y = s.kracht
                    geluid_manager.speel_sprong()
            elif getattr(s, "draai", False):
                sp._draai_bol = True        # draai-bol: druk om de zwaartekracht om te draaien
            else:
                sp._bol_kracht = s.kracht   # gewone bol: druk om te springen

    def _springboost(self, sp):
        """Sta je op een spring-bol en druk je op springen? Dan gebeurt er iets:
        gewone bol = springen, draai-bol = zwaartekracht omdraaien (je valt de andere kant op)."""
        if getattr(sp, "_draai_bol", False):
            sp.zwaartekracht_richting *= -1
            sp.snelheid_y = -6 * sp.zwaartekracht_richting   # duwtje de nieuwe kant op
            sp.rotatie = 180 if sp.zwaartekracht_richting == -1 else 0  # op z'n kop
            geluid_manager.speel_sprong()
            return True
        if getattr(sp, "_bol_kracht", None) is not None:
            sp.snelheid_y = sp._bol_kracht
            geluid_manager.speel_sprong()
            return True
        return False

    def _raakt_blok_zijkant(self, sp):
        """Botst deze speler tegen de ZIJKANT van een blok? (Geometry Dash-dood.)"""
        for p in self._blokken:
            top = p.y + p.hoogte
            # Overlapt de speler verticaal met het blok, maar staat hij er niet bovenop?
            if not (sp.y + sp.hoogte > p.y + 4 and sp.y < top - 6):
                continue
            raakt_links = (sp.snelheid_x > 0 and sp.x < p.x and sp.x + sp.breedte > p.x)
            raakt_rechts = (sp.snelheid_x < 0 and sp.x + sp.breedte > p.x + p.breedte and sp.x < p.x + p.breedte)
            if raakt_links or raakt_rechts:
                return True
        return False

    def _check_blok_zijkant(self):
        """Eén-speler: ga dood als je tegen de zijkant van een blok botst."""
        if self._raakt_blok_zijkant(self.speler):
            self._speler_geraakt()
            return True
        return False

    # ================== 2-SPELERS-MODUS (split-screen race) ==================

    def _zet_twee_klaar(self):
        """Zet speler 2 op de start en verdeel het scherm in twee helften."""
        # Speler 1 wordt blauw, speler 2 wordt rood (zo zie je wie wie is)
        self.speler.kleur = (60, 140, 255)
        self.speler2.kleur = (255, 80, 80)
        self.speler2.reset()
        self.speler2.modus = self.speler.modus
        self.speler2.snelheid_bonus = self.speler.snelheid_bonus
        self.speler2.sprong_bonus = self.speler.sprong_bonus
        self._vorige_speler_x2 = self.speler2.x
        self._finish1 = False
        self._finish2 = False
        self.winnaar = None
        self._vlieg_omhoog = False
        self._vlieg_omhoog2 = False
        # Links speler 1, rechts speler 2 (elk de halve breedte van het grote scherm)
        W, H = self.window.width, self.window.height
        half = W // 2
        self.camera.viewport = arcade.LBWH(0, 0, half, H)
        self.camera.projection = arcade.LRBT(-half / 2, half / 2, -H / 2, H / 2)
        self.camera2.viewport = arcade.LBWH(half, 0, half, H)
        self.camera2.projection = arcade.LRBT(-half / 2, half / 2, -H / 2, H / 2)

    def _is_klaar(self, idx):
        """Is deze speler klaar (gefinisht)? In de vechtmodus nooit (samen tot het eind)."""
        return self._finish1 if idx == 1 else self._finish2

    def _racer_dood(self, sp, idx):
        """Een speler ging af: terug naar de start (geen leven kwijt)."""
        sp.reset()
        sp.modus = "vliegtuig" if self.vlucht else "blok"
        geluid_manager.speel_geraakt()
        if idx == 1:
            self._vorige_speler_x = sp.x
        else:
            self._vorige_speler_x2 = sp.x

    def _beweeg_speler_twee(self, sp, idx):
        """Beweeg één speler (auto-run of handmatig), met portalen en botsingen."""
        if self.race or self.vlucht:
            sp.rechts_ingedrukt = True          # auto-run modi: vanzelf naar rechts
            sp.links_ingedrukt = False
        if sp.modus in ("vliegtuig", "golf", "robot"):
            sp.vlieg_omhoog = self._vlieg_omhoog if idx == 1 else self._vlieg_omhoog2
        sp.bijwerken(self.level_breedte, self.platforms)
        vorige = self._vorige_speler_x if idx == 1 else self._vorige_speler_x2
        self._pas_portalen_toe(sp, vorige)
        if idx == 1:
            self._vorige_speler_x = sp.x
        else:
            self._vorige_speler_x2 = sp.x
        self._check_springers(sp)          # spring-matten en spring-bollen
        self._pas_rotatie_toe(sp)
        if self._raakt_blok_zijkant(sp) or sp.is_gevallen():
            self._racer_dood(sp, idx)

    def _update_monsters_twee(self):
        """Werk de monsters bij; beide spelers kunnen stompen of geraakt worden."""
        weg = []
        nieuw = []
        p1c = self.speler.x + self.speler.breedte / 2
        p2c = self.speler2.x + self.speler2.breedte / 2
        for vijand in self.vijanden:
            vc = vijand.x + vijand.breedte / 2
            doel = p1c if abs(p1c - vc) <= abs(p2c - vc) else p2c   # richt op dichtstbijzijnde
            vijand.bijwerken(doel)
            if getattr(vijand, 'nieuwe_monsters', None):
                nieuw.extend(vijand.nieuwe_monsters)
                vijand.nieuwe_monsters = []
            for sp, idx in ((self.speler, 1), (self.speler2, 2)):
                if self._is_klaar(idx):
                    continue
                van_boven = (sp.snelheid_y < 0) or (sp.y >= vijand.y + vijand.hoogte / 2)
                if van_boven and vijand.speler_springt_erop(sp.x, sp.y, sp.breedte, sp.hoogte):
                    if hasattr(vijand, 'word_gestompt'):
                        vijand.word_gestompt()
                        if vijand.levens <= 0 and vijand not in weg:
                            weg.append(vijand)
                    elif vijand not in weg:
                        weg.append(vijand)
                    sp.snelheid_y = SPRING_KRACHT / 2
                    geluid_manager.speel_vijand_dood()
                elif not sp.is_onkwetsbaar() and vijand.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                    self._racer_dood(sp, idx)
        for v in weg:
            if v in self.vijanden:
                self.vijanden.remove(v)
        self.vijanden.extend(nieuw)

    def _check_win_twee(self):
        """Bepaal per modus of er gewonnen is."""
        if self.arena:
            levende = [v for v in self.vijanden if not getattr(v, 'is_spike', False)]
            if not levende and not self.level_gehaald:
                self.level_gehaald = True    # allebei gewonnen!
                geluid_manager.speel_level_gehaald()
            return
        # Vlag-modi (race/vlucht): wie het eerst bij de finish is, wint
        for sp, idx in ((self.speler, 1), (self.speler2, 2)):
            if self._is_klaar(idx):
                continue
            y_ok = True if self.vlucht else sp.y < self.vlag_y + 60
            if sp.x + sp.breedte > self.vlag_x and y_ok:
                if idx == 1:
                    self._finish1 = True
                else:
                    self._finish2 = True
                if not self.winnaar:
                    self.winnaar = idx
                    geluid_manager.speel_level_gehaald()

    def _update_twee(self):
        """Werk beide spelers + de monsters bij en laat de twee camera's meebewegen."""
        if self.winnaar or self.level_gehaald:
            return
        for sp, idx in ((self.speler, 1), (self.speler2, 2)):
            if not self._is_klaar(idx):
                self._beweeg_speler_twee(sp, idx)
        self._update_monsters_twee()
        # Power-ups: beide spelers kunnen ze oppakken
        for pu in self.powerups:
            if not pu.opgepakt:
                pu.bijwerken()
                for sp, idx in ((self.speler, 1), (self.speler2, 2)):
                    if not self._is_klaar(idx) and pu.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                        pu.toepassen(sp)
                        pu.opgepakt = True
                        geluid_manager.speel_powerup()
                        break
        self._check_win_twee()
        # Camera's laten meebewegen
        W, H = self.window.width, self.window.height
        half = W // 2
        for sp, cam in ((self.speler, self.camera), (self.speler2, self.camera2)):
            cx = sp.x + sp.breedte / 2
            cx = max(half / 2, min(cx, self.level_breedte - half / 2))
            cam.position = cx, H / 2

    def _actie_druk(self, sp, idx):
        """Een speler drukt op zijn knop: doe de actie die bij zijn modus hoort."""
        # Sta je op een spring-bol? Dan spring je (ook in de lucht), wat je modus ook is.
        if self._springboost(sp):
            return
        m = sp.modus
        if m in ("vliegtuig", "golf"):
            if idx == 1:
                self._vlieg_omhoog = True
            else:
                self._vlieg_omhoog2 = True
        elif m == "robot":
            if idx == 1:
                self._vlieg_omhoog = True
            else:
                self._vlieg_omhoog2 = True
            sp.robot_sprong()
            geluid_manager.speel_sprong()
        elif m == "ufo":
            sp.flap()
            geluid_manager.speel_sprong()
        elif m == "bal":
            sp.flip_zwaartekracht()
            geluid_manager.speel_sprong()
        elif m == "spin":
            self._spin_teleport(sp)
            geluid_manager.speel_sprong()
        else:
            op_grond = sp.staat_op_grond
            sp.spring()
            if op_grond:
                geluid_manager.speel_sprong()

    def _volgende_twee_baan(self):
        """Ga met z'n tweeën naar de volgende racebaan."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _teken_twee(self):
        """Teken het scherm in twee helften: links speler 1, rechts speler 2."""
        W, H = self.window.width, self.window.height
        half = W // 2
        for sp, cam in ((self.speler, self.camera), (self.speler2, self.camera2)):
            with cam.activate():
                cx = cam.position[0]
                links = cx - half / 2 - 60
                rechts = cx + half / 2 + 60

                def zicht(o, b=0):
                    return o.x + b >= links and o.x <= rechts

                for deco in self.decoraties:
                    if zicht(deco, deco.breedte):
                        deco.teken()
                for p in self.platforms:
                    if zicht(p, p.breedte):
                        p.teken()
                for v in self.vijanden:
                    if zicht(v, v.breedte):
                        v.teken()
                for springer in self.springers:
                    if zicht(springer, springer.breedte):
                        springer.teken()
                for portaal in self.portalen:
                    if zicht(portaal, portaal.breedte):
                        portaal.teken()
                if not self.arena:                 # in de vechtmodus is er geen vlag
                    self._teken_vlag(self.vlag_x, self.vlag_y)
                # Teken BEIDE spelers, zodat je elkaar ziet als je dicht bij elkaar bent.
                # Speler 1 is blauw, speler 2 is rood (die kleuren zitten in de speler zelf).
                for speler in (self.speler, self.speler2):
                    if zicht(speler, speler.breedte):
                        speler.teken()
        # Scheidingslijn precies in het midden
        arcade.draw_lrbt_rectangle_filled(half - 3, half + 3, 0, H, (20, 20, 30))
        self._teken_twee_hud()
        # Banner: iemand wint (race/vlucht) of allebei winnen (vechtmodus)
        if self.winnaar or (self.arena and self.level_gehaald):
            mx, my = W // 2, H // 2
            arcade.draw_lrbt_rectangle_filled(mx - 340, mx + 340, my - 80, my + 80, (20, 70, 20))
            arcade.draw_lrbt_rectangle_outline(mx - 340, mx + 340, my - 80, my + 80,
                                               arcade.color.WHITE, 3)
            if self.winnaar:
                titel = f"🏆 Speler {self.winnaar} wint!"
                hint = "ENTER = nieuwe baan   •   K = kaart"
            else:
                titel = "🎉 Allebei gewonnen! 🎉"
                hint = "ENTER = volgend monster-level   •   K = kaart"
            arcade.draw_text(titel, mx, my + 12, (255, 230, 80), 34, bold=True, anchor_x="center")
            arcade.draw_text(hint, mx, my - 42, arcade.color.WHITE, 18, anchor_x="center")

    def _teken_twee_hud(self):
        """Teken bovenin elke helft een naam + (in race/vlucht) een voortgangsbalk."""
        W, H = self.window.width, self.window.height
        half = W // 2
        doel = self.vlag_x if self.vlag_x > 0 else self.level_breedte
        for sp, idx, midden, klaar in ((self.speler, 1, half // 2, self._finish1),
                                       (self.speler2, 2, half + half // 2, self._finish2)):
            if self.arena:
                # Vechtmodus: geen voortgangsbalk, alleen een kopje
                arcade.draw_text(f"Speler {idx}  —  Vechten! ⚔️", midden, H - 40,
                                 arcade.color.WHITE, 16, bold=True, anchor_x="center")
                continue
            pct = max(0.0, min(sp.x / doel, 1.0))
            bl, br = midden - 150, midden + 150
            bb, bt = H - 26, H - 12
            arcade.draw_lrbt_rectangle_filled(bl, br, bb, bt, (40, 40, 55))
            if pct > 0:
                arcade.draw_lrbt_rectangle_filled(bl, bl + (br - bl) * pct, bb, bt, (80, 220, 90))
            arcade.draw_lrbt_rectangle_outline(bl, br, bb, bt, arcade.color.WHITE, 2)
            kop = f"Speler {idx}  —  FINISH! 🏁" if klaar else f"Speler {idx}  —  {int(pct * 100)}%"
            arcade.draw_text(kop, midden, H - 52, arcade.color.WHITE, 16,
                             bold=True, anchor_x="center")

    def _speler_geraakt(self):
        """Verwerk dat de speler geraakt wordt: leven aftrekken of game over."""
        # In de vecht-, race-, vlucht- en bouwmodus ga je wel 'af' (opnieuw proberen),
        # maar je verliest GEEN leven en het is nooit game-over.
        if self.arena or self.race or self.vlucht or self.eigen:
            geluid_manager.speel_geraakt()  # 🎵 Bonk!
            self.dood = True
            return
        self.speler.levens -= 1
        geluid_manager.speel_geraakt()  # 🎵 Bonk!
        # Sla voortgang op (update levens) — in de arena NIET
        if not self.arena:
            try:
                voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
            except Exception:
                pass
        if self.speler.levens <= 0:
            self.game_over = True
            geluid_manager.stop_muziek()
            geluid_manager.speel_game_over()  # 🎵 Game over melodie
        else:
            self.dood = True

    def on_key_press(self, toets, modifiers):
        """Wordt aangeroepen als je een toets indrukt."""
        # 2-spelers-modus: speler 1 = W (springen) + A/D (bewegen),
        #                   speler 2 = PIJLTJE OMHOOG (springen) + links/rechts (bewegen)
        if self.twee:
            bezig = not (self.winnaar or self.level_gehaald)
            if toets in (arcade.key.W, arcade.key.SPACE):
                if bezig and not self._finish1:
                    self._actie_druk(self.speler, 1)
            elif toets == arcade.key.A:
                self.speler.links_ingedrukt = True
            elif toets == arcade.key.D:
                self.speler.rechts_ingedrukt = True
            elif toets == arcade.key.UP:
                if bezig and not self._finish2:
                    self._actie_druk(self.speler2, 2)
            elif toets == arcade.key.LEFT:
                self.speler2.links_ingedrukt = True
            elif toets == arcade.key.RIGHT:
                self.speler2.rechts_ingedrukt = True
            elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
                if self.winnaar or self.level_gehaald:
                    if self.eigen:
                        self._naar_bouwer()          # terug naar de bouwmodus
                    else:
                        self._volgende_twee_baan()
            elif toets == arcade.key.K:
                if self.eigen:
                    self._naar_bouwer()              # terug naar de bouwmodus
                else:
                    self._verlaat_arena()            # terug naar de kaart
            return
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = True
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = True
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            # Sta je op een spring-bol? Dan spring je meteen (ook in de lucht)
            if self._springboost(self.speler):
                return
            modus = self.speler.modus
            if modus in ("vliegtuig", "golf"):
                # Vasthoud-modi: knop ingedrukt = omhoog (stuwen of schuin omhoog)
                self._vlieg_omhoog = True
            elif modus == "robot":
                # Robot: vasthouden = hoger springen; de sprong begint hier
                self._vlieg_omhoog = True
                self.speler.robot_sprong()
                geluid_manager.speel_sprong()
            elif modus == "ufo":
                # UFO: elke tik een sprongetje omhoog
                self.speler.flap()
                geluid_manager.speel_sprong()
            elif modus == "bal":
                # Bal: elke tik draait de zwaartekracht om
                self.speler.flip_zwaartekracht()
                geluid_manager.speel_sprong()
            elif modus == "spin":
                # Spin: elke tik teleporteer je naar de vloer of het plafond
                self._spin_teleport(self.speler)
                geluid_manager.speel_sprong()
            else:
                # Gewoon blokje: springen
                voor_sprong = self.speler.staat_op_grond or (
                    self.speler.dubbel_sprong_timer > 0 and not self.speler.heeft_dubbel_gesprongen)
                self.speler.spring()
                if voor_sprong:
                    geluid_manager.speel_sprong()  # 🎵 Sprong-piepje!
        elif toets == arcade.key.Z:
            # Z = schieten (alleen als schiet power-up actief is)
            if self.speler.schiet_timer > 0 and not self.gewonnen and not self.game_over and not self.dood:
                richting = 1 if self.speler.kijkt_rechts else -1
                kogel_x = (self.speler.x + self.speler.breedte + 4 if richting == 1
                           else self.speler.x - 4)
                kogel_y = self.speler.y + self.speler.hoogte // 2
                self.kogels.append(Kogel(kogel_x, kogel_y, richting))
        elif toets == arcade.key.KEY_2 and self.arena:
            # Geheime sprong-toets: spring meteen naar level 250 (om te proberen!)
            self.huidig_level = 250
            self._arena_top = max(self._arena_top, 250)
            self.maak_level(250)
        elif toets == arcade.key.K:
            # K = terug (naar de bouwmodus, of naar de kaart)
            if self.eigen:
                self._naar_bouwer()
            elif self.arena or self.race or self.vlucht:
                self._verlaat_arena()   # zet de kaart-punten/levens terug
            else:
                self._naar_kaart()
        elif toets == arcade.key.ENTER or toets == arcade.key.NUM_ENTER:
            # ENTER = door na een gehaald level
            if self.level_gehaald:
                if self.eigen:
                    self._naar_bouwer()            # Terug naar de bouwmodus
                elif self.vlucht:
                    self._volgende_vlucht_baan()   # Door naar de volgende vliegbaan!
                elif self.race:
                    self._volgende_race_baan()     # Door naar de volgende racebaan!
                elif self.arena:
                    self._volgende_arena_level()   # Door naar het volgende monster-level!
                else:
                    self._naar_kaart()
        elif toets == arcade.key.R:
            if self.arena and self.game_over:
                self._verlaat_arena()              # Na game-over in de arena: terug naar de kaart
            elif self.gewonnen:
                self._naar_kaart()                 # Terug naar de kaart na winst
            elif self.game_over:
                # Opnieuw beginnen bij level 1! Alles wordt gereset
                self.punten = 0
                self.start_level = 1
                self.huidig_level = 1
                self.speler.volledig_reset()
                # Voortgang wissen — alle levels weer op slot
                self.voltooid.clear()
                # Sla op: geen voltooide levels meer, punten en levens terug naar 0/None
                voortgang_module.sla_voortgang_op(self.voltooid, 0, None)
                self.maak_level(1)
            elif self.dood:
                self.maak_level(self.huidig_level) # Zelfde level opnieuw (levens blijven!)

    def on_mouse_press(self, x, y, knop, modifiers):
        """In de vechtmodus: klik op de pijltjes of de reset-knop bovenin."""
        if not self.arena:
            return
        ll, lr, lb, lt = self.ARENA_PIJL_LINKS
        rl, rr, rb, rt = self.ARENA_PIJL_RECHTS
        pl, pr, pb, pt = self.ARENA_RESET_KNOP
        if ll <= x <= lr and lb <= y <= lt:
            self._ga_naar_arena_level(self.huidig_level - 1)   # ◀ vorige level
        elif rl <= x <= rr and rb <= y <= rt:
            self._ga_naar_arena_level(self.huidig_level + 1)   # ▶ volgende level
        elif pl <= x <= pr and pb <= y <= pt:
            self._arena_reset()                                 # 🔄 helemaal opnieuw

    def _arena_reset(self):
        """Begin de vechtmodus helemaal opnieuw bij level 1.

        Ook je hoogste-bereikte level gaat terug naar 1, dus met ▶ kun je
        niet meer naar de hogere levels springen — die moet je opnieuw winnen.
        """
        self.huidig_level = 1
        self._arena_top = 1
        voortgang_module.reset_arena_record()   # record ook terug naar 0
        self.maak_level(1)

    def on_key_release(self, toets, modifiers):
        """Wordt aangeroepen als je een toets loslaat."""
        # 2-spelers-modus: knoppen loslaten
        if self.twee:
            if toets in (arcade.key.W, arcade.key.SPACE):
                self._vlieg_omhoog = False
            elif toets == arcade.key.A:
                self.speler.links_ingedrukt = False
            elif toets == arcade.key.D:
                self.speler.rechts_ingedrukt = False
            elif toets == arcade.key.UP:
                self._vlieg_omhoog2 = False
            elif toets == arcade.key.LEFT:
                self.speler2.links_ingedrukt = False
            elif toets == arcade.key.RIGHT:
                self.speler2.rechts_ingedrukt = False
            return
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = False
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            # Vliegtuig-modus: knop losgelaten = niet meer stuwen (je zakt)
            self._vlieg_omhoog = False

    def _naar_kaart(self):
        """Ga terug naar de levelkaart — punten en levens worden bewaard."""
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        # Sla voortgang op vóór je naar de kaart gaat
        try:
            voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
        except Exception:
            pass
        data = voortgang_module.laad_voortgang()
        kaart = LevelKaartView(self.voltooid, self.punten, self.speler.levens,
                               data.get("arena_record", 0), data.get("race_record", 0),
                               data.get("vlucht_record", 0))
        self.window.show_view(kaart)

    def _naar_bouwer(self):
        """Ga terug naar de bouwmodus (met dezelfde kaart-gegevens)."""
        from bouwer import BouwerView
        geluid_manager.stop_muziek()
        data = voortgang_module.laad_voortgang()
        b = BouwerView(self.voltooid, self.kaart_punten, self.kaart_levens,
                       data.get("arena_record", 0), data.get("race_record", 0),
                       data.get("vlucht_record", 0), twee=self.twee)
        self.window.show_view(b)

    def _volgende_arena_level(self):
        """Ga naar het volgende monster-level (punten en levens blijven behouden)."""
        self.huidig_level += 1
        # Onthoud dat je nu zo hoog bent geweest (zodat je met ▶ hier terug kunt)
        self._arena_top = max(self._arena_top, self.huidig_level)
        self.maak_level(self.huidig_level)

    def _volgende_race_baan(self):
        """Ga naar de volgende (langere, snellere) racebaan."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _volgende_vlucht_baan(self):
        """Ga naar de volgende (langere) vliegtuig-baan."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _ga_naar_arena_level(self, nummer):
        """Spring naar een ander arena-level met de pijltjes (tussen 1 en je hoogste)."""
        nummer = max(1, min(nummer, self._arena_top))
        if nummer != self.huidig_level:
            self.huidig_level = nummer
            self.maak_level(nummer)

    def _verlaat_arena(self):
        """Verlaat de vechtmodus en ga terug naar de kaart.

        De gewone punten en levens van de kaart worden teruggezet
        (de arena telt helemaal apart).
        """
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        data = voortgang_module.laad_voortgang()
        kaart = LevelKaartView(self.voltooid, self.kaart_punten, self.kaart_levens,
                               data.get("arena_record", 0), data.get("race_record", 0),
                               data.get("vlucht_record", 0))
        self.window.show_view(kaart)

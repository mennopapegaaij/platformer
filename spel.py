# spel.py
# Het hoofdspel — brengt alles samen.
# De PlatformerSpel klasse beheert de game loop: tekenen, bijwerken, toetsen.

import arcade
import levels as levels_module
import achtergrond as achtergrond_module
from geluid import geluid as geluid_manager
from instellingen import (SCHERM_BREEDTE, SCHERM_HOOGTE,
                           SPRING_KRACHT, LUCHT_KLEUR, VLAG_KLEUR,
                           VLAG_DOEK_KLEUR, LEVEL_NAMEN, AANTAL_LEVELS)
from speler import Speler
from powerup import Kogel
import voortgang as voortgang_module


class PlatformerSpel(arcade.View):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self, level_nummer, voltooid_levels, punten=0, levens=None,
                 arena=False, kaart_punten=0, kaart_levens=None):
        super().__init__()
        # Onthoud welk level we starten en welke al gehaald zijn
        self.start_level = level_nummer
        self.voltooid = voltooid_levels
        # Bewaar punten en levens van het vorige level
        self.start_punten = punten
        self.start_levens = levens   # None = gebruik het standaard aantal levens
        # Vechtmodus (arena): aparte levels waar je alle monsters moet verslaan
        self.arena = arena
        # De punten/levens van de gewone kaart, om terug te zetten na de arena
        self.kaart_punten = kaart_punten
        self.kaart_levens = kaart_levens
        # Maak een camera aan die de speler volgt
        self.camera = arcade.camera.Camera2D()
        self.speler = Speler()
        # Hoogste arena-level dat je mag kiezen met de pijltjes (groeit als je wint)
        self._arena_top = 1

    # Klik-vlakken voor de arena-pijltjes bovenin: (links, rechts, onder, boven)
    ARENA_PIJL_LINKS = (322, 356, 458, 486)
    ARENA_PIJL_RECHTS = (444, 478, 458, 486)
    # Klik-vlak voor de reset-knop rechtsboven
    ARENA_RESET_KNOP = (700, 792, 430, 456)

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        arcade.set_background_color(LUCHT_KLEUR)
        self.huidig_level = self.start_level
        # Herstel punten van het vorige level
        self.punten = self.start_punten
        # Reset de speler (power-ups weg, positie terug naar start)
        self.speler.volledig_reset()
        # Herstel levens als die meegegeven zijn
        if self.start_levens is not None:
            self.speler.levens = self.start_levens
        # Herstel de snelheids- en sprongbonus die je met punten verdiend had
        # (in de vechtmodus geen bonus: daar speel je gewoon normaal)
        bonus = 0 if self.arena else self.punten // 10
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

        # Haal de level-gegevens op: uit de arena of uit de gewone levels
        if self.arena:
            data = levels_module.maak_arena(nummer)
        else:
            data = levels_module.maak_level(nummer)
        platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte = data
        self.platforms = platforms
        self.vijanden = vijanden
        self.powerups = powerups
        self.vlag_x = vlag_x
        self.vlag_y = vlag_y
        self.level_breedte = level_breedte
        self.kogels = []   # Lijst van actieve kogels

        # Bepaal of de speler genoeg punten heeft voor dit bonus-level
        # (in de arena bestaat deze waarschuwing niet)
        benodigde_punten = {} if self.arena else {6: 10, 7: 20, 8: 30, 9: 70}
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

        # --- Teken eerst de achtergrond (altijd op vaste plek, schuift niet mee) ---
        achtergrond_module.teken_achtergrond(self.huidig_level, SCHERM_BREEDTE, SCHERM_HOOGTE)

        # --- Teken de spelwereld met de camera ---
        # Alles binnen dit blok beweegt mee met de camera
        with self.camera.activate():

            # Teken alle platforms
            for platform in self.platforms:
                platform.teken()

            # Teken alle vijanden
            for vijand in self.vijanden:
                vijand.teken()

            # Teken de power-ups die nog niet opgepakt zijn
            for powerup in self.powerups:
                if not powerup.opgepakt:
                    powerup.teken()

            # Teken de vlag (in de arena is er geen vlag)
            if not self.arena:
                self._teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de kogels
            for kogel in self.kogels:
                kogel.teken()

            # Teken de speler
            self.speler.teken()

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---

        # Levelnaam altijd bovenin (arena krijgt een korte naam + pijltjes in het midden)
        if self.arena:
            naam_tekst = "⚔️ Vechtmodus"
        else:
            naam = LEVEL_NAMEN.get(self.huidig_level) or f"Oneindig Level {self.huidig_level}"
            naam_tekst = f"Level {self.huidig_level}: {naam}"
        arcade.draw_text(naam_tekst,
                         10, SCHERM_HOOGTE - 30, arcade.color.WHITE, 16, bold=True)

        # Pijltjes bovenin het midden om van monster-level te wisselen (alleen arena)
        if self.arena:
            self._teken_arena_pijltjes()

        # Punten rechtsboven
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

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, (80, 0, 0))
            arcade.draw_text("💀 Game Over! 💀",
                             230, 270, arcade.color.WHITE, 28, bold=True)
            if self.arena:
                arcade.draw_text(f"Je haalde arena-level {self.huidig_level}!",
                                 220, 240, arcade.color.YELLOW, 16, bold=True)
                arcade.draw_text("Druk op R om terug naar de kaart te gaan",
                                 190, 205, arcade.color.WHITE, 16)
            else:
                arcade.draw_text("Druk op R om opnieuw te beginnen",
                                 205, 210, arcade.color.WHITE, 18)
        elif self.gewonnen:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_GREEN)
            arcade.draw_text("🎉 Je hebt het hele spel uitgespeeld! 🎉",
                             130, 270, arcade.color.WHITE, 22, bold=True)
            arcade.draw_text("Druk op R om terug naar de kaart te gaan",
                             185, 210, arcade.color.WHITE, 18)
        elif self.level_gehaald:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_BLUE)
            if self.arena:
                arcade.draw_text("Alle monsters verslagen! 🎉",
                                 200, 270, arcade.color.WHITE, 24, bold=True)
                arcade.draw_text("ENTER = volgend monster-level  •  K = kaart",
                                 180, 210, arcade.color.WHITE, 16)
            else:
                arcade.draw_text(f"Level {self.huidig_level} gehaald! 🎉",
                                 240, 270, arcade.color.WHITE, 26, bold=True)
                arcade.draw_text("Druk op ENTER om terug naar de kaart te gaan",
                                 185, 210, arcade.color.WHITE, 18)
        elif self.dood:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_RED)
            arcade.draw_text("Oeps! Je ging af!",
                             240, 270, arcade.color.WHITE, 26, bold=True)
            if self.arena:
                arcade.draw_text("Maar je verliest GEEN leven! 😎",
                                 220, 240, arcade.color.YELLOW, 16, bold=True)
                arcade.draw_text("Druk op R om dit monster-level opnieuw te doen",
                                 175, 205, arcade.color.WHITE, 16)
            else:
                arcade.draw_text("Druk op R om dit level opnieuw te spelen",
                                 190, 210, arcade.color.WHITE, 18)

    def _teken_vlag(self, x, y):
        """Teken een vlag op de gegeven positie."""
        # Vlaggestok
        arcade.draw_line(x, y, x, y + 60, VLAG_KLEUR, 3)
        # Vlagdoek (groen driehoekje)
        arcade.draw_triangle_filled(x, y + 60, x + 30, y + 48, x, y + 36, VLAG_DOEK_KLEUR)

    def _teken_levens_hud(self):
        """Teken de levens als hartjes rechtsboven in het scherm."""
        # In de vechtmodus heb je oneindig levens: toon één hartje met ∞
        if self.arena:
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
        arcade.draw_text(f"Level {self.huidig_level}", 400, lb + 7,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

        # Reset-knop rechtsboven: begin helemaal opnieuw bij level 1
        pl, pr, pb, pt = self.ARENA_RESET_KNOP
        arcade.draw_lrbt_rectangle_filled(pl, pr, pb, pt, (180, 60, 40))
        arcade.draw_lrbt_rectangle_outline(pl, pr, pb, pt, (255, 220, 150), 2)
        arcade.draw_text("🔄 Reset", (pl + pr) / 2, pb + 6,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

    def on_update(self, delta_time):
        """Werk het spel bij — dit wordt heel snel herhaald."""

        # Als het spel voorbij is, doe niets meer
        if self.gewonnen or self.game_over or self.level_gehaald:
            return

        # Als de speler dood is, wacht op toetsinvoer (wordt hierboven al getekend)
        if self.dood:
            return

        # Laat de speler bewegen en botsingen controleren
        self.speler.bijwerken(self.level_breedte, self.platforms)

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

        # --- Arena/vechtmodus: win als ALLE monsters verslagen zijn ---
        if self.arena:
            if len(self.vijanden) == 0 and not self.level_gehaald:
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
        # In de vechtmodus GEEN extra snelheid/sprong — daar speel je gewoon
        # met je normale snelheid en sprongkracht.
        if not self.arena:
            bonus = self.punten // 10
            self.speler.snelheid_bonus = bonus
            self.speler.sprong_bonus = bonus  # Elke 10 punten ook iets hoger springen
        # Sla voortgang op (updates punten) — in de arena NIET, want die telt apart
        if not self.arena:
            try:
                voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
            except Exception:
                pass

    def _speler_geraakt(self):
        """Verwerk dat de speler geraakt wordt: leven aftrekken of game over."""
        # In de vechtmodus ga je wel 'af' (level opnieuw), maar je verliest
        # GEEN leven en het is nooit game-over.
        if self.arena:
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
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = True
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = True
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
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
        elif toets == arcade.key.K:
            # K = terug naar de kaart (altijd beschikbaar)
            if self.arena:
                self._verlaat_arena()
            else:
                self._naar_kaart()
        elif toets == arcade.key.ENTER or toets == arcade.key.NUM_ENTER:
            # ENTER = door na een gehaald level
            if self.level_gehaald:
                if self.arena:
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
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = False

    def _naar_kaart(self):
        """Ga terug naar de levelkaart — punten en levens worden bewaard."""
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        # Sla voortgang op vóór je naar de kaart gaat
        try:
            voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
        except Exception:
            pass
        record = voortgang_module.laad_voortgang().get("arena_record", 0)
        kaart = LevelKaartView(self.voltooid, self.punten, self.speler.levens, record)
        self.window.show_view(kaart)

    def _volgende_arena_level(self):
        """Ga naar het volgende monster-level (punten en levens blijven behouden)."""
        self.huidig_level += 1
        # Onthoud dat je nu zo hoog bent geweest (zodat je met ▶ hier terug kunt)
        self._arena_top = max(self._arena_top, self.huidig_level)
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
        record = voortgang_module.laad_voortgang().get("arena_record", 0)
        kaart = LevelKaartView(self.voltooid, self.kaart_punten, self.kaart_levens, record)
        self.window.show_view(kaart)

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

    def __init__(self, level_nummer, voltooid_levels):
        super().__init__()
        # Onthoud welk level we starten en welke al gehaald zijn
        self.start_level = level_nummer
        self.voltooid = voltooid_levels
        # Maak een camera aan die de speler volgt
        self.camera = arcade.camera.Camera2D()
        self.speler = Speler()

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        arcade.set_background_color(LUCHT_KLEUR)
        # Reset de speler en start het level
        self.huidig_level = self.start_level
        self.punten = 0
        self.speler.volledig_reset()
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

        # Haal de level-gegevens op uit levels.py
        platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte = levels_module.maak_level(nummer)
        self.platforms = platforms
        self.vijanden = vijanden
        self.powerups = powerups
        self.vlag_x = vlag_x
        self.vlag_y = vlag_y
        self.level_breedte = level_breedte
        self.kogels = []   # Lijst van actieve kogels

        # Bepaal of de speler genoeg punten heeft voor dit bonus-level
        # Toon anders een waarschuwing (gedurende 240 frames = 4 seconden)
        benodigde_punten = {6: 10, 7: 20, 8: 30, 9: 70}
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

            # Teken de vlag
            self._teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de kogels
            for kogel in self.kogels:
                kogel.teken()

            # Teken de speler
            self.speler.teken()

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---

        # Levelnaam altijd bovenin
        naam = LEVEL_NAMEN.get(self.huidig_level, "")
        arcade.draw_text(f"Level {self.huidig_level}: {naam}",
                         10, SCHERM_HOOGTE - 30, arcade.color.WHITE, 16, bold=True)

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

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, (80, 0, 0))
            arcade.draw_text("💀 Game Over! 💀",
                             230, 270, arcade.color.WHITE, 28, bold=True)
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
            arcade.draw_text(f"Level {self.huidig_level} gehaald! 🎉",
                             240, 270, arcade.color.WHITE, 26, bold=True)
            arcade.draw_text("Druk op ENTER om terug naar de kaart te gaan",
                             185, 210, arcade.color.WHITE, 18)
        elif self.dood:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_RED)
            arcade.draw_text("Oeps! Probeer het opnieuw.",
                             195, 270, arcade.color.WHITE, 26, bold=True)
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
        speler_cx = self.speler.x + self.speler.breedte / 2
        for vijand in self.vijanden:
            vijand.bijwerken(speler_cx)

            # Springt de speler van bovenaf op de vijand?
            if (self.speler.snelheid_y < 0 and
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

        # --- Heeft de speler de vlag bereikt? ---
        if (self.speler.x + self.speler.breedte > self.vlag_x and
                self.speler.x < self.vlag_x + 10 and
                self.speler.y < self.vlag_y + 60):
            # Markeer dit level als voltooid (sla op in het bestand)
            self.voltooid = voortgang_module.markeer_level_voltooid(self.huidig_level, self.voltooid)
            if self.huidig_level < AANTAL_LEVELS:
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()  # 🎵 Fanfare!
            else:
                self.gewonnen = True
                geluid_manager.speel_level_gehaald()

    def _voeg_punt_toe(self):
        """Geef de speler 1 punt. Elke 10 punten: sneller én hoger springen!"""
        self.punten += 1
        bonus = self.punten // 10
        self.speler.snelheid_bonus = bonus
        self.speler.sprong_bonus = bonus  # Elke 10 punten ook iets hoger springen

    def _speler_geraakt(self):
        """Verwerk dat de speler geraakt wordt: leven aftrekken of game over."""
        self.speler.levens -= 1
        geluid_manager.speel_geraakt()  # 🎵 Bonk!
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
        elif toets == arcade.key.ENTER or toets == arcade.key.NUM_ENTER:
            # ENTER = ga terug naar de kaart als je het level gehaald hebt
            if self.level_gehaald:
                self._naar_kaart()
        elif toets == arcade.key.R:
            if self.gewonnen:
                self._naar_kaart()                     # Terug naar de kaart na winst
            elif self.game_over:
                # Opnieuw beginnen! Levens en punten worden gereset
                self.punten = 0
                self.speler.volledig_reset()
                self.maak_level(self.huidig_level)
            elif self.dood:
                self.maak_level(self.huidig_level) # Zelfde level opnieuw (levens blijven!)

    def on_key_release(self, toets, modifiers):
        """Wordt aangeroepen als je een toets loslaat."""
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = False

    def _naar_kaart(self):
        """Ga terug naar de levelkaart."""
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        kaart = LevelKaartView(self.voltooid)
        self.window.show_view(kaart)

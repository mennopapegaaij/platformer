# spel.py
# Het hoofdspel — brengt alles samen.
# De PlatformerSpel klasse beheert de game loop: tekenen, bijwerken, toetsen.

import arcade
import levels as levels_module
from instellingen import (SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL,
                           SPRING_KRACHT, LUCHT_KLEUR, VLAG_KLEUR,
                           VLAG_DOEK_KLEUR, LEVEL_NAMEN, AANTAL_LEVELS)
from speler import Speler


class PlatformerSpel(arcade.Window):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self):
        # Maak het venster aan
        super().__init__(SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL)
        arcade.set_background_color(LUCHT_KLEUR)
        # Maak een camera aan die de speler volgt
        self.camera = arcade.camera.Camera2D()
        self.speler = Speler()

    def setup(self):
        """Herstart het spel helemaal vanaf level 1."""
        self.huidig_level = 1
        self.maak_level(1)

    def maak_level(self, nummer):
        """Laad een level op basis van het nummer (1 t/m AANTAL_LEVELS)."""

        # Zet de speler terug naar de beginpositie
        self.speler.reset()

        # Spelstatus resetten
        self.gewonnen = False
        self.dood = False
        self.level_gehaald = False  # Wordt True als de speler de vlag raakt

        # Haal de level-gegevens op uit levels.py
        platforms, vijanden, vlag_x, vlag_y, level_breedte = levels_module.maak_level(nummer)
        self.platforms = platforms
        self.vijanden = vijanden
        self.vlag_x = vlag_x
        self.vlag_y = vlag_y
        self.level_breedte = level_breedte

    def on_draw(self):
        """Teken alles op het scherm."""
        self.clear()

        # --- Teken de spelwereld met de camera ---
        # Alles binnen dit blok beweegt mee met de camera
        with self.camera.activate():

            # Teken alle platforms
            for platform in self.platforms:
                platform.teken()

            # Teken alle vijanden
            for vijand in self.vijanden:
                vijand.teken()

            # Teken de vlag
            self._teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de speler
            self.speler.teken()

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---

        # Levelnaam altijd bovenin
        naam = LEVEL_NAMEN.get(self.huidig_level, "")
        arcade.draw_text(f"Level {self.huidig_level}: {naam}",
                         10, SCHERM_HOOGTE - 30, arcade.color.WHITE, 16, bold=True)

        if self.gewonnen:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_GREEN)
            arcade.draw_text("🎉 Je hebt het hele spel uitgespeeld! 🎉",
                             130, 270, arcade.color.WHITE, 22, bold=True)
            arcade.draw_text("Druk op R om opnieuw te beginnen",
                             220, 210, arcade.color.WHITE, 18)
        elif self.level_gehaald:
            arcade.draw_lrbt_rectangle_filled(100, 700, 160, 340, arcade.color.DARK_BLUE)
            arcade.draw_text(f"Level {self.huidig_level} gehaald! 🎉",
                             240, 270, arcade.color.WHITE, 26, bold=True)
            arcade.draw_text(f"Druk op ENTER voor level {self.huidig_level + 1}",
                             220, 210, arcade.color.WHITE, 18)
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

    def on_update(self, delta_time):
        """Werk het spel bij — dit wordt heel snel herhaald."""

        # Als het spel voorbij is, doe niets meer
        if self.gewonnen or self.dood or self.level_gehaald:
            return

        # Laat de speler bewegen en botsingen controleren
        self.speler.bijwerken(self.level_breedte, self.platforms)

        # Is de speler in een kuil gevallen?
        if self.speler.is_gevallen():
            self.dood = True
            return

        # --- Camera laten meebewegen met de speler ---
        cam_x = self.speler.x + self.speler.breedte / 2
        cam_x = max(SCHERM_BREEDTE / 2, min(cam_x, self.level_breedte - SCHERM_BREEDTE / 2))
        cam_y = SCHERM_HOOGTE / 2
        self.camera.position = cam_x, cam_y

        # --- Vijanden bijwerken en controleren ---
        vijanden_weg = []  # Vijanden die dood zijn, bewaar ze hier
        for vijand in self.vijanden:
            vijand.bijwerken()

            # Springt de speler van bovenaf op de vijand? Dan gaat de vijand dood!
            if (self.speler.snelheid_y < 0 and
                    vijand.speler_springt_erop(self.speler.x, self.speler.y,
                                               self.speler.breedte, self.speler.hoogte)):
                vijanden_weg.append(vijand)                       # Markeer als dood
                self.speler.snelheid_y = SPRING_KRACHT / 2       # Kleine stuiterpons omhoog

            # Raakt de speler de vijand anders (van de zijkant of van onder)? Dan is de speler dood!
            elif vijand.raakt_speler(self.speler.x, self.speler.y,
                                     self.speler.breedte, self.speler.hoogte):
                self.dood = True

        # Verwijder de dode vijanden uit de lijst (nooit tijdens het loopen verwijderen!)
        for vijand in vijanden_weg:
            self.vijanden.remove(vijand)

        # --- Heeft de speler de vlag bereikt? ---
        if (self.speler.x + self.speler.breedte > self.vlag_x and
                self.speler.x < self.vlag_x + 10 and
                self.speler.y < self.vlag_y + 60):
            if self.huidig_level < AANTAL_LEVELS:
                self.level_gehaald = True   # Naar het volgende level!
            else:
                self.gewonnen = True        # Laatste level gehaald — gewonnen!

    def on_key_press(self, toets, modifiers):
        """Wordt aangeroepen als je een toets indrukt."""
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = True
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = True
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            self.speler.spring()
        elif toets == arcade.key.ENTER or toets == arcade.key.NUM_ENTER:
            # ENTER = ga naar het volgende level (als je het huidige level gehaald hebt)
            if self.level_gehaald:
                self.huidig_level += 1
                self.maak_level(self.huidig_level)
        elif toets == arcade.key.R:
            # R = huidig level opnieuw beginnen (of heel het spel als je gewonnen hebt)
            if self.gewonnen:
                self.setup()                       # Na de eindoverwinning: terug naar level 1
            else:
                self.maak_level(self.huidig_level) # Bij dood: zelfde level opnieuw

    def on_key_release(self, toets, modifiers):
        """Wordt aangeroepen als je een toets loslaat."""
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = False

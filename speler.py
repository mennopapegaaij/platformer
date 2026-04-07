# speler.py
# De Speler klasse — alles over het poppetje dat jij bestuurt.

import arcade
from instellingen import (SPELER_SNELHEID, SPRING_KRACHT, ZWAARTEKRACHT,
                           SPELER_KLEUR, OOG_KLEUR)

LEVENS_BEGIN = 3  # Hoeveel levens de speler krijgt bij het begin


class Speler:
    """Het poppetje dat de speler bestuurt: een geel vierkantje met een gezichtje."""

    def __init__(self):
        # Startpositie
        self.x = 50
        self.y = 100
        self.breedte = 32
        self.hoogte = 32

        # Bewegingssnelheid
        self.snelheid_x = 0
        self.snelheid_y = 0

        # Is de speler op de grond? (nodig voor springen)
        self.staat_op_grond = False

        # Welke toetsen zijn ingedrukt?
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

        # --- Levens ---
        self.levens = LEVENS_BEGIN

        # --- Power-up timers (tellen af per frame) ---
        self.onkwetsbaar_timer = 0      # ⭐ Ster: niet geraakt kunnen worden
        self.snelheid_boost_timer = 0   # 💨 Snelheid: dubbel zo snel
        self.dubbel_sprong_timer = 0    # 🦘 Dubbel springen: nog een keer springen
        self.schiet_timer = 0           # 🔫 Schieten: kogels afschieten met Z

        # Heeft de speler zijn extra sprong al gebruikt?
        self.heeft_dubbel_gesprongen = False

        # Richting waar de speler naar kijkt (True = rechts, False = links)
        self.kijkt_rechts = True

        # Extra snelheid en spronghoogte door punten (elke 10 punten = +1)
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

        # Knippercyclus voor als de speler onkwetsbaar is
        self._knippering = 0

    def reset(self):
        """Zet de speler terug naar de beginpositie (bij het opnieuw spelen van een level)."""
        self.x = 50
        self.y = 100
        self.snelheid_x = 0
        self.snelheid_y = 0
        self.staat_op_grond = False
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False
        # Power-up effecten stoppen bij het herstarten
        self.onkwetsbaar_timer = 0
        self.snelheid_boost_timer = 0
        self.dubbel_sprong_timer = 0
        self.schiet_timer = 0
        self.heeft_dubbel_gesprongen = False

    def volledig_reset(self):
        """Reset alles inclusief levens (voor een nieuw spel)."""
        self.reset()
        self.levens = LEVENS_BEGIN
        # Bonussen ook resetten — anders is de speler na game over nog steeds snel
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

    def bijwerken(self, level_breedte, platforms):
        """Beweeg de speler en controleer botsingen met platforms."""

        # Timers aftikken
        if self.onkwetsbaar_timer > 0:
            self.onkwetsbaar_timer -= 1
            self._knippering = (self._knippering + 1) % 6
        if self.snelheid_boost_timer > 0:
            self.snelheid_boost_timer -= 1
        if self.dubbel_sprong_timer > 0:
            self.dubbel_sprong_timer -= 1
            if self.dubbel_sprong_timer == 0:
                self.heeft_dubbel_gesprongen = False
        if self.schiet_timer > 0:
            self.schiet_timer -= 1

        # Bepaal de snelheid: normaal + snelheidsboost power-up + punten-bonus
        snelheid = SPELER_SNELHEID + self.snelheid_bonus
        if self.snelheid_boost_timer > 0:
            snelheid *= 2   # Dubbel bij snelheidsboost power-up

        # Horizontale beweging
        if self.links_ingedrukt:
            self.snelheid_x = -snelheid
            self.kijkt_rechts = False   # Speler kijkt naar links
        elif self.rechts_ingedrukt:
            self.snelheid_x = snelheid
            self.kijkt_rechts = True    # Speler kijkt naar rechts
        else:
            self.snelheid_x = 0

        self.x += self.snelheid_x

        # Niet buiten het level lopen
        if self.x < 0:
            self.x = 0
        if self.x + self.breedte > level_breedte:
            self.x = level_breedte - self.breedte

        # Zwaartekracht
        self.snelheid_y -= ZWAARTEKRACHT
        self.y += self.snelheid_y
        self.staat_op_grond = False

        # Botsingen met platforms
        for platform in platforms:
            # Landen op het platform (van bovenaf)
            if platform.raakt(self.x, self.y, self.breedte, self.hoogte):
                self.y = platform.y + platform.hoogte
                self.snelheid_y = 0
                self.staat_op_grond = True
                self.heeft_dubbel_gesprongen = False  # Op de grond: extra sprong herlaadbaar
            # Hoofd stoot tegen onderkant platform
            elif (self.snelheid_y > 0 and
                  platform.raakt_van_onder(self.x, self.y, self.breedte, self.hoogte)):
                self.y = platform.y - self.hoogte
                self.snelheid_y = 0

    def spring(self):
        """Laat de speler springen — hoger naarmate je meer punten hebt!"""
        sprongkracht = SPRING_KRACHT + self.sprong_bonus
        if self.staat_op_grond:
            self.snelheid_y = sprongkracht
        elif (self.dubbel_sprong_timer > 0 and not self.heeft_dubbel_gesprongen):
            self.snelheid_y = sprongkracht
            self.heeft_dubbel_gesprongen = True

    def is_gevallen(self):
        """Geeft True terug als de speler te ver naar beneden is gevallen."""
        return self.y < -50

    def is_onkwetsbaar(self):
        """Geeft True terug als de speler nu onkwetsbaar is (ster-effect)."""
        return self.onkwetsbaar_timer > 0

    def teken(self):
        """Teken het speler-vierkantje met een gezichtje."""
        # Knipperen als de speler onkwetsbaar is
        if self.onkwetsbaar_timer > 0 and self._knippering < 3:
            return  # Niet tekenen = onzichtbaar in de knippercyclus

        x = self.x
        y = self.y
        w = self.breedte
        h = self.hoogte

        # Lijf (geel, of goudgeel bij snelheidsboost)
        lijf_kleur = (255, 220, 0) if self.snelheid_boost_timer > 0 else SPELER_KLEUR
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, lijf_kleur)

        # Rand: oranje normaal, rood bij dubbel-sprong, lichtblauw bij onkwetsbaar
        if self.onkwetsbaar_timer > 0:
            rand_kleur = arcade.color.YELLOW
        elif self.dubbel_sprong_timer > 0:
            rand_kleur = arcade.color.CYAN
        else:
            rand_kleur = arcade.color.ORANGE
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, rand_kleur, 3)

        # Linker oog
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        # Lachend mondje
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

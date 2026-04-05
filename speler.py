# speler.py
# De Speler klasse — alles over het poppetje dat jij bestuurt.

import arcade
from instellingen import (SPELER_SNELHEID, SPRING_KRACHT, ZWAARTEKRACHT,
                           SPELER_KLEUR, OOG_KLEUR)


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

    def reset(self):
        """Zet de speler terug naar de beginpositie."""
        self.x = 50
        self.y = 100
        self.snelheid_x = 0
        self.snelheid_y = 0
        self.staat_op_grond = False
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

    def bijwerken(self, level_breedte, platforms):
        """Beweeg de speler en controleer botsingen met platforms."""

        # Horizontale beweging
        if self.links_ingedrukt:
            self.snelheid_x = -SPELER_SNELHEID
        elif self.rechts_ingedrukt:
            self.snelheid_x = SPELER_SNELHEID
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
            # Hoofd stoot tegen onderkant platform
            elif (self.snelheid_y > 0 and
                  platform.raakt_van_onder(self.x, self.y, self.breedte, self.hoogte)):
                self.y = platform.y - self.hoogte
                self.snelheid_y = 0

    def spring(self):
        """Laat de speler springen (alleen als hij op de grond staat)."""
        if self.staat_op_grond:
            self.snelheid_y = SPRING_KRACHT

    def is_gevallen(self):
        """Geeft True terug als de speler te ver naar beneden is gevallen."""
        return self.y < -50

    def teken(self):
        """Teken het speler-vierkantje met een gezichtje."""
        x = self.x
        y = self.y
        w = self.breedte
        h = self.hoogte

        # Lijf (geel vierkantje)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, SPELER_KLEUR)
        # Oranje rand
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, arcade.color.ORANGE, 2)
        # Linker oog
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        # Lachend mondje
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

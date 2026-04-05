# De Platformer
# Dit is het hoofdbestand van ons spelletje!

import arcade

# --- Instellingen van het scherm ---
SCHERM_BREEDTE = 800       # Hoe breed het venster is (in pixels)
SCHERM_HOOGTE = 500        # Hoe hoog het venster is (in pixels)
SCHERM_TITEL = "De Platformer"
LEVEL_BREEDTE = 3200       # Hoe breed het hele level is

# --- Instellingen van de speler ---
SPELER_SNELHEID = 4        # Hoe snel de speler beweegt
SPRING_KRACHT = 12         # Hoe hoog de speler springt
ZWAARTEKRACHT = 0.5        # Hoe snel de speler valt

# --- Instellingen van vijanden ---
VIJAND_SNELHEID = 2        # Hoe snel vijanden bewegen

# --- Kleuren ---
LUCHT_KLEUR = arcade.color.SKY_BLUE        # Achtergrondkleur
GROND_KLEUR = arcade.color.DARK_GREEN      # Kleur van platforms
SPELER_KLEUR = arcade.color.YELLOW         # Kleur van het speler-vierkantje
OOG_KLEUR = arcade.color.BLACK             # Kleur van de ogen
VIJAND_KLEUR = arcade.color.RED            # Kleur van vijanden
VLAG_KLEUR = arcade.color.WHITE            # Kleur van de vlaggestok
VLAG_DOEK_KLEUR = arcade.color.GREEN       # Kleur van het vlagdoek


class Platform:
    """Een platform (een stuk grond waar je op kunt staan)."""

    def __init__(self, x, y, breedte, hoogte):
        # Positie en grootte opslaan
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte

    def teken(self):
        # Teken het platform als een groen rechthoek
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y, self.y + self.hoogte,
            GROND_KLEUR
        )
        # Teken een iets lichtere rand bovenop voor een 3D-effect
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y + self.hoogte - 6, self.y + self.hoogte,
            arcade.color.GREEN
        )

    def raakt(self, px, py, pw, ph):
        """Controleer of de speler dit platform raakt van bovenaf."""
        speler_links = px
        speler_rechts = px + pw
        speler_onder = py
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_boven = self.y + self.hoogte

        # De speler staat op het platform als hij van bovenaf landt
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_onder <= platform_boven and
                speler_boven > platform_boven):
            return True
        return False

    def raakt_van_onder(self, px, py, pw, ph):
        """Controleer of de speler met zijn hoofd tegen de onderkant stoot."""
        speler_links = px
        speler_rechts = px + pw
        speler_boven = py + ph
        platform_links = self.x
        platform_rechts = self.x + self.breedte
        platform_onder = self.y  # Onderkant van het platform

        # Hoofd van de speler raakt de onderkant van het platform
        if (speler_rechts > platform_links and
                speler_links < platform_rechts and
                speler_boven >= platform_onder and
                py < platform_onder):
            return True
        return False


class Vijand:
    """Een vijand die heen en weer loopt."""

    def __init__(self, x, y, links_grens, rechts_grens):
        self.x = x            # Huidige x-positie
        self.y = y            # Huidige y-positie
        self.breedte = 30     # Breedte van de vijand
        self.hoogte = 30      # Hoogte van de vijand
        self.snelheid = VIJAND_SNELHEID
        self.links_grens = links_grens    # Tot hier beweegt hij naar links
        self.rechts_grens = rechts_grens  # Tot hier beweegt hij naar rechts

    def bijwerken(self):
        """Beweeg de vijand heen en weer."""
        self.x += self.snelheid

        # Als de vijand een grens bereikt, draai hij om
        if self.x <= self.links_grens or self.x + self.breedte >= self.rechts_grens:
            self.snelheid = -self.snelheid  # Omgekeerde richting

    def teken(self):
        """Teken de vijand als een rood vierkantje met een boos gezicht."""
        # Lijf
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.breedte,
            self.y, self.y + self.hoogte,
            VIJAND_KLEUR
        )
        # Linker oog
        arcade.draw_circle_filled(self.x + 8, self.y + 20, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(self.x + 22, self.y + 20, 4, OOG_KLEUR)
        # Boze wenkbrauwen (twee lijntjes)
        arcade.draw_line(self.x + 4, self.y + 26, self.x + 12, self.y + 23, OOG_KLEUR, 2)
        arcade.draw_line(self.x + 18, self.y + 23, self.x + 26, self.y + 26, OOG_KLEUR, 2)
        # Mond (fronsend)
        arcade.draw_arc_outline(self.x + 15, self.y + 9, 10, 6, OOG_KLEUR, 190, 350, 2)

    def raakt_speler(self, px, py, pw, ph):
        """Controleer of de vijand de speler raakt."""
        return (px < self.x + self.breedte and
                px + pw > self.x and
                py < self.y + self.hoogte and
                py + ph > self.y)

    def speler_springt_erop(self, px, py, pw, ph):
        """Controleer of de speler van bovenaf op de vijand springt."""
        speler_onder = py
        vijand_boven = self.y + self.hoogte
        # De speler springt erop als zijn voeten de bovenkant van de vijand raken
        # en hij van boven komt (niet van de zijkant)
        return (px + pw > self.x + 4 and          # Niet helemaal langs de linkerkant
                px < self.x + self.breedte - 4 and # Niet helemaal langs de rechterkant
                speler_onder <= vijand_boven and
                speler_onder >= vijand_boven - 12)  # Komt van bovenaf


class PlatformerSpel(arcade.Window):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self):
        # Maak het venster aan
        super().__init__(SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL)
        arcade.set_background_color(LUCHT_KLEUR)
        # Maak een camera aan die de speler volgt
        self.camera = arcade.camera.Camera2D()

    def setup(self):
        """Zet het spel klaar (wordt ook gebruikt om opnieuw te starten)."""

        # --- Speler ---
        self.speler_x = 50       # Startpositie links
        self.speler_y = 100      # Startpositie hoogte
        self.speler_breedte = 32
        self.speler_hoogte = 32
        self.speler_snelheid_x = 0    # Beweegt hij nu links of rechts?
        self.speler_snelheid_y = 0    # Beweegt hij nu omhoog of omlaag?
        self.staat_op_grond = False   # Staat de speler op een platform?

        # Bijhouden welke toetsen ingedrukt zijn
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

        # --- Platforms ---
        # De vloer heeft gaten (kuilen) — de speler kan erin vallen!
        # Daarna komen zwevende platforms om over te springen.
        self.platforms = [
            # === Vloer met gaten ===
            Platform(0, 0, 300, 40),       # Startstuk
            Platform(380, 0, 220, 40),     # Na gat 1
            Platform(700, 0, 260, 40),     # Na gat 2
            Platform(1060, 0, 280, 40),    # Na gat 3
            Platform(1440, 0, 260, 40),    # Na gat 4
            Platform(1800, 0, 280, 40),    # Na gat 5
            Platform(2180, 0, 260, 40),    # Na gat 6
            Platform(2540, 0, 660, 40),    # Lang eindstuk (tot x=3200)

            # === Zwevende platforms ===
            Platform(150, 130, 120, 20),   # Section 1
            Platform(310, 170, 90, 20),    # Brug over gat 1
            Platform(500, 140, 120, 20),   # Section 2
            Platform(630, 200, 110, 20),   # Hoog platform section 2
            Platform(810, 160, 120, 20),   # Section 3
            Platform(970, 250, 100, 20),   # Hoog platform section 3
            Platform(1090, 180, 100, 20),  # Section 4
            Platform(1260, 290, 120, 20),  # Hoog platform section 4
            Platform(1350, 190, 90, 20),   # Brug over gat 4
            Platform(1460, 200, 120, 20),  # Section 5
            Platform(1610, 310, 100, 20),  # Heel hoog platform
            Platform(1710, 200, 90, 20),   # Brug over gat 5
            Platform(1820, 160, 120, 20),  # Section 6
            Platform(1980, 290, 100, 20),  # Hoog platform section 6
            Platform(2090, 200, 100, 20),  # Brug over gat 6
            Platform(2260, 310, 120, 20),  # Hoog platform section 7
            Platform(2600, 200, 120, 20),  # Eindstuk platform 1
            Platform(2810, 310, 120, 20),  # Eindstuk platform 2 (hoog)
            Platform(3010, 200, 120, 20),  # Eindstuk platform 3
        ]

        # --- Vijanden ---
        self.vijanden = [
            Vijand(100, 40, 0, 300),          # Section 1 (vloer)
            Vijand(420, 40, 380, 600),         # Section 2 (vloer)
            Vijand(640, 220, 630, 740),        # Hoog platform section 2
            Vijand(830, 40, 700, 960),         # Section 3 (vloer)
            Vijand(1100, 40, 1060, 1340),      # Section 4 (vloer)
            Vijand(1270, 310, 1260, 1380),     # Hoog platform section 4
            Vijand(1500, 40, 1440, 1700),      # Section 5 (vloer)
            Vijand(1840, 40, 1800, 2080),      # Section 6 (vloer)
            Vijand(2300, 40, 2180, 2540),      # Section 7 (vloer)
            Vijand(2620, 220, 2600, 2720),     # Eindstuk platform 1
            Vijand(2700, 40, 2540, 2900),      # Eindstuk (vloer)
            Vijand(3030, 220, 3010, 3130),     # Eindstuk platform 3
        ]

        # --- Vlag (eindpunt) ---
        self.vlag_x = 3150   # Ver aan het einde van het level
        self.vlag_y = 40

        # --- Spelstatus ---
        self.gewonnen = False   # Heeft de speler gewonnen?
        self.dood = False       # Is de speler dood?

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
            self.teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de speler (een geel vierkantje met een gezichtje)
            self.teken_speler()

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---
        if self.gewonnen:
            arcade.draw_lrbt_rectangle_filled(150, 650, 180, 320, arcade.color.DARK_GREEN)
            arcade.draw_text("Je hebt gewonnen! 🎉", 250, 270, arcade.color.WHITE, 28, bold=True)
            arcade.draw_text("Druk op R om opnieuw te spelen", 220, 220, arcade.color.WHITE, 18)
        elif self.dood:
            arcade.draw_lrbt_rectangle_filled(150, 650, 180, 320, arcade.color.DARK_RED)
            arcade.draw_text("Oeps! Probeer het opnieuw.", 195, 270, arcade.color.WHITE, 26, bold=True)
            arcade.draw_text("Druk op R om opnieuw te spelen", 220, 220, arcade.color.WHITE, 18)

    def teken_speler(self):
        """Teken het speler-vierkantje met een gezichtje."""
        x = self.speler_x
        y = self.speler_y
        w = self.speler_breedte
        h = self.speler_hoogte

        # Lijf (geel vierkantje)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, SPELER_KLEUR)
        # Rand eromheen
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, arcade.color.ORANGE, 2)
        # Linker oog
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        # Lachend mondje
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

    def teken_vlag(self, x, y):
        """Teken een vlag op de gegeven positie."""
        # Vlaggestok
        arcade.draw_line(x, y, x, y + 60, VLAG_KLEUR, 3)
        # Vlagdoek (groen driehoekje)
        arcade.draw_triangle_filled(x, y + 60, x + 30, y + 48, x, y + 36, VLAG_DOEK_KLEUR)

    def on_update(self, delta_time):
        """Werk het spel bij — dit wordt heel snel herhaald."""

        # Als het spel voorbij is, doe niets
        if self.gewonnen or self.dood:
            return

        # --- Beweeg de speler horizontaal ---
        if self.links_ingedrukt:
            self.speler_snelheid_x = -SPELER_SNELHEID
        elif self.rechts_ingedrukt:
            self.speler_snelheid_x = SPELER_SNELHEID
        else:
            self.speler_snelheid_x = 0  # Stop als er geen toets ingedrukt is

        self.speler_x += self.speler_snelheid_x

        # Zorg dat de speler niet links uit het level loopt
        if self.speler_x < 0:
            self.speler_x = 0
        # En niet rechts voorbij het einde van het level
        if self.speler_x + self.speler_breedte > LEVEL_BREEDTE:
            self.speler_x = LEVEL_BREEDTE - self.speler_breedte

        # --- Zwaartekracht ---
        self.speler_snelheid_y -= ZWAARTEKRACHT  # Trek de speler omlaag
        self.speler_y += self.speler_snelheid_y
        self.staat_op_grond = False

        # --- Botsing met platforms ---
        for platform in self.platforms:
            # Landen op het platform (van bovenaf)
            if platform.raakt(self.speler_x, self.speler_y,
                              self.speler_breedte, self.speler_hoogte):
                # Zet de speler precies op het platform
                self.speler_y = platform.y + platform.hoogte
                self.speler_snelheid_y = 0
                self.staat_op_grond = True
            # Hoofd stoot tegen de onderkant (van onderaf springen)
            elif (self.speler_snelheid_y > 0 and
                  platform.raakt_van_onder(self.speler_x, self.speler_y,
                                           self.speler_breedte, self.speler_hoogte)):
                # Stoot hoofd — zet de speler net onder het platform en laat vallen
                self.speler_y = platform.y - self.speler_hoogte
                self.speler_snelheid_y = 0

        # --- Valt de speler in een kuil? ---
        if self.speler_y < -50:
            self.dood = True  # Gevallen — spel voorbij!

        # --- Camera laten meebewegen met de speler ---
        # Zorg dat de camera niet buiten het level kijkt
        cam_x = self.speler_x + self.speler_breedte / 2
        cam_x = max(SCHERM_BREEDTE / 2, min(cam_x, LEVEL_BREEDTE - SCHERM_BREEDTE / 2))
        cam_y = SCHERM_HOOGTE / 2  # Verticaal blijft de camera op dezelfde hoogte
        self.camera.position = cam_x, cam_y

        # --- Vijanden bijwerken en controleren ---
        vijanden_weg = []  # Lijst van vijanden die dood zijn
        for vijand in self.vijanden:
            vijand.bijwerken()

            # Springt de speler van bovenaf op de vijand? Dan gaat de vijand dood!
            if (self.speler_snelheid_y < 0 and
                    vijand.speler_springt_erop(self.speler_x, self.speler_y,
                                               self.speler_breedte, self.speler_hoogte)):
                vijanden_weg.append(vijand)          # Markeer vijand als dood
                self.speler_snelheid_y = SPRING_KRACHT / 2  # Kleine stuiterpons omhoog

            # Raakt de speler de vijand van de zijkant of van onder? Dan is de speler dood!
            elif vijand.raakt_speler(self.speler_x, self.speler_y,
                                     self.speler_breedte, self.speler_hoogte):
                self.dood = True

        # Verwijder de dode vijanden uit de lijst
        for vijand in vijanden_weg:
            self.vijanden.remove(vijand)

        # --- Heeft de speler de vlag bereikt? ---
        if (self.speler_x + self.speler_breedte > self.vlag_x and
                self.speler_x < self.vlag_x + 10 and
                self.speler_y < self.vlag_y + 60):
            self.gewonnen = True  # Vlag bereikt — gewonnen!

    def on_key_press(self, toets, modifiers):
        """Wordt aangeroepen als je een toets indrukt."""
        if toets == arcade.key.LEFT:
            self.links_ingedrukt = True
        elif toets == arcade.key.RIGHT:
            self.rechts_ingedrukt = True
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            # Springen mag alleen als de speler op de grond staat
            if self.staat_op_grond:
                self.speler_snelheid_y = SPRING_KRACHT
        elif toets == arcade.key.R:
            # R = opnieuw beginnen
            self.setup()

    def on_key_release(self, toets, modifiers):
        """Wordt aangeroepen als je een toets loslaat."""
        if toets == arcade.key.LEFT:
            self.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.rechts_ingedrukt = False


# --- Start het spel ---
def main():
    spel = PlatformerSpel()   # Maak het spel aan
    spel.setup()              # Zet alles klaar
    arcade.run()              # Start de game loop


# Dit zorgt ervoor dat het spel alleen start als je dit bestand rechtstreeks uitvoert
if __name__ == "__main__":
    main()


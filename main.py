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

    def __init__(self, x, y, links_grens, rechts_grens, snelheid=VIJAND_SNELHEID):
        self.x = x            # Huidige x-positie
        self.y = y            # Huidige y-positie
        self.breedte = 30     # Breedte van de vijand
        self.hoogte = 30      # Hoogte van de vijand
        self.snelheid = snelheid
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
        """Herstart het spel helemaal vanaf level 1."""
        self.huidig_level = 1
        self.maak_level(1)

    def maak_level(self, nummer):
        """Laad een level op basis van het nummer (1 t/m 5)."""

        # --- Speler terug naar beginpositie ---
        self.speler_x = 50
        self.speler_y = 100
        self.speler_breedte = 32
        self.speler_hoogte = 32
        self.speler_snelheid_x = 0
        self.speler_snelheid_y = 0
        self.staat_op_grond = False
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

        # --- Spelstatus ---
        self.gewonnen = False
        self.dood = False
        self.level_gehaald = False   # Wordt True als de speler de vlag raakt

        # =============================================
        # LEVEL 1: De Beginners Wereld
        # Makkelijk — kleine gaten, trage vijanden
        # =============================================
        if nummer == 1:
            self.level_breedte = 2000
            self.platforms = [
                Platform(0, 0, 350, 40),
                Platform(430, 0, 270, 40),
                Platform(800, 0, 300, 40),
                Platform(1220, 0, 780, 40),
                Platform(150, 130, 120, 20),
                Platform(350, 160, 100, 20),
                Platform(470, 150, 120, 20),
                Platform(630, 200, 100, 20),
                Platform(710, 160, 100, 20),
                Platform(840, 150, 120, 20),
                Platform(1000, 220, 100, 20),
                Platform(1110, 170, 100, 20),
                Platform(1280, 180, 120, 20),
                Platform(1550, 200, 120, 20),
                Platform(1800, 180, 120, 20),
            ]
            self.vijanden = [
                Vijand(100, 40, 0, 350, 2),
                Vijand(500, 40, 430, 700, 2),
                Vijand(870, 40, 800, 1100, 2),
                Vijand(1400, 40, 1220, 1900, 2),
            ]
            self.vlag_x = 1950
            self.vlag_y = 40

        # =============================================
        # LEVEL 2: Het Bos
        # Iets moeilijker — bredere gaten, meer vijanden
        # =============================================
        elif nummer == 2:
            self.level_breedte = 2400
            self.platforms = [
                Platform(0, 0, 300, 40),
                Platform(420, 0, 260, 40),
                Platform(800, 0, 280, 40),
                Platform(1220, 0, 260, 40),
                Platform(1620, 0, 780, 40),
                Platform(130, 150, 100, 20),
                Platform(310, 190, 100, 20),
                Platform(450, 160, 110, 20),
                Platform(580, 280, 90, 20),
                Platform(700, 200, 100, 20),
                Platform(830, 170, 100, 20),
                Platform(970, 300, 90, 20),
                Platform(1100, 200, 100, 20),
                Platform(1250, 180, 100, 20),
                Platform(1390, 300, 90, 20),
                Platform(1500, 200, 100, 20),
                Platform(1680, 200, 100, 20),
                Platform(1900, 280, 100, 20),
                Platform(2200, 200, 100, 20),
            ]
            self.vijanden = [
                Vijand(100, 40, 0, 300, 2.5),
                Vijand(460, 40, 420, 680, 2.5),
                Vijand(590, 300, 580, 660, 2.5),
                Vijand(850, 40, 800, 1080, 2.5),
                Vijand(1280, 40, 1220, 1480, 2.5),
                Vijand(1700, 40, 1620, 2300, 2.5),
            ]
            self.vlag_x = 2350
            self.vlag_y = 40

        # =============================================
        # LEVEL 3: De Bergen
        # Middel — hogere platforms, snellere vijanden
        # =============================================
        elif nummer == 3:
            self.level_breedte = 2800
            self.platforms = [
                Platform(0, 0, 280, 40),
                Platform(440, 0, 260, 40),
                Platform(870, 0, 260, 40),
                Platform(1300, 0, 250, 40),
                Platform(1720, 0, 260, 40),
                Platform(2160, 0, 640, 40),
                Platform(100, 160, 90, 20),
                Platform(290, 210, 90, 20),
                Platform(460, 170, 90, 20),
                Platform(580, 300, 80, 20),
                Platform(710, 220, 90, 20),
                Platform(890, 170, 90, 20),
                Platform(1010, 310, 80, 20),
                Platform(1140, 220, 90, 20),
                Platform(1320, 190, 90, 20),
                Platform(1430, 320, 80, 20),
                Platform(1560, 220, 90, 20),
                Platform(1740, 190, 90, 20),
                Platform(1860, 330, 80, 20),
                Platform(1990, 220, 90, 20),
                Platform(2200, 220, 90, 20),
                Platform(2450, 300, 90, 20),
                Platform(2650, 220, 90, 20),
            ]
            self.vijanden = [
                Vijand(100, 40, 0, 280, 3),
                Vijand(470, 40, 440, 700, 3),
                Vijand(590, 320, 580, 660, 3),
                Vijand(910, 40, 870, 1130, 3),
                Vijand(1020, 330, 1010, 1090, 3),
                Vijand(1340, 40, 1300, 1550, 3),
                Vijand(1760, 40, 1720, 1980, 3),
                Vijand(2200, 40, 2160, 2700, 3),
            ]
            self.vlag_x = 2750
            self.vlag_y = 40

        # =============================================
        # LEVEL 4: Het Kasteel
        # Moeilijk — smalle platforms, veel vijanden
        # =============================================
        elif nummer == 4:
            self.level_breedte = 3200
            self.platforms = [
                Platform(0, 0, 260, 40),
                Platform(440, 0, 240, 40),
                Platform(870, 0, 240, 40),
                Platform(1300, 0, 230, 40),
                Platform(1720, 0, 230, 40),
                Platform(2140, 0, 230, 40),
                Platform(2560, 0, 640, 40),
                Platform(80, 170, 80, 20),
                Platform(270, 220, 80, 20),
                Platform(460, 180, 80, 20),
                Platform(560, 330, 80, 20),
                Platform(700, 230, 80, 20),
                Platform(890, 180, 80, 20),
                Platform(1000, 340, 80, 20),
                Platform(1120, 230, 80, 20),
                Platform(1320, 200, 80, 20),
                Platform(1420, 340, 80, 20),
                Platform(1540, 230, 80, 20),
                Platform(1740, 200, 80, 20),
                Platform(1840, 340, 80, 20),
                Platform(1960, 230, 80, 20),
                Platform(2160, 200, 80, 20),
                Platform(2270, 340, 80, 20),
                Platform(2380, 230, 80, 20),
                Platform(2590, 210, 80, 20),
                Platform(2800, 320, 80, 20),
                Platform(3050, 220, 80, 20),
            ]
            self.vijanden = [
                Vijand(80, 40, 0, 260, 3.5),
                Vijand(470, 40, 440, 680, 3.5),
                Vijand(570, 350, 560, 630, 3.5),
                Vijand(900, 40, 870, 1110, 3.5),
                Vijand(1010, 360, 1000, 1080, 3.5),
                Vijand(1330, 40, 1300, 1530, 3.5),
                Vijand(1750, 40, 1720, 1950, 3.5),
                Vijand(1850, 360, 1840, 1920, 3.5),
                Vijand(2170, 40, 2140, 2370, 3.5),
                Vijand(2600, 40, 2560, 3100, 3.5),
            ]
            self.vlag_x = 3150
            self.vlag_y = 40

        # =============================================
        # LEVEL 5: De Eindbaas
        # Heel moeilijk — grote gaten, razendsnelle vijanden
        # =============================================
        elif nummer == 5:
            self.level_breedte = 3600
            self.platforms = [
                Platform(0, 0, 240, 40),
                Platform(450, 0, 220, 40),
                Platform(890, 0, 220, 40),
                Platform(1330, 0, 210, 40),
                Platform(1760, 0, 210, 40),
                Platform(2190, 0, 210, 40),
                Platform(2620, 0, 210, 40),
                Platform(3040, 0, 560, 40),
                Platform(70, 180, 70, 20),
                Platform(260, 230, 70, 20),
                Platform(470, 190, 70, 20),
                Platform(590, 350, 70, 20),
                Platform(710, 250, 70, 20),
                Platform(910, 190, 70, 20),
                Platform(1030, 360, 70, 20),
                Platform(1140, 250, 70, 20),
                Platform(1350, 210, 70, 20),
                Platform(1460, 360, 70, 20),
                Platform(1560, 250, 70, 20),
                Platform(1780, 210, 70, 20),
                Platform(1890, 360, 70, 20),
                Platform(1980, 250, 70, 20),
                Platform(2210, 210, 70, 20),
                Platform(2320, 360, 70, 20),
                Platform(2410, 250, 70, 20),
                Platform(2640, 210, 70, 20),
                Platform(2760, 360, 70, 20),
                Platform(2840, 250, 70, 20),
                Platform(3060, 230, 70, 20),
                Platform(3300, 340, 70, 20),
                Platform(3530, 230, 70, 20),
            ]
            self.vijanden = [
                Vijand(70, 40, 0, 240, 4),
                Vijand(480, 40, 450, 670, 4),
                Vijand(600, 370, 590, 660, 4),
                Vijand(920, 40, 890, 1110, 4),
                Vijand(1040, 380, 1030, 1100, 4),
                Vijand(1360, 40, 1330, 1540, 4),
                Vijand(1470, 380, 1460, 1530, 4),
                Vijand(1790, 40, 1760, 1970, 4),
                Vijand(1900, 380, 1890, 1960, 4),
                Vijand(2220, 40, 2190, 2400, 4),
                Vijand(2650, 40, 2620, 2830, 4),
                Vijand(2770, 380, 2760, 2830, 4),
                Vijand(3070, 40, 3040, 3500, 4),
            ]
            self.vlag_x = 3560
            self.vlag_y = 40

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

        # Levelnummer altijd bovenin
        level_namen = {
            1: "De Beginners Wereld", 2: "Het Bos",
            3: "De Bergen", 4: "Het Kasteel", 5: "De Eindbaas"
        }
        naam = level_namen.get(self.huidig_level, "")
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
        if self.gewonnen or self.dood or self.level_gehaald:
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
        if self.speler_x + self.speler_breedte > self.level_breedte:
            self.speler_x = self.level_breedte - self.speler_breedte

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
        cam_x = max(SCHERM_BREEDTE / 2, min(cam_x, self.level_breedte - SCHERM_BREEDTE / 2))
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
            if self.huidig_level < 5:
                self.level_gehaald = True   # Naar het volgende level!
            else:
                self.gewonnen = True        # Laatste level gehaald — gewonnen!

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


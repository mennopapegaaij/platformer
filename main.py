# De Platformer
# Dit is het hoofdbestand van ons spelletje!

import arcade

# --- Instellingen van het scherm ---
SCHERM_BREEDTE = 800       # Hoe breed het venster is (in pixels)
SCHERM_HOOGTE = 500        # Hoe hoog het venster is (in pixels)
SCHERM_TITEL = "De Platformer"

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


class PlatformerSpel(arcade.Window):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self):
        # Maak het venster aan
        super().__init__(SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL)
        arcade.set_background_color(LUCHT_KLEUR)

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
        # (x, y, breedte, hoogte) — de vloer en zwevende platforms
        self.platforms = [
            Platform(0, 0, 800, 40),       # De vloer van het level
            Platform(150, 120, 120, 20),   # Een platform links
            Platform(330, 200, 120, 20),   # Een platform in het midden
            Platform(520, 140, 120, 20),   # Een platform rechts
            Platform(680, 260, 120, 20),   # Een hoog platform rechts
        ]

        # --- Kuilen ---
        # Dit zijn gaten in de vloer. We verwijderen een deel van de vloer
        # en slagen de kuilen op als gevaarlijke zones.
        # Een speler die hieronder komt, begint opnieuw.
        self.kuilen = [
            (260, 360),   # Gat van x=260 tot x=360
            (460, 530),   # Gat van x=460 tot x=530
        ]

        # Verwijder stukken van de vloer voor de kuilen
        self.platforms = [
            Platform(0, 0, 255, 40),       # Vloer voor gat 1
            Platform(365, 0, 90, 40),      # Vloer tussen gat 1 en 2
            Platform(535, 0, 265, 40),     # Vloer na gat 2
            Platform(150, 120, 120, 20),   # Platform 1
            Platform(330, 200, 120, 20),   # Platform 2
            Platform(520, 140, 120, 20),   # Platform 3
            Platform(680, 260, 120, 20),   # Platform 4
        ]

        # --- Vijanden ---
        self.vijanden = [
            Vijand(160, 40, 150, 270),    # Vijand op eerste stuk vloer
            Vijand(370, 40, 365, 455),    # Vijand op middelste stuk vloer
            Vijand(340, 220, 330, 450),   # Vijand op platform 2
        ]

        # --- Vlag (eindpunt) ---
        self.vlag_x = 750    # Positie van de vlag
        self.vlag_y = 40     # Op de vloer (na gat 2)

        # --- Spelstatus ---
        self.gewonnen = False   # Heeft de speler gewonnen?
        self.dood = False       # Is de speler dood?

    def on_draw(self):
        """Teken alles op het scherm."""
        self.clear()

        # Teken alle platforms
        for platform in self.platforms:
            platform.teken()

        # Teken de kuilen (donkerblauwe gaten)
        for (links, rechts) in self.kuilen:
            arcade.draw_lrbt_rectangle_filled(links, rechts, 0, 40, arcade.color.DARK_BLUE)

        # Teken alle vijanden
        for vijand in self.vijanden:
            vijand.teken()

        # Teken de vlag
        self.teken_vlag(self.vlag_x, self.vlag_y)

        # Teken de speler (een geel vierkantje met een gezichtje)
        self.teken_speler()

        # Toon een bericht als de speler heeft gewonnen of verloren
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

        # Zorg dat de speler niet uit het scherm loopt
        if self.speler_x < 0:
            self.speler_x = 0
        if self.speler_x + self.speler_breedte > SCHERM_BREEDTE:
            self.speler_x = SCHERM_BREEDTE - self.speler_breedte

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
        midden_x = self.speler_x + self.speler_breedte / 2
        if self.speler_y < -50:
            self.dood = True  # Gevallen — spel voorbij!
        else:
            # Controleer ook of de speler boven een kuil staat zonder platform
            for (links, rechts) in self.kuilen:
                if links < midden_x < rechts and self.speler_y < 5:
                    self.dood = True

        # --- Vijanden bijwerken en controleren ---
        for vijand in self.vijanden:
            vijand.bijwerken()
            if vijand.raakt_speler(self.speler_x, self.speler_y,
                                   self.speler_breedte, self.speler_hoogte):
                self.dood = True  # Vijand geraakt — spel voorbij!

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


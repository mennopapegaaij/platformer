# instellingen.py
# Alle instellingen van het spel op één plek.
# Wil je iets aanpassen? Dan doe je dat hier!

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
VIJAND_SNELHEID = 2        # Standaard snelheid van vijanden

# --- Kleuren ---
LUCHT_KLEUR = arcade.color.SKY_BLUE        # Achtergrondkleur
GROND_KLEUR = arcade.color.DARK_GREEN      # Kleur van platforms
SPELER_KLEUR = arcade.color.YELLOW         # Kleur van het speler-vierkantje
OOG_KLEUR = arcade.color.BLACK             # Kleur van de ogen
VIJAND_KLEUR = arcade.color.RED            # Kleur van vijanden
VLAG_KLEUR = arcade.color.WHITE            # Kleur van de vlaggestok
VLAG_DOEK_KLEUR = arcade.color.GREEN       # Kleur van het vlagdoek

# --- Namen van de levels ---
LEVEL_NAMEN = {
    1: "De Beginners Wereld",
    2: "Het Bos",
    3: "De Bergen",
    4: "Het Kasteel",
    5: "De Eindbaas",
    6: "De Snelheids Tempel",
    7: "De Wolken",
    8: "Het Ultieme Dak",
}

# --- Aantal levels in het spel ---
AANTAL_LEVELS = 8

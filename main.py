# main.py
# Start het spel!
# Dit is het enige bestand dat je hoeft te starten.

import arcade
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL
from geluid import geluid as geluid_manager
from levelkaart import LevelKaartView
import voortgang

def main():
    # Maak het venster aan
    window = arcade.Window(SCHERM_BREEDTE, SCHERM_HOOGTE, SCHERM_TITEL)
    # Laad alle geluiden (één keer aan het begin)
    geluid_manager.laad_alles()
    # Laad de opgeslagen voortgang
    voltooid = voortgang.laad_voortgang()
    # Laat de levelkaart zien
    kaart = LevelKaartView(voltooid)
    window.show_view(kaart)
    arcade.run()              # Start de game loop

# Dit zorgt ervoor dat het spel alleen start als je dit bestand rechtstreeks uitvoert
if __name__ == "__main__":
    main()

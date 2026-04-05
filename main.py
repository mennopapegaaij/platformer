# main.py
# Start het spel!
# Dit is het enige bestand dat je hoeft te starten.

import arcade
from spel import PlatformerSpel

def main():
    spel = PlatformerSpel()   # Maak het spel aan
    spel.setup()              # Zet alles klaar
    arcade.run()              # Start de game loop

# Dit zorgt ervoor dat het spel alleen start als je dit bestand rechtstreeks uitvoert
if __name__ == "__main__":
    main()

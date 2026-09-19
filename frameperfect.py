# frameperfect.py
# De FRAME PERFECT-kamer. De baan past zich aan aan je gekozen poppetje, zodat het
# voor ELK poppetje moeilijk MAAR haalbaar is:
#  - Spring-poppetjes: grond-spikes, over te halen met een perfecte sprong.
#  - Vliegers: een strak tunneltje (grond-spikes onder, plafond-spikes boven).
#  - Zwaargewicht: minder spikes (want het springt laag).
#  - Boemerang: spikes vlak bij de start (het elastiek trekt je terug).
#  - Klimmer: een klim-schacht (twee muren) naar een vlag bovenin.

from platforms import Platform, BlokPlatform
from vijand import Spikes

# Vliegers met een strak tunneltje
SMOOTH_TUNNEL = {"vliegtuig", "ballon", "raket", "draak", "golf"}
# Flappers met een iets ruimer tunneltje
FLAP_TUNNEL = {"ufo", "kolibrie"}
# Alle poppetjes zijn nu speelbaar in de Frame Perfect-kamer
FRAME_POPPETJES = None   # None = alles mag


def frameperfect_baan(modus):
    """Geef (leveldata, plafond, snelheid_bonus) voor dit poppetje."""
    acht = [(0, 8)]

    # --- Klimmer: een klim-schacht met twee muren, vlag bovenin ---
    if modus == "klimmer":
        platforms = [
            Platform(0, 0, 760, 40),               # aanloop
            BlokPlatform(760, 40, 40, 420),        # linker muur van de schacht
            BlokPlatform(880, 40, 40, 420),        # rechter muur van de schacht
            Platform(800, 470, 80, 40),            # richel bovenin bij de vlag
        ]
        data = (platforms, [], [], 830, 490, 1000, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Boemerang: het elastiek trekt je terug, dus spikes + vlag dicht bij de start ---
    if modus == "boemerang":
        platforms = [Platform(0, 0, 500, 40)]
        vijanden = [Spikes(150, 40, aantal=1)]
        data = (platforms, vijanden, [], 230, 40, 500, [], [], [], [], acht, [], [], [])
        return data, None, 6

    platforms = [Platform(0, 0, 1400, 40)]

    # --- Vliegers: strak tunneltje ---
    if modus in SMOOTH_TUNNEL:
        vijanden = [Spikes(760, 40, aantal=5), Spikes(760, 100, aantal=5, rotatie=180)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, 130, 1
    if modus in FLAP_TUNNEL:
        vijanden = [Spikes(760, 40, aantal=5), Spikes(760, 130, aantal=5, rotatie=180)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, 160, 1

    # --- Zwaargewicht: springt laag, dus 2 spikes en iets meer snelheid ---
    if modus == "zwaargewicht":
        vijanden = [Spikes(740, 40, aantal=2)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 3

    # --- Groeier: spikes vroeg, want hij wordt al lopend steeds groter ---
    if modus == "groeier":
        vijanden = [Spikes(150, 40, aantal=5)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Flits: teleporteert per blok, dus wat minder spikes ---
    if modus == "flits":
        vijanden = [Spikes(700, 40, aantal=3)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Stuiteraar: stuitert vanzelf; spikes op een plek waar de stuiter eroverheen komt ---
    if modus == "stuiteraar":
        vijanden = [Spikes(610, 40, aantal=5)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Alle andere (spring-)poppetjes: 5 grond-spikes ---
    vijanden = [Spikes(700, 40, aantal=5)]
    data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
    return data, None, 1


def maak_frameperfect(modus=None):
    """Alleen de leveldata (voor terugval-compatibiliteit)."""
    return frameperfect_baan(modus)[0]

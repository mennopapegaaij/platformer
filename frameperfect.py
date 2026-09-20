# frameperfect.py
# De FRAME PERFECT-kamer. De baan past zich aan aan je gekozen poppetje, zodat het
# voor ELK poppetje moeilijk MAAR haalbaar is.

from platforms import Platform, BlokPlatform
from vijand import Spikes

# Alle poppetjes zijn speelbaar in de Frame Perfect-kamer
FRAME_POPPETJES = None   # None = alles mag

# Vlieg-poppetjes: een tunneltje (grond-spikes onder + plafond-spikes boven).
# modus -> (hoogte plafond-spikes, onzichtbaar plafond)
TUNNEL = {
    "vliegtuig": (100, 130), "ballon": (100, 130), "raket": (100, 130),
    "draak": (100, 130), "golf": (100, 130),
    "ufo": (130, 160), "kolibrie": (130, 160),
    "heli": (110, 140), "dronken": (150, 180),
}

# Sommige springers springen hoog/ver, dus die krijgen MEER spikes (anders te makkelijk)
AANTAL_PER_MODUS = {
    "ninja": 7, "versneller": 13, "turbo": 9, "dobbelsteen": 7,
    "zweefspringer": 16, "wind": 6,
}


def frameperfect_baan(modus):
    """Geef (leveldata, plafond, snelheid_bonus) voor dit poppetje."""
    acht = [(0, 8)]

    # --- Klimmer: een klim-schacht met twee muren, vlag bovenin ---
    if modus == "klimmer":
        platforms = [
            Platform(0, 0, 760, 40),
            BlokPlatform(760, 40, 40, 420),
            BlokPlatform(880, 40, 40, 420),
            Platform(800, 470, 80, 40),
        ]
        data = (platforms, [], [], 830, 490, 1000, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Boemerang: het elastiek trekt je terug, dus spikes + vlag dicht bij de start ---
    if modus == "boemerang":
        platforms = [Platform(0, 0, 500, 40)]
        vijanden = [Spikes(150, 40, aantal=1)]
        data = (platforms, vijanden, [], 230, 40, 500, [], [], [], [], acht, [], [], [])
        return data, None, 6

    # --- Bal & spin: een zwaartekracht-gang (vloer + plafond, spikes op allebei).
    #     Je moet op tijd van de vloer naar het plafond en weer terug wisselen. ---
    if modus in ("bal", "spin"):
        platforms = [Platform(0, 0, 1400, 40), Platform(0, 300, 1400, 40)]
        vijanden = [Spikes(600, 40, aantal=4),                 # vloer-spikes: wees op het plafond
                    Spikes(900, 255, aantal=4, rotatie=180)]   # plafond-spikes: wees op de vloer
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Vlieg-poppetjes: een tunneltje ---
    if modus in TUNNEL:
        cy, plaf = TUNNEL[modus]
        platforms = [Platform(0, 0, 1400, 40)]
        vijanden = [Spikes(760, 40, aantal=5), Spikes(760, cy, aantal=5, rotatie=180)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, plaf, 1

    # --- Zwaargewicht: springt laag, dus 2 spikes en iets meer snelheid ---
    if modus == "zwaargewicht":
        platforms = [Platform(0, 0, 1400, 40)]
        vijanden = [Spikes(740, 40, aantal=2)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 3

    # --- Groeier: spikes vroeg, want hij wordt al lopend steeds groter ---
    if modus == "groeier":
        platforms = [Platform(0, 0, 1400, 40)]
        vijanden = [Spikes(150, 40, aantal=5)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Flits: teleporteert per blok, dus wat minder spikes ---
    if modus == "flits":
        platforms = [Platform(0, 0, 1400, 40)]
        vijanden = [Spikes(700, 40, aantal=3)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Stuiteraar: stuitert vanzelf; spikes op een plek waar de stuiter eroverheen komt ---
    if modus == "stuiteraar":
        platforms = [Platform(0, 0, 1400, 40)]
        vijanden = [Spikes(610, 40, aantal=5)]
        data = (platforms, vijanden, [], 1250, 40, 1400, [], [], [], [], acht, [], [], [])
        return data, None, 1

    # --- Alle andere (spring-)poppetjes: grond-spikes (aantal past bij het poppetje) ---
    aantal = AANTAL_PER_MODUS.get(modus, 5)
    sx = 700
    eind = sx + aantal * 40
    vlag_x = eind + 120
    breedte = vlag_x + 200
    platforms = [Platform(0, 0, breedte, 40)]
    vijanden = [Spikes(sx, 40, aantal=aantal)]
    data = (platforms, vijanden, [], vlag_x, 40, breedte, [], [], [], [], acht, [], [], [])
    return data, None, 1


def maak_frameperfect(modus=None):
    """Alleen de leveldata (voor terugval-compatibiliteit)."""
    return frameperfect_baan(modus)[0]

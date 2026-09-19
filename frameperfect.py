# frameperfect.py
# De FRAME PERFECT-kamer: een pittige race-baan (je rent vanzelf naar rechts)
# waar je precies op het juiste moment moet springen. Kies eerst een poppetje!

from platforms import Platform, BlokPlatform
from vijand import maak_spike


def maak_frameperfect():
    """Bouw de leveldata (14 onderdelen) voor de frame-perfect race-baan."""
    # Grond in stukjes met gaten ertussen (over de gaten moet je springen)
    platforms = [
        Platform(0, 0, 440, 40),
        Platform(540, 0, 320, 40),
        Platform(960, 0, 360, 40),
        Platform(1420, 0, 320, 40),
        Platform(1840, 0, 360, 40),
        Platform(2300, 0, 260, 40),
        Platform(2660, 0, 500, 40),
        BlokPlatform(1180, 40, 40, 40),   # een bultje om overheen te springen
        BlokPlatform(2420, 40, 40, 40),   # nog een bultje
    ]
    # Spikes die je precies op tijd moet ontwijken
    vijanden = [
        maak_spike("gewoon", 700, 40),
        maak_spike("gewoon", 1080, 40),
        maak_spike("dubbel", 1520, 40),
        maak_spike("gewoon", 1980, 40),
        maak_spike("gewoon", 2720, 40),
    ]
    powerups = []
    vlag_x, vlag_y = 3050, 40           # de finish helemaal rechts
    level_breedte = 3200
    acht_zones = [(0, 8)]               # ruimte-achtergrond (donker, spannend)
    return (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte,
            [], [], [], [], acht_zones, [], [], [])

# frameperfect.py
# De FRAME PERFECT-kamer: je rent vanzelf naar rechts en moet met ÉÉN perfect
# getimede sprong over 5 spikes naast elkaar springen. Te vroeg of te laat = raak!

from platforms import Platform
from vijand import Spikes


def maak_frameperfect():
    """Bouw de leveldata (14 onderdelen): een aanloop, 5 spikes en dan de finish."""
    platforms = [
        Platform(0, 0, 1500, 40),          # één lange grond (aanloop + landing)
    ]
    # 5 spikes vlak naast elkaar (één groep van 5) -> samen 200 breed
    vijanden = [Spikes(700, 40, aantal=5)]
    powerups = []
    vlag_x, vlag_y = 1350, 40              # de finish net na de spikes
    level_breedte = 1600
    acht_zones = [(0, 8)]                  # ruimte-achtergrond (spannend!)
    return (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte,
            [], [], [], [], acht_zones, [], [], [])

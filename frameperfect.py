# frameperfect.py
# De FRAME PERFECT-kamer: je rent vanzelf naar rechts en moet met ÉÉN perfect
# getimede sprong over 5 spikes naast elkaar.
#  - Spring-poppetjes: precies op tijd springen (venster van ~2 frames!).
#  - Vlieg-poppetjes: er is een onzichtbaar plafond (zie FRAME_PLAFOND in spel.py),
#    dus je kunt er niet bovenlangs cheesen — je moet in een strakke baan blijven.

from platforms import Platform
from vijand import Spikes


def maak_frameperfect():
    """Bouw de leveldata (14 onderdelen): een aanloop, 5 spikes en dan de finish."""
    platforms = [
        Platform(0, 0, 1700, 40),          # één lange grond (aanloop + landing)
    ]
    vijanden = [
        Spikes(700, 40, aantal=5),                    # 5 grond-spikes: hier precies OMHOOG
        Spikes(1050, 70, aantal=5, rotatie=180),      # 5 plafond-spikes: hier precies OMLAAG
    ]
    powerups = []
    vlag_x, vlag_y = 1450, 40              # de finish na beide hindernissen
    level_breedte = 1700
    acht_zones = [(0, 8)]                  # ruimte-achtergrond (spannend!)
    return (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte,
            [], [], [], [], acht_zones, [], [], [])

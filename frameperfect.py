# frameperfect.py
# De FRAME PERFECT-kamer. De baan past zich aan aan je gekozen poppetje:
#  - SPRING-poppetjes: 5 grond-spikes, over te halen met ÉÉN perfecte sprong.
#  - GLADDE VLIEGERS: een piepklein tunneltje (grond-spikes onder, plafond-spikes
#    boven) waar je precies omhoog het gaatje in en er precies doorheen moet vliegen.
#  - FLAPPERS (ufo/kolibrie): hetzelfde tunneltje, maar iets ruimer.

from platforms import Platform
from vijand import Spikes

# Welke poppetjes krijgen het strakke vlieg-tunneltje
SMOOTH_TUNNEL = {"vliegtuig", "ballon", "raket", "draak", "golf"}
FLAP_TUNNEL = {"ufo", "kolibrie"}


def maak_frameperfect(modus=None):
    """Bouw de leveldata (14 onderdelen), passend bij het gekozen poppetje."""
    platforms = [Platform(0, 0, 1500, 40)]
    if modus in SMOOTH_TUNNEL:
        # Strak tunneltje: grond-spikes ONDER en plafond-spikes BOVEN, klein gaatje
        vijanden = [Spikes(760, 40, aantal=5),
                    Spikes(760, 100, aantal=5, rotatie=180)]
    elif modus in FLAP_TUNNEL:
        # Iets ruimer tunneltje voor de flappers
        vijanden = [Spikes(760, 40, aantal=5),
                    Spikes(760, 130, aantal=5, rotatie=180)]
    else:
        # Spring-poppetjes: 5 grond-spikes, één perfecte sprong
        vijanden = [Spikes(700, 40, aantal=5)]
    vlag_x, vlag_y = 1250, 40
    level_breedte = 1400
    acht_zones = [(0, 8)]                  # ruimte-achtergrond
    return (platforms, vijanden, [], vlag_x, vlag_y, level_breedte,
            [], [], [], [], acht_zones, [], [], [])

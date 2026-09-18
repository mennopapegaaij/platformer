# testruimte.py
# Een speelkamer om ALLES te testen: grond, trapjes, muren om te klimmen,
# een stuiterblok, een bewegend platform en een spike. Wissel van poppetje met N.

from platforms import Platform, BlokPlatform, StuiterBlok, BewegendBlok
from vijand import maak_spike
from decoratie import TekstBord


def maak_testruimte():
    """Bouw de leveldata (14 onderdelen) voor de testruimte."""
    platforms = [
        Platform(0, 0, 2600, 40),                 # lange grond om op te lopen
        BlokPlatform(300, 40, 80, 40),            # trapje 1
        BlokPlatform(380, 80, 80, 40),            # trapje 2 (hoger)
        StuiterBlok(560, 40, 40, 40),             # stuiterblok (springt je omhoog)
        BlokPlatform(820, 40, 40, 260),           # muur A
        BlokPlatform(980, 40, 40, 260),           # muur B (klim ertussen: ninja/klimmer/plakker)
        BewegendBlok(1200, 140, 100, 30, "vert",  # bewegend platform (op en neer)
                     afstand=120, snelheid=2),
        BlokPlatform(1500, 40, 40, 40),           # los blokje
        BlokPlatform(1560, 40, 40, 40),           # en nog een (om overheen te springen)
    ]
    vijanden = [maak_spike("gewoon", 1750, 40)]   # één spike om botsingen te testen
    powerups = []
    borden = [
        TekstBord(120, 40, "Test alles hier!  N = ander poppetje"),
        TekstBord(560, 90, "Stuiterblok"),
        TekstBord(860, 300, "Klim tussen de muren"),
        TekstBord(1200, 280, "Bewegend platform"),
        TekstBord(1750, 90, "Spike (pas op!)"),
    ]
    vlag_x, vlag_y = 2500, 40                      # de finish staat helemaal rechts
    level_breedte = 2600
    acht_zones = [(0, 7)]                          # lichtblauwe wolkenlucht
    return (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte,
            [], [], [], [], acht_zones, [], borden, [])

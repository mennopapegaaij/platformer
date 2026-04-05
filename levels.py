# levels.py
# Alle level-gegevens op één plek.
# Wil je een nieuw level toevoegen? Voeg hier een nieuw blok toe!

from platforms import Platform
from vijand import Vijand
from powerup import SterPowerUp, SnelheidPowerUp, DubbelSprongPowerUp, ExtraLevenPowerUp


def maak_level(nummer):
    """
    Geeft de gegevens voor een level terug.
    nummer = 1 t/m 5

    Geeft terug: (platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte)
    """

    # =============================================
    # LEVEL 1: De Beginners Wereld
    # Makkelijk — kleine gaten, trage vijanden
    # =============================================
    if nummer == 1:
        level_breedte = 2000
        platforms = [
            Platform(0, 0, 350, 40),
            Platform(430, 0, 270, 40),
            Platform(800, 0, 300, 40),
            Platform(1220, 0, 780, 40),
            Platform(150, 130, 120, 20),
            Platform(350, 160, 100, 20),
            Platform(470, 150, 120, 20),
            Platform(630, 200, 100, 20),
            Platform(710, 160, 100, 20),
            Platform(840, 150, 120, 20),
            Platform(1000, 220, 100, 20),
            Platform(1110, 170, 100, 20),
            Platform(1280, 180, 120, 20),
            Platform(1550, 200, 120, 20),
            Platform(1800, 180, 120, 20),
        ]
        vijanden = [
            Vijand(100, 40, 0, 350, 2),
            Vijand(500, 40, 430, 700, 2),
            Vijand(870, 40, 800, 1100, 2),
            Vijand(1400, 40, 1220, 1900, 2),
        ]
        vlag_x = 1950
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(200, 152),        # Op het eerste hoge platform
            SterPowerUp(660, 222),              # Op het platform op hoogte 200
            SnelheidPowerUp(1030, 242),         # Op een hoog platform halverwege
            DubbelSprongPowerUp(1580, 222),     # Bijna aan het einde
        ]
    # Iets moeilijker — bredere gaten, meer vijanden
    # =============================================
    elif nummer == 2:
        level_breedte = 2400
        platforms = [
            Platform(0, 0, 300, 40),
            Platform(420, 0, 260, 40),
            Platform(800, 0, 280, 40),
            Platform(1220, 0, 260, 40),
            Platform(1620, 0, 780, 40),
            Platform(130, 150, 100, 20),
            Platform(310, 190, 100, 20),
            Platform(450, 160, 110, 20),
            Platform(580, 280, 90, 20),
            Platform(700, 200, 100, 20),
            Platform(830, 170, 100, 20),
            Platform(970, 300, 90, 20),
            Platform(1100, 200, 100, 20),
            Platform(1250, 180, 100, 20),
            Platform(1390, 300, 90, 20),
            Platform(1500, 200, 100, 20),
            Platform(1680, 200, 100, 20),
            Platform(1900, 280, 100, 20),
            Platform(2200, 200, 100, 20),
        ]
        vijanden = [
            Vijand(100, 40, 0, 300, 2.5),
            Vijand(460, 40, 420, 680, 2.5),
            Vijand(590, 300, 580, 660, 2.5),
            Vijand(850, 40, 800, 1080, 2.5),
            Vijand(1280, 40, 1220, 1480, 2.5),
            Vijand(1700, 40, 1620, 2300, 2.5),
        ]
        vlag_x = 2350
        vlag_y = 40
        powerups = [
            SnelheidPowerUp(160, 172),          # Op hoog platform in het bos
            DubbelSprongPowerUp(600, 302),      # Op een hoog platform midden
            SterPowerUp(1130, 222),             # Halverwege het level
            ExtraLevenPowerUp(1920, 302),       # Bijna aan het einde, hoog
        ]

    # =============================================
    # LEVEL 3: De Bergen
    # Middel — hogere platforms, snellere vijanden
    # =============================================
    elif nummer == 3:
        level_breedte = 2800
        platforms = [
            Platform(0, 0, 280, 40),
            Platform(440, 0, 260, 40),
            Platform(870, 0, 260, 40),
            Platform(1300, 0, 250, 40),
            Platform(1720, 0, 260, 40),
            Platform(2160, 0, 640, 40),
            Platform(100, 160, 90, 20),
            Platform(290, 210, 90, 20),
            Platform(460, 170, 90, 20),
            Platform(580, 300, 80, 20),
            Platform(710, 220, 90, 20),
            Platform(890, 170, 90, 20),
            Platform(1010, 310, 80, 20),
            Platform(1140, 220, 90, 20),
            Platform(1320, 190, 90, 20),
            Platform(1430, 320, 80, 20),
            Platform(1560, 220, 90, 20),
            Platform(1740, 190, 90, 20),
            Platform(1860, 330, 80, 20),
            Platform(1990, 220, 90, 20),
            Platform(2200, 220, 90, 20),
            Platform(2450, 300, 90, 20),
            Platform(2650, 220, 90, 20),
        ]
        vijanden = [
            Vijand(100, 40, 0, 280, 3),
            Vijand(470, 40, 440, 700, 3),
            Vijand(590, 320, 580, 660, 3),
            Vijand(910, 40, 870, 1130, 3),
            Vijand(1020, 330, 1010, 1090, 3),
            Vijand(1340, 40, 1300, 1550, 3),
            Vijand(1760, 40, 1720, 1980, 3),
            Vijand(2200, 40, 2160, 2700, 3),
        ]
        vlag_x = 2750
        vlag_y = 40
        powerups = [
            DubbelSprongPowerUp(120, 182),      # Op eerste hoge platform
            ExtraLevenPowerUp(1040, 332),       # Op hoog platform midden-links
            SterPowerUp(1580, 242),             # Gevaarlijk punt: ster helpt!
            SnelheidPowerUp(2470, 322),         # Bijna aan het einde
        ]
    # Moeilijk — smalle platforms, veel vijanden
    # =============================================
    elif nummer == 4:
        level_breedte = 3200
        platforms = [
            Platform(0, 0, 260, 40),
            Platform(440, 0, 240, 40),
            Platform(870, 0, 240, 40),
            Platform(1300, 0, 230, 40),
            Platform(1720, 0, 230, 40),
            Platform(2140, 0, 230, 40),
            Platform(2560, 0, 640, 40),
            Platform(80, 170, 80, 20),
            Platform(270, 220, 80, 20),
            Platform(460, 180, 80, 20),
            Platform(560, 330, 80, 20),
            Platform(700, 230, 80, 20),
            Platform(890, 180, 80, 20),
            Platform(1000, 340, 80, 20),
            Platform(1120, 230, 80, 20),
            Platform(1320, 200, 80, 20),
            Platform(1420, 340, 80, 20),
            Platform(1540, 230, 80, 20),
            Platform(1740, 200, 80, 20),
            Platform(1840, 340, 80, 20),
            Platform(1960, 230, 80, 20),
            Platform(2160, 200, 80, 20),
            Platform(2270, 340, 80, 20),
            Platform(2380, 230, 80, 20),
            Platform(2590, 210, 80, 20),
            Platform(2800, 320, 80, 20),
            Platform(3050, 220, 80, 20),
        ]
        vijanden = [
            Vijand(80, 40, 0, 260, 3.5),
            Vijand(470, 40, 440, 680, 3.5),
            Vijand(570, 350, 560, 630, 3.5),
            Vijand(900, 40, 870, 1110, 3.5),
            Vijand(1010, 360, 1000, 1080, 3.5),
            Vijand(1330, 40, 1300, 1530, 3.5),
            Vijand(1750, 40, 1720, 1950, 3.5),
            Vijand(1850, 360, 1840, 1920, 3.5),
            Vijand(2170, 40, 2140, 2370, 3.5),
            Vijand(2600, 40, 2560, 3100, 3.5),
        ]
        vlag_x = 3150
        vlag_y = 40
        powerups = [
            SterPowerUp(100, 192),              # Direct aan het begin — nodig!
            DubbelSprongPowerUp(580, 352),      # Op een hoog platform
            ExtraLevenPowerUp(1450, 362),       # Halverwege, beloont moed
            SnelheidPowerUp(2300, 362),         # In het moeilijke stuk
            SterPowerUp(2830, 342),             # Laatste stuk: extra ster
        ]
    # Heel moeilijk — grote gaten, razendsnelle vijanden
    # =============================================
    elif nummer == 5:
        level_breedte = 3600
        platforms = [
            Platform(0, 0, 240, 40),
            Platform(450, 0, 220, 40),
            Platform(890, 0, 220, 40),
            Platform(1330, 0, 210, 40),
            Platform(1760, 0, 210, 40),
            Platform(2190, 0, 210, 40),
            Platform(2620, 0, 210, 40),
            Platform(3040, 0, 560, 40),
            Platform(70, 180, 70, 20),
            Platform(260, 230, 70, 20),
            Platform(470, 190, 70, 20),
            Platform(590, 350, 70, 20),
            Platform(710, 250, 70, 20),
            Platform(910, 190, 70, 20),
            Platform(1030, 360, 70, 20),
            Platform(1140, 250, 70, 20),
            Platform(1350, 210, 70, 20),
            Platform(1460, 360, 70, 20),
            Platform(1560, 250, 70, 20),
            Platform(1780, 210, 70, 20),
            Platform(1890, 360, 70, 20),
            Platform(1980, 250, 70, 20),
            Platform(2210, 210, 70, 20),
            Platform(2320, 360, 70, 20),
            Platform(2410, 250, 70, 20),
            Platform(2640, 210, 70, 20),
            Platform(2760, 360, 70, 20),
            Platform(2840, 250, 70, 20),
            Platform(3060, 230, 70, 20),
            Platform(3300, 340, 70, 20),
            Platform(3530, 230, 70, 20),
        ]
        vijanden = [
            Vijand(70, 40, 0, 240, 4),
            Vijand(480, 40, 450, 670, 4),
            Vijand(600, 370, 590, 660, 4),
            Vijand(920, 40, 890, 1110, 4),
            Vijand(1040, 380, 1030, 1100, 4),
            Vijand(1360, 40, 1330, 1540, 4),
            Vijand(1470, 380, 1460, 1530, 4),
            Vijand(1790, 40, 1760, 1970, 4),
            Vijand(1900, 380, 1890, 1960, 4),
            Vijand(2220, 40, 2190, 2400, 4),
            Vijand(2650, 40, 2620, 2830, 4),
            Vijand(2770, 380, 2760, 2830, 4),
            Vijand(3070, 40, 3040, 3500, 4),
        ]
        vlag_x = 3560
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(100, 202),        # Eerste platform — extra leven!
            SterPowerUp(620, 372),              # Gevaarlijk stuk, ster helpt
            DubbelSprongPowerUp(1170, 272),     # Halverwege
            SnelheidPowerUp(1810, 232),         # Hoog platform
            ExtraLevenPowerUp(2340, 382),       # Bijna eindbaas
            SterPowerUp(2870, 382),             # Laatste kans voor de vlag!
        ]

    else:
        # Onbekend levelnummer — geef lege data terug
        level_breedte = 800
        platforms = []
        vijanden = []
        powerups = []
        vlag_x = 700
        vlag_y = 40

    return platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte

# levels.py
# Alle level-gegevens op één plek.
# Wil je een nieuw level toevoegen? Voeg hier een nieuw blok toe!

import random  # nodig om automatisch oneindige levels te maken
import math    # voor het uitrekenen van de sprong-afstanden
from platforms import Platform, BlokPlatform
from vijand import (Vijand, VliegendVijand, SpringendVijand, GroteVijand, GeestVijand,
                    JagerVijand, EindBaas,
                    SlijmVijand, StekelVijand, VuurVijand, IJsVijand, BomVijand,
                    VleermuisVijand, SlangVijand, RobotVijand, KraaiVijand, PaddenstoelVijand,
                    ArenaBaas, ArenaVechter, Spikes)
from powerup import ExtraLevenPowerUp
from portaal import Portaal


def maak_level(nummer):
    """
    Geeft de gegevens voor een level terug.
    nummer = 1 t/m 9 zijn handgemaakte levels.
    nummer = 10 of hoger worden AUTOMATISCH gemaakt (oneindig veel levels!).

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
            # Nieuwe vijanden: vliegend en springend als kennismaking
            VliegendVijand(600, 120, 430, 800, 2.5),    # 🐝 Vliegt boven het gat
            SpringendVijand(1300, 40, 1220, 1500, 1.5), # 🐸 Springende kikker
        ]
        vlag_x = 1950
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(200, 152),        # Op het eerste hoge platform
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
            # Nieuwe vijanden: geest zweeft door het bos, grote vijand verspert de weg
            GeestVijand(700, 160, 580, 1000, 2),     # 👻 Geest zweeft door het bos
            GroteVijand(1500, 40, 1400, 1700, 1.5),  # 💜 Grote vijand midden in het bos
        ]
        vlag_x = 2350
        vlag_y = 40
        powerups = [
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
            # Nieuwe vijanden: vos jaagt, bij vliegt over de bergen
            JagerVijand(600, 40, 440, 870, 3),          # 🦊 Jager in het bergdal
            VliegendVijand(1200, 150, 1000, 1600, 3),   # 🐝 Bij vliegt over bergtop
            SpringendVijand(2000, 40, 1720, 2160, 2.5), # 🐸 Kikker op breed plateau
        ]
        vlag_x = 2750
        vlag_y = 40
        powerups = []      # In dit level geen power-ups
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
            # Nieuwe vijanden: grote schildwacht, jager en geest
            GroteVijand(500, 40, 440, 800, 2),           # 💜 Grote schildwacht bij ingang
            JagerVijand(1200, 40, 1000, 1400, 4),        # 🦊 Snelle jager in kasteel
            GeestVijand(2000, 200, 1840, 2400, 3),       # 👻 Geest zweeft door kasteel
            VliegendVijand(2700, 160, 2560, 3000, 3.5),  # 🐝 Bij bewaakt de doorgang
        ]
        vlag_x = 3150
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(1450, 362),       # Halverwege, beloont moed
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
            # Eindbaas heeft ALLE nieuwe vijandtypen!
            GroteVijand(300, 40, 0, 450, 2.5),           # 💜 Grote schildwacht
            VliegendVijand(750, 180, 450, 1000, 4),      # 🐝 Snelle bij
            SpringendVijand(1200, 40, 1100, 1400, 3),    # 🐸 Springkikker
            GeestVijand(1700, 220, 1460, 2000, 3.5),     # 👻 Zweefgeest
            JagerVijand(2500, 40, 2400, 2700, 5),        # 🦊 Razendsnelle jager
            GroteVijand(3200, 40, 3040, 3500, 3),        # 💜 Grote eindbaas!
        ]
        vlag_x = 3560
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(100, 202),        # Eerste platform — extra leven!
            ExtraLevenPowerUp(2340, 382),       # Bijna eindbaas
        ]

    # =============================================
    # LEVEL 6: De Snelheids Tempel
    # Je hebt minimaal 10 punten nodig (snelheidsbonus +1)!
    # De gaten zijn 205px breed — zonder bonus kun je er NIET overheen springen.
    # Verslaan van monsters geeft je punten én meer snelheid.
    # =============================================
    elif nummer == 6:
        level_breedte = 3200
        platforms = [
            # Grond-eilanden met brede gaten (205-210px — minimum +1 bonus nodig!)
            Platform(0, 0, 260, 40),
            Platform(465, 0, 225, 40),      # gat: 205px
            Platform(895, 0, 225, 40),      # gat: 205px
            Platform(1325, 0, 225, 40),     # gat: 205px
            Platform(1755, 0, 225, 40),     # gat: 205px
            Platform(2185, 0, 225, 40),     # gat: 210px
            Platform(2620, 0, 580, 40),     # gat: 210px → eindzone

            # Verhoogde platforms (top=210px) — net bereikbaar met +1 sprong
            # Dienen als tussenstap om gaten makkelijker over te komen
            Platform(290, 190, 80, 20),
            Platform(400, 190, 80, 20),
            Platform(720, 190, 80, 20),
            Platform(830, 190, 80, 20),
            Platform(1150, 190, 80, 20),
            Platform(1260, 190, 80, 20),
            Platform(1580, 190, 80, 20),
            Platform(1690, 190, 80, 20),
            Platform(2010, 190, 80, 20),
            Platform(2120, 190, 80, 20),
            Platform(2440, 190, 80, 20),
            Platform(2550, 190, 80, 20),
        ]
        vijanden = [
            # Veel monsters — verslaan ze voor extra punten en snelheid!
            Vijand(50, 40, 0, 260, 3),
            Vijand(520, 40, 465, 690, 3),
            JagerVijand(570, 40, 465, 690, 3),
            Vijand(950, 40, 895, 1120, 3),
            JagerVijand(1000, 40, 895, 1120, 3.5),
            Vijand(1380, 40, 1325, 1550, 3),
            JagerVijand(1430, 40, 1325, 1550, 3.5),
            Vijand(1810, 40, 1755, 1980, 3.5),
            VliegendVijand(1850, 150, 1755, 1980, 3),
            Vijand(2240, 40, 2185, 2410, 3.5),
            VliegendVijand(2280, 150, 2185, 2410, 3),
            GroteVijand(2700, 40, 2620, 3100, 2.5),
            JagerVijand(2800, 40, 2620, 3100, 4),
        ]
        vlag_x = 3150
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(720, 212),        # Op verhoogd platform
        ]

    # =============================================
    # LEVEL 7: De Wolken
    # Je hebt minimaal 20 punten nodig (snelheidsbonus +2)!
    # Gaten van 275px EN platforms op y=220 — zonder +2 kom je er NIET doorheen.
    # =============================================
    elif nummer == 7:
        level_breedte = 3600
        platforms = [
            # Grond-eilanden met gaten van 275px (niet te overbruggen zonder +2!)
            Platform(0, 0, 260, 40),
            Platform(535, 0, 220, 40),      # gat: 275px
            Platform(1030, 0, 220, 40),     # gat: 275px
            Platform(1525, 0, 220, 40),     # gat: 275px
            Platform(2020, 0, 220, 40),     # gat: 275px
            Platform(2520, 0, 220, 40),     # gat: 280px
            Platform(3020, 0, 580, 40),     # gat: 280px

            # Hoge wolken-platforms (y=220, top=240 — net bereikbaar met +2 bonus)
            Platform(270, 220, 80, 20),
            Platform(400, 220, 80, 20),
            Platform(760, 220, 80, 20),
            Platform(890, 220, 80, 20),
            Platform(1255, 220, 80, 20),
            Platform(1385, 220, 80, 20),
            Platform(1755, 220, 80, 20),
            Platform(1880, 220, 80, 20),
            Platform(2250, 220, 80, 20),
            Platform(2380, 220, 80, 20),
            Platform(2750, 220, 80, 20),
            Platform(2880, 220, 80, 20),

            # Extra lage tussenplatforms voor afwisseling
            Platform(310, 130, 60, 20),
            Platform(800, 130, 60, 20),
            Platform(1300, 130, 60, 20),
            Platform(1800, 130, 60, 20),
        ]
        vijanden = [
            Vijand(100, 40, 0, 260, 4),
            VliegendVijand(600, 120, 535, 755, 3.5),
            JagerVijand(650, 40, 535, 755, 4),
            SpringendVijand(700, 40, 535, 755, 3),
            VliegendVijand(1100, 120, 1030, 1250, 3.5),
            JagerVijand(1150, 40, 1030, 1250, 4.5),
            GeestVijand(1300, 200, 1250, 1530, 3.5),
            VliegendVijand(1600, 120, 1525, 1745, 4),
            JagerVijand(1650, 40, 1525, 1745, 4.5),
            SpringendVijand(1700, 40, 1525, 1745, 3.5),
            GroteVijand(2100, 40, 2020, 2240, 3),
            VliegendVijand(2150, 150, 2020, 2240, 4),
            JagerVijand(2600, 40, 2520, 2740, 5),
            GeestVijand(2700, 200, 2520, 2740, 4),
            GroteVijand(3100, 40, 3020, 3500, 3.5),
            JagerVijand(3200, 40, 3020, 3500, 5),
        ]
        vlag_x = 3550
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(310, 152),        # Op tussenplatform
            ExtraLevenPowerUp(2250, 242),       # Bijna eindbaas
        ]

    # =============================================
    # LEVEL 8: Het Ultieme Dak
    # Je hebt minimaal 30 punten nodig (snelheidsbonus +3)!
    # Gaten van 345px EN platforms op y=250 — het zwaarste level van het spel!
    # =============================================
    elif nummer == 8:
        level_breedte = 4000
        platforms = [
            # Grond-eilanden met gaten van 345-360px (onmogelijk zonder +3!)
            Platform(0, 0, 280, 40),
            Platform(625, 0, 220, 40),      # gat: 345px
            Platform(1195, 0, 220, 40),     # gat: 350px
            Platform(1765, 0, 220, 40),     # gat: 350px
            Platform(2340, 0, 220, 40),     # gat: 355px
            Platform(2920, 0, 220, 40),     # gat: 360px
            Platform(3500, 0, 500, 40),     # gat: 360px

            # Extreme hoge platforms (y=250, top=270 — bereikbaar met +3 bonus)
            Platform(300, 250, 70, 20),
            Platform(430, 250, 70, 20),
            Platform(870, 250, 70, 20),
            Platform(1000, 250, 70, 20),
            Platform(1440, 250, 70, 20),
            Platform(1570, 250, 70, 20),
            Platform(2015, 250, 70, 20),
            Platform(2145, 250, 70, 20),
            Platform(2590, 250, 70, 20),
            Platform(2720, 250, 70, 20),
            Platform(3165, 250, 70, 20),
            Platform(3295, 250, 70, 20),

            # Tussenstap platforms op twee hoogtes
            Platform(330, 140, 60, 20),
            Platform(880, 140, 60, 20),
            Platform(1450, 140, 60, 20),
            Platform(2025, 140, 60, 20),
            Platform(2600, 140, 60, 20),
            Platform(3175, 140, 60, 20),
        ]
        vijanden = [
            # Alle vijandtypen — zo snel en gevaarlijk mogelijk!
            Vijand(80, 40, 0, 280, 5),
            GroteVijand(160, 40, 0, 280, 3),
            JagerVijand(700, 40, 625, 845, 5.5),
            VliegendVijand(750, 150, 625, 845, 4.5),
            SpringendVijand(800, 40, 625, 845, 4),
            JagerVijand(1270, 40, 1195, 1415, 5.5),
            GeestVijand(1350, 220, 1195, 1415, 4.5),
            GroteVijand(1300, 40, 1195, 1415, 3.5),
            JagerVijand(1840, 40, 1765, 1985, 6),
            VliegendVijand(1900, 180, 1765, 1985, 5),
            SpringendVijand(1950, 40, 1765, 1985, 4.5),
            JagerVijand(2420, 40, 2340, 2560, 6),
            GeestVijand(2480, 220, 2340, 2560, 5),
            GroteVijand(2460, 40, 2340, 2560, 4),
            JagerVijand(3010, 40, 2920, 3140, 6),
            VliegendVijand(3060, 180, 2920, 3140, 5),
            GroteVijand(3050, 40, 2920, 3140, 4),
            # Eindbaas-groep!
            GroteVijand(3600, 40, 3500, 3900, 4),
            JagerVijand(3700, 40, 3500, 3900, 6.5),
            GeestVijand(3750, 220, 3500, 3900, 5),
            VliegendVijand(3800, 200, 3500, 3900, 5),
        ]
        vlag_x = 3960
        vlag_y = 40
        powerups = [
            ExtraLevenPowerUp(330, 162),        # Op tussenstap platform
            ExtraLevenPowerUp(1440, 162),       # Bijna halverwege
            ExtraLevenPowerUp(3500, 62),        # Net voor de eindbaas-groep
        ]

    # =============================================
    # LEVEL 9: De Grote Achtervolging
    # Je hebt minimaal 70 punten nodig (snelheidsbonus +7, snelheid=11)!
    # De eindbaas heeft snelheid 11 — je moet hem inhalen en 3x stompen!
    # =============================================
    elif nummer == 9:
        level_breedte = 99999
        platforms = [
            Platform(0, 0, 99999, 40),
        ]

        # Herhalende platforms voor variatie
        hoogtes = [130, 160, 200, 130, 170, 150, 190, 160]
        for i in range(200):
            x = 300 + i * 400
            hoogte = hoogtes[i % len(hoogtes)]
            platforms.append(Platform(x, hoogte, 120, 20))
            if i % 2 == 0:
                platforms.append(Platform(x + 180, hoogte + 80, 100, 20))

        # De eindbaas kan ver weglopen maar binnen deze grote grenzen
        vijanden = [
            EindBaas(1400, 40, 100, 99900),
        ]
        # Geen vlag — versla de eindbaas om te winnen!
        vlag_x = -999
        vlag_y = -999
        powerups = []

    else:
        # Level 10 of hoger: laat de computer automatisch een nieuw level maken!
        return _genereer_oneindig_level(nummer)

    return platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte


def _genereer_oneindig_level(nummer):
    """Maak automatisch een level voor nummer 10, 11, 12, ... (oneindig veel!).

    Hoe hoger het nummer, hoe moeilijker: breder, meer vijanden en sneller.
    Met random.Random(nummer) krijgt elk levelnummer ALTIJD hetzelfde level,
    ook als je hetzelfde level nog een keer speelt. Handig én eerlijk!
    """
    # Een eigen 'dobbelsteen' die altijd dezelfde worp geeft bij hetzelfde nummer
    rng = random.Random(nummer)
    trap = nummer - 9                      # 1 bij level 10, 2 bij level 11, enz.

    # Breedte loopt op (met een MAXIMUM zodat het spel niet gaat haperen)
    level_breedte = min(2600 + trap * 250, 5000)  # breder, maar nooit gigantisch groot

    if nummer >= 11:
        # === LEVEL 11 EN HOGER: BIJNA ONMOGELIJK (maar wél te halen!) ===
        extra = nummer - 10                              # 1 bij level 11, 2 bij 12...
        basis_snelheid = min(6.0 + extra * 0.25, 9.0)    # razendsnelle vijanden!
        vijanden_per_eiland = min(3 + extra // 2, 5)     # heel veel vijanden
        kans_lucht = 0.45                                # ook veel vliegende vijanden
        moeilijk = True
    else:
        # === Level 10: een rustige opwarmer ===
        basis_snelheid = min(2.5 + trap * 0.15, 6.0)     # vijanden worden sneller (max 6)
        vijanden_per_eiland = min(1 + trap // 3, 3)      # rustig aantal vijanden
        kans_lucht = 0.35
        moeilijk = False

    platforms = []
    vijanden = []
    powerups = []

    # --- 1. De grond: eilandjes met gaten ertussen ---
    eilanden = []                          # onthoud elk eiland als (start_x, breedte)
    x = 0
    while x < level_breedte - 500:
        breedte = rng.randint(230, 340)
        platforms.append(Platform(x, 0, breedte, 40))
        eilanden.append((x, breedte))
        gat = rng.randint(120, 170)        # zo'n gat kun je makkelijk overspringen
        x += breedte + gat

    # Groot eindeiland waar de vlag op komt te staan
    eind_start = x
    eind_breedte = max(400, level_breedte - x)
    platforms.append(Platform(eind_start, 0, eind_breedte, 40))
    eilanden.append((eind_start, eind_breedte))

    # --- 2. Zwevende platforms om op te springen ---
    for (ex, ebr) in eilanden:
        if rng.random() < 0.7:             # niet op elk eiland eentje
            hoogte = rng.choice([130, 160, 190, 220])
            pw = rng.randint(80, 120)
            speelruimte = max(10, ebr - pw - 20)
            px = ex + rng.randint(10, speelruimte)
            platforms.append(Platform(px, hoogte, pw, 20))

    # --- 3. Vijanden (niet op het start-eiland, wel op de rest) ---
    grond_soorten = [Vijand, SpringendVijand, JagerVijand, GroteVijand,
                     SlijmVijand, StekelVijand, IJsVijand, BomVijand,
                     SlangVijand, RobotVijand, PaddenstoelVijand]
    lucht_soorten = [VliegendVijand, GeestVijand,
                     VuurVijand, VleermuisVijand, KraaiVijand]
    for (ex, ebr) in eilanden[1:-1]:       # sla het start- en eindeiland over
        for _ in range(vijanden_per_eiland):
            links = ex + 10
            rechts = ex + ebr - 10
            start_x = rng.randint(links, rechts)
            if rng.random() < kans_lucht:
                # Een vliegende of zwevende vijand, hoog in de lucht
                soort = rng.choice(lucht_soorten)
                y = rng.choice([130, 160, 190])
            else:
                # Een vijand die over de grond loopt
                soort = rng.choice(grond_soorten)
                y = 40
            snelheid = round(basis_snelheid + rng.uniform(-0.3, 0.6), 1)
            vijanden.append(soort(start_x, y, links, rechts, snelheid))

    # Veiligheid: nooit te veel vijanden, anders gaat het spel haperen
    if len(vijanden) > 45:
        vijanden = vijanden[:45]

    # --- Spikes: scherpe punten waar je OVERHEEN moet springen (niet te doden) ---
    for (ex, ebr) in eilanden[1:-1]:        # niet op het start- en eindeiland
        if rng.random() < 0.4:
            aantal_punten = rng.randint(2, 4)
            sw = aantal_punten * 16
            sx = ex + rng.randint(30, max(30, ebr - sw - 30))
            vijanden.append(Spikes(sx, 40, aantal_punten))

    # --- 4. Power-ups op sommige zwevende platforms (alleen nog hartjes!) ---
    zwevend = [p for p in platforms if p.y > 40]   # alleen de hoge platforms
    rng.shuffle(zwevend)
    if moeilijk:
        # In zware levels: meer hartjes zodat je meer levens hebt om te overleven
        aantal_powerups = min(5 + extra, len(zwevend))
    else:
        aantal_powerups = min(3 + trap // 2, len(zwevend))
    for p in zwevend[:aantal_powerups]:
        powerups.append(ExtraLevenPowerUp(p.x + p.breedte // 2 - 10, p.y + 22))

    # --- 5. De vlag helemaal aan het einde ---
    vlag_x = eind_start + eind_breedte - 60
    vlag_y = 40

    # BELANGRIJK: maak de levelbreedte precies zo groot als het eindeiland.
    # Anders staat er een onzichtbare muur vóór de vlag en kun je er niet bij!
    level_breedte = eind_start + eind_breedte

    return platforms, vijanden, powerups, vlag_x, vlag_y, level_breedte


# =================================================================
# VECHTMODUS (ARENA)
# Aparte levels waar je ALLE monsters moet verslaan om te winnen.
# Begint heel makkelijk en wordt steeds moeilijker. Elke 10 levels
# een eindbaas met speciale krachten! Oneindig veel levels.
# =================================================================
def maak_arena(nummer):
    """Maak een vecht-level (arena) voor de vechtmodus.

    Je wint door alle monsters te verslaan (er is geen vlag).
    nummer 1 = supermakkelijk, daarna steeds moeilijker.
    Elke 10e level (10, 20, 30, ...) is een eindbaas met speciale krachten.
    """
    ARENA_BREEDTE = 1100
    rng = random.Random(1000 + nummer)   # eigen deterministische reeks

    # De vloer (geen gaten!) + een paar zwevende platforms om op te springen
    platforms = [
        Platform(0, 0, ARENA_BREEDTE, 40),
        Platform(180, 150, 120, 20),
        Platform(490, 210, 120, 20),
        Platform(800, 150, 120, 20),
    ]
    vijanden = []
    powerups = []
    links, rechts = 40, ARENA_BREEDTE - 40

    if nummer % 10 == 0:
        # ===== EINDBAAS-LEVEL =====
        # Alleen de eindbaas mag extra beesten oproepen!
        kracht = nummer // 10   # level 10 -> 1, level 20 -> 2, level 30 -> 3, ...
        baas_x = ARENA_BREEDTE // 2 - 38
        vijanden.append(ArenaBaas(baas_x, 40, links, rechts,
                                  snelheid=2.5 + kracht * 0.3, kracht=kracht))
        # Altijd een hartje zodat je een kans hebt
        powerups.append(ExtraLevenPowerUp(540, 232))

    else:
        # ===== GEWOON VECHT-LEVEL: precies ÉÉN monster =====
        # Dat ene monster wordt steeds sterker en krijgt steeds meer krachten.
        snel = min(1.5 + nummer * 0.1, 6.5)
        mx = rng.randint(links + 100, rechts - 100)
        vijanden.append(ArenaVechter(mx, 40, links, rechts, snel, niveau=nummer))

        # Af en toe een hartje op een zwevend platform
        if nummer % 3 == 0:
            powerups.append(ExtraLevenPowerUp(230, 172))

    # --- Spikes op de vloer: spring eroverheen tijdens het gevecht! ---
    # (niet in het allereerste level, zodat dat lekker rustig blijft)
    if nummer > 1:
        for _ in range(rng.randint(0, 2)):
            aantal_punten = rng.randint(2, 3)
            sw = aantal_punten * 16
            sx = rng.randint(250, ARENA_BREEDTE - 250 - sw)
            vijanden.append(Spikes(sx, 40, aantal_punten))

    # Geen vlag in de arena — je wint door ALLE monsters te verslaan!
    return platforms, vijanden, powerups, -999, -999, ARENA_BREEDTE


# =================================================================
# RACEMODUS
# Je rent VANZELF vooruit en springt over gaten, spikes en blokken.
# Haal de finishvlag! Elke baan wordt langer en een beetje sneller.
# =================================================================
def race_snelheid_bonus(nummer):
    """Hoeveel extra snelheid je in de racemodus hebt (bovenop de basissnelheid).
    Wordt zowel door het spel als door de baan-generator gebruikt, zodat de
    sprongen precies passen bij de snelheid."""
    return min(0.5 + nummer * 0.15, 3)


def _race_spikebrug(x, rng, nummer, platforms, obstakels):
    """Bouw een 'spike-brug': een strook vol spikes met stapsteen-blokken
    erboven. Je moet van blok naar blok springen om eroverheen te komen.
    Soms KLIMT de brug omhoog: de blokken staan steeds hoger! Geeft de
    nieuwe x terug (het einde van de brug)."""
    snelheid = 4 + race_snelheid_bonus(nummer)       # 4 = basissnelheid van de speler
    n = 2 if nummer < 5 else rng.choice([2, 3, 3, 4])
    bw = 150                                          # brede blokken = makkelijker landen
    bh = 22

    # Soms een 'hoge' klim-brug (de kans wordt groter in latere banen)
    hoog = rng.random() < min(0.35 + nummer * 0.05, 0.85)

    prev_top = 40.0          # je begint op de grond (bovenkant = 40)
    prev_x = x + 45          # ongeveer waar je van de grond af springt
    blok_data = []
    for i in range(n):
        if hoog:
            stijging = rng.randint(55, 115)          # elk blok flink hoger
        else:
            stijging = rng.randint(-15, 45)          # ongeveer gelijke hoogte
        # Nieuwe hoogte: hoger, maar nooit meer dan je kunt springen (~120 omhoog)
        top = max(70.0, min(prev_top + stijging, prev_top + 120, 260.0))
        # Reken uit hoe ver dit blok mag staan om er (dalend) op te landen
        onder_wortel = max(576 - 4 * (top - prev_top), 16)
        t_land = 24 + math.sqrt(onder_wortel)
        bcx = prev_x + snelheid * t_land
        platforms.append(BlokPlatform(bcx - bw // 2, top - bh, bw, bh))
        blok_data.append((bcx, top))
        prev_top = top
        prev_x = bcx

    # De grond onder de brug (veilige aanloop + genoeg landingsruimte om af te dalen)
    laatste_rechts = blok_data[-1][0] + bw // 2
    seg = int(laatste_rechts + 240) - x
    platforms.append(Platform(x, 0, seg, 40))

    # Spikes op de grond onder de blokken (aanloop en landing blijven vrij)
    sx = x + 55
    while sx + 48 <= laatste_rechts:
        obstakels.append(Spikes(sx, 40, 3))
        sx += 48

    return x + seg


def vlucht_snelheid_bonus(nummer):
    """Hoe snel je vooruit vliegt per vlucht-baan (iets rustiger dan de race)."""
    return min(0.5 + nummer * 0.12, 2.5)


def maak_vlucht(nummer):
    """Maak een vliegtuig-baan (auto-run + vliegen): je houdt de knop vast om
    omhoog te gaan en laat los om te zakken (net als de raket in Geometry Dash).

    Er is een doorlopende vloer (je valt dus niet zomaar dood), met daarboven
    spikes en zweefblokken waar je omheen en doorheen moet vliegen. Aan het eind
    staat de finishvlag. Deterministisch per baannummer."""
    rng = random.Random(7000 + nummer)
    lengte = (3000 + nummer * 400) * 3     # lekker lang

    # Doorlopende vloer over de hele baan
    platforms = [Platform(0, 0, lengte + 400, 40)]
    obstakels = []                          # spikes -> gaan in 'vijanden'

    plafond = 440                           # net onder de balk bovenin
    x = 700                                 # veilige start (eerst even rustig)

    # Hoe verder je komt, hoe dichter de obstakels op elkaar staan
    afstand_min = max(150, 260 - nummer * 4)
    afstand_max = max(220, 340 - nummer * 4)

    while x < lengte - 400:
        keuze = rng.random()
        if keuze < 0.32:
            # Vloer-spikes: vlieg eroverheen
            obstakels.append(Spikes(x, 40, rng.randint(2, 3)))
        elif keuze < 0.55:
            # Zwevend blok hoog in de lucht: blijf laag vliegen
            bh = rng.randint(60, 100)
            by = rng.randint(190, 320)
            platforms.append(BlokPlatform(x, by, rng.randint(70, 110), bh))
        elif keuze < 0.80:
            # Een muur met een gat: vlieg precies door de opening!
            gat_onder = rng.randint(90, 230)      # onderkant van de opening
            opening = rng.randint(110, 140)       # hoe groot de opening is
            # Onderste stuk muur: van de vloer tot aan de opening
            if gat_onder - 40 > 10:
                platforms.append(BlokPlatform(x, 40, 60, gat_onder - 40))
            # Bovenste stuk muur: van boven de opening tot aan het plafond
            boven_start = gat_onder + opening
            if plafond - boven_start > 10:
                platforms.append(BlokPlatform(x, boven_start, 60, plafond - boven_start))
        # anders: een rustig stukje zonder obstakels
        x += rng.randint(afstand_min, afstand_max)

    # Finishvlag aan het eind (rustig, geen obstakels)
    vlag_x = lengte + 100
    vlag_y = 40
    level_breedte = lengte + 400
    return platforms, obstakels, [], vlag_x, vlag_y, level_breedte


# ==========================================================================
#  NAMAAK van de echte Geometry Dash-levels (Stereo Madness, enz.)
#  We bouwen ze op uit veilige stukjes (segmenten), net als in het echte spel.
# ==========================================================================

class _RaceBouwer:
    """Handig hulpje om een racebaan op te bouwen uit veilige stukjes.

    Je zet stukje voor stukje neer (vlak, spike, muur, gat, schip...) en het
    hulpje onthoudt hoe ver je al bent. Alle afstanden zijn ruim genoeg gekozen
    zodat je er met de vaste sprong (auto-run) overheen kunt.
    """

    def __init__(self):
        self.x = 0
        self.platforms = []
        self.spikes = []
        self.portalen = []
        self.grond(500)          # veilige start

    def grond(self, lengte):
        """Leg een stuk vloer neer en schuif vooruit."""
        self.platforms.append(Platform(self.x, 0, lengte, 40))
        self.x += lengte

    def vlak(self, lengte=240):
        """Een rustig stukje vloer (ruimte tussen obstakels)."""
        self.grond(lengte)

    def spike(self, n=1):
        """Een stukje vloer met n spikes erop (max 2, zodat je er goed overheen komt)."""
        n = min(n, 2)
        seg = 200
        self.platforms.append(Platform(self.x, 0, seg, 40))
        sx = self.x + seg // 2 - (n * 16) // 2
        self.spikes.append(Spikes(sx, 40, n))
        self.x += seg

    def muur(self, hoogte=30):
        """Een laag blok-muurtje om overheen te springen (max 32 hoog = eerlijk)."""
        hoogte = min(hoogte, 32)
        seg = 200
        self.platforms.append(Platform(self.x, 0, seg, 40))
        self.platforms.append(BlokPlatform(self.x + seg // 2 - 20, 40, 40, hoogte))
        self.x += seg

    def plateau(self, hoogte=80, lengte=140):
        """Een blok-plateau waar je bovenop springt en overheen loopt (zoals in Stereo Madness)."""
        hoogte = min(hoogte, 90)
        seg = lengte + 200
        self.platforms.append(Platform(self.x, 0, seg, 40))          # grond eronder
        self.platforms.append(BlokPlatform(self.x + 90, 0, lengte, hoogte))  # het plateau
        self.x += seg

    def trap(self, stappen=4, stap_h=40, stap_b=70):
        """Een trap van blokken die je omhoog springt (tap-tap-tap), zoals in Stereo Madness."""
        seg = stappen * stap_b + 200
        self.platforms.append(Platform(self.x, 0, seg, 40))          # grond eronder
        for i in range(stappen):
            self.platforms.append(BlokPlatform(self.x + 90 + i * stap_b, 0, stap_b, stap_h * (i + 1)))
        self.x += seg

    def gat(self, breedte=120):
        """Een gat in de vloer om overheen te springen (max 130 breed)."""
        self.x += min(breedte, 130)

    def snel(self, soort):
        """Een snelheid-portaal (x0.5 / x2 / ...)."""
        self.portalen.append(Portaal(self.x + 5, 40, soort))
        self.grond(120)

    def schip(self, lengte=1400):
        """Een raket-stuk: schip-portaal in, muren met ruime openingen, blok-portaal uit."""
        self.portalen.append(Portaal(self.x + 5, 40, "vlucht"))
        start = self.x
        self.grond(lengte)                 # doorlopende vloer eronder (je valt niet dood)
        mx = start + 340                   # eerst even rustig na het portaal
        beurt = 0
        while mx < start + lengte - 320:
            gat_onder = 110 + (beurt % 3) * 35     # opening zit steeds iets anders
            opening = 170                           # ruime opening om door te vliegen
            self.platforms.append(BlokPlatform(mx, 40, 46, gat_onder - 40))
            boven = gat_onder + opening
            if 440 - boven > 12:
                self.platforms.append(BlokPlatform(mx, boven, 46, 440 - boven))
            mx += 340
            beurt += 1
        # Uitgang-portaal is superhoog, zodat je het ook raakt als je hoog vliegt
        self.portalen.append(Portaal(self.x + 5, 40, "blok", hoogte=400))
        self.grond(200)

    def klaar(self):
        """Sluit de baan af met een finishvlag en geef de level-gegevens terug."""
        self.grond(500)
        vlag_x = self.x - 200
        level_breedte = self.x
        return (self.platforms, self.spikes, [], vlag_x, 40, level_breedte, self.portalen)


def _stereo_madness(nummer):
    """Namaak van 'Stereo Madness'. De opbouw volgt het echte level (bron: de
    officiele Geometry Dash-wiki): blokje 0-29%, raket 29-46%, blokje 46-85%,
    raket 85-100%. De exacte plek van elk blokje is niet bekend, dus die stukjes
    zijn zo goed mogelijk nagemaakt (lijkt erop, niet tot op de pixel exact)."""
    b = _RaceBouwer()
    # --- Blokje 0-29%: 2 spikes, dan een trap van 4 blokken, dan hoge/lage blokken ---
    b.vlak(320)                       # rustige start
    b.spike(1); b.vlak(230)           # eerste spike
    b.spike(1); b.vlak(250)           # tweede spike
    b.trap(4, 40, 70); b.vlak(240)    # trap van 4 blokken omhoog (tap-tap-tap)
    b.plateau(80, 110); b.vlak(200)   # afwisselend hoog...
    b.plateau(40, 110); b.vlak(220)   # ...en laag blok
    b.spike(1); b.vlak(220)
    b.gat(120); b.vlak(260)           # een pit (gat)
    # --- Raket 29-46% ---
    b.schip(1200)
    b.vlak(260)
    # --- Blokje 46-85% (het 'rode' stuk): spikes (1, 2, 3), plateaus en hoge pilaren ---
    b.spike(1); b.vlak(240)
    b.spike(2); b.vlak(240)
    b.plateau(80, 140); b.vlak(220)
    b.gat(130); b.vlak(240)
    b.spike(2); b.vlak(240)
    b.trap(3, 40, 70); b.vlak(240)          # pilaren omhoog
    b.spike(2); b.vlak(240)
    b.plateau(70, 120); b.vlak(220)
    b.spike(1); b.vlak(260)
    # --- Raket 85-100%: nog een keer vliegen tot de finish ---
    b.schip(1100)
    return b.klaar()


def _back_on_track(nummer):
    """Namaak van 'Back on Track' — drukker: dubbel-spikes, muurtjes en plateaus."""
    b = _RaceBouwer()
    b.vlak(300)
    b.spike(2); b.vlak(240)
    b.muur(30); b.vlak(220)
    b.spike(2); b.vlak(240)
    b.plateau(70, 140); b.vlak(240)
    b.spike(1); b.vlak(220)
    b.gat(130); b.vlak(260)
    b.spike(2); b.vlak(240)
    b.plateau(80, 160); b.vlak(260)
    b.schip(1400)
    b.vlak(260)
    b.spike(2); b.vlak(240)
    b.muur(30); b.vlak(220)
    b.spike(2); b.vlak(240)
    b.plateau(70, 140); b.vlak(240)
    b.gat(130); b.vlak(240)
    b.spike(2); b.vlak(240)
    return b.klaar()


def _polargeist(nummer):
    """Namaak van 'Polargeist' — nog pittiger: meer gaten, plateaus en een lang raket-stuk."""
    b = _RaceBouwer()
    b.vlak(300)
    b.spike(2); b.vlak(240)
    b.gat(130); b.vlak(240)
    b.spike(2); b.vlak(240)
    b.plateau(80, 140); b.vlak(240)
    b.spike(2); b.vlak(240)
    b.muur(30); b.vlak(220)
    b.gat(130); b.vlak(260)
    b.spike(2); b.vlak(240)
    b.plateau(90, 160); b.vlak(260)
    b.schip(1600)
    b.vlak(260)
    b.spike(2); b.vlak(240)
    b.gat(130); b.vlak(240)
    b.plateau(80, 140); b.vlak(240)
    b.spike(2); b.vlak(240)
    b.muur(30); b.vlak(220)
    b.spike(2); b.vlak(260)
    return b.klaar()


# De namaak-levels op hun baannummer, met hun echte naam
GD_LEVELS = {1: _stereo_madness, 2: _back_on_track, 3: _polargeist}
GD_NAMEN = {1: "Stereo Madness", 2: "Back on Track", 3: "Polargeist"}


def race_naam(nummer):
    """De naam van een racebaan: een echte Geometry Dash-naam of gewoon 'Baan N'."""
    return GD_NAMEN.get(nummer, f"Baan {nummer}")


def maak_race(nummer):
    """Maak een racebaan. Baan 1 t/m 3 zijn namaak van echte Geometry Dash-levels;
    daarna komen automatisch gemaakte banen."""
    if nummer in GD_LEVELS:
        return GD_LEVELS[nummer](nummer)
    return _maak_race_willekeurig(nummer)


def _maak_race_willekeurig(nummer):
    """Maak een racebaan (auto-run): grond met gaten, spikes en zweefblokken
    (waar je OP kunt staan) en zwevende spikes. Finishvlag aan het eind.
    Deterministisch per baannummer."""
    rng = random.Random(5000 + nummer)
    lengte = (3200 + nummer * 500) * 5    # 5x zo lang! (elke baan wordt ook langer)

    platforms = []                        # grond + blokken waar je op kunt staan
    obstakels = []                        # spikes (die doen pijn) -> gaan in 'vijanden'

    # Veilige start: de eerste 700px zonder gaten of obstakels
    platforms.append(Platform(0, 0, 700, 40))
    x = 700

    # Moeilijkheid loopt langzaam op
    gat_kans = min(0.30 + nummer * 0.02, 0.55)
    max_gat = 150 + min(nummer * 4, 60)
    brug_kans = min(0.15 + nummer * 0.02, 0.35)

    while x < lengte - 600:
        # Soms een spike-brug: op de blokken springen om over de spikes te komen
        if x > 1000 and rng.random() < brug_kans:
            x = _race_spikebrug(x, rng, nummer, platforms, obstakels)
            continue
        # Soms een gat vóór het volgende stuk grond
        if rng.random() < gat_kans:
            x += rng.randint(120, max_gat)
        # Een stuk grond
        seg = rng.randint(320, 520)
        platforms.append(Platform(x, 0, seg, 40))
        mid = x + seg // 2
        keuze = rng.random()
        if keuze < 0.40:
            # Grond-spikes: spring eroverheen
            obst_x = x + rng.randint(120, seg - 160)
            obstakels.append(Spikes(obst_x, 40, rng.randint(2, 3)))
        elif keuze < 0.68:
            # Een zweefblok in de lucht — spring erop en sta erop!
            bw = rng.randint(64, 90)
            hoogte = rng.choice([70, 100, 130])
            platforms.append(BlokPlatform(mid - bw // 2, hoogte, bw, 24))
        elif keuze < 0.82:
            # Zwevende spikes op sprong-hoogte: niet erin springen!
            obstakels.append(Spikes(mid - 24, rng.choice([95, 125]), 3))
        # anders: een rustig stuk zonder obstakels
        x += seg

    # Eind-stuk met de finishvlag (veilig, geen obstakels)
    platforms.append(Platform(x, 0, 600, 40))
    vlag_x = x + 500
    vlag_y = 40
    level_breedte = x + 600

    return platforms, obstakels, [], vlag_x, vlag_y, level_breedte

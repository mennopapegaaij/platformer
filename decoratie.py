# decoratie.py
# Versiering voor je eigen level: bloemen, bomen, wolken, sterren en struikjes.
# Decoratie is ALLEEN voor de mooiigheid — je botst er niet tegenaan en gaat er
# niet dood van. Het wordt achter de spelwereld getekend.

import arcade
import math

# De soorten decoratie waar je met de Deco-knop doorheen klikt
DECO_SOORTEN = ["bloem", "boom", "wolk", "ster", "struik"]
DECO_NAAM = {"bloem": "Bloem", "boom": "Boom", "wolk": "Wolk",
             "ster": "Ster", "struik": "Struik"}


def teken_deco(soort, x, y, g):
    """Teken een stukje decoratie op scherm-plek (x, y) met grootte g."""
    cx = x + g / 2
    if soort == "bloem":
        arcade.draw_line(cx, y, cx, y + g * 0.6, (60, 160, 60), 3)     # steeltje
        for hoek in range(0, 360, 72):                                 # 5 blaadjes
            px = cx + math.cos(math.radians(hoek)) * g * 0.18
            py = y + g * 0.72 + math.sin(math.radians(hoek)) * g * 0.18
            arcade.draw_circle_filled(px, py, g * 0.14, (255, 120, 180))
        arcade.draw_circle_filled(cx, y + g * 0.72, g * 0.12, (255, 220, 80))  # hartje
    elif soort == "boom":
        arcade.draw_lrbt_rectangle_filled(cx - g * 0.08, cx + g * 0.08, y, y + g * 0.4,
                                          (110, 70, 30))               # stam
        arcade.draw_triangle_filled(cx - g * 0.34, y + g * 0.35, cx + g * 0.34, y + g * 0.35,
                                    cx, y + g * 0.95, (40, 150, 50))   # bladeren
        arcade.draw_triangle_filled(cx - g * 0.26, y + g * 0.6, cx + g * 0.26, y + g * 0.6,
                                    cx, y + g * 1.1, (60, 180, 70))
    elif soort == "wolk":
        cy = y + g * 0.5
        arcade.draw_ellipse_filled(cx, cy, g * 0.85, g * 0.4, (255, 255, 255))
        arcade.draw_ellipse_filled(cx - g * 0.18, cy + g * 0.12, g * 0.45, g * 0.35, (255, 255, 255))
        arcade.draw_ellipse_filled(cx + g * 0.18, cy + g * 0.12, g * 0.45, g * 0.35, (255, 255, 255))
    elif soort == "ster":
        cy = y + g * 0.55
        R, r = g * 0.42, g * 0.18
        punten = []
        for i in range(10):
            hoek = math.radians(-90 + i * 36)
            straal = R if i % 2 == 0 else r
            punten.append((cx + math.cos(hoek) * straal, cy + math.sin(hoek) * straal))
        arcade.draw_polygon_filled(punten, (255, 220, 70))
    elif soort == "struik":
        for dx, r in [(0.3, 0.22), (0.5, 0.3), (0.7, 0.22)]:
            arcade.draw_circle_filled(x + g * dx, y + g * 0.3, g * r, (50, 150, 60))


class Decoratie:
    """Een stukje versiering in je level (geen botsing, alleen tekenen)."""

    # Sommige decoratie is wat hoger/groter
    GROOTTE = {"boom": 80}

    def __init__(self, x, y, soort):
        self.x = x
        self.y = y
        self.soort = soort
        self.breedte = 40
        self.hoogte = self.GROOTTE.get(soort, 40)

    def teken(self):
        teken_deco(self.soort, self.x, self.y, self.hoogte)

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


def teken_deco(soort, x, y, g, rotatie=0):
    """Teken een stukje decoratie op scherm-plek (x, y) met grootte g.

    rotatie (0/90/180/270) draait de decoratie rond het midden van het vakje.
    """
    mx, my = x + g / 2, y + g / 2         # midden om te draaien

    def d(px, py):
        dx, dy = px - mx, py - my
        r = rotatie % 360
        if r == 90:
            return (mx - dy, my + dx)
        if r == 180:
            return (mx - dx, my - dy)
        if r == 270:
            return (mx + dy, my - dx)
        return (px, py)

    cx = x + g / 2
    if soort == "bloem":
        a, b = d(cx, y), d(cx, y + g * 0.6)
        arcade.draw_line(a[0], a[1], b[0], b[1], (60, 160, 60), 3)     # steeltje
        for hoek in range(0, 360, 72):                                 # 5 blaadjes
            px = cx + math.cos(math.radians(hoek)) * g * 0.18
            py = y + g * 0.72 + math.sin(math.radians(hoek)) * g * 0.18
            bx, by = d(px, py)
            arcade.draw_circle_filled(bx, by, g * 0.14, (255, 120, 180))
        hx, hy = d(cx, y + g * 0.72)
        arcade.draw_circle_filled(hx, hy, g * 0.12, (255, 220, 80))    # hartje
    elif soort == "boom":
        # stam (als vierkant dat meedraait)
        arcade.draw_polygon_filled([d(cx - g * 0.08, y), d(cx + g * 0.08, y),
                                    d(cx + g * 0.08, y + g * 0.4), d(cx - g * 0.08, y + g * 0.4)],
                                   (110, 70, 30))
        arcade.draw_polygon_filled([d(cx - g * 0.34, y + g * 0.35), d(cx + g * 0.34, y + g * 0.35),
                                    d(cx, y + g * 0.95)], (40, 150, 50))   # bladeren
        arcade.draw_polygon_filled([d(cx - g * 0.26, y + g * 0.6), d(cx + g * 0.26, y + g * 0.6),
                                    d(cx, y + g * 1.1)], (60, 180, 70))
    elif soort == "wolk":
        cy = y + g * 0.5
        for ddx, ddy, ww, hh in [(0, 0, 0.85, 0.4), (-0.18, 0.12, 0.45, 0.35), (0.18, 0.12, 0.45, 0.35)]:
            ex, ey = d(cx + g * ddx, cy + g * ddy)
            arcade.draw_ellipse_filled(ex, ey, g * ww, g * hh, (255, 255, 255))
    elif soort == "ster":
        cy = y + g * 0.55
        R, r = g * 0.42, g * 0.18
        punten = []
        for i in range(10):
            hoek = math.radians(-90 + i * 36)
            straal = R if i % 2 == 0 else r
            punten.append(d(cx + math.cos(hoek) * straal, cy + math.sin(hoek) * straal))
        arcade.draw_polygon_filled(punten, (255, 220, 70))
    elif soort == "struik":
        for ddx, r in [(0.3, 0.22), (0.5, 0.3), (0.7, 0.22)]:
            bx, by = d(x + g * ddx, y + g * 0.3)
            arcade.draw_circle_filled(bx, by, g * r, (50, 150, 60))


class Decoratie:
    """Een stukje versiering in je level (geen botsing, alleen tekenen)."""

    # Sommige decoratie is wat hoger/groter
    GROOTTE = {"boom": 80}

    def __init__(self, x, y, soort, rotatie=0):
        self.x = x
        self.y = y
        self.soort = soort
        self.rotatie = rotatie % 360
        self.breedte = 40
        self.hoogte = self.GROOTTE.get(soort, 40)

    def teken(self):
        teken_deco(self.soort, self.x, self.y, self.hoogte, self.rotatie)

# decoratie.py
# Versiering voor je eigen level: bloemen, bomen, wolken, sterren en struikjes.
# Decoratie is ALLEEN voor de mooiigheid — je botst er niet tegenaan en gaat er
# niet dood van. Het wordt achter de spelwereld getekend.

import arcade
import math

# De soorten decoratie waar je met de Deco-knop doorheen klikt
DECO_SOORTEN = ["bloem", "boom", "wolk", "ster", "struik",
                "zon", "maan", "regenboog", "paddenstoel", "steen", "vlinder"]
DECO_NAAM = {"bloem": "Bloem", "boom": "Boom", "wolk": "Wolk",
             "ster": "Ster", "struik": "Struik", "zon": "Zon", "maan": "Maan",
             "regenboog": "Regenboog", "paddenstoel": "Paddenstoel",
             "steen": "Steen", "vlinder": "Vlinder"}


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
    elif soort == "zon":
        cy = y + g * 0.5
        scx, scy = d(cx, cy)
        for hoek in range(0, 360, 45):                     # stralen rondom
            r = math.radians(hoek)
            x1, y1 = d(cx + math.cos(r) * g * 0.32, cy + math.sin(r) * g * 0.32)
            x2, y2 = d(cx + math.cos(r) * g * 0.48, cy + math.sin(r) * g * 0.48)
            arcade.draw_line(x1, y1, x2, y2, (255, 200, 40), 3)
        arcade.draw_circle_filled(scx, scy, g * 0.28, (255, 210, 50))
    elif soort == "maan":
        cy = y + g * 0.5
        mcx, mcy = d(cx, cy)
        arcade.draw_circle_filled(mcx, mcy, g * 0.32, (240, 235, 180))     # bleke maan
        for ddx, ddy, rr in [(-0.09, 0.06, 0.06), (0.1, -0.02, 0.05), (0.02, 0.15, 0.045)]:
            kx, ky = d(cx + g * ddx, cy + g * ddy)
            arcade.draw_circle_filled(kx, ky, g * rr, (210, 205, 150))     # kratertjes
    elif soort == "regenboog":
        cy = y + g * 0.15                                  # boog vanaf onderaan
        kleuren = [(230, 60, 60), (240, 150, 40), (240, 220, 60),
                   (70, 180, 80), (60, 120, 220)]
        for i, kl in enumerate(kleuren):
            maat = g * (0.9 - i * 0.15)
            arcade.draw_arc_outline(cx, cy, maat, maat, kl, 0, 180, 4)
    elif soort == "paddenstoel":
        # steeltje
        arcade.draw_polygon_filled([d(cx - g * 0.1, y), d(cx + g * 0.1, y),
                                    d(cx + g * 0.1, y + g * 0.45), d(cx - g * 0.1, y + g * 0.45)],
                                   (240, 230, 200))
        # rode hoed
        hx, hy = d(cx, y + g * 0.5)
        arcade.draw_ellipse_filled(hx, hy, g * 0.72, g * 0.5, (220, 50, 50))
        # witte stippen op de hoed
        for ddx, ddy in [(-0.18, 0.08), (0.16, 0.05), (0.0, 0.16)]:
            sx, sy = d(cx + g * ddx, y + g * 0.5 + g * ddy)
            arcade.draw_circle_filled(sx, sy, g * 0.06, (255, 255, 255))
    elif soort == "steen":
        punten = [d(cx - g * 0.35, y + g * 0.12), d(cx - g * 0.28, y + g * 0.5),
                  d(cx, y + g * 0.62), d(cx + g * 0.32, y + g * 0.46),
                  d(cx + g * 0.3, y + g * 0.14)]
        arcade.draw_polygon_filled(punten, (140, 140, 150))
        arcade.draw_polygon_outline(punten, (90, 90, 100), 2)
    elif soort == "vlinder":
        cy = y + g * 0.5
        for kant in (-1, 1):                               # twee vleugels
            w1 = d(cx + kant * g * 0.05, cy)
            w2 = d(cx + kant * g * 0.36, cy + g * 0.22)
            w3 = d(cx + kant * g * 0.36, cy - g * 0.22)
            arcade.draw_triangle_filled(w1[0], w1[1], w2[0], w2[1], w3[0], w3[1],
                                        (180, 100, 220))
        b1 = d(cx, cy + g * 0.22)
        b2 = d(cx, cy - g * 0.22)
        arcade.draw_line(b1[0], b1[1], b2[0], b2[1], (60, 40, 30), 3)      # lijfje


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

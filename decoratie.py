# decoratie.py
# Versiering voor je eigen level: bloemen, bomen, wolken, sterren en struikjes.
# Decoratie is ALLEEN voor de mooiigheid — je botst er niet tegenaan en gaat er
# niet dood van. Het wordt achter de spelwereld getekend.

import arcade
import math
import time

# De soorten decoratie waar je met de Deco-knop doorheen klikt.
# De laatste zes BEWEGEN (animatie) — en net als alle deco loop je er doorheen.
DECO_SOORTEN = ["bloem", "boom", "wolk", "ster", "struik",
                "zon", "maan", "regenboog", "paddenstoel", "steen", "vlinder",
                "vuur", "fonkel", "draaister", "waterval", "hartje", "bel"]
DECO_NAAM = {"bloem": "Bloem", "boom": "Boom", "wolk": "Wolk",
             "ster": "Ster", "struik": "Struik", "zon": "Zon", "maan": "Maan",
             "regenboog": "Regenboog", "paddenstoel": "Paddenstoel",
             "steen": "Steen", "vlinder": "Vlinder",
             "vuur": "Vuur", "fonkel": "Fonkel", "draaister": "Draaister",
             "waterval": "Waterval", "hartje": "Hartje", "bel": "Belletjes"}


def teken_deco(soort, x, y, g, rotatie=0, kleur=None):
    """Teken een stukje decoratie op scherm-plek (x, y) met grootte g.

    rotatie (0/90/180/270) draait de decoratie rond het midden van het vakje.
    `kleur` (verf): is die er, dan wordt de hele decoratie in die kleur getekend.
    """
    def K(standaard):
        return kleur if kleur else standaard      # verf-kleur wint als die er is
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
        arcade.draw_line(a[0], a[1], b[0], b[1], K((60, 160, 60)), 3)     # steeltje
        for hoek in range(0, 360, 72):                                 # 5 blaadjes
            px = cx + math.cos(math.radians(hoek)) * g * 0.18
            py = y + g * 0.72 + math.sin(math.radians(hoek)) * g * 0.18
            bx, by = d(px, py)
            arcade.draw_circle_filled(bx, by, g * 0.14, K((255, 120, 180)))
        hx, hy = d(cx, y + g * 0.72)
        arcade.draw_circle_filled(hx, hy, g * 0.12, K((255, 220, 80)))    # hartje
    elif soort == "boom":
        # stam (als vierkant dat meedraait)
        arcade.draw_polygon_filled([d(cx - g * 0.08, y), d(cx + g * 0.08, y),
                                    d(cx + g * 0.08, y + g * 0.4), d(cx - g * 0.08, y + g * 0.4)],
                                   K((110, 70, 30)))
        arcade.draw_polygon_filled([d(cx - g * 0.34, y + g * 0.35), d(cx + g * 0.34, y + g * 0.35),
                                    d(cx, y + g * 0.95)], K((40, 150, 50)))   # bladeren
        arcade.draw_polygon_filled([d(cx - g * 0.26, y + g * 0.6), d(cx + g * 0.26, y + g * 0.6),
                                    d(cx, y + g * 1.1)], K((60, 180, 70)))
    elif soort == "wolk":
        cy = y + g * 0.5
        for ddx, ddy, ww, hh in [(0, 0, 0.85, 0.4), (-0.18, 0.12, 0.45, 0.35), (0.18, 0.12, 0.45, 0.35)]:
            ex, ey = d(cx + g * ddx, cy + g * ddy)
            arcade.draw_ellipse_filled(ex, ey, g * ww, g * hh, K((255, 255, 255)))
    elif soort == "ster":
        cy = y + g * 0.55
        R, r = g * 0.42, g * 0.18
        punten = []
        for i in range(10):
            hoek = math.radians(-90 + i * 36)
            straal = R if i % 2 == 0 else r
            punten.append(d(cx + math.cos(hoek) * straal, cy + math.sin(hoek) * straal))
        arcade.draw_polygon_filled(punten, K((255, 220, 70)))
    elif soort == "struik":
        for ddx, r in [(0.3, 0.22), (0.5, 0.3), (0.7, 0.22)]:
            bx, by = d(x + g * ddx, y + g * 0.3)
            arcade.draw_circle_filled(bx, by, g * r, K((50, 150, 60)))
    elif soort == "zon":
        cy = y + g * 0.5
        scx, scy = d(cx, cy)
        for hoek in range(0, 360, 45):                     # stralen rondom
            r = math.radians(hoek)
            x1, y1 = d(cx + math.cos(r) * g * 0.32, cy + math.sin(r) * g * 0.32)
            x2, y2 = d(cx + math.cos(r) * g * 0.48, cy + math.sin(r) * g * 0.48)
            arcade.draw_line(x1, y1, x2, y2, K((255, 200, 40)), 3)
        arcade.draw_circle_filled(scx, scy, g * 0.28, K((255, 210, 50)))
    elif soort == "maan":
        cy = y + g * 0.5
        mcx, mcy = d(cx, cy)
        arcade.draw_circle_filled(mcx, mcy, g * 0.32, K((240, 235, 180)))     # bleke maan
        for ddx, ddy, rr in [(-0.09, 0.06, 0.06), (0.1, -0.02, 0.05), (0.02, 0.15, 0.045)]:
            kx, ky = d(cx + g * ddx, cy + g * ddy)
            arcade.draw_circle_filled(kx, ky, g * rr, K((210, 205, 150)))     # kratertjes
    elif soort == "regenboog":
        cy = y + g * 0.15                                  # boog vanaf onderaan
        kleuren = [(230, 60, 60), (240, 150, 40), (240, 220, 60),
                   (70, 180, 80), (60, 120, 220)]
        for i, kl in enumerate(kleuren):
            maat = g * (0.9 - i * 0.15)
            arcade.draw_arc_outline(cx, cy, maat, maat, K(kl), 0, 180, 4)
    elif soort == "paddenstoel":
        # steeltje
        arcade.draw_polygon_filled([d(cx - g * 0.1, y), d(cx + g * 0.1, y),
                                    d(cx + g * 0.1, y + g * 0.45), d(cx - g * 0.1, y + g * 0.45)],
                                   K((240, 230, 200)))
        # rode hoed
        hx, hy = d(cx, y + g * 0.5)
        arcade.draw_ellipse_filled(hx, hy, g * 0.72, g * 0.5, K((220, 50, 50)))
        # witte stippen op de hoed
        for ddx, ddy in [(-0.18, 0.08), (0.16, 0.05), (0.0, 0.16)]:
            sx, sy = d(cx + g * ddx, y + g * 0.5 + g * ddy)
            arcade.draw_circle_filled(sx, sy, g * 0.06, K((255, 255, 255)))
    elif soort == "steen":
        punten = [d(cx - g * 0.35, y + g * 0.12), d(cx - g * 0.28, y + g * 0.5),
                  d(cx, y + g * 0.62), d(cx + g * 0.32, y + g * 0.46),
                  d(cx + g * 0.3, y + g * 0.14)]
        arcade.draw_polygon_filled(punten, K((140, 140, 150)))
        arcade.draw_polygon_outline(punten, (90, 90, 100), 2)
    elif soort == "vlinder":
        cy = y + g * 0.5
        for kant in (-1, 1):                               # twee vleugels
            w1 = d(cx + kant * g * 0.05, cy)
            w2 = d(cx + kant * g * 0.36, cy + g * 0.22)
            w3 = d(cx + kant * g * 0.36, cy - g * 0.22)
            arcade.draw_triangle_filled(w1[0], w1[1], w2[0], w2[1], w3[0], w3[1],
                                        K((180, 100, 220)))
        b1 = d(cx, cy + g * 0.22)
        b2 = d(cx, cy - g * 0.22)
        arcade.draw_line(b1[0], b1[1], b2[0], b2[1], K((60, 40, 30)), 3)      # lijfje

    # ---------- BEWEGENDE decoratie (animatie met een tijd-klok) ----------
    elif soort == "vuur":
        t = time.perf_counter() * 8
        basis_y = y + g * 0.15
        hoog = 0.55 + 0.25 * math.sin(t) + 0.1 * math.sin(t * 2.3)   # flakkeren
        # gloed onderaan
        arcade.draw_ellipse_filled(cx, basis_y, g * 0.55, g * 0.16, K((255, 150, 40)))
        # buitenvlam (oranje) en binnenvlam (geel)
        arcade.draw_triangle_filled(cx - g * 0.28, basis_y, cx + g * 0.28, basis_y,
                                    cx + math.sin(t) * g * 0.08, basis_y + g * hoog, K((240, 110, 30)))
        arcade.draw_triangle_filled(cx - g * 0.15, basis_y, cx + g * 0.15, basis_y,
                                    cx + math.sin(t * 1.5) * g * 0.05, basis_y + g * hoog * 0.6,
                                    K((255, 225, 90)))
    elif soort == "fonkel":
        t = time.perf_counter()
        for i, (ddx, ddy) in enumerate([(0.3, 0.7), (0.68, 0.45), (0.45, 0.28), (0.72, 0.72)]):
            s = (math.sin(t * 4 + i * 1.7) + 1) / 2             # 0..1 twinkelen
            r = g * 0.05 + g * 0.11 * s
            px, py = x + g * ddx, y + g * ddy
            kl = K((255, 255, 190))
            arcade.draw_line(px - r, py, px + r, py, kl, 2)
            arcade.draw_line(px, py - r, px, py + r, kl, 2)
    elif soort == "draaister":
        t = time.perf_counter()
        cy = y + g * 0.5
        R, r = g * 0.42, g * 0.18
        hoek0 = t * 2.2                                          # draait rond
        punten = []
        for i in range(10):
            hoek = hoek0 + math.radians(i * 36)
            straal = R if i % 2 == 0 else r
            punten.append((cx + math.cos(hoek) * straal, cy + math.sin(hoek) * straal))
        arcade.draw_polygon_filled(punten, K((255, 210, 70)))
    elif soort == "waterval":
        t = time.perf_counter()
        arcade.draw_lrbt_rectangle_filled(x + g * 0.15, x + g * 0.85, y, y + g, K((90, 170, 255, 150)))
        for i in range(3):
            ry = y + ((t * 55 + i * g / 3) % g)                 # ribbels stromen omlaag
            arcade.draw_line(x + g * 0.15, ry, x + g * 0.85, ry, K((230, 245, 255)), 2)
        arcade.draw_ellipse_filled(cx, y + g * 0.06, g * 0.7, g * 0.14, K((225, 240, 255)))
    elif soort == "hartje":
        t = time.perf_counter()
        s = 1 + 0.14 * math.sin(t * 6)                          # klopt
        r = g * 0.17 * s
        hy = y + g * 0.52
        arcade.draw_circle_filled(cx - r * 0.9, hy + r * 0.5, r, K((230, 60, 90)))
        arcade.draw_circle_filled(cx + r * 0.9, hy + r * 0.5, r, K((230, 60, 90)))
        arcade.draw_triangle_filled(cx - r * 1.7, hy + r * 0.55, cx + r * 1.7, hy + r * 0.55,
                                    cx, hy - r * 1.6, K((230, 60, 90)))
    elif soort == "bel":
        t = time.perf_counter()
        for i in range(4):
            by = y + ((t * 42 + i * g * 0.45) % g)              # belletjes stijgen op
            bx = cx + (i - 1.5) * g * 0.12 + math.sin(t * 3 + i) * g * 0.08
            arcade.draw_circle_outline(bx, by, g * 0.07 + (i % 2) * g * 0.03, K((180, 230, 255)), 2)


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
        teken_deco(self.soort, self.x, self.y, self.hoogte, self.rotatie,
                   getattr(self, "verf_kleur", None))


class TekstBord:
    """Een bordje met je eigen tekst erop (geen botsing, alleen om te lezen)."""

    def __init__(self, x, y, tekst=""):
        self.x = x
        self.y = y
        self.tekst = tekst
        self.breedte = 40
        self.hoogte = 40

    def teken(self):
        cx = self.x + self.breedte / 2
        # Paaltje
        arcade.draw_lrbt_rectangle_filled(cx - 3, cx + 3, self.y, self.y + 24, (120, 80, 40))
        # Bord (bruin plankje met rand)
        arcade.draw_lrbt_rectangle_filled(self.x - 4, self.x + self.breedte + 4,
                                          self.y + 24, self.y + 46, (200, 160, 90))
        arcade.draw_lrbt_rectangle_outline(self.x - 4, self.x + self.breedte + 4,
                                           self.y + 24, self.y + 46, (120, 80, 40), 2)
        # De tekst zweeft boven het bord (goed leesbaar)
        if self.tekst:
            breedte = 8 * len(self.tekst) + 14
            arcade.draw_lrbt_rectangle_filled(cx - breedte / 2, cx + breedte / 2,
                                              self.y + 52, self.y + 78, (30, 30, 45))
            arcade.draw_lrbt_rectangle_outline(cx - breedte / 2, cx + breedte / 2,
                                               self.y + 52, self.y + 78, (255, 255, 255), 2)
            arcade.draw_text(self.tekst, cx, self.y + 58, arcade.color.WHITE, 12,
                             bold=True, anchor_x="center")

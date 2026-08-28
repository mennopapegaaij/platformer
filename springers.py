# springers.py
# Extra spring-dingen, zoals in Geometry Dash:
#   - SpringBol (ring): raak je hem en DRUK je op springen, dan spring je (ook in de lucht)
#   - SpringMat (pad): raak je hem, dan spring je VANZELF omhoog (geen knop nodig)
# Elk heeft een KRACHT: hoe groter, hoe hoger je springt.
# Een NEGATIEVE kracht schiet je juist naar BENEDEN (dan val je) — de paarse bol.

import arcade

# Kracht-standen 1 t/m 5 -> hoe snel je omhoog schiet
KRACHT_PER_STAND = {1: 10, 2: 13, 3: 16, 4: 19, 5: 22}
# De naar-beneden-bol (je valt)
NEER_KRACHT = -15


def spring_kleur(kracht):
    """Kleur van een spring-ding: geel (zacht) -> rood (hard), paars = naar beneden."""
    if kracht < 0:
        return (150, 90, 220)                       # paars = naar beneden
    t = min(max((kracht - 10) / 12.0, 0.0), 1.0)     # 10..22 -> 0..1
    return (255, int(215 - t * 150), 50)             # geel -> oranje/rood


class SpringBol:
    """Een zweef-ring. Raak je hem en druk je op springen, dan gebeurt er iets:
      - gewone bol: je springt met zijn kracht omhoog (of omlaag bij een negatieve kracht)
      - draai-bol: de zwaartekracht draait om, dan val je juist de andere kant op!
    Werkt ook midden in de lucht."""

    def __init__(self, x, y, kracht=13, draai=False):
        self.x = x
        self.y = y
        self.breedte = 34
        self.hoogte = 34
        self.kracht = kracht
        self.draai = draai        # True = draai-bol (zwaartekracht omdraaien)

    def raakt_speler(self, sx, sy, sb, sh):
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        if self.draai:
            # Draai-bol: blauwe ring met twee pijltjes (omhoog + omlaag)
            arcade.draw_circle_outline(cx, cy, 16, (70, 150, 255), 4)
            arcade.draw_circle_outline(cx, cy, 9, (200, 230, 255), 2)
            arcade.draw_triangle_filled(cx - 7, cy + 1, cx - 3, cy + 1, cx - 5, cy + 7, (70, 150, 255))
            arcade.draw_triangle_filled(cx + 3, cy - 1, cx + 7, cy - 1, cx + 5, cy - 7, (70, 150, 255))
            return
        kleur = spring_kleur(self.kracht)
        arcade.draw_circle_outline(cx, cy, 16, kleur, 4)
        arcade.draw_circle_outline(cx, cy, 9, (255, 245, 200), 2)
        # pijltje: omhoog bij een gewone bol, omlaag bij de neer-bol
        if self.kracht < 0:
            arcade.draw_triangle_filled(cx - 6, cy + 3, cx + 6, cy + 3, cx, cy - 6, kleur)
        else:
            arcade.draw_triangle_filled(cx - 6, cy - 3, cx + 6, cy - 3, cx, cy + 6, kleur)


class SpringMat:
    """Een spring-mat op de grond (of op een blok). Raak je hem, dan spring je
    VANZELF omhoog met zijn kracht — je hoeft niet te drukken!"""

    def __init__(self, x, y, kracht=16):
        self.x = x
        self.y = y
        self.breedte = 40
        self.hoogte = 14
        self.kracht = kracht

    def raakt_speler(self, sx, sy, sb, sh):
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        kleur = spring_kleur(self.kracht)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (200, 110, 30))     # voet
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 4, y + h, kleur)      # gekleurde rand
        # twee pijltjes omhoog erbovenop
        for i in range(2):
            sx = x + 8 + i * 18
            arcade.draw_triangle_filled(sx, y + h, sx + 10, y + h, sx + 5, y + h + 8, kleur)

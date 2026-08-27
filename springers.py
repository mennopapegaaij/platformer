# springers.py
# Extra spring-dingen, zoals in Geometry Dash:
#   - SpringBol (ring): raak je hem en DRUK je op springen, dan spring je (ook in de lucht)
#   - SpringMat (pad): raak je hem, dan spring je VANZELF omhoog (geen knop nodig)

import arcade

BOL_KRACHT = 13   # hoe hoog je springt met een spring-bol (druk terwijl je hem raakt)
MAT_KRACHT = 16   # hoe hoog je springt met een spring-mat (vanzelf, geen druk nodig)


class SpringBol:
    """Een zweef-ring. Raak je hem en druk je op springen, dan spring je omhoog —
    ook midden in de lucht! Handig om hoge sprongen te maken."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.breedte = 34
        self.hoogte = 34

    def raakt_speler(self, sx, sy, sb, sh):
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        arcade.draw_circle_outline(cx, cy, 16, (255, 210, 50), 4)      # gele ring
        arcade.draw_circle_outline(cx, cy, 9, (255, 240, 160), 2)
        # pijltje omhoog in het midden
        arcade.draw_triangle_filled(cx - 6, cy - 3, cx + 6, cy - 3, cx, cy + 6, (255, 210, 50))


class SpringMat:
    """Een spring-mat op de grond (of op een blok). Raak je hem, dan spring je
    VANZELF omhoog — je hoeft niet te drukken!"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.breedte = 40
        self.hoogte = 14

    def raakt_speler(self, sx, sy, sb, sh):
        return (sx + sb > self.x and sx < self.x + self.breedte and
                sy + sh > self.y and sy < self.y + self.hoogte)

    def teken(self):
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (255, 140, 40))     # oranje voet
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 4, y + h, (255, 210, 50))  # gele rand
        # twee pijltjes omhoog erbovenop
        for i in range(2):
            sx = x + 8 + i * 18
            arcade.draw_triangle_filled(sx, y + h, sx + 10, y + h, sx + 5, y + h + 8, (255, 210, 50))

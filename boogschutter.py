# boogschutter.py
# De BOOGSCHUTTER: schiet pijlen die in muren blijven steken, en daar kun je op staan!
#
#  Pijltje omlaag : schiet een pijl recht vooruit (5 in je koker, elke 1,5 seconde een erbij)
#  Pijl raakt een muur   -> hij blijft steken en wordt een klein opstapje
#  Pijl raakt een monster -> weg ermee
# Spring en schiet op verschillende hoogtes: zo bouw je een trap van pijlen tegen een muur.
# Alles is vast: geen toeval.

import arcade
from platforms import Platform

KOKER_MAX = 5             # zoveel pijlen passen er in je koker
BIJVULLEN = 90            # elke 90 stapjes (1,5 seconde) komt er een pijl bij
PIJL_SNELHEID = 14        # zo snel vliegt een pijl
PIJL_BEREIK = 520         # zo ver vliegt een pijl hoogstens
PIJL_LENGTE = 34          # zo ver steekt een pijl uit de muur (zo breed is je opstapje)
MAX_VAST = 6              # zoveel pijlen kunnen er tegelijk in de muren steken


class PijlPlatform(Platform):
    """Een pijl die in een muur steekt: een smal opstapje."""

    is_pijl = True

    def __init__(self, x, y, richting):
        super().__init__(x, y, PIJL_LENGTE, 6)
        self.richting = richting      # welke kant de pijl op vloog (de punt zit in de muur)

    def teken(self):
        _teken_pijl(self.x, self.y + 3, self.richting, self.breedte)


def _teken_pijl(x, y, richting, lengte=PIJL_LENGTE):
    """Teken een pijl van x tot x+lengte op hoogte y (punt aan de kant van 'richting')."""
    arcade.draw_line(x, y, x + lengte, y, (150, 100, 50), 4)
    if richting > 0:
        punt, staart = x + lengte, x
    else:
        punt, staart = x, x + lengte
    arcade.draw_triangle_filled(punt + richting * 6, y, punt, y - 4, punt, y + 4, (190, 190, 200))
    for i in range(2):                                    # veertjes aan de staart
        sx = staart + richting * (2 + i * 5)
        arcade.draw_line(sx, y, sx - richting * 5, y + 5, (230, 60, 60), 2)
        arcade.draw_line(sx, y, sx - richting * 5, y - 5, (230, 60, 60), 2)


def reset(sp):
    sp._bs_koker = KOKER_MAX
    sp._bs_bijvul = 0
    sp._bs_vliegend = []      # {"x", "y", "r" (richting), "af" (afgelegd)}
    sp._bs_vast = []          # PijlPlatforms die in muren steken
    sp._bs_t = 0
    sp._bs_span = 0           # animatie: boog gespannen


def schiet(sp):
    """Pijltje omlaag: schiet een pijl. Geeft True als het lukte."""
    if sp._bs_koker <= 0:
        return False
    sp._bs_koker -= 1
    r = 1 if sp.kijkt_rechts else -1
    x = sp.x + sp.breedte + 2 if r > 0 else sp.x - 2
    sp._bs_vliegend.append({"x": x, "y": sp.y + sp.hoogte * 0.55, "r": r, "af": 0})
    sp._bs_span = 10
    return True


def stap(sp, platforms):
    """Elke stap: pijlen vliegen, blijven in muren steken, en je koker vult bij."""
    sp._bs_t += 1
    if sp._bs_span > 0:
        sp._bs_span -= 1
    if sp._bs_koker < KOKER_MAX:
        sp._bs_bijvul += 1
        if sp._bs_bijvul >= BIJVULLEN:
            sp._bs_bijvul = 0
            sp._bs_koker += 1
    else:
        sp._bs_bijvul = 0
    muren = [p for p in platforms if getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
             and not getattr(p, "is_pijl", False)]
    klaar = []
    for pijl in sp._bs_vliegend:
        for _ in range(PIJL_SNELHEID // 2):              # kleine stapjes, zodat hij niet door dunne muren gaat
            pijl["x"] += 2 * pijl["r"]
            pijl["af"] += 2
            muur = next((p for p in muren if p.x <= pijl["x"] <= p.x + p.breedte
                         and p.y <= pijl["y"] <= p.y + p.hoogte), None)
            if muur is not None:
                # Vast in de muur: het stuk dat uitsteekt wordt een opstapje
                if pijl["r"] > 0:
                    px = muur.x - PIJL_LENGTE
                else:
                    px = muur.x + muur.breedte
                sp._bs_vast.append(PijlPlatform(px, pijl["y"] - 3, pijl["r"]))
                if len(sp._bs_vast) > MAX_VAST:
                    sp._bs_vast.pop(0)                    # de oudste pijl valt eruit
                klaar.append(pijl)
                break
            if pijl["af"] >= PIJL_BEREIK:
                klaar.append(pijl)                        # te ver: de pijl valt weg
                break
    sp._bs_vliegend = [p for p in sp._bs_vliegend if p not in klaar]


def raakt(pijl, obj):
    """Raakt deze vliegende pijl dit monster?"""
    return (obj.x <= pijl["x"] <= obj.x + getattr(obj, "breedte", 32)
            and obj.y <= pijl["y"] <= obj.y + getattr(obj, "hoogte", 32))


# ===========================================================================
# Tekenen
# ===========================================================================
def teken(sp):
    for pijl in sp._bs_vliegend:
        _teken_pijl(pijl["x"] - (PIJL_LENGTE if pijl["r"] > 0 else 0), pijl["y"], pijl["r"])
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    # Groene tuniek en kap
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (60, 130, 60))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + h * 0.28, y + h * 0.34, (110, 70, 30))   # riem
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 6, (240, 205, 170))
    arcade.draw_triangle_filled(x + 2, y + h * 0.66, x + w - 2, y + h * 0.66, cx - k * 6, y + h + 8,
                                (50, 110, 50))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.76, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.76, 2.5, (20, 20, 30))
    # Koker op de rug met pijlen erin
    kx = x - 3 if k > 0 else x + w - 3
    arcade.draw_lrbt_rectangle_filled(kx, kx + 6, y + h * 0.25, y + h * 0.7, (120, 80, 40))
    for i in range(sp._bs_koker):
        arcade.draw_line(kx + 1 + i, y + h * 0.7, kx + 1 + i, y + h * 0.7 + 5, (230, 60, 60), 1)
    # De boog (iets meer gebogen als je net schiet)
    bx = x + w + 3 if k > 0 else x - 3
    span = 6 + sp._bs_span * 0.4
    arcade.draw_arc_outline(bx - k * span / 2, y + h * 0.55, span * 2, h * 0.9, (140, 90, 40),
                            -90 if k > 0 else 90, 90 if k > 0 else 270, 3)
    arcade.draw_line(bx - k * span, y + h * 0.1, bx - k * span, y + h, (230, 230, 230), 1)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 190, x + 190, y - 10, y + 22, (0, 0, 0, 150))
    arcade.draw_text("Pijlen:", x - 180, y, (170, 230, 150), 12, bold=True)
    for i in range(KOKER_MAX):
        px = x - 105 + i * 16
        kleur = (230, 60, 60) if i < sp._bs_koker else (90, 90, 90)
        arcade.draw_line(px, y - 2, px, y + 16, (150, 100, 50) if i < sp._bs_koker else (90, 90, 90), 3)
        arcade.draw_triangle_filled(px, y + 20, px - 3, y + 14, px + 3, y + 14, kleur)
    if sp._bs_koker < KOKER_MAX:
        arcade.draw_lrbt_rectangle_filled(x - 20, x - 20 + 40 * sp._bs_bijvul / BIJVULLEN, y + 2, y + 10, (170, 230, 150))
        arcade.draw_lrbt_rectangle_outline(x - 20, x + 20, y + 2, y + 10, (170, 230, 150), 1)
    arcade.draw_text("omlaag = schieten", x + 30, y, (220, 220, 220), 10)

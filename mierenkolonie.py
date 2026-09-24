# mierenkolonie.py
# De MIERENKOLONIE: jij bent de koningin-mier en een rijtje mieren loopt achter je aan!
#
#  - De mieren lopen precies over jouw pad (zoals een treintje).
#  - De mieren zijn je LEVENS: raakt een mier een spike of monster, dan ben je hem kwijt.
#    Word jij zelf geraakt, dan offert de achterste mier zich op. Pas zonder mieren ga je af.
#  - Stamp op een monster: er komt een nieuwe mier bij.
#  - Pijltje omlaag op de grond: de mieren vormen een TOREN en jij staat bovenop.
#  - Pijltje omlaag in de lucht: de mieren vormen een BRUG onder je voeten.
#  - Land je weer op echte grond, dan komen de mieren terug in je rijtje.
# Alles is vast: geen toeval.

import math
import arcade
from platforms import BlokPlatform

MIEREN_MAX = 4            # zoveel mieren kunnen er achter je aan lopen
AFSTAND = 8               # zoveel pad-puntjes zit er tussen twee mieren
PAD_STAP = 3              # om de zoveel pixels onthouden we een puntje van je pad
MIER_B = 22               # hoe breed een volg-mier is
MIER_H = 16               # hoe hoog een volg-mier is
TOREN_H = 20              # zoveel hoger kom je voor elke mier in de toren
BRUG_B = 26               # zoveel breder wordt de brug voor elke mier
BESCHERM = 60             # na een opoffering ben je zolang onkwetsbaar
ROOD = (150, 45, 35)
DONKER = (90, 25, 20)


class MierWerk(BlokPlatform):
    """Een toren of brug van mieren (je kunt erop staan)."""

    is_mierwerk = True

    def __init__(self, x, y, breedte, hoogte, soort, aantal):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort          # "toren" of "brug"
        self.aantal = aantal        # uit hoeveel mieren hij bestaat

    def teken(self):
        # Getekend als losse mieren op of naast elkaar
        for i in range(self.aantal):
            if self.soort == "toren":
                mx, my = self.x + self.breedte / 2, self.y + i * TOREN_H + TOREN_H / 2
            else:
                mx, my = self.x + i * BRUG_B + BRUG_B / 2, self.y + self.hoogte / 2
            teken_mier(mx, my, 1.0, 1 if i % 2 == 0 else -1, i * 3, vast=True)


def teken_mier(cx, cy, schaal, kant, stap, vast=False, kroon=False):
    """Teken één mier: drie lijfdelen, zes pootjes en voelsprietjes."""
    s = schaal
    # Pootjes (bewegen tijdens het lopen)
    beweeg = 0 if vast else math.sin(stap * 0.5) * 3 * s
    for i, dx in enumerate((-6, 0, 6)):
        wiebel = beweeg if i % 2 == 0 else -beweeg
        arcade.draw_line(cx + dx * s, cy, cx + dx * s + wiebel - 3 * s, cy - 8 * s, DONKER, 2)
        arcade.draw_line(cx + dx * s, cy, cx + dx * s - wiebel + 3 * s, cy - 8 * s, DONKER, 2)
    # Achterlijf, borststuk en kop
    arcade.draw_ellipse_filled(cx - kant * 8 * s, cy + 1 * s, 12 * s, 10 * s, ROOD)
    arcade.draw_circle_filled(cx, cy + 1 * s, 4 * s, ROOD)
    arcade.draw_circle_filled(cx + kant * 7 * s, cy + 3 * s, 5 * s, ROOD)
    arcade.draw_circle_filled(cx + kant * 9 * s, cy + 4 * s, 1.6 * s, (255, 255, 255))
    # Voelsprietjes
    arcade.draw_line(cx + kant * 8 * s, cy + 7 * s, cx + kant * 12 * s, cy + 13 * s, DONKER, 2)
    arcade.draw_line(cx + kant * 6 * s, cy + 7 * s, cx + kant * 7 * s, cy + 14 * s, DONKER, 2)
    if kroon:
        ky = cy + 8 * s
        kx = cx + kant * 6 * s
        arcade.draw_polygon_filled([(kx - 5, ky), (kx + 5, ky), (kx + 5, ky + 5), (kx + 2, ky + 2),
                                    (kx, ky + 6), (kx - 2, ky + 2), (kx - 5, ky + 5)], (255, 210, 40))


def reset(sp):
    """Weer met 4 mieren beginnen, zonder toren of brug."""
    sp._mk_aantal = MIEREN_MAX
    sp._mk_pad = []           # onthouden puntjes van jouw pad: (x, y)
    sp._mk_werk = None        # de toren of brug die er nu staat (of None)
    sp._mk_poef = []          # wolkjes van verloren mieren: [x, y, t]
    sp._mk_t = 0


def _vul_pad(sp):
    """Alle mieren staan (weer) op jouw plek, bv. na een toren of brug."""
    sp._mk_pad = [(sp.x + sp.breedte / 2, sp.y)] * (MIEREN_MAX * AFSTAND + 1)


def mier_posities(sp):
    """Waar lopen de volg-mieren nu? Lijst met (midden-x, onderkant-y), dichtstbij eerst."""
    if sp._mk_werk is not None:
        return []                              # ze zitten in de toren of brug
    if not sp._mk_pad:
        _vul_pad(sp)
    uit = []
    for i in range(sp._mk_aantal):
        index = max(0, len(sp._mk_pad) - 1 - (i + 1) * AFSTAND)
        uit.append(sp._mk_pad[index])
    return uit


def mier_rechthoek(pos):
    """De rechthoek (x, y, b, h) van een volg-mier, voor botsingen."""
    return pos[0] - MIER_B / 2, pos[1], MIER_B, MIER_H


def stap(sp):
    """Elke stap: pad onthouden en wolkjes laten verdwijnen."""
    sp._mk_t += 1
    if sp._mk_werk is None:
        if not sp._mk_pad:
            _vul_pad(sp)
        punt = (sp.x + sp.breedte / 2, sp.y)
        laatste = sp._mk_pad[-1]
        if math.hypot(punt[0] - laatste[0], punt[1] - laatste[1]) >= PAD_STAP:
            sp._mk_pad.append(punt)
            if len(sp._mk_pad) > MIEREN_MAX * AFSTAND + 1:
                sp._mk_pad.pop(0)
    for p in sp._mk_poef:
        p[2] += 1
    sp._mk_poef = [p for p in sp._mk_poef if p[2] < 25]


def mier_kwijt(sp, index=None):
    """Een mier is weg (geraakt of opgeofferd). index = welke; None = de achterste."""
    if sp._mk_aantal <= 0:
        return
    posities = mier_posities(sp)
    if index is None:
        index = sp._mk_aantal - 1
    if posities and index < len(posities):
        sp._mk_poef.append([posities[index][0], posities[index][1] + MIER_H / 2, 0])
    sp._mk_aantal -= 1


def mier_erbij(sp):
    """Een monster opgegeten: er komt een mier bij (als er plek is)."""
    if sp._mk_aantal < MIEREN_MAX:
        sp._mk_aantal += 1


def bescherm(sp):
    """Je wordt geraakt. Offert een mier zich op? Geeft True als jij het overleeft."""
    if sp._mk_aantal <= 0 or sp._mk_werk is not None:
        return False
    sp._mk_poef.append([sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2, 0])
    mier_kwijt(sp)
    sp.onkwetsbaar_timer = BESCHERM
    return True


def bouw(sp):
    """Pijltje omlaag: toren (op de grond) of brug (in de lucht). Staat er al iets? Dan laat je los.
    Geeft het nieuwe MierWerk terug (of None)."""
    if sp._mk_werk is not None:
        los(sp)
        return None
    n = sp._mk_aantal
    if n <= 0:
        return None
    if sp.staat_op_grond:
        h = n * TOREN_H
        werk = MierWerk(sp.x + sp.breedte / 2 - MIER_B / 2, sp.y, MIER_B, h, "toren", n)
        sp.y += h                               # jij staat bovenop de toren
        sp.snelheid_y = 0
    else:
        b = n * BRUG_B
        if sp.kijkt_rechts:
            bx = sp.x - 6
        else:
            bx = sp.x + sp.breedte + 6 - b
        werk = MierWerk(bx, sp.y - 14, b, 14, "brug", n)
    sp._mk_werk = werk
    return werk


def los(sp):
    """De toren of brug valt uit elkaar: de mieren komen terug in je rijtje."""
    sp._mk_werk = None
    _vul_pad(sp)


def op_echte_grond(sp):
    """Je landde op echte grond: de mieren komen terug uit de toren of brug."""
    if sp._mk_werk is not None:
        los(sp)


def teken(sp):
    """Teken de volg-mieren, de wolkjes en de koningin."""
    t = sp._mk_t
    for p in sp._mk_poef:
        r = 6 + p[2]
        arcade.draw_circle_outline(p[0], p[1], r, (255, 255, 255, max(0, 255 - p[2] * 10)), 2)
    posities = mier_posities(sp)
    for i in range(len(posities) - 1, -1, -1):
        px, py = posities[i]
        # De mier kijkt de kant op waar het volgende stukje pad heen gaat
        voor = posities[i - 1] if i > 0 else (sp.x + sp.breedte / 2, sp.y)
        kant = 1 if voor[0] >= px else -1
        teken_mier(px, py + 8, 1.0, kant, t + i * 4)
    # De koningin: grotere mier met een kroontje
    kant = 1 if sp.kijkt_rechts else -1
    stap_teller = t if abs(sp.snelheid_x) > 0.5 else 0
    if sp.onkwetsbaar_timer > 0 and (t // 4) % 2 == 0:
        return                                  # knipperen na een opoffering
    teken_mier(sp.x + sp.breedte / 2, sp.y + 12, 1.45, kant, stap_teller, kroon=True)


def teken_hud(sp, x, y):
    """Balkje bovenin: hoeveel mieren je hebt en wat pijltje omlaag doet."""
    arcade.draw_lrbt_rectangle_filled(x - 220, x + 220, y - 10, y + 22, (0, 0, 0, 150))
    arcade.draw_text("Mieren:", x - 210, y, (255, 200, 170), 12, bold=True)
    for i in range(MIEREN_MAX):
        mx = x - 130 + i * 26
        if i < sp._mk_aantal:
            teken_mier(mx, y + 4, 0.8, 1, 0, vast=True)
        else:
            arcade.draw_circle_outline(mx, y + 6, 6, (120, 80, 70), 1)
    if sp._mk_werk is not None:
        tekst = "omlaag = mieren loslaten"
    else:
        tekst = "omlaag: toren (grond) / brug (lucht)"
    arcade.draw_text(tekst, x - 15, y, (230, 230, 230), 10)

# spinnenheld.py
# De SPINNENHELD: een kleine spin die met webben slingert!
#
#  In de lucht, pijltje omlaag : schiet een web schuin omhoog. Raakt het een blok,
#                                dan slinger je eraan (links/rechts = extra zwaai).
#                                Springen of nog eens omlaag = loslaten (met je vaart!).
#  Op de grond, pijltje omlaag : schiet een webnet vooruit. Een monster dat geraakt
#                                wordt, zit 5 seconden in een cocon (kan niks).
# Alles is vast: geen toeval.

import math
import arcade
from instellingen import ZWAARTEKRACHT

WEB_BEREIK = 330          # zo ver reikt je slinger-web
WEB_MIN = 60              # het touw is minstens zo lang
ZWAAI = 0.18              # zo hard geeft links/rechts extra zwaai
MAX_SNELHEID = 13         # sneller dan dit slinger je niet
LOS_BOOST = 4             # springen om los te laten geeft een zetje omhoog
NET_SNELHEID = 10         # zo snel vliegt een webnet
NET_BEREIK = 300          # zo ver vliegt een webnet
COCON = 300               # zo lang zit een monster in een cocon (5 seconden)
MIS_TIJD = 12             # zo lang zie je een web dat niks raakte


def reset(sp):
    sp._sh_anker = None       # (x, y) waar je web vastzit, of None
    sp._sh_lengte = 0         # hoe lang je web is
    sp._sh_netten = []        # vliegende webnetten {"x", "y", "r", "af"}
    sp._sh_coconnen = []      # monsters die in een cocon zitten
    sp._sh_mis = None         # (x, y, t): een web dat niks raakte
    sp._sh_t = 0
    sp._sh_vaart = None       # vaart opzij na het loslaten (tot je landt)


def _vast_blok(x, y, platforms):
    """Zit er op (x, y) een vast blok? Geef het terug (of None)."""
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and p.x <= x <= p.x + p.breedte and p.y <= y <= p.y + p.hoogte):
            return p
    return None


def web(sp, platforms):
    """Pijltje omlaag: loslaten, slinger-web (in de lucht) of webnet (op de grond)."""
    if sp._sh_anker is not None:
        los(sp)
        return True
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    kant = 1 if sp.kijkt_rechts else -1
    if sp.staat_op_grond:
        sp._sh_netten.append({"x": cx + kant * sp.breedte / 2, "y": cy, "r": kant, "af": 0})
        return True
    # Slinger-web: schuin omhoog, in stapjes van 6 pixels tot het een blok raakt
    dx, dy = kant * 0.7071, 0.7071
    for i in range(1, int(WEB_BEREIK / 6) + 1):
        hx, hy = cx + dx * i * 6, cy + dy * i * 6
        if _vast_blok(hx, hy, platforms) is not None:
            sp._sh_anker = (hx, hy)
            sp._sh_lengte = max(WEB_MIN, math.hypot(hx - cx, hy - cy))
            return True
    sp._sh_mis = (cx + dx * WEB_BEREIK, cy + dy * WEB_BEREIK, MIS_TIJD)
    return False


def los(sp, sprong=False):
    """Laat het web los; je vliegt verder met je vaart (springen geeft een zetje omhoog)."""
    sp._sh_anker = None
    sp._sh_vaart = sp.snelheid_x          # je slinger-vaart blijft (tot je landt)
    if sprong:
        sp.snelheid_y = max(sp.snelheid_y, 0) + LOS_BOOST


def slinger(sp, platforms, level_breedte):
    """Slinger-natuurkunde: je hangt aan een touw van vaste lengte rond het ankerpunt."""
    ax, ay = sp._sh_anker
    # Zwaartekracht en extra zwaai met links/rechts
    sp.snelheid_y -= ZWAARTEKRACHT
    if sp.links_ingedrukt and not sp.rechts_ingedrukt:
        sp.snelheid_x -= ZWAAI
        sp.kijkt_rechts = False
    elif sp.rechts_ingedrukt and not sp.links_ingedrukt:
        sp.snelheid_x += ZWAAI
        sp.kijkt_rechts = True
    snel = math.hypot(sp.snelheid_x, sp.snelheid_y)
    if snel > MAX_SNELHEID:
        sp.snelheid_x *= MAX_SNELHEID / snel
        sp.snelheid_y *= MAX_SNELHEID / snel
    # Nieuwe plek (midden van de spin), en dan het touw strak trekken
    cx = sp.x + sp.breedte / 2 + sp.snelheid_x
    cy = sp.y + sp.hoogte / 2 + sp.snelheid_y
    ddx, ddy = cx - ax, cy - ay
    afstand = math.hypot(ddx, ddy)
    if afstand < sp._sh_lengte:
        sp._sh_lengte = max(WEB_MIN, afstand)      # het web rolt zich op: zo blijft het altijd strak
    if afstand > sp._sh_lengte and afstand > 0:
        nx, ny = ddx / afstand, ddy / afstand
        cx, cy = ax + nx * sp._sh_lengte, ay + ny * sp._sh_lengte
        radiaal = sp.snelheid_x * nx + sp.snelheid_y * ny
        if radiaal > 0:                            # alleen de 'weg van het anker'-vaart haalt het touw weg
            sp.snelheid_x -= radiaal * nx
            sp.snelheid_y -= radiaal * ny
    oud_x, oud_y = sp.x, sp.y
    sp.x = cx - sp.breedte / 2
    sp.y = cy - sp.hoogte / 2
    sp.staat_op_grond = False
    # Tegen een blok aan geslingerd? Dan terug en loslaten (de gewone natuurkunde doet de rest)
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and sp._overlapt(p)):
            sp.x, sp.y = oud_x, oud_y
            sp.snelheid_x *= 0.3
            sp.snelheid_y = min(sp.snelheid_y, 0)
            los(sp)
            break
    sp.x = max(0, min(level_breedte - sp.breedte, sp.x))


def vlieg(sp, L, R, snelheid):
    """Na het loslaten: je vliegt door met je vaart; links/rechts stuurt een beetje bij."""
    if sp.staat_op_grond:
        sp._sh_vaart = None                    # geland: weer gewoon lopen
        sp.snelheid_x = -snelheid if L else (snelheid if R else 0)
        return
    doel = -snelheid if L else (snelheid if R else sp._sh_vaart)
    if abs(sp._sh_vaart) > abs(doel) and (doel == 0 or (doel > 0) == (sp._sh_vaart > 0)):
        doel = sp._sh_vaart                    # in dezelfde richting: je snelle vaart houden
    sp._sh_vaart += (doel - sp._sh_vaart) * 0.08
    sp.snelheid_x = sp._sh_vaart
    if L or R:
        sp.kijkt_rechts = R


def stap(sp, platforms):
    """Elke stap: webnetten vliegen, cocons worden zwakker."""
    sp._sh_t += 1
    if sp._sh_mis is not None:
        x, y, t = sp._sh_mis
        sp._sh_mis = (x, y, t - 1) if t > 1 else None
    klaar = []
    for n in sp._sh_netten:
        n["x"] += NET_SNELHEID * n["r"]
        n["af"] += NET_SNELHEID
        if n["af"] >= NET_BEREIK or _vast_blok(n["x"], n["y"], platforms) is not None:
            klaar.append(n)
    sp._sh_netten = [n for n in sp._sh_netten if n not in klaar]
    for v in sp._sh_coconnen:
        v._cocon -= 1
    sp._sh_coconnen = [v for v in sp._sh_coconnen if v._cocon > 0]


def net_raakt(net, v):
    return (v.x - 8 <= net["x"] <= v.x + getattr(v, "breedte", 32) + 8
            and v.y - 8 <= net["y"] <= v.y + getattr(v, "hoogte", 32) + 8)


def pak_in(sp, v):
    """Een monster wordt ingepakt in een cocon."""
    v._cocon = COCON
    if v not in sp._sh_coconnen:
        sp._sh_coconnen.append(v)


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_net(x, y, grootte):
    for i in range(4):
        h = math.radians(i * 45)
        arcade.draw_line(x - math.cos(h) * grootte, y - math.sin(h) * grootte,
                         x + math.cos(h) * grootte, y + math.sin(h) * grootte, (240, 240, 250), 1)
    arcade.draw_circle_outline(x, y, grootte * 0.6, (240, 240, 250), 1)
    arcade.draw_circle_outline(x, y, grootte, (240, 240, 250), 1)


def teken(sp):
    t = sp._sh_t
    # Cocons om ingepakte monsters
    for v in sp._sh_coconnen:
        vx, vy = v.x + v.breedte / 2, v.y + v.hoogte / 2
        arcade.draw_ellipse_filled(vx, vy, v.breedte + 10, v.hoogte + 10, (235, 235, 240, 220))
        for i in range(4):
            yy = v.y + 4 + i * (v.hoogte / 3.5)
            arcade.draw_line(v.x - 4, yy, v.x + v.breedte + 4, yy + 5, (200, 200, 210), 1)
    for n in sp._sh_netten:
        _teken_net(n["x"], n["y"], 10)
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    # Het slinger-web
    if sp._sh_anker is not None:
        ax, ay = sp._sh_anker
        arcade.draw_line(cx, cy + 4, ax, ay, (245, 245, 250), 2)
        _teken_net(ax, ay, 6)
    if sp._sh_mis is not None:
        mx, my, mt = sp._sh_mis
        arcade.draw_line(cx, cy, mx, my, (245, 245, 250, mt * 20), 1)
    # De spin: rond lijfje, acht pootjes, grote ogen en een klein petje
    k = 1 if sp.kijkt_rechts else -1
    beweegt = abs(sp.snelheid_x) > 0.5
    for i in range(4):
        for kant in (-1, 1):
            wiebel = math.sin(t * 0.5 + i) * 3 if beweegt else 0
            px = cx + kant * 10
            py = cy - 2 + i * 3
            knie_x = px + kant * 9
            knie_y = py + 6 + wiebel
            arcade.draw_line(px, py, knie_x, knie_y, (40, 30, 50), 2)
            arcade.draw_line(knie_x, knie_y, knie_x + kant * 4, cy - 14 + i * 2 - wiebel, (40, 30, 50), 2)
    arcade.draw_circle_filled(cx, cy, 13, (60, 45, 80))
    arcade.draw_circle_filled(cx, cy - 3, 7, (90, 70, 120))                      # buikje
    for dx in (-5, 5):
        arcade.draw_circle_filled(cx + dx + k * 2, cy + 5, 4.5, (255, 255, 255))
        arcade.draw_circle_filled(cx + dx + k * 3, cy + 5, 2.2, (20, 20, 30))
    arcade.draw_arc_filled(cx, cy + 10, 20, 12, (240, 180, 40), 0, 180)          # petje
    arcade.draw_lrbt_rectangle_filled(min(cx, cx + k * 14), max(cx, cx + k * 14), cy + 9, cy + 12,
                                      (220, 160, 30))


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 230, x + 230, y - 10, y + 22, (0, 0, 0, 150))
    if sp._sh_anker is not None:
        tekst = "slingeren! links/rechts = zwaaien, springen of omlaag = loslaten"
    else:
        tekst = "omlaag: in de lucht = slinger-web, op de grond = webnet"
    arcade.draw_text(tekst, x, y + 1, (240, 240, 250), 11, anchor_x="center")

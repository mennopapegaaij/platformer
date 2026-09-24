# schilder.py
# De SCHILDER: spuit verf op de grond, en elke kleur doet iets anders!
#
#  Toets 1 = BLAUW  : trampoline (land je erop, dan stuiter je superhoog)
#  Toets 2 = ROOD   : snelweg (je rent twee keer zo snel)
#  Toets 3 = GROEN  : bedekt spikes (dan zijn ze onschadelijk)
#  Toets 4 = GEEL   : glijbaan (superglad)
#  Pijltje omlaag   : spuit een verfvlek op de grond onder je (ook vanuit de lucht)
#
# Elke kleur heeft een eigen voorraad die langzaam weer bijvult. Geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT

KLEUREN = ["blauw", "rood", "groen", "geel"]
RGB = {"blauw": (60, 140, 255), "rood": (235, 60, 50), "groen": (70, 200, 80), "geel": (250, 215, 40)}
UITLEG = {"blauw": "trampoline", "rood": "snelweg", "groen": "spikes bedekken", "geel": "glijbaan"}
VOORRAAD_MAX = 100
KOST = 25                 # een verfvlek kost zoveel verf
BIJVULLEN = 0.08          # zoveel verf komt er per stapje vanzelf bij (per kleur)
VLEK_BREEDTE = 70         # zo breed is een verfvlek
MAX_VLEKKEN = 14          # meer vlekken? Dan verdwijnt de oudste
TRAMPOLINE = 1.8          # zo hard stuiter je van blauwe verf (keer een gewone sprong)
SNELWEG = 2.0             # zo snel ren je op rode verf
GLAD = 0.03               # zo glad is gele verf (klein = heel glad)


def reset(sp):
    sp._sv_kleur = "blauw"
    sp._sv_voorraad = {k: VOORRAAD_MAX for k in KLEUREN}
    sp._sv_vlekken = []       # {"p": platform, "x0", "x1", "kleur", "t"}
    sp._sv_spikes = []        # spikes die je groen hebt geverfd
    sp._sv_onder = None       # op welke kleur je het laatst stond
    sp._sv_t = 0
    sp._sv_spetters = []      # [x, y, vx, vy, leven, kleur]


def kies_kleur(sp, nummer):
    if 1 <= nummer <= len(KLEUREN):
        sp._sv_kleur = KLEUREN[nummer - 1]
        return True
    return False


def _kleur_op(sp, platform):
    """Welke verf ligt er op dit platform, precies onder het midden van de speler?"""
    cx = sp.x + sp.breedte / 2
    for v in reversed(sp._sv_vlekken):           # nieuwste vlek eerst
        if v["p"] is platform and v["x0"] <= cx <= v["x1"]:
            return v["kleur"]
    return None


def kleur_onder(sp):
    """Op welke verf sta je (of stond je het laatst, als je in de lucht bent)?"""
    if sp.staat_op_grond:
        sp._sv_onder = _kleur_op(sp, getattr(sp, "_gelande_platform", None))
    return sp._sv_onder


def loop(sp, L, R, snelheid):
    """Lopen: rood = twee keer zo snel, geel = glad."""
    kleur = kleur_onder(sp)
    kant = -1 if (L and not R) else (1 if (R and not L) else 0)
    if kant != 0:
        sp.kijkt_rechts = kant > 0
    doel = kant * snelheid * (SNELWEG if kleur == "rood" else 1)
    if kleur == "geel":
        # glad: je snelheid verandert maar heel langzaam (vaart houd je, afremmen kan bijna niet)
        sp.snelheid_x += (doel - sp.snelheid_x) * GLAD if kant != 0 else (-sp.snelheid_x * GLAD)
    else:
        sp.snelheid_x = doel


def trampoline(sp, platform):
    """Net geland op dit platform: is het blauw? Dan stuiter je omhoog (geeft True)."""
    if _kleur_op(sp, platform) == "blauw":
        sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * TRAMPOLINE
        cx = sp.x + sp.breedte / 2
        for i in range(8):
            h = math.radians(20 + i * 20)
            _spetter(sp, cx, sp.y, math.cos(h) * 3, math.sin(h) * 3, "blauw")
        return True
    return False


def _spetter(sp, x, y, vx, vy, kleur):
    sp._sv_spetters.append([x, y, vx, vy, 20, kleur])


def stap(sp):
    """Elke stap: verf bijvullen en spettertjes laten vallen."""
    sp._sv_t += 1
    for k in KLEUREN:
        sp._sv_voorraad[k] = min(VOORRAAD_MAX, sp._sv_voorraad[k] + BIJVULLEN)
    for s in sp._sv_spetters:
        s[0] += s[2]
        s[1] += s[3]
        s[3] -= 0.25
        s[4] -= 1
    sp._sv_spetters = [s for s in sp._sv_spetters if s[4] > 0]
    # Rode snelweg: vuurstreepjes achter je
    if kleur_onder(sp) == "rood" and abs(sp.snelheid_x) > 5 and sp._sv_t % 3 == 0:
        achter = -1 if sp.snelheid_x > 0 else 1
        _spetter(sp, sp.x + sp.breedte / 2 + achter * sp.breedte / 2, sp.y + 4, achter, 0.5, "rood")


def spuit(sp, platforms, vijanden):
    """Pijltje omlaag: spuit een verfvlek op het platform onder je. Geeft True als het lukte."""
    kleur = sp._sv_kleur
    if sp._sv_voorraad[kleur] < KOST:
        return False
    cx = sp.x + sp.breedte / 2
    # Zoek het hoogste platform onder je voeten (daar komt de verf op)
    doel = None
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and p.x <= cx <= p.x + p.breedte and p.y + p.hoogte <= sp.y + 2):
            if doel is None or p.y + p.hoogte > doel.y + doel.hoogte:
                doel = p
    if doel is None:
        return False                              # onder je is niks (een kuil): de verf valt weg
    x0 = max(doel.x, cx - VLEK_BREEDTE / 2)
    x1 = min(doel.x + doel.breedte, cx + VLEK_BREEDTE / 2)
    sp._sv_vlekken.append({"p": doel, "x0": x0, "x1": x1, "kleur": kleur, "t": 0})
    if len(sp._sv_vlekken) > MAX_VLEKKEN:
        sp._sv_vlekken.pop(0)
    sp._sv_voorraad[kleur] -= KOST
    top = doel.y + doel.hoogte
    # Groen op spikes: die worden bedekt en zijn dan onschadelijk
    if kleur == "groen":
        for v in vijanden:
            if (getattr(v, "is_spike", False) and hasattr(v, "aantal") and abs(v.y - top) < 6
                    and v.x < x1 and v.x + v.breedte > x0):
                v.geverfd = True
                if v not in sp._sv_spikes:
                    sp._sv_spikes.append(v)
    # Spettertjes van de spuitbus naar beneden
    for i in range(10):
        _spetter(sp, cx + (i - 4.5) * 6, sp.y, (i - 4.5) * 0.3, -2 - (i % 3), kleur)
    return True


# ===========================================================================
# Tekenen
# ===========================================================================
def teken(sp):
    t = sp._sv_t
    # Verfvlekken op de platforms
    for v in sp._sv_vlekken:
        top = v["p"].y + v["p"].hoogte
        kl = RGB[v["kleur"]]
        arcade.draw_lrbt_rectangle_filled(v["x0"], v["x1"], top - 3, top + 3, kl)
        for i in range(int((v["x1"] - v["x0"]) // 14)):              # druppeltjes langs de rand
            dx = v["x0"] + 7 + i * 14
            arcade.draw_circle_filled(dx, top - 3 - (i % 2) * 2, 3, kl)
        if v["kleur"] == "blauw":                                      # veertje-streepjes
            for i in range(int((v["x1"] - v["x0"]) // 20)):
                dx = v["x0"] + 10 + i * 20
                arcade.draw_line(dx - 4, top + 4, dx + 4, top + 8, (200, 230, 255), 2)
        elif v["kleur"] == "rood":                                     # pijltjes vooruit
            for i in range(int((v["x1"] - v["x0"]) // 24)):
                dx = v["x0"] + 12 + i * 24
                arcade.draw_triangle_filled(dx + 5, top + 6, dx - 3, top + 3, dx - 3, top + 9, (255, 200, 190))
        elif v["kleur"] == "geel":                                     # glimmertjes
            if t % 20 < 10:
                arcade.draw_circle_filled(v["x0"] + (t * 3) % max(1, int(v["x1"] - v["x0"])), top + 4, 2,
                                          (255, 255, 255))
    # Groen geverfde spikes: een dikke laag groene smurrie eroverheen
    for s in sp._sv_spikes:
        arcade.draw_lrbt_rectangle_filled(s.x - 2, s.x + s.breedte + 2, s.y, s.y + s.hoogte * 0.7, (70, 200, 80))
        for i in range(s.aantal * 2):
            arcade.draw_circle_filled(s.x + 5 + i * (s.breedte - 10) / max(1, s.aantal * 2 - 1),
                                      s.y + s.hoogte * 0.7, 6, (70, 200, 80))
    for x, y, vx, vy, leven, kleur in sp._sv_spetters:
        arcade.draw_circle_filled(x, y, 2 + leven / 10, RGB[kleur])
    # De schilder: overall met verfvlekken, een baret en een spuitbus
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.65, (245, 245, 240))
    for i, kl in enumerate(KLEUREN):                                   # vlekjes op zijn overall
        arcade.draw_circle_filled(x + 6 + i * (w - 12) / 3, y + h * (0.2 + (i % 2) * 0.22), 2.5, RGB[kl])
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h * 0.6, y + h - 5, (240, 200, 160))
    arcade.draw_circle_filled(cx - 5 + k * 2, y + h * 0.78, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 5 + k * 2, y + h * 0.78, 2.5, (20, 20, 30))
    # Baret (in je gekozen kleur)
    arcade.draw_ellipse_filled(cx - k * 2, y + h - 3, w * 0.85, 9, RGB[sp._sv_kleur])
    arcade.draw_circle_filled(cx - k * 2, y + h + 2, 2, RGB[sp._sv_kleur])
    # Spuitbus in de hand
    bx = x + w + 1 if k > 0 else x - 9
    arcade.draw_lrbt_rectangle_filled(bx, bx + 8, y + h * 0.25, y + h * 0.55, RGB[sp._sv_kleur])
    arcade.draw_lrbt_rectangle_filled(bx + 2, bx + 6, y + h * 0.55, y + h * 0.62, (60, 60, 60))


def teken_hud(sp, x, y):
    """Balkje bovenin: de 4 verfpotjes met hun voorraad; de gekozen kleur licht op."""
    arcade.draw_lrbt_rectangle_filled(x - 250, x + 250, y - 14, y + 26, (0, 0, 0, 150))
    for i, k in enumerate(KLEUREN):
        l = x - 240 + i * 100
        gekozen = k == sp._sv_kleur
        if gekozen:
            arcade.draw_lrbt_rectangle_outline(l - 3, l + 92, y - 12, y + 24, (255, 255, 255), 2)
        arcade.draw_text("%d" % (i + 1), l, y + 8, (255, 255, 255), 10, bold=True)
        arcade.draw_lrbt_rectangle_filled(l + 12, l + 12 + 74 * sp._sv_voorraad[k] / VOORRAAD_MAX, y + 9, y + 19, RGB[k])
        arcade.draw_lrbt_rectangle_outline(l + 12, l + 86, y + 9, y + 19, RGB[k], 1)
        arcade.draw_text(UITLEG[k], l + 12, y - 8, RGB[k] if gekozen else (190, 190, 190), 9, bold=gekozen)
    arcade.draw_text("omlaag = spuiten", x + 162, y + 2, (230, 230, 230), 9)

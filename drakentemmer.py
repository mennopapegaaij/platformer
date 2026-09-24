# drakentemmer.py
# De DRAKENTEMMER: je draak groeit tijdens het spelen op!
#
#   Ei  ->  Baby  ->  Jonge draak  ->  Grote draak
#
# Je krijgt GROEIPUNTEN door verder te komen in het level en door monsters te
# verslaan (die eet je draak op). Bij genoeg punten groeit hij naar de volgende fase.
#
#   Ei           : rollen en springen (hoe meer punten, hoe meer barstjes)
#   Baby         : 1 keer fladderen in de lucht
#   Jonge draak  : 3 keer fladderen + vuurbal spuwen (pijltje omlaag)
#   Grote draak  : echt vliegen (springknop vasthouden) + grote vuurballen
#                  + VUURSTORM als de superbalk vol is (verslaat monsters en smelt spikes!)
#
# ENERGIE: vliegen en vuur spuwen kosten energie. Op de grond laadt het op,
# en een monster opeten geeft ook energie. Alles is vast: geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

# De vier fases: naam, hoeveel groeipunten nodig, grootte, sprong, snelheid, fladders
FASES = [
    {"naam": "Ei",          "punten": 0,   "grootte": 0.75, "sprong": 0.95, "snel": 1.0, "fladder": 0},
    {"naam": "Baby",        "punten": 40,  "grootte": 0.85, "sprong": 1.0,  "snel": 1.0, "fladder": 1},
    {"naam": "Jonge draak", "punten": 150, "grootte": 1.0,  "sprong": 1.0,  "snel": 1.1, "fladder": 3},
    {"naam": "Grote draak", "punten": 350, "grootte": 1.3,  "sprong": 1.1,  "snel": 1.2, "fladder": 0},
]
PUNTEN_PER_AFSTAND = 10   # elke 10 pixels verder = 1 groeipunt
PUNTEN_PER_MONSTER = 25   # een monster opeten = zoveel groeipunten
ENERGIE_MAX = 100
ENERGIE_OPLADEN = 0.35    # zoveel energie erbij per stapje op de grond
ENERGIE_MONSTER = 30      # een monster opeten geeft zoveel energie
FLADDER_KRACHT = 8        # hoe hard een fladder je omhoog duwt
VLIEG_DUW = 0.9           # grote draak: zo hard duwt vliegen je omhoog
VLIEG_MAX = 5             # grote draak: zo snel vlieg je hoogstens omhoog
VLIEG_KOST = 0.9          # grote draak: zoveel energie kost vliegen per stapje
VUUR_KOST = 20            # een vuurbal kost zoveel energie
VUUR_SNELHEID = 9         # zo snel vliegt een vuurbal
VUUR_LEVEN = 60           # zo lang vliegt een vuurbal (stapjes)
SUPER_PER_MONSTER = 34    # een monster opeten vult de superbalk met zoveel (3 = vol)
STORM_BEREIK = 260        # zo ver reikt de vuurstorm
GROEI_FEEST = 70          # zo lang duurt het groei-feestje

GROEN = (70, 170, 80)
LICHTGROEN = (160, 220, 120)
BUIK = (240, 220, 150)


def fase(sp):
    return FASES[sp._dt_fase]


def reset(sp):
    """Terug naar een ei, zonder punten."""
    sp._dt_fase = 0
    sp._dt_punten = 0
    sp._dt_start_x = None      # waar je begon (voor de afstands-punten)
    sp._dt_verste = 0          # hoe ver je al bent geweest
    sp._dt_energie = ENERGIE_MAX
    sp._dt_super = 0
    sp._dt_fladders = 0
    sp._dt_vuurballen = []     # [x, y, richting, leven, groot]
    sp._dt_storm = 0           # tikt af tijdens de vuurstorm (voor de tekening)
    sp._dt_storm_nieuw = False # het spel moet de vuurstorm nog uitvoeren
    sp._dt_feest = 0           # groei-feestje (tekst + sterretjes)
    sp._dt_t = 0
    sp._dt_deeltjes = []


def _deeltje(sp, x, y, vx, vy, leven, kleur, grootte):
    sp._dt_deeltjes.append([x, y, vx, vy, leven, leven, kleur, grootte])


def punten_erbij(sp, aantal):
    """Groeipunten erbij; groei naar de volgende fase als het genoeg is."""
    sp._dt_punten += aantal
    while (sp._dt_fase + 1 < len(FASES)
           and sp._dt_punten >= FASES[sp._dt_fase + 1]["punten"]):
        sp._dt_fase += 1
        f = fase(sp)
        sp.zet_grootte(f["grootte"], 0)
        sp._dt_feest = GROEI_FEEST
        sp._dt_energie = ENERGIE_MAX           # groeien = vol energie
        cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
        for i in range(20):
            h = math.radians(i * 18)
            _deeltje(sp, cx, cy, math.cos(h) * 4, math.sin(h) * 4, 30, (255, 230, 90), 4)


def monster_opgegeten(sp, super_vullen=True):
    """Het spel meldt: je draak heeft een monster verslagen (en opgegeten).
    (Monsters van een vuurstorm vullen de superbalk niet, anders is hij meteen weer vol.)"""
    sp._dt_energie = min(ENERGIE_MAX, sp._dt_energie + ENERGIE_MONSTER)
    if super_vullen and sp._dt_fase == len(FASES) - 1:
        sp._dt_super = min(100, sp._dt_super + SUPER_PER_MONSTER)
    punten_erbij(sp, PUNTEN_PER_MONSTER)


def stap(sp, platforms):
    """Elke stap: groeipunten voor afstand, energie opladen, vuurballen laten vliegen."""
    sp._dt_t += 1
    f = fase(sp)
    if abs(sp.grootte_factor - f["grootte"]) > 0.001:
        sp.zet_grootte(f["grootte"], 0)            # de draak heeft de grootte van zijn fase
    if sp._dt_start_x is None:
        sp._dt_start_x = sp.x
    # Groeipunten voor elk nieuw stukje dat je verder komt
    verder = sp.x - sp._dt_start_x
    if verder > sp._dt_verste + PUNTEN_PER_AFSTAND:
        erbij = int((verder - sp._dt_verste) // PUNTEN_PER_AFSTAND)
        sp._dt_verste += erbij * PUNTEN_PER_AFSTAND
        punten_erbij(sp, erbij)
    # Energie opladen op de grond
    if sp.staat_op_grond:
        sp._dt_energie = min(ENERGIE_MAX, sp._dt_energie + ENERGIE_OPLADEN)
        sp._dt_fladders = fase(sp)["fladder"]
    if sp._dt_feest > 0:
        sp._dt_feest -= 1
    if sp._dt_storm > 0:
        sp._dt_storm -= 1
    # Vuurballen vliegen; tegen een muur doven ze uit
    for v in sp._dt_vuurballen:
        v[0] += VUUR_SNELHEID * v[2]
        v[3] -= 1
        if sp._dt_t % 2 == 0:
            _deeltje(sp, v[0] - v[2] * 8, v[1], -v[2] * 0.5, 0.6, 12, (255, 180, 40), 3)
        for p in platforms:
            if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                    and p.x <= v[0] <= p.x + p.breedte and p.y <= v[1] <= p.y + p.hoogte):
                v[3] = 0
                break
    sp._dt_vuurballen = [v for v in sp._dt_vuurballen if v[3] > 0]
    # Deeltjes
    for d in sp._dt_deeltjes:
        d[0] += d[2]
        d[1] += d[3]
        d[4] -= 1
    sp._dt_deeltjes = [d for d in sp._dt_deeltjes if d[4] > 0]
    # Grote draak: vleugel-wolkjes als hij vliegt
    if sp._dt_fase == 3 and sp.vlieg_omhoog and not sp.staat_op_grond and sp._dt_t % 4 == 0:
        _deeltje(sp, sp.x + sp.breedte / 2, sp.y, 0, -1.2, 14, (230, 240, 255), 3)


def loop_snelheid(sp, snelheid):
    return snelheid * fase(sp)["snel"]


def zwaartekracht(sp, richting):
    """Vallen, en als grote draak: vliegen zolang je de knop vasthoudt en energie hebt."""
    sp.snelheid_y -= ZWAARTEKRACHT * richting
    if (sp._dt_fase == 3 and sp.vlieg_omhoog and not sp.staat_op_grond
            and sp._dt_energie > 0):
        sp.snelheid_y = min(sp.snelheid_y * richting + VLIEG_DUW, VLIEG_MAX) * richting
        sp._dt_energie = max(0, sp._dt_energie - VLIEG_KOST)


def spring(sp):
    """Op de grond springen; in de lucht fladderen (baby / jonge draak)."""
    f = fase(sp)
    if sp.staat_op_grond:
        sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * f["sprong"] * sp.zwaartekracht_richting
        return
    if sp._dt_fladders > 0:
        sp._dt_fladders -= 1
        sp.snelheid_y = FLADDER_KRACHT * sp.zwaartekracht_richting
        for i in range(6):                              # veertjes
            _deeltje(sp, sp.x + sp.breedte / 2 + (i - 2.5) * 4, sp.y + sp.hoogte / 2,
                     (i - 2.5) * 0.5, -1.5, 16, LICHTGROEN, 2.5)


def vuur(sp):
    """Pijltje omlaag: vuurbal spuwen (of vuurstorm als de superbalk vol is).
    Geeft True als er iets gebeurde."""
    if sp._dt_fase < 2:
        return False                                    # ei en baby kunnen nog geen vuur spuwen
    if sp._dt_fase == 3 and sp._dt_super >= 100:
        sp._dt_super = 0
        sp._dt_storm = 40
        sp._dt_storm_nieuw = True                       # het spel verslaat alles in de buurt
        cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
        for i in range(36):
            h = math.radians(i * 10)
            _deeltje(sp, cx, cy, math.cos(h) * 7, math.sin(h) * 7, 35, (255, 120 + (i * 7) % 120, 30), 5)
        return True
    if sp._dt_energie < VUUR_KOST:
        return False                                    # te moe
    sp._dt_energie -= VUUR_KOST
    richting = 1 if sp.kijkt_rechts else -1
    groot = sp._dt_fase == 3
    sp._dt_vuurballen.append([sp.x + sp.breedte / 2 + richting * sp.breedte / 2,
                              sp.y + sp.hoogte * 0.6, richting, VUUR_LEVEN, groot])
    return True


def vuurbal_raakt(v, obj):
    """Raakt vuurbal v dit voorwerp (monster)?"""
    r = 14 if v[4] else 9
    return (obj.x - r < v[0] < obj.x + getattr(obj, "breedte", 32) + r
            and obj.y - r < v[1] < obj.y + getattr(obj, "hoogte", 32) + r)


# ===========================================================================
# Tekenen
# ===========================================================================
def _vleugel(cx, cy, kant, grootte, klap, kleur):
    """Een vleermuis-achtige drakenvleugel (kant = -1 links, 1 rechts)."""
    punt = (cx + kant * grootte * 1.3, cy + grootte * (0.6 + klap))
    arcade.draw_triangle_filled(cx, cy, punt[0], punt[1], cx + kant * grootte * 0.9, cy - grootte * 0.2, kleur)
    arcade.draw_triangle_filled(cx, cy, punt[0], punt[1], cx + kant * grootte * 0.3, cy + grootte * 0.1,
                                (kleur[0] // 2 + 60, kleur[1] // 2 + 60, kleur[2] // 2 + 60))


def teken(sp):
    t = sp._dt_t
    for x, y, vx, vy, leven, max_leven, kleur, grootte in sp._dt_deeltjes:
        deel = leven / max_leven
        arcade.draw_circle_filled(x, y, max(1, grootte * deel),
                                  (kleur[0], kleur[1], kleur[2], int(60 + 195 * deel)))
    for v in sp._dt_vuurballen:
        r = 12 if v[4] else 8
        arcade.draw_circle_filled(v[0], v[1], r + 4, (255, 120, 20, 110))
        arcade.draw_circle_filled(v[0], v[1], r, (255, 170, 40))
        arcade.draw_circle_filled(v[0] + v[2] * 2, v[1] + 1, r * 0.5, (255, 240, 150))
    if sp._dt_storm > 0:
        r = (40 - sp._dt_storm) / 40 * STORM_BEREIK
        cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
        arcade.draw_circle_outline(cx, cy, r, (255, 140, 30, int(sp._dt_storm * 6)), 8)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx, cy = x + w / 2, y + h / 2
    k = 1 if sp.kijkt_rechts else -1
    nr = sp._dt_fase
    if nr == 0:
        # Een wiebelend ei met barstjes (meer barstjes = bijna uitkomen)
        wiebel = math.sin(t * 0.25) * 2 if abs(sp.snelheid_x) > 0.5 else 0
        arcade.draw_ellipse_filled(cx + wiebel, cy, w, h * 1.05, (245, 240, 220))
        arcade.draw_ellipse_outline(cx + wiebel, cy, w, h * 1.05, (180, 170, 140), 2)
        for i in range(3):
            arcade.draw_circle_filled(cx + wiebel - w * 0.2 + i * w * 0.2, cy - h * 0.15 + (i % 2) * h * 0.25,
                                      w * 0.07, (120, 190, 110))
        barsten = int(4 * sp._dt_punten / FASES[1]["punten"])
        for i in range(min(barsten, 4)):
            bx = cx + wiebel - w * 0.3 + i * w * 0.18
            arcade.draw_line(bx, cy + h * 0.2, bx + w * 0.08, cy + h * 0.05, (90, 80, 60), 2)
            arcade.draw_line(bx + w * 0.08, cy + h * 0.05, bx + w * 0.14, cy + h * 0.22, (90, 80, 60), 2)
    else:
        klap = math.sin(t * (0.5 if not sp.staat_op_grond else 0.15)) * 0.4
        vleugel = {1: w * 0.35, 2: w * 0.55, 3: w * 0.75}[nr]
        _vleugel(cx - k * w * 0.1, cy + h * 0.15, -k, vleugel, klap, (60, 140, 70))
        # Staart
        staart = [(cx - k * w * 0.3, y + h * 0.2), (cx - k * w * (0.85 + 0.15 * nr), y + h * 0.1),
                  (cx - k * w * 0.3, y + h * 0.4)]
        arcade.draw_polygon_filled(staart, GROEN)
        if nr == 3:
            arcade.draw_triangle_filled(staart[1][0], staart[1][1] - 6, staart[1][0] - k * 10, staart[1][1] + 2,
                                        staart[1][0], staart[1][1] + 6, (220, 80, 60))
        # Lijf en buik
        arcade.draw_ellipse_filled(cx, cy - h * 0.05, w * 0.95, h * 0.8, GROEN)
        arcade.draw_ellipse_filled(cx + k * w * 0.05, cy - h * 0.12, w * 0.55, h * 0.55, BUIK)
        # Kop
        kx, ky = cx + k * w * 0.35, y + h * 0.78
        arcade.draw_circle_filled(kx, ky, w * 0.3, GROEN)
        arcade.draw_ellipse_filled(kx + k * w * 0.22, ky - h * 0.05, w * 0.3, h * 0.22, LICHTGROEN)  # snuit
        arcade.draw_circle_filled(kx + k * w * 0.05, ky + h * 0.06, max(2, w * 0.08), (255, 255, 255))
        arcade.draw_circle_filled(kx + k * w * 0.07, ky + h * 0.06, max(1.5, w * 0.045), (20, 20, 20))
        if nr >= 2:
            # Hoorntjes
            arcade.draw_triangle_filled(kx - k * w * 0.1, ky + w * 0.25, kx - k * w * 0.02, ky + w * 0.25,
                                        kx - k * w * 0.12, ky + w * 0.45, (240, 230, 200))
        if nr == 1:
            # Stukje eierschaal op zijn hoofd
            arcade.draw_arc_filled(kx, ky + w * 0.2, w * 0.45, w * 0.3, (245, 240, 220), 0, 180)
        if nr == 3:
            # Stekels op de rug
            for i in range(3):
                sx = cx - k * w * (0.05 + i * 0.16)     # van het midden naar de staart
                arcade.draw_triangle_filled(sx - 4, y + h * 0.62, sx + 4, y + h * 0.62, sx, y + h * 0.8,
                                            (220, 80, 60))
        _vleugel(cx + k * w * 0.05, cy + h * 0.2, -k, vleugel * 0.8, -klap, (80, 170, 90))
        # Rookpluimpjes uit de neus als je genoeg energie hebt voor vuur
        if nr >= 2 and sp._dt_energie >= VUUR_KOST and t % 30 < 10:
            arcade.draw_circle_filled(kx + k * w * 0.4, ky + h * 0.05 + (t % 30), 3, (200, 200, 200, 150))
    # Groei-feestje
    if sp._dt_feest > 0:
        deel = sp._dt_feest / GROEI_FEEST
        arcade.draw_circle_outline(cx, cy, w * 0.7 + (1 - deel) * 40, (255, 230, 90, int(255 * deel)), 3)


def teken_hud(sp, x, y):
    """Balkjes bovenin: fase, groei, energie en (grote draak) superbalk."""
    f = fase(sp)
    arcade.draw_lrbt_rectangle_filled(x - 230, x + 230, y - 22, y + 24, (0, 0, 0, 150))
    arcade.draw_text("%s (%d/4)" % (f["naam"], sp._dt_fase + 1), x - 222, y + 4, (255, 230, 120), 12, bold=True)
    # Groeibalk
    if sp._dt_fase + 1 < len(FASES):
        van = f["punten"]
        tot = FASES[sp._dt_fase + 1]["punten"]
        deel = (sp._dt_punten - van) / (tot - van)
        label = "groei naar " + FASES[sp._dt_fase + 1]["naam"]
    else:
        deel, label = 1.0, "volgroeid!"
    arcade.draw_lrbt_rectangle_filled(x - 80, x - 80 + 150 * min(1, deel), y + 6, y + 16, (90, 200, 90))
    arcade.draw_lrbt_rectangle_outline(x - 80, x + 70, y + 6, y + 16, (200, 255, 200), 1)
    arcade.draw_text(label, x + 78, y + 5, (200, 255, 200), 10)
    # Energiebalk
    arcade.draw_text("energie", x - 222, y - 17, (255, 240, 120), 10)
    arcade.draw_lrbt_rectangle_filled(x - 160, x - 160 + 130 * sp._dt_energie / ENERGIE_MAX, y - 16, y - 6,
                                      (255, 220, 60))
    arcade.draw_lrbt_rectangle_outline(x - 160, x - 30, y - 16, y - 6, (255, 240, 150), 1)
    # Superbalk (alleen voor de grote draak) of uitleg
    if sp._dt_fase == 3:
        vol = sp._dt_super >= 100
        arcade.draw_text("vuurstorm" if not vol else "VUURSTORM KLAAR! (omlaag)", x - 15, y - 17,
                         (255, 140, 40), 10, bold=vol)
        if not vol:
            arcade.draw_lrbt_rectangle_filled(x + 60, x + 60 + 90 * sp._dt_super / 100, y - 16, y - 6, (255, 120, 30))
            arcade.draw_lrbt_rectangle_outline(x + 60, x + 150, y - 16, y - 6, (255, 170, 90), 1)
    elif sp._dt_fase == 2:
        arcade.draw_text("pijltje omlaag = vuurbal", x - 15, y - 17, (255, 170, 90), 10)
    else:
        arcade.draw_text("kom verder om te groeien!", x - 15, y - 17, (220, 220, 220), 10)

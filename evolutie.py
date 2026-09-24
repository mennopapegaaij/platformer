# evolutie.py
# EVOLUTIE: je begint als een klein blobje en bouwt zelf je eigen wezen!
#
#  - Verzamel DNA: door verder te komen en door op monsters te stampen.
#  - DNA-balk vol? Dan stopt het spel even en kies JIJ 1 van 3 mutaties (toets 1, 2 of 3).
#  - Elke mutatie geeft een kracht en verandert hoe je wezen eruitziet.
# Welke 3 mutaties je krijgt, hangt af van je level en wat je al hebt: geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT, SCHERM_BREEDTE, SCHERM_HOOGTE

# Alle mutaties: sleutel -> (naam, icoon-tekst, uitleg, hoe vaak je hem mag kiezen)
MUTATIES = {
    "vleugels": ("Vleugels", "V", "een extra sprong in de lucht", 3),
    "sterk":    ("Sterke poten", "S", "hoger springen", 3),
    "snel":     ("Snelle poten", ">>", "sneller rennen", 3),
    "stekels":  ("Stekels", "^", "monsters die je raken gaan dood", 1),
    "pantser":  ("Pantser", "#", "houdt 1 klap tegen", 3),
    "zweefvel": ("Zweefvel", "~", "glijden: springknop vasthouden", 1),
    "stamp":    ("Stamppoten", "!", "omlaag in de lucht = stamp + schokgolf", 1),
    "klein":    ("Klein", "o", "kleiner: past door smalle gaatjes", 1),
}
VOLGORDE = list(MUTATIES)

DNA_PER_AFSTAND = 10      # elke 10 pixels verder = 1 DNA
DNA_PER_MONSTER = 15      # op een monster stampen of het met stekels raken = zoveel DNA
DNA_STAP = 30             # level 1 kost 30 DNA, level 2 60, level 3 90, ...
MAX_LEVEL = 14            # daarna kun je niks meer kiezen (alles is dan wel op)
SNEL_PER = 0.15           # zoveel sneller per 'snelle poten'
STERK_PER = 0.15          # zoveel hoger per 'sterke poten'
GLIJ_SNELHEID = -1.5
STAMP_SNELHEID = 20
KLEIN = 0.7
SCHOK_BEREIK = 170


def reset(sp):
    sp._evo_dna = 0
    sp._evo_level = 0
    sp._evo_muts = {k: 0 for k in MUTATIES}
    sp._evo_kiezen = False      # staat het keuze-scherm open?
    sp._evo_start_x = None
    sp._evo_verste = 0
    sp._evo_extra = 0           # extra luchtsprongen die je nog over hebt
    sp._evo_pantser = 0         # pantser-ladingen die je nog hebt
    sp._evo_stamp = False
    sp._evo_t = 0
    sp._evo_deeltjes = []
    sp._evo_flits = 0
    sp._schokgolf = None


def heeft(sp, sleutel):
    return sp._evo_muts[sleutel]


def nodig(sp):
    """Hoeveel DNA je nodig hebt voor het volgende level."""
    return DNA_STAP * (sp._evo_level + 1)


def dna_erbij(sp, aantal):
    sp._evo_dna += aantal
    if (not sp._evo_kiezen and sp._evo_level < MAX_LEVEL and sp._evo_dna >= nodig(sp)
            and keuzes(sp)):
        sp._evo_kiezen = True       # het spel stopt even: kies een mutatie


def keuzes(sp):
    """De 3 mutaties die je nu mag kiezen (vaste volgorde, draait mee met je level)."""
    open_ = [k for k in VOLGORDE if sp._evo_muts[k] < MUTATIES[k][3]]
    if not open_:
        return []
    start = (sp._evo_level * 3) % len(open_)
    uit = []
    for i in range(min(3, len(open_))):
        uit.append(open_[(start + i) % len(open_)])
    return uit


def kies(sp, nummer):
    """Kies mutatie 1, 2 of 3 uit het keuze-scherm."""
    opties = keuzes(sp)
    if not sp._evo_kiezen or not (1 <= nummer <= len(opties)):
        return False
    k = opties[nummer - 1]
    sp._evo_muts[k] += 1
    sp._evo_dna -= nodig(sp)
    sp._evo_level += 1
    sp._evo_kiezen = False
    if k == "pantser":
        sp._evo_pantser += 1
    if k == "vleugels":
        sp._evo_extra = heeft(sp, "vleugels")
    sp._evo_flits = 30
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    for i in range(18):
        h = math.radians(i * 20)
        _deeltje(sp, cx, cy, math.cos(h) * 3.5, math.sin(h) * 3.5, 28, (120, 255, 160), 3)
    dna_erbij(sp, 0)                # genoeg DNA over? Dan meteen de volgende keuze
    return True


def _deeltje(sp, x, y, vx, vy, leven, kleur, grootte):
    sp._evo_deeltjes.append([x, y, vx, vy, leven, leven, kleur, grootte])


def stap(sp, platforms):
    sp._evo_t += 1
    doel = KLEIN if heeft(sp, "klein") else 1.0
    if abs(sp.grootte_factor - doel) > 0.001:
        sp.zet_grootte(doel, 0)
    if sp._evo_start_x is None:
        sp._evo_start_x = sp.x
    verder = sp.x - sp._evo_start_x
    if verder > sp._evo_verste + DNA_PER_AFSTAND:
        erbij = int((verder - sp._evo_verste) // DNA_PER_AFSTAND)
        sp._evo_verste += erbij * DNA_PER_AFSTAND
        dna_erbij(sp, erbij)
    if sp.staat_op_grond:
        sp._evo_extra = heeft(sp, "vleugels")
    if sp._evo_flits > 0:
        sp._evo_flits -= 1
    if sp._schokgolf is not None:
        sp._schokgolf["t"] += 1
        if sp._schokgolf["t"] > 25:
            sp._schokgolf = None
    for d in sp._evo_deeltjes:
        d[0] += d[2]
        d[1] += d[3]
        d[4] -= 1
    sp._evo_deeltjes = [d for d in sp._evo_deeltjes if d[4] > 0]


def loop_snelheid(sp, snelheid):
    return snelheid * (1 + SNEL_PER * heeft(sp, "snel"))


def zwaartekracht(sp, richting):
    if sp._evo_stamp:
        sp.snelheid_y = -STAMP_SNELHEID * richting
        return
    sp.snelheid_y -= ZWAARTEKRACHT * richting
    if heeft(sp, "zweefvel") and sp.vlieg_omhoog and sp.snelheid_y * richting < GLIJ_SNELHEID:
        sp.snelheid_y = GLIJ_SNELHEID * richting


def spring(sp):
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * (1 + STERK_PER * heeft(sp, "sterk")) * sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp.snelheid_y = kracht
    elif sp._evo_extra > 0:
        sp._evo_extra -= 1
        sp.snelheid_y = kracht * 0.9
        for i in range(6):
            _deeltje(sp, sp.x + sp.breedte / 2 + (i - 2.5) * 4, sp.y + sp.hoogte / 2,
                     (i - 2.5) * 0.5, -1.5, 16, (230, 240, 255), 2.5)


def omlaag(sp):
    """Pijltje omlaag: stampen (als je stamppoten hebt en in de lucht bent)."""
    if heeft(sp, "stamp") and not sp.staat_op_grond and not sp._evo_stamp:
        sp._evo_stamp = True
        return True
    return False


def geland(sp):
    """Net geland: na een stamp komt er een schokgolf."""
    if sp._evo_stamp:
        sp._evo_stamp = False
        cx = sp.x + sp.breedte / 2
        sp._schokgolf = {"x": cx, "y": sp.y, "t": 0, "klaar": False}
        for i in range(12):
            h = math.radians(i * 180 / 11)
            _deeltje(sp, cx, sp.y + 2, math.cos(h) * 4, math.sin(h) * 3, 20, (170, 130, 80), 4)


def bescherm(sp):
    """Word je geraakt en heb je pantser? Dan houdt het pantser de klap tegen."""
    if sp._evo_pantser > 0:
        sp._evo_pantser -= 1
        sp.onkwetsbaar_timer = 45
        cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
        for i in range(10):
            h = math.radians(i * 36)
            _deeltje(sp, cx, cy, math.cos(h) * 3, math.sin(h) * 3, 18, (150, 150, 170), 3)
        return True
    return False


# ===========================================================================
# Tekenen: het wezen verandert met elke mutatie
# ===========================================================================
def _kleur(sp):
    """De kleur van je wezen verschuift met elk level (van groen naar paars)."""
    lv = min(sp._evo_level, 10) / 10
    return (int(90 + 120 * lv), int(200 - 90 * lv), int(120 + 100 * lv))


def teken(sp):
    t = sp._evo_t
    for x, y, vx, vy, leven, max_leven, kleur, grootte in sp._evo_deeltjes:
        deel = leven / max_leven
        arcade.draw_circle_filled(x, y, max(1, grootte * deel),
                                  (kleur[0], kleur[1], kleur[2], int(60 + 195 * deel)))
    if sp._schokgolf is not None:
        sg = sp._schokgolf
        r = 10 + sg["t"] * (SCHOK_BEREIK / 25)
        arcade.draw_ellipse_outline(sg["x"], sg["y"] + 4, r * 2, r * 0.7,
                                    (190, 140, 80, max(0, 255 - sg["t"] * 10)), 4)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx, cy = x + w / 2, y + h / 2
    k = 1 if sp.kijkt_rechts else -1
    lijf = _kleur(sp)
    donker = (lijf[0] // 2, lijf[1] // 2, lijf[2] // 2)
    loopt = abs(sp.snelheid_x) > 0.5
    # Vleugels (groter met elke keer vleugels)
    nv = heeft(sp, "vleugels")
    if nv:
        klap = math.sin(t * (0.6 if not sp.staat_op_grond else 0.15)) * 5
        g = w * (0.35 + 0.18 * nv)
        arcade.draw_triangle_filled(cx - k * w * 0.1, cy + h * 0.2, cx - k * (w * 0.1 + g), cy + h * 0.2 + g * 0.8 + klap,
                                    cx - k * (w * 0.1 + g * 0.8), cy + h * 0.1, (235, 240, 255))
    # Zweefvel: een vliesje tussen voor- en achterkant
    if heeft(sp, "zweefvel") and not sp.staat_op_grond:
        arcade.draw_polygon_filled([(x - 6, cy), (cx, cy + h * 0.35), (x + w + 6, cy)], (lijf[0], lijf[1], lijf[2], 140))
    # Pootjes (dik als sterk, groot als stamppoten)
    dik = 2 + heeft(sp, "sterk")
    voet = 4 if heeft(sp, "stamp") else 2
    for i, dx in enumerate((-0.25, 0.25)):
        stapje = math.sin(t * 0.4 + i * 3) * 4 if loopt else 0
        px = cx + dx * w
        arcade.draw_line(px, y + h * 0.3, px + stapje, y + 2, donker, dik)
        arcade.draw_ellipse_filled(px + stapje + k * 2, y + 2, voet * 3, voet * 1.5, donker)
    # Lijf: een blob
    arcade.draw_ellipse_filled(cx, cy + h * 0.1, w, h * 0.75, lijf)
    # Pantser: platen op de rug
    for i in range(heeft(sp, "pantser")):
        px = cx - k * w * (0.25 - i * 0.18)
        kleur = (170, 170, 190) if i < sp._evo_pantser else (100, 100, 110)
        arcade.draw_ellipse_filled(px, cy + h * 0.32, w * 0.3, h * 0.2, kleur)
    # Stekels op de rug
    if heeft(sp, "stekels"):
        for i in range(4):
            sx = cx - w * 0.3 + i * w * 0.2
            arcade.draw_triangle_filled(sx - 4, cy + h * 0.38, sx + 4, cy + h * 0.38, sx, cy + h * 0.62, (240, 240, 220))
    # Snelheidsstreepjes
    if heeft(sp, "snel") and loopt:
        for i in range(heeft(sp, "snel")):
            yy = cy + h * (0.2 - i * 0.12)
            arcade.draw_line(cx - k * w * 0.6, yy, cx - k * (w * 0.6 + 10 + 4 * i), yy, (255, 255, 255, 180), 2)
    # Ogen (groter als je klein bent, dat is schattig)
    oog = w * (0.14 if heeft(sp, "klein") else 0.11)
    for dx in (0.05, 0.28):
        ox = cx + k * w * dx
        arcade.draw_circle_filled(ox, cy + h * 0.2, oog, (255, 255, 255))
        arcade.draw_circle_filled(ox + k * oog * 0.3, cy + h * 0.2, oog * 0.55, (20, 20, 30))
    # Stamp-pijl
    if sp._evo_stamp:
        arcade.draw_triangle_filled(cx - 8, y - 2, cx + 8, y - 2, cx, y - 14, (255, 230, 120))
    # Flits na een mutatie
    if sp._evo_flits > 0:
        deel = sp._evo_flits / 30
        arcade.draw_circle_outline(cx, cy, w * 0.7 + (1 - deel) * 40, (120, 255, 160, int(255 * deel)), 3)


def teken_hud(sp, x, y):
    """Balkje bovenin: level, DNA-balk en je mutaties."""
    arcade.draw_lrbt_rectangle_filled(x - 240, x + 240, y - 10, y + 22, (0, 0, 0, 150))
    arcade.draw_text("Level %d" % sp._evo_level, x - 232, y, (120, 255, 160), 12, bold=True)
    if sp._evo_level < MAX_LEVEL and keuzes(sp):
        deel = min(1, sp._evo_dna / nodig(sp))
        arcade.draw_lrbt_rectangle_filled(x - 160, x - 160 + 110 * deel, y + 1, y + 13, (90, 220, 130))
        arcade.draw_lrbt_rectangle_outline(x - 160, x - 50, y + 1, y + 13, (170, 255, 200), 1)
        arcade.draw_text("DNA", x - 45, y, (170, 255, 200), 10)
    else:
        arcade.draw_text("helemaal geëvolueerd!", x - 160, y, (170, 255, 200), 10)
    tekst = "  ".join("%s%s" % (MUTATIES[k][1], ("x%d" % n) if n > 1 else "")
                      for k, n in sp._evo_muts.items() if n)
    arcade.draw_text(tekst or "(nog geen mutaties)", x - 10, y, (230, 230, 230), 10)


def teken_keuze(sp):
    """Het keuze-scherm: 3 kaarten met mutaties. Kies met 1, 2 of 3."""
    opties = keuzes(sp)
    arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, 0, SCHERM_HOOGTE, (0, 0, 0, 150))
    onder, boven = 140, 310            # waar de kaarten staan
    arcade.draw_text("Je wezen evolueert! Kies een mutatie (toets 1, 2 of 3)",
                     SCHERM_BREEDTE // 2, boven + 25, (120, 255, 160), 18,
                     bold=True, anchor_x="center")
    kaart_b = 220
    start = SCHERM_BREEDTE // 2 - (len(opties) * (kaart_b + 20) - 20) // 2
    for i, k in enumerate(opties):
        naam, icoon, uitleg, maxi = MUTATIES[k]
        l = start + i * (kaart_b + 20)
        arcade.draw_lrbt_rectangle_filled(l, l + kaart_b, onder, boven, (30, 60, 45))
        arcade.draw_lrbt_rectangle_outline(l, l + kaart_b, onder, boven, (120, 255, 160), 3)
        arcade.draw_text(str(i + 1), l + 16, boven - 35, (255, 230, 90), 24, bold=True)
        arcade.draw_text(icoon, l + kaart_b // 2, boven - 75, (255, 255, 255), 28, bold=True, anchor_x="center")
        arcade.draw_text(naam, l + kaart_b // 2, boven - 112, (170, 255, 200), 16, bold=True, anchor_x="center")
        arcade.draw_text(uitleg, l + 10, onder + 42, (230, 230, 230), 11, width=kaart_b - 20,
                         multiline=True, align="center")
        al = sp._evo_muts[k]
        if maxi > 1:
            arcade.draw_text("(heb je %d van %d)" % (al, maxi), l + kaart_b // 2, onder + 8, (180, 180, 180), 9,
                             anchor_x="center")

# chemicus.py
# De CHEMICUS: meng drankjes in je ketel en ontdek recepten!
#
#  Toets 1 t/m 6  : doe een drankje in je ketel (er passen er 4 in)
#  Pijltje omlaag : drink je brouwsel op (het werkt 10 seconden)
#  Backspace      : ketel leeggooien
#
# De 6 drankjes (elk drankje in de mix telt mee, dus 2 rode = dubbel zo sterk):
#  1 rood  = Springdrank : hoger springen
#  2 groen = Rendrank    : sneller rennen
#  3 blauw = Veerdrank   : lichter (je zweeft meer)
#  4 geel  = Reuzendrank : groter worden
#  5 paars = Schilddrank : een schild tegen een klap (per drankje 1)
#  6 wit   = Wolkdrank   : een extra sprong in de lucht (per drankje 1)
#
# Met 6 drankjes en 1 tot 4 in de ketel zijn er 209 verschillende recepten!
# (De volgorde maakt niet uit: rood+blauw is hetzelfde recept als blauw+rood.)

import math
from itertools import combinations_with_replacement
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

DRANKEN = ["rood", "groen", "blauw", "geel", "paars", "wit"]
RGB = {"rood": (230, 60, 60), "groen": (70, 200, 90), "blauw": (70, 140, 255),
       "geel": (250, 210, 40), "paars": (170, 80, 220), "wit": (240, 240, 250)}
WOORD = {"rood": "Spring", "groen": "Ren", "blauw": "Veer", "geel": "Reuzen", "paars": "Schild", "wit": "Wolk"}
UITLEG = {"rood": "hoger", "groen": "sneller", "blauw": "lichter", "geel": "groter",
          "paars": "schild", "wit": "luchtsprong"}
KETEL_MAX = 4             # zoveel drankjes passen er in je ketel
DUUR = 600                # zo lang werkt een brouwsel (600 stapjes = 10 seconden)
SPRONG_PER = 0.2          # per rood drankje: zoveel hoger springen
SNEL_PER = 0.2            # per groen drankje: zoveel sneller
LICHT_PER = 0.18          # per blauw drankje: zoveel minder zwaartekracht
GROOT_PER = 0.2           # per geel drankje: zoveel groter

# Alle mogelijke recepten: 1 tot 4 drankjes, volgorde maakt niet uit
ALLE_RECEPTEN = set()
for _n in range(1, KETEL_MAX + 1):
    for _combi in combinations_with_replacement(range(len(DRANKEN)), _n):
        ALLE_RECEPTEN.add(tuple(_combi.count(i) for i in range(len(DRANKEN))))
AANTAL_RECEPTEN = len(ALLE_RECEPTEN)          # = 209

VOORVOEGSEL = {1: "", 2: "Dubbel-", 3: "Driedubbel-", 4: "Viervoudig-"}


def recept(ketel):
    """Het recept van een ketel: hoeveel van elk drankje (volgorde maakt niet uit)."""
    return tuple(ketel.count(d) for d in DRANKEN)


def naam(rec):
    """Een naam voor een recept, bv. (2,0,1,0,0,0) -> 'Dubbel-Spring-Veer-drank'."""
    delen = [VOORVOEGSEL[n] + WOORD[d] for d, n in zip(DRANKEN, rec) if n]
    return "-".join(delen) + "-drank" if delen else "leeg"


def reset(sp):
    sp._ch_ketel = []          # de drankjes in je ketel
    sp._ch_actief = None       # het recept dat nu werkt (of None)
    sp._ch_tijd = 0            # hoe lang het nog werkt
    sp._ch_schild = 0          # schild-ladingen van paarse drank
    sp._ch_extra = 0           # extra luchtsprongen die je nog over hebt
    sp._ch_ontdekt = []        # recepten die je al hebt ontdekt (op volgorde)
    sp._ch_melding = ""        # tekstje bovenin ("Nieuw recept!")
    sp._ch_melding_tijd = 0
    sp._ch_t = 0
    sp._ch_bubbels = []


def _telling(sp, drank):
    """Hoeveel van dit drankje zit er in het recept dat nu werkt?"""
    if sp._ch_actief is None:
        return 0
    return sp._ch_actief[DRANKEN.index(drank)]


def voeg_toe(sp, nummer):
    """Toets 1-6: doe een drankje in de ketel."""
    if not (1 <= nummer <= len(DRANKEN)) or len(sp._ch_ketel) >= KETEL_MAX:
        return False
    sp._ch_ketel.append(DRANKEN[nummer - 1])
    return True


def leeg(sp):
    sp._ch_ketel = []


def drink(sp):
    """Pijltje omlaag: drink je brouwsel op. Geeft True als er iets in de ketel zat."""
    if not sp._ch_ketel:
        return False
    rec = recept(sp._ch_ketel)
    sp._ch_actief = rec
    sp._ch_tijd = DUUR
    sp._ch_schild = _telling(sp, "paars")
    sp._ch_extra = _telling(sp, "wit")
    sp._ch_ketel = []
    if rec not in sp._ch_ontdekt:
        sp._ch_ontdekt.append(rec)
        sp._ch_melding = "Nieuw recept: " + naam(rec) + "!"
    else:
        sp._ch_melding = naam(rec)
    sp._ch_melding_tijd = 150
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    for i, d in enumerate(DRANKEN):
        for j in range(rec[i] * 4):
            h = math.radians(i * 60 + j * 22)
            sp._ch_bubbels.append([cx, cy, math.cos(h) * 3, math.sin(h) * 3, 26, RGB[d]])
    return True


def stap(sp):
    """Elke stap: brouwsel uitwerken, grootte bijhouden, bubbels."""
    sp._ch_t += 1
    if sp._ch_tijd > 0:
        sp._ch_tijd -= 1
        if sp._ch_tijd == 0:
            sp._ch_actief = None             # het brouwsel is uitgewerkt
            sp._ch_schild = 0
            sp._ch_extra = 0
    doel = 1 + GROOT_PER * _telling(sp, "geel")
    if abs(sp.grootte_factor - doel) > 0.001:
        sp.zet_grootte(doel, 0)
    if sp.staat_op_grond:
        sp._ch_extra = _telling(sp, "wit")
    if sp._ch_melding_tijd > 0:
        sp._ch_melding_tijd -= 1
    # Bubbeltjes boven je hoofd zolang een brouwsel werkt
    if sp._ch_actief is not None and sp._ch_t % 6 == 0:
        kleuren = [d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]
        kl = RGB[kleuren[(sp._ch_t // 6) % len(kleuren)]]
        sp._ch_bubbels.append([sp.x + sp.breedte / 2 + ((sp._ch_t * 7) % 20) - 10,
                               sp.y + sp.hoogte, 0, 1.0, 30, kl])
    for b in sp._ch_bubbels:
        b[0] += b[2]
        b[1] += b[3]
        b[4] -= 1
    sp._ch_bubbels = [b for b in sp._ch_bubbels if b[4] > 0]


def loop_snelheid(sp, snelheid):
    return snelheid * (1 + SNEL_PER * _telling(sp, "groen"))


def zwaartekracht(sp, richting):
    licht = max(0.28, 1 - LICHT_PER * _telling(sp, "blauw"))
    sp.snelheid_y -= ZWAARTEKRACHT * licht * richting


def spring(sp):
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * (1 + SPRONG_PER * _telling(sp, "rood")) * sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp.snelheid_y = kracht
    elif sp._ch_extra > 0:
        sp._ch_extra -= 1
        sp.snelheid_y = kracht * 0.9
        for i in range(6):
            sp._ch_bubbels.append([sp.x + sp.breedte / 2 + (i - 2.5) * 4, sp.y, (i - 2.5) * 0.5, -1.5, 16,
                                   RGB["wit"]])


def bescherm(sp):
    """Word je geraakt en heb je een schild van paarse drank? Dan houdt het de klap tegen."""
    if sp._ch_schild > 0:
        sp._ch_schild -= 1
        sp.onkwetsbaar_timer = 45
        return True
    return False


# ===========================================================================
# Tekenen
# ===========================================================================
def _mengkleur(dranken):
    if not dranken:
        return (120, 120, 130)
    r = sum(RGB[d][0] for d in dranken) // len(dranken)
    g = sum(RGB[d][1] for d in dranken) // len(dranken)
    b = sum(RGB[d][2] for d in dranken) // len(dranken)
    return (r, g, b)


def teken(sp):
    t = sp._ch_t
    for x, y, vx, vy, leven, kleur in sp._ch_bubbels:
        arcade.draw_circle_outline(x, y, 2 + (30 - leven) / 8, (kleur[0], kleur[1], kleur[2], min(255, leven * 9)), 2)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    # Gloed zolang een brouwsel werkt (in de mengkleur van het recept)
    if sp._ch_actief is not None:
        dranken = [d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]
        mk = _mengkleur(dranken)
        puls = 3 * math.sin(t * 0.2)
        arcade.draw_ellipse_filled(cx, y + h / 2, w + 16 + puls, h + 16 + puls, (mk[0], mk[1], mk[2], 70))
    # Witte labjas
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.65, (245, 245, 250))
    arcade.draw_line(cx, y + 2, cx, y + h * 0.6, (200, 200, 210), 1)
    # Hoofd met een wilde haardos en een veiligheidsbril
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h * 0.6, y + h - 4, (240, 205, 170))
    for i in range(5):
        hx = x + 3 + i * (w - 6) / 4
        arcade.draw_triangle_filled(hx - 4, y + h - 5, hx + 4, y + h - 5, hx, y + h + 3, (230, 230, 235))
    for dx in (-5, 5):
        arcade.draw_circle_filled(cx + dx + k, y + h * 0.78, 4, (160, 220, 255))
        arcade.draw_circle_outline(cx + dx + k, y + h * 0.78, 4, (60, 60, 70), 1)
        arcade.draw_circle_filled(cx + dx + k * 2, y + h * 0.78, 1.5, (20, 20, 30))
    # Een kolf in de hand, gevuld met wat er in de ketel zit
    fx = x + w + 4 if k > 0 else x - 4
    arcade.draw_circle_filled(fx, y + h * 0.3, 6, (220, 230, 240))
    vul = _mengkleur(sp._ch_ketel)
    if sp._ch_ketel:
        arcade.draw_circle_filled(fx, y + h * 0.28, 4.5, vul)
    arcade.draw_lrbt_rectangle_filled(fx - 2, fx + 2, y + h * 0.3 + 4, y + h * 0.3 + 10, (220, 230, 240))


def teken_hud(sp, x, y):
    """Balkje bovenin: de ketel, het brouwsel dat werkt en je receptenboekje."""
    arcade.draw_lrbt_rectangle_filled(x - 260, x + 260, y - 30, y + 28, (0, 0, 0, 155))
    # Drankjes 1-6
    for i, d in enumerate(DRANKEN):
        l = x - 252 + i * 42
        arcade.draw_circle_filled(l + 10, y + 12, 8, RGB[d])
        arcade.draw_text(str(i + 1), l + 10, y + 7, (0, 0, 0) if d in ("wit", "geel") else (255, 255, 255), 9,
                         bold=True, anchor_x="center")
        arcade.draw_text(UITLEG[d], l + 10, y - 7, (200, 200, 200), 7, anchor_x="center")
    # De ketel: 4 plekjes
    kx = x + 20
    arcade.draw_text("ketel:", kx - 2, y + 7, (230, 230, 230), 10)
    for i in range(KETEL_MAX):
        vx = kx + 45 + i * 20
        if i < len(sp._ch_ketel):
            arcade.draw_circle_filled(vx, y + 12, 7, RGB[sp._ch_ketel[i]])
        arcade.draw_circle_outline(vx, y + 12, 7, (180, 180, 190), 1)
    arcade.draw_text("omlaag = drinken", kx + 125, y + 7, (200, 200, 200), 9)
    # Brouwsel dat werkt (met tijdbalk) + receptenboekje
    if sp._ch_actief is not None:
        arcade.draw_lrbt_rectangle_filled(x - 252, x - 252 + 250 * sp._ch_tijd / DUUR, y - 26, y - 20,
                                          _mengkleur([d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]))
    arcade.draw_text("Receptenboek: %d / %d ontdekt" % (len(sp._ch_ontdekt), AANTAL_RECEPTEN),
                     x + 20, y - 24, (255, 230, 120), 10, bold=True)
    if sp._ch_melding_tijd > 0:
        arcade.draw_text(sp._ch_melding, x, y - 50, (255, 240, 150), 13, bold=True, anchor_x="center")

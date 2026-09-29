# ruimte.py
# Het RUIMTESTATION: bouw modules, pas op je zuurstof en vlieg naar andere planeten!
#
#  Toets 1 : ZONNEPANEEL     (3 metaal) - maakt 2 stroom
#  Toets 2 : ZUURSTOFMAKER   (5 metaal) - gebruikt 2 stroom; vult je zuurstof bij als je dichtbij bent
#  Toets 3 : KAS             (5 metaal) - gebruikt 1 stroom; laat ruimtefruit groeien (+1 leven)
#  Toets 4 : ASTEROIDEMIJN   (6 metaal) - gebruikt 1 stroom; maakt elke 4 seconden 1 metaal
#  Toets 5 : LANCEERPLATFORM (8 metaal) - gebruikt 3 stroom; sta erop en druk omlaag: naar een andere planeet!
#  Omlaag  : op het lanceerplatform = lanceren; anders = de module voor je slopen (metaal terug)
#  Springen vasthouden in de lucht = JETPACK (kost zuurstof!)
#
# ZUURSTOF: je zuurstof loopt langzaam leeg. Op = een leven kwijt! Blijf in de buurt van een zuurstofmaker.
# STROOM: alle modules zitten aan hetzelfde stroomnet. Te weinig stroom? Dan werkt alles langzamer.
# PLANETEN (steeds in deze volgorde): Aarde -> Maan -> Mars -> Jupiter -> Aarde ...
#   Elke planeet heeft een andere zwaartekracht. Alles is vast: geen toeval.

import math
import arcade
from instellingen import ZWAARTEKRACHT
from platforms import Platform

METAAL = 20               # zoveel metaal heb je aan het begin
MODULES = ["paneel", "zuurstof", "kas", "mijn", "lanceer"]
KOST = {"paneel": 3, "zuurstof": 5, "kas": 5, "mijn": 6, "lanceer": 8}
NAAM = {"paneel": "zonnepaneel", "zuurstof": "zuurstof", "kas": "kas", "mijn": "mijn", "lanceer": "lanceer"}
STROOM = {"paneel": 2, "zuurstof": -2, "kas": -1, "mijn": -1, "lanceer": -3}   # + maakt, - gebruikt
MAAT = {"paneel": (40, 44), "zuurstof": (40, 44), "kas": (52, 36), "mijn": (44, 40), "lanceer": (56, 12)}
PLANETEN = [("Aarde", 1.0, (120, 180, 255)), ("Maan", 0.4, (200, 200, 210)),
            ("Mars", 0.7, (220, 110, 70)), ("Jupiter", 1.6, (230, 180, 120))]
ZUURSTOF_MAX = 100
ZUURSTOF_TIJD = 18        # elke 18 stapjes 1 zuurstof minder (100 zuurstof = 30 seconden)
JETPACK_KOST = 4          # jetpack: elke 4 stapjes 1 zuurstof extra
JETPACK_DUW = 0.9
JETPACK_MAX = 5
BIJVUL_BEREIK = 150       # zo dichtbij moet je bij een zuurstofmaker zijn
BIJVUL_SNEL = 1.0         # zoveel zuurstof per stapje (met volle stroom)
FRUIT_TIJD = 600          # kas: elke 10 seconden een ruimtefruit
MAX_LEVENS = 5
MIJN_TIJD = 240           # mijn: elke 4 seconden 1 metaal
LANCEER_TIJD = 90         # zo lang duurt een lancering


class Module(Platform):
    """Een module van je ruimtestation: je kunt erop staan."""

    is_ruimte = True

    def __init__(self, soort, x, y):
        w, h = MAAT[soort]
        super().__init__(x, y, w, h)
        self.soort = soort
        self.werk = 0                 # hoe ver het volgende fruit / metaal is
        self.fruit = False            # kas: hangt er een ruimtefruit?
        self.t = 0

    def teken(self):
        pass                          # (het ruimtestation tekent alles zelf)


def reset(sp):
    sp._rs_metaal = METAAL
    sp._rs_modules = []
    sp._rs_zuurstof = ZUURSTOF_MAX
    sp._rs_klok = 0
    sp._rs_planeet = 0
    sp._rs_lancering = 0      # >0: de raket vliegt (aftellen)
    sp._rs_jetpack = False
    sp._rs_t = 0
    sp._rs_melding = ""
    sp._rs_melding_tijd = 0


def _meld(sp, tekst):
    sp._rs_melding = tekst
    sp._rs_melding_tijd = 150


def planeet(sp):
    return PLANETEN[sp._rs_planeet]


def stroom(sp):
    """(gemaakt, gebruikt) van het hele station."""
    gemaakt = sum(STROOM[m.soort] for m in sp._rs_modules if STROOM[m.soort] > 0)
    gebruikt = -sum(STROOM[m.soort] for m in sp._rs_modules if STROOM[m.soort] < 0)
    return gemaakt, gebruikt


def kracht(sp):
    """Hoeveel stroom krijgt elke module? 1 = genoeg, minder = alles werkt langzamer."""
    gemaakt, gebruikt = stroom(sp)
    if gebruikt == 0:
        return 1.0
    return min(1.0, gemaakt / gebruikt)


def _vrij(x, y, w, h, platforms):
    return not any(getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                   and x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y
                   for p in platforms)


def plaats(sp, soort, platforms):
    """Toets 1-5: zet een module vlak voor je neer."""
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    if sp._rs_metaal < KOST[soort]:
        _meld(sp, "Te weinig metaal! (bouw een asteroidemijn)")
        return False
    w, h = MAAT[soort]
    x = sp.x + sp.breedte + 2 if sp.kijkt_rechts else sp.x - 2 - w
    if not _vrij(x, sp.y, w, h, platforms):
        _meld(sp, "Daar is geen plek")
        return False
    sp._rs_metaal -= KOST[soort]
    sp._rs_modules.append(Module(soort, x, sp.y))
    return True


def omlaag(sp):
    """Omlaag: lanceren (op het lanceerplatform) of de module voor je slopen."""
    g = sp._gelande_platform
    if sp.staat_op_grond and g in sp._rs_modules and g.soort == "lanceer":
        return _lanceer(sp)
    kijk_x = sp.x + sp.breedte + 10 if sp.kijkt_rechts else sp.x - 10
    kandidaten = [m for m in sp._rs_modules
                  if (m.x <= kijk_x <= m.x + m.breedte and m.y <= sp.y + 5 <= m.y + m.hoogte + 5) or m is g]
    if not kandidaten:
        _meld(sp, "Hier staat niks om te slopen")
        return False
    m = kandidaten[0]
    sp._rs_modules.remove(m)
    sp._rs_metaal += KOST[m.soort]
    return True


def _lanceer(sp):
    if sp._rs_lancering > 0:
        return False
    if kracht(sp) < 1:
        _meld(sp, "Te weinig stroom om te lanceren! (bouw zonnepanelen)")
        return False
    sp._rs_lancering = LANCEER_TIJD
    _meld(sp, "3... 2... 1... LANCERING!")
    return True


def zwaartekracht(sp, richting):
    """Zwaartekracht van de planeet, en de jetpack."""
    sp._rs_jetpack = False
    if sp._rs_lancering > 0:
        sp.snelheid_y = 0                            # in de raket
        return
    sp.snelheid_y -= ZWAARTEKRACHT * planeet(sp)[1] * richting
    if (getattr(sp, "vlieg_omhoog", False) and not sp.staat_op_grond and sp._rs_zuurstof > 0
            and sp.snelheid_y * richting < JETPACK_MAX):
        sp.snelheid_y = min(JETPACK_MAX, sp.snelheid_y * richting + JETPACK_DUW) * richting
        sp._rs_jetpack = True


def wereld(sp):
    """Elke stap: zuurstof, stroom, kas, mijn en lancering. Geeft True als je net geen zuurstof meer hebt."""
    sp._rs_t += 1
    if sp._rs_melding_tijd > 0:
        sp._rs_melding_tijd -= 1
    k = kracht(sp)
    for m in sp._rs_modules:
        m.t += 1
    # Zuurstof: langzaam op, sneller met de jetpack
    sp._rs_klok += 1
    if sp._rs_klok % ZUURSTOF_TIJD == 0:
        sp._rs_zuurstof -= 1
    if sp._rs_jetpack and sp._rs_klok % JETPACK_KOST == 0:
        sp._rs_zuurstof -= 1
    cx = sp.x + sp.breedte / 2
    for m in sp._rs_modules:
        if m.soort == "zuurstof" and abs(m.x + m.breedte / 2 - cx) <= BIJVUL_BEREIK and abs(m.y - sp.y) < 120:
            sp._rs_zuurstof = min(ZUURSTOF_MAX, sp._rs_zuurstof + BIJVUL_SNEL * k)
    # Kas: ruimtefruit groeit; loop je langs de kas, dan eet je het op
    for m in sp._rs_modules:
        if m.soort == "kas":
            if not m.fruit:
                m.werk += k
                if m.werk >= FRUIT_TIJD:
                    m.werk, m.fruit = 0, True
            elif (sp.levens < MAX_LEVENS and m.x - 10 <= cx <= m.x + m.breedte + 10
                  and abs(sp.y - m.y) < 60):
                m.fruit = False
                sp.levens += 1
                _meld(sp, "Ruimtefruit! +1 leven")
        elif m.soort == "mijn":
            m.werk += k
            if m.werk >= MIJN_TIJD:
                m.werk = 0
                sp._rs_metaal += 1
    # Lancering: na het aftellen ben je op de volgende planeet
    if sp._rs_lancering > 0:
        sp._rs_lancering -= 1
        if sp._rs_lancering == 0:
            sp._rs_planeet = (sp._rs_planeet + 1) % len(PLANETEN)
            naam, zw, _ = planeet(sp)
            _meld(sp, "Welkom op %s! (zwaartekracht x%s)" % (naam, zw))
    if sp._rs_zuurstof <= 0:
        sp._rs_zuurstof = ZUURSTOF_MAX               # (nieuwe zuurstoffles, maar je bent een leven kwijt)
        return True
    return False


def platforms_van(sp):
    return list(sp._rs_modules)


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_module(sp, m, k):
    x, y, w, h = m.x, m.y, m.breedte, m.hoogte
    s = m.soort
    if s == "paneel":
        arcade.draw_lrbt_rectangle_filled(x + w / 2 - 2, x + w / 2 + 2, y, y + h - 14, (160, 160, 170))
        arcade.draw_lrbt_rectangle_filled(x - 4, x + w + 4, y + h - 16, y + h, (40, 70, 160))
        for i in range(1, 4):
            arcade.draw_line(x - 4 + i * (w + 8) / 4, y + h - 16, x - 4 + i * (w + 8) / 4, y + h, (120, 160, 230), 1)
        arcade.draw_line(x - 4, y + h - 8, x + w + 4, y + h - 8, (120, 160, 230), 1)
    elif s == "zuurstof":
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y, y + h - 8, (235, 240, 245))
        arcade.draw_arc_filled(x + w / 2, y + h - 8, w - 12, 16, (235, 240, 245), 0, 180)
        arcade.draw_text("O2", x + w / 2, y + 12, (60, 120, 220), 11, bold=True, anchor_x="center")
        if k > 0:
            for i in range(3):
                f = (m.t // 4 + i * 7) % 20
                arcade.draw_circle_outline(x + 12 + i * 8, y + h + f * 1.5, 2 + f / 8, (150, 210, 255, 220 - f * 10), 1)
    elif s == "kas":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 8, (150, 150, 160))
        arcade.draw_arc_filled(x + w / 2, y + 8, w, 56, (170, 230, 255, 110), 0, 180)
        arcade.draw_arc_outline(x + w / 2, y + 8, w, 56, (220, 240, 255), 0, 180, 2)
        for i in range(3):
            px = x + 12 + i * 14
            groei = min(1.0, m.werk / FRUIT_TIJD) if not m.fruit else 1.0
            arcade.draw_line(px, y + 8, px, y + 10 + 12 * groei, (60, 170, 70), 3)
        if m.fruit:
            arcade.draw_circle_filled(x + w / 2, y + 26, 6, (250, 120, 200))
            arcade.draw_circle_filled(x + w / 2 + 2, y + 28, 2, (255, 220, 240))
    elif s == "mijn":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 20, (120, 110, 100))
        arcade.draw_polygon_filled([(x + 6, y + 20), (x + 16, y + h), (x + 34, y + h - 4), (x + 40, y + 20)],
                                   (110, 100, 90))
        boor = (m.t // 4) % 3 if k > 0 else 0
        arcade.draw_triangle_filled(x + w - 12, y + 30, x + w - 4, y + 30, x + w - 8, y + 14 - boor, (220, 220, 230))
        arcade.draw_circle_filled(x + 14, y + 10, 3, (200, 200, 90))
    elif s == "lanceer":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 90, 100))
        for i in range(4):
            arcade.draw_lrbt_rectangle_filled(x + 4 + i * 13, x + 10 + i * 13, y + h - 3, y + h,
                                              (250, 210, 60) if i % 2 == 0 else (40, 40, 45))
    if STROOM[s] < 0:
        kleur = (80, 230, 90) if k >= 1 else (250, 170, 40) if k > 0 else (230, 50, 50)
        arcade.draw_circle_filled(x + w - 4, y + 4, 3, kleur)


def teken(sp):
    t = sp._rs_t
    k = kracht(sp)
    for m in sp._rs_modules:
        _teken_module(sp, m, k)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    r = 1 if sp.kijkt_rechts else -1
    if sp._rs_lancering > 0:
        # De raket met jou erin, steeds hoger
        hoogte = (LANCEER_TIJD - sp._rs_lancering) ** 2 / 20
        ry = y + hoogte
        arcade.draw_lrbt_rectangle_filled(cx - 10, cx + 10, ry, ry + 44, (240, 240, 245))
        arcade.draw_triangle_filled(cx - 10, ry + 44, cx + 10, ry + 44, cx, ry + 60, (220, 60, 60))
        arcade.draw_circle_filled(cx, ry + 30, 5, (120, 190, 240))
        arcade.draw_triangle_filled(cx - 8, ry, cx + 8, ry, cx, ry - 14 - (t % 6), (255, 170, 40))
        return
    # Jetpack op de rug
    jx = x - 5 if r > 0 else x + w - 1
    arcade.draw_lrbt_rectangle_filled(jx, jx + 6, y + 6, y + h - 8, (170, 170, 180))
    if sp._rs_jetpack:
        arcade.draw_triangle_filled(jx, y + 6, jx + 6, y + 6, jx + 3, y - 6 - (t % 5), (255, 170, 40))
    # Astronaut: wit pak, helm met blauw vizier
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (240, 240, 245))
    arcade.draw_lrbt_rectangle_filled(x + 10, x + w - 10, y + h * 0.3, y + h * 0.45, (220, 60, 60))
    arcade.draw_circle_filled(cx, y + h * 0.78, w * 0.42, (235, 235, 240))
    arcade.draw_ellipse_filled(cx + r * 3, y + h * 0.78, w * 0.5, h * 0.25, (70, 130, 200))
    arcade.draw_ellipse_filled(cx + r * 6, y + h * 0.82, w * 0.14, h * 0.07, (200, 230, 255))
    # Zuurstof bijna op: rood knipperen
    if sp._rs_zuurstof < 25 and t % 20 < 10:
        arcade.draw_circle_outline(cx, y + h * 0.78, w * 0.46, (240, 50, 50), 2)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Metaal: %d" % sp._rs_metaal, x - 292, y + 1, (200, 200, 210), 11, bold=True)
    # Zuurstofmeter
    z = max(0, sp._rs_zuurstof) / ZUURSTOF_MAX
    kleur = (100, 200, 255) if z > 0.25 else (240, 60, 60)
    arcade.draw_text("O2", x - 292, y - 24, kleur, 11, bold=True)
    arcade.draw_lrbt_rectangle_filled(x - 266, x - 266 + 100 * z, y - 22, y - 12, kleur)
    arcade.draw_lrbt_rectangle_outline(x - 266, x - 166, y - 22, y - 12, (220, 220, 230), 1)
    gemaakt, gebruikt = stroom(sp)
    arcade.draw_text("Stroom: %d / %d" % (gebruikt, gemaakt), x - 150, y - 24,
                     (80, 230, 90) if gebruikt <= gemaakt else (250, 170, 40), 10, bold=True)
    naam, zw, pk = planeet(sp)
    arcade.draw_circle_filled(x + 60, y - 17, 7, pk)
    arcade.draw_text("%s (zwaartekracht x%s)" % (naam, zw), x + 72, y - 24, (230, 230, 240), 10)
    for i, s in enumerate(MODULES):
        l = x - 190 + i * 98
        kan = sp._rs_metaal >= KOST[s]
        arcade.draw_lrbt_rectangle_filled(l, l + 94, y, y + 18, (60, 90, 130) if kan else (60, 60, 60))
        arcade.draw_text("%d %s (%d)" % (i + 1, NAAM[s], KOST[s]), l + 47, y + 4,
                         (255, 255, 255) if kan else (140, 140, 140), 9, anchor_x="center")
    if sp._rs_melding_tijd > 0:
        arcade.draw_text(sp._rs_melding, x, y - 50, (200, 230, 255), 13, bold=True, anchor_x="center")

# kok.py
# De KOK: maak ingredienten, kook gerechten, bedien klanten en krijg krachten van je eten!
#
#  Toets 1 : MOESTUIN    (4 munten) - elke 4 seconden 1 groente
#  Toets 2 : KIPPENHOK   (5 munten) - elke 5 seconden 1 ei
#  Toets 3 : MOLEN       (6 munten) - elke 5 seconden 1 meel
#  Toets 4 : KOEIENWEI   (6 munten) - elke 6 seconden 1 melk
#  Toets 5 : RESTAURANT  (8 munten) - met een fornuis; er komen klanten die iets bestellen
#  Toets 6 : kies een ander gerecht
#  Toets 7 : KOKEN (bij je restaurant) - het gerecht komt op je dienblad (er passen er 3 op)
#  Toets 8 : SLOPEN (het gebouw voor je; munten terug)
#  Omlaag  : een klant wil wat jij draagt? Dan geef je het (en hij betaalt).
#            Anders eet je het eerste gerecht zelf op, en krijg je de kracht ervan.
#
# Gerechten:  salade (2 groente)          klant betaalt 2   kracht: +1 leven
#             omelet (2 ei)               klant betaalt 2   kracht: 10 sec sneller
#             soep (groente + melk)       klant betaalt 3   kracht: schild tegen een klap
#             pizza (meel + groente)      klant betaalt 3   kracht: boer! monsters in de buurt weg
#             pannenkoek (meel+ei+melk)   klant betaalt 4   kracht: 10 sec een extra luchtsprong
#             taart (2 meel + ei)         klant betaalt 5   kracht: 10 sec superhoog springen
# Klanten wachten 30 seconden. Daarna lopen ze boos weg. Alles is vast: geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT
from platforms import Platform

MUNTEN = 20
GEBOUWEN = ["moestuin", "kippenhok", "molen", "koeienwei", "restaurant"]
KOST = {"moestuin": 4, "kippenhok": 5, "molen": 6, "koeienwei": 6, "restaurant": 8}
MAAT = {"moestuin": (48, 16), "kippenhok": (40, 32), "molen": (36, 50), "koeienwei": (56, 20), "restaurant": (64, 50)}
MAAKT = {"moestuin": ("groente", 240), "kippenhok": ("ei", 300), "molen": ("meel", 300), "koeienwei": ("melk", 360)}
INGREDIENTEN = ["groente", "ei", "meel", "melk"]
MAX_VOORRAAD = 9
GERECHTEN = ["salade", "omelet", "soep", "pizza", "pannenkoek", "taart"]
RECEPT = {"salade": {"groente": 2}, "omelet": {"ei": 2}, "soep": {"groente": 1, "melk": 1},
          "pizza": {"meel": 1, "groente": 1}, "pannenkoek": {"meel": 1, "ei": 1, "melk": 1},
          "taart": {"meel": 2, "ei": 1}}
PRIJS = {"salade": 2, "omelet": 2, "soep": 3, "pizza": 3, "pannenkoek": 4, "taart": 5}
KRACHT = {"salade": "+1 leven", "omelet": "sneller", "soep": "schild", "pizza": "boer!",
          "pannenkoek": "extra sprong", "taart": "superhoog"}
KLEUR = {"salade": (90, 190, 80), "omelet": (250, 220, 90), "soep": (220, 120, 60), "pizza": (230, 80, 50),
         "pannenkoek": (220, 170, 90), "taart": (250, 170, 200),
         "groente": (90, 190, 80), "ei": (250, 250, 240), "meel": (240, 230, 200), "melk": (230, 240, 250)}
DIENBLAD = 3
KLANT_TIJD = 360          # elke 6 seconden een nieuwe klant
MAX_KLANTEN = 3
GEDULD = 1800             # klanten wachten 30 seconden
KRACHT_TIJD = 600         # krachten werken 10 seconden
BOER_BEREIK = 150
MAX_LEVENS = 5
KOOK_BEREIK = 60          # zo dicht moet je bij het fornuis staan


class KokGebouw(Platform):
    is_kok = True

    def __init__(self, soort, x, y):
        w, h = MAAT[soort]
        super().__init__(x, y, w, h)
        self.soort = soort
        self.werk = 0
        self.t = 0

    def teken(self):
        pass                          # (de kok tekent alles zelf)


def reset(sp):
    sp._kk_munten = MUNTEN
    sp._kk_gebouwen = []
    sp._kk_voorraad = {i: 0 for i in INGREDIENTEN}
    sp._kk_keuze = 0          # welk gerecht is gekozen
    sp._kk_blad = []          # gerechten op je dienblad
    sp._kk_klanten = []       # {"restaurant", "bestelling", "geduld", "x", "nr"}
    sp._kk_klant_nr = 0
    sp._kk_klok = 0
    sp._kk_kracht = {}        # kracht -> tijd (sneller, extra sprong, superhoog)
    sp._kk_schild = 0
    sp._kk_luchtsprong = 0
    sp._kk_boer = False       # pizza gegeten: het spel haalt monsters in de buurt weg
    sp._kk_bediend = 0
    sp._kk_boos = 0
    sp._kk_t = 0
    sp._kk_melding = ""
    sp._kk_melding_tijd = 0


def _meld(sp, tekst):
    sp._kk_melding = tekst
    sp._kk_melding_tijd = 120


def gekozen(sp):
    return GERECHTEN[sp._kk_keuze]


def _vrij(x, y, w, h, platforms):
    return not any(getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                   and x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y for p in platforms)


def plaats(sp, soort, platforms):
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    if sp._kk_munten < KOST[soort]:
        _meld(sp, "Te weinig munten! (bedien klanten)")
        return False
    w, h = MAAT[soort]
    x = sp.x + sp.breedte + 2 if sp.kijkt_rechts else sp.x - 2 - w
    if not _vrij(x, sp.y, w, h, platforms):
        _meld(sp, "Daar is geen plek")
        return False
    sp._kk_munten -= KOST[soort]
    sp._kk_gebouwen.append(KokGebouw(soort, x, sp.y))
    return True


def volgende_gerecht(sp):
    """Toets 6: kies het volgende gerecht."""
    sp._kk_keuze = (sp._kk_keuze + 1) % len(GERECHTEN)
    g = gekozen(sp)
    _meld(sp, "%s: %s" % (g, " + ".join("%d %s" % (n, i) for i, n in RECEPT[g].items())))
    return True


def _bij_restaurant(sp):
    cx = sp.x + sp.breedte / 2
    for g in sp._kk_gebouwen:
        if g.soort == "restaurant" and g.x - KOOK_BEREIK <= cx <= g.x + g.breedte + KOOK_BEREIK and abs(g.y - sp.y) < 60:
            return g
    return None


def kook(sp):
    """Toets 7: kook het gekozen gerecht (bij je restaurant)."""
    if _bij_restaurant(sp) is None:
        _meld(sp, "Ga naar je restaurant om te koken")
        return False
    if len(sp._kk_blad) >= DIENBLAD:
        _meld(sp, "Je dienblad is vol!")
        return False
    g = gekozen(sp)
    tekort = [i for i, n in RECEPT[g].items() if sp._kk_voorraad[i] < n]
    if tekort:
        _meld(sp, "Te weinig " + " en ".join(tekort) + " voor " + g)
        return False
    for i, n in RECEPT[g].items():
        sp._kk_voorraad[i] -= n
    sp._kk_blad.append(g)
    _meld(sp, "Gekookt: %s!" % g)
    return True


def omlaag(sp):
    """Omlaag: geef een gerecht aan een klant die het wil, of eet zelf."""
    if not sp._kk_blad:
        _meld(sp, "Je dienblad is leeg (kook eerst iets met 7)")
        return False
    r = _bij_restaurant(sp)
    if r is not None:
        for k in [k for k in sp._kk_klanten if k["restaurant"] is r]:
            if k["bestelling"] in sp._kk_blad:
                sp._kk_blad.remove(k["bestelling"])
                sp._kk_klanten.remove(k)
                sp._kk_munten += PRIJS[k["bestelling"]]
                sp._kk_bediend += 1
                _meld(sp, "Lekker! De klant betaalt %d munten" % PRIJS[k["bestelling"]])
                return True
    return _eet(sp, sp._kk_blad.pop(0))


def _eet(sp, g):
    """Zelf opeten: je krijgt de kracht van het gerecht."""
    if g == "salade":
        if sp.levens < MAX_LEVENS:
            sp.levens += 1
    elif g == "omelet":
        sp._kk_kracht["sneller"] = KRACHT_TIJD
    elif g == "soep":
        sp._kk_schild += 1
    elif g == "pizza":
        sp._kk_boer = True
    elif g == "pannenkoek":
        sp._kk_kracht["extra sprong"] = KRACHT_TIJD
        sp._kk_luchtsprong = 1
    elif g == "taart":
        sp._kk_kracht["superhoog"] = KRACHT_TIJD
    _meld(sp, "Mmm, %s! Kracht: %s" % (g, KRACHT[g]))
    return True


def loop_factor(sp):
    return 1.5 if "sneller" in sp._kk_kracht else 1.0


def spring(sp):
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * (1.5 if "superhoog" in sp._kk_kracht else 1) * sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp.snelheid_y = kracht
        if "extra sprong" in sp._kk_kracht:
            sp._kk_luchtsprong = 1
    elif sp._kk_luchtsprong > 0:
        sp._kk_luchtsprong -= 1
        sp.snelheid_y = kracht * 0.9


def bescherm(sp):
    if sp._kk_schild > 0:
        sp._kk_schild -= 1
        sp.onkwetsbaar_timer = 60
        _meld(sp, "De soep beschermde je!")
        return True
    return False


def alle_delen(sp):
    return list(sp._kk_gebouwen)


def wereld(sp, vijanden):
    """Elke stap: ingredienten groeien, klanten komen en gaan, krachten. Geeft monsters die weg moeten."""
    sp._kk_t += 1
    if sp._kk_melding_tijd > 0:
        sp._kk_melding_tijd -= 1
    for k in list(sp._kk_kracht):
        sp._kk_kracht[k] -= 1
        if sp._kk_kracht[k] <= 0:
            del sp._kk_kracht[k]
    if sp.staat_op_grond and "extra sprong" in sp._kk_kracht:
        sp._kk_luchtsprong = 1
    for g in sp._kk_gebouwen:
        g.t += 1
        if g.soort in MAAKT:
            stof, tijd = MAAKT[g.soort]
            if sp._kk_voorraad[stof] < MAX_VOORRAAD:
                g.werk += 1
                if g.werk >= tijd:
                    g.werk = 0
                    sp._kk_voorraad[stof] += 1
    # Klanten komen bij de restaurants
    restaurants = [g for g in sp._kk_gebouwen if g.soort == "restaurant"]
    sp._kk_klok += 1
    if sp._kk_klok >= KLANT_TIJD:
        sp._kk_klok = 0
        for r in restaurants:
            if sum(1 for k in sp._kk_klanten if k["restaurant"] is r) < MAX_KLANTEN:
                n = sp._kk_klant_nr
                sp._kk_klanten.append({"restaurant": r, "bestelling": GERECHTEN[(n * 5) % len(GERECHTEN)],
                                       "geduld": GEDULD, "nr": n})
                sp._kk_klant_nr += 1
                break
    for k in list(sp._kk_klanten):
        k["geduld"] -= 1
        if k["geduld"] <= 0 or k["restaurant"] not in sp._kk_gebouwen:
            sp._kk_klanten.remove(k)
            if k["geduld"] <= 0:
                sp._kk_boos += 1
                _meld(sp, "Een klant liep boos weg (wilde %s)" % k["bestelling"])
    # Pizza: boer! monsters in de buurt weg
    weg = []
    if sp._kk_boer:
        sp._kk_boer = False
        cx = sp.x + sp.breedte / 2
        weg = [v for v in vijanden if not getattr(v, "is_spike", False)
               and abs(v.x + v.breedte / 2 - cx) <= BOER_BEREIK and abs(v.y - sp.y) < 80]
    return weg


def sloop(sp):
    k = 1 if sp.kijkt_rechts else -1
    kijk_x = sp.x + sp.breedte + 10 if k > 0 else sp.x - 10
    for g in sp._kk_gebouwen:
        if (g.x <= kijk_x <= g.x + g.breedte and g.y <= sp.y + 5 <= g.y + g.hoogte + 5) or g is sp._gelande_platform:
            sp._kk_gebouwen.remove(g)
            sp._kk_munten += KOST[g.soort]
            for k in [k for k in sp._kk_klanten if k["restaurant"] is g]:
                sp._kk_klanten.remove(k)
            return True
    _meld(sp, "Hier staat niks om te slopen")
    return False


# ===========================================================================
# Tekenen
# ===========================================================================
def _gerecht(g, x, y):
    k = KLEUR[g]
    arcade.draw_ellipse_filled(x, y, 18, 6, (245, 245, 250))                 # bord
    if g == "salade":
        for i in range(3):
            arcade.draw_circle_filled(x - 4 + i * 4, y + 3, 3, k)
    elif g == "omelet":
        arcade.draw_ellipse_filled(x, y + 2, 12, 6, k)
    elif g == "soep":
        arcade.draw_arc_filled(x, y + 2, 14, 12, (180, 180, 190), 180, 360)
        arcade.draw_ellipse_filled(x, y + 2, 12, 3, k)
    elif g == "pizza":
        arcade.draw_triangle_filled(x - 7, y + 1, x + 7, y + 1, x, y + 9, (240, 200, 110))
        arcade.draw_circle_filled(x, y + 4, 1.5, k)
    elif g == "pannenkoek":
        for i in range(3):
            arcade.draw_ellipse_filled(x, y + 2 + i * 2, 13, 3, k)
    elif g == "taart":
        arcade.draw_lrbt_rectangle_filled(x - 6, x + 6, y + 1, y + 9, k)
        arcade.draw_line(x, y + 9, x, y + 13, (255, 255, 255), 1)
        arcade.draw_circle_filled(x, y + 14, 1.5, (255, 200, 60))


def _teken_gebouw(g, sp):
    x, y, w, h = g.x, g.y, g.breedte, g.hoogte
    s = g.soort
    groei = g.werk / MAAKT[s][1] if s in MAAKT else 0
    if s == "moestuin":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h - 6, (110, 75, 45))
        for i in range(4):
            arcade.draw_circle_filled(x + 7 + i * 11, y + h - 4 + groei * 4, 3 + groei * 3, (90, 190, 80))
    elif s == "kippenhok":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h - 8, (190, 120, 70))
        arcade.draw_triangle_filled(x - 3, y + h - 8, x + w + 3, y + h - 8, x + w / 2, y + h + 4, (150, 60, 50))
        arcade.draw_ellipse_filled(x + w / 2, y + 6, 12, 10, (255, 255, 255))                  # kip
        arcade.draw_circle_filled(x + w / 2 + 6, y + 12, 3, (255, 255, 255))
        arcade.draw_triangle_filled(x + w / 2 + 8, y + 13, x + w / 2 + 12, y + 12, x + w / 2 + 8, y + 11, (250, 180, 40))
    elif s == "molen":
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y, y + h - 10, (220, 210, 190))
        arcade.draw_triangle_filled(x + 2, y + h - 10, x + w - 2, y + h - 10, x + w / 2, y + h, (140, 90, 60))
        for i in range(4):
            a = g.t * 0.05 + i * math.pi / 2
            arcade.draw_line(x + w / 2, y + h - 12, x + w / 2 + math.cos(a) * 20, y + h - 12 + math.sin(a) * 20,
                             (240, 240, 240), 3)
    elif s == "koeienwei":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 3, (80, 160, 70))
        for px in (x + 2, x + w - 2):
            arcade.draw_line(px, y, px, y + h, (150, 110, 70), 2)
        arcade.draw_line(x, y + h - 4, x + w, y + h - 4, (150, 110, 70), 2)
        arcade.draw_ellipse_filled(x + w / 2, y + 10, 24, 12, (255, 255, 255))                 # koe
        arcade.draw_circle_filled(x + w / 2 - 4, y + 10, 3, (40, 40, 40))
        arcade.draw_circle_filled(x + w / 2 + 12, y + 13, 4, (255, 255, 255))
    elif s == "restaurant":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h - 12, (240, 230, 210))
        for i in range(8):
            arcade.draw_lrbt_rectangle_filled(x + i * 8, x + i * 8 + 8, y + h - 12, y + h,
                                              (200, 60, 60) if i % 2 == 0 else (255, 255, 255))
        arcade.draw_lrbt_rectangle_filled(x + 6, x + 26, y, y + 14, (60, 60, 65))              # fornuis
        arcade.draw_circle_filled(x + 12, y + 14, 3, (255, 120, 40) if g.t % 20 < 10 else (255, 180, 60))
        arcade.draw_circle_filled(x + 20, y + 14, 3, (255, 120, 40) if g.t % 20 >= 10 else (255, 180, 60))
        arcade.draw_text("RESTAURANT", x + w / 2, y + h - 22, (150, 40, 40), 6, anchor_x="center", bold=True)
        # Klanten met een tekstwolkje: wat ze willen en hoe lang ze nog wachten
        klanten = [k for k in sp._kk_klanten if k["restaurant"] is g]
        for i, k in enumerate(klanten):
            kx = x + w + 8 + i * 20
            kleur = ((k["nr"] * 70) % 200 + 55, (k["nr"] * 130) % 200 + 55, (k["nr"] * 40) % 200 + 55)
            arcade.draw_lrbt_rectangle_filled(kx, kx + 10, y + 6, y + 16, kleur)
            arcade.draw_circle_filled(kx + 5, y + 20, 4, (240, 205, 170))
            arcade.draw_line(kx + 3, y, kx + 3, y + 6, (60, 50, 50), 2)
            arcade.draw_line(kx + 7, y, kx + 7, y + 6, (60, 50, 50), 2)
            arcade.draw_ellipse_filled(kx + 5, y + 38, 22, 16, (255, 255, 255))
            _gerecht(k["bestelling"], kx + 5, y + 34)
            deel = k["geduld"] / GEDULD
            arcade.draw_lrbt_rectangle_filled(kx - 2, kx - 2 + 14 * deel, y + 27, y + 29,
                                              (90, 220, 90) if deel > 0.3 else (240, 70, 70))


def teken(sp):
    for g in sp._kk_gebouwen:
        _teken_gebouw(g, sp)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    # De kok: wit jasje met knoopjes, hoge koksmuts, rood sjaaltje
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (250, 250, 250))
    for i in range(3):
        arcade.draw_circle_filled(cx, y + 5 + i * 6, 1.5, (120, 120, 130))
    arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + h * 0.56, y + h * 0.62, (220, 50, 50))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 6, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + h - 6, y + h + 8, (255, 255, 255))
    arcade.draw_circle_filled(x + 9, y + h + 9, 5, (255, 255, 255))
    arcade.draw_circle_filled(cx, y + h + 11, 6, (255, 255, 255))
    arcade.draw_circle_filled(x + w - 9, y + h + 9, 5, (255, 255, 255))
    # Dienblad met gerechten
    bx = x + w + 4 if k > 0 else x - 34
    if sp._kk_blad:
        arcade.draw_lrbt_rectangle_filled(bx, bx + 30, y + h * 0.5, y + h * 0.5 + 3, (170, 170, 180))
        for i, g in enumerate(sp._kk_blad):
            _gerecht(g, bx + 6 + i * 9, y + h * 0.5 + 5)
    if sp._kk_schild > 0:
        arcade.draw_ellipse_outline(cx, y + h / 2, w + 14, h + 16, (230, 150, 80, 150), 2)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 22, (0, 0, 0, 155))
    for i, s in enumerate(GEBOUWEN):
        l = x - 292 + i * 80
        kan = sp._kk_munten >= KOST[s]
        arcade.draw_lrbt_rectangle_filled(l, l + 76, y, y + 18, (160, 90, 40) if kan else (60, 60, 60))
        arcade.draw_text("%d %s" % (i + 1, s), l + 38, y + 4, (255, 255, 255) if kan else (150, 150, 150), 8,
                         anchor_x="center")
    g = gekozen(sp)
    arcade.draw_lrbt_rectangle_filled(x + 112, x + 292, y, y + 18, (90, 60, 110))
    _gerecht(g, x + 124, y + 5)
    arcade.draw_text("6 kies: %s  7 koken  8 slopen" % g, x + 134, y + 4, (255, 255, 255), 7)
    v = sp._kk_voorraad
    arcade.draw_text("munten %d | groente %d  ei %d  meel %d  melk %d" % (sp._kk_munten, v["groente"], v["ei"],
                                                                        v["meel"], v["melk"]),
                     x - 292, y - 24, (240, 220, 160), 10, bold=True)
    krachten = ", ".join("%s %ds" % (k, t // 60 + 1) for k, t in sp._kk_kracht.items())
    if sp._kk_schild:
        krachten = (krachten + ", " if krachten else "") + "schild x%d" % sp._kk_schild
    arcade.draw_text(krachten or "bediend: %d  boos weg: %d" % (sp._kk_bediend, sp._kk_boos), x + 292, y - 24,
                     (200, 230, 200), 9, anchor_x="right")
    if sp._kk_melding_tijd > 0:
        arcade.draw_text(sp._kk_melding, x, y - 50, (255, 230, 180), 13, bold=True, anchor_x="center")

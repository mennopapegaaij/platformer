# pretpark.py
# De PRETPARKBAAS: bouw een pretpark, laat bezoekers betalen en rij zelf mee in de attracties!
#
#  Toets 1 : KASSA       (4 munten)  - hier komen elke 5 seconden nieuwe bezoekers binnen
#  Toets 2 : REUZENRAD   (10 munten) - 4 bakjes draaien rond; bezoekers betalen 2
#                                      (stap zelf in een bakje en draai mee omhoog!)
#  Toets 3 : BOTSAUTO'S  (8 munten)  - bezoekers betalen 1; monsters die erin komen worden weggebotst
#  Toets 4 : ACHTBAAN    (12 munten) - een berg van 120 hoog met een karretje; bezoekers betalen 3
#                                      (spring in het karretje en rij mee naar boven!)
#  Toets 5 : SNOEPKRAAM  (3 munten)  - bezoekers betalen 1; loop jij erlangs = suikerkick (sneller!)
#  Toets 6 : PRULLENBAK  (1 munt)    - bij een prullenbak in de buurt valt er geen afval
#  Omlaag  : SLOPEN      - haal de attractie voor je weg (munten terug)
#
# ZELF MEERIJDEN: spring op een bakje van het reuzenrad of op het karretje van de achtbaan.
#   Dan stap je in: je zit er echt in, achter de beugel, en je ziet het uitzicht van binnenuit!
#   Omlaag   = wisselen tussen je eigen uitzicht en het gewone beeld
#   Springen = uitstappen
#
# BEZOEKERS lopen van de kassa langs 3 attracties (steeds een andere volgorde), staan in de rij,
#   betalen en gaan dan weer naar huis. Ze kunnen niet springen: niet over kuilen!
# AFVAL: wie snoep koopt, laat soms afval vallen. Afval maakt het park minder leuk.
#   Is de BLIJHEID lager dan 40, dan komen er geen nieuwe bezoekers. Loop over afval om het op te ruimen.
# Alles is vast: geen toeval.

import math
import arcade
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE
from platforms import Platform

MUNTEN = 20
SOORTEN = ["kassa", "reuzenrad", "botsauto", "achtbaan", "snoep", "prullenbak"]
NAAM = {"kassa": "kassa", "reuzenrad": "reuzenrad", "botsauto": "botsauto", "achtbaan": "achtbaan",
        "snoep": "snoep", "prullenbak": "prullenbak"}
KOST = {"kassa": 4, "reuzenrad": 10, "botsauto": 8, "achtbaan": 12, "snoep": 3, "prullenbak": 1}
PRIJS = {"reuzenrad": 2, "botsauto": 1, "achtbaan": 3, "snoep": 1}      # wat een bezoeker betaalt
PLEKKEN = {"reuzenrad": 4, "botsauto": 2, "achtbaan": 2, "snoep": 1}
RITTIJD = {"reuzenrad": 300, "botsauto": 180, "achtbaan": 240, "snoep": 60}
MAAT = {"kassa": (36, 40), "reuzenrad": (40, 16), "botsauto": (100, 8), "achtbaan": (40, 12),
        "snoep": (40, 36), "prullenbak": (14, 20)}
ATTRACTIES = ("reuzenrad", "botsauto", "achtbaan", "snoep")
BEZOEKER_TIJD = 300       # elke 5 seconden een nieuwe bezoeker
MAX_BEZOEKERS_PER = 2     # hoogstens 2 bezoekers per attractie (plus 2) tegelijk in het park
LOOP = 1.4
RAD_STRAAL = 70
RAD_HOOGTE = 100          # het midden van het rad zit zo hoog boven de grond (het laagste bakje komt net boven de voet langs)
RAD_DRAAI = 0.008         # zo snel draait het rad
ACHTBAAN = [0, 40, 80, 120, 120, 80, 40, 0, 0]   # hoogtes van de achtbaan, per 40 pixels
ACHTBAAN_SNEL = 2.5
AFVAL_ZONDER_BAK = 2      # elke 2e snoepkoper laat afval vallen (als er geen prullenbak is)
BAK_BEREIK = 200
SUIKER_TIJD = 300         # suikerkick: 5 seconden sneller
SUIKER_RUST = 600         # daarna 10 seconden wachten op de volgende
SUIKER_SNEL = 1.5
INSTAP_RUST = 40          # na het uitstappen even niet meteen weer instappen
UITSTAP_SPRONG = 12       # uitstappen = een gewone sprong


class PretDeel(Platform):
    """Een attractie of een bewegend deel (bakje, karretje): je kunt erop staan."""

    is_pretpark = True

    def __init__(self, soort, x, y, breedte, hoogte):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort
        self.dx = 0

    def teken(self):
        pass                          # (het pretpark tekent alles zelf)


class Attractie(PretDeel):
    def __init__(self, soort, x, y, k):
        w, h = MAAT[soort]
        super().__init__(soort, x, y, w, h)
        self.k = k
        self.rij = []                 # bezoekers die wachten
        self.rijders = []             # bezoekers die nu meerijden
        self.rit = 0                  # hoe lang de rit nog duurt
        self.verkocht = 0
        self.hoek = 0.0               # reuzenrad
        self.bakjes = []              # reuzenrad: 4 PretDelen
        self.kar = None               # achtbaan: het karretje
        self.kar_d = 0.0
        self.kar_r = 1
        self.t = 0
        if soort == "reuzenrad":
            self.bakjes = [PretDeel("bakje", 0, 0, 30, 8) for _ in range(4)]
        if soort == "achtbaan":
            self.kar = PretDeel("kar", 0, 0, 36, 10)
        self.beweeg()

    def midden_rad(self):
        return self.x + self.breedte / 2, self.y + RAD_HOOGTE

    def baan_punt(self, d):
        """Achtbaan: (x, y) van de rails op afstand d (0 = bij het station)."""
        n = len(ACHTBAAN) - 1
        d = max(0, min(n * 40, d))
        i = min(int(d // 40), n - 1)
        f = (d - i * 40) / 40
        start = self.x + self.breedte if self.k > 0 else self.x
        x = start + self.k * d
        return x, self.y + ACHTBAAN[i] + (ACHTBAAN[i + 1] - ACHTBAAN[i]) * f

    def beweeg(self):
        """Het rad draait en het karretje rijdt (altijd, ook als er niemand in zit)."""
        if self.soort == "reuzenrad":
            self.hoek += RAD_DRAAI
            mx, my = self.midden_rad()
            for i, b in enumerate(self.bakjes):
                h = self.hoek + i * math.pi / 2
                oud = b.x
                b.x = mx + math.cos(h) * RAD_STRAAL - b.breedte / 2
                b.y = my + math.sin(h) * RAD_STRAAL - 14
                b.dx = b.x - oud if self.t > 0 else 0
        elif self.soort == "achtbaan":
            n = (len(ACHTBAAN) - 1) * 40
            self.kar_d += ACHTBAAN_SNEL * self.kar_r
            if self.kar_d >= n or self.kar_d <= 0:
                self.kar_d = max(0, min(n, self.kar_d))
                self.kar_r *= -1
            x, y = self.baan_punt(self.kar_d)
            oud = self.kar.x
            self.kar.x = x - self.kar.breedte / 2
            self.kar.y = y + 2
            self.kar.dx = self.kar.x - oud if self.t > 0 else 0
        self.t += 1


def reset(sp):
    sp._pp_munten = MUNTEN
    sp._pp_attracties = []
    sp._pp_bezoekers = []
    sp._pp_afval = []         # (x, y)
    sp._pp_nummer = 0         # telt de bezoekers (voor de volgorde van hun rondje)
    sp._pp_klok = 0
    sp._pp_suiker = 0         # suikerkick: zo lang ben je nog sneller
    sp._pp_suiker_rust = 0
    sp._pp_verdiend = 0
    sp._pp_rit = None         # (attractie, bakje-nummer of None voor het karretje) als je meerijdt
    sp._pp_uitzicht = True    # zie je het uitzicht van binnenuit?
    sp._pp_instap_rust = 0
    sp._pp_t = 0
    sp._pp_melding = ""
    sp._pp_melding_tijd = 0


def _meld(sp, tekst):
    sp._pp_melding = tekst
    sp._pp_melding_tijd = 120


def blijheid(sp):
    return max(0, 100 - 15 * len(sp._pp_afval))


def _vast(p):
    return getattr(p, "vast", True) and not getattr(p, "is_schuin", False)


def _vrij(x, y, w, h, platforms):
    return not any(_vast(p) and x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y
                   for p in platforms)


def _grondstuk(x, y, platforms):
    stukken = sorted(((p.x, p.x + p.breedte) for p in platforms
                      if _vast(p) and not getattr(p, "is_pretpark", False) and abs(p.y + p.hoogte - y) < 1),
                     key=lambda s: s[0])
    samen = []
    for l, r in stukken:
        if samen and l <= samen[-1][1] + 1:
            samen[-1] = (samen[-1][0], max(samen[-1][1], r))
        else:
            samen.append((l, r))
    for l, r in samen:
        if l - 1 <= x <= r + 1:
            return (l, r)
    return None


def plaats(sp, soort, platforms):
    """Toets 1-6: zet een attractie vlak voor je neer."""
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    if sp._pp_munten < KOST[soort]:
        _meld(sp, "Te weinig munten! (laat bezoekers betalen)")
        return False
    k = 1 if sp.kijkt_rechts else -1
    w, h = MAAT[soort]
    x = sp.x + sp.breedte + 2 if k > 0 else sp.x - 2 - w
    if not _vrij(x, sp.y, w, h, platforms) or _grondstuk(x + w / 2, sp.y, platforms) is None:
        _meld(sp, "Daar is geen plek")
        return False
    sp._pp_munten -= KOST[soort]
    sp._pp_attracties.append(Attractie(soort, x, sp.y, k))
    return True


def sloop(sp):
    k = 1 if sp.kijkt_rechts else -1
    kijk_x = sp.x + sp.breedte + 10 if k > 0 else sp.x - 10
    for a in sp._pp_attracties:
        if (a.x <= kijk_x <= a.x + a.breedte and a.y <= sp.y + 5 <= a.y + a.hoogte + 5) or a is sp._gelande_platform:
            sp._pp_attracties.remove(a)
            sp._pp_munten += KOST[a.soort]
            for b in sp._pp_bezoekers:           # wie hier stond of reed, gaat verder
                if b["doel"] is a:
                    b["staat"], b["doel"] = "klaar", None
            return True
    _meld(sp, "Hier staat niks om te slopen")
    return False


def alle_delen(sp):
    uit = []
    for a in sp._pp_attracties:
        uit.append(a)
        uit += a.bakjes
        if a.kar is not None:
            uit.append(a.kar)
    return uit


def loop_factor(sp):
    return SUIKER_SNEL if sp._pp_suiker > 0 else 1.0


def _loop_naar(b, doel_x, stuk):
    if stuk is not None:
        doel_x = max(stuk[0], min(stuk[1] - 10, doel_x))
    dx = doel_x - b["x"]
    b["stap"] += 1
    if abs(dx) <= LOOP:
        b["x"] = doel_x
        return True
    b["x"] += LOOP if dx > 0 else -LOOP
    return False


def _wacht_x(a):
    """Waar staat de rij van deze attractie?"""
    if a.soort == "achtbaan":
        return a.x + a.breedte / 2 - 6
    return a.x + a.breedte / 2 - 6


# ---------------------------------------------------------------------------
# Zelf meerijden
# ---------------------------------------------------------------------------
def rijdt(sp):
    return sp._pp_rit is not None


def _stoel(sp):
    """Het bakje of karretje waar je in zit."""
    a, nr = sp._pp_rit
    return a.bakjes[nr] if nr is not None else a.kar


def _probeer_instappen(sp):
    if sp._pp_rit is not None or sp._pp_instap_rust > 0 or not sp.staat_op_grond:
        return
    g = sp._gelande_platform
    for a in sp._pp_attracties:
        if g in a.bakjes:
            sp._pp_rit = (a, a.bakjes.index(g))
        elif g is not None and g is a.kar:
            sp._pp_rit = (a, None)
        else:
            continue
        sp._pp_uitzicht = True
        _meld(sp, "Ingestapt! Springen = uitstappen, omlaag = uitzicht aan/uit")
        return


def rij_stap(sp):
    """Je zit in een bakje of karretje: je gaat gewoon mee (in plaats van zelf te bewegen)."""
    a, nr = sp._pp_rit
    if a not in sp._pp_attracties:
        sp._pp_rit = None
        return
    s = _stoel(sp)
    sp.x = s.x + s.breedte / 2 - sp.breedte / 2
    sp.y = s.y + 2                               # je zit IN het bakje (je benen zijn achter de rand)
    sp.snelheid_x = s.dx
    sp.snelheid_y = 0
    sp.staat_op_grond = False


def uitstappen(sp):
    """Springen: uitstappen (met een klein sprongetje)."""
    sp._pp_rit = None
    sp._pp_instap_rust = INSTAP_RUST
    sp.snelheid_y = UITSTAP_SPRONG * sp.zwaartekracht_richting
    sp.y += 4
    _meld(sp, "Uitgestapt!")


def wissel_uitzicht(sp):
    sp._pp_uitzicht = not sp._pp_uitzicht
    return True


def wereld(sp, vijanden, platforms):
    """Elke stap: attracties bewegen, bezoekers komen en gaan, afval, botsauto's. Geeft monsters die weg moeten."""
    sp._pp_t += 1
    for teller in ("_pp_suiker", "_pp_suiker_rust", "_pp_melding_tijd", "_pp_instap_rust"):
        if getattr(sp, teller) > 0:
            setattr(sp, teller, getattr(sp, teller) - 1)
    for a in sp._pp_attracties:
        a.beweeg()
    _probeer_instappen(sp)
    attracties = [a for a in sp._pp_attracties if a.soort in ATTRACTIES]
    # Nieuwe bezoekers bij de kassa
    sp._pp_klok += 1
    kassas = [a for a in sp._pp_attracties if a.soort == "kassa"]
    maximum = 2 + MAX_BEZOEKERS_PER * len(attracties)
    if sp._pp_klok >= BEZOEKER_TIJD:
        sp._pp_klok = 0
        if kassas and attracties and len(sp._pp_bezoekers) < maximum and blijheid(sp) >= 40:
            kassa = kassas[sp._pp_nummer % len(kassas)]
            stuk = _grondstuk(kassa.x + kassa.breedte / 2, kassa.y, platforms)
            bereikbaar = sorted([a for a in attracties if stuk and stuk[0] <= a.x + a.breedte / 2 <= stuk[1]],
                                key=lambda a: a.x)
            if bereikbaar:
                n = sp._pp_nummer
                plan = [bereikbaar[(n + i) % len(bereikbaar)] for i in range(min(3, len(bereikbaar)))]
                sp._pp_bezoekers.append({"x": kassa.x + kassa.breedte / 2, "y": kassa.y, "kassa": kassa,
                                         "plan": plan, "doel": None, "staat": "klaar", "stap": 0, "nr": n,
                                         "kleur": ((n * 70) % 200 + 55, (n * 130) % 200 + 55, (n * 40) % 200 + 55)})
                sp._pp_nummer += 1
    # Bezoekers
    weg = []
    for b in sp._pp_bezoekers:
        stuk = _grondstuk(b["x"] + 5, b["y"], platforms)
        if b["staat"] == "klaar":
            b["plan"] = [a for a in b["plan"] if a in sp._pp_attracties]
            if b["plan"]:
                b["doel"], b["staat"] = b["plan"].pop(0), "naar"
            else:
                b["staat"] = "naar_huis"
        if b["staat"] == "naar":
            if _loop_naar(b, _wacht_x(b["doel"]) - len(b["doel"].rij) * 12, stuk):
                b["staat"] = "wachten"
                b["doel"].rij.append(b)
        elif b["staat"] == "naar_huis":
            kassa = b["kassa"]
            if kassa not in sp._pp_attracties or _loop_naar(b, kassa.x + kassa.breedte / 2, stuk):
                weg.append(b)                          # de bezoeker gaat blij naar huis
    for b in weg:
        sp._pp_bezoekers.remove(b)
    # Attracties: instappen, betalen, rijden, uitstappen
    for a in attracties:
        a.rij = [b for b in a.rij if b in sp._pp_bezoekers and b["staat"] == "wachten"]
        if a.rit > 0:
            a.rit -= 1
            if a.rit == 0:
                for b in a.rijders:
                    b["staat"], b["doel"] = "klaar", None
                    if a.soort == "snoep":
                        _snoep_op(sp, a, b)
                a.rijders = []
        elif a.rij:
            a.rijders = a.rij[:PLEKKEN[a.soort]]
            a.rij = a.rij[PLEKKEN[a.soort]:]
            for b in a.rijders:
                b["staat"] = "rijden"
                sp._pp_munten += PRIJS[a.soort]
                sp._pp_verdiend += PRIJS[a.soort]
                a.verkocht += 1
            a.rit = RITTIJD[a.soort]
    # Afval opruimen door eroverheen te lopen
    cx = sp.x + sp.breedte / 2
    sp._pp_afval = [(x, y) for (x, y) in sp._pp_afval if not (abs(x - cx) < 20 and abs(y - sp.y) < 30)]
    # Suikerkick bij de snoepkraam
    for a in sp._pp_attracties:
        if (a.soort == "snoep" and sp._pp_suiker_rust == 0 and abs(a.x + a.breedte / 2 - cx) < 30
                and abs(a.y - sp.y) < 40):
            sp._pp_suiker = SUIKER_TIJD
            sp._pp_suiker_rust = SUIKER_RUST
            _meld(sp, "Suikerkick! Je bent 5 seconden sneller")
    # Botsauto's botsen monsters weg
    monsters_weg = []
    for a in sp._pp_attracties:
        if a.soort == "botsauto":
            for v in vijanden:
                if (not getattr(v, "is_spike", False) and v not in monsters_weg
                        and v.x < a.x + a.breedte and v.x + v.breedte > a.x and abs(v.y - a.y) < 40):
                    monsters_weg.append(v)
    return monsters_weg


def _snoep_op(sp, kraam, b):
    """Een bezoeker heeft snoep gekocht. Zonder prullenbak in de buurt valt er soms afval."""
    if any(p.soort == "prullenbak" and abs(p.x - kraam.x) <= BAK_BEREIK for p in sp._pp_attracties):
        return
    if kraam.verkocht % AFVAL_ZONDER_BAK == 0:
        afstand = 50 + (kraam.verkocht * 23) % 60
        richting = 1 if b["nr"] % 2 == 0 else -1
        sp._pp_afval.append((kraam.x + kraam.breedte / 2 + richting * afstand, kraam.y))


# ===========================================================================
# Tekenen
# ===========================================================================
def _mensje(x, y, kleur, stap=0):
    arcade.draw_line(x + 3, y, x + 4, y + 7 - stap, (60, 50, 50), 2)
    arcade.draw_line(x + 7, y, x + 6, y + 5 + stap, (60, 50, 50), 2)
    arcade.draw_lrbt_rectangle_filled(x + 1, x + 9, y + 6, y + 14, kleur)
    arcade.draw_circle_filled(x + 5, y + 17, 3.5, (240, 205, 170))


def _teken_attractie(a, t):
    x, y, w, h = a.x, a.y, a.breedte, a.hoogte
    s = a.soort
    if s == "kassa":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h - 10, (230, 80, 80))
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + 14, y + h - 16, (250, 240, 200))
        for i in range(4):
            arcade.draw_lrbt_rectangle_filled(x + i * 9, x + i * 9 + 9, y + h - 10, y + h,
                                              (255, 255, 255) if i % 2 else (230, 80, 80))
        arcade.draw_line(x + w / 2, y + h, x + w / 2, y + h + 14, (120, 100, 80), 2)
        arcade.draw_triangle_filled(x + w / 2, y + h + 14, x + w / 2, y + h + 6, x + w / 2 + 10, y + h + 10, (250, 210, 60))
    elif s == "reuzenrad":
        mx, my = a.midden_rad()
        arcade.draw_line(x + 6, y + h, mx, my, (160, 160, 170), 3)
        arcade.draw_line(x + w - 6, y + h, mx, my, (160, 160, 170), 3)
        arcade.draw_circle_outline(mx, my, RAD_STRAAL, (230, 230, 240), 3)
        for i in range(8):
            hh = a.hoek + i * math.pi / 4
            arcade.draw_line(mx, my, mx + math.cos(hh) * RAD_STRAAL, my + math.sin(hh) * RAD_STRAAL, (200, 200, 210), 1)
        arcade.draw_circle_filled(mx, my, 5, (250, 200, 60))
        kleuren = [(230, 80, 80), (80, 150, 230), (250, 210, 60), (90, 200, 110)]
        zit = list(a.rijders) if a.soort == "reuzenrad" else []
        for i, bk in enumerate(a.bakjes):
            arcade.draw_line(bk.x + bk.breedte / 2, bk.y + bk.hoogte, bk.x + bk.breedte / 2, bk.y + 14, (150, 150, 160), 2)
            arcade.draw_lrbt_rectangle_filled(bk.x, bk.x + bk.breedte, bk.y, bk.y + bk.hoogte, kleuren[i])
            if i < len(zit):
                arcade.draw_circle_filled(bk.x + bk.breedte / 2, bk.y + bk.hoogte + 4, 4, (240, 205, 170))
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (120, 110, 130))
    elif s == "botsauto":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 90, 110))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h + 16, (250, 210, 60), 2)
        for i, kleur in enumerate(((230, 70, 70), (70, 140, 230))):
            fase = (t * 0.04 + i * math.pi)
            ax = x + w / 2 + math.sin(fase) * (w / 2 - 14) - 10
            arcade.draw_lrbt_rectangle_filled(ax, ax + 20, y + h, y + h + 10, kleur)
            arcade.draw_line(ax + 10, y + h + 10, ax + 10, y + h + 26, (150, 150, 160), 1)
            if i < len(a.rijders):
                arcade.draw_circle_filled(ax + 10, y + h + 13, 3.5, (240, 205, 170))
    elif s == "achtbaan":
        # Rails met palen
        vorige = None
        for i in range(len(ACHTBAAN)):
            px, py = a.baan_punt(i * 40)
            if ACHTBAAN[i] > 0:
                arcade.draw_line(px, a.y, px, py, (150, 110, 70), 2)
            if vorige:
                arcade.draw_line(vorige[0], vorige[1], px, py, (230, 60, 60), 3)
                arcade.draw_line(vorige[0], vorige[1] - 4, px, py - 4, (180, 40, 40), 1)
            vorige = (px, py)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (230, 60, 60))
        kar = a.kar
        arcade.draw_lrbt_rectangle_filled(kar.x, kar.x + kar.breedte, kar.y, kar.y + kar.hoogte, (250, 210, 60))
        for i in range(len(a.rijders)):
            arcade.draw_circle_filled(kar.x + 10 + i * 14, kar.y + kar.hoogte + 4, 4, (240, 205, 170))
    elif s == "snoep":
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + 18, (240, 200, 220))
        for i in range(5):
            arcade.draw_lrbt_rectangle_filled(x + i * 8, x + i * 8 + 8, y + 26, y + h,
                                              (240, 110, 180) if i % 2 == 0 else (255, 255, 255))
        arcade.draw_line(x + 4, y + 18, x + 4, y + 26, (150, 110, 80), 2)
        arcade.draw_line(x + w - 4, y + 18, x + w - 4, y + 26, (150, 110, 80), 2)
        arcade.draw_line(x + w / 2, y + 18, x + w / 2, y + 30, (255, 255, 255), 2)
        arcade.draw_circle_filled(x + w / 2, y + 31, 5, (240, 90, 160))
    elif s == "prullenbak":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (60, 140, 70))
        arcade.draw_lrbt_rectangle_filled(x - 2, x + w + 2, y + h - 3, y + h, (40, 110, 50))


def teken(sp):
    t = sp._pp_t
    for a in sp._pp_attracties:
        _teken_attractie(a, t)
    for (x, y) in sp._pp_afval:
        arcade.draw_lrbt_rectangle_filled(x - 4, x + 4, y, y + 4, (200, 200, 200))
        arcade.draw_circle_filled(x + 5, y + 2, 2, (240, 110, 180))
    for b in sp._pp_bezoekers:
        if b["staat"] == "rijden":
            continue                                 # (zit in de attractie)
        stap = 2 if (b["stap"] // 6) % 2 else 0
        _mensje(b["x"], b["y"], b["kleur"], stap)
        if b["nr"] % 3 == 0:                          # sommige hebben een ballon
            arcade.draw_line(b["x"] + 9, b["y"] + 12, b["x"] + 12, b["y"] + 30, (200, 200, 200), 1)
            arcade.draw_circle_filled(b["x"] + 12, b["y"] + 34, 5, b["kleur"])
    # De pretparkbaas: gestreept jasje, hoge hoed met een veer, en een fluitje
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    for i in range(5):
        arcade.draw_lrbt_rectangle_filled(x + 3 + i * (w - 6) / 5, x + 3 + (i + 1) * (w - 6) / 5, y, y + h * 0.62,
                                          (230, 60, 60) if i % 2 == 0 else (250, 240, 240))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 7, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_lrbt_rectangle_filled(x + 1, x + w - 1, y + h - 8, y + h - 5, (40, 40, 120))
    arcade.draw_lrbt_rectangle_filled(x + 7, x + w - 7, y + h - 5, y + h + 8, (40, 40, 120))
    arcade.draw_line(x + w - 8, y + h + 4, x + w - 2, y + h + 14, (250, 210, 60), 3)
    if sp._pp_rit is not None:
        # De voorkant van het bakje over je benen, met de veiligheidsbeugel
        s = _stoel(sp)
        a, nr = sp._pp_rit
        kleur = [(230, 80, 80), (80, 150, 230), (250, 210, 60), (90, 200, 110)][nr] if nr is not None else (250, 210, 60)
        voor_y = s.y + s.hoogte + 12
        arcade.draw_lrbt_rectangle_filled(s.x - 3, s.x + s.breedte + 3, s.y, voor_y, kleur)
        arcade.draw_lrbt_rectangle_outline(s.x - 3, s.x + s.breedte + 3, s.y, voor_y, (60, 60, 60), 1)
        arcade.draw_line(s.x, voor_y + 5, s.x + s.breedte, voor_y + 5, (200, 200, 210), 3)
        arcade.draw_line(s.x + 3, voor_y, s.x + 3, voor_y + 5, (200, 200, 210), 2)
        arcade.draw_line(s.x + s.breedte - 3, voor_y, s.x + s.breedte - 3, voor_y + 5, (200, 200, 210), 2)
    if sp._pp_suiker > 0:
        for i in range(3):
            arcade.draw_line(cx - k * (w / 2 + 4 + i * 6), y + 6 + i * 8, cx - k * (w / 2 + 14 + i * 6), y + 6 + i * 8,
                             (240, 110, 180), 2)


# ---------------------------------------------------------------------------
# Uitzicht van binnenuit
# ---------------------------------------------------------------------------
def _handjes(cx, y, omhoog):
    """Je eigen handjes op de beugel (of in de lucht: WIIII!)."""
    for kant in (-1, 1):
        hx = cx + kant * 120
        if omhoog:
            arcade.draw_line(hx, y, hx + kant * 30, y + 150, (240, 205, 170), 18)
            arcade.draw_circle_filled(hx + kant * 30, y + 160, 16, (240, 205, 170))
        else:
            arcade.draw_circle_filled(hx, y + 8, 16, (240, 205, 170))


def _baan_hoogte(a, dd):
    n = (len(ACHTBAAN) - 1) * 40
    return a.baan_punt(max(0, min(n, dd)))[1] - a.y


def _teken_achtbaan_uitzicht(sp, a, W, H, t):
    n = (len(ACHTBAAN) - 1) * 40
    d, r = a.kar_d, a.kar_r
    helling = (_baan_hoogte(a, d + r * 10) - _baan_hoogte(a, d - r * 10)) / 20     # >0 = omhoog
    horizon = H * 0.55 - helling * 160                                           # omhoog kijken: horizon zakt
    arcade.draw_lrbt_rectangle_filled(0, W, 0, H, (120, 190, 250))              # lucht
    arcade.draw_circle_filled(W * 0.8, H * 0.85, 30, (255, 240, 150))           # zon
    if horizon > 0:
        arcade.draw_lrbt_rectangle_filled(0, W, 0, horizon, (90, 170, 80))      # gras
        arcade.draw_circle_outline(W * 0.2, horizon + 40, 30, (240, 240, 250), 3)            # reuzenrad in de verte
        arcade.draw_lrbt_rectangle_filled(W * 0.65, W * 0.7, horizon, horizon + 25, (230, 80, 80))
    # De rails vóór je, in perspectief (hoe verder weg, hoe kleiner)
    cx = W / 2
    oog = 30
    vorige = None
    hoogste_sy = -1e9                              # wat achter een top ligt, kun je niet zien
    for i in range(1, 40):
        s = i * 8
        dh = _baan_hoogte(a, d + r * s) - _baan_hoogte(a, d)
        p = 260 / (s + 26)
        sy = horizon + (dh - oog) * p * 1.4 + oog * 0.9
        halve = 60 * p
        if sy < hoogste_sy - 1:
            break                                  # achter de top: verborgen
        hoogste_sy = max(hoogste_sy, sy)
        if vorige:
            arcade.draw_line(cx - vorige[1], vorige[0], cx - halve, sy, (230, 60, 60), max(1, 6 * p))
            arcade.draw_line(cx + vorige[1], vorige[0], cx + halve, sy, (230, 60, 60), max(1, 6 * p))
        if i % 2 == 0:
            arcade.draw_line(cx - halve, sy, cx + halve, sy, (150, 110, 70), max(1, 4 * p))
        vorige = (sy, halve)
        if d + r * s <= 0 or d + r * s >= n:
            break                                  # daar houdt de baan op
    for i in range(8):                             # snelheidsstreepjes
        f = (t * 6 + i * 70) % 400
        arcade.draw_line(40 + i * 100, H - 60 - f * 0.3, 20 + i * 100, H - 80 - f * 0.3, (255, 255, 255, 120), 2)
    # De voorkant van het karretje, de beugel en je handjes
    arcade.draw_lrbt_rectangle_filled(0, W, 0, 70, (250, 210, 60))
    arcade.draw_lrbt_rectangle_filled(0, W, 64, 74, (220, 170, 40))
    arcade.draw_line(W * 0.25, 90, W * 0.75, 90, (200, 200, 210), 10)
    naar_beneden = helling < -0.3
    _handjes(cx, 80, naar_beneden)
    if naar_beneden:
        arcade.draw_text("WIIIIII!", cx, H * 0.7, (255, 255, 255), 36, bold=True, anchor_x="center")


def _teken_rad_uitzicht(sp, a, nr, W, H, t):
    b = a.bakjes[nr]
    hoog = b.y - a.y                               # zo hoog zit je boven de grond
    arcade.draw_lrbt_rectangle_filled(0, W, 0, H, (140, 200, 250))
    if hoog > 90:
        for i in range(3):                         # wolken
            wx = (i * 280 + t * 0.3) % (W + 200) - 100
            arcade.draw_ellipse_filled(wx, H * 0.75 - i * 30 + (180 - hoog) * 0.5, 120, 40, (255, 255, 255, 220))
    # De grond zakt weg als je hoger komt, en het pretpark wordt kleiner
    schaal = max(0.3, 1.2 - hoog / 180)
    grond = 80 + max(0, 200 - hoog) * 1.1          # hoe hoger je zit, hoe verder de grond wegzakt
    if grond > 0:
        arcade.draw_lrbt_rectangle_filled(0, W, 0, grond, (90, 170, 80))
    cx = W / 2
    kleuren = {"kassa": (230, 80, 80), "botsauto": (90, 90, 110), "achtbaan": (230, 60, 60),
               "snoep": (240, 110, 180), "prullenbak": (60, 140, 70)}
    for ander in sp._pp_attracties:
        if ander.soort == "reuzenrad":
            continue
        ax = cx + (ander.x - a.x) * schaal * 1.5
        hoogte = 120 if ander.soort == "achtbaan" else 40
        arcade.draw_lrbt_rectangle_filled(ax, ax + 40 * schaal * 1.5, grond, grond + hoogte * schaal, kleuren[ander.soort])
    for bz in sp._pp_bezoekers:
        arcade.draw_circle_filled(cx + (bz["x"] - a.x) * schaal * 1.5, grond + 6 * schaal, max(1.5, 4 * schaal),
                                  bz["kleur"])
    hx, hy = -60, H * 0.5 + (hoog - RAD_HOOGTE) * 1.2          # spaken van het rad aan de zijkant
    for i in range(6):
        hh = a.hoek + i * math.pi / 3
        arcade.draw_line(hx, hy, hx + math.cos(hh) * 500, hy + math.sin(hh) * 500, (230, 230, 240), 4)
    kleur = [(230, 80, 80), (80, 150, 230), (250, 210, 60), (90, 200, 110)][nr]
    arcade.draw_lrbt_rectangle_filled(0, W, 0, 70, kleur)
    arcade.draw_line(W * 0.25, 90, W * 0.75, 90, (200, 200, 210), 10)
    _handjes(cx, 80, False)
    arcade.draw_text("%d meter hoog" % max(0, int(hoog / 10)), cx, H - 40, (40, 60, 90), 18, bold=True, anchor_x="center")


def teken_uitzicht(sp):
    """Als je meerijdt (en het uitzicht aan staat): het hele scherm = wat je vanuit je bakje ziet."""
    if sp._pp_rit is None or not sp._pp_uitzicht:
        return False
    a, nr = sp._pp_rit
    if nr is None:
        _teken_achtbaan_uitzicht(sp, a, SCHERM_BREEDTE, SCHERM_HOOGTE, sp._pp_t)
    else:
        _teken_rad_uitzicht(sp, a, nr, SCHERM_BREEDTE, SCHERM_HOOGTE, sp._pp_t)
    arcade.draw_text("springen = uitstappen     omlaag = gewoon beeld", SCHERM_BREEDTE / 2, 20, (60, 40, 20), 11,
                     bold=True, anchor_x="center")
    return True


def teken_hud(sp, x, y):
    if teken_uitzicht(sp):
        return
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Munten: %d" % sp._pp_munten, x - 292, y - 24, (250, 210, 60), 11, bold=True)
    bl = blijheid(sp)
    kleur = (90, 230, 110) if bl >= 70 else (250, 200, 60) if bl >= 40 else (240, 70, 70)
    arcade.draw_text("Blijheid: %d%%" % bl, x - 180, y - 24, kleur, 11, bold=True)
    arcade.draw_text("Bezoekers: %d" % len(sp._pp_bezoekers), x - 50, y - 24, (220, 220, 230), 10)
    if bl < 40:
        arcade.draw_text("Te veel afval: er komen geen bezoekers!", x + 60, y - 24, (240, 90, 90), 9, bold=True)
    else:
        arcade.draw_text("omlaag = slopen", x + 292, y - 24, (200, 200, 200), 9, anchor_x="right")
    for i, s in enumerate(SOORTEN):
        l = x - 292 + i * 98
        kan = sp._pp_munten >= KOST[s]
        arcade.draw_lrbt_rectangle_filled(l, l + 94, y, y + 18, (150, 60, 110) if kan else (60, 60, 60))
        arcade.draw_text("%d %s (%d)" % (i + 1, NAAM[s], KOST[s]), l + 47, y + 4, (255, 255, 255) if kan else (150, 150, 150),
                         9, anchor_x="center")
    if sp._pp_melding_tijd > 0:
        arcade.draw_text(sp._pp_melding, x, y - 50, (255, 210, 240), 13, bold=True, anchor_x="center")

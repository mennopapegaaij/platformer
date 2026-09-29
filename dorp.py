# dorp.py
# Het DORPSHOOFD: bouw een dorp met bewoners die hout, steen en eten maken
# en die bruggen, trappen en muren voor je bouwen!
#
#  Toets 1 : HUT          (5 hout)          - er komen 2 bewoners wonen
#  Toets 2 : HOUTHAKKER   (4 hout)          - werker: elke 4 seconden 1 hout
#  Toets 3 : STEENGROEVE  (6 hout)          - werker: elke 5 seconden 1 steen
#  Toets 4 : BOERDERIJ    (4 hout, 2 steen) - werker: elke 3 seconden 1 eten
#  Toets 5 : BRUG         (2 hout per stuk) - bewoners bouwen een brug vanaf waar je staat
#  Toets 6 : STENEN TRAP  (2 steen per tree)- bewoners bouwen een trap omhoog
#  Toets 7 : MUUR         (3 steen)         - monsters kunnen er niet langs
#  Omlaag  : SLOPEN       - haal het gebouw (of het bouwproject) voor je weg, spullen terug
#
# WERKERS: een werkplaats doet pas iets als er een bewoner komt werken.
# BOUWERS: bewoners zonder werk bouwen vanzelf aan je bruggen, trappen en muren.
#   Ze lopen er echt naartoe (niet over kuilen!), en over een brug die ze aan het bouwen zijn.
# HONGER: elke bewoner eet om de 20 seconden 1 eten. Geen eten? Dan stoppen ze met werken.
# Alles is vast: geen toeval.

import arcade
from platforms import Platform

START = {"hout": 10, "steen": 5, "eten": 10}
START_BEWONERS = 2
SOORTEN = ["hut", "houthakker", "steengroeve", "boerderij", "brug", "trap", "muur"]
NAAM = {"hut": "hut", "houthakker": "hout", "steengroeve": "steen", "boerderij": "boer",
        "brug": "brug", "trap": "trap", "muur": "muur"}
KOST = {"hut": {"hout": 5}, "houthakker": {"hout": 4}, "steengroeve": {"hout": 6},
        "boerderij": {"hout": 4, "steen": 2}}
STUK_KOST = {"brug": {"hout": 2}, "trap": {"steen": 2}, "muur": {"steen": 3}}
MAAT = {"hut": (44, 40), "houthakker": (44, 36), "steengroeve": (44, 30), "boerderij": (52, 34)}
WERK = {"houthakker": ("hout", 240), "steengroeve": ("steen", 300), "boerderij": ("eten", 180)}
MAX_STUKKEN = {"brug": 10, "trap": 8, "muur": 1}
BOUW_TIJD = {"brug": 60, "trap": 60, "muur": 120}   # zo lang doet een bouwer over 1 stuk
BRUG_STUK = 40
TREDE = 32
TREDE_HOOGTE = 24
MUUR_BREEDTE, MUUR_HOOGTE = 20, 70
EET_TIJD = 1200           # elke 20 seconden eet een bewoner 1 eten
LOOP = 1.5


class DorpDeel(Platform):
    """Een gebouw of een stuk brug/trap/muur: je kunt erop staan."""

    is_dorp = True

    def __init__(self, soort, x, y, breedte, hoogte):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort
        self.werker = None
        self.werk = 0
        self.t = 0

    def teken(self):
        pass                          # (het dorp tekent alles zelf)


def reset(sp):
    sp._dp_voorraad = dict(START)
    sp._dp_gebouwen = []
    sp._dp_projecten = []     # {"soort", "x0", "y", "k", "stukken" [DorpDeel], "bouwer", "werk", "klaar"}
    sp._dp_bewoners = []
    sp._dp_start_bewoners = True  # de eerste 2 bewoners komen met je mee
    sp._dp_t = 0
    sp._dp_melding = ""
    sp._dp_melding_tijd = 0


def _meld(sp, tekst):
    sp._dp_melding = tekst
    sp._dp_melding_tijd = 120


def _nieuwe_bewoner(sp, x, y, huis):
    sp._dp_bewoners.append({"x": x, "y": y, "huis": huis, "baan": None, "project": None, "staat": "vrij",
                            "doel_x": x, "honger": False, "eet": len(sp._dp_bewoners) * 97 % EET_TIJD,
                            "stap": 0, "rechts": True})


def _vast(p):
    return getattr(p, "vast", True) and not getattr(p, "is_schuin", False)


def _vrij(x, y, w, h, platforms):
    return not any(_vast(p) and x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y
                   for p in platforms)


def _grondstuk(x, y, platforms):
    """Het stuk grond (links, rechts) op hoogte y waar x op ligt (bruggen tellen mee)."""
    stukken = sorted(((p.x, p.x + p.breedte) for p in platforms
                      if _vast(p) and abs(p.y + p.hoogte - y) < 1
                      and (not getattr(p, "is_dorp", False) or p.soort == "brugstuk")),
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


def _kan_betalen(sp, kost):
    return all(sp._dp_voorraad[s] >= n for s, n in kost.items())


def _betaal(sp, kost, terug=False):
    for s, n in kost.items():
        sp._dp_voorraad[s] += n if terug else -n


def plaats(sp, soort, platforms):
    """Toets 1-7: bouw een gebouw of begin een bouwproject voor je."""
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    k = 1 if sp.kijkt_rechts else -1
    if soort in KOST:
        if not _kan_betalen(sp, KOST[soort]):
            _meld(sp, "Te weinig " + " en ".join(KOST[soort]) + "!")
            return False
        w, h = MAAT[soort]
        x = sp.x + sp.breedte + 2 if k > 0 else sp.x - 2 - w
        if not _vrij(x, sp.y, w, h, platforms) or _grondstuk(x + w / 2, sp.y, platforms) is None:
            _meld(sp, "Daar is geen plek")
            return False
        _betaal(sp, KOST[soort])
        g = DorpDeel(soort, x, sp.y, w, h)
        sp._dp_gebouwen.append(g)
        if soort == "hut":
            for i in range(2):
                _nieuwe_bewoner(sp, x + 10 + i * 16, sp.y, g)
        return True
    # Bouwproject: brug, trap of muur, vanaf vlak voor je
    x0 = sp.x + sp.breedte + 2 if k > 0 else sp.x - 2
    if any(abs(p["x0"] - x0) < 40 and p["y"] == sp.y for p in sp._dp_projecten):
        _meld(sp, "Hier wordt al gebouwd")
        return False
    sp._dp_projecten.append({"soort": soort, "x0": x0, "y": sp.y, "k": k, "stukken": [], "bouwer": None,
                             "werk": 0, "klaar": False, "betaald": False})
    _meld(sp, {"brug": "Nieuwe brug: de bewoners gaan bouwen!", "trap": "Nieuwe trap: de bewoners gaan bouwen!",
               "muur": "Nieuwe muur: de bewoners gaan bouwen!"}[soort])
    return True


def _volgend_stuk(p):
    """Waar komt het volgende stuk van dit project? Geeft een DorpDeel (nog niet gebouwd)."""
    i, k, x0, y = len(p["stukken"]), p["k"], p["x0"], p["y"]
    if p["soort"] == "brug":
        x = x0 + i * BRUG_STUK if k > 0 else x0 - (i + 1) * BRUG_STUK
        return DorpDeel("brugstuk", x, y - 12, BRUG_STUK, 12)
    if p["soort"] == "trap":
        x = x0 + i * TREDE if k > 0 else x0 - (i + 1) * TREDE
        return DorpDeel("trede", x, y, TREDE, TREDE_HOOGTE * (i + 1))
    x = x0 if k > 0 else x0 - MUUR_BREEDTE
    return DorpDeel("muurstuk", x, y, MUUR_BREEDTE, MUUR_HOOGTE)


def sloop(sp):
    """Omlaag: sloop het gebouw of bouwproject voor je. Je krijgt je spullen terug."""
    k = 1 if sp.kijkt_rechts else -1
    kijk_x = sp.x + sp.breedte + 10 if k > 0 else sp.x - 10
    for g in sp._dp_gebouwen:
        if (g.x <= kijk_x <= g.x + g.breedte and g.y <= sp.y + 5 <= g.y + g.hoogte + 5) or g is sp._gelande_platform:
            sp._dp_gebouwen.remove(g)
            _betaal(sp, KOST[g.soort], terug=True)
            if g.soort == "hut":
                for b in [b for b in sp._dp_bewoners if b["huis"] is g]:
                    _laat_los(sp, b)
                    sp._dp_bewoners.remove(b)
            elif g.werker is not None:
                _laat_los(sp, g.werker)
            return True
    for p in sp._dp_projecten:
        stukken = p["stukken"] or [_volgend_stuk(p)]
        if any(s.x - 10 <= kijk_x <= s.x + s.breedte + 10 for s in stukken) and abs(p["y"] - sp.y) < 200:
            sp._dp_projecten.remove(p)
            for _ in p["stukken"]:
                _betaal(sp, STUK_KOST[p["soort"]], terug=True)
            if p["betaald"]:
                _betaal(sp, STUK_KOST[p["soort"]], terug=True)
            if p["bouwer"] is not None:
                _laat_los(sp, p["bouwer"])
            return True
    _meld(sp, "Hier staat niks om te slopen")
    return False


def _laat_los(sp, b):
    """Deze bewoner heeft geen werk meer."""
    if b["baan"] is not None:
        b["baan"].werker = None
    if b["project"] is not None:
        b["project"]["bouwer"] = None
    b["baan"], b["project"], b["staat"] = None, None, "vrij"


def _loop_naar(b, doel_x, stuk):
    if stuk is not None:
        doel_x = max(stuk[0], min(stuk[1] - 12, doel_x))
    dx = doel_x - b["x"]
    b["stap"] += 1
    if abs(dx) <= LOOP:
        b["x"] = doel_x
        return True
    b["x"] += LOOP if dx > 0 else -LOOP
    b["rechts"] = dx > 0
    return False


def alle_delen(sp):
    """Alles van het dorp waar je op kunt staan."""
    uit = list(sp._dp_gebouwen)
    for p in sp._dp_projecten:
        uit += p["stukken"]
    return uit


def wereld(sp, vijanden, platforms):
    """Elke stap: de bewoners eten, werken en bouwen; muren houden monsters tegen."""
    sp._dp_t += 1
    if sp._dp_melding_tijd > 0:
        sp._dp_melding_tijd -= 1
    if sp._dp_start_bewoners and sp.staat_op_grond:
        sp._dp_start_bewoners = False
        for i in range(START_BEWONERS):
            _nieuwe_bewoner(sp, sp.x - 20 - i * 18, sp.y, None)
    for g in sp._dp_gebouwen:
        g.t += 1
    # Honger
    for b in sp._dp_bewoners:
        b["eet"] += 1
        if b["eet"] >= EET_TIJD and not b["honger"]:
            b["eet"] = 0
            if sp._dp_voorraad["eten"] > 0:
                sp._dp_voorraad["eten"] -= 1
            else:
                b["honger"] = True
        if b["honger"] and sp._dp_voorraad["eten"] > 0:
            sp._dp_voorraad["eten"] -= 1
            b["honger"] = False
            b["eet"] = 0
    # Vrije bewoners zoeken werk: eerst een werkplaats, dan een bouwproject
    for g in sp._dp_gebouwen:
        if g.soort in WERK and g.werker is None:
            b = _vrije_bewoner(sp, g.x + g.breedte / 2, g.y, platforms)
            if b is not None:
                b["baan"], b["staat"] = g, "naar_werk"
                g.werker = b
    for p in sp._dp_projecten:
        if not p["klaar"] and p["bouwer"] is None:
            b = _vrije_bewoner(sp, p["x0"], p["y"], platforms)
            if b is not None:
                b["project"], b["staat"] = p, "bouwen"
                p["bouwer"] = b
    # Bewoners doen hun ding
    for b in sp._dp_bewoners:
        stuk = _grondstuk(b["x"] + 6, b["y"], platforms)
        if b["staat"] == "vrij":
            h = b["huis"]
            thuis = h.x + h.breedte / 2 if h is not None else b["doel_x"]
            if _loop_naar(b, b["doel_x"], stuk):
                b["doel_x"] = thuis - 30 if b["x"] >= thuis else thuis + 30
        elif b["staat"] == "naar_werk":
            g = b["baan"]
            if _loop_naar(b, g.x + g.breedte / 2 - 6, stuk):
                b["staat"] = "werken"
        elif b["staat"] == "werken" and not b["honger"]:
            g = b["baan"]
            stof, tijd = WERK[g.soort]
            g.werk += 1
            if g.werk >= tijd:
                g.werk = 0
                sp._dp_voorraad[stof] += 1
        elif b["staat"] == "bouwen" and not b["honger"]:
            _bouw_stap(sp, b, b["project"], stuk, platforms)
    # Muren: monsters lopen er niet langs
    muren = [s for p in sp._dp_projecten if p["soort"] == "muur" for s in p["stukken"]]
    for v in vijanden:
        if getattr(v, "is_spike", False):
            continue
        for m in muren:
            if v.x < m.x + m.breedte and v.x + v.breedte > m.x and v.y < m.y + m.hoogte and v.y + v.hoogte > m.y:
                if v.x + v.breedte / 2 < m.x + m.breedte / 2:
                    v.x = m.x - v.breedte                       # terug naar links
                    if getattr(v, "snelheid", 0) > 0:
                        v.snelheid = -v.snelheid
                else:
                    v.x = m.x + m.breedte                       # terug naar rechts
                    if getattr(v, "snelheid", 0) < 0:
                        v.snelheid = -v.snelheid


def _vrije_bewoner(sp, x, y, platforms):
    """De dichtstbijzijnde vrije bewoner die er (over de grond) kan komen."""
    stuk = _grondstuk(x, y, platforms)
    kandidaten = [b for b in sp._dp_bewoners if b["staat"] == "vrij" and abs(b["y"] - y) < 1
                  and stuk is not None and stuk[0] - 1 <= b["x"] + 6 <= stuk[1] + 1]
    if not kandidaten:
        return None
    return min(kandidaten, key=lambda b: (abs(b["x"] - x), b["x"]))


def _bouw_stap(sp, b, p, stuk, platforms):
    """De bouwer loopt naar het volgende stuk en bouwt het."""
    nieuw = _volgend_stuk(p)
    # Waar moet de bouwer staan? Aan het eind van wat er al staat (bij een brug: op de brug)
    if p["k"] > 0:
        doel = nieuw.x - 12
    else:
        doel = nieuw.x + nieuw.breedte
    if not _loop_naar(b, doel, stuk):
        return
    # Is het project klaar? (het maximum, of het volgende stuk zou in de grond of een blok komen:
    # bij een brug betekent dat: de overkant is bereikt)
    anders = [q for q in platforms if not getattr(q, "is_dorp", False)]
    if p["soort"] == "brug":
        in_de_weg = p["stukken"] and not _vrij(nieuw.x + 2, nieuw.y + 2, nieuw.breedte - 4, 8, anders)
    else:
        in_de_weg = not _vrij(nieuw.x + 1, nieuw.y + 1, nieuw.breedte - 2, nieuw.hoogte - 2, anders)
    if len(p["stukken"]) >= MAX_STUKKEN[p["soort"]] or in_de_weg:
        p["klaar"] = True
        _laat_los(sp, b)
        return
    if not p["betaald"]:
        if not _kan_betalen(sp, STUK_KOST[p["soort"]]):
            b["wacht_op"] = " en ".join(STUK_KOST[p["soort"]])
            return                                   # wachten op hout of steen
        _betaal(sp, STUK_KOST[p["soort"]])
        p["betaald"] = True
    b["wacht_op"] = None
    p["werk"] += 1
    if p["werk"] >= BOUW_TIJD[p["soort"]]:
        p["werk"] = 0
        p["betaald"] = False
        p["stukken"].append(nieuw)


# ===========================================================================
# Tekenen
# ===========================================================================
KLEREN = {None: (150, 140, 120), "houthakker": (180, 60, 50), "steengroeve": (120, 120, 130),
          "boerderij": (90, 150, 60), "bouwer": (230, 170, 40)}


def _teken_gebouw(g):
    x, y, w, h = g.x, g.y, g.breedte, g.hoogte
    s = g.soort
    if s == "hut":
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.6, (160, 110, 70))
        arcade.draw_triangle_filled(x - 3, y + h * 0.6, x + w + 3, y + h * 0.6, x + w / 2, y + h, (220, 190, 90))
        arcade.draw_lrbt_rectangle_filled(x + w / 2 - 6, x + w / 2 + 6, y, y + 14, (90, 60, 35))
    elif s == "houthakker":
        for i in range(3):
            arcade.draw_circle_filled(x + 10 + i * 10, y + 6, 6, (140, 90, 50))
            arcade.draw_circle_filled(x + 10 + i * 10, y + 6, 3, (200, 160, 110))
        arcade.draw_lrbt_rectangle_filled(x + w - 10, x + w - 6, y, y + 22, (100, 70, 40))    # boom
        arcade.draw_circle_filled(x + w - 8, y + 28, 10, (60, 140, 60))
        arcade.draw_line(x + 18, y + 14, x + 26, y + 30, (120, 90, 60), 2)                 # bijl
        arcade.draw_triangle_filled(x + 24, y + 26, x + 32, y + 30, x + 27, y + 34, (200, 200, 210))
    elif s == "steengroeve":
        arcade.draw_polygon_filled([(x, y), (x + w, y), (x + w - 6, y + h), (x + 8, y + h - 6)], (130, 130, 135))
        for i in range(3):
            arcade.draw_lrbt_rectangle_filled(x + 6 + i * 12, x + 14 + i * 12, y + 4, y + 12, (170, 170, 175))
    elif s == "boerderij":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 6, (110, 80, 50))
        groei = min(1.0, g.werk / WERK["boerderij"][1]) if g.werker else 0
        for i in range(6):
            arcade.draw_line(x + 4 + i * 8, y + 6, x + 4 + i * 8, y + 10 + 14 * groei, (220, 200, 80), 2)
        arcade.draw_lrbt_rectangle_filled(x + w - 16, x + w, y + 6, y + h - 6, (190, 60, 50))      # schuurtje
        arcade.draw_triangle_filled(x + w - 18, y + h - 6, x + w + 2, y + h - 6, x + w - 8, y + h + 2, (150, 40, 40))
    if s in WERK and g.werker is None:
        arcade.draw_text("?", x + w / 2, y + h + 4, (255, 240, 120), 14, bold=True, anchor_x="center")


def _teken_stuk(s):
    x, y, w, h = s.x, s.y, s.breedte, s.hoogte
    if s.soort == "brugstuk":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 100, 55))
        for i in range(4):
            arcade.draw_line(x + i * 10, y, x + i * 10, y + h, (100, 65, 35), 1)
        arcade.draw_line(x, y + h + 12, x + w, y + h + 12, (120, 90, 60), 2)
    elif s.soort == "trede":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 150, 155))
        for ry in range(int(y), int(y + h), 12):
            arcade.draw_line(x, ry, x + w, ry, (110, 110, 115), 1)
    elif s.soort == "muurstuk":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (140, 135, 130))
        for ry in range(int(y), int(y + h), 10):
            arcade.draw_line(x, ry, x + w, ry, (100, 95, 90), 1)


def _teken_bewoner(b, t):
    x, y = b["x"], b["y"]
    baan = b["baan"].soort if b["baan"] is not None else ("bouwer" if b["project"] is not None else None)
    stap = 2 if (b["stap"] // 6) % 2 else 0
    arcade.draw_line(x + 3, y, x + 4, y + 8 - stap, (60, 50, 50), 2)
    arcade.draw_line(x + 9, y, x + 8, y + 6 + stap, (60, 50, 50), 2)
    arcade.draw_lrbt_rectangle_filled(x + 1, x + 11, y + 7, y + 16, KLEREN.get(baan, (150, 140, 120)))
    arcade.draw_circle_filled(x + 6, y + 19, 4, (240, 205, 170))
    if baan == "bouwer":
        arcade.draw_lrbt_rectangle_filled(x + 1, x + 11, y + 21, y + 24, (250, 200, 40))       # helmpje
        if b["staat"] == "bouwen" and b["project"] and b["project"]["werk"] > 0 and t % 20 < 10:
            arcade.draw_line(x + 11, y + 14, x + 17, y + 20, (120, 90, 60), 2)               # hamer
    if b["honger"]:
        arcade.draw_circle_filled(x + 14, y + 30, 7, (255, 255, 255))
        arcade.draw_text("!", x + 14, y + 25, (220, 50, 50), 10, bold=True, anchor_x="center")
    elif b.get("wacht_op"):
        arcade.draw_circle_filled(x + 14, y + 30, 7, (255, 255, 255))
        arcade.draw_text("?", x + 14, y + 25, (90, 90, 90), 10, bold=True, anchor_x="center")


def teken(sp):
    t = sp._dp_t
    for g in sp._dp_gebouwen:
        _teken_gebouw(g)
    for p in sp._dp_projecten:
        for s in p["stukken"]:
            _teken_stuk(s)
        if not p["klaar"]:
            n = _volgend_stuk(p)                         # steigertje waar gebouwd gaat worden
            arcade.draw_lrbt_rectangle_outline(n.x, n.x + n.breedte, n.y, n.y + n.hoogte, (250, 220, 120, 150), 1)
    for b in sp._dp_bewoners:
        _teken_bewoner(b, t)
    # Het dorpshoofd: groene mantel, kroontje van bladeren, wandelstok
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.62, (50, 110, 60))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 6, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    for i in range(5):
        arcade.draw_ellipse_filled(x + 5 + i * 5.5, y + h - 4, 6, 9, (90, 170, 70))
    sx = x + w + 3 if k > 0 else x - 3
    arcade.draw_line(sx, y, sx, y + h * 0.8, (130, 90, 50), 3)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 22, (0, 0, 0, 155))
    v = sp._dp_voorraad
    arcade.draw_text("hout %d   steen %d   eten %d" % (v["hout"], v["steen"], v["eten"]), x - 292, y - 24,
                     (240, 220, 150), 11, bold=True)
    hongerig = sum(1 for b in sp._dp_bewoners if b["honger"])
    arcade.draw_text("bewoners: %d%s" % (len(sp._dp_bewoners), ("  (%d met honger!)" % hongerig) if hongerig else ""),
                     x + 20, y - 24, (240, 120, 120) if hongerig else (220, 220, 230), 10)
    for i, s in enumerate(SOORTEN):
        l = x - 292 + i * 84
        kost = KOST.get(s) or STUK_KOST[s]
        kan = _kan_betalen(sp, kost)
        arcade.draw_lrbt_rectangle_filled(l, l + 80, y, y + 18, (80, 110, 60) if kan else (60, 60, 60))
        arcade.draw_text("%d %s" % (i + 1, NAAM[s]), l + 40, y + 4, (255, 255, 255) if kan else (150, 150, 150), 9,
                         anchor_x="center")
    arcade.draw_text("omlaag = slopen", x + 292, y - 24, (200, 200, 200), 9, anchor_x="right")
    if sp._dp_melding_tijd > 0:
        arcade.draw_text(sp._dp_melding, x, y - 50, (240, 230, 170), 13, bold=True, anchor_x="center")

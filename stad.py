# stad.py
# De STADSBOUWER: bouw een stadje waar poppetjes wonen en werken, en ze helpen jou!
#
#  Toets 1 : HUIS        (4 munten) - er komen 2 bewoners wonen
#  Toets 2 : MARKT       (5 munten) - koopman: elke 3 seconden 1 munt
#  Toets 3 : BAKKERIJ    (6 munten) - bakker: bakt brood en brengt het naar jou (+1 leven)
#  Toets 4 : SMEDERIJ    (6 munten) - smid: maakt schilden en brengt ze naar jou
#  Toets 5 : WACHTTOREN  (7 munten) - wachter: loopt rond en verjaagt monsters
#  Toets 6 : FONTEIN     (4 munten) - werkers in de buurt worden blij en werken 1,5 keer zo snel
#  Omlaag  : SLOPEN      - haal het gebouw voor je weg (munten terug)
#
# WERKERS: een werkplaats (markt, bakkerij, smederij, wachttoren) doet pas iets als er een
#   bewoner komt werken. Een vrije bewoner loopt vanzelf van zijn huis naar de werkplaats.
#   Bewoners kunnen niet springen: ze komen alleen waar de grond doorloopt (niet over een kuil)!
# BEZORGEN: de bakker en de smid lopen naar je toe als je in de buurt bent (op hun stuk grond).
# Alles is vast: geen toeval.

import arcade
from platforms import Platform

MUNTEN = 20               # zoveel munten heb je aan het begin
GEBOUWEN = ["huis", "markt", "bakkerij", "smederij", "toren", "fontein"]
KOST = {"huis": 4, "markt": 5, "bakkerij": 6, "smederij": 6, "toren": 7, "fontein": 4}
NAAM = {"huis": "huis", "markt": "markt", "bakkerij": "bakker", "smederij": "smid", "toren": "toren",
        "fontein": "fontein"}
MAAT = {"huis": (48, 48), "markt": (48, 40), "bakkerij": (48, 48), "smederij": (48, 44),
        "toren": (40, 80), "fontein": (48, 20)}
WERKPLAATS = ("markt", "bakkerij", "smederij", "toren")
BEWONERS_PER_HUIS = 2
LOOP = 1.5                # zo snel lopen bewoners
WACHTER_LOOP = 2.5
MARKT_TIJD = 180          # koopman: 1 munt per 3 seconden
BAK_TIJD = 480            # bakker: 1 brood per 8 seconden
SMEED_TIJD = 480          # smid: 1 schild per 8 seconden
MAX_BROOD = 3
MAX_SCHILD_VOORRAAD = 2
MAX_LEVENS = 5            # de bakker brengt geen brood als je al 5 levens hebt
MAX_SCHILDEN = 3          # zoveel schilden kun je hebben
BEZORG_AFSTAND = 300      # de bakker en smid komen als je zo dichtbij bent
FONTEIN_BEREIK = 200
FONTEIN_BONUS = 1.5
TOREN_BEREIK = 220        # de wachter verjaagt monsters zo ver van zijn toren
PATROUILLE = 100          # de wachter loopt zo ver heen en weer


class Gebouw(Platform):
    """Een gebouw in je stad: je kunt erop staan."""

    is_stad = True

    def __init__(self, soort, x, y):
        w, h = MAAT[soort]
        super().__init__(x, y, w, h)
        self.soort = soort
        self.werker = None            # de bewoner die hier werkt
        self.werk = 0                 # hoe ver het volgende product is
        self.voorraad = 0             # brood of schilden die klaar liggen
        self.glim = 0
        self.t = 0

    def teken(self):
        _teken_gebouw(self)


def reset(sp):
    sp._sb_munten = MUNTEN
    sp._sb_gebouwen = []
    sp._sb_bewoners = []      # {"huis", "x", "y", "baan", "staat", "doel_x", "draagt", "stap"}
    sp._sb_schild = 0         # schilden van de smid
    sp._sb_t = 0
    sp._sb_melding = ""
    sp._sb_melding_tijd = 0
    sp._sb_munt_flits = 0


def _meld(sp, tekst):
    sp._sb_melding = tekst
    sp._sb_melding_tijd = 120


def _vast(p):
    return getattr(p, "vast", True) and not getattr(p, "is_schuin", False)


def _vrij(x, y, w, h, platforms):
    return not any(_vast(p) and x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y
                   for p in platforms)


def _grondstuk(x, y, platforms):
    """Het stuk grond (links, rechts) op hoogte y waar x op ligt: zover kan een bewoner lopen.
    Losse tegels die tegen elkaar liggen tellen als 1 stuk."""
    stukken = sorted(((p.x, p.x + p.breedte) for p in platforms
                      if _vast(p) and not getattr(p, "is_stad", False) and abs(p.y + p.hoogte - y) < 1),
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
    """Toets 1-6: zet een gebouw vlak voor je neer."""
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    if sp._sb_munten < KOST[soort]:
        _meld(sp, "Te weinig munten! (bouw een markt)")
        return False
    w, h = MAAT[soort]
    k = 1 if sp.kijkt_rechts else -1
    x = sp.x + sp.breedte + 2 if k > 0 else sp.x - 2 - w
    y = sp.y
    if not _vrij(x, y, w, h, platforms) or _grondstuk(x + w / 2, y, platforms) is None:
        _meld(sp, "Daar is geen plek")
        return False
    sp._sb_munten -= KOST[soort]
    g = Gebouw(soort, x, y)
    sp._sb_gebouwen.append(g)
    if soort == "huis":
        for i in range(BEWONERS_PER_HUIS):
            sp._sb_bewoners.append({"huis": g, "x": x + 14 + i * 20, "y": y, "baan": None,
                                    "staat": "thuis", "doel_x": x + 14 + i * 20, "draagt": None, "stap": i * 7})
    return True


def sloop(sp):
    """Omlaag: sloop het gebouw voor je (of waar je op staat). Je krijgt je munten terug."""
    k = 1 if sp.kijkt_rechts else -1
    kijk_x = sp.x + sp.breedte + 10 if k > 0 else sp.x - 10
    kandidaten = [g for g in sp._sb_gebouwen
                  if (g.x <= kijk_x <= g.x + g.breedte and g.y <= sp.y + 5 <= g.y + g.hoogte + 5)
                  or g is sp._gelande_platform]
    if not kandidaten:
        _meld(sp, "Hier staat niks om te slopen")
        return False
    g = kandidaten[0]
    sp._sb_gebouwen.remove(g)
    sp._sb_munten += KOST[g.soort]
    if g.soort == "huis":
        for b in [b for b in sp._sb_bewoners if b["huis"] is g]:
            if b["baan"] is not None:
                b["baan"].werker = None          # de werkplaats is zijn werker kwijt
            sp._sb_bewoners.remove(b)
    elif g.werker is not None:
        b = g.werker
        b["baan"], b["draagt"] = None, None
        b["staat"], b["doel_x"] = "naar_huis", b["huis"].x + 20
    return True


def bescherm(sp):
    """Een schild van de smid houdt de klap tegen."""
    if sp._sb_schild > 0:
        sp._sb_schild -= 1
        sp.onkwetsbaar_timer = 60
        _meld(sp, "Je schild ving de klap op!")
        return True
    return False


def _loop_naar(b, doel_x, snelheid, stuk):
    """Loop een stapje naar doel_x (niet verder dan het stuk grond). Geeft True als je er bent."""
    if stuk is not None:
        doel_x = max(stuk[0], min(stuk[1] - 14, doel_x))
    dx = doel_x - b["x"]
    b["stap"] += 1
    if abs(dx) <= snelheid:
        b["x"] = doel_x
        return True
    b["x"] += snelheid if dx > 0 else -snelheid
    b["rechts"] = dx > 0
    return False


def _blij(sp, g):
    """Staat er een fontein in de buurt? Dan werken de werkers sneller."""
    return any(f.soort == "fontein" and abs(f.x - g.x) <= FONTEIN_BEREIK for f in sp._sb_gebouwen)


def wereld(sp, vijanden, platforms):
    """Elke stap: bewoners zoeken werk, lopen, werken en helpen. Geeft de monsters die weg moeten."""
    sp._sb_t += 1
    if sp._sb_melding_tijd > 0:
        sp._sb_melding_tijd -= 1
    if sp._sb_munt_flits > 0:
        sp._sb_munt_flits -= 1
    weg = []
    for g in sp._sb_gebouwen:
        g.t += 1
        if g.glim > 0:
            g.glim -= 1
    # Vrije bewoners zoeken een werkplaats (op hetzelfde stuk grond)
    for g in sp._sb_gebouwen:
        if g.soort not in WERKPLAATS or g.werker is not None:
            continue
        stuk = _grondstuk(g.x + g.breedte / 2, g.y, platforms)
        vrij = [b for b in sp._sb_bewoners if b["baan"] is None and abs(b["y"] - g.y) < 1
                and stuk is not None and stuk[0] - 1 <= b["x"] <= stuk[1] + 1]
        if vrij:
            b = min(vrij, key=lambda b: (abs(b["x"] - g.x), b["x"]))
            b["baan"], b["staat"] = g, "naar_werk"
            g.werker = b
    # Bewoners doen hun ding
    for b in sp._sb_bewoners:
        stuk = _grondstuk(b["x"] + 7, b["y"], platforms)
        g = b["baan"]
        if b["staat"] == "thuis":
            # rondkuieren bij het huis
            h = b["huis"]
            if _loop_naar(b, b["doel_x"], LOOP * 0.5, stuk):
                b["doel_x"] = h.x - 10 if b["x"] > h.x + 20 else h.x + h.breedte + 10
        elif b["staat"] == "naar_huis":
            if _loop_naar(b, b["huis"].x + 20, LOOP, stuk):
                b["staat"] = "thuis"
        elif b["staat"] == "naar_werk":
            if _loop_naar(b, g.x + g.breedte / 2 - 7, LOOP, stuk):
                b["staat"] = "werken"
        elif b["staat"] == "werken":
            _werk(sp, b, g, vijanden, stuk, weg)
        elif b["staat"] == "bezorgen":
            if not _speler_dichtbij(sp, b, stuk):
                b["staat"] = "terug"             # je bent weggelopen: terug naar het werk
            elif _loop_naar(b, sp.x + sp.breedte / 2 - 7, LOOP * 1.5, stuk) or abs(b["x"] - sp.x) < 16:
                _geef(sp, b)
                b["staat"] = "terug"
        elif b["staat"] == "terug":
            if _loop_naar(b, g.x + g.breedte / 2 - 7, LOOP, stuk):
                b["staat"] = "werken"
        elif b["staat"] == "jagen":
            doel = b.get("prooi")
            if doel not in vijanden or doel in weg:
                b["staat"] = "werken"
            elif _loop_naar(b, doel.x + doel.breedte / 2 - 7, WACHTER_LOOP, stuk) or abs(b["x"] + 7 - (doel.x + doel.breedte / 2)) < 24:
                weg.append(doel)                 # monster verjaagd!
                g.glim = 20
                b["staat"] = "werken"
    return weg


def _speler_dichtbij(sp, b, stuk):
    """Is de speler in de buurt, op hetzelfde stuk grond (niet hoog op een blok)?"""
    px = sp.x + sp.breedte / 2
    return (stuk is not None and stuk[0] - 5 <= px <= stuk[1] + 5 and abs(sp.y - b["y"]) < 80
            and abs(px - b["x"]) <= BEZORG_AFSTAND)


def _geef(sp, b):
    if b["draagt"] == "brood":
        if sp.levens < MAX_LEVENS:
            sp.levens += 1
            _meld(sp, "De bakker bracht brood: +1 leven!")
    elif b["draagt"] == "schild":
        sp._sb_schild = min(MAX_SCHILDEN, sp._sb_schild + 1)
        _meld(sp, "De smid bracht een schild!")
    b["draagt"] = None


def _werk(sp, b, g, vijanden, stuk, weg):
    """De bewoner is op zijn werk."""
    tempo = FONTEIN_BONUS if _blij(sp, g) else 1
    if g.soort == "markt":
        g.werk += tempo
        if g.werk >= MARKT_TIJD:
            g.werk = 0
            sp._sb_munten += 1
            sp._sb_munt_flits = 30
            g.glim = 20
    elif g.soort in ("bakkerij", "smederij"):
        tijd, max_v = (BAK_TIJD, MAX_BROOD) if g.soort == "bakkerij" else (SMEED_TIJD, MAX_SCHILD_VOORRAAD)
        if g.voorraad < max_v:
            g.werk += tempo
            if g.werk >= tijd:
                g.werk = 0
                g.voorraad += 1
                g.glim = 20
        nodig = sp.levens < MAX_LEVENS if g.soort == "bakkerij" else sp._sb_schild < MAX_SCHILDEN
        if g.voorraad > 0 and nodig and _speler_dichtbij(sp, b, stuk):
            g.voorraad -= 1
            b["draagt"] = "brood" if g.soort == "bakkerij" else "schild"
            b["staat"] = "bezorgen"
    elif g.soort == "toren":
        tx = g.x + g.breedte / 2
        prooien = [v for v in vijanden if not getattr(v, "is_spike", False) and v not in weg
                   and abs(v.x + v.breedte / 2 - tx) <= TOREN_BEREIK and abs(v.y - g.y) < 60
                   and stuk is not None and stuk[0] <= v.x + v.breedte / 2 <= stuk[1]]
        if prooien:
            b["prooi"] = min(prooien, key=lambda v: (abs(v.x - b["x"]), v.x))
            b["staat"] = "jagen"
        else:
            # patrouille: heen en weer rond de toren
            if "patrouille" not in b or _loop_naar(b, b["patrouille"], LOOP, stuk):
                b["patrouille"] = tx + PATROUILLE if b.get("patrouille", tx) <= tx else tx - PATROUILLE


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_gebouw(g):
    x, y, w, h = g.x, g.y, g.breedte, g.hoogte
    s = g.soort
    if s == "huis":
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.65, (235, 215, 170))
        arcade.draw_triangle_filled(x - 2, y + h * 0.65, x + w + 2, y + h * 0.65, x + w / 2, y + h, (200, 60, 50))
        arcade.draw_lrbt_rectangle_filled(x + 8, x + 18, y, y + 18, (130, 80, 40))          # deur
        arcade.draw_lrbt_rectangle_filled(x + 26, x + 38, y + 14, y + 24, (255, 230, 120))  # raam
        arcade.draw_line(x + 32, y + 14, x + 32, y + 24, (130, 80, 40), 1)
    elif s == "markt":
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + 20, (170, 120, 70))       # toonbank
        for i in range(6):
            kleur = (230, 60, 60) if i % 2 == 0 else (250, 250, 250)
            arcade.draw_lrbt_rectangle_filled(x + i * 8, x + i * 8 + 8, y + 28, y + h, kleur)  # luifel
        arcade.draw_line(x + 3, y + 20, x + 3, y + 28, (120, 80, 40), 2)
        arcade.draw_line(x + w - 3, y + 20, x + w - 3, y + 28, (120, 80, 40), 2)
        arcade.draw_circle_filled(x + w / 2, y + 12, 5, (250, 210, 60))
    elif s == "bakkerij":
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.7, (240, 230, 210))
        arcade.draw_lrbt_rectangle_filled(x - 2, x + w + 2, y + h * 0.7, y + h * 0.8, (160, 100, 60))
        arcade.draw_lrbt_rectangle_filled(x + 30, x + 38, y + h * 0.8, y + h + 6, (140, 90, 60))   # schoorsteen
        if g.werker is not None and g.werker["staat"] == "werken":
            f = (g.t // 8) % 4
            arcade.draw_circle_filled(x + 34 + f, y + h + 10 + f * 3, 3 + f, (220, 220, 220, 170 - f * 30))
        arcade.draw_ellipse_filled(x + w / 2, y + 16, 22, 10, (210, 150, 70))              # brood-bord
        for i in range(g.voorraad):
            arcade.draw_ellipse_filled(x + 8 + i * 12, y + 4, 10, 5, (200, 140, 60))
    elif s == "smederij":
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.75, (110, 100, 100))
        arcade.draw_triangle_filled(x - 2, y + h * 0.75, x + w + 2, y + h * 0.75, x + w / 2, y + h, (80, 70, 70))
        arcade.draw_lrbt_rectangle_filled(x + 14, x + 34, y + 10, y + 16, (60, 60, 65))      # aambeeld
        arcade.draw_lrbt_rectangle_filled(x + 20, x + 28, y + 4, y + 10, (60, 60, 65))
        if g.werker is not None and g.werker["staat"] == "werken" and g.t % 20 < 6:
            for i in range(3):
                arcade.draw_line(x + 24, y + 17, x + 18 + i * 6, y + 25, (255, 200, 80), 2)
        for i in range(g.voorraad):
            arcade.draw_circle_filled(x + 8 + i * 10, y + 26, 4, (120, 170, 230))
    elif s == "toren":
        arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y, y + h - 12, (150, 140, 130))
        for i in range(3):
            arcade.draw_lrbt_rectangle_filled(x + 2 + i * 14, x + 10 + i * 14, y + h - 12, y + h, (150, 140, 130))
        arcade.draw_lrbt_rectangle_filled(x + 15, x + 25, y + 30, y + 44, (40, 40, 50))       # raampje
        arcade.draw_line(x + w / 2, y + h, x + w / 2, y + h + 14, (100, 80, 60), 2)
        arcade.draw_triangle_filled(x + w / 2, y + h + 14, x + w / 2, y + h + 6, x + w / 2 + 12, y + h + 10, (60, 120, 220))
    elif s == "fontein":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (170, 170, 180))
        arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h - 6, y + h, (90, 160, 240))
        for i in range(3):
            hoogte = 12 + ((g.t // 5 + i * 3) % 6) * 2
            arcade.draw_line(x + 12 + i * 12, y + h, x + 12 + i * 12, y + h + hoogte, (130, 190, 255), 2)
    if g.soort in WERKPLAATS and g.werker is None:
        arcade.draw_text("?", x + w / 2, y + h + 4, (255, 240, 120), 14, bold=True, anchor_x="center")
    if g.glim > 0:
        arcade.draw_circle_outline(x + w / 2, y + h / 2, 10 + (20 - g.glim), (255, 240, 150, g.glim * 12), 2)


KLEREN = {None: (150, 150, 160), "markt": (70, 170, 80), "bakkerij": (240, 240, 240),
          "smederij": (120, 80, 50), "toren": (60, 100, 200)}


def _teken_bewoner(b):
    x, y = b["x"], b["y"]
    baan = b["baan"].soort if b["baan"] is not None else None
    stap = 2 if (b["stap"] // 6) % 2 else 0
    arcade.draw_line(x + 4, y, x + 5, y + 8 - stap, (60, 50, 50), 2)
    arcade.draw_line(x + 10, y, x + 9, y + 6 + stap, (60, 50, 50), 2)
    arcade.draw_lrbt_rectangle_filled(x + 2, x + 12, y + 7, y + 16, KLEREN.get(baan, (150, 150, 160)))
    arcade.draw_circle_filled(x + 7, y + 19, 4, (240, 205, 170))
    if baan == "bakkerij":
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 11, y + 22, y + 27, (255, 255, 255))   # koksmuts
    elif baan == "toren":
        arcade.draw_line(x + 13, y + 4, x + 13, y + 26, (120, 90, 60), 2)                   # speer
        arcade.draw_triangle_filled(x + 11, y + 26, x + 15, y + 26, x + 13, y + 31, (200, 200, 210))
    elif baan == "smederij":
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 11, y + 7, y + 13, (80, 50, 30))       # schort
    if b["draagt"] == "brood":
        arcade.draw_ellipse_filled(x + 7, y + 32, 12, 6, (210, 150, 70))
    elif b["draagt"] == "schild":
        arcade.draw_circle_filled(x + 7, y + 32, 5, (120, 170, 230))


def teken(sp):
    for b in sp._sb_bewoners:
        _teken_bewoner(b)
    # De stadsbouwer: een burgemeester met hoge hoed en een ketting
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (120, 40, 60))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 8, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_lrbt_rectangle_filled(x + 1, x + w - 1, y + h - 9, y + h - 6, (30, 30, 35))
    arcade.draw_lrbt_rectangle_filled(x + 7, x + w - 7, y + h - 6, y + h + 8, (30, 30, 35))
    arcade.draw_arc_outline(cx, y + h * 0.6, 18, 14, (250, 210, 60), 180, 360, 2)       # ambtsketting
    arcade.draw_circle_filled(cx, y + h * 0.5, 3, (250, 210, 60))
    if sp._sb_schild > 0:
        arcade.draw_ellipse_outline(cx, y + h / 2, w + 14, h + 16, (120, 170, 230, 160), 2)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 22, (0, 0, 0, 155))
    kleur = (255, 255, 150) if sp._sb_munt_flits else (250, 210, 60)
    arcade.draw_text("Munten: %d" % sp._sb_munten, x - 292, y + 1, kleur, 11, bold=True)
    vrij = sum(1 for b in sp._sb_bewoners if b["baan"] is None)
    arcade.draw_text("Bewoners: %d (vrij: %d)  Schilden: %d" % (len(sp._sb_bewoners), vrij, sp._sb_schild),
                     x - 292, y - 24, (220, 220, 230), 10)
    for i, soort in enumerate(GEBOUWEN):
        l = x - 170 + i * 78
        kan = sp._sb_munten >= KOST[soort]
        arcade.draw_lrbt_rectangle_filled(l, l + 74, y, y + 18, (70, 110, 70) if kan else (60, 60, 60))
        arcade.draw_text("%d %s (%d)" % (i + 1, NAAM[soort], KOST[soort]), l + 37, y + 4,
                         (255, 255, 255) if kan else (140, 140, 140), 9, anchor_x="center")
    arcade.draw_text("omlaag = slopen", x + 292, y - 24, (200, 200, 200), 9, anchor_x="right")
    if sp._sb_melding_tijd > 0:
        arcade.draw_text(sp._sb_melding, x, y - 50, (250, 230, 160), 13, bold=True, anchor_x="center")

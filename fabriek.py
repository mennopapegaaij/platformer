# fabriek.py
# De FABRIEK-BAAS: bouw een fabriek die trappen en bruggen voor je maakt!
#
#  Toets 1 : MIJN           (4 tandwielen) - maakt elke seconde een blokje
#  Toets 2 : LOPENDE BAND   (1 tandwiel)   - vervoert blokjes (en jou!) de kant op die je kijkt
#  Toets 3 : TRAPPENBOUWER  (3 tandwielen) - maakt van elk blokje een traptree erbij
#  Toets 4 : BRUGBOUWER     (3 tandwielen) - maakt van elk blokje een stuk brug erbij
#  Toets 5 : TANDWIEL-MACHINE (3 tandwielen) - maakt van elke 3 blokjes 1 nieuw tandwiel
#  Omlaag  : SLOPEN         - haal de machine voor je (of onder je) weg, tandwielen terug
#
# Machines zet je vlak voor je neer, op de grond waar je staat, in de richting waar je kijkt.
# Een mijn gooit zijn blokjes naar voren. Ligt daar een band, dan rijden de blokjes mee.
# Komt een blokje bij een bouwer, dan bouwt die een stukje trap of brug.
# Komt een blokje bij een tandwiel-machine, dan verdien je (na 3 blokjes) een tandwiel.
# Voorbeeld:  [MIJN] -> [band][band] -> [BRUGBOUWER] ====brug====>
# Alles is vast: geen toeval.

import math
import arcade
from platforms import Platform

TANDWIELEN = 12           # zoveel tandwielen heb je aan het begin
KOST = {"mijn": 4, "band": 1, "trap": 3, "brug": 3, "tandwiel": 3}
BLOKJES_PER_TANDWIEL = 3
MACHINE = 40              # machines zijn 40 x 40
BAND_BREEDTE = 64
BAND_HOOGTE = 10
BAND_SNELHEID = 2
MIJN_TIJD = 60            # elke 60 stapjes (1 seconde) een blokje
BLOKJE = 12               # blokjes zijn 12 x 12
MAX_BLOKJES = 30
TREDE_BREEDTE = 32
TREDE_HOOGTE = 24
MAX_TREDEN = 8
BRUG_STUK = 40
BRUG_DIKTE = 12
MAX_BRUG = 10


class FabriekDeel(Platform):
    """Alles wat de fabriek neerzet of bouwt: je kunt erop staan."""

    is_fabriek = True

    def __init__(self, soort, x, y, breedte, hoogte, richting=1):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort            # "mijn", "band", "trap", "brug", "trede" of "brugstuk"
        self.richting = richting      # 1 = rechts, -1 = links
        self.dx = BAND_SNELHEID * richting if soort == "band" else 0   # op een band rijd je mee
        self.klok = 0                 # mijn: aftellen tot het volgende blokje
        self.gebouwd = []             # bouwer: wat hij al gebouwd heeft
        self.voorraad = 0             # tandwiel-machine: zoveel blokjes zitten erin
        self.glim = 0                 # tandwiel-machine: glimt even als er een tandwiel uit komt
        self.t = 0

    def teken(self):
        _teken_deel(self)


def reset(sp):
    sp._fb_tandwielen = TANDWIELEN
    sp._fb_delen = []         # alle FabriekDelen (machines, banden en wat ze bouwden)
    sp._fb_blokjes = []       # {"x", "y", "vy"}
    sp._fb_t = 0
    sp._fb_melding = ""
    sp._fb_melding_tijd = 0


def _meld(sp, tekst):
    sp._fb_melding = tekst
    sp._fb_melding_tijd = 120


def _vast(p):
    return getattr(p, "vast", True) and not getattr(p, "is_schuin", False)


def _overlapt(x, y, w, h, p):
    return x < p.x + p.breedte and x + w > p.x and y < p.y + p.hoogte and y + h > p.y


def _vrij(x, y, w, h, platforms):
    return not any(_vast(p) and _overlapt(x, y, w, h, p) for p in platforms)


def plaats(sp, soort, platforms):
    """Toets 1-4: zet een machine of band vlak voor je neer."""
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    if sp._fb_tandwielen < KOST[soort]:
        _meld(sp, "Te weinig tandwielen! (omlaag = slopen geeft ze terug)")
        return False
    k = 1 if sp.kijkt_rechts else -1
    if soort == "band":
        w, h = BAND_BREEDTE, BAND_HOOGTE
    else:
        w, h = MACHINE, MACHINE
    x = sp.x + sp.breedte + 2 if k > 0 else sp.x - 2 - w
    y = sp.y
    if not _vrij(x, y, w, h, platforms):
        _meld(sp, "Daar is geen plek")
        return False
    sp._fb_tandwielen -= KOST[soort]
    sp._fb_delen.append(FabriekDeel(soort, x, y, w, h, k))
    return True


def sloop(sp):
    """Omlaag: sloop de machine of band voor je (of waar je op staat)."""
    k = 1 if sp.kijkt_rechts else -1
    kijk_x = sp.x + sp.breedte + 10 if k > 0 else sp.x - 10
    kandidaten = [d for d in sp._fb_delen if d.soort in KOST
                  and (d.x <= kijk_x <= d.x + d.breedte and d.y <= sp.y + 5 <= d.y + d.hoogte + 5
                       or d is sp._gelande_platform)]
    if not kandidaten:
        _meld(sp, "Hier staat niks om te slopen")
        return False
    d = kandidaten[0]
    sp._fb_delen.remove(d)
    sp._fb_tandwielen += KOST[d.soort]
    return True


def _bouw(sp, bouwer):
    """Een bouwer krijgt een blokje: bouw een stukje erbij. Geeft False als hij vol is."""
    k = bouwer.richting
    i = len(bouwer.gebouwd)
    if bouwer.soort == "trap":
        if i >= MAX_TREDEN:
            return False
        w, h = TREDE_BREEDTE, TREDE_HOOGTE * (i + 1)
        x = bouwer.x + MACHINE + i * w if k > 0 else bouwer.x - (i + 1) * w
        stuk = FabriekDeel("trede", x, bouwer.y, w, h, k)
    else:
        if i >= MAX_BRUG:
            return False
        w, h = BRUG_STUK, BRUG_DIKTE
        x = bouwer.x + MACHINE + i * w if k > 0 else bouwer.x - (i + 1) * w
        stuk = FabriekDeel("brugstuk", x, bouwer.y + MACHINE - h, w, h, k)
    bouwer.gebouwd.append(stuk)
    sp._fb_delen.append(stuk)
    return True


def _maak_tandwiel(sp, machine):
    """Tandwiel-machine: elke 3 blokjes worden 1 tandwiel."""
    machine.voorraad += 1
    if machine.voorraad >= BLOKJES_PER_TANDWIEL:
        machine.voorraad = 0
        machine.glim = 30
        sp._fb_tandwielen += 1


def stap(sp, platforms):
    """Elke stap: mijnen maken blokjes, blokjes rijden en vallen, bouwers bouwen."""
    sp._fb_t += 1
    if sp._fb_melding_tijd > 0:
        sp._fb_melding_tijd -= 1
    delen = sp._fb_delen
    for d in delen:
        d.t += 1
        if d.glim > 0:
            d.glim -= 1
    # Mijnen: elke seconde een blokje (als de uitgang vrij is)
    for m in [d for d in delen if d.soort == "mijn"]:
        m.klok += 1
        if m.klok < MIJN_TIJD or len(sp._fb_blokjes) >= MAX_BLOKJES:
            continue
        bx = m.x + MACHINE + 1 if m.richting > 0 else m.x - BLOKJE - 1
        by = m.y + 14
        if any(abs(b["x"] - bx) < BLOKJE and abs(b["y"] - by) < 20 for b in sp._fb_blokjes):
            continue                                     # uitgang vol: even wachten
        m.klok = 0
        sp._fb_blokjes.append({"x": bx, "y": by, "vy": 0})
    # Blokjes: meerijden op een band, anders vallen tot ze ergens op liggen
    alles = [p for p in platforms if _vast(p) and not getattr(p, "is_fabriek", False)] + delen
    bouwers = [d for d in delen if d.soort in ("trap", "brug", "tandwiel")]
    klaar = []
    for b in sp._fb_blokjes:
        band = next((p for p in delen if p.soort == "band" and abs(b["y"] - (p.y + p.hoogte)) < 1
                     and b["x"] + BLOKJE > p.x and b["x"] < p.x + p.breedte), None)
        if band is not None:
            b["x"] += band.dx
            b["vy"] = 0
        else:
            b["vy"] -= 0.5
            b["y"] += b["vy"]
            for p in alles:
                top = p.y + p.hoogte
                # Viel het blokje dit stapje door de bovenkant van iets heen? Dan ligt het erop.
                if (b["x"] + BLOKJE > p.x and b["x"] < p.x + p.breedte and b["y"] < top
                        and b["y"] - b["vy"] >= top - 1):
                    b["y"] = top
                    b["vy"] = 0
                    break
        if b["y"] < -100:
            klaar.append(b)                             # in een kuil gevallen
            continue
        # Bij een bouwer aangekomen? Dan wordt het een stukje trap of brug
        for bw in bouwers:
            if _overlapt(b["x"], b["y"], BLOKJE, BLOKJE, bw):
                if bw.soort == "tandwiel":
                    _maak_tandwiel(sp, bw)
                    klaar.append(b)
                elif _bouw(sp, bw):
                    klaar.append(b)
                break
    sp._fb_blokjes = [b for b in sp._fb_blokjes if b not in klaar]


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_deel(d):
    x, y, w, h = d.x, d.y, d.breedte, d.hoogte
    k = d.richting
    if d.soort == "band":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (50, 50, 55))
        schuif = (d.t * BAND_SNELHEID * k) % 16
        for i in range(-1, int(w / 16) + 1):
            sx = x + i * 16 + schuif
            if x <= sx <= x + w - 6:
                arcade.draw_triangle_filled(sx + (6 if k > 0 else 0), y + h / 2, sx + (0 if k > 0 else 6), y + 2,
                                            sx + (0 if k > 0 else 6), y + h - 2, (230, 190, 60))
        arcade.draw_circle_filled(x + 4, y + h / 2, 4, (120, 120, 130))
        arcade.draw_circle_filled(x + w - 4, y + h / 2, 4, (120, 120, 130))
    elif d.soort == "mijn":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (110, 110, 120))
        arcade.draw_lrbt_rectangle_filled(x + 26, x + 34, y + h, y + h + 12, (80, 80, 90))    # schoorsteen
        rook = (d.t // 8) % 4
        arcade.draw_circle_filled(x + 30 + rook, y + h + 16 + rook * 3, 3 + rook, (190, 190, 190, 160 - rook * 30))
        uit = x + w if k > 0 else x
        arcade.draw_triangle_filled(uit, y + 10, uit, y + 24, uit + k * 6, y + 17, (230, 190, 60))
        # draaiend boortje
        boor = (d.t % 20) / 20 * 6
        arcade.draw_triangle_filled(x + 12, y + 30, x + 22, y + 30, x + 17, y + 14 + boor, (200, 200, 210))
    elif d.soort in ("trap", "brug"):
        kleur = (220, 130, 40) if d.soort == "trap" else (60, 120, 210)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, kleur)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 40, 40), 2)
        if d.soort == "trap":
            for i in range(3):
                arcade.draw_lrbt_rectangle_filled(x + 8 + i * 8, x + 16 + i * 8, y + 8, y + 14 + i * 7, (255, 230, 180))
        else:
            arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + 22, y + 26, (230, 240, 255))
            for i in range(3):
                arcade.draw_lrbt_rectangle_filled(x + 9 + i * 10, x + 12 + i * 10, y + 10, y + 22, (230, 240, 255))
        arcade.draw_text(str(len(d.gebouwd)), x + w / 2, y + 1, (255, 255, 255), 8, anchor_x="center")
    elif d.soort == "tandwiel":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 120, 60))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 40, 40), 2)
        # draaiend tandwiel
        hoek = d.t * 0.05
        cx, cy = x + w / 2, y + h / 2 + 3
        for i in range(8):
            a = hoek + i * math.pi / 4
            arcade.draw_circle_filled(cx + math.cos(a) * 10, cy + math.sin(a) * 10, 3, (250, 210, 80))
        arcade.draw_circle_filled(cx, cy, 9, (250, 210, 80))
        arcade.draw_circle_filled(cx, cy, 3, (150, 120, 60))
        # hoeveel blokjes erin zitten
        for i in range(BLOKJES_PER_TANDWIEL):
            arcade.draw_lrbt_rectangle_filled(x + 6 + i * 10, x + 13 + i * 10, y + 3, y + 7,
                                              (190, 140, 70) if i < d.voorraad else (70, 60, 40))
        if d.glim > 0:
            arcade.draw_text("+1", cx, y + h + 4 + (30 - d.glim) * 0.8, (250, 210, 80, d.glim * 8), 12,
                             bold=True, anchor_x="center")
    elif d.soort == "trede":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (170, 90, 60))
        for ry in range(int(y), int(y + h), 12):
            arcade.draw_line(x, ry, x + w, ry, (120, 60, 40), 1)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 4, y + h, (200, 120, 80))
    elif d.soort == "brugstuk":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 100, 55))
        for i in range(4):
            arcade.draw_line(x + i * 10, y, x + i * 10, y + h, (100, 65, 35), 1)
        arcade.draw_line(x, y + h + 10, x + w, y + h + 10, (120, 120, 130), 2)             # leuning


def teken(sp):
    t = sp._fb_t
    for b in sp._fb_blokjes:
        arcade.draw_lrbt_rectangle_filled(b["x"], b["x"] + BLOKJE, b["y"], b["y"] + BLOKJE, (190, 140, 70))
        arcade.draw_lrbt_rectangle_outline(b["x"], b["x"] + BLOKJE, b["y"], b["y"] + BLOKJE, (110, 70, 30), 1)
    # De fabriek-baas: overall, gele helm en een moersleutel
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (60, 90, 160))
    arcade.draw_lrbt_rectangle_filled(x + 8, x + w - 8, y + h * 0.3, y + h * 0.62, (70, 100, 175))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 6, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_arc_filled(cx, y + h - 6, w - 4, 20, (250, 200, 30), 0, 180)
    arcade.draw_lrbt_rectangle_filled(x + 1, x + w - 1, y + h - 7, y + h - 4, (230, 180, 20))
    sx = x + w + 2 if k > 0 else x - 2
    arcade.draw_line(sx, y + h * 0.3, sx + k * 6, y + h * 0.55, (170, 170, 180), 3)
    arcade.draw_circle_outline(sx + k * 7, y + h * 0.58, 3, (170, 170, 180), 2)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 280, x + 280, y - 10, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Tandwielen: %d" % sp._fb_tandwielen, x - 272, y + 1, (250, 210, 80), 11, bold=True)
    for i, (soort, naam) in enumerate((("mijn", "mijn"), ("band", "band"), ("trap", "trap"), ("brug", "brug"),
                                       ("tandwiel", "tandwiel"))):
        l = x - 145 + i * 84
        kan = sp._fb_tandwielen >= KOST[soort]
        arcade.draw_lrbt_rectangle_filled(l, l + 80, y, y + 18, (70, 110, 70) if kan else (60, 60, 60))
        arcade.draw_text("%d %s (%d)" % (i + 1, naam, KOST[soort]), l + 40, y + 4,
                         (255, 255, 255) if kan else (140, 140, 140), 9, anchor_x="center")
    arcade.draw_lrbt_rectangle_filled(x - 60, x + 60, y - 26, y - 10, (0, 0, 0, 155))
    arcade.draw_text("omlaag = slopen", x, y - 22, (200, 200, 200), 9, anchor_x="center")
    if sp._fb_melding_tijd > 0:
        arcade.draw_text(sp._fb_melding, x, y - 46, (250, 220, 150), 13, bold=True, anchor_x="center")

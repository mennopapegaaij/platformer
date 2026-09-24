# bommenlegger.py
# De BOMMENLEGGER: leg bommen die na 2 seconden ontploffen!
#
#  Pijltje omlaag : leg een bom (je hebt er 3; elke 3 seconden komt er een bij)
#  De ontploffing blaast monsters, spikes en stenen blokken weg (de grond niet!).
#  Sta je vlakbij? Dan word je weggeblazen: een BOMSPRONG omhoog (jij gaat er niet af).
#  Een ontploffing laat bommen in de buurt ook ontploffen (kettingreactie!).
# Alles is vast: geen toeval.

import math
import arcade
from platforms import BlokPlatform

BOMMEN_MAX = 3            # zoveel bommen kun je bij je hebben
BIJVULLEN = 180           # elke 180 stapjes (3 seconden) komt er een bom bij
LONT = 120                # na 120 stapjes (2 seconden) ontploft een bom
BEREIK = 90               # zo ver blaast een ontploffing dingen weg
DUW_OMHOOG = 14           # bomsprong: zo hard word je omhoog geblazen
DUW_OPZIJ = 7             # bomsprong: zo hard word je opzij geblazen...
DUW_DUUR = 20             # ...zolang
KETTING = 6               # een bom in de buurt van een ontploffing gaat na zoveel stapjes


def reset(sp):
    sp._bm_bommen = []        # {"x", "y", "vy", "lont"}
    sp._bm_voorraad = BOMMEN_MAX
    sp._bm_bijvul = 0
    sp._bm_nieuw = []         # ontploffingen die het spel nog moet afhandelen: (x, y)
    sp._bm_knallen = []       # ontploffingen om te tekenen: [x, y, t]
    sp._bm_duw = 0            # bomsprong: hoe lang je nog opzij wordt geblazen
    sp._bm_duw_vx = 0
    sp._bm_t = 0


def leg(sp):
    """Pijltje omlaag: leg een bom bij je voeten. Geeft True als het lukte."""
    if sp._bm_voorraad <= 0:
        return False
    sp._bm_voorraad -= 1
    sp._bm_bommen.append({"x": sp.x + sp.breedte / 2, "y": sp.y, "vy": 0.0, "lont": LONT})
    return True


def _vaste_blokken(platforms):
    return [p for p in platforms if getattr(p, "vast", True) and not getattr(p, "is_schuin", False)]


def stap(sp, platforms):
    """Elke stap: bommen vallen en tikken af, ontploffen, en je krijgt nieuwe bommen."""
    sp._bm_t += 1
    if sp._bm_voorraad < BOMMEN_MAX:
        sp._bm_bijvul += 1
        if sp._bm_bijvul >= BIJVULLEN:
            sp._bm_bijvul = 0
            sp._bm_voorraad += 1
    else:
        sp._bm_bijvul = 0
    if sp._bm_duw > 0:
        sp._bm_duw -= 1
    for k in sp._bm_knallen:
        k[2] += 1                                  # ontploffingen worden groter en vervagen
    sp._bm_knallen = [k for k in sp._bm_knallen if k[2] < 18]
    blokken = _vaste_blokken(platforms)
    ontploft = []
    for b in sp._bm_bommen:
        # Vallen tot de bom ergens op ligt
        oud_y = b["y"]
        b["vy"] -= 0.5
        b["y"] += b["vy"]
        for p in blokken:
            top = p.y + p.hoogte
            if p.x <= b["x"] <= p.x + p.breedte and b["y"] <= top <= oud_y:
                b["y"] = top
                b["vy"] = 0
        b["lont"] -= 1
        if b["lont"] <= 0:
            ontploft.append(b)
    for b in ontploft:
        if b in sp._bm_bommen:
            _ontplof(sp, b)


def _ontplof(sp, b):
    """BOEM! Onthoud de ontploffing voor het spel, blaas jou weg, en laat andere bommen meegaan."""
    sp._bm_bommen.remove(b)
    bx, by = b["x"], b["y"] + 8
    sp._bm_nieuw.append((bx, by))
    sp._bm_knallen.append([bx, by, 0])
    # Kettingreactie: bommen in de buurt gaan zo ook
    for ander in sp._bm_bommen:
        if math.hypot(ander["x"] - bx, ander["y"] - b["y"]) < BEREIK:
            ander["lont"] = min(ander["lont"], KETTING)
    # Sta jij vlakbij? Dan word je weggeblazen (bomsprong!)
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    if math.hypot(cx - bx, cy - by) < BEREIK:
        sp.snelheid_y = DUW_OMHOOG
        kant = 1 if cx >= bx else -1
        if abs(cx - bx) < 4:
            kant = 1 if sp.kijkt_rechts else -1
        sp._bm_duw_vx = DUW_OPZIJ * kant
        sp._bm_duw = DUW_DUUR


def loop(sp, L, R, snelheid):
    """Lopen; tijdens een bomsprong word je opzij geblazen."""
    kant = -1 if (L and not R) else (1 if (R and not L) else 0)
    if kant != 0:
        sp.kijkt_rechts = kant > 0
    if sp._bm_duw > 0:
        sp.snelheid_x = sp._bm_duw_vx
    else:
        sp.snelheid_x = kant * snelheid


def kan_weg(obj):
    """Kan een ontploffing dit blok opblazen? Alleen gewone stenen blokken (niet de grond)."""
    return type(obj) is BlokPlatform


def in_bereik(obj, x, y):
    """Is dit voorwerp dichtbij genoeg bij een ontploffing op (x, y)?"""
    ox = obj.x + getattr(obj, "breedte", 32) / 2
    oy = obj.y + getattr(obj, "hoogte", 32) / 2
    # Afstand tot de rand van het voorwerp (niet het midden), zodat brede dingen ook meedoen
    dx = max(0, abs(ox - x) - getattr(obj, "breedte", 32) / 2)
    dy = max(0, abs(oy - y) - getattr(obj, "hoogte", 32) / 2)
    return math.hypot(dx, dy) < BEREIK


# ===========================================================================
# Tekenen
# ===========================================================================
def teken(sp):
    t = sp._bm_t
    # Ontploffingen
    for k in sp._bm_knallen:
        r = 10 + k[2] * 5
        a = max(0, 255 - k[2] * 14)
        arcade.draw_circle_filled(k[0], k[1], min(r, BEREIK), (255, 160, 40, a // 2))
        arcade.draw_circle_filled(k[0], k[1], min(r * 0.6, BEREIK), (255, 230, 120, a))
        for i in range(8):
            h = math.radians(i * 45 + k[2] * 3)
            arcade.draw_circle_filled(k[0] + math.cos(h) * r, k[1] + math.sin(h) * r, 4, (120, 100, 90, a))
    # Bommen: zwarte bol, lontje met vonk, knippert rood vlak voor de knal
    for b in sp._bm_bommen:
        snel = 20 if b["lont"] > 60 else (8 if b["lont"] > 25 else 3)
        rood = (t // snel) % 2 == 0 and b["lont"] < LONT - 10
        arcade.draw_circle_filled(b["x"], b["y"] + 9, 9, (200, 40, 30) if rood else (40, 40, 45))
        arcade.draw_circle_filled(b["x"] - 3, b["y"] + 12, 2.5, (140, 140, 150))
        arcade.draw_line(b["x"] + 4, b["y"] + 16, b["x"] + 8, b["y"] + 22, (160, 120, 60), 2)
        if t % 4 < 2:
            arcade.draw_circle_filled(b["x"] + 8, b["y"] + 23, 3, (255, 220, 80))
    # De bommenlegger: mijnwerker met helm en lampje, en een tas vol bommen
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.62, (90, 110, 150))
    arcade.draw_line(x + 2, y + h * 0.55, x + w - 2, y + h * 0.2, (140, 90, 40), 3)     # tasriem
    tx = x + 2 if k > 0 else x + w - 12
    arcade.draw_lrbt_rectangle_filled(tx, tx + 10, y + h * 0.1, y + h * 0.3, (140, 90, 40))
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h * 0.6, y + h - 6, (240, 200, 160))
    arcade.draw_circle_filled(cx - 5 + k * 2, y + h * 0.75, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 5 + k * 2, y + h * 0.75, 2.5, (20, 20, 30))
    arcade.draw_arc_filled(cx, y + h - 6, w - 2, 20, (240, 190, 40), 0, 180)                  # helm
    arcade.draw_circle_filled(cx + k * 4, y + h + 1, 3, (255, 250, 200))                        # lampje


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 170, x + 170, y - 10, y + 22, (0, 0, 0, 150))
    arcade.draw_text("Bommen:", x - 160, y, (255, 200, 120), 12, bold=True)
    for i in range(BOMMEN_MAX):
        bx = x - 70 + i * 24
        if i < sp._bm_voorraad:
            arcade.draw_circle_filled(bx, y + 6, 8, (40, 40, 45))
            arcade.draw_line(bx + 4, y + 12, bx + 7, y + 17, (160, 120, 60), 2)
        else:
            arcade.draw_circle_outline(bx, y + 6, 8, (120, 120, 120), 1)
    if sp._bm_voorraad < BOMMEN_MAX:
        arcade.draw_lrbt_rectangle_filled(x + 10, x + 10 + 40 * sp._bm_bijvul / BIJVULLEN, y + 2, y + 10,
                                          (255, 200, 120))
        arcade.draw_lrbt_rectangle_outline(x + 10, x + 50, y + 2, y + 10, (255, 200, 120), 1)
    arcade.draw_text("omlaag = bom", x + 60, y, (220, 220, 220), 10)

# uitvinder.py
# De UITVINDER: combineer 2 onderdelen en ontdek 12 uitvindingen!
#
#  Toets 1-6 : leg een onderdeel op je werkbank (er passen er 2 op)
#               1 veer, 2 wiel, 3 ballon, 4 ventilator, 5 magneet, 6 klok
#  Omlaag     : 2 onderdelen op de werkbank? Dan BOUW je de uitvinding.
#               Anders: GEBRUIK je uitvinding (als die een knopje heeft)
#
# De uitvindingen (elke combinatie van 2 verschillende onderdelen):
#   veer + wiel          = Skateboard       : snel rijden, je houdt je vaart
#   veer + ballon        = Stuiterpak       : je stuitert vanzelf hoog
#   veer + ventilator    = Katapult         : omlaag = lanceer jezelf (3 keer)
#   veer + klok          = Vertrager        : monsters lopen heel sloom
#   wiel + ventilator    = Hovercraft       : je zweeft even door als je van een rand rijdt
#   wiel + magneet       = Schildrobot      : een robotje vangt 2 klappen op
#   wiel + klok          = Terugkeerhorloge : omlaag = terug naar waar je hem bouwde (1 keer)
#   ballon + ventilator  = Luchtschip       : springen vasthouden = omhoog vliegen (2 seconden gas)
#   ballon + magneet     = Plafondlopers    : je loopt op het plafond
#   ballon + klok        = Wekkerbom        : omlaag = leg een bom (3 bommen)
#   ventilator + magneet = Stofzuiger       : omlaag = zuig monsters voor je op (5 keer)
#   ventilator + klok    = Tijdstopwaaier   : omlaag = alle monsters 3 seconden bevroren (2 keer)
#   veer + magneet, wiel + ballon, magneet + klok = MISLUKT (alleen rook!)
# Uitvindingen zonder knopje werken 10 seconden. Alles is vast: geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

ONDERDELEN = ["veer", "wiel", "ballon", "ventilator", "magneet", "klok"]
KLEUR = {"veer": (200, 200, 210), "wiel": (60, 60, 65), "ballon": (230, 70, 90),
         "ventilator": (120, 190, 240), "magneet": (220, 50, 50), "klok": (250, 210, 70)}
UITVINDINGEN = {
    ("veer", "wiel"): "Skateboard",
    ("veer", "ballon"): "Stuiterpak",
    ("veer", "ventilator"): "Katapult",
    ("veer", "klok"): "Vertrager",
    ("wiel", "ventilator"): "Hovercraft",
    ("wiel", "magneet"): "Schildrobot",
    ("wiel", "klok"): "Terugkeerhorloge",
    ("ballon", "ventilator"): "Luchtschip",
    ("ballon", "magneet"): "Plafondlopers",
    ("ballon", "klok"): "Wekkerbom",
    ("ventilator", "magneet"): "Stofzuiger",
    ("ventilator", "klok"): "Tijdstopwaaier",
}
AANTAL_UITVINDINGEN = len(UITVINDINGEN)       # = 12
LADINGEN = {"Katapult": 3, "Schildrobot": 2, "Terugkeerhorloge": 1, "Wekkerbom": 3,
            "Stofzuiger": 5, "Tijdstopwaaier": 2}   # uitvindingen die een paar keer werken
DUUR = 600                # uitvindingen zonder ladingen werken 10 seconden
SKATE_SNEL = 2.0          # skateboard: zoveel keer sneller
SKATE_GAS = 0.25
SKATE_REM = 0.08
STUITER = 1.3             # stuiterpak: zo hoog stuiter je
KATAPULT_OMHOOG = 12
KATAPULT_VOORUIT = 9
KATAPULT_TIJD = 40
HOVER_TIJD = 60           # hovercraft: zo lang zweef je door na een rand
HOVER_SNEL = 1.3
LUCHT_DUW = 0.9
LUCHT_MAX = 3
LUCHT_GAS = 120           # luchtschip: zo lang kun je omhoog (2 seconden), daarna zweef je alleen nog
LUCHT_ZWAARTE = 0.7
BOM_LONT = 120
BOM_BEREIK = 110
ZUIG_TIJD = 35            # lang genoeg om een monster van het eind van het bereik binnen te halen
ZUIG_BEREIK = 180
ZUIG_KRACHT = 6
WAAIER_TIJD = 180


def reset(sp):
    sp._uv_bank = []          # onderdelen op de werkbank
    sp._uv_ding = None        # de uitvinding die je nu hebt
    sp._uv_tijd = 0           # hoe lang hij nog werkt (voor uitvindingen zonder ladingen)
    sp._uv_ladingen = 0
    sp._uv_ontdekt = []       # uitvindingen (en mislukkingen) die je al hebt gemaakt
    sp._uv_mislukt = []
    sp._uv_zoef = 0           # katapult: zo lang vlieg je nog vooruit
    sp._uv_hover = 0          # hovercraft: zo lang zweef je nog
    sp._uv_was_grond = True
    sp._uv_thuis = None       # terugkeerhorloge: hier ga je naartoe
    sp._uv_bommen = []        # wekkerbommen {"x", "y", "lont"}
    sp._uv_knallen = []       # ontploffingen om te tekenen {"x", "y", "t", "nieuw"}
    sp._uv_zuig = 0           # stofzuiger: zo lang zuigt hij nog
    sp._uv_gas = 0            # luchtschip: zoveel gas is er nog
    sp._uv_bevroren = 0       # tijdstopwaaier: zo lang zijn de monsters nog bevroren
    sp._uv_rook = 0
    sp._uv_t = 0
    sp._uv_melding = ""
    sp._uv_melding_tijd = 0


def _meld(sp, tekst):
    sp._uv_melding = tekst
    sp._uv_melding_tijd = 150


def heeft(sp, naam):
    return sp._uv_ding == naam


def uitvinding_van(a, b):
    """Wat maak je van deze 2 onderdelen? (None = mislukt)"""
    paar = tuple(sorted((a, b), key=ONDERDELEN.index))
    return UITVINDINGEN.get(paar)


def kies(sp, nummer):
    """Toets 1-6: een onderdeel op de werkbank (op een volle werkbank: het oudste eraf)."""
    if not 1 <= nummer <= len(ONDERDELEN):
        return False
    deel = ONDERDELEN[nummer - 1]
    if deel in sp._uv_bank:
        _meld(sp, "Dat onderdeel ligt er al: kies een ander")
        return False
    sp._uv_bank.append(deel)
    if len(sp._uv_bank) > 2:
        sp._uv_bank.pop(0)
    return True


def _stop_ding(sp):
    """De oude uitvinding is op of wordt vervangen."""
    if heeft(sp, "Plafondlopers"):
        sp.zwaartekracht_richting = 1
    sp._uv_ding = None
    sp._uv_tijd = 0
    sp._uv_ladingen = 0


def omlaag(sp):
    """Omlaag: bouwen (werkbank vol) of je uitvinding gebruiken."""
    if len(sp._uv_bank) == 2:
        return _bouw(sp)
    if len(sp._uv_bank) == 1:
        _meld(sp, "Kies nog een onderdeel (1-6)")
        return False
    return _gebruik(sp)


def _bouw(sp):
    a, b = sp._uv_bank
    sp._uv_bank = []
    naam = uitvinding_van(a, b)
    if naam is None:
        sp._uv_rook = 60
        paar = tuple(sorted((a, b), key=ONDERDELEN.index))
        if paar not in sp._uv_mislukt:
            sp._uv_mislukt.append(paar)
        _meld(sp, "MISLUKT! %s + %s geeft alleen rook..." % (a, b))
        return False
    _stop_ding(sp)
    sp._uv_ding = naam
    if naam in LADINGEN:
        sp._uv_ladingen = LADINGEN[naam]
    else:
        sp._uv_tijd = DUUR
    if naam == "Plafondlopers":
        sp.zwaartekracht_richting = -1
    if naam == "Terugkeerhorloge":
        sp._uv_thuis = (sp.x, sp.y)
    if naam == "Luchtschip":
        sp._uv_gas = LUCHT_GAS
    if naam not in sp._uv_ontdekt:
        sp._uv_ontdekt.append(naam)
        _meld(sp, "NIEUWE UITVINDING: %s!" % naam)
    else:
        _meld(sp, naam)
    return True


def _gebruik(sp):
    naam = sp._uv_ding
    if naam is None:
        _meld(sp, "Leg eerst 2 onderdelen op je werkbank (1-6)")
        return False
    if naam not in LADINGEN or naam == "Schildrobot":
        _meld(sp, "%s werkt vanzelf" % naam)
        return False
    k = 1 if sp.kijkt_rechts else -1
    if naam == "Katapult":
        sp.snelheid_y = KATAPULT_OMHOOG * sp.zwaartekracht_richting
        sp._uv_zoef = KATAPULT_TIJD
    elif naam == "Terugkeerhorloge":
        sp.x, sp.y = sp._uv_thuis
        sp.snelheid_x = sp.snelheid_y = 0
    elif naam == "Wekkerbom":
        sp._uv_bommen.append({"x": sp.x + sp.breedte / 2, "y": sp.y, "lont": BOM_LONT})
    elif naam == "Stofzuiger":
        sp._uv_zuig = ZUIG_TIJD
    elif naam == "Tijdstopwaaier":
        sp._uv_bevroren = WAAIER_TIJD
    sp._uv_ladingen -= 1
    if sp._uv_ladingen <= 0:
        naam_oud = naam
        _stop_ding(sp)
        _meld(sp, "%s is op" % naam_oud)
    return True


def bescherm(sp):
    """Schildrobot: vangt een klap op."""
    if heeft(sp, "Schildrobot") and sp._uv_ladingen > 0:
        sp._uv_ladingen -= 1
        sp.onkwetsbaar_timer = 60
        _meld(sp, "Je schildrobot ving de klap op!")
        if sp._uv_ladingen <= 0:
            _stop_ding(sp)
        return True
    return False


def loop(sp, L, R, snelheid):
    k = 1 if sp.kijkt_rechts else -1
    if sp._uv_zoef > 0:
        sp.snelheid_x = KATAPULT_VOORUIT * k        # gelanceerd: je vliegt vooruit
        return
    if heeft(sp, "Skateboard"):
        doel = (-1 if L and not R else 1 if R and not L else 0) * snelheid * SKATE_SNEL
        if doel == 0 and not sp.staat_op_grond:
            return                                  # in de lucht rol je door
        stap = SKATE_GAS if doel != 0 else SKATE_REM
        if abs(doel - sp.snelheid_x) <= stap:
            sp.snelheid_x = doel
        else:
            sp.snelheid_x += stap if doel > sp.snelheid_x else -stap
    else:
        s = snelheid * (HOVER_SNEL if heeft(sp, "Hovercraft") else 1)
        sp.snelheid_x = -s if L and not R else s if R and not L else 0
    if L and not R:
        sp.kijkt_rechts = False
    elif R and not L:
        sp.kijkt_rechts = True


def zwaartekracht(sp, richting):
    if sp._uv_hover > 0 and not sp.staat_op_grond:
        sp.snelheid_y = 0                           # hovercraft: even blijven zweven
        return
    if heeft(sp, "Luchtschip"):
        sp.snelheid_y -= ZWAARTEKRACHT * LUCHT_ZWAARTE * richting
        if getattr(sp, "vlieg_omhoog", False) and sp._uv_gas > 0 and sp.snelheid_y * richting < LUCHT_MAX:
            sp._uv_gas -= 1
            sp.snelheid_y = min(LUCHT_MAX, sp.snelheid_y * richting + LUCHT_DUW) * richting
        return
    sp.snelheid_y -= ZWAARTEKRACHT * richting


def stap(sp):
    """Elke stap: tijd aftellen, stuiteren, hovercraft, bommen."""
    sp._uv_t += 1
    for teller in ("_uv_zoef", "_uv_hover", "_uv_zuig", "_uv_bevroren", "_uv_rook", "_uv_melding_tijd"):
        if getattr(sp, teller) > 0:
            setattr(sp, teller, getattr(sp, teller) - 1)
    if sp._uv_tijd > 0:
        sp._uv_tijd -= 1
        if sp._uv_tijd == 0:
            naam = sp._uv_ding
            _stop_ding(sp)
            _meld(sp, "%s is uitgewerkt" % naam)
    if sp.staat_op_grond:
        sp._uv_zoef = 0
        sp._uv_hover = 0
        if heeft(sp, "Stuiterpak"):
            sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * STUITER * sp.zwaartekracht_richting
    elif sp._uv_was_grond and heeft(sp, "Hovercraft") and sp.snelheid_y * sp.zwaartekracht_richting <= 0:
        sp._uv_hover = HOVER_TIJD                   # van een rand gereden: even doorzweven
    sp._uv_was_grond = sp.staat_op_grond
    for b in sp._uv_bommen:
        b["lont"] -= 1
    for b in [b for b in sp._uv_bommen if b["lont"] <= 0]:
        sp._uv_bommen.remove(b)
        sp._uv_knallen.append({"x": b["x"], "y": b["y"], "t": 20, "nieuw": True})
    for k in sp._uv_knallen:
        k["t"] -= 1
    sp._uv_knallen = [k for k in sp._uv_knallen if k["t"] > 0]


def wereld(sp, vijanden):
    """Wat doen de uitvindingen met monsters? Geeft (monsters weg, spikes weg)."""
    weg, spikes = [], []
    for k in sp._uv_knallen:
        if k["nieuw"]:
            k["nieuw"] = False
            for v in vijanden:
                if (v not in weg and v not in spikes
                        and math.hypot(v.x + v.breedte / 2 - k["x"], v.y + v.hoogte / 2 - k["y"]) < BOM_BEREIK):
                    (spikes if getattr(v, "is_spike", False) else weg).append(v)
    if sp._uv_zuig > 0:
        r = 1 if sp.kijkt_rechts else -1
        cx = sp.x + sp.breedte / 2
        for v in vijanden:
            if getattr(v, "is_spike", False) or v in weg:
                continue
            d = (v.x + v.breedte / 2 - cx) * r
            if 0 < d <= ZUIG_BEREIK and abs(v.y - sp.y) < 60:
                v.x -= ZUIG_KRACHT * r                  # naar de stofzuiger toe
                if d < sp.breedte / 2 + v.breedte / 2 + ZUIG_KRACHT:
                    weg.append(v)                       # opgezogen!
    return weg, spikes


def bevroren(sp):
    return sp._uv_bevroren > 0


def monster_sloom(sp):
    """Vertrager: monsters bewegen maar 1 op de 3 stapjes."""
    return heeft(sp, "Vertrager") and sp._uv_t % 3 != 0


# ===========================================================================
# Tekenen
# ===========================================================================
def _onderdeel(deel, x, y, r=7):
    kleur = KLEUR[deel]
    if deel == "veer":
        for i in range(4):
            arcade.draw_ellipse_outline(x, y - r + 3 + i * (2 * r - 4) / 3, r * 1.6, 4, kleur, 2)
    elif deel == "wiel":
        arcade.draw_circle_filled(x, y, r, kleur)
        arcade.draw_circle_filled(x, y, r / 3, (180, 180, 190))
    elif deel == "ballon":
        arcade.draw_ellipse_filled(x, y + 1, r * 1.5, r * 1.9, kleur)
        arcade.draw_line(x, y - r, x, y - r - 4, (200, 200, 200), 1)
    elif deel == "ventilator":
        for i in range(3):
            h = i * 2.094
            arcade.draw_ellipse_filled(x + math.cos(h) * r * 0.5, y + math.sin(h) * r * 0.5, r, r * 0.5, kleur,
                                       math.degrees(h))
        arcade.draw_circle_filled(x, y, 2, (60, 60, 70))
    elif deel == "magneet":
        arcade.draw_arc_outline(x, y, r * 1.6, r * 2, kleur, 180, 360, 5)
        arcade.draw_lrbt_rectangle_filled(x - r * 0.8 - 2, x - r * 0.8 + 3, y - 1, y + r, kleur)
        arcade.draw_lrbt_rectangle_filled(x + r * 0.8 - 3, x + r * 0.8 + 2, y - 1, y + r, kleur)
    elif deel == "klok":
        arcade.draw_circle_filled(x, y, r, kleur)
        arcade.draw_line(x, y, x, y + r * 0.7, (40, 40, 40), 2)
        arcade.draw_line(x, y, x + r * 0.5, y, (40, 40, 40), 2)


def teken(sp):
    t = sp._uv_t
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    ding = sp._uv_ding
    # Bommen en knallen
    for b in sp._uv_bommen:
        arcade.draw_circle_filled(b["x"], b["y"] + 8, 8, (40, 40, 45))
        _onderdeel("klok", b["x"], b["y"] + 8, 5)
        if b["lont"] % 20 < 10:
            arcade.draw_circle_filled(b["x"] + 6, b["y"] + 17, 3, (255, 90, 40))
    for kn in sp._uv_knallen:
        r = BOM_BEREIK * (1 - kn["t"] / 20)
        arcade.draw_circle_filled(kn["x"], kn["y"] + 10, r, (255, 170, 50, kn["t"] * 10))
    # Terugkeerhorloge: een vlaggetje waar je terugkomt
    if ding == "Terugkeerhorloge" and sp._uv_thuis:
        hx, hy = sp._uv_thuis
        arcade.draw_line(hx + 16, hy, hx + 16, hy + 30, (200, 200, 200), 2)
        arcade.draw_triangle_filled(hx + 16, hy + 30, hx + 16, hy + 20, hx + 28, hy + 25, (250, 210, 70))
    # Uitvinding-plaatjes ACHTER het poppetje
    if ding == "Luchtschip":
        arcade.draw_ellipse_filled(cx, y + h + 22, 50, 26, (230, 70, 90))
        arcade.draw_line(cx - 16, y + h + 10, x + 4, y + h, (120, 90, 60), 1)
        arcade.draw_line(cx + 16, y + h + 10, x + w - 4, y + h, (120, 90, 60), 1)
        blad = 8 * abs(math.cos(t * 0.8))
        arcade.draw_line(cx - k * 26, y + h + 22 - blad, cx - k * 26, y + h + 22 + blad, (120, 190, 240), 3)
    if ding == "Katapult" or sp._uv_zoef > 0:
        arcade.draw_line(cx - k * 8, y + 6, cx - k * 16, y + h, (140, 100, 60), 3)
    # De uitvinder: bruin vest, wilde haren, bril op het voorhoofd, gereedschapsriem
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (240, 240, 235))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + 4, y + h * 0.62, (140, 90, 50))
    arcade.draw_lrbt_rectangle_filled(x + w - 9, x + w - 3, y + 4, y + h * 0.62, (140, 90, 50))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 4, y + 9, (90, 60, 40))            # riem
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 5, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    for i in range(4):
        arcade.draw_circle_filled(x + 6 + i * 7, y + h - 3, 5, (230, 140, 50))                # haren
    arcade.draw_circle_outline(cx - 5, y + h - 6, 4, (80, 180, 220), 2)                         # bril
    arcade.draw_circle_outline(cx + 5, y + h - 6, 4, (80, 180, 220), 2)
    # Uitvinding-plaatjes VOOR het poppetje
    if ding == "Skateboard":
        arcade.draw_lrbt_rectangle_filled(x - 4, x + w + 4, y - 4, y, (200, 60, 60))
        for wx in (x + 2, x + w - 2):
            arcade.draw_circle_filled(wx, y - 6, 3, (40, 40, 45))
    elif ding == "Stuiterpak":
        for wx in (x + 8, x + w - 8):
            _onderdeel("veer", wx, y + 2, 5)
    elif ding == "Hovercraft":
        arcade.draw_lrbt_rectangle_filled(x - 6, x + w + 6, y - 3, y + 3, (80, 80, 90))
        if not sp.staat_op_grond:
            for i in range(3):
                arcade.draw_line(x + 4 + i * 12, y - 4, x + 2 + i * 12, y - 12, (200, 230, 255), 2)
    elif ding == "Plafondlopers":
        for wx in (x + 8, x + w - 8):
            arcade.draw_lrbt_rectangle_filled(wx - 5, wx + 5, y + h - 2, y + h + 3, (220, 50, 50))
    elif ding == "Stofzuiger":
        arcade.draw_line(cx, y + h * 0.4, cx + k * 20, y + h * 0.3, (100, 100, 110), 4)
        if sp._uv_zuig > 0:
            for i in range(3):
                afst = 30 + ((t * 4 + i * 20) % 60)
                arcade.draw_line(cx + k * afst, y + h * 0.3 + 10, cx + k * (afst - 10), y + h * 0.3, (200, 230, 255), 2)
    elif ding == "Tijdstopwaaier":
        _onderdeel("ventilator", cx + k * 16, y + h * 0.5, 7)
    elif ding == "Schildrobot":
        for i in range(sp._uv_ladingen):
            hoek = t * 0.08 + i * math.pi
            rx, ry = cx + math.cos(hoek) * 26, y + h / 2 + math.sin(hoek) * 20
            arcade.draw_circle_filled(rx, ry, 5, (150, 160, 175))
            arcade.draw_circle_filled(rx + 1, ry + 1, 1.5, (90, 240, 200))
    elif ding == "Vertrager":
        _onderdeel("klok", cx, y + h + 12, 6)
    elif ding == "Terugkeerhorloge":
        _onderdeel("klok", cx + k * 10, y + h * 0.35, 4)
    if sp._uv_rook > 0:
        for i in range(4):
            f = (60 - sp._uv_rook) / 4
            arcade.draw_circle_filled(cx - 12 + i * 8, y + h + f + i * 3, 5 + f / 4, (90, 90, 90, sp._uv_rook * 3))


def teken_bevroren(vijanden):
    for v in vijanden:
        if not getattr(v, "is_spike", False):
            arcade.draw_lrbt_rectangle_filled(v.x - 2, v.x + v.breedte + 2, v.y, v.y + v.hoogte + 2, (160, 220, 255, 110))


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 290, x + 290, y - 30, y + 24, (0, 0, 0, 155))
    for i, deel in enumerate(ONDERDELEN):
        l = x - 282 + i * 46
        arcade.draw_lrbt_rectangle_filled(l, l + 42, y - 2, y + 22, (60, 60, 70) if deel not in sp._uv_bank else (90, 130, 90))
        _onderdeel(deel, l + 13, y + 10, 7)
        arcade.draw_text(str(i + 1), l + 34, y + 2, (255, 255, 255), 9, bold=True, anchor_x="center")
    # Werkbank
    arcade.draw_text("werkbank:", x + 8, y + 5, (230, 230, 230), 10)
    for i in range(2):
        l = x + 82 + i * 30
        arcade.draw_lrbt_rectangle_outline(l, l + 26, y, y + 22, (200, 200, 200), 1)
        if i < len(sp._uv_bank):
            _onderdeel(sp._uv_bank[i], l + 13, y + 11, 7)
    arcade.draw_text("omlaag = bouwen" if len(sp._uv_bank) == 2 else "omlaag = gebruiken", x + 148, y + 5,
                     (200, 200, 200), 9)
    # Wat je nu hebt
    if sp._uv_ding:
        extra = ("%d keer" % sp._uv_ladingen) if sp._uv_ding in LADINGEN else ("%d sec" % (sp._uv_tijd // 60 + 1))
        if sp._uv_ding == "Luchtschip":
            extra += ", gas %d%%" % (100 * sp._uv_gas // LUCHT_GAS)
        arcade.draw_text("Uitvinding: %s (%s)" % (sp._uv_ding, extra), x - 282, y - 24, (250, 220, 120), 10, bold=True)
    arcade.draw_text("Uitvindingenboek: %d / %d   mislukt: %d / 3" % (len(sp._uv_ontdekt), AANTAL_UITVINDINGEN,
                                                                    len(sp._uv_mislukt)),
                     x + 282, y - 24, (220, 220, 230), 9, anchor_x="right")
    if sp._uv_melding_tijd > 0:
        arcade.draw_text(sp._uv_melding, x, y - 50, (250, 230, 150), 13, bold=True, anchor_x="center")

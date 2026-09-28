# trein.py
# De TREINMACHINIST: leg rails, zet er een trein op en rijd mee!
#
#  Toets 1 : rails RECHTDOOR  (1 rail)   } je bouwt steeds verder vanaf het EINDE van je spoor,
#  Toets 2 : rails OMHOOG     (1 rail)   } dus ook over kuilen en de lucht in!
#  Toets 3 : rails OMLAAG     (1 rail)   } (je allereerste rails komt voor je voeten)
#  Toets 4 : LOCOMOTIEF op de rails (5), daarna elke keer een WAGON erbij (3, hoogstens 3)
#  Toets 5 : STATION bij de rails waar je op staat (4)
#  Omlaag  : het laatste stuk rails weghalen (je krijgt de rail terug)
#
# Over de rails zelf kun je NIET lopen (je valt erdoorheen): alleen de trein rijdt erover.
# De trein rijdt vanzelf heen en weer over het spoor. Spring erop en rijd mee!
# De locomotief ramt monsters van de rails. Bij een station stopt de trein 2 seconden.
# REIZIGERS: bij elk station komen reizigers wachten (elke 5 seconden 1, hoogstens 3).
#   Een wagon heeft 2 plekken. De trein brengt ze naar het volgende station,
#   en elke reiziger betaalt met een kaartje = 2 nieuwe rails.
# Alles is vast: geen toeval.

import math
import arcade
from platforms import Platform

RAILS = 30                # zoveel rails heb je aan het begin
STUK = 40                 # een stuk rails is 40 breed
HELLING = 20              # omhoog/omlaag: zoveel hoger/lager per stuk
KOST_LOC = 5
KOST_WAGON = 3
KOST_STATION = 4
MAX_WAGONS = 3
SNELHEID = 2.5
LOC_BREEDTE, LOC_HOOGTE = 60, 34
WAGON_BREEDTE, WAGON_HOOGTE = 52, 28
KOPPELING = 6             # ruimte tussen de wagons
STATION_STOP = 120        # zo lang stopt de trein bij een station (2 seconden)
EIND_STOP = 60            # aan het eind van het spoor wacht hij 1 seconde en rijdt terug
REIZIGER_TIJD = 300       # elke 5 seconden een nieuwe reiziger
MAX_WACHTEND = 3
PLEKKEN_PER_WAGON = 2
RAILS_PER_KAARTJE = 2


class TreinDeel(Platform):
    """De locomotief of een wagon: je kunt erop staan."""

    is_trein = True

    def __init__(self, x, y, breedte, hoogte, soort):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort            # "loc" of "wagon"
        self.dx = 0                   # zo ver schoof hij dit stapje (dan rijd je mee)

    def teken(self):
        pass                          # (de machinist tekent alles zelf)


def reset(sp):
    sp._tn_rails = RAILS
    sp._tn_spoor = []         # punten [(x, y), ...]: elk stuk rails loopt van het ene punt naar het volgende
    sp._tn_richting = 1       # welke kant het spoor op loopt (1 = rechts, -1 = links)
    sp._tn_trein = None       # {"d", "rijrichting", "wacht", "wagons", "reizigers", "bezocht"}
    sp._tn_wagens = []        # TreinDelen van de locomotief en de wagons
    sp._tn_stations = []      # {"i" (welk stuk), "wachtend" [bestemming...], "klok", "nr"}
    sp._tn_kaartjes = 0
    sp._tn_t = 0
    sp._tn_melding = ""
    sp._tn_melding_tijd = 0


def _meld(sp, tekst):
    sp._tn_melding = tekst
    sp._tn_melding_tijd = 120


def _vast(p):
    return (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
            and not getattr(p, "is_trein", False))


def _in_iets(x, y, platforms):
    """Zit het punt (x, y) binnenin een blok?"""
    return any(_vast(p) and p.x < x < p.x + p.breedte and p.y < y < p.y + p.hoogte for p in platforms)


# ---------------------------------------------------------------------------
# Het spoor
# ---------------------------------------------------------------------------
def aantal_stukken(sp):
    return max(0, len(sp._tn_spoor) - 1)


def hoogte_op(sp, d):
    """Waar ben je op afstand d langs het spoor? Geeft (x, y) van de bovenkant van de rails."""
    n = aantal_stukken(sp)
    d = max(0, min(n * STUK, d))
    i = min(int(d // STUK), n - 1)
    f = (d - i * STUK) / STUK
    (x1, y1), (x2, y2) = sp._tn_spoor[i], sp._tn_spoor[i + 1]
    return x1 + (x2 - x1) * f, y1 + (y2 - y1) * f


def leg(sp, soort, platforms):
    """Toets 1-3: leg een stuk rails aan het einde van het spoor."""
    if sp._tn_rails < 1:
        _meld(sp, "Geen rails meer! (vervoer reizigers voor kaartjes)")
        return False
    if not sp._tn_spoor:
        if not sp.staat_op_grond:
            _meld(sp, "Je eerste rails leg je op de grond")
            return False
        sp._tn_richting = 1 if sp.kijkt_rechts else -1
        start_x = sp.x + sp.breedte / 2 if sp._tn_richting > 0 else sp.x + sp.breedte / 2
        begin = [(start_x, sp.y)]
    else:
        begin = sp._tn_spoor
    x, y = begin[-1]
    dy = {"recht": 0, "omhoog": HELLING, "omlaag": -HELLING}[soort]
    nx, ny = x + sp._tn_richting * STUK, y + dy
    if _in_iets(nx, ny + 1, platforms) or _in_iets((x + nx) / 2, (y + ny) / 2 + 1, platforms):
        _meld(sp, "Daar zit iets in de weg")
        return False
    if not sp._tn_spoor:
        sp._tn_spoor = list(begin)
    sp._tn_spoor.append((nx, ny))
    sp._tn_rails -= 1
    return True


def haal_weg(sp):
    """Omlaag: haal het laatste stuk rails weg (niet als de trein of een station erop staat)."""
    n = aantal_stukken(sp)
    if n == 0:
        _meld(sp, "Er liggen geen rails")
        return False
    if any(st["i"] == n - 1 for st in sp._tn_stations):
        _meld(sp, "Daar staat een station")
        return False
    if sp._tn_trein is not None and _trein_bereik(sp)[1] > (n - 1) * STUK - 1:
        _meld(sp, "Daar staat de trein")
        return False
    sp._tn_spoor.pop()
    if len(sp._tn_spoor) == 1:
        sp._tn_spoor = []
    sp._tn_rails += 1
    return True


def _stuk_onder(sp):
    """Bij welk stuk rails sta je (met je voeten op de hoogte van de rails)? Geeft None als je niet bij de rails bent."""
    if not sp.staat_op_grond:
        return None
    cx = sp.x + sp.breedte / 2
    for i in range(aantal_stukken(sp)):
        (x1, y1), (x2, y2) = sp._tn_spoor[i], sp._tn_spoor[i + 1]
        if min(x1, x2) <= cx <= max(x1, x2):
            f = abs(cx - x1) / STUK
            if abs(y1 + (y2 - y1) * f - sp.y) < 12:
                return i
    return None


# ---------------------------------------------------------------------------
# De trein
# ---------------------------------------------------------------------------
def _lengtes(sp):
    t = sp._tn_trein
    return [LOC_BREEDTE] + [WAGON_BREEDTE] * t["wagons"]


def _trein_bereik(sp):
    """(achterkant, voorkant) van de hele trein, als afstand langs het spoor."""
    t = sp._tn_trein
    totaal = sum(_lengtes(sp)) + KOPPELING * t["wagons"]
    return t["d"] - totaal, t["d"]


def trein_erbij(sp):
    """Toets 4: een locomotief op de rails waar je staat, of een wagon erbij."""
    if sp._tn_trein is None:
        i = _stuk_onder(sp)
        if i is None:
            _meld(sp, "Ga bij de rails staan om de locomotief neer te zetten")
            return False
        if sp._tn_rails < KOST_LOC:
            _meld(sp, "Te weinig rails voor een locomotief (%d)" % KOST_LOC)
            return False
        sp._tn_rails -= KOST_LOC
        sp._tn_trein = {"d": min(aantal_stukken(sp) * STUK, i * STUK + LOC_BREEDTE), "rijrichting": 1,
                        "wacht": 0, "wagons": 0, "reizigers": [], "bezocht": []}
        _maak_wagens(sp)
        return True
    if sp._tn_trein["wagons"] >= MAX_WAGONS:
        _meld(sp, "De trein is al lang genoeg")
        return False
    if sp._tn_rails < KOST_WAGON:
        _meld(sp, "Te weinig rails voor een wagon (%d)" % KOST_WAGON)
        return False
    sp._tn_rails -= KOST_WAGON
    sp._tn_trein["wagons"] += 1
    _maak_wagens(sp)
    return True


def _maak_wagens(sp):
    t = sp._tn_trein
    sp._tn_wagens = [TreinDeel(0, 0, LOC_BREEDTE, LOC_HOOGTE, "loc")]
    sp._tn_wagens += [TreinDeel(0, 0, WAGON_BREEDTE, WAGON_HOOGTE, "wagon") for _ in range(t["wagons"])]
    _zet_wagens(sp)
    for w in sp._tn_wagens:
        w.dx = 0


def _zet_wagens(sp):
    """Zet de locomotief en de wagons op hun plek langs het spoor."""
    t = sp._tn_trein
    d = t["d"]
    for w, lengte in zip(sp._tn_wagens, _lengtes(sp)):
        midden = d - lengte / 2
        x, y = hoogte_op(sp, midden)
        oud = w.x
        w.x = x - lengte / 2
        w.y = y + 3                               # (op de wieltjes)
        w.dx = w.x - oud
        d -= lengte + KOPPELING


def station_erbij(sp):
    """Toets 5: een station bij het stuk rails waar je op staat."""
    i = _stuk_onder(sp)
    if i is None:
        _meld(sp, "Ga bij de rails staan om een station te bouwen")
        return False
    if any(abs(st["i"] - i) < 3 for st in sp._tn_stations):
        _meld(sp, "Te dicht bij een ander station")
        return False
    if sp._tn_rails < KOST_STATION:
        _meld(sp, "Te weinig rails voor een station (%d)" % KOST_STATION)
        return False
    sp._tn_rails -= KOST_STATION
    sp._tn_stations.append({"i": i, "wachtend": 0, "klok": 0})
    sp._tn_stations.sort(key=lambda st: st["i"])
    return True


def _station_d(st):
    return st["i"] * STUK + STUK / 2


def wereld(sp, vijanden):
    """Elke stap: de trein rijdt, stopt bij stations en ramt monsters. Geeft de monsters die weg moeten."""
    sp._tn_t += 1
    if sp._tn_melding_tijd > 0:
        sp._tn_melding_tijd -= 1
    for st in sp._tn_stations:
        st["klok"] += 1
        if st["klok"] >= REIZIGER_TIJD:
            st["klok"] = 0
            if st["wachtend"] < MAX_WACHTEND:
                st["wachtend"] += 1
    t = sp._tn_trein
    if t is None:
        return []
    n = aantal_stukken(sp)
    achter, voor = _trein_bereik(sp)
    if t["wacht"] > 0:
        t["wacht"] -= 1
        for w in sp._tn_wagens:
            w.dx = 0
    else:
        # Rijden, maar niet van de rails af
        stap = SNELHEID * t["rijrichting"]
        if voor + stap > n * STUK:
            stap = n * STUK - voor
        if achter + stap < 0:
            stap = -achter
        t["d"] += stap
        _zet_wagens(sp)
        achter, voor = _trein_bereik(sp)
        # Aan het eind van het spoor: even wachten en dan terug
        if (t["rijrichting"] > 0 and voor >= n * STUK - 0.01) or (t["rijrichting"] < 0 and achter <= 0.01):
            t["rijrichting"] *= -1
            t["wacht"] = EIND_STOP
            t["bezocht"] = []                    # terugweg: alle stations weer aandoen
        # Staat er een station naast de trein (net als een perron)? Stoppen, reizigers eruit en erin
        for st in sp._tn_stations:
            if achter <= _station_d(st) <= voor and st not in t["bezocht"]:
                t["bezocht"].append(st)
                t["wacht"] = STATION_STOP
                _bij_station(sp, t, st)
                break
    # De locomotief ramt monsters
    loc = sp._tn_wagens[0]
    weg = [v for v in vijanden if not getattr(v, "is_spike", False)
           and v.x < loc.x + loc.breedte and v.x + v.breedte > loc.x
           and v.y < loc.y + loc.hoogte and v.y + v.hoogte > loc.y]
    return weg


def _bij_station(sp, t, st):
    """Reizigers stappen uit (en betalen) en in."""
    uit = [r for r in t["reizigers"] if r is not st]
    if uit:
        t["reizigers"] = [r for r in t["reizigers"] if r is st]
        sp._tn_kaartjes += len(uit)
        sp._tn_rails += len(uit) * RAILS_PER_KAARTJE
        _meld(sp, "%d reiziger(s) uitgestapt: +%d rails!" % (len(uit), len(uit) * RAILS_PER_KAARTJE))
    plek = t["wagons"] * PLEKKEN_PER_WAGON - len(t["reizigers"])
    instappen = min(plek, st["wachtend"])
    st["wachtend"] -= instappen
    t["reizigers"] += [st] * instappen           # (ze onthouden waar ze instapten)


def platforms_van(sp):
    """Alles van de trein waar je op kunt staan (de wagons, niet de rails)."""
    return list(sp._tn_wagens)


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_mensje(x, y, kleur):
    arcade.draw_lrbt_rectangle_filled(x - 4, x + 4, y, y + 9, kleur)
    arcade.draw_circle_filled(x, y + 12, 3.5, (240, 205, 170))


def teken(sp):
    t_nu = sp._tn_t
    # Stations (achter de rails)
    for nr, st in enumerate(sp._tn_stations):
        x, y = hoogte_op(sp, _station_d(st))
        arcade.draw_lrbt_rectangle_filled(x - 30, x + 30, y, y + 40, (200, 170, 130, 230))
        arcade.draw_triangle_filled(x - 36, y + 40, x + 36, y + 40, x, y + 58, (120, 60, 50))
        arcade.draw_lrbt_rectangle_filled(x - 18, x + 18, y + 26, y + 36, (250, 250, 250))
        arcade.draw_text("Station %d" % (nr + 1), x, y + 27, (40, 40, 40), 7, anchor_x="center", bold=True)
        for i in range(st["wachtend"]):
            _teken_mensje(x - 20 + i * 12, y + 2, (90, 130, 200))
    # Rails: dwarsliggers en twee staven
    for i in range(aantal_stukken(sp)):
        (x1, y1), (x2, y2) = sp._tn_spoor[i], sp._tn_spoor[i + 1]
        for j in range(4):
            f = (j + 0.5) / 4
            xm, ym = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
            arcade.draw_lrbt_rectangle_filled(xm - 3, xm + 3, ym - 6, ym - 1, (120, 80, 45))
        arcade.draw_line(x1, y1, x2, y2, (170, 170, 180), 3)
        arcade.draw_line(x1, y1 - 4, x2, y2 - 4, (120, 120, 130), 1)
        # steunpaaltjes als de rails in de lucht hangen
        arcade.draw_line(x1, y1 - 6, x1, y1 - 26, (110, 80, 50, 120), 2)
    # De trein
    t = sp._tn_trein
    if t is not None:
        reizigers = len(t["reizigers"])
        for nr, w in enumerate(sp._tn_wagens):
            x, y, b, h = w.x, w.y, w.breedte, w.hoogte
            draai = t_nu * SNELHEID / 6 * t["rijrichting"] if t["wacht"] == 0 else 0
            for wx in (x + 10, x + b - 10):
                arcade.draw_circle_filled(wx, y + 2, 6, (40, 40, 45))
                arcade.draw_line(wx, y + 2, wx + math.cos(draai) * 5, y + 2 + math.sin(draai) * 5, (200, 200, 210), 2)
            if w.soort == "loc":
                voor_rechts = sp._tn_richting > 0
                cab_x = x if voor_rechts else x + b - 22
                arcade.draw_lrbt_rectangle_filled(x, x + b, y + 6, y + 22, (200, 40, 40))        # ketel
                arcade.draw_lrbt_rectangle_filled(cab_x, cab_x + 22, y + 6, y + h, (160, 30, 30))  # cabine
                arcade.draw_lrbt_rectangle_filled(cab_x + 5, cab_x + 17, y + 22, y + h - 4, (200, 230, 255))
                sx = x + b - 14 if voor_rechts else x + 8
                arcade.draw_lrbt_rectangle_filled(sx, sx + 6, y + 22, y + 32, (50, 50, 55))        # schoorsteen
                if t["wacht"] == 0:
                    for i in range(3):
                        f = (t_nu // 5 + i * 4) % 12
                        arcade.draw_circle_filled(sx + 3 - t["rijrichting"] * f * 2, y + 34 + f * 2, 3 + f / 3,
                                                  (220, 220, 220, 200 - f * 15))
            else:
                arcade.draw_lrbt_rectangle_filled(x, x + b, y + 6, y + h, (60, 140, 80))
                for i in range(PLEKKEN_PER_WAGON):
                    rx = x + 8 + i * 22
                    arcade.draw_lrbt_rectangle_filled(rx, rx + 16, y + 14, y + h - 4, (200, 230, 255))
                    zit = (nr - 1) * PLEKKEN_PER_WAGON + i
                    if zit < reizigers:
                        _teken_mensje(rx + 8, y + 12, (90, 130, 200))
    # De machinist: blauwe pet, overall met streepjes
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (50, 70, 130))
    for i in range(4):
        arcade.draw_line(x + 6 + i * 6, y, x + 6 + i * 6, y + h * 0.62, (240, 240, 250), 1)
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 6, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h - 7, y + h, (50, 70, 130))
    arcade.draw_lrbt_rectangle_filled(min(cx, cx + k * 16), max(cx, cx + k * 16), y + h - 7, y + h - 4, (40, 55, 110))
    arcade.draw_circle_filled(x + w - 6 if k < 0 else x + 6, y + h * 0.45, 3, (250, 60, 60))   # zakdoek


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 280, x + 280, y - 30, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Rails: %d" % sp._tn_rails, x - 272, y + 1, (220, 220, 230), 11, bold=True)
    arcade.draw_text("Kaartjes: %d" % sp._tn_kaartjes, x - 272, y - 24, (250, 210, 80), 10, bold=True)
    t = sp._tn_trein
    if t is not None:
        arcade.draw_text("Reizigers in de trein: %d / %d" % (len(t["reizigers"]), t["wagons"] * PLEKKEN_PER_WAGON),
                         x - 170, y - 24, (180, 210, 255), 10)
    loc_tekst = "wagon (3)" if t is not None else "loc (5)"
    for i, tekst in enumerate(("recht", "omhoog", "omlaag", loc_tekst, "station (4)")):
        l = x - 170 + i * 88
        arcade.draw_lrbt_rectangle_filled(l, l + 84, y, y + 18, (70, 90, 120))
        arcade.draw_text("%d %s" % (i + 1, tekst), l + 42, y + 4, (255, 255, 255), 9, anchor_x="center")
    arcade.draw_text("omlaag = rail weg", x + 272, y - 24, (200, 200, 200), 9, anchor_x="right")
    if sp._tn_melding_tijd > 0:
        arcade.draw_text(sp._tn_melding, x, y - 50, (230, 230, 255), 13, bold=True, anchor_x="center")

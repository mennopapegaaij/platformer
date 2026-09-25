# robotbouwer.py
# De ROBOTBOUWER: bouw je eigen robot uit onderdelen!
#
# Je robot heeft 3 plekken. Op elke plek kies je 1 onderdeel (of niks):
#   BENEN : 1 = wielen  (snel rijden, je houdt je vaart)
#           2 = veer    (hoger springen, en je stuitert na een hoge val)
#   RUG   : 3 = raket   (springen vasthouden in de lucht = omhoog vliegen)
#           4 = schild  (houdt een klap tegen)
#   ARM   : 5 = grijparm (pijltje omlaag = grijp een rand en trek je erheen)
#           6 = laser    (pijltje omlaag = laserstraal: monsters en spikes weg)
# Nog eens op dezelfde toets = onderdeel eraf. Bouwen kan alleen op de grond.
# Raket, schild, grijparm en laser gebruiken stroom uit je batterij.
# De batterij laadt op als je op de grond staat.
#
# GEHEIME COMBO'S (twee onderdelen die samen iets extra's doen):
#   veer + raket     = Kanonsprong  : enorm hoge sprong vanaf de grond
#   wielen + schild  = Stormram     : met volle vaart ram je monsters weg
#   raket + grijparm = Raketgrijper : de grijparm reikt veel verder en is gratis
#   raket + laser    = Luchtlaser   : in de lucht kost de laser geen stroom
# 3 plekken met elk 3 keuzes = 27 verschillende robots. Alles is vast: geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

ONDERDELEN = {1: ("benen", "wielen"), 2: ("benen", "veer"), 3: ("rug", "raket"),
              4: ("rug", "schild"), 5: ("arm", "grijparm"), 6: ("arm", "laser")}
COMBOS = [("veer", "raket", "Kanonsprong"), ("wielen", "schild", "Stormram"),
          ("raket", "grijparm", "Raketgrijper"), ("raket", "laser", "Luchtlaser")]

BATTERIJ = 100            # zo vol is je batterij
OPLADEN = 0.6             # zoveel stroom komt erbij per stapje op de grond
WIEL_SNEL = 1.7           # wielen: zoveel keer sneller
WIEL_GAS = 0.3            # wielen: zo snel trek je op
WIEL_REM = 0.15           # wielen: zo snel rol je uit
VEER_SPRONG = 1.45        # veer: zoveel keer hoger springen
VEER_STUITER = 0.55       # veer: zoveel van je valsnelheid stuitert terug
VEER_MIN = 8              # veer: pas stuiteren na een val van minstens deze snelheid
KANON = 1.9               # kanonsprong: zoveel keer hoger
RAKET_DUW = 0.95          # raket: zo hard duwt hij omhoog
RAKET_MAX = 7             # raket: sneller dan dit omhoog gaat niet
RAKET_KOST = 2.2          # raket: stroom per stapje (volle batterij = bijna 1 seconde vliegen)
SCHILD_KOST = 35          # schild: stroom per klap
GRIJP_BEREIK = 220        # grijparm: zo ver reikt hij
GRIJP_KOST = 15
ZIP_SNELHEID = 12         # zo snel trekt de grijparm je
LASER_BEREIK = 450
LASER_KOST = 25
STORMRAM_VAART = 5.5      # stormram: zo snel moet je rijden


def reset(sp):
    sp._rb_delen = {"benen": None, "rug": None, "arm": None}
    sp._rb_batterij = BATTERIJ
    sp._rb_zip = None         # grijparm: (doel_x, doel_y) waar hij je heen trekt
    sp._rb_haak = None        # waar de grijparm vastzit (om te tekenen)
    sp._rb_straal = None      # laserstraal (x1, y, x2, tijd)
    sp._rb_raket_aan = False  # vlam van de raket (om te tekenen)
    sp._rb_valsnelheid = 0
    sp._rb_t = 0
    sp._rb_melding = ""
    sp._rb_melding_tijd = 0


def heeft(sp, deel):
    return deel in sp._rb_delen.values()


def combos(sp):
    """Welke geheime combo's werken nu?"""
    return [naam for a, b, naam in COMBOS if heeft(sp, a) and heeft(sp, b)]


def combo(sp, naam):
    return naam in combos(sp)


def robotnaam(sp):
    delen = [d for d in (sp._rb_delen["benen"], sp._rb_delen["rug"], sp._rb_delen["arm"]) if d]
    if not delen:
        return "Kale robot"
    return "-".join(d.capitalize() for d in delen) + "-bot"


def _meld(sp, tekst):
    sp._rb_melding = tekst
    sp._rb_melding_tijd = 120


def _gebruik(sp, kost):
    """Stroom gebruiken. Geeft False als de batterij te leeg is."""
    if sp._rb_batterij < kost:
        _meld(sp, "Batterij te leeg!")
        return False
    sp._rb_batterij -= kost
    return True


def kies(sp, nummer):
    """Toets 1-6: zet een onderdeel op je robot (of haal het eraf)."""
    if nummer not in ONDERDELEN:
        return False
    if not sp.staat_op_grond:
        _meld(sp, "Bouwen kan alleen op de grond")
        return False
    plek, deel = ONDERDELEN[nummer]
    oude_combos = combos(sp)
    sp._rb_delen[plek] = None if sp._rb_delen[plek] == deel else deel
    nieuw = [c for c in combos(sp) if c not in oude_combos]
    _meld(sp, "COMBO: " + nieuw[0] + "!" if nieuw else robotnaam(sp))
    return True


def loop(sp, L, R, snelheid):
    """Rijden of lopen."""
    if heeft(sp, "wielen"):
        doel = (-1 if L and not R else 1 if R and not L else 0) * snelheid * WIEL_SNEL
        if doel == 0 and not sp.staat_op_grond:
            return                           # in de lucht rol je gewoon door
        stap = WIEL_GAS if doel != 0 else WIEL_REM
        if not sp.staat_op_grond:
            stap *= 0.4                      # in de lucht kun je maar een beetje bijsturen
        if abs(doel - sp.snelheid_x) <= stap:
            sp.snelheid_x = doel
        else:
            sp.snelheid_x += stap if doel > sp.snelheid_x else -stap
    else:
        sp.snelheid_x = -snelheid if L and not R else snelheid if R and not L else 0
    if L and not R:
        sp.kijkt_rechts = False
    elif R and not L:
        sp.kijkt_rechts = True


def zwaartekracht(sp, richting):
    sp.snelheid_y -= ZWAARTEKRACHT * richting
    sp._rb_raket_aan = False
    # Raket: springen vasthouden in de lucht = omhoog
    if (heeft(sp, "raket") and getattr(sp, "vlieg_omhoog", False) and not sp.staat_op_grond
            and sp.snelheid_y < RAKET_MAX and sp._rb_batterij >= RAKET_KOST):
        sp._rb_batterij -= RAKET_KOST
        sp.snelheid_y = min(RAKET_MAX, sp.snelheid_y + RAKET_DUW * richting)
        sp._rb_raket_aan = True


def spring(sp):
    if not sp.staat_op_grond:
        return
    kracht = SPRING_KRACHT + sp.sprong_bonus
    if combo(sp, "Kanonsprong"):
        kracht *= KANON
    elif heeft(sp, "veer"):
        kracht *= VEER_SPRONG
    sp.snelheid_y = kracht * sp.zwaartekracht_richting


def bescherm(sp):
    """Schild: houdt een klap tegen (kost stroom)."""
    if heeft(sp, "schild") and _gebruik(sp, SCHILD_KOST):
        sp.onkwetsbaar_timer = 45
        _meld(sp, "Schild!")
        return True
    return False


def _vast(p):
    return (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
            and not getattr(p, "is_echo", False))


def _vrij(sp, x, y, platforms):
    for p in platforms:
        if (_vast(p) and x < p.x + p.breedte and x + sp.breedte > p.x
                and y < p.y + p.hoogte and y + sp.hoogte > p.y):
            return False
    return True


def _lijn_vrij(x1, y1, x2, y2, platforms, behalve):
    """Zit er niks in de weg op de lijn van (x1, y1) naar (x2, y2)?"""
    afstand = math.hypot(x2 - x1, y2 - y1)
    n = max(1, int(afstand / 6))
    for i in range(1, n):
        x = x1 + (x2 - x1) * i / n
        y = y1 + (y2 - y1) * i / n
        for p in platforms:
            if (p is not behalve and _vast(p) and p.x < x < p.x + p.breedte
                    and p.y < y < p.y + p.hoogte):
                return False
    return True


def grijp_doel(sp, platforms):
    """Zoek de dichtstbijzijnde rand vooruit waar de grijparm je heen kan trekken."""
    k = 1 if sp.kijkt_rechts else -1
    bereik = GRIJP_BEREIK * (1.6 if combo(sp, "Raketgrijper") else 1)
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    beste, beste_afstand = None, None
    for p in platforms:
        if not _vast(p) or (sp.staat_op_grond and p is sp._gelande_platform):
            continue
        top = p.y + p.hoogte
        if top < sp.y - 5:
            continue                                  # alleen randen omhoog (of even hoog)
        # Je landt op de rand die naar je toe wijst
        doel_x = p.x + 2 if k > 0 else p.x + p.breedte - sp.breedte - 2
        haak_x = p.x if k > 0 else p.x + p.breedte
        if (haak_x - cx) * k < 0:
            continue                                  # die rand ligt achter je
        afstand = math.hypot(haak_x - cx, top - cy)
        if afstand > bereik or (beste_afstand is not None and afstand >= beste_afstand):
            continue
        if not _vrij(sp, doel_x, top, platforms) or not _lijn_vrij(cx, cy, haak_x, top, platforms, p):
            continue
        beste, beste_afstand = (doel_x, top, haak_x), afstand
    return beste


def actie(sp, platforms):
    """Pijltje omlaag: de arm doet zijn ding. Geeft 'laser', 'grijp' of None."""
    arm = sp._rb_delen["arm"]
    if arm == "grijparm" and sp._rb_zip is None:
        doel = grijp_doel(sp, platforms)
        if doel is None:
            _meld(sp, "Geen rand om te grijpen")
            return None
        if not combo(sp, "Raketgrijper") and not _gebruik(sp, GRIJP_KOST):
            return None
        sp._rb_zip = (doel[0], doel[1])
        sp._rb_haak = (doel[2], doel[1])
        return "grijp"
    if arm == "laser":
        gratis = combo(sp, "Luchtlaser") and not sp.staat_op_grond
        if not gratis and not _gebruik(sp, LASER_KOST):
            return None
        return "laser"
    return None


def zip_stap(sp):
    """De grijparm trekt je naar de rand (in een rechte lijn)."""
    dx, dy = sp._rb_zip[0] - sp.x, sp._rb_zip[1] - sp.y
    afstand = math.hypot(dx, dy)
    if afstand <= ZIP_SNELHEID:
        sp.x, sp.y = sp._rb_zip
        sp.snelheid_x, sp.snelheid_y = 0, 0
        sp._rb_zip = None
        sp._rb_haak = None
    else:
        sp.x += dx / afstand * ZIP_SNELHEID
        sp.y += dy / afstand * ZIP_SNELHEID
        sp.snelheid_y = 0
    _tijd(sp)


def laser(sp, vijanden, platforms):
    """Schiet de laserstraal. Geeft het monster of de spike die geraakt is (of None)."""
    k = 1 if sp.kijkt_rechts else -1
    x = sp.x + sp.breedte if k > 0 else sp.x
    y = sp.y + sp.hoogte * 0.55
    geraakt = None
    eind = x + k * LASER_BEREIK
    for i in range(1, LASER_BEREIK // 4 + 1):
        lx = x + k * i * 4
        muur = any(_vast(p) and p.x <= lx <= p.x + p.breedte and p.y <= y <= p.y + p.hoogte
                   for p in platforms)
        if muur:
            eind = lx
            break
        doel = next((v for v in vijanden if v.x <= lx <= v.x + v.breedte
                     and v.y - 4 <= y <= v.y + v.hoogte + 4), None)
        if doel is not None:
            geraakt, eind = doel, lx
            break
    sp._rb_straal = (x, y, eind, 10)
    return geraakt


def stormram(sp, v):
    """Stormram: rij je met volle vaart tegen een monster, dan vliegt het weg."""
    return (combo(sp, "Stormram") and abs(sp.snelheid_x) >= STORMRAM_VAART
            and not getattr(v, "is_spike", False) and v.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte))


def stap(sp, platforms):
    """Elke stap: batterij opladen, veer-stuiter, laserstraal."""
    if sp.staat_op_grond:
        # Veer: na een hoge val stuiter je terug
        if heeft(sp, "veer") and sp._rb_valsnelheid >= VEER_MIN:
            sp.snelheid_y = sp._rb_valsnelheid * VEER_STUITER * sp.zwaartekracht_richting
        sp._rb_valsnelheid = 0
        sp._rb_batterij = min(BATTERIJ, sp._rb_batterij + OPLADEN)
    else:
        sp._rb_valsnelheid = max(0, -sp.snelheid_y * sp.zwaartekracht_richting)
    _tijd(sp)


def _tijd(sp):
    sp._rb_t += 1
    if sp._rb_straal is not None:
        x1, y, x2, t = sp._rb_straal
        sp._rb_straal = (x1, y, x2, t - 1) if t > 1 else None
    if sp._rb_melding_tijd > 0:
        sp._rb_melding_tijd -= 1


# ===========================================================================
# Tekenen
# ===========================================================================
def teken(sp):
    t = sp._rb_t
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    delen = sp._rb_delen
    # Laserstraal
    if sp._rb_straal is not None:
        x1, ly, x2, lt = sp._rb_straal
        arcade.draw_line(x1, ly, x2, ly, (255, 60, 60, 60 + lt * 19), 7)
        arcade.draw_line(x1, ly, x2, ly, (255, 230, 230), 2)
    # Grijparm-kabel
    if sp._rb_haak is not None:
        hx, hy = sp._rb_haak
        arcade.draw_line(cx, y + h * 0.55, hx, hy, (180, 180, 190), 2)
        arcade.draw_circle_filled(hx, hy, 4, (220, 180, 60))
    # Raket op de rug (met vlam als hij aan staat)
    rx = x - 6 if k > 0 else x + w
    if delen["rug"] == "raket":
        arcade.draw_lrbt_rectangle_filled(rx, rx + 6, y + 8, y + h - 6, (200, 60, 60))
        arcade.draw_triangle_filled(rx, y + h - 6, rx + 6, y + h - 6, rx + 3, y + h, (230, 230, 240))
        if sp._rb_raket_aan:
            lang = 10 + (t % 4) * 3
            arcade.draw_triangle_filled(rx, y + 8, rx + 6, y + 8, rx + 3, y + 8 - lang, (255, 170, 40))
            arcade.draw_triangle_filled(rx + 1, y + 8, rx + 5, y + 8, rx + 3, y + 8 - lang * 0.6, (255, 240, 120))
    # Benen: wielen, veer of gewone pootjes
    if delen["benen"] == "wielen":
        hoek = sp.x * 0.15
        for wx in (x + 7, x + w - 7):
            arcade.draw_circle_filled(wx, y + 6, 6, (40, 40, 45))
            arcade.draw_line(wx - math.cos(hoek) * 5, y + 6 - math.sin(hoek) * 5,
                             wx + math.cos(hoek) * 5, y + 6 + math.sin(hoek) * 5, (160, 160, 170), 2)
    elif delen["benen"] == "veer":
        for i in range(4):
            arcade.draw_ellipse_outline(cx, y + 2 + i * 3, 16, 4, (200, 200, 210), 2)
    else:
        arcade.draw_lrbt_rectangle_filled(x + 7, x + 11, y, y + 10, (120, 120, 130))
        arcade.draw_lrbt_rectangle_filled(x + w - 11, x + w - 7, y, y + 10, (120, 120, 130))
    # Lijf en hoofd met een scherm-gezicht
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 10, y + h * 0.62, (150, 160, 175))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.62, y + h - 2, (170, 180, 195))
    arcade.draw_lrbt_rectangle_filled(x + 7, x + w - 7, y + h * 0.66, y + h - 5, (30, 50, 60))
    arcade.draw_lrbt_rectangle_filled(cx - 6 + k * 2, cx - 3 + k * 2, y + h * 0.74, y + h * 0.84, (90, 240, 200))
    arcade.draw_lrbt_rectangle_filled(cx + 3 + k * 2, cx + 6 + k * 2, y + h * 0.74, y + h * 0.84, (90, 240, 200))
    arcade.draw_line(cx, y + h - 2, cx, y + h + 6, (120, 120, 130), 2)          # antenne
    arcade.draw_circle_filled(cx, y + h + 7, 2.5, (255, 80, 80) if t % 40 < 20 else (120, 40, 40))
    # Batterij-lampjes op de buik
    for i in range(4):
        aan = sp._rb_batterij > i * 25
        arcade.draw_lrbt_rectangle_filled(x + 7 + i * 5, x + 10 + i * 5, y + 14, y + 17,
                                          (90, 240, 120) if aan else (60, 60, 60))
    # Arm: grijparm of laser
    ax = x + w if k > 0 else x
    if delen["arm"] == "grijparm":
        arcade.draw_line(ax, y + h * 0.45, ax + k * 8, y + h * 0.5, (120, 120, 130), 3)
        arcade.draw_line(ax + k * 8, y + h * 0.5, ax + k * 13, y + h * 0.6, (220, 180, 60), 2)
        arcade.draw_line(ax + k * 8, y + h * 0.5, ax + k * 13, y + h * 0.4, (220, 180, 60), 2)
    elif delen["arm"] == "laser":
        arcade.draw_lrbt_rectangle_filled(min(ax, ax + k * 12), max(ax, ax + k * 12), y + h * 0.5, y + h * 0.6,
                                          (80, 80, 90))
        arcade.draw_circle_filled(ax + k * 12, y + h * 0.55, 2.5, (255, 80, 80))
    # Schild-bel
    if delen["rug"] == "schild" and sp._rb_batterij >= SCHILD_KOST:
        arcade.draw_ellipse_outline(cx, y + h / 2, w + 16, h + 18, (120, 200, 255, 150), 2)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 270, x + 270, y - 26, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Stroom:", x - 262, y + 2, (120, 240, 150), 11, bold=True)
    arcade.draw_lrbt_rectangle_filled(x - 200, x - 200 + 90 * sp._rb_batterij / BATTERIJ, y + 3, y + 15,
                                      (90, 240, 120))
    arcade.draw_lrbt_rectangle_outline(x - 200, x - 110, y + 3, y + 15, (200, 240, 210), 1)
    # De 6 onderdelen, oplichtend als ze erop zitten
    for nr, (plek, deel) in ONDERDELEN.items():
        l = x - 100 + (nr - 1) * 62
        aan = sp._rb_delen[plek] == deel
        arcade.draw_lrbt_rectangle_filled(l, l + 58, y, y + 18, (70, 140, 90) if aan else (50, 50, 55))
        arcade.draw_text("%d %s" % (nr, deel), l + 29, y + 4, (255, 255, 255) if aan else (150, 150, 150), 9,
                         anchor_x="center", bold=aan)
    naam = robotnaam(sp)
    c = combos(sp)
    if c:
        naam += "   COMBO: " + ", ".join(c)
    arcade.draw_text(naam, x, y - 20, (220, 230, 240), 10, anchor_x="center")
    if sp._rb_melding_tijd > 0:
        arcade.draw_text(sp._rb_melding, x, y - 44, (150, 255, 200), 13, bold=True, anchor_x="center")

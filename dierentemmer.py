# dierentemmer.py
# De DIERENTEMMER: spring op een monster en het wordt je vriendje!
#
#  Op een monster springen : het monster is getemd en loopt achter je aan (max 3 dieren)
#                            (tem je een 4e, dan gaat het oudste dier terug de natuur in)
#  Pijltje omlaag          : al je dieren doen hun kunstje (daarna even rusten)
#
# Elk soort monster heeft een eigen kunstje (zie DIEREN hieronder).
# Sommige kunstjes werken vanzelf (zoals hoger springen), andere doe je met omlaag.
# Grote bazen en stekelmonsters laten zich niet temmen. Alles is vast: geen toeval.

import math
import arcade

# Soort monster -> (naam van het kunstje, uitleg, "actief" (omlaag) of "vanzelf")
DIEREN = {
    "Vijand":            ("Beuker", "rent vooruit en beukt een monster weg", "actief"),
    "VliegendVijand":    ("Vlieger", "tilt je omhoog, ook in de lucht", "actief"),
    "KraaiVijand":       ("Vlieger", "tilt je omhoog, ook in de lucht", "actief"),
    "VleermuisVijand":   ("Vlieger", "tilt je omhoog, ook in de lucht", "actief"),
    "SpringendVijand":   ("Springer", "je springt hoger", "vanzelf"),
    "PaddenstoelVijand": ("Springer", "je springt hoger", "vanzelf"),
    "GroteVijand":       ("Lijfwacht", "houdt een klap voor je tegen", "vanzelf"),
    "RobotVijand":       ("Lijfwacht", "houdt een klap voor je tegen", "vanzelf"),
    "GeestVijand":       ("Spookje", "2 seconden onkwetsbaar", "actief"),
    "JagerVijand":       ("Speurneus", "je rent sneller", "vanzelf"),
    "Achtervolger":      ("Speurneus", "je rent sneller", "vanzelf"),
    "SlijmVijand":       ("Slijmspuger", "plakt een monster 4 seconden vast", "actief"),
    "VuurVijand":        ("Vuurspuwer", "spuugt een vuurbal", "actief"),
    "IJsVijand":         ("IJsadem", "bevriest monsters dichtbij", "actief"),
    "BomVijand":         ("Ontploffer", "ontploft: alles in de buurt weg (1 keer)", "actief"),
    "SlangVijand":       ("Zwiep", "zwiept je een stuk vooruit", "actief"),
}
MAX_DIEREN = 3
AFSTAND = 22              # zoveel stapjes loopt elk dier achter het vorige aan
RUST = 180                # na een kunstje moet een dier 3 seconden rusten
SPRINGER_BONUS = 0.25     # per springer: zoveel hoger springen
SPEUR_BONUS = 0.3         # per speurneus: zoveel sneller rennen
BEUK_BEREIK = 300
SLIJM_BEREIK = 260
SLIJM_TIJD = 240
IJS_BEREIK = 200
IJS_TIJD = 180
BOEM_BEREIK = 130
VLIEG_KRACHT = 11
SPOOK_TIJD = 120
ZWIEP = 150


def kan_temmen(v):
    return type(v).__name__ in DIEREN and not getattr(v, "is_spike", False)


def kunstje(dier):
    return DIEREN[type(dier["monster"]).__name__][0]


def reset(sp):
    sp._dm_dieren = []        # {"monster", "rust"}
    sp._dm_spoor = []         # jouw pad, zodat de dieren je volgen
    sp._dm_t = 0
    sp._dm_flitsen = []       # effecten om te tekenen {"soort", "x", "y", "x2", "t"}
    sp._dm_melding = ""
    sp._dm_melding_tijd = 0
    sp._dm_gezien = []        # kunstjes die je al hebt ontdekt


def _meld(sp, tekst):
    sp._dm_melding = tekst
    sp._dm_melding_tijd = 120


def tem(sp, v):
    """Je sprong op een monster: het is nu jouw dier!"""
    if len(sp._dm_dieren) >= MAX_DIEREN:
        sp._dm_dieren.pop(0)                       # het oudste dier gaat terug de natuur in
    sp._dm_dieren.append({"monster": v, "rust": 0})
    naam, uitleg, _ = DIEREN[type(v).__name__]
    if naam not in sp._dm_gezien:
        sp._dm_gezien.append(naam)
        _meld(sp, "Nieuw dier: " + naam + "! (" + uitleg + ")")
    else:
        _meld(sp, "Getemd: " + naam)


def aantal(sp, naam):
    return sum(1 for d in sp._dm_dieren if kunstje(d) == naam)


def loop_snelheid(sp, snelheid):
    return snelheid * (1 + SPEUR_BONUS * aantal(sp, "Speurneus"))


def sprong_factor(sp):
    return 1 + SPRINGER_BONUS * aantal(sp, "Springer")


def bescherm(sp):
    """Een lijfwacht houdt de klap tegen (en gaat dan terug de natuur in)."""
    for d in sp._dm_dieren:
        if kunstje(d) == "Lijfwacht":
            sp._dm_dieren.remove(d)
            sp.onkwetsbaar_timer = 60
            _meld(sp, "Je lijfwacht beschermde je!")
            return True
    return False


def _vrij(sp, x, platforms):
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and x < p.x + p.breedte and x + sp.breedte > p.x
                and sp.y < p.y + p.hoogte and sp.y + sp.hoogte > p.y):
            return False
    return True


def _voor_je(sp, vijanden, bereik):
    """Het dichtstbijzijnde monster vóór je (ongeveer op jouw hoogte)."""
    k = 1 if sp.kijkt_rechts else -1
    cx = sp.x + sp.breedte / 2
    beste = None
    for v in vijanden:
        if getattr(v, "is_spike", False):
            continue
        d = (v.x + v.breedte / 2 - cx) * k
        if 0 < d <= bereik and abs(v.y - sp.y) < 80 and (beste is None or d < beste[0]):
            beste = (d, v)
    return beste[1] if beste else None


def doe_kunstjes(sp, vijanden, platforms):
    """Pijltje omlaag: elk uitgerust dier doet zijn kunstje.
    Geeft (monsters weg, spikes weg, vuurballen [(x, y, richting)])."""
    weg, spikes_weg, vuur = [], [], []
    k = 1 if sp.kijkt_rechts else -1
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    gedaan = False
    for d in list(sp._dm_dieren):
        naam, _, soort = DIEREN[type(d["monster"]).__name__]
        if soort != "actief" or d["rust"] > 0:
            continue
        m = d["monster"]
        mx, my = m.x + m.breedte / 2, m.y + m.hoogte / 2
        gedaan = True
        d["rust"] = RUST
        if naam == "Beuker":
            v = _voor_je(sp, [v for v in vijanden if v not in weg], BEUK_BEREIK)
            eind = v.x + v.breedte / 2 if v else cx + k * BEUK_BEREIK
            if v:
                weg.append(v)
            sp._dm_flitsen.append({"soort": "beuk", "x": mx, "y": my, "x2": eind, "t": 15})
        elif naam == "Vlieger":
            sp.snelheid_y = VLIEG_KRACHT * sp.zwaartekracht_richting
            sp._dm_flitsen.append({"soort": "veer", "x": cx, "y": sp.y, "x2": cx, "t": 15})
        elif naam == "Spookje":
            sp.onkwetsbaar_timer = max(sp.onkwetsbaar_timer, SPOOK_TIJD)
        elif naam == "Slijmspuger":
            v = _voor_je(sp, vijanden, SLIJM_BEREIK)
            eind = v.x + v.breedte / 2 if v else cx + k * SLIJM_BEREIK
            if v:
                v._dm_vast = SLIJM_TIJD
            sp._dm_flitsen.append({"soort": "slijm", "x": mx, "y": my, "x2": eind, "t": 15})
        elif naam == "Vuurspuwer":
            vuur.append((cx + k * (sp.breedte / 2 + 4), cy, k))
        elif naam == "IJsadem":
            for v in vijanden:
                if (not getattr(v, "is_spike", False)
                        and math.hypot(v.x + v.breedte / 2 - cx, v.y + v.hoogte / 2 - cy) < IJS_BEREIK):
                    v._dm_vast = IJS_TIJD
            sp._dm_flitsen.append({"soort": "ijs", "x": cx, "y": cy, "x2": cx, "t": 20})
        elif naam == "Ontploffer":
            for v in vijanden:
                if v not in weg and math.hypot(v.x + v.breedte / 2 - mx, v.y + v.hoogte / 2 - my) < BOEM_BEREIK:
                    (spikes_weg if getattr(v, "is_spike", False) else weg).append(v)
            sp._dm_dieren.remove(d)                       # de ontploffer is op
            sp._dm_flitsen.append({"soort": "boem", "x": mx, "y": my, "x2": mx, "t": 20})
        elif naam == "Zwiep":
            # In stapjes van 10 vooruit, en stoppen zodra er een muur in de weg zit
            verder = 0
            while verder < ZWIEP and _vrij(sp, sp.x + k * (verder + 10), platforms):
                verder += 10
            sp.x += k * verder
    if not gedaan:
        _meld(sp, "Je dieren rusten nog even" if sp._dm_dieren else "Tem eerst een monster (spring erop)")
    return weg, spikes_weg, vuur


def stap(sp):
    """Elke stap: de dieren volgen je pad, rusten uit, effecten verdwijnen."""
    sp._dm_t += 1
    sp._dm_spoor.append((sp.x + sp.breedte / 2, sp.y, sp.kijkt_rechts))
    if len(sp._dm_spoor) > AFSTAND * (MAX_DIEREN + 1):
        sp._dm_spoor.pop(0)
    # Het nieuwste dier loopt vlak achter je, het oudste achteraan
    for i, d in enumerate(reversed(sp._dm_dieren)):
        plek = max(0, len(sp._dm_spoor) - 1 - AFSTAND * (i + 1))
        x, y, r = sp._dm_spoor[plek]
        m = d["monster"]
        m.x = x - m.breedte / 2
        m.y = y
        if d["rust"] > 0:
            d["rust"] -= 1
    for f in sp._dm_flitsen:
        f["t"] -= 1
    sp._dm_flitsen = [f for f in sp._dm_flitsen if f["t"] > 0]
    if sp._dm_melding_tijd > 0:
        sp._dm_melding_tijd -= 1


def vast(v):
    """Zit dit monster vast (slijm of ijs)?"""
    return getattr(v, "_dm_vast", 0) > 0


def tik_vast(vijanden):
    for v in vijanden:
        if getattr(v, "_dm_vast", 0) > 0:
            v._dm_vast -= 1


# ===========================================================================
# Tekenen
# ===========================================================================
def teken_vast(vijanden):
    for v in vijanden:
        if vast(v):
            arcade.draw_lrbt_rectangle_filled(v.x - 2, v.x + v.breedte + 2, v.y, v.y + v.hoogte + 2,
                                              (150, 220, 255, 110))


def teken(sp):
    t = sp._dm_t
    # De dieren (in hun eigen monster-uiterlijk, met een halsband)
    for d in sp._dm_dieren:
        m = d["monster"]
        m.teken()
        arcade.draw_lrbt_rectangle_filled(m.x + 2, m.x + m.breedte - 2, m.y + m.hoogte * 0.55,
                                          m.y + m.hoogte * 0.55 + 4, (230, 50, 90))
        arcade.draw_circle_filled(m.x + m.breedte / 2, m.y + m.hoogte * 0.55, 3, (250, 210, 60))
        if d["rust"] > 0:
            arcade.draw_text("z", m.x + m.breedte, m.y + m.hoogte + 2 + (t // 10) % 6, (220, 220, 255), 10)
    # Effecten
    for f in sp._dm_flitsen:
        if f["soort"] == "beuk":
            arcade.draw_line(f["x"], f["y"], f["x2"], f["y"], (255, 255, 255, f["t"] * 15), 4)
        elif f["soort"] == "slijm":
            arcade.draw_line(f["x"], f["y"], f["x2"], f["y"], (120, 220, 80, f["t"] * 15), 6)
            arcade.draw_circle_filled(f["x2"], f["y"], 8, (120, 220, 80, f["t"] * 15))
        elif f["soort"] == "ijs":
            r = IJS_BEREIK * (1 - f["t"] / 20)
            arcade.draw_circle_outline(f["x"], f["y"], r, (170, 230, 255), 3)
        elif f["soort"] == "boem":
            r = BOEM_BEREIK * (1 - f["t"] / 20)
            arcade.draw_circle_filled(f["x"], f["y"], r, (255, 170, 50, f["t"] * 10))
        elif f["soort"] == "veer":
            for i in range(3):
                arcade.draw_line(f["x"] - 10 + i * 10, f["y"] - 4, f["x"] - 14 + i * 10, f["y"] - 16,
                                 (255, 255, 255, f["t"] * 15), 2)
    # De temmer: safari-hoed, groene blouse en een zweep
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.3, (110, 80, 50))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + h * 0.3, y + h * 0.62, (110, 140, 70))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 5, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30))
    arcade.draw_ellipse_filled(cx, y + h - 4, w + 8, 6, (200, 180, 120))
    arcade.draw_arc_filled(cx, y + h - 3, w - 6, 16, (220, 200, 140), 0, 180)
    zx = x + w if k > 0 else x
    zwaai = math.sin(t * 0.15) * 6
    arcade.draw_line(zx, y + h * 0.45, zx + k * 10, y + h * 0.6 + zwaai, (90, 60, 30), 2)
    arcade.draw_line(zx + k * 10, y + h * 0.6 + zwaai, zx + k * 16, y + h * 0.3 - zwaai, (90, 60, 30), 1)


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 270, x + 270, y - 10, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Dieren:", x - 262, y + 1, (250, 210, 120), 11, bold=True)
    for i in range(MAX_DIEREN):
        l = x - 195 + i * 118
        if i < len(sp._dm_dieren):
            d = sp._dm_dieren[i]
            naam, _, soort = DIEREN[type(d["monster"]).__name__]
            klaar = soort == "vanzelf" or d["rust"] == 0
            arcade.draw_lrbt_rectangle_filled(l, l + 112, y, y + 18, (70, 120, 70) if klaar else (70, 70, 80))
            if soort == "actief" and d["rust"] > 0:
                arcade.draw_lrbt_rectangle_filled(l, l + 112 * (1 - d["rust"] / RUST), y, y + 3, (250, 210, 120))
            arcade.draw_text(naam, l + 56, y + 4, (255, 255, 255), 9, bold=True, anchor_x="center")
        else:
            arcade.draw_lrbt_rectangle_outline(l, l + 112, y, y + 18, (110, 110, 110), 1)
            arcade.draw_text("leeg", l + 56, y + 4, (130, 130, 130), 9, anchor_x="center")
    arcade.draw_text("omlaag = kunstjes", x + 160, y + 1, (200, 200, 200), 9)
    if sp._dm_melding_tijd > 0:
        arcade.draw_text(sp._dm_melding, x, y - 24, (250, 220, 150), 13, bold=True, anchor_x="center")

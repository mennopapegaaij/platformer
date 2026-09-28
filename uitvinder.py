# uitvinder.py
# De UITVINDER: combineer onderdelen en ontdek 100 uitvindingen!
#
#  Toets 1-8 : leg een onderdeel op je werkbank (er passen er 3 op)
#               1 veer, 2 wiel, 3 ballon, 4 ventilator, 5 magneet, 6 klok, 7 lamp, 8 raket
#  Omlaag     : ligt er iets op de werkbank? Dan BOUW je de uitvinding.
#               Anders: GEBRUIK je uitvinding (als die een knopje heeft)
#
# Zo kom je aan 100 uitvindingen:
#   1 onderdeel                 =  8 kleine uitvindingen    (bv. veer = Springveren)
#   2 dezelfde onderdelen       =  8 dubbele uitvindingen   (bv. veer + veer = Dubbele Springveren)
#   2 verschillende onderdelen  = 28 uitvindingen           (bv. veer + wiel = Skateboard)
#   3 verschillende onderdelen  = 56 combi-uitvindingen     (alle 3 de uitvindingen van de paartjes tegelijk!)
#   Iets anders (bv. 3 dezelfde) = MISLUKT: alleen rook.
# Uitvindingen zonder knopje werken 10 seconden; met knopje werken ze een paar keer.
# Alles is vast: geen toeval.

import math
from itertools import combinations
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT
from platforms import Platform

ONDERDELEN = ["veer", "wiel", "ballon", "ventilator", "magneet", "klok", "lamp", "raket"]
KLEUR = {"veer": (200, 200, 210), "wiel": (60, 60, 65), "ballon": (230, 70, 90),
         "ventilator": (120, 190, 240), "magneet": (220, 50, 50), "klok": (250, 210, 70),
         "lamp": (255, 250, 170), "raket": (240, 140, 50)}
# 1 onderdeel (en 2 dezelfde = dubbel zo sterk)
KLEIN = {"veer": "Springveren", "wiel": "Rolschaatsen", "ballon": "Zweefballon", "ventilator": "Windsprong",
         "magneet": "Monstermagneet", "klok": "Slowmotion", "lamp": "Flitslicht", "raket": "Raketsprong"}
# 2 verschillende onderdelen
UITVINDINGEN = {
    ("veer", "wiel"): "Skateboard",
    ("veer", "ballon"): "Stuiterpak",
    ("veer", "ventilator"): "Katapult",
    ("veer", "magneet"): "Terugveer",
    ("veer", "klok"): "Vertrager",
    ("veer", "lamp"): "Lichttrap",
    ("veer", "raket"): "Raketlaarzen",
    ("wiel", "ballon"): "Ballonfiets",
    ("wiel", "ventilator"): "Hovercraft",
    ("wiel", "magneet"): "Schildrobot",
    ("wiel", "klok"): "Terugkeerhorloge",
    ("wiel", "lamp"): "Koplampauto",
    ("wiel", "raket"): "Raketauto",
    ("ballon", "ventilator"): "Luchtschip",
    ("ballon", "magneet"): "Plafondlopers",
    ("ballon", "klok"): "Wekkerbom",
    ("ballon", "lamp"): "Lampion",
    ("ballon", "raket"): "Maanlander",
    ("ventilator", "magneet"): "Stofzuiger",
    ("ventilator", "klok"): "Tijdstopwaaier",
    ("ventilator", "lamp"): "Discobal",
    ("ventilator", "raket"): "Zweefvlieger",
    ("magneet", "klok"): "Magneetklok",
    ("magneet", "lamp"): "Lichtzwaard",
    ("magneet", "raket"): "Grijpraket",
    ("klok", "lamp"): "Stroboscoop",
    ("klok", "raket"): "Aftelraket",
    ("lamp", "raket"): "Vuurpijl",
}
# Uitvindingen met ladingen (werken een paar keer); ACTIE = gebruiken met omlaag
LADINGEN = {"Katapult": 3, "Schildrobot": 2, "Terugkeerhorloge": 1, "Wekkerbom": 3, "Stofzuiger": 5,
            "Tijdstopwaaier": 2, "Monstermagneet": 1, "Flitslicht": 2, "Raketsprong": 2, "Terugveer": 1,
            "Lichttrap": 3, "Lichtzwaard": 3, "Vuurpijl": 5, "Raketlaarzen": 3, "Grijpraket": 2, "Aftelraket": 2}
ACTIE = {"Katapult", "Terugkeerhorloge", "Wekkerbom", "Stofzuiger", "Tijdstopwaaier", "Monstermagneet",
         "Flitslicht", "Raketsprong", "Lichttrap", "Vuurpijl", "Raketlaarzen", "Grijpraket", "Aftelraket"}
KLEIN_LADING_PER_NIVEAU = {"Monstermagneet": 1, "Flitslicht": 2, "Raketsprong": 2}

DUUR = 600                # uitvindingen zonder ladingen werken 10 seconden
SKATE_SNEL = 2.0
SKATE_GAS = 0.25
SKATE_REM = 0.08
STUITER = 1.3
KATAPULT_OMHOOG = 12
KATAPULT_VOORUIT = 9
KATAPULT_TIJD = 40
HOVER_TIJD = 60
LUCHT_DUW = 0.9
LUCHT_MAX = 3
LUCHT_GAS = 120
BOM_LONT = 120
BOM_BEREIK = 110
ZUIG_TIJD = 35
ZUIG_BEREIK = 180
ZUIG_KRACHT = 6
WAAIER_TIJD = 180
FLITS_BEREIK = 150
FLITS_TIJD = 120
MAGNEET_BEREIK = 150
MAGNEETKLOK_TIJD = 120
MAGNEETKLOK_BEREIK = 200
LICHTBLOK_TIJD = 240
KOPLAMP_BEREIK = 120
DISCO_BEREIK = 200
AFTEL_TIJD = 60


class LichtBlok(Platform):
    """Een blok van licht (lichttrap): je kunt erop staan, maar het verdwijnt na 4 seconden."""

    is_uvlicht = True

    def __init__(self, x, y):
        super().__init__(x, y, 40, 10)
        self.tijd = LICHTBLOK_TIJD

    def teken(self):
        a = min(255, self.tijd * 3)
        arcade.draw_lrbt_rectangle_filled(self.x, self.x + self.breedte, self.y, self.y + self.hoogte, (255, 250, 170, a))
        arcade.draw_lrbt_rectangle_outline(self.x, self.x + self.breedte, self.y, self.y + self.hoogte, (255, 255, 255, a), 1)


# ---------------------------------------------------------------------------
# Het uitvindingenboek: alle 100 recepten
# ---------------------------------------------------------------------------
def _sorteer(delen):
    return tuple(sorted(delen, key=ONDERDELEN.index))


def recept(delen):
    """Wat maak je van deze onderdelen? Geeft (naam, [(effect, niveau), ...]) of None (mislukt)."""
    d = _sorteer(delen)
    if len(d) == 1:
        return KLEIN[d[0]], [(KLEIN[d[0]], 1)]
    if len(d) == 2 and d[0] == d[1]:
        return "Dubbele " + KLEIN[d[0]], [(KLEIN[d[0]], 2)]
    if len(d) == 2:
        return UITVINDINGEN[d], [(UITVINDINGEN[d], 1)]
    if len(d) == 3 and len(set(d)) == 3:
        paren = [UITVINDINGEN[p] for p in combinations(d, 2)]
        return "Combi: " + " + ".join(paren), [(p, 1) for p in paren]
    return None


def alle_recepten():
    uit = []
    for n in (1, 2, 3):
        for d in combinations(ONDERDELEN, n):
            uit.append(d)
    uit += [(p, p) for p in ONDERDELEN]
    return uit


AANTAL_UITVINDINGEN = len(alle_recepten())    # = 100


# ---------------------------------------------------------------------------
def reset(sp):
    sp._uv_bank = []          # onderdelen op de werkbank
    sp._uv_naam = None        # naam van de uitvinding die je nu hebt
    sp._uv_actief = {}        # effect -> {"tijd": ..., "lad": ...}
    sp._uv_niveau = {}        # effect -> 1 of 2 (dubbel)
    sp._uv_ontdekt = []       # namen van ontdekte uitvindingen
    sp._uv_zoef = 0
    sp._uv_hover = 0
    sp._uv_was_grond = True
    sp._uv_thuis = None
    sp._uv_laatst = None      # terugveer: laatste plek op de grond
    sp._uv_bommen = []
    sp._uv_knallen = []
    sp._uv_zuig = 0
    sp._uv_bevroren = 0
    sp._uv_gas = 0
    sp._uv_luchtsprongen = 0
    sp._uv_aftel = 0
    sp._uv_lichtblokken = []
    sp._uv_actie_nu = []      # acties die over monsters gaan (het spel voert ze uit)
    sp._uv_magneetklok = 0
    sp._uv_rook = 0
    sp._uv_t = 0
    sp._uv_melding = ""
    sp._uv_melding_tijd = 0


def _meld(sp, tekst):
    sp._uv_melding = tekst
    sp._uv_melding_tijd = 150


def heeft(sp, naam):
    return naam in sp._uv_actief


def niveau(sp, naam):
    return sp._uv_niveau.get(naam, 0) if naam in sp._uv_actief else 0


def kies(sp, nummer):
    """Toets 1-8: een onderdeel op de werkbank (op een volle werkbank gaat het oudste eraf)."""
    if not 1 <= nummer <= len(ONDERDELEN):
        return False
    sp._uv_bank.append(ONDERDELEN[nummer - 1])
    if len(sp._uv_bank) > 3:
        sp._uv_bank.pop(0)
    return True


def _stop_alles(sp):
    if heeft(sp, "Plafondlopers"):
        sp.zwaartekracht_richting = 1
    sp._uv_actief = {}
    sp._uv_niveau = {}
    sp._uv_naam = None


def _stop(sp, effect):
    """Eén effect is op (de rest van een combi-uitvinding werkt nog)."""
    if effect == "Plafondlopers":
        sp.zwaartekracht_richting = 1
    sp._uv_actief.pop(effect, None)
    if not sp._uv_actief:
        _meld(sp, "%s is op" % sp._uv_naam)
        sp._uv_naam = None


def omlaag(sp, platforms):
    """Omlaag: bouwen (als er iets op de werkbank ligt) of je uitvinding gebruiken."""
    if sp._uv_bank:
        return _bouw(sp)
    return _gebruik(sp, platforms)


def _bouw(sp):
    delen = sp._uv_bank
    sp._uv_bank = []
    r = recept(delen)
    if r is None:
        sp._uv_rook = 60
        _meld(sp, "MISLUKT! %s geeft alleen rook..." % " + ".join(delen))
        return False
    naam, effecten = r
    _stop_alles(sp)
    sp._uv_naam = naam
    for effect, nv in effecten:
        lad = LADINGEN.get(effect)
        if effect in KLEIN_LADING_PER_NIVEAU:
            lad = KLEIN_LADING_PER_NIVEAU[effect] * nv
        sp._uv_actief[effect] = {"tijd": None if lad else DUUR, "lad": lad}
        sp._uv_niveau[effect] = nv
        if effect == "Plafondlopers":
            sp.zwaartekracht_richting = -1
        if effect == "Terugkeerhorloge":
            sp._uv_thuis = (sp.x, sp.y)
        if effect == "Luchtschip":
            sp._uv_gas = LUCHT_GAS
        if effect == "Windsprong":
            sp._uv_luchtsprongen = nv                 # meteen klaar, ook als je direct springt
    if naam not in sp._uv_ontdekt:
        sp._uv_ontdekt.append(naam)
        _meld(sp, "NIEUW (%d/%d): %s!" % (len(sp._uv_ontdekt), AANTAL_UITVINDINGEN, naam))
    else:
        _meld(sp, naam)
    return True


def _lading_op(sp, effect):
    sp._uv_actief[effect]["lad"] -= 1
    if sp._uv_actief[effect]["lad"] <= 0:
        _stop(sp, effect)


def _gebruik(sp, platforms):
    acties = [e for e in sp._uv_actief if e in ACTIE]
    if not sp._uv_actief:
        _meld(sp, "Leg eerst onderdelen op je werkbank (1-8)")
        return False
    if not acties:
        _meld(sp, "%s werkt vanzelf" % sp._uv_naam)
        return False
    k = 1 if sp.kijkt_rechts else -1
    r = sp.zwaartekracht_richting
    for e in acties:
        if e == "Katapult":
            sp.snelheid_y = KATAPULT_OMHOOG * r
            sp._uv_zoef = KATAPULT_TIJD
        elif e == "Terugkeerhorloge":
            sp.x, sp.y = sp._uv_thuis
            sp.snelheid_x = sp.snelheid_y = 0
        elif e == "Wekkerbom":
            sp._uv_bommen.append({"x": sp.x + sp.breedte / 2, "y": sp.y, "lont": BOM_LONT})
        elif e == "Stofzuiger":
            sp._uv_zuig = ZUIG_TIJD
        elif e == "Tijdstopwaaier":
            sp._uv_bevroren = WAAIER_TIJD
        elif e == "Raketsprong":
            sp.snelheid_y = 15 * r
        elif e == "Raketlaarzen":
            sp.snelheid_y = 13 * r
        elif e == "Aftelraket":
            sp._uv_aftel = AFTEL_TIJD
        elif e == "Lichttrap":
            sp._uv_lichtblokken.append(LichtBlok(sp.x + sp.breedte / 2 - 20, sp.y - 10 if r > 0 else sp.y + sp.hoogte))
        elif e == "Grijpraket":
            doel = _grijp_doel(sp, platforms)
            if doel is None:
                _meld(sp, "Geen rand om naartoe te raketten")
                continue
            sp.x, sp.y = doel
            sp.snelheid_x = sp.snelheid_y = 0
        elif e in ("Monstermagneet", "Flitslicht", "Vuurpijl"):
            sp._uv_actie_nu.append(e)                 # (het spel doet dit, want het gaat om monsters)
        _lading_op(sp, e)
    return True


def _grijp_doel(sp, platforms):
    """De dichtstbijzijnde bovenkant van een blok vooruit en omhoog (binnen 250)."""
    k = 1 if sp.kijkt_rechts else -1
    cx = sp.x + sp.breedte / 2
    beste = None
    for p in platforms:
        if not getattr(p, "vast", True) or getattr(p, "is_schuin", False) or p is sp._gelande_platform:
            continue
        top = p.y + p.hoogte
        rand = p.x if k > 0 else p.x + p.breedte
        if top <= sp.y + 5 or (rand - cx) * k < -20:
            continue
        afstand = math.hypot(rand - cx, top - sp.y)
        if afstand > 250:
            continue
        doel_x = p.x + 2 if k > 0 else p.x + p.breedte - sp.breedte - 2
        vrij = not any(getattr(q, "vast", True) and doel_x < q.x + q.breedte and doel_x + sp.breedte > q.x
                       and top < q.y + q.hoogte and top + sp.hoogte > q.y for q in platforms)
        if vrij and (beste is None or afstand < beste[0]):
            beste = (afstand, (doel_x, top))
    return beste[1] if beste else None


def bescherm(sp):
    """Schildrobot: vangt een klap op."""
    if heeft(sp, "Schildrobot"):
        sp.onkwetsbaar_timer = 60
        _meld(sp, "Je schildrobot ving de klap op!")
        _lading_op(sp, "Schildrobot")
        return True
    return False


# ---------------------------------------------------------------------------
# Bewegen
# ---------------------------------------------------------------------------
def _snelheidsfactor(sp, L, R):
    f = 1 + 0.4 * niveau(sp, "Rolschaatsen")
    if heeft(sp, "Hovercraft"):
        f *= 1.3
    if heeft(sp, "Koplampauto"):
        f *= 1.6
    if heeft(sp, "Raketauto"):
        f *= 2.5
    if heeft(sp, "Zweefvlieger") and not sp.staat_op_grond and (L or R):
        f *= 1.5
    return f


def loop(sp, L, R, snelheid):
    k = 1 if sp.kijkt_rechts else -1
    if sp._uv_zoef > 0:
        sp.snelheid_x = KATAPULT_VOORUIT * k
        return
    s = snelheid * _snelheidsfactor(sp, L, R)
    if heeft(sp, "Skateboard"):
        doel = (-1 if L and not R else 1 if R and not L else 0) * s * SKATE_SNEL
        if doel == 0 and not sp.staat_op_grond:
            return
        stap = SKATE_GAS if doel != 0 else SKATE_REM
        if abs(doel - sp.snelheid_x) <= stap:
            sp.snelheid_x = doel
        else:
            sp.snelheid_x += stap if doel > sp.snelheid_x else -stap
    else:
        sp.snelheid_x = -s if L and not R else s if R and not L else 0
    if L and not R:
        sp.kijkt_rechts = False
    elif R and not L:
        sp.kijkt_rechts = True


def zwaartekracht(sp, richting):
    L, R = sp.links_ingedrukt, sp.rechts_ingedrukt
    if sp._uv_hover > 0 and not sp.staat_op_grond:
        sp.snelheid_y = 0
        return
    if heeft(sp, "Ballonfiets") and not sp.staat_op_grond and (L or R) and sp.snelheid_y * richting <= 0:
        sp.snelheid_y = 0                                # rijdend in de lucht blijf je op hoogte
        return
    zwaarte = 1.0
    if heeft(sp, "Luchtschip"):
        zwaarte *= 0.7
    if heeft(sp, "Maanlander"):
        zwaarte *= 0.4
    sp.snelheid_y -= ZWAARTEKRACHT * zwaarte * richting
    if (heeft(sp, "Luchtschip") and getattr(sp, "vlieg_omhoog", False) and sp._uv_gas > 0
            and sp.snelheid_y * richting < LUCHT_MAX):
        sp._uv_gas -= 1
        sp.snelheid_y = min(LUCHT_MAX, sp.snelheid_y * richting + LUCHT_DUW) * richting
    # Langzaam vallen: de zachtste valsnelheid telt
    max_val = None
    if heeft(sp, "Zweefballon"):
        max_val = 4 / niveau(sp, "Zweefballon")
    if heeft(sp, "Lampion"):
        max_val = min(max_val or 99, 1.5)
    if heeft(sp, "Zweefvlieger") and (L or R):
        max_val = min(max_val or 99, 1.0)
    if max_val is not None and sp.snelheid_y * richting < -max_val:
        sp.snelheid_y = -max_val * richting


def spring(sp):
    """Springen: springveren = hoger; windsprong = extra sprongen in de lucht."""
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * (1 + 0.3 * niveau(sp, "Springveren")) * sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp.snelheid_y = kracht
    elif sp._uv_luchtsprongen > 0:
        sp._uv_luchtsprongen -= 1
        sp.snelheid_y = kracht * 0.9


def stap(sp):
    """Elke stap: tijd aftellen, stuiteren, hovercraft, terugveer, aftelraket, bommen, lichtblokken."""
    sp._uv_t += 1
    for teller in ("_uv_zoef", "_uv_hover", "_uv_zuig", "_uv_bevroren", "_uv_rook", "_uv_melding_tijd"):
        if getattr(sp, teller) > 0:
            setattr(sp, teller, getattr(sp, teller) - 1)
    for e, w in list(sp._uv_actief.items()):
        if w["tijd"] is not None:
            w["tijd"] -= 1
            if w["tijd"] <= 0:
                _stop(sp, e)
    r = sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp._uv_zoef = 0
        sp._uv_hover = 0
        sp._uv_luchtsprongen = niveau(sp, "Windsprong")
        sp._uv_laatst = (sp.x, sp.y)
        if heeft(sp, "Stuiterpak"):
            sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * STUITER * r
    elif sp._uv_was_grond and heeft(sp, "Hovercraft") and sp.snelheid_y * r <= 0:
        sp._uv_hover = HOVER_TIJD
    sp._uv_was_grond = sp.staat_op_grond
    # Terugveer: in een kuil gevallen? Terug naar de laatste plek op de grond
    if heeft(sp, "Terugveer") and sp.y < -20 and sp._uv_laatst is not None:
        sp.x, sp.y = sp._uv_laatst
        sp.y += 40
        sp.snelheid_y = 0
        _meld(sp, "Boing! De terugveer redde je")
        _lading_op(sp, "Terugveer")
    # Aftelraket: 3, 2, 1... LANCERING!
    if sp._uv_aftel > 0:
        sp._uv_aftel -= 1
        if sp._uv_aftel == 0:
            sp.snelheid_y = 20 * r
    for b in sp._uv_bommen:
        b["lont"] -= 1
    for b in [b for b in sp._uv_bommen if b["lont"] <= 0]:
        sp._uv_bommen.remove(b)
        sp._uv_knallen.append({"x": b["x"], "y": b["y"], "t": 20, "nieuw": True})
    for k in sp._uv_knallen:
        k["t"] -= 1
    sp._uv_knallen = [k for k in sp._uv_knallen if k["t"] > 0]
    for lb in sp._uv_lichtblokken:
        lb.tijd -= 1
    sp._uv_lichtblokken = [lb for lb in sp._uv_lichtblokken if lb.tijd > 0]


def platforms_van(sp):
    return list(sp._uv_lichtblokken)


# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------
def _dichtste(sp, vijanden, bereik, weg):
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    kandidaten = [(math.hypot(v.x + v.breedte / 2 - cx, v.y + v.hoogte / 2 - cy), v.x, v) for v in vijanden
                  if not getattr(v, "is_spike", False) and v not in weg]
    kandidaten = [k for k in kandidaten if k[0] <= bereik]
    return min(kandidaten, key=lambda k: (k[0], k[1]))[2] if kandidaten else None


def wereld(sp, vijanden):
    """Wat doen de uitvindingen met monsters? Geeft (monsters weg, spikes weg, kogels [(x, y, richting)])."""
    weg, spikes, kogels = [], [], []
    k = 1 if sp.kijkt_rechts else -1
    cx = sp.x + sp.breedte / 2
    # Bommen
    for kn in sp._uv_knallen:
        if kn["nieuw"]:
            kn["nieuw"] = False
            for v in vijanden:
                if (v not in weg and v not in spikes
                        and math.hypot(v.x + v.breedte / 2 - kn["x"], v.y + v.hoogte / 2 - kn["y"]) < BOM_BEREIK):
                    (spikes if getattr(v, "is_spike", False) else weg).append(v)
    # Stofzuiger
    if sp._uv_zuig > 0:
        for v in vijanden:
            if getattr(v, "is_spike", False) or v in weg:
                continue
            d = (v.x + v.breedte / 2 - cx) * k
            if 0 < d <= ZUIG_BEREIK and abs(v.y - sp.y) < 60:
                v.x -= ZUIG_KRACHT * k
                if d < sp.breedte / 2 + v.breedte / 2 + ZUIG_KRACHT:
                    weg.append(v)
    # Acties met omlaag die over monsters gaan
    for actie in sp._uv_actie_nu:
        if actie == "Monstermagneet":
            v = _dichtste(sp, vijanden, MAGNEET_BEREIK, weg)
            if v is not None:
                weg.append(v)
        elif actie == "Flitslicht":
            for v in vijanden:
                if (not getattr(v, "is_spike", False)
                        and math.hypot(v.x + v.breedte / 2 - cx, v.y - sp.y) <= FLITS_BEREIK):
                    v._uv_flits = FLITS_TIJD
        elif actie == "Vuurpijl":
            kogels.append((sp.x + sp.breedte + 4 if k > 0 else sp.x - 4, sp.y + sp.hoogte / 2, k))
    sp._uv_actie_nu = []
    # Magneetklok: elke 2 seconden het dichtstbijzijnde monster
    if heeft(sp, "Magneetklok"):
        sp._uv_magneetklok += 1
        if sp._uv_magneetklok >= MAGNEETKLOK_TIJD:
            sp._uv_magneetklok = 0
            v = _dichtste(sp, vijanden, MAGNEETKLOK_BEREIK, weg)
            if v is not None:
                weg.append(v)
    # Koplampauto: monsters vóór je schrikken en lopen weg
    if heeft(sp, "Koplampauto"):
        for v in vijanden:
            d = (v.x + v.breedte / 2 - cx) * k
            if not getattr(v, "is_spike", False) and 0 < d <= KOPLAMP_BEREIK and abs(v.y - sp.y) < 60:
                if getattr(v, "snelheid", 0):
                    v.snelheid = abs(v.snelheid) * k
    # Lichtzwaard: raak je een monster, dan is het weg
    if heeft(sp, "Lichtzwaard"):
        for v in vijanden:
            if (not getattr(v, "is_spike", False) and v not in weg
                    and v.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte)):
                weg.append(v)
                _lading_op(sp, "Lichtzwaard")
                if not heeft(sp, "Lichtzwaard"):
                    break
    # Verblinde monsters worden weer beter
    for v in vijanden:
        if getattr(v, "_uv_flits", 0) > 0:
            v._uv_flits -= 1
    return weg, spikes, kogels


def _disco(sp):
    return heeft(sp, "Discobal") and sp.staat_op_grond and abs(sp.snelheid_x) < 0.1


def monster_bevroren(sp, v):
    """Staat dit monster stil en is het ongevaarlijk? (tijdstopwaaier, flitslicht, discobal)"""
    if getattr(v, "is_spike", False):
        return False
    if sp._uv_bevroren > 0 or getattr(v, "_uv_flits", 0) > 0:
        return True
    if _disco(sp):
        return math.hypot(v.x - sp.x, v.y - sp.y) <= DISCO_BEREIK
    return False


def monster_sloom(sp):
    """Slowmotion, Vertrager en Stroboscoop: monsters bewegen maar af en toe."""
    n = 1
    if heeft(sp, "Slowmotion"):
        n = max(n, 1 + niveau(sp, "Slowmotion"))
    if heeft(sp, "Vertrager"):
        n = max(n, 3)
    if heeft(sp, "Stroboscoop"):
        n = max(n, 4)
    return n > 1 and sp._uv_t % n != 0


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
    elif deel == "lamp":
        arcade.draw_circle_filled(x, y + 2, r * 0.8, kleur)
        arcade.draw_lrbt_rectangle_filled(x - r * 0.4, x + r * 0.4, y - r, y - r * 0.4, (160, 160, 170))
    elif deel == "raket":
        arcade.draw_lrbt_rectangle_filled(x - r * 0.35, x + r * 0.35, y - r * 0.6, y + r * 0.5, kleur)
        arcade.draw_triangle_filled(x - r * 0.35, y + r * 0.5, x + r * 0.35, y + r * 0.5, x, y + r, (230, 230, 240))
        arcade.draw_triangle_filled(x - r * 0.35, y - r * 0.6, x + r * 0.35, y - r * 0.6, x, y - r, (255, 220, 80))


def teken(sp):
    t = sp._uv_t
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    for b in sp._uv_bommen:
        arcade.draw_circle_filled(b["x"], b["y"] + 8, 8, (40, 40, 45))
        _onderdeel("klok", b["x"], b["y"] + 8, 5)
        if b["lont"] % 20 < 10:
            arcade.draw_circle_filled(b["x"] + 6, b["y"] + 17, 3, (255, 90, 40))
    for kn in sp._uv_knallen:
        r = BOM_BEREIK * (1 - kn["t"] / 20)
        arcade.draw_circle_filled(kn["x"], kn["y"] + 10, r, (255, 170, 50, kn["t"] * 10))
    if heeft(sp, "Terugkeerhorloge") and sp._uv_thuis:
        hx, hy = sp._uv_thuis
        arcade.draw_line(hx + 16, hy, hx + 16, hy + 30, (200, 200, 200), 2)
        arcade.draw_triangle_filled(hx + 16, hy + 30, hx + 16, hy + 20, hx + 28, hy + 25, (250, 210, 70))
    # Achter het poppetje
    if heeft(sp, "Luchtschip") or heeft(sp, "Zweefballon") or heeft(sp, "Lampion"):
        kleur = (255, 230, 120) if heeft(sp, "Lampion") and not heeft(sp, "Luchtschip") else (230, 70, 90)
        arcade.draw_ellipse_filled(cx, y + h + 22, 44 if heeft(sp, "Luchtschip") else 26, 24, kleur)
        arcade.draw_line(cx - 10, y + h + 10, x + 4, y + h, (120, 90, 60), 1)
        arcade.draw_line(cx + 10, y + h + 10, x + w - 4, y + h, (120, 90, 60), 1)
    if heeft(sp, "Maanlander"):
        arcade.draw_circle_outline(cx, y + h / 2, w, (200, 220, 255, 120), 2)
    if heeft(sp, "Zweefvlieger"):
        arcade.draw_triangle_filled(cx - 30, y + h, cx + 30, y + h, cx, y + h + 10, (120, 190, 240))
    if heeft(sp, "Discobal"):
        arcade.draw_circle_filled(cx, y + h + 20, 7, (200, 200, 220))
        if _disco(sp):
            for i in range(4):
                hoek = t * 0.1 + i * 1.57
                arcade.draw_line(cx, y + h + 20, cx + math.cos(hoek) * 60, y + h + 20 + math.sin(hoek) * 40,
                                 ((i * 80) % 255, 200, 255 - i * 50, 120), 2)
    # De uitvinder: bruin vest, wilde haren, bril op het voorhoofd, gereedschapsriem
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h * 0.62, (240, 240, 235))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + 4, y + h * 0.62, (140, 90, 50))
    arcade.draw_lrbt_rectangle_filled(x + w - 9, x + w - 3, y + 4, y + h * 0.62, (140, 90, 50))
    arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 4, y + 9, (90, 60, 40))
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 5, (240, 205, 170))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.72, 2.5, (20, 20, 30))
    for i in range(4):
        arcade.draw_circle_filled(x + 6 + i * 7, y + h - 3, 5, (230, 140, 50))
    arcade.draw_circle_outline(cx - 5, y + h - 6, 4, (80, 180, 220), 2)
    arcade.draw_circle_outline(cx + 5, y + h - 6, 4, (80, 180, 220), 2)
    # Voor het poppetje
    if heeft(sp, "Skateboard") or heeft(sp, "Raketauto") or heeft(sp, "Koplampauto") or heeft(sp, "Ballonfiets"):
        arcade.draw_lrbt_rectangle_filled(x - 4, x + w + 4, y - 4, y, (200, 60, 60))
        for wx in (x + 2, x + w - 2):
            arcade.draw_circle_filled(wx, y - 6, 3, (40, 40, 45))
        if heeft(sp, "Koplampauto"):
            lx = x + w + 4 if k > 0 else x - 4
            arcade.draw_triangle_filled(lx, y + 2, lx + k * 60, y + 16, lx + k * 60, y - 8, (255, 250, 170, 70))
        if heeft(sp, "Raketauto"):
            ax = x if k > 0 else x + w
            arcade.draw_triangle_filled(ax, y - 2, ax, y + 6, ax - k * (10 + t % 6), y + 2, (255, 170, 40))
    if heeft(sp, "Stuiterpak") or heeft(sp, "Springveren") or heeft(sp, "Terugveer"):
        for wx in (x + 8, x + w - 8):
            _onderdeel("veer", wx, y + 2, 5)
    if heeft(sp, "Hovercraft"):
        arcade.draw_lrbt_rectangle_filled(x - 6, x + w + 6, y - 3, y + 3, (80, 80, 90))
    if heeft(sp, "Plafondlopers"):
        for wx in (x + 8, x + w - 8):
            arcade.draw_lrbt_rectangle_filled(wx - 5, wx + 5, y + h - 2, y + h + 3, (220, 50, 50))
    if heeft(sp, "Stofzuiger"):
        arcade.draw_line(cx, y + h * 0.4, cx + k * 20, y + h * 0.3, (100, 100, 110), 4)
        if sp._uv_zuig > 0:
            for i in range(3):
                afst = 30 + ((t * 4 + i * 20) % 60)
                arcade.draw_line(cx + k * afst, y + h * 0.3 + 10, cx + k * (afst - 10), y + h * 0.3, (200, 230, 255), 2)
    if heeft(sp, "Lichtzwaard"):
        arcade.draw_line(cx + k * 8, y + h * 0.4, cx + k * 30, y + h * 0.9, (140, 255, 180), 4)
    if heeft(sp, "Schildrobot"):
        for i in range(sp._uv_actief["Schildrobot"]["lad"]):
            hoek = t * 0.08 + i * math.pi
            rx, ry = cx + math.cos(hoek) * 26, y + h / 2 + math.sin(hoek) * 20
            arcade.draw_circle_filled(rx, ry, 5, (150, 160, 175))
            arcade.draw_circle_filled(rx + 1, ry + 1, 1.5, (90, 240, 200))
    if sp._uv_aftel > 0:
        arcade.draw_text(str(sp._uv_aftel // 20 + 1), cx, y + h + 30, (255, 220, 80), 18, bold=True, anchor_x="center")
    if sp._uv_rook > 0:
        for i in range(4):
            f = (60 - sp._uv_rook) / 4
            arcade.draw_circle_filled(cx - 12 + i * 8, y + h + f + i * 3, 5 + f / 4, (90, 90, 90, sp._uv_rook * 3))


def teken_bevroren(sp, vijanden):
    for v in vijanden:
        if monster_bevroren(sp, v):
            arcade.draw_lrbt_rectangle_filled(v.x - 2, v.x + v.breedte + 2, v.y, v.y + v.hoogte + 2, (160, 220, 255, 110))


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 30, y + 24, (0, 0, 0, 155))
    for i, deel in enumerate(ONDERDELEN):
        l = x - 292 + i * 40
        arcade.draw_lrbt_rectangle_filled(l, l + 37, y - 2, y + 22, (60, 60, 70) if deel not in sp._uv_bank else (90, 130, 90))
        _onderdeel(deel, l + 12, y + 10, 7)
        arcade.draw_text(str(i + 1), l + 30, y + 2, (255, 255, 255), 9, bold=True, anchor_x="center")
    arcade.draw_text("werkbank:", x + 30, y + 5, (230, 230, 230), 10)
    for i in range(3):
        l = x + 100 + i * 28
        arcade.draw_lrbt_rectangle_outline(l, l + 24, y, y + 22, (200, 200, 200), 1)
        if i < len(sp._uv_bank):
            _onderdeel(sp._uv_bank[i], l + 12, y + 11, 7)
    arcade.draw_text("omlaag = bouwen" if sp._uv_bank else "omlaag = gebruiken", x + 292, y + 5,
                     (200, 200, 200), 9, anchor_x="right")
    if sp._uv_naam:
        delen = []
        for e, wv in sp._uv_actief.items():
            delen.append("%s %s" % (e, ("x%d" % wv["lad"]) if wv["lad"] else ("%ds" % (wv["tijd"] // 60 + 1))))
        arcade.draw_text(", ".join(delen), x - 292, y - 24, (250, 220, 120), 9, bold=True)
    arcade.draw_text("Boek: %d / %d" % (len(sp._uv_ontdekt), AANTAL_UITVINDINGEN), x + 292, y - 24,
                     (220, 220, 230), 10, bold=True, anchor_x="right")
    if sp._uv_melding_tijd > 0:
        arcade.draw_text(sp._uv_melding, x, y - 50, (250, 230, 150), 12, bold=True, anchor_x="center")

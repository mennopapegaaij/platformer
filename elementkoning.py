# elementkoning.py
# De ELEMENTENKONING: een poppetje met 25 vormen!
# Net als de Elementmeester wissel je bij elke landing naar de volgende vorm,
# altijd in dezelfde volgorde (geen toeval). Elke vorm heeft een eigen kracht.
#
# Alles staat in één grote tabel (ELEMENTEN). Wil je een element veranderen?
# Pas dan gewoon de getallen in de tabel aan!

import math
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

# ---------------------------------------------------------------------------
# De standaard-waarden. Elk element hieronder verandert alleen wat anders is.
# ---------------------------------------------------------------------------
STANDAARD = {
    "snel": 1.0,        # hoe snel je loopt (1.0 = gewoon)
    "grip": None,       # None = meteen op snelheid; een klein getal = glad
    "zwaar": 1.0,       # zwaartekracht (1.0 = gewoon, kleiner = zweveriger)
    "sprong": 1.0,      # hoe hoog je springt
    "grootte": 1.0,     # hoe groot je bent
    "extra": 0,         # hoeveel extra sprongen je in de lucht hebt
    "actie": None,      # wat een druk in de lucht doet: stamp/dash/teleport/omkeer
    "vasthoud": None,   # wat knop-vasthouden doet: glij (langzaam vallen) / zweef (jetpack)
    "stuiter": 0,       # stuiteren bij landen (0 = niet, 0.7 = flink)
    "spikestuiter": False,  # val je op een spike, dan stuiter je weg (en je blijft dit element)
    "ver": 0,           # extra vaart naar voren bij elke sprong
    "valzacht": None,   # je valt nooit sneller dan dit (bv. -1.2 = heel langzaam)
    "smelt": False,     # spikes die je raakt smelten weg (en doen geen pijn)
    "schild": False,    # één klap tegenhouden
    "gif": False,       # monsters die je raakt gaan dood
    "knal": False,      # elke sprong vanaf de grond maakt een schokgolf
    "vorm": "blok",     # hoe hij eruitziet
    "deeltje": None,    # welke deeltjes hij maakt
}

# ---------------------------------------------------------------------------
# De 25 elementen, op volgorde. (naam, kleur, tweede kleur, uitleg, anders)
# ---------------------------------------------------------------------------
_LIJST = [
    ("Vuur",      (230, 80, 30),   (255, 190, 40),  "supersnel",
     dict(snel=1.4, vorm="vlam", deeltje="vonk")),
    ("Water",     (60, 150, 255),  (200, 230, 255), "dubbelsprong",
     dict(extra=1, grip=0.12, vorm="druppel", deeltje="bel")),
    ("Lucht",     (225, 240, 255), (160, 200, 235), "glijden (knop vasthouden)",
     dict(zwaar=0.45, sprong=0.8, vasthoud="glij", vorm="wolk", deeltje="wolkje")),
    ("Aarde",     (150, 105, 60),  (95, 65, 35),    "stampen + schokgolf",
     dict(snel=0.7, zwaar=1.4, sprong=0.8, actie="stamp", vorm="rots", deeltje="stof")),
    ("IJs",       (170, 225, 255), (255, 255, 255), "superglad",
     dict(snel=1.3, grip=0.04, vorm="kristal", deeltje="sneeuw")),
    ("Bliksem",   (255, 225, 40),  (255, 255, 200), "dash in de lucht",
     dict(snel=1.5, actie="dash", vorm="bliksem", deeltje="vonk")),
    ("Lava",      (220, 60, 20),   (255, 150, 30),  "smelt spikes!",
     dict(snel=0.85, smelt=True, vorm="bol", deeltje="vonk")),
    ("Plant",     (70, 170, 60),   (170, 230, 110), "hoog springen",
     dict(sprong=1.3, vorm="blad", deeltje="blaadje")),
    ("Metaal",    (150, 155, 170), (220, 225, 235), "schild tegen 1 klap",
     dict(snel=0.9, zwaar=1.6, schild=True, vorm="blok")),
    ("Zand",      (225, 195, 120), (190, 150, 80),  "verste sprong van allemaal",
     dict(grip=0.2, ver=7, sprong=1.1, vorm="hoop", deeltje="korrel")),
    ("Licht",     (255, 250, 190), (255, 255, 255), "teleporteren in de lucht",
     dict(actie="teleport", vorm="ster", deeltje="glitter")),
    ("Schaduw",   (45, 40, 65),    (110, 90, 150),  "piepklein",
     dict(grootte=0.6, snel=1.1, vorm="bol")),
    ("Rook",      (140, 140, 150), (200, 200, 210), "jetpack (knop vasthouden)",
     dict(zwaar=0.7, vasthoud="zweef", vorm="wolk", deeltje="wolkje")),
    ("Kristal",   (190, 110, 240), (240, 200, 255), "stuiter op spikes (van boven)!",
     dict(spikestuiter=True, vorm="kristal", deeltje="glitter")),
    ("Sneeuw",    (245, 250, 255), (190, 215, 240), "groot + zacht vallen",
     dict(grootte=1.4, valzacht=-3, vorm="bol", deeltje="sneeuw")),
    ("Stoom",     (220, 225, 230), (255, 255, 255), "heel licht",
     dict(zwaar=0.3, sprong=0.7, vorm="wolk", deeltje="wolkje")),
    ("Gif",       (120, 220, 60),  (40, 110, 30),   "monsters die je raakt gaan dood",
     dict(gif=True, vorm="druppel", deeltje="bel")),
    ("Donder",    (80, 80, 110),   (255, 230, 60),  "zwaartekracht omdraaien in de lucht",
     dict(actie="omkeer", vorm="wolk", deeltje="vonk")),
    ("Kosmos",    (60, 30, 110),   (255, 255, 255), "maan-zwaartekracht",
     dict(zwaar=0.25, sprong=0.6, vorm="bol", deeltje="glitter")),
    ("Olie",      (35, 30, 30),    (120, 100, 160), "glibberig en snel",
     dict(snel=1.6, grip=0.03, vorm="druppel")),
    ("Veer",      (250, 245, 235), (200, 190, 170), "valt altijd langzaam",
     dict(valzacht=-1.2, sprong=0.9, vorm="blad", deeltje="blaadje")),
    ("Glas",      (200, 240, 245), (255, 255, 255), "driedubbele sprong, maar traag",
     dict(extra=2, snel=0.6, vorm="kristal", deeltje="glitter")),
    ("Geluid",    (240, 120, 200), (255, 220, 245), "elke sprong een schokgolf",
     dict(knal=True, vorm="bol")),
    ("Zon",       (255, 200, 30),  (255, 245, 150), "snel en hoog",
     dict(snel=1.2, sprong=1.2, vorm="ster", deeltje="glitter")),
    ("Regenboog", (255, 90, 90),   (90, 160, 255),  "snel + dubbelsprong + glijden",
     dict(snel=1.2, extra=1, vasthoud="glij", vorm="regenboog", deeltje="glitter")),
]

ELEMENTEN = []
for _naam, _k1, _k2, _uitleg, _anders in _LIJST:
    _e = dict(STANDAARD)
    _e.update(_anders)
    _e.update(naam=_naam, kleur=_k1, kleur2=_k2, uitleg=_uitleg)
    ELEMENTEN.append(_e)

# Een paar vaste getallen voor de krachten
STAMP_SNELHEID = 20       # zo snel stamp je omlaag
DASH_SNELHEID = 11        # zo snel schiet je vooruit bij een dash
DASH_DUUR = 10            # zoveel stapjes duurt een dash
TELEPORT_AFSTAND = 90     # zo ver teleporteer je naar voren
GLIJ_SNELHEID = -1.5      # met glijden val je nooit sneller dan dit
ZWEEF_BRANDSTOF = 50      # zoveel stapjes kan de jetpack duwen per sprong
SCHOK_BEREIK = 170        # hoe ver een schokgolf monsters wegblaast
SPIKE_STUITER = 11        # zo hard stuiter je als kristal omhoog van een spike
FLITS = 20                # hoe lang de flits duurt bij het wisselen

# De regenboog-kleuren (voor de regenboog-vorm)
REGENBOOG = [(255, 70, 70), (255, 160, 40), (255, 230, 50), (80, 200, 80), (70, 140, 255), (160, 90, 230)]


# ===========================================================================
# Hulpjes die de speler gebruikt
# ===========================================================================
def element(sp):
    """Het element (de tabel-regel) waarin de speler nu is."""
    return ELEMENTEN[sp._ek_nr]


def volgend(sp):
    """Het element dat hierna komt."""
    return ELEMENTEN[(sp._ek_nr + 1) % len(ELEMENTEN)]


def reset(sp):
    """Begin weer bij element 1 (vuur)."""
    sp._ek_nr = 0
    sp._ek_flits = 0
    sp._ek_t = 0
    sp._ek_deeltjes = []
    sp._ek_extra = ELEMENTEN[0]["extra"]   # extra sprongen die je nog over hebt
    sp._ek_actie_klaar = True              # mag je je lucht-actie nog gebruiken?
    sp._ek_stamp = False
    sp._ek_dash = 0
    sp._ek_brandstof = ZWEEF_BRANDSTOF
    sp._ek_schild = ELEMENTEN[0]["schild"]
    sp._ek_platforms = []
    sp._schokgolf = None                   # (dezelfde naam als bij de Elementmeester)


def _deeltje(sp, x, y, vx, vy, leven, kleur, grootte):
    sp._ek_deeltjes.append([x, y, vx, vy, leven, leven, kleur, grootte])


def _schokgolf(sp, x, y):
    """Maak een schokgolf (het spel blaast dan monsters in de buurt weg)."""
    sp._schokgolf = {"x": x, "y": y, "t": 0, "klaar": False}
    for i in range(14):
        h = math.radians(i * 180 / 13)
        _deeltje(sp, x, y + 2, math.cos(h) * 4, math.sin(h) * 3, 22, element(sp)["kleur2"], 4)


def stap(sp, platforms):
    """Elke stap: deeltjes bewegen, nieuwe deeltjes maken, tellers aftellen."""
    sp._ek_platforms = platforms
    sp._ek_t += 1
    if sp._ek_flits > 0:
        sp._ek_flits -= 1
    for d in sp._ek_deeltjes:
        d[0] += d[2]
        d[1] += d[3]
        d[4] -= 1
    sp._ek_deeltjes = [d for d in sp._ek_deeltjes if d[4] > 0]
    if sp._schokgolf is not None:
        sp._schokgolf["t"] += 1
        if sp._schokgolf["t"] > 25:
            sp._schokgolf = None
    # Nieuwe deeltjes (op een vast ritme van het tellertje: niet willekeurig)
    e = element(sp)
    soort = e["deeltje"]
    if soort is None or sp._ek_t % 3 != 0:
        return
    t = sp._ek_t
    cx = sp.x + sp.breedte / 2
    achter = -1 if sp.kijkt_rechts else 1
    k = e["kleur2"]
    if soort == "vonk" and abs(sp.snelheid_x) > 0.5:
        _deeltje(sp, cx + achter * sp.breedte / 2, sp.y + 6 + (t * 7) % 16, achter * 0.8, 1.2, 16, k, 3)
    elif soort == "bel" and t % 6 == 0:
        _deeltje(sp, cx - 8 + (t * 5) % 16, sp.y + sp.hoogte, 0, 0.9, 28, k, 2.5)
    elif soort == "wolkje":
        h = t * 0.35
        _deeltje(sp, cx + math.cos(h) * 22, sp.y + sp.hoogte / 2 + math.sin(h) * 22,
                 -math.sin(h) * 0.6, math.cos(h) * 0.6, 18, k, 3)
    elif soort == "stof" and sp._ek_stamp:
        _deeltje(sp, cx, sp.y + sp.hoogte, 0, 1.5, 12, k, 3)
    elif soort == "sneeuw":
        _deeltje(sp, cx - 12 + (t * 11) % 24, sp.y + sp.hoogte + 4, 0.3, -0.8, 24, k, 2)
    elif soort == "glitter":
        h = t * 1.7
        _deeltje(sp, cx + math.cos(h) * 16, sp.y + sp.hoogte / 2 + math.sin(h) * 16, 0, 0.3, 14, k, 2)
    elif soort == "blaadje" and abs(sp.snelheid_x) > 0.5:
        _deeltje(sp, cx + achter * sp.breedte / 2, sp.y + sp.hoogte * 0.7, achter * 0.5, -0.6, 26, k, 3)
    elif soort == "korrel" and abs(sp.snelheid_x) > 0.5:
        _deeltje(sp, cx + achter * sp.breedte / 2, sp.y + 2, achter * 1.0, 0.8, 12, k, 2)


def loop(sp, L, R, snelheid):
    """Links/rechts lopen, zoals het huidige element dat doet."""
    e = element(sp)
    kant = -1 if (L and not R) else (1 if (R and not L) else 0)
    if kant != 0:
        sp.kijkt_rechts = kant > 0
    if sp._ek_dash > 0:
        # Aan het dashen: razendsnel rechtdoor
        sp._ek_dash -= 1
        sp.snelheid_x = DASH_SNELHEID * (1 if sp.kijkt_rechts else -1)
        return
    if e["ver"] and not sp.staat_op_grond:
        return                                    # verre sprong: in de lucht hou je je vaart
    doel = kant * snelheid * e["snel"]
    if e["grip"] is None:
        sp.snelheid_x = doel
    else:
        sp.snelheid_x += (doel - sp.snelheid_x) * e["grip"]


def zwaartekracht(sp, richting):
    """Omhoog/omlaag bewegen, zoals het huidige element dat doet."""
    e = element(sp)
    if sp._ek_dash > 0:
        sp.snelheid_y = 0                     # tijdens een dash vlieg je rechtdoor
        return
    if sp._ek_stamp:
        sp.snelheid_y = -STAMP_SNELHEID * richting
        return
    sp.snelheid_y -= ZWAARTEKRACHT * e["zwaar"] * richting
    omlaag = sp.snelheid_y * richting            # negatief = aan het vallen
    if e["vasthoud"] == "glij" and sp.vlieg_omhoog and omlaag < GLIJ_SNELHEID:
        sp.snelheid_y = GLIJ_SNELHEID * richting   # glijden: langzaam naar beneden
    elif e["vasthoud"] == "zweef" and sp.vlieg_omhoog and sp._ek_brandstof > 0:
        sp._ek_brandstof -= 1                      # jetpack: duwt je omhoog zolang er brandstof is
        sp.snelheid_y = min(sp.snelheid_y * richting + 0.9, 4) * richting
        _deeltje(sp, sp.x + sp.breedte / 2, sp.y, 0, -2, 12, e["kleur2"], 3)
    if e["valzacht"] is not None and sp.snelheid_y * richting < e["valzacht"]:
        sp.snelheid_y = e["valzacht"] * richting   # zacht vallen


def stuiter_bij_landen(sp):
    """Moet je nu stuiteren in plaats van landen? Zo ja: doe het en geef True."""
    e = element(sp)
    if e["stuiter"] and sp.snelheid_y < -4:
        sp.snelheid_y = -sp.snelheid_y * e["stuiter"]
        return True
    return False


def spike_stuiter(sp):
    """Kristal valt op een spike: stuiter omhoog. Geeft True als dat gebeurde."""
    e = element(sp)
    if not e["spikestuiter"] or sp.snelheid_y * sp.zwaartekracht_richting > -1:
        return False                              # alleen als je van boven op de spike valt
    sp.snelheid_y = SPIKE_STUITER * sp.zwaartekracht_richting
    sp._ek_actie_klaar = True
    cx = sp.x + sp.breedte / 2
    for i in range(10):                           # rinkel! glinsterende scherfjes
        h = math.radians(i * 18)
        _deeltje(sp, cx, sp.y, math.cos(h) * 3, math.sin(h) * 3, 18, e["kleur2"], 3)
    return True


def spring(sp):
    """De springknop: op de grond springen, in de lucht je extra kracht."""
    e = element(sp)
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * sp.zwaartekracht_richting
    kant = 1 if sp.kijkt_rechts else -1
    if sp.staat_op_grond:
        sp.snelheid_y = kracht * e["sprong"]
        if e["ver"]:
            sp.snelheid_x += e["ver"] * kant        # verre sprong: extra vaart naar voren
        if e["knal"]:
            _schokgolf(sp, sp.x + sp.breedte / 2, sp.y)   # elke sprong: BOEM
        return
    # In de lucht: eerst je extra sprongen
    if sp._ek_extra > 0:
        sp._ek_extra -= 1
        sp.snelheid_y = kracht * e["sprong"] * 0.9
        cx = sp.x + sp.breedte / 2
        for i in range(8):
            h = math.radians(i * 45)
            _deeltje(sp, cx, sp.y, math.cos(h) * 2, math.sin(h) * 2, 16, e["kleur2"], 3)
        return
    # Dan je lucht-actie (één keer per sprong)
    actie = e["actie"]
    if actie is None or not sp._ek_actie_klaar:
        return
    sp._ek_actie_klaar = False
    if actie == "stamp":
        sp._ek_stamp = True
    elif actie == "dash":
        sp._ek_dash = DASH_DUUR
    elif actie == "omkeer":
        sp.zwaartekracht_richting *= -1           # de zwaartekracht draait om!
        sp.snelheid_y = 0
    elif actie == "teleport":
        oude_x = sp.x
        sp.x += TELEPORT_AFSTAND * kant
        for p in sp._ek_platforms:                # niet ín een muur teleporteren
            if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                    and sp._overlapt(p)):
                sp.x = oude_x
                break
        for i in range(10):                       # glitter op de oude én de nieuwe plek
            _deeltje(sp, oude_x + sp.breedte / 2, sp.y + i * 3, 0, 0.5, 18, e["kleur2"], 3)
            _deeltje(sp, sp.x + sp.breedte / 2, sp.y + i * 3, 0, 0.5, 18, e["kleur"], 3)


def geland(sp):
    """Net geland: eerst het effect van deze vorm, dan wissel je naar de volgende."""
    cx = sp.x + sp.breedte / 2
    if sp._ek_stamp:
        _schokgolf(sp, cx, sp.y)                  # stamp-landing: BOEM
    sp._ek_stamp = False
    sp._ek_dash = 0
    # Volgende element
    sp._ek_nr = (sp._ek_nr + 1) % len(ELEMENTEN)
    e = element(sp)
    sp._ek_extra = e["extra"]
    sp._ek_actie_klaar = True
    sp._ek_brandstof = ZWEEF_BRANDSTOF
    sp._ek_schild = e["schild"]
    sp.zwaartekracht_richting = 1                 # na donder: weer gewoon naar beneden
    if abs(sp.grootte_factor - e["grootte"]) > 0.001:
        sp.zet_grootte(e["grootte"], 0)           # groter of kleiner worden
    sp._ek_flits = FLITS
    cy = sp.y + sp.hoogte / 2
    for i in range(12):
        h = math.radians(i * 30)
        _deeltje(sp, cx, cy, math.cos(h) * 3, math.sin(h) * 3, 18, e["kleur"], 3)


# ===========================================================================
# Tekenen
# ===========================================================================
def _ster(cx, cy, r_buiten, r_binnen, punten=5, draai=0):
    pts = []
    for i in range(punten * 2):
        r = r_buiten if i % 2 == 0 else r_binnen
        h = math.radians(90 + draai + i * 180 / punten)
        pts.append((cx + math.cos(h) * r, cy + math.sin(h) * r))
    return pts


def _teken_vorm(vorm, x, y, w, h, k1, k2, t):
    cx, cy = x + w / 2, y + h / 2
    if vorm == "vlam":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, k1)
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 3, y + h * 0.5, k2)
        for i in range(4):
            fx = x + w * (i + 0.5) / 4
            hoog = h * 0.28 + ((t + i * 5) % 8)
            arcade.draw_triangle_filled(fx - w / 8, y + h, fx + w / 8, y + h, fx, y + h + hoog, k2)
    elif vorm == "druppel":
        arcade.draw_circle_filled(cx, y + h * 0.42, w * 0.5, k1)
        arcade.draw_triangle_filled(cx - w * 0.42, y + h * 0.6, cx + w * 0.42, y + h * 0.6,
                                    cx, y + h + h * 0.2, k1)
        arcade.draw_circle_filled(cx - w * 0.2, y + h * 0.55, w / 8, k2)
    elif vorm == "wolk":
        for dx, dy, r in ((-0.25, 0, 0.32), (0.25, 0, 0.32), (0, 0.22, 0.35), (0, -0.12, 0.32)):
            arcade.draw_circle_filled(cx + dx * w, cy + dy * h, r * w, k1)
        for i in range(2):
            h0 = t * 0.12 + i * 3.1
            arcade.draw_arc_outline(cx, cy, w * 1.4, h * 1.4, k2,
                                    math.degrees(h0), math.degrees(h0) + 50, 2)
    elif vorm == "rots":
        rots = [(x, y), (x + w, y), (x + w, y + h * 0.75), (x + w * 0.75, y + h),
                (x + w * 0.2, y + h), (x, y + h * 0.7)]
        arcade.draw_polygon_filled(rots, k1)
        arcade.draw_polygon_outline(rots, k2, 2)
        arcade.draw_line(x + w * 0.3, y + h * 0.2, x + w * 0.45, y + h * 0.45, k2, 2)
        arcade.draw_line(x + w * 0.7, y + h * 0.15, x + w * 0.8, y + h * 0.4, k2, 2)
    elif vorm == "kristal":
        pts = [(cx, y + h + 4), (x + w, cy), (cx, y - 2), (x, cy)]
        arcade.draw_polygon_filled(pts, k1)
        arcade.draw_polygon_outline(pts, k2, 2)
        arcade.draw_line(cx, y + h + 4, cx, y - 2, k2, 1)
        arcade.draw_triangle_filled(cx - w * 0.2, cy + h * 0.2, cx - w * 0.05, cy + h * 0.4,
                                    cx - w * 0.3, cy, (255, 255, 255))
    elif vorm == "ster":
        arcade.draw_polygon_filled(_ster(cx, cy, w * 0.62, w * 0.3, 5, t * 2), k1)
        arcade.draw_circle_filled(cx, cy, w * 0.25, k2)
    elif vorm == "bol":
        arcade.draw_circle_filled(cx, cy, w * 0.5, k1)
        arcade.draw_circle_outline(cx, cy, w * 0.5, k2, 2)
        arcade.draw_circle_outline(cx, cy, w * 0.5 + 3 + (t % 20) * 0.5, (k2[0], k2[1], k2[2], 120), 1)
    elif vorm == "blad":
        arcade.draw_ellipse_filled(cx, cy, w * 1.1, h * 0.8, k1, 25)
        arcade.draw_line(cx - w * 0.45, cy - h * 0.2, cx + w * 0.45, cy + h * 0.2, k2, 2)
    elif vorm == "hoop":
        pts = [(x, y)] + [(cx + math.cos(math.radians(a)) * w / 2, y + math.sin(math.radians(a)) * h)
                          for a in range(0, 181, 20)] + [(x + w, y)]
        arcade.draw_polygon_filled(pts, k1)
        for i in range(5):
            arcade.draw_circle_filled(x + w * (0.2 + i * 0.15), y + h * (0.3 + (i % 2) * 0.2), 1.5, k2)
    elif vorm == "bliksem":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (70, 70, 90))
        bolt = [(cx + w * 0.1, y + h), (cx - w * 0.25, cy), (cx, cy), (cx - w * 0.1, y),
                (cx + w * 0.25, cy + h * 0.1), (cx, cy + h * 0.1)]
        arcade.draw_polygon_filled(bolt, k1)
    elif vorm == "regenboog":
        for i, kl in enumerate(REGENBOOG):
            arcade.draw_circle_filled(cx, cy, w * 0.55 - i * w * 0.07, kl)
    else:  # blok
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, k1)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, k2, 3)
        for i in range(3):
            arcade.draw_circle_filled(x + w * (0.25 + i * 0.25), y + h * 0.2, 2, k2)


def teken(sp):
    """Teken de elementenkoning: deeltjes, schokgolf, de vorm, kroontje en extra's."""
    e = element(sp)
    for x, y, vx, vy, leven, max_leven, kleur, grootte in sp._ek_deeltjes:
        deel = leven / max_leven
        arcade.draw_circle_filled(x, y, max(1, grootte * deel),
                                  (kleur[0], kleur[1], kleur[2], int(60 + 195 * deel)))
    if sp._schokgolf is not None:
        sg = sp._schokgolf
        r = 10 + sg["t"] * (SCHOK_BEREIK / 25)
        a = max(0, 255 - sg["t"] * 10)
        arcade.draw_ellipse_outline(sg["x"], sg["y"] + 4, r * 2, r * 0.7, (190, 140, 80, a), 4)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx, cy = x + w / 2, y + h / 2
    t = sp._ek_t
    # Dash-strepen achter je
    if sp._ek_dash > 0:
        achter = -1 if sp.kijkt_rechts else 1
        for i in range(3):
            yy = y + h * (0.25 + i * 0.25)
            arcade.draw_line(cx + achter * w * 0.6, yy, cx + achter * (w * 0.6 + 30), yy, e["kleur2"], 3)
    _teken_vorm(e["vorm"], x, y, w, h, e["kleur"], e["kleur2"], t)
    # Oogjes (kijken de kant op waar je heen gaat)
    kijk = 2 if sp.kijkt_rechts else -2
    oog = (20, 20, 30) if sum(e["kleur"]) > 250 else (255, 255, 255)
    arcade.draw_circle_filled(cx - w * 0.18 + kijk, cy + h * 0.12, max(2, w / 12), oog)
    arcade.draw_circle_filled(cx + w * 0.18 + kijk, cy + h * 0.12, max(2, w / 12), oog)
    # Gouden kroontje: je bent de koning!
    ky = y + h + 3 if e["vorm"] not in ("vlam", "druppel") else y + h + h * 0.35
    arcade.draw_polygon_filled([(cx - 7, ky), (cx + 7, ky), (cx + 7, ky + 5), (cx + 4, ky + 2),
                                (cx, ky + 7), (cx - 4, ky + 2), (cx - 7, ky + 5)], (255, 210, 40))
    # Schild (metaal): een blauwe ring zolang het schild er nog is
    if sp._ek_schild:
        arcade.draw_circle_outline(cx, cy, max(w, h) * 0.8, (120, 200, 255, 180), 2)
    # Jetpack-brandstof (rook): een klein balkje
    if e["vasthoud"] == "zweef":
        deel = sp._ek_brandstof / ZWEEF_BRANDSTOF
        arcade.draw_lrbt_rectangle_filled(x, x + w * deel, y - 6, y - 3, (255, 160, 40))
    # Extra sprongen over: bolletjes boven je hoofd
    for i in range(sp._ek_extra):
        arcade.draw_circle_outline(cx - 5 * (sp._ek_extra - 1) + i * 10, ky + 14, 3, e["kleur2"], 2)
    # Flits bij het wisselen
    if sp._ek_flits > 0:
        deel = sp._ek_flits / FLITS
        arcade.draw_circle_outline(cx, cy, w * 0.6 + (1 - deel) * 30, (255, 255, 255, int(255 * deel)), 3)


def teken_hud(sp, x, y):
    """Het balkje bovenin: nummer, naam en kracht van nu, en wat hierna komt."""
    e, straks = element(sp), volgend(sp)
    arcade.draw_lrbt_rectangle_filled(x - 210, x + 210, y - 10, y + 22, (0, 0, 0, 150))
    arcade.draw_circle_filled(x - 192, y + 6, 8, e["kleur"])
    arcade.draw_text("%d/25 %s: %s" % (sp._ek_nr + 1, e["naam"], e["uitleg"]),
                     x - 178, y, e["kleur"] if sum(e["kleur"]) > 200 else (230, 230, 240), 12, bold=True)
    arcade.draw_text("-> " + straks["naam"], x + 120, y, (200, 200, 200), 11)

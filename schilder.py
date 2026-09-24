# schilder.py
# De SCHILDER: spuit verf op de grond, en elke kleur doet iets anders!
#
#  Toets 1 = BLAUW  : trampoline (land je erop, dan stuiter je superhoog)
#  Toets 2 = ROOD   : snelweg (je rent twee keer zo snel)
#  Toets 3 = GROEN  : bedekt spikes (dan zijn ze onschadelijk)
#  Toets 4 = GEEL   : glijbaan (superglad)
#  Toets 5 = PAARS  : teleport (twee paarse vlekken zijn verbonden)
#  Toets 6 = ORANJE : lanceerverf (stap erop en je wordt schuin omhoog weggeschoten)
#  Toets 7 = WIT    : wolkverf (in de lucht: een wolkje onder je voeten, dat daarna oplost)
#  Toets 8 = BRUIN  : modder (monsters blijven erin vastzitten, jij loopt er langzaam)
#  Pijltje omlaag   : spuit een verfvlek op de grond onder je (ook vanuit de lucht)
#
# Elke kleur heeft een eigen voorraad die langzaam weer bijvult. Geen toeval.

import math
import arcade
from instellingen import SPRING_KRACHT
from platforms import Platform

KLEUREN = ["blauw", "rood", "groen", "geel", "paars", "oranje", "wit", "bruin"]
RGB = {"blauw": (60, 140, 255), "rood": (235, 60, 50), "groen": (70, 200, 80), "geel": (250, 215, 40),
       "paars": (170, 80, 230), "oranje": (255, 140, 30), "wit": (245, 245, 255), "bruin": (130, 85, 45)}
UITLEG = {"blauw": "trampoline", "rood": "snelweg", "groen": "spikes weg", "geel": "glijbaan",
          "paars": "teleport", "oranje": "lanceer", "wit": "wolk", "bruin": "modder"}
VOORRAAD_MAX = 100
KOST = 25                 # een verfvlek kost zoveel verf
BIJVULLEN = 0.08          # zoveel verf komt er per stapje vanzelf bij (per kleur)
VLEK_BREEDTE = 70         # zo breed is een verfvlek
MAX_VLEKKEN = 14          # meer vlekken? Dan verdwijnt de oudste
TRAMPOLINE = 1.8          # zo hard stuiter je van blauwe verf (keer een gewone sprong)
SNELWEG = 2.0             # zo snel ren je op rode verf
GLAD = 0.03               # zo glad is gele verf (klein = heel glad)
LANCEER_OMHOOG = 12       # oranje: zo hard word je omhoog geschoten
LANCEER_VOORUIT = 9       # oranje: zo hard word je vooruit geschoten...
LANCEER_DUUR = 40         # ...zolang (stapjes)
WOLK_BREEDTE = 80         # wit: zo breed is een wolkje
WOLK_LEVEN = 180          # wit: zo lang blijft een wolkje (3 seconden)
MODDER = 0.5              # bruin: zo snel loop jij door de modder


class Wolk(Platform):
    """Een wolkje van witte verf: je kunt er even op staan, daarna lost het op."""

    is_wolk = True

    def __init__(self, x, y):
        super().__init__(x, y, WOLK_BREEDTE, 12)
        self.leven = WOLK_LEVEN

    def teken(self):
        deel = max(0.0, self.leven / WOLK_LEVEN)
        a = int(80 + 175 * deel)                  # het wolkje wordt steeds doorzichtiger
        cx, cy = self.x + self.breedte / 2, self.y + self.hoogte / 2
        for dx, r in ((-26, 10), (-10, 14), (8, 13), (25, 10)):
            arcade.draw_circle_filled(cx + dx, cy + 2, r, (250, 250, 255, a))


def reset(sp):
    sp._sv_kleur = "blauw"
    sp._sv_voorraad = {k: VOORRAAD_MAX for k in KLEUREN}
    sp._sv_vlekken = []       # {"p": platform, "x0", "x1", "kleur", "t"}
    sp._sv_spikes = []        # spikes die je groen hebt geverfd
    sp._sv_onder = None       # op welke kleur je het laatst stond
    sp._sv_t = 0
    sp._sv_spetters = []      # [x, y, vx, vy, leven, kleur]
    sp._sv_tp_wacht = False   # paars: net geteleporteerd (eerst van de vlek af stappen)
    sp._sv_lanceer = 0        # oranje: hoe lang je nog vooruit wordt geschoten
    sp._sv_wolken = []        # wit: de wolkjes die er nu zijn


def kies_kleur(sp, nummer):
    if 1 <= nummer <= len(KLEUREN):
        sp._sv_kleur = KLEUREN[nummer - 1]
        return True
    return False


def _kleur_op(sp, platform):
    """Welke verf ligt er op dit platform, precies onder het midden van de speler?"""
    cx = sp.x + sp.breedte / 2
    for v in reversed(sp._sv_vlekken):           # nieuwste vlek eerst
        if v["p"] is platform and v["x0"] <= cx <= v["x1"]:
            return v["kleur"]
    return None


def kleur_onder(sp):
    """Op welke verf sta je (of stond je het laatst, als je in de lucht bent)?"""
    if sp.staat_op_grond:
        sp._sv_onder = _kleur_op(sp, getattr(sp, "_gelande_platform", None))
    return sp._sv_onder


def loop(sp, L, R, snelheid):
    """Lopen: rood = twee keer zo snel, geel = glad."""
    kleur = kleur_onder(sp)
    kant = -1 if (L and not R) else (1 if (R and not L) else 0)
    if kant != 0:
        sp.kijkt_rechts = kant > 0
    if sp._sv_lanceer > 0:
        sp._sv_lanceer -= 1
        sp.snelheid_x = LANCEER_VOORUIT * (1 if sp.kijkt_rechts else -1)   # oranje: weggeschoten!
        return
    if kleur == "rood":
        doel = kant * snelheid * SNELWEG
    elif kleur == "bruin":
        doel = kant * snelheid * MODDER            # modder: langzaam
    else:
        doel = kant * snelheid
    if kleur == "geel":
        # glad: je snelheid verandert maar heel langzaam (vaart houd je, afremmen kan bijna niet)
        sp.snelheid_x += (doel - sp.snelheid_x) * GLAD if kant != 0 else (-sp.snelheid_x * GLAD)
    else:
        sp.snelheid_x = doel


def trampoline(sp, platform):
    """Net geland op dit platform: is het blauw? Dan stuiter je omhoog (geeft True)."""
    if _kleur_op(sp, platform) == "blauw":
        sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * TRAMPOLINE
        cx = sp.x + sp.breedte / 2
        for i in range(8):
            h = math.radians(20 + i * 20)
            _spetter(sp, cx, sp.y, math.cos(h) * 3, math.sin(h) * 3, "blauw")
        return True
    return False


def _vlek_onder(sp):
    """De verfvlek waar je nu op staat (of None)."""
    cx = sp.x + sp.breedte / 2
    p = getattr(sp, "_gelande_platform", None)
    for v in reversed(sp._sv_vlekken):
        if v["p"] is p and v["x0"] <= cx <= v["x1"]:
            return v
    return None


def _spetter_rondje(sp, kleur):
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    for i in range(10):
        h = math.radians(i * 36)
        _spetter(sp, cx, cy, math.cos(h) * 3, math.sin(h) * 3 + 1, kleur)


def in_modder(sp, vijand):
    """Staat dit monster in de bruine modder? (Dan zit het vast.)"""
    mx = vijand.x + getattr(vijand, "breedte", 32) / 2
    for v in sp._sv_vlekken:
        if v["kleur"] == "bruin":
            top = v["p"].y + v["p"].hoogte
            if v["x0"] <= mx <= v["x1"] and abs(vijand.y - top) < 12:
                return True
    return False


def _spetter(sp, x, y, vx, vy, kleur):
    sp._sv_spetters.append([x, y, vx, vy, 20, kleur])


def stap(sp):
    """Elke stap: verf bijvullen en spettertjes laten vallen."""
    sp._sv_t += 1
    for k in KLEUREN:
        sp._sv_voorraad[k] = min(VOORRAAD_MAX, sp._sv_voorraad[k] + BIJVULLEN)
    for s in sp._sv_spetters:
        s[0] += s[2]
        s[1] += s[3]
        s[3] -= 0.25
        s[4] -= 1
    sp._sv_spetters = [s for s in sp._sv_spetters if s[4] > 0]
    onder = kleur_onder(sp) if sp.staat_op_grond else None
    # Paars: sta je op een paarse vlek? Dan teleporteer je naar de andere paarse vlek
    if onder != "paars":
        sp._sv_tp_wacht = False
    elif not sp._sv_tp_wacht:
        paars = [v for v in sp._sv_vlekken if v["kleur"] == "paars"]
        hier = _vlek_onder(sp)
        if len(paars) == 2 and hier in paars:
            daar = paars[1] if hier is paars[0] else paars[0]
            _spetter_rondje(sp, "paars")
            sp.x = (daar["x0"] + daar["x1"]) / 2 - sp.breedte / 2
            sp.y = daar["p"].y + daar["p"].hoogte
            sp._gelande_platform = daar["p"]
            sp._sv_tp_wacht = True                # eerst van de vlek af, anders flits je terug
            _spetter_rondje(sp, "paars")
    # Oranje: op een oranje vlek word je schuin omhoog weggeschoten
    if onder == "oranje" and sp._sv_lanceer == 0:
        sp.snelheid_y = LANCEER_OMHOOG
        sp._sv_lanceer = LANCEER_DUUR
        _spetter_rondje(sp, "oranje")
    if sp.staat_op_grond and onder != "oranje" and sp._sv_lanceer < LANCEER_DUUR - 5:
        sp._sv_lanceer = 0                        # weer geland: niet meer weggeschoten
    # Wit: wolkjes lossen langzaam op
    for w in sp._sv_wolken:
        w.leven -= 1
    sp._sv_wolken = [w for w in sp._sv_wolken if w.leven > 0]
    # Rode snelweg: vuurstreepjes achter je
    if kleur_onder(sp) == "rood" and abs(sp.snelheid_x) > 5 and sp._sv_t % 3 == 0:
        achter = -1 if sp.snelheid_x > 0 else 1
        _spetter(sp, sp.x + sp.breedte / 2 + achter * sp.breedte / 2, sp.y + 4, achter, 0.5, "rood")


def spuit(sp, platforms, vijanden):
    """Pijltje omlaag: spuit een verfvlek op het platform onder je. Geeft True als het lukte."""
    kleur = sp._sv_kleur
    if sp._sv_voorraad[kleur] < KOST:
        return False
    cx = sp.x + sp.breedte / 2
    if kleur == "wit":
        # Wolkverf werkt alleen in de lucht: er komt een wolkje onder je voeten
        if sp.staat_op_grond:
            return False
        wolk = Wolk(cx - WOLK_BREEDTE / 2, sp.y - 12)
        sp._sv_wolken.append(wolk)
        sp._sv_voorraad[kleur] -= KOST
        for i in range(10):
            _spetter(sp, cx + (i - 4.5) * 7, sp.y - 6, (i - 4.5) * 0.3, -1, kleur)
        return True
    # Zoek het hoogste platform onder je voeten (daar komt de verf op)
    doel = None
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and p.x <= cx <= p.x + p.breedte and p.y + p.hoogte <= sp.y + 2):
            if doel is None or p.y + p.hoogte > doel.y + doel.hoogte:
                doel = p
    if doel is None:
        return False                              # onder je is niks (een kuil): de verf valt weg
    x0 = max(doel.x, cx - VLEK_BREEDTE / 2)
    x1 = min(doel.x + doel.breedte, cx + VLEK_BREEDTE / 2)
    if kleur == "paars":
        # Er kunnen maar 2 paarse vlekken zijn (die zijn met elkaar verbonden)
        paars = [v for v in sp._sv_vlekken if v["kleur"] == "paars"]
        if len(paars) >= 2:
            sp._sv_vlekken.remove(paars[0])
    sp._sv_vlekken.append({"p": doel, "x0": x0, "x1": x1, "kleur": kleur, "t": 0})
    if len(sp._sv_vlekken) > MAX_VLEKKEN:
        sp._sv_vlekken.pop(0)
    sp._sv_voorraad[kleur] -= KOST
    top = doel.y + doel.hoogte
    # Groen op spikes: die worden bedekt en zijn dan onschadelijk
    if kleur == "groen":
        for v in vijanden:
            if (getattr(v, "is_spike", False) and hasattr(v, "aantal") and abs(v.y - top) < 6
                    and v.x < x1 and v.x + v.breedte > x0):
                v.geverfd = True
                if v not in sp._sv_spikes:
                    sp._sv_spikes.append(v)
    # Spettertjes van de spuitbus naar beneden
    for i in range(10):
        _spetter(sp, cx + (i - 4.5) * 6, sp.y, (i - 4.5) * 0.3, -2 - (i % 3), kleur)
    return True


# ===========================================================================
# Tekenen
# ===========================================================================
def teken(sp):
    t = sp._sv_t
    # Verfvlekken op de platforms
    for v in sp._sv_vlekken:
        top = v["p"].y + v["p"].hoogte
        kl = RGB[v["kleur"]]
        arcade.draw_lrbt_rectangle_filled(v["x0"], v["x1"], top - 3, top + 3, kl)
        for i in range(int((v["x1"] - v["x0"]) // 14)):              # druppeltjes langs de rand
            dx = v["x0"] + 7 + i * 14
            arcade.draw_circle_filled(dx, top - 3 - (i % 2) * 2, 3, kl)
        if v["kleur"] == "blauw":                                      # veertje-streepjes
            for i in range(int((v["x1"] - v["x0"]) // 20)):
                dx = v["x0"] + 10 + i * 20
                arcade.draw_line(dx - 4, top + 4, dx + 4, top + 8, (200, 230, 255), 2)
        elif v["kleur"] == "rood":                                     # pijltjes vooruit
            for i in range(int((v["x1"] - v["x0"]) // 24)):
                dx = v["x0"] + 12 + i * 24
                arcade.draw_triangle_filled(dx + 5, top + 6, dx - 3, top + 3, dx - 3, top + 9, (255, 200, 190))
        elif v["kleur"] == "paars":                                    # draaiend kringetje
            mx = (v["x0"] + v["x1"]) / 2
            arcade.draw_ellipse_outline(mx, top + 5, 30 + 6 * math.sin(t * 0.15), 8, (220, 170, 255), 2)
        elif v["kleur"] == "oranje":                                   # pijl schuin omhoog
            mx = (v["x0"] + v["x1"]) / 2
            arcade.draw_triangle_filled(mx + 8, top + 14, mx - 4, top + 12, mx + 4, top + 4, (255, 220, 170))
        elif v["kleur"] == "bruin":                                    # bubbeltjes in de modder
            for i in range(int((v["x1"] - v["x0"]) // 18)):
                if (t // 15 + i) % 3 == 0:
                    arcade.draw_circle_outline(v["x0"] + 9 + i * 18, top + 3, 3, (170, 120, 70), 1)
        elif v["kleur"] == "geel":                                     # glimmertjes
            if t % 20 < 10:
                arcade.draw_circle_filled(v["x0"] + (t * 3) % max(1, int(v["x1"] - v["x0"])), top + 4, 2,
                                          (255, 255, 255))
    # Groen geverfde spikes: een dikke laag groene smurrie eroverheen
    for s in sp._sv_spikes:
        arcade.draw_lrbt_rectangle_filled(s.x - 2, s.x + s.breedte + 2, s.y, s.y + s.hoogte * 0.7, (70, 200, 80))
        for i in range(s.aantal * 2):
            arcade.draw_circle_filled(s.x + 5 + i * (s.breedte - 10) / max(1, s.aantal * 2 - 1),
                                      s.y + s.hoogte * 0.7, 6, (70, 200, 80))
    for x, y, vx, vy, leven, kleur in sp._sv_spetters:
        arcade.draw_circle_filled(x, y, 2 + leven / 10, RGB[kleur])
    # De schilder: overall met verfvlekken, een baret en een spuitbus
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.65, (245, 245, 240))
    for i, kl in enumerate(KLEUREN):                                   # vlekjes op zijn overall
        arcade.draw_circle_filled(x + 6 + i * (w - 12) / 3, y + h * (0.2 + (i % 2) * 0.22), 2.5, RGB[kl])
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h * 0.6, y + h - 5, (240, 200, 160))
    arcade.draw_circle_filled(cx - 5 + k * 2, y + h * 0.78, 2.5, (20, 20, 30))
    arcade.draw_circle_filled(cx + 5 + k * 2, y + h * 0.78, 2.5, (20, 20, 30))
    # Baret (in je gekozen kleur)
    arcade.draw_ellipse_filled(cx - k * 2, y + h - 3, w * 0.85, 9, RGB[sp._sv_kleur])
    arcade.draw_circle_filled(cx - k * 2, y + h + 2, 2, RGB[sp._sv_kleur])
    # Spuitbus in de hand
    bx = x + w + 1 if k > 0 else x - 9
    arcade.draw_lrbt_rectangle_filled(bx, bx + 8, y + h * 0.25, y + h * 0.55, RGB[sp._sv_kleur])
    arcade.draw_lrbt_rectangle_filled(bx + 2, bx + 6, y + h * 0.55, y + h * 0.62, (60, 60, 60))


def teken_hud(sp, x, y):
    """Balkje bovenin: de 8 verfpotjes met hun voorraad; de gekozen kleur licht op."""
    arcade.draw_lrbt_rectangle_filled(x - 250, x + 250, y - 16, y + 26, (0, 0, 0, 150))
    for i, k in enumerate(KLEUREN):
        l = x - 246 + i * 62
        gekozen = k == sp._sv_kleur
        if gekozen:
            arcade.draw_lrbt_rectangle_outline(l - 2, l + 60, y - 14, y + 24, (255, 255, 255), 2)
        arcade.draw_text("%d" % (i + 1), l + 1, y + 8, (255, 255, 255), 9, bold=True)
        arcade.draw_lrbt_rectangle_filled(l + 10, l + 10 + 46 * sp._sv_voorraad[k] / VOORRAAD_MAX, y + 9, y + 18, RGB[k])
        arcade.draw_lrbt_rectangle_outline(l + 10, l + 56, y + 9, y + 18, RGB[k], 1)
        arcade.draw_text(UITLEG[k], l + 2, y - 9, RGB[k] if gekozen else (190, 190, 190), 8, bold=gekozen)

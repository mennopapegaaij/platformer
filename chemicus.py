# chemicus.py
# De CHEMICUS: meng drankjes in je ketel en ontdek superkrachten!
#
#  Toets 1 t/m 6  : doe een drankje in je ketel (er passen er 4 in)
#  Pijltje omlaag : drink je brouwsel op (het werkt 10 seconden)
#  Backspace      : ketel leeggooien
#
# De 6 flessen, elk met een gewoon effect (2 dezelfde = dubbel zo sterk):
#  1 blauw = Veerdrank   : lichter (je zweeft meer)
#  2 rood  = Springdrank : hoger springen
#  3 geel  = Reuzendrank : groter worden
#  4 groen = Rendrank    : sneller rennen
#  5 paars = Schilddrank : een schild tegen een klap (per drankje 1)
#  6 sterk = Krachtdrank : loop een monster omver (per drankje 1)
#
# SUPERKRACHTEN: elke combinatie van 2 verschillende kleuren geeft een eigen superkracht
# (15 stuks, zie SUPERKRACHTEN hieronder). Meng je 3 of 4 kleuren, dan krijg je al hun
# superkrachten tegelijk! Met 1 tot 4 drankjes zijn er 209 verschillende recepten.
# Alles is vast: hetzelfde recept geeft altijd hetzelfde (geen toeval).

import math
from itertools import combinations_with_replacement
import arcade
from instellingen import SPRING_KRACHT, ZWAARTEKRACHT

DRANKEN = ["blauw", "rood", "geel", "groen", "paars", "sterk"]
RGB = {"blauw": (70, 140, 255), "rood": (230, 60, 60), "geel": (250, 210, 40),
       "groen": (70, 200, 90), "paars": (170, 80, 220), "sterk": (150, 150, 165)}
WOORD = {"blauw": "Veer", "rood": "Spring", "geel": "Reuzen", "groen": "Ren", "paars": "Schild", "sterk": "Kracht"}
UITLEG = {"blauw": "lichter", "rood": "hoger", "geel": "groter", "groen": "sneller",
          "paars": "schild", "sterk": "omver"}

# De 15 superkrachten: (kleur, kleur) -> (naam, wat het doet)
SUPERKRACHTEN = {
    ("blauw", "rood"):  ("Wolkensprong", "2 extra sprongen in de lucht"),
    ("blauw", "geel"):  ("Parachute", "je valt heel langzaam"),
    ("blauw", "groen"): ("Luchtdash", "springen in de lucht = zoef vooruit"),
    ("blauw", "paars"): ("Spook", "monsters gaan dwars door je heen"),
    ("blauw", "sterk"): ("Omkeerder", "springen in de lucht = zwaartekracht om"),
    ("rood", "geel"):   ("Stampgolf", "elke landing = schokgolf"),
    ("rood", "groen"):  ("Stuiterschoenen", "je stuitert vanzelf"),
    ("rood", "paars"):  ("Sterrenkracht", "onkwetsbaar en monsters weg"),
    ("rood", "sterk"):  ("Raketsprong", "enorm hoge sprong"),
    ("geel", "groen"):  ("Tijdrem", "monsters lopen super sloom"),
    ("geel", "paars"):  ("Zeepbel", "val je in een kuil, dan zweef je terug"),
    ("geel", "sterk"):  ("Aardbeving", "de grond schudt monsters weg"),
    ("groen", "paars"): ("Flitser", "springen in de lucht = teleport vooruit"),
    ("groen", "sterk"): ("Vuurballen", "je schiet vanzelf vuurballen"),
    ("paars", "sterk"): ("Stekelpantser", "spikes breken als je ze raakt"),
}
AANTAL_KRACHTEN = len(SUPERKRACHTEN)          # = 15

KETEL_MAX = 4             # zoveel drankjes passen er in je ketel
DUUR = 600                # zo lang werkt een brouwsel (600 stapjes = 10 seconden)
SPRONG_PER = 0.2          # per rood drankje: zoveel hoger springen
SNEL_PER = 0.2            # per groen drankje: zoveel sneller
LICHT_PER = 0.18          # per blauw drankje: zoveel minder zwaartekracht
GROOT_PER = 0.2           # per geel drankje: zoveel groter
PARACHUTE_VAL = 2.5       # parachute: sneller dan dit val je niet
DASH_TIJD = 12            # luchtdash: zo lang zoef je
DASH_SNELHEID = 13        # luchtdash: zo snel
FLITS_AFSTAND = 130       # flitser: zo ver teleporteer je
STAMP_SNELHEID = 3        # stampgolf: bij elke landing (niet bij een piepklein stapje)
GOLF_BEREIK = 150         # zo ver reikt een schokgolf
BEVING_TIJD = 120         # aardbeving: elke 2 seconden een schok
VUUR_TIJD = 40            # vuurballen: zo vaak schiet je
RAKET = 1.7               # raketsprong: zoveel keer hoger
STUITER = 1.15            # stuiterschoenen: zo hard stuiter je

# Alle mogelijke recepten: 1 tot 4 drankjes, volgorde maakt niet uit
ALLE_RECEPTEN = set()
for _n in range(1, KETEL_MAX + 1):
    for _combi in combinations_with_replacement(range(len(DRANKEN)), _n):
        ALLE_RECEPTEN.add(tuple(_combi.count(i) for i in range(len(DRANKEN))))
AANTAL_RECEPTEN = len(ALLE_RECEPTEN)          # = 209

VOORVOEGSEL = {1: "", 2: "Dubbel-", 3: "Driedubbel-", 4: "Viervoudig-"}


def recept(ketel):
    """Het recept van een ketel: hoeveel van elk drankje (volgorde maakt niet uit)."""
    return tuple(ketel.count(d) for d in DRANKEN)


def naam(rec):
    """Een naam voor een recept, bv. (2,0,1,0,0,0) -> 'Dubbel-Veer-Reuzen-drank'."""
    delen = [VOORVOEGSEL[n] + WOORD[d] for d, n in zip(DRANKEN, rec) if n]
    return "-".join(delen) + "-drank" if delen else "leeg"


def krachten_van(rec):
    """Welke superkrachten geeft dit recept? (elk paar van verschillende kleuren = 1 kracht)"""
    kleuren = [d for d, n in zip(DRANKEN, rec) if n]
    uit = []
    for i in range(len(kleuren)):
        for j in range(i + 1, len(kleuren)):
            uit.append(SUPERKRACHTEN[(kleuren[i], kleuren[j])][0])
    return uit


def heeft(sp, kracht):
    """Werkt deze superkracht nu?"""
    return kracht in sp._ch_krachten


def reset(sp):
    sp._ch_ketel = []          # de drankjes in je ketel
    sp._ch_actief = None       # het recept dat nu werkt (of None)
    sp._ch_krachten = []       # de superkrachten die nu werken
    sp._ch_tijd = 0            # hoe lang het nog werkt
    sp._ch_schild = 0          # schild-ladingen van paarse drank
    sp._ch_kracht = 0          # krachtdrank: zoveel monsters kun je nog omver lopen
    sp._ch_extra = 0           # extra luchtsprongen die je nog over hebt
    sp._ch_lucht_truc = True   # dash/flits/omkeer: 1 keer per sprong
    sp._ch_dash = 0            # luchtdash: hoe lang je nog zoeft
    sp._ch_bel = 0             # zeepbel: zo vaak red je jezelf nog
    sp._ch_laatst = None       # zeepbel: laatste plek waar je stond
    sp._ch_valsnelheid = 0     # stampgolf: hoe hard je net viel
    sp._ch_golven = []         # schokgolven {"x", "y", "r"} (nieuw = r 0)
    sp._ch_vuur = 0            # vuurballen: aftellen tot de volgende
    sp._ch_vuurbal_nieuw = False
    sp._ch_platforms = []
    sp._ch_ontdekt = []        # recepten die je al hebt ontdekt (op volgorde)
    sp._ch_krachten_ontdekt = []   # superkrachten die je al hebt gehad
    sp._ch_melding = ""        # tekstje bovenin ("Nieuw recept!")
    sp._ch_melding_tijd = 0
    sp._ch_t = 0
    sp._ch_bubbels = []


def _telling(sp, drank):
    """Hoeveel van dit drankje zit er in het recept dat nu werkt?"""
    if sp._ch_actief is None:
        return 0
    return sp._ch_actief[DRANKEN.index(drank)]


def voeg_toe(sp, nummer):
    """Toets 1-6: doe een drankje in de ketel."""
    if not (1 <= nummer <= len(DRANKEN)) or len(sp._ch_ketel) >= KETEL_MAX:
        return False
    sp._ch_ketel.append(DRANKEN[nummer - 1])
    return True


def leeg(sp):
    sp._ch_ketel = []


def _uitgewerkt(sp):
    """Het brouwsel is op: alles terug naar normaal."""
    sp._ch_actief = None
    sp._ch_krachten = []
    sp._ch_schild = 0
    sp._ch_kracht = 0
    sp._ch_extra = 0
    sp._ch_dash = 0
    sp._ch_bel = 0
    sp.zwaartekracht_richting = 1            # (omkeerder) zwaartekracht weer gewoon omlaag


def drink(sp):
    """Pijltje omlaag: drink je brouwsel op. Geeft True als er iets in de ketel zat."""
    if not sp._ch_ketel:
        return False
    rec = recept(sp._ch_ketel)
    _uitgewerkt(sp)
    sp._ch_actief = rec
    sp._ch_krachten = krachten_van(rec)
    sp._ch_tijd = DUUR
    sp._ch_schild = _telling(sp, "paars")
    sp._ch_kracht = _telling(sp, "sterk")
    sp._ch_bel = 1 if heeft(sp, "Zeepbel") else 0
    sp._ch_ketel = []
    nieuwe = [k for k in sp._ch_krachten if k not in sp._ch_krachten_ontdekt]
    sp._ch_krachten_ontdekt.extend(nieuwe)
    if nieuwe:
        sp._ch_melding = "NIEUWE SUPERKRACHT: " + ", ".join(nieuwe) + "!"
    elif rec not in sp._ch_ontdekt:
        sp._ch_melding = "Nieuw recept: " + naam(rec) + "!"
    else:
        sp._ch_melding = naam(rec)
    if rec not in sp._ch_ontdekt:
        sp._ch_ontdekt.append(rec)
    sp._ch_melding_tijd = 150
    cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
    for i, d in enumerate(DRANKEN):
        for j in range(rec[i] * 4):
            h = math.radians(i * 60 + j * 22)
            sp._ch_bubbels.append([cx, cy, math.cos(h) * 3, math.sin(h) * 3, 26, RGB[d]])
    return True


def _vast(p):
    return getattr(p, "vast", True) and not getattr(p, "is_schuin", False)


def _golf(sp):
    """Een schokgolf vanaf je voeten (stampgolf en aardbeving)."""
    sp._ch_golven.append({"x": sp.x + sp.breedte / 2, "y": sp.y, "r": 0})


def stap(sp, platforms):
    """Elke stap: brouwsel uitwerken, superkrachten, grootte bijhouden, bubbels."""
    sp._ch_t += 1
    sp._ch_platforms = platforms             # (voor de flitser)
    if sp._ch_tijd > 0:
        sp._ch_tijd -= 1
        if sp._ch_tijd == 0:
            _uitgewerkt(sp)                  # het brouwsel is uitgewerkt
    doel = 1 + GROOT_PER * _telling(sp, "geel")
    if abs(sp.grootte_factor - doel) > 0.001:
        sp.zet_grootte(doel, 0)
    if sp.staat_op_grond:
        sp._ch_extra = 2 if heeft(sp, "Wolkensprong") else 0
        sp._ch_lucht_truc = True
        sp._ch_laatst = (sp.x, sp.y)         # zeepbel: hier stond je veilig
        # Stampgolf: hard geland? Dan een schokgolf
        if heeft(sp, "Stampgolf") and sp._ch_valsnelheid >= STAMP_SNELHEID:
            _golf(sp)
        # Stuiterschoenen: je stuitert vanzelf weer omhoog
        if heeft(sp, "Stuiterschoenen"):
            sp.snelheid_y = (SPRING_KRACHT + sp.sprong_bonus) * STUITER * sp.zwaartekracht_richting
        sp._ch_valsnelheid = 0
    else:
        sp._ch_valsnelheid = max(0, -sp.snelheid_y * sp.zwaartekracht_richting)
    # Aardbeving: elke 2 seconden, als je op de grond staat
    if heeft(sp, "Aardbeving") and sp.staat_op_grond and sp._ch_t % BEVING_TIJD == 0:
        _golf(sp)
    # Vuurballen: vanzelf schieten
    if heeft(sp, "Vuurballen"):
        sp._ch_vuur -= 1
        if sp._ch_vuur <= 0:
            sp._ch_vuur = VUUR_TIJD
            sp._ch_vuurbal_nieuw = True
    # Sterrenkracht: je bent onkwetsbaar
    if heeft(sp, "Sterrenkracht"):
        sp.onkwetsbaar_timer = max(sp.onkwetsbaar_timer, 2)
    # Zeepbel: in een kuil gevallen? Zweef terug naar waar je stond
    if sp._ch_bel > 0 and sp.y < -20 and sp._ch_laatst is not None:
        sp._ch_bel -= 1
        sp.x, sp.y = sp._ch_laatst
        sp.y += 60
        sp.snelheid_y = 0
        sp._ch_melding = "Zeepbel: gered!"
        sp._ch_melding_tijd = 90
    if sp._ch_dash > 0:
        sp._ch_dash -= 1
    for g in sp._ch_golven:
        if g["r"] > 0:
            g["r"] += 8                      # de golf wordt groter (om te zien)
    sp._ch_golven = [g for g in sp._ch_golven if g["r"] < GOLF_BEREIK]
    if sp._ch_melding_tijd > 0:
        sp._ch_melding_tijd -= 1
    # Bubbeltjes boven je hoofd zolang een brouwsel werkt
    if sp._ch_actief is not None and sp._ch_t % 6 == 0:
        kleuren = [d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]
        kl = RGB[kleuren[(sp._ch_t // 6) % len(kleuren)]]
        sp._ch_bubbels.append([sp.x + sp.breedte / 2 + ((sp._ch_t * 7) % 20) - 10,
                               sp.y + sp.hoogte, 0, 1.0, 30, kl])
    for b in sp._ch_bubbels:
        b[0] += b[2]
        b[1] += b[3]
        b[4] -= 1
    sp._ch_bubbels = [b for b in sp._ch_bubbels if b[4] > 0]


def loop(sp, L, R, snelheid):
    """Lopen: rendrank = sneller, luchtdash = zoef!"""
    if sp._ch_dash > 0:
        sp.snelheid_x = DASH_SNELHEID * (1 if sp.kijkt_rechts else -1)
        return
    loop_snel = snelheid * (1 + SNEL_PER * _telling(sp, "groen"))
    if L and not R:
        sp.snelheid_x = -loop_snel
        sp.kijkt_rechts = False
    elif R and not L:
        sp.snelheid_x = loop_snel
        sp.kijkt_rechts = True
    else:
        sp.snelheid_x = 0


def zwaartekracht(sp, richting):
    if sp._ch_dash > 0:
        sp.snelheid_y = 0                    # tijdens een dash vlieg je recht vooruit
        return
    licht = max(0.28, 1 - LICHT_PER * _telling(sp, "blauw"))
    sp.snelheid_y -= ZWAARTEKRACHT * licht * richting
    if heeft(sp, "Parachute") and sp.snelheid_y * richting < -PARACHUTE_VAL:
        sp.snelheid_y = -PARACHUTE_VAL * richting


def _vrij(sp, x, y):
    """Past de speler op plek (x, y) zonder in een blok te zitten?"""
    for p in sp._ch_platforms:
        if (_vast(p) and x < p.x + p.breedte and x + sp.breedte > p.x
                and y < p.y + p.hoogte and y + sp.hoogte > p.y):
            return False
    return True


def spring(sp):
    kracht = (SPRING_KRACHT + sp.sprong_bonus) * (1 + SPRONG_PER * _telling(sp, "rood")) * sp.zwaartekracht_richting
    if sp.staat_op_grond:
        sp.snelheid_y = kracht * (RAKET if heeft(sp, "Raketsprong") else 1)
        return
    if sp._ch_extra > 0:                     # wolkensprong
        sp._ch_extra -= 1
        sp.snelheid_y = kracht * 0.9
        for i in range(6):
            sp._ch_bubbels.append([sp.x + sp.breedte / 2 + (i - 2.5) * 4, sp.y, (i - 2.5) * 0.5, -1.5, 16,
                                   (240, 240, 250)])
        return
    if not sp._ch_lucht_truc:
        return
    k = 1 if sp.kijkt_rechts else -1
    if heeft(sp, "Luchtdash"):
        sp._ch_lucht_truc = False
        sp._ch_dash = DASH_TIJD
    elif heeft(sp, "Flitser"):
        # Zoek de verste vrije plek vooruit (hoogstens FLITS_AFSTAND ver)
        for afstand in range(FLITS_AFSTAND, 0, -10):
            if _vrij(sp, sp.x + k * afstand, sp.y):
                sp._ch_lucht_truc = False
                for i in range(8):
                    sp._ch_bubbels.append([sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2,
                                           math.cos(i * 0.8) * 2, math.sin(i * 0.8) * 2, 20, RGB["paars"]])
                sp.x += k * afstand
                break
    elif heeft(sp, "Omkeerder"):
        sp._ch_lucht_truc = False
        sp.zwaartekracht_richting *= -1
        sp.snelheid_y = 0


def bescherm(sp):
    """Word je geraakt en heb je een schild van paarse drank? Dan houdt het de klap tegen."""
    if sp._ch_schild > 0:
        sp._ch_schild -= 1
        sp.onkwetsbaar_timer = 45
        return True
    return False


def wereld(sp, vijanden):
    """Wat doen je superkrachten met de monsters?
    Geeft (monsters die weg moeten, spikes die weg moeten, nieuwe vuurbal (x, y, richting) of None)."""
    monsters_weg, spikes_weg = [], []
    for v in vijanden:
        if getattr(v, "is_spike", False):
            if heeft(sp, "Stekelpantser") and v.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                spikes_weg.append(v)             # stekelpantser: de spike breekt
            continue
        # Nieuwe schokgolven (stampgolf, aardbeving) raken monsters dichtbij
        geraakt = any(g["r"] == 0 and abs(v.x + v.breedte / 2 - g["x"]) < GOLF_BEREIK
                      and abs(v.y - g["y"]) < 60 for g in sp._ch_golven)
        if not geraakt and v.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
            if heeft(sp, "Sterrenkracht"):
                geraakt = True
            elif not heeft(sp, "Spook") and sp._ch_kracht > 0:
                sp._ch_kracht -= 1               # krachtdrank: omver gelopen!
                geraakt = True
        if geraakt:
            monsters_weg.append(v)
    for g in sp._ch_golven:
        g["r"] = max(g["r"], 1)                  # een golf raakt maar 1 keer (daarna groeit hij alleen)
    vuurbal = None
    if sp._ch_vuurbal_nieuw:
        sp._ch_vuurbal_nieuw = False
        k = 1 if sp.kijkt_rechts else -1
        vuurbal = (sp.x + sp.breedte + 4 if k > 0 else sp.x - 4, sp.y + sp.hoogte / 2, k)
    return monsters_weg, spikes_weg, vuurbal


def veilig(sp, v):
    """Kan dit monster je nu geen pijn doen? (spook)"""
    return heeft(sp, "Spook") and not getattr(v, "is_spike", False)


def monster_stil(sp):
    """Tijdrem: monsters bewegen maar 1 op de 3 stapjes."""
    return heeft(sp, "Tijdrem") and sp._ch_t % 3 != 0


# ===========================================================================
# Tekenen
# ===========================================================================
def _mengkleur(dranken):
    if not dranken:
        return (120, 120, 130)
    r = sum(RGB[d][0] for d in dranken) // len(dranken)
    g = sum(RGB[d][1] for d in dranken) // len(dranken)
    b = sum(RGB[d][2] for d in dranken) // len(dranken)
    return (r, g, b)


def teken(sp):
    t = sp._ch_t
    for x, y, vx, vy, leven, kleur in sp._ch_bubbels:
        arcade.draw_circle_outline(x, y, 2 + (30 - leven) / 8, (kleur[0], kleur[1], kleur[2], min(255, leven * 9)), 2)
    for g in sp._ch_golven:                      # schokgolven
        arcade.draw_ellipse_outline(g["x"], g["y"] + 4, g["r"] * 2 + 4, 16 + g["r"] * 0.1, (230, 190, 90), 3)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx = x + w / 2
    k = 1 if sp.kijkt_rechts else -1
    # Gloed zolang een brouwsel werkt (in de mengkleur van het recept)
    if sp._ch_actief is not None:
        dranken = [d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]
        mk = _mengkleur(dranken)
        puls = 3 * math.sin(t * 0.2)
        arcade.draw_ellipse_filled(cx, y + h / 2, w + 16 + puls, h + 16 + puls, (mk[0], mk[1], mk[2], 70))
    # Superkracht-extraatjes om je heen
    if heeft(sp, "Sterrenkracht"):
        for i in range(5):
            h2 = t * 0.1 + i * 1.2566
            arcade.draw_circle_filled(cx + math.cos(h2) * (w * 0.8), y + h / 2 + math.sin(h2) * (h * 0.8), 3,
                                      (255, 230, 80))
    if sp._ch_bel > 0:
        arcade.draw_circle_outline(cx, y + h / 2, max(w, h) * 0.85, (180, 230, 255, 160), 2)
    if heeft(sp, "Parachute") and not sp.staat_op_grond and sp.snelheid_y < 0:
        arcade.draw_arc_filled(cx, y + h + 22, w * 2, 26, (250, 210, 40), 0, 180)
        arcade.draw_line(cx - w, y + h + 22, x + 2, y + h, (80, 80, 80), 1)
        arcade.draw_line(cx + w, y + h + 22, x + w - 2, y + h, (80, 80, 80), 1)
    if sp._ch_dash > 0:
        for i in range(3):
            arcade.draw_line(cx - k * (w + i * 8), y + 6 + i * 8, cx - k * (w + 20 + i * 8), y + 6 + i * 8,
                             (200, 230, 255), 2)
    # Witte labjas
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.65, (245, 245, 250))
    arcade.draw_line(cx, y + 2, cx, y + h * 0.6, (200, 200, 210), 1)
    # Hoofd met een wilde haardos en een veiligheidsbril
    arcade.draw_lrbt_rectangle_filled(x + 4, x + w - 4, y + h * 0.6, y + h - 4, (240, 205, 170))
    for i in range(5):
        hx = x + 3 + i * (w - 6) / 4
        arcade.draw_triangle_filled(hx - 4, y + h - 5, hx + 4, y + h - 5, hx, y + h + 3, (230, 230, 235))
    for dx in (-5, 5):
        arcade.draw_circle_filled(cx + dx + k, y + h * 0.78, 4, (160, 220, 255))
        arcade.draw_circle_outline(cx + dx + k, y + h * 0.78, 4, (60, 60, 70), 1)
        arcade.draw_circle_filled(cx + dx + k * 2, y + h * 0.78, 1.5, (20, 20, 30))
    # Een kolf in de hand, gevuld met wat er in de ketel zit
    fx = x + w + 4 if k > 0 else x - 4
    arcade.draw_circle_filled(fx, y + h * 0.3, 6, (220, 230, 240))
    vul = _mengkleur(sp._ch_ketel)
    if sp._ch_ketel:
        arcade.draw_circle_filled(fx, y + h * 0.28, 4.5, vul)
    arcade.draw_lrbt_rectangle_filled(fx - 2, fx + 2, y + h * 0.3 + 4, y + h * 0.3 + 10, (220, 230, 240))


def teken_hud(sp, x, y):
    """Balkje bovenin: de ketel, het brouwsel dat werkt, je superkrachten en je receptenboekje."""
    arcade.draw_lrbt_rectangle_filled(x - 260, x + 260, y - 46, y + 28, (0, 0, 0, 155))
    # Flessen 1-6
    for i, d in enumerate(DRANKEN):
        l = x - 252 + i * 42
        arcade.draw_circle_filled(l + 10, y + 12, 8, RGB[d])
        arcade.draw_text(str(i + 1), l + 10, y + 7, (0, 0, 0) if d in ("geel", "sterk") else (255, 255, 255), 9,
                         bold=True, anchor_x="center")
        arcade.draw_text(UITLEG[d], l + 10, y - 7, (200, 200, 200), 7, anchor_x="center")
    # De ketel: 4 plekjes
    kx = x + 20
    arcade.draw_text("ketel:", kx - 2, y + 7, (230, 230, 230), 10)
    for i in range(KETEL_MAX):
        vx = kx + 45 + i * 20
        if i < len(sp._ch_ketel):
            arcade.draw_circle_filled(vx, y + 12, 7, RGB[sp._ch_ketel[i]])
        arcade.draw_circle_outline(vx, y + 12, 7, (180, 180, 190), 1)
    arcade.draw_text("omlaag = drinken", kx + 125, y + 7, (200, 200, 200), 9)
    # Brouwsel dat werkt (met tijdbalk) + receptenboekje
    if sp._ch_actief is not None:
        arcade.draw_lrbt_rectangle_filled(x - 252, x - 252 + 250 * sp._ch_tijd / DUUR, y - 26, y - 20,
                                          _mengkleur([d for d, n in zip(DRANKEN, sp._ch_actief) for _ in range(n)]))
    arcade.draw_text("Recepten: %d / %d   Superkrachten: %d / %d" % (
        len(sp._ch_ontdekt), AANTAL_RECEPTEN, len(sp._ch_krachten_ontdekt), AANTAL_KRACHTEN),
        x + 20, y - 24, (255, 230, 120), 9, bold=True)
    # De superkrachten die nu werken
    if sp._ch_krachten:
        arcade.draw_text("Kracht: " + ", ".join(sp._ch_krachten), x, y - 41, (150, 255, 200), 9,
                         bold=True, anchor_x="center")
    if sp._ch_melding_tijd > 0:
        arcade.draw_text(sp._ch_melding, x, y - 66, (255, 240, 150), 13, bold=True, anchor_x="center")

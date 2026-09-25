# fabriek.py
# De FABRIEK-BAAS: bouw een fabriek die trappen, bruggen en liften voor je maakt!
#
#  Toets 1 : MIJN             (4) - maakt grondstoffen: steen, hout, steen, ijzer (steeds deze volgorde)
#  Toets 2 : LOPENDE BAND     (1) - vervoert blokjes (en jou!) de kant op die je kijkt
#  Toets 3 : TRAPPENBOUWER    (3) - STEEN   -> een traptree erbij
#  Toets 4 : BRUGBOUWER       (3) - HOUT    -> een stuk brug erbij
#  Toets 5 : TANDWIEL-MACHINE (3) - IJZER   -> een nieuw tandwiel
#  Toets 6 : WINDMOLEN        (3) - geeft STROOM aan machines in de buurt
#  Toets 7 : SMELTERIJ        (4) - 2 IJZER -> 1 STAAL
#  Toets 8 : LIFT             (4) - STAAL   -> de lift gaat een verdieping hoger
#  Toets 9 : KANON            (3) - elk blokje wordt een kogel tegen monsters
#  Omlaag  : SLOPEN           - haal de machine voor je (of onder je) weg, tandwielen terug
# (tussen haakjes: zoveel tandwielen kost het)
#
# STROOM: machines werken alleen als er een windmolen in de buurt staat (240 pixels).
#   Een molen geeft 4 stroom. Mijn, bouwers, lift en kanon gebruiken 1, de smelterij 2.
#   Te weinig stroom? Dan werken de machines langzamer. Geen stroom? Dan staan ze stil.
# DOORGEVEN: krijgt een machine een blokje dat hij niet wil (of is hij vol),
#   dan geeft hij het door naar de andere kant. Zo kun je machines achter elkaar zetten:
#   [MIJN] -> band -> [BRUG: pakt hout] -> band -> [TRAP: pakt steen] -> band -> [TANDWIEL: pakt ijzer]
# Alles is vast: geen toeval.

import math
import arcade
from platforms import Platform

TANDWIELEN = 20           # zoveel tandwielen heb je aan het begin
KOST = {"mijn": 4, "band": 1, "trap": 3, "brug": 3, "tandwiel": 3,
        "molen": 3, "smelterij": 4, "lift": 4, "kanon": 3}
TOETSEN = ["mijn", "band", "trap", "brug", "tandwiel", "molen", "smelterij", "lift", "kanon"]
NAAM = {"mijn": "mijn", "band": "band", "trap": "trap", "brug": "brug", "tandwiel": "tandwiel",
        "molen": "molen", "smelterij": "smelter", "lift": "lift", "kanon": "kanon"}
STROOM_NODIG = {"mijn": 1, "trap": 1, "brug": 1, "tandwiel": 1, "smelterij": 2, "lift": 1, "kanon": 1}
MOLEN_STROOM = 4          # zoveel stroom geeft een windmolen
STROOM_BEREIK = 240       # zo ver reikt de stroom van een molen (opzij)
MIJN_VOLGORDE = ["steen", "hout", "steen", "ijzer"]
STOF_KLEUR = {"steen": (150, 150, 155), "hout": (170, 110, 55), "ijzer": (80, 100, 140),
              "staal": (215, 225, 240)}
WIL = {"trap": ("steen",), "brug": ("hout",), "tandwiel": ("ijzer",), "smelterij": ("ijzer",),
       "lift": ("staal",)}   # (het kanon wil alles)
MACHINE = 40              # machines zijn 40 x 40
BAND_BREEDTE = 64
BAND_HOOGTE = 10
BAND_SNELHEID = 2
MIJN_TIJD = 40            # met volle stroom elke 40 stapjes (2/3 seconde) een blokje
VERWERK_TIJD = 20         # zo lang is een machine bezig met een blokje (met volle stroom)
BLOKJE = 12               # blokjes zijn 12 x 12
MAX_BLOKJES = 40
TREDE_BREEDTE = 32
TREDE_HOOGTE = 24
MAX_TREDEN = 8
BRUG_STUK = 40
BRUG_DIKTE = 12
MAX_BRUG = 10
IJZER_PER_STAAL = 2
MAX_VERDIEPING = 6        # de lift gaat hoogstens 6 x 40 = 240 pixels omhoog
VERDIEPING = 40
LIFT_SNELHEID = 1.5
MAX_MUNITIE = 5
KANON_BEREIK = 450
KANON_RUST = 30


class FabriekDeel(Platform):
    """Alles wat de fabriek neerzet of bouwt: je kunt erop staan."""

    is_fabriek = True

    def __init__(self, soort, x, y, breedte, hoogte, richting=1):
        super().__init__(x, y, breedte, hoogte)
        self.soort = soort            # machine, "band", "trede", "brugstuk" of "liftplank"
        self.richting = richting      # 1 = rechts, -1 = links
        self.dx = BAND_SNELHEID * richting if soort == "band" else 0   # op een band rijd je mee
        self.werk = 0                 # mijn: hoe ver het volgende blokje al is
        self.teller = 0               # mijn: welk blokje uit de volgorde is het volgende
        self.bezig = 0                # machine: nog even bezig met het vorige blokje
        self.stroom = 0               # 0 = geen stroom, 1 = volle stroom (ertussen = langzamer)
        self.molen = None             # de molen die hem stroom geeft
        self.gebouwd = []             # bouwer: wat hij al gebouwd heeft
        self.voorraad = 0             # smelterij: ijzer erin
        self.munitie = 0              # kanon: blokjes erin
        self.rust = 0                 # kanon: even wachten na een schot
        self.verdiepingen = 0         # lift: zo hoog kan hij
        self.plank = None             # lift: de plank die op en neer gaat
        self.lift_op = 1              # lift: gaat de plank omhoog (1) of omlaag (-1)?
        self.glim = 0                 # glimt even als er iets gemaakt is
        self.t = 0

    def teken(self):
        _teken_deel(self)


def reset(sp):
    sp._fb_tandwielen = TANDWIELEN
    sp._fb_delen = []         # alle FabriekDelen (machines, banden en wat ze bouwden)
    sp._fb_blokjes = []       # {"x", "y", "vy", "stof"}
    sp._fb_schoten = []       # kanonschoten die het spel nog moet afvuren (x, y, richting)
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


def _staat_stevig(x, y, w, platforms):
    """Is er onder de HELE breedte (van x tot x+w) grond op hoogte y? (Niet half over een rand.)
    De grond mag uit meerdere stukjes bestaan, zolang er nergens een gat zit."""
    stukken = [p for p in platforms if _vast(p) and abs(p.y + p.hoogte - y) < 1]
    for i in range(int(w) + 1):
        px = x + i
        if not any(p.x <= px <= p.x + p.breedte for p in stukken):
            return False                         # hier zit niks onder: hij hangt over de rand
    return True


def is_machine(d):
    return d.soort in KOST and d.soort != "band"


def plaats(sp, soort, platforms):
    """Toets 1-9: zet een machine of band vlak voor je neer."""
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
    if not _staat_stevig(x, y, w, platforms):
        _meld(sp, "Dat hangt over de rand!")
        return False
    sp._fb_tandwielen -= KOST[soort]
    deel = FabriekDeel(soort, x, y, w, h, k)
    sp._fb_delen.append(deel)
    if soort == "lift":
        deel.plank = FabriekDeel("liftplank", x, y + MACHINE, MACHINE, 8, k)
        sp._fb_delen.append(deel.plank)
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
    if d.plank is not None and d.plank in sp._fb_delen:
        sp._fb_delen.remove(d.plank)             # de liftplank gaat mee
    sp._fb_tandwielen += KOST[d.soort]
    return True


# ---------------------------------------------------------------------------
# Stroom
# ---------------------------------------------------------------------------
def _verdeel_stroom(delen):
    """Elke machine krijgt stroom van de dichtstbijzijnde molen (binnen het bereik).
    Vragen te veel machines stroom van 1 molen, dan krijgen ze allemaal een beetje minder."""
    molens = [d for d in delen if d.soort == "molen"]
    vraag = {id(m): 0 for m in molens}
    for d in delen:
        d.molen = None
        if d.soort not in STROOM_NODIG:
            continue
        cx = d.x + d.breedte / 2
        dichtbij = [m for m in molens if abs(m.x + MACHINE / 2 - cx) <= STROOM_BEREIK and abs(m.y - d.y) <= 160]
        if dichtbij:
            d.molen = min(dichtbij, key=lambda m: (abs(m.x - d.x), m.x))
            vraag[id(d.molen)] += STROOM_NODIG[d.soort]
    for d in delen:
        if d.soort in STROOM_NODIG:
            d.stroom = 0 if d.molen is None else min(1.0, MOLEN_STROOM / vraag[id(d.molen)])


def stroom_info(sp):
    """(gebruikt, aanbod) van alle molens samen, voor het balkje bovenin."""
    molens = [d for d in sp._fb_delen if d.soort == "molen"]
    gebruikt = sum(STROOM_NODIG[d.soort] for d in sp._fb_delen if d.soort in STROOM_NODIG and d.molen)
    return gebruikt, len(molens) * MOLEN_STROOM


# ---------------------------------------------------------------------------
# Machines aan het werk
# ---------------------------------------------------------------------------
def _wil(machine, stof):
    """Wil deze machine dit blokje hebben?"""
    s = machine.soort
    if s == "kanon":
        return machine.munitie < MAX_MUNITIE
    if s == "trap" and len(machine.gebouwd) >= MAX_TREDEN:
        return False
    if s == "brug" and len(machine.gebouwd) >= MAX_BRUG:
        return False
    if s == "lift" and machine.verdiepingen >= MAX_VERDIEPING:
        return False
    return stof in WIL.get(s, ())


def _bouw(sp, bouwer):
    """Een bouwer krijgt een blokje: bouw een stukje trap of brug erbij."""
    k = bouwer.richting
    i = len(bouwer.gebouwd)
    if bouwer.soort == "trap":
        w, h = TREDE_BREEDTE, TREDE_HOOGTE * (i + 1)
        x = bouwer.x + MACHINE + i * w if k > 0 else bouwer.x - (i + 1) * w
        stuk = FabriekDeel("trede", x, bouwer.y, w, h, k)
    else:
        w, h = BRUG_STUK, BRUG_DIKTE
        x = bouwer.x + MACHINE + i * w if k > 0 else bouwer.x - (i + 1) * w
        stuk = FabriekDeel("brugstuk", x, bouwer.y + MACHINE - h, w, h, k)
    bouwer.gebouwd.append(stuk)
    sp._fb_delen.append(stuk)


def _uitgang_vrij(sp, x, y):
    return not any(abs(b["x"] - x) < BLOKJE and abs(b["y"] - y) < 20 for b in sp._fb_blokjes)


def _maak_blokje(sp, machine, stof):
    """Een machine gooit een blokje naar voren. Geeft False als de uitgang nog vol ligt."""
    bx = machine.x + MACHINE + 1 if machine.richting > 0 else machine.x - BLOKJE - 1
    by = machine.y + 14
    if len(sp._fb_blokjes) >= MAX_BLOKJES or not _uitgang_vrij(sp, bx, by):
        return False
    sp._fb_blokjes.append({"x": bx, "y": by, "vy": 0, "stof": stof})
    return True


def _verwerk(sp, machine, stof):
    """De machine pakt het blokje en doet er iets mee."""
    s = machine.soort
    machine.bezig = VERWERK_TIJD
    machine.glim = 20
    if s in ("trap", "brug"):
        _bouw(sp, machine)
    elif s == "tandwiel":
        sp._fb_tandwielen += 1
    elif s == "smelterij":
        machine.voorraad += 1
    elif s == "lift":
        machine.verdiepingen += 1
    elif s == "kanon":
        machine.munitie += 1


def _geef_door(b, machine):
    """Dit blokje wil de machine niet: het komt er aan de andere kant weer uit."""
    if b["x"] + BLOKJE / 2 < machine.x + MACHINE / 2:
        b["x"] = machine.x + MACHINE + 1          # kwam van links: rechts eruit
    else:
        b["x"] = machine.x - BLOKJE - 1            # kwam van rechts: links eruit
    b["vy"] = 0


def stap(sp, platforms):
    """Elke stap: stroom verdelen, mijnen maken blokjes, blokjes rijden en vallen, machines werken."""
    sp._fb_t += 1
    if sp._fb_melding_tijd > 0:
        sp._fb_melding_tijd -= 1
    delen = sp._fb_delen
    _verdeel_stroom(delen)
    for d in delen:
        d.t += 1
        if d.glim > 0:
            d.glim -= 1
        if d.bezig > 0:
            d.bezig -= d.stroom                    # met minder stroom duurt het langer
    # Mijnen: grondstoffen maken (sneller met meer stroom)
    for m in [d for d in delen if d.soort == "mijn"]:
        m.werk = min(MIJN_TIJD, m.werk + m.stroom)
        if m.werk >= MIJN_TIJD and _maak_blokje(sp, m, MIJN_VOLGORDE[m.teller % len(MIJN_VOLGORDE)]):
            m.werk = 0
            m.teller += 1
    # Smelterij: 2 ijzer -> 1 staal
    for s in [d for d in delen if d.soort == "smelterij"]:
        if s.voorraad >= IJZER_PER_STAAL and s.stroom > 0 and _maak_blokje(sp, s, "staal"):
            s.voorraad -= IJZER_PER_STAAL
    # Lift: de plank gaat op en neer (alleen met stroom)
    for l in [d for d in delen if d.soort == "lift"]:
        p = l.plank
        top = l.y + MACHINE + l.verdiepingen * VERDIEPING
        p.x = l.x
        if l.stroom > 0 and l.verdiepingen > 0:
            p.y += LIFT_SNELHEID * l.stroom * l.lift_op
            if p.y >= top:
                p.y, l.lift_op = top, -1
            elif p.y <= l.y + MACHINE:
                p.y, l.lift_op = l.y + MACHINE, 1
        p.y = max(l.y + MACHINE, min(top, p.y))
    # Kanon: schiet als er munitie is (het spel kijkt of er een monster voor staat)
    for k in [d for d in delen if d.soort == "kanon"]:
        if k.rust > 0:
            k.rust -= 1
    # Blokjes: meerijden op een band, anders vallen tot ze ergens op liggen
    alles = [p for p in platforms if _vast(p) and not getattr(p, "is_fabriek", False)] + delen
    machines = [d for d in delen if is_machine(d)]
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
        # In een machine? Pakken (als hij het wil), wachten (als hij bezig is) of doorgeven
        for m in machines:
            if not _overlapt(b["x"], b["y"], BLOKJE, BLOKJE, m):
                continue
            if _wil(m, b["stof"]):
                if m.stroom > 0 and m.bezig <= 0:
                    _verwerk(sp, m, b["stof"])
                    klaar.append(b)
                # anders: even wachten tot de machine klaar is (of stroom krijgt)
            else:
                _geef_door(b, m)
            break
    sp._fb_blokjes = [b for b in sp._fb_blokjes if b not in klaar]


def kanon_schoten(sp, vijanden):
    """Kanonnen met munitie en stroom schieten op een monster voor ze. Geeft [(x, y, richting)]."""
    schoten = []
    for k in [d for d in sp._fb_delen if d.soort == "kanon"]:
        if k.munitie <= 0 or k.stroom <= 0 or k.rust > 0:
            continue
        r = k.richting
        loop_x = k.x + MACHINE / 2
        doel = any(not getattr(v, "is_spike", False) and 0 < (v.x + v.breedte / 2 - loop_x) * r <= KANON_BEREIK
                   and abs(v.y - k.y) < 60 for v in vijanden)
        if doel:
            k.munitie -= 1
            k.rust = KANON_RUST
            k.glim = 10
            schoten.append((k.x + MACHINE + 4 if r > 0 else k.x - 4, k.y + 26, r))
    return schoten


# ===========================================================================
# Tekenen
# ===========================================================================
def _stroomlampje(d, x, y, w, h):
    """Rechtsboven: groen = stroom, oranje = te weinig, rood = geen stroom."""
    if d.soort not in STROOM_NODIG:
        return
    kleur = (80, 230, 90) if d.stroom >= 1 else (250, 170, 40) if d.stroom > 0 else (230, 50, 50)
    arcade.draw_circle_filled(x + w - 5, y + h - 5, 3, kleur)


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
        return
    if d.soort == "trede":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (170, 90, 60))
        for ry in range(int(y), int(y + h), 12):
            arcade.draw_line(x, ry, x + w, ry, (120, 60, 40), 1)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 4, y + h, (200, 120, 80))
        return
    if d.soort == "brugstuk":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 100, 55))
        for i in range(4):
            arcade.draw_line(x + i * 10, y, x + i * 10, y + h, (100, 65, 35), 1)
        arcade.draw_line(x, y + h + 10, x + w, y + h + 10, (120, 120, 130), 2)             # leuning
        return
    if d.soort == "liftplank":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (200, 210, 225))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 90, 100), 1)
        return
    # Kabel naar de molen (als hij stroom krijgt)
    if d.molen is not None:
        mx = d.molen.x + MACHINE / 2
        arcade.draw_line(x + w / 2, y + h, mx, d.molen.y + MACHINE + 20, (250, 220, 60, 110), 1)
    if d.soort == "mijn":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (110, 110, 120))
        arcade.draw_lrbt_rectangle_filled(x + 26, x + 34, y + h, y + h + 12, (80, 80, 90))    # schoorsteen
        if d.stroom > 0:
            rook = (d.t // 8) % 4
            arcade.draw_circle_filled(x + 30 + rook, y + h + 16 + rook * 3, 3 + rook, (190, 190, 190, 160 - rook * 30))
        uit = x + w if k > 0 else x
        arcade.draw_triangle_filled(uit, y + 10, uit, y + 24, uit + k * 6, y + 17, (230, 190, 60))
        boor = (d.werk % 20) / 20 * 6
        arcade.draw_triangle_filled(x + 12, y + 30, x + 22, y + 30, x + 17, y + 14 + boor, (200, 200, 210))
        # welk blokje komt er straks uit?
        volgende = MIJN_VOLGORDE[d.teller % len(MIJN_VOLGORDE)]
        arcade.draw_lrbt_rectangle_filled(x + 4, x + 10, y + 4, y + 10, STOF_KLEUR[volgende])
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
        wil = WIL[d.soort][0]
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + h - 9, y + h - 3, STOF_KLEUR[wil])   # wat hij wil
        arcade.draw_text(str(len(d.gebouwd)), x + w / 2, y + 1, (255, 255, 255), 8, anchor_x="center")
    elif d.soort == "tandwiel":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 120, 60))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 40, 40), 2)
        hoek = d.t * 0.05 * (1 if d.stroom > 0 else 0)
        cx, cy = x + w / 2, y + h / 2 + 3
        for i in range(8):
            a = hoek + i * math.pi / 4
            arcade.draw_circle_filled(cx + math.cos(a) * 10, cy + math.sin(a) * 10, 3, (250, 210, 80))
        arcade.draw_circle_filled(cx, cy, 9, (250, 210, 80))
        arcade.draw_circle_filled(cx, cy, 3, (150, 120, 60))
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + h - 9, y + h - 3, STOF_KLEUR["ijzer"])
        if d.glim > 0:
            arcade.draw_text("+1", cx, y + h + 4 + (20 - d.glim), (250, 210, 80, d.glim * 12), 12,
                             bold=True, anchor_x="center")
    elif d.soort == "molen":
        cx, top = x + w / 2, y + h + 20
        arcade.draw_triangle_filled(x + 8, y, x + w - 8, y, cx, top, (230, 230, 235))
        arcade.draw_lrbt_rectangle_filled(x + 14, x + w - 14, y, y + 12, (150, 90, 60))       # deurtje
        hoek = d.t * 0.08
        for i in range(4):
            a = hoek + i * math.pi / 2
            arcade.draw_line(cx, top, cx + math.cos(a) * 22, top + math.sin(a) * 22, (120, 80, 50), 4)
            arcade.draw_line(cx + math.cos(a) * 8, top + math.sin(a) * 8,
                             cx + math.cos(a) * 22, top + math.sin(a) * 22, (240, 240, 245), 3)
        arcade.draw_circle_filled(cx, top, 3, (80, 60, 40))
    elif d.soort == "smelterij":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 60, 50))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 30, 30), 2)
        gloed = 180 + int(60 * math.sin(d.t * 0.2)) if d.stroom > 0 else 60
        arcade.draw_lrbt_rectangle_filled(x + 10, x + w - 10, y + 6, y + 20, (255, gloed // 2 + 60, 40))
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + h - 9, y + h - 3, STOF_KLEUR["ijzer"])
        for i in range(IJZER_PER_STAAL):
            arcade.draw_lrbt_rectangle_filled(x + 14 + i * 8, x + 19 + i * 8, y + h - 10, y + h - 5,
                                              STOF_KLEUR["ijzer"] if i < d.voorraad else (50, 40, 35))
    elif d.soort == "lift":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (120, 130, 150))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (50, 50, 60), 2)
        arcade.draw_triangle_filled(x + 12, y + 18, x + 28, y + 18, x + 20, y + 30, (240, 240, 250))
        arcade.draw_triangle_filled(x + 12, y + 14, x + 28, y + 14, x + 20, y + 4, (240, 240, 250))
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y + h - 9, y + h - 3, STOF_KLEUR["staal"])
        # de liftschacht
        top = y + h + d.verdiepingen * VERDIEPING
        if d.verdiepingen:
            arcade.draw_line(x + 2, y + h, x + 2, top + 8, (90, 90, 100), 2)
            arcade.draw_line(x + w - 2, y + h, x + w - 2, top + 8, (90, 90, 100), 2)
        arcade.draw_text(str(d.verdiepingen), x + w / 2, y + 1, (255, 255, 255), 8, anchor_x="center")
    elif d.soort == "kanon":
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 22, (70, 80, 70))
        loop = x + w / 2
        arcade.draw_lrbt_rectangle_filled(min(loop, loop + k * 26), max(loop, loop + k * 26), y + 20, y + 32,
                                          (50, 55, 50))
        arcade.draw_circle_filled(loop, y + 24, 10, (70, 80, 70))
        if d.glim > 0:
            arcade.draw_circle_filled(loop + k * 30, y + 26, 6 + d.glim / 2, (255, 200, 80, 200))
        for i in range(MAX_MUNITIE):
            arcade.draw_lrbt_rectangle_filled(x + 3 + i * 7, x + 8 + i * 7, y + 3, y + 8,
                                              (220, 200, 90) if i < d.munitie else (40, 45, 40))
    _stroomlampje(d, x, y, w, h)


def teken(sp):
    for b in sp._fb_blokjes:
        kleur = STOF_KLEUR[b["stof"]]
        arcade.draw_lrbt_rectangle_filled(b["x"], b["x"] + BLOKJE, b["y"], b["y"] + BLOKJE, kleur)
        arcade.draw_lrbt_rectangle_outline(b["x"], b["x"] + BLOKJE, b["y"], b["y"] + BLOKJE, (40, 40, 40), 1)
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
    arcade.draw_lrbt_rectangle_filled(x - 300, x + 300, y - 56, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Tandwielen: %d" % sp._fb_tandwielen, x - 292, y + 1, (250, 210, 80), 11, bold=True)
    gebruikt, aanbod = stroom_info(sp)
    kleur = (80, 230, 90) if gebruikt <= aanbod else (250, 170, 40)
    arcade.draw_text("Stroom: %d / %d" % (gebruikt, aanbod), x - 292, y - 26, kleur, 11, bold=True)
    for i, soort in enumerate(TOETSEN):
        rij, kol = divmod(i, 5)
        l = x - 150 + kol * 90
        b = y - rij * 26
        kan = sp._fb_tandwielen >= KOST[soort]
        arcade.draw_lrbt_rectangle_filled(l, l + 86, b, b + 18, (70, 110, 70) if kan else (60, 60, 60))
        arcade.draw_text("%d %s (%d)" % (i + 1, NAAM[soort], KOST[soort]), l + 43, b + 4,
                         (255, 255, 255) if kan else (140, 140, 140), 9, anchor_x="center")
    arcade.draw_text("omlaag = slopen", x + 222, y - 22, (200, 200, 200), 9)
    # Uitleg van de kleuren van de grondstoffen
    for i, stof in enumerate(("steen", "hout", "ijzer", "staal")):
        l = x - 292 + i * 70
        arcade.draw_lrbt_rectangle_filled(l, l + 10, y - 50, y - 40, STOF_KLEUR[stof])
        arcade.draw_text(stof, l + 14, y - 50, (230, 230, 230), 9)
    if sp._fb_melding_tijd > 0:
        arcade.draw_text(sp._fb_melding, x, y - 70, (250, 220, 150), 13, bold=True, anchor_x="center")

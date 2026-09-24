# portaalschieter.py
# De PORTAALSCHIETER: een poppetje met een portaal-pistool!
#
#  - Pijltje omlaag (1e keer): er komt een BLAUW portaal vlak voor je.
#  - Pijltje omlaag (2e keer): je SCHIET een ORANJE portaal weg. Het vliegt
#    vooruit tot het een muur raakt (dan plakt het op de muur), of het blijft
#    na een flink stuk in de lucht hangen.
#  - Loop je door het ene portaal, dan kom je uit het andere. Je vaart neem je mee!
#  - Nog eens drukken: je begint opnieuw met een nieuw blauw portaal.
#
# Alles is vast (geen toeval): hetzelfde doen geeft altijd hetzelfde resultaat.

import math
import arcade

BLAUW = (60, 150, 255)
ORANJE = (255, 150, 40)
PORTAAL_B = 16            # hoe breed een portaal is
PORTAAL_H = 80            # hoe hoog een portaal is
BLAUW_AFSTAND = 30        # zo ver voor je komt het blauwe portaal
KOGEL_SNELHEID = 14       # zo snel vliegt de oranje portaal-kogel
KOGEL_BEREIK = 450        # zo ver vliegt hij hoogstens (daarna blijft het portaal in de lucht hangen)
WACHT = 25                # zolang kun je na een teleport niet meteen weer teleporteren
UIT_SNELHEID = 4          # je komt minstens zo snel uit een portaal


def reset(sp):
    """Geen portalen, geen kogel: alles weer leeg."""
    sp._pt_blauw = None       # het blauwe portaal (of None)
    sp._pt_oranje = None      # het oranje portaal (of None)
    sp._pt_kogel = None       # de vliegende oranje kogel (of None)
    sp._pt_volgende = "blauw" # welk portaal je hierna maakt
    sp._pt_wacht = 0          # teller na een teleport
    sp._pt_t = 0              # tikt door voor de draaiende portalen


def _portaal(x, y, kant):
    """Een portaal: linkerkant x, onderkant y, en welke kant de opening op wijst (1 of -1)."""
    return {"x": x, "y": y, "kant": kant}


def schiet(sp):
    """Pijltje omlaag: blauw neerzetten, of oranje wegschieten."""
    richting = 1 if sp.kijkt_rechts else -1
    py = sp.y + sp.hoogte / 2 - PORTAAL_H / 2          # portaal staat op jouw hoogte
    if sp._pt_volgende == "blauw":
        if richting > 0:
            px = sp.x + sp.breedte + BLAUW_AFSTAND
        else:
            px = sp.x - BLAUW_AFSTAND - PORTAAL_B
        sp._pt_blauw = _portaal(px, py, richting)
        sp._pt_oranje = None                           # nieuwe ronde: oude oranje weg
        sp._pt_kogel = None
        sp._pt_volgende = "oranje"
    else:
        cx = sp.x + sp.breedte / 2
        sp._pt_kogel = {"x": cx, "y": sp.y + sp.hoogte / 2, "richting": richting,
                        "start": cx, "py": py}
        sp._pt_volgende = "blauw"


def _raakt_muur(x, y, platforms):
    """Raakt een puntje (x, y) een vast blok? Geeft dat blok terug, anders None."""
    for p in platforms:
        if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                and not getattr(p, "is_bouwblok", False)
                and p.x <= x <= p.x + p.breedte and p.y <= y <= p.y + p.hoogte):
            return p
    return None


def _overlapt(sp, pt):
    return (sp.x < pt["x"] + PORTAAL_B and sp.x + sp.breedte > pt["x"]
            and sp.y < pt["y"] + PORTAAL_H and sp.y + sp.hoogte > pt["y"])


def _kom_uit(sp, uit):
    """Zet de speler vlak naast het uitgangs-portaal, met vaart de goede kant op."""
    kant = uit["kant"]
    snel = max(abs(sp.snelheid_x), UIT_SNELHEID)
    sp.snelheid_x = snel * kant                        # je vaart neem je mee, de goede kant op
    sp.kijkt_rechts = kant > 0
    if kant > 0:
        sp.x = uit["x"] + PORTAAL_B + 2
    else:
        sp.x = uit["x"] - sp.breedte - 2
    sp.y = uit["y"] + PORTAAL_H / 2 - sp.hoogte / 2    # midden van het portaal
    sp._pt_wacht = WACHT


def stap(sp, platforms):
    """Elke stap: de kogel laten vliegen en kijken of je door een portaal loopt."""
    sp._pt_t += 1
    if sp._pt_wacht > 0:
        sp._pt_wacht -= 1
    # De oranje kogel vliegt (in kleine stapjes, zodat hij niet door dunne muren gaat)
    k = sp._pt_kogel
    if k is not None:
        for _ in range(KOGEL_SNELHEID // 2):
            k["x"] += 2 * k["richting"]
            muur = _raakt_muur(k["x"], k["y"], platforms)
            if muur is not None:
                # Tegen een muur: het portaal plakt op de muur en kijkt terug naar jou
                if k["richting"] > 0:
                    px = muur.x - PORTAAL_B
                else:
                    px = muur.x + muur.breedte
                sp._pt_oranje = _portaal(px, k["py"], -k["richting"])
                sp._pt_kogel = None
                break
            if abs(k["x"] - k["start"]) >= KOGEL_BEREIK:
                # Niks geraakt: het portaal blijft in de lucht hangen en kijkt vooruit
                px = k["x"] if k["richting"] > 0 else k["x"] - PORTAAL_B
                sp._pt_oranje = _portaal(px, k["py"], k["richting"])
                sp._pt_kogel = None
                break
    # Door een portaal lopen = teleporteren (alleen als ze er allebei zijn)
    b, o = sp._pt_blauw, sp._pt_oranje
    if b is None or o is None or sp._pt_wacht > 0:
        return
    if _overlapt(sp, b):
        _kom_uit(sp, o)
    elif _overlapt(sp, o):
        _kom_uit(sp, b)


# ===========================================================================
# Tekenen
# ===========================================================================
def _teken_portaal(pt, kleur, t):
    cx = pt["x"] + PORTAAL_B / 2
    cy = pt["y"] + PORTAAL_H / 2
    donker = (kleur[0] // 3, kleur[1] // 3, kleur[2] // 3)
    arcade.draw_ellipse_filled(cx, cy, PORTAAL_B + 6, PORTAAL_H, donker)
    arcade.draw_ellipse_outline(cx, cy, PORTAAL_B + 6, PORTAAL_H, kleur, 4)
    # Draaiende lichtjes in het portaal
    for i in range(3):
        h = t * 0.15 + i * 2.1
        arcade.draw_circle_filled(cx + math.cos(h) * 4, cy + math.sin(h) * 30, 3, kleur)
    # Pijltje: welke kant kom je eruit?
    k = pt["kant"]
    arcade.draw_triangle_filled(cx + k * 14, cy, cx + k * 7, cy - 5, cx + k * 7, cy + 5, kleur)


def teken(sp):
    """Teken de portalen, de vliegende kogel en de portaalschieter zelf."""
    t = sp._pt_t
    if sp._pt_blauw is not None:
        _teken_portaal(sp._pt_blauw, BLAUW, t)
    if sp._pt_oranje is not None:
        _teken_portaal(sp._pt_oranje, ORANJE, t)
    if sp._pt_kogel is not None:
        k = sp._pt_kogel
        arcade.draw_circle_filled(k["x"], k["y"], 7, (255, 200, 120, 120))
        arcade.draw_circle_filled(k["x"], k["y"], 4, ORANJE)
    x, y, w, h = sp.x, sp.y, sp.breedte, sp.hoogte
    cx, cy = x + w / 2, y + h / 2
    # Wit pak met een streep in de kleur van het volgende portaal
    volgend = BLAUW if sp._pt_volgende == "blauw" else ORANJE
    arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (235, 235, 240))
    arcade.draw_lrbt_rectangle_filled(x, x + w, y + h * 0.35, y + h * 0.5, volgend)
    arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 90, 110), 2)
    kijk = 2 if sp.kijkt_rechts else -2
    arcade.draw_circle_filled(cx - 6 + kijk, y + h * 0.75, 3, (30, 30, 40))
    arcade.draw_circle_filled(cx + 6 + kijk, y + h * 0.75, 3, (30, 30, 40))
    # Het portaal-pistool, met een gloeiende punt in de kleur van het volgende portaal
    r = 1 if sp.kijkt_rechts else -1
    gx = cx + r * (w / 2)
    arcade.draw_lrbt_rectangle_filled(min(gx, gx + r * 14), max(gx, gx + r * 14), cy - 4, cy + 2, (120, 120, 135))
    arcade.draw_circle_filled(gx + r * 15, cy - 1, 4, volgend)


def teken_hud(sp, x, y):
    """Balkje bovenin: welk portaal komt er, en welke portalen staan er al."""
    arcade.draw_lrbt_rectangle_filled(x - 190, x + 190, y - 10, y + 22, (0, 0, 0, 150))
    volgend = sp._pt_volgende
    kleur = BLAUW if volgend == "blauw" else ORANJE
    tekst = "blauw neerzetten" if volgend == "blauw" else "oranje wegschieten"
    arcade.draw_circle_filled(x - 172, y + 6, 8, kleur)
    arcade.draw_text("pijltje omlaag = " + tekst, x - 158, y, kleur, 12, bold=True)
    # Twee lampjes: staan de portalen er al?
    for i, (pt, kl) in enumerate(((sp._pt_blauw, BLAUW), (sp._pt_oranje, ORANJE))):
        lx = x + 150 + i * 20
        if pt is not None:
            arcade.draw_ellipse_filled(lx, y + 6, 10, 20, kl)
        arcade.draw_ellipse_outline(lx, y + 6, 10, 20, kl, 2)

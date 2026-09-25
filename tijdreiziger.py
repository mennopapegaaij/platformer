# tijdreiziger.py
# De TIJDREIZIGER: speel met de tijd!
#
#  Pijltje omlaag (vasthouden) : TERUGSPOELEN - je vliegt terug langs de weg die je kwam
#                                (tot 5 seconden terug). Handig als je in een kuil valt!
#  Toets 1                     : TIJDSTOP - alle monsters staan 3 seconden stil (en doen geen pijn)
#  Toets 2                     : VROEGER-IK - 1e keer drukken = opnemen, 2e keer = stoppen.
#                                Daarna doet een tijd-kopie van jou precies na wat je deed,
#                                steeds opnieuw. Je kunt op je vroeger-ik staan (een tijd-lift!)
#                                en monsters die hij raakt zijn weg.
# Alles kost tijd-energie (de blauwe balk), die langzaam weer vol loopt.
# Alles is vast: geen toeval.

import math
import arcade
from platforms import Platform

GESCHIEDENIS = 300        # zoveel stapjes onthoud je (5 seconden)
SPOEL_SNELHEID = 2        # zoveel stapjes spoel je per stapje terug
SPOEL_KOST = 1.0          # terugspoelen kost zoveel energie per stapje
STOP_KOST = 50            # tijdstop kost zoveel energie
STOP_TIJD = 180           # tijdstop duurt 3 seconden
OPNAME_MAX = 240          # een opname is hoogstens 4 seconden
ENERGIE_MAX = 100
BIJVULLEN = 0.25          # zoveel energie komt er per stapje bij


class EchoPlatform(Platform):
    """Je vroeger-ik: een tijd-kopie waar je op kunt staan."""

    is_echo = True

    def __init__(self, x, y, breedte, hoogte):
        super().__init__(x, y, breedte, hoogte)
        self.dx = 0               # zo ver schoof hij dit stapje (dan rijd je mee)

    def teken(self):
        pass                      # (de tijdreiziger tekent zijn vroeger-ik zelf)


def reset(sp):
    sp._tr_geschiedenis = []  # (x, y, vx, vy, kijkt_rechts) van de laatste stapjes
    sp._tr_energie = ENERGIE_MAX
    sp._tr_spoel = False      # wordt omlaag ingedrukt gehouden?
    sp._tr_spoelt = False     # spoelt hij nu echt terug?
    sp._tr_stop = 0           # hoe lang de tijdstop nog duurt
    sp._tr_opnemen = False    # zijn we aan het opnemen?
    sp._tr_opname = []        # de opname: (x, y, kijkt_rechts) per stapje
    sp._tr_echo = None        # EchoPlatform van je vroeger-ik (of None)
    sp._tr_echo_i = 0         # waar in de opname je vroeger-ik nu is
    sp._tr_echo_rechts = True
    sp._tr_t = 0
    sp._tr_melding = ""
    sp._tr_melding_tijd = 0


def _meld(sp, tekst):
    sp._tr_melding = tekst
    sp._tr_melding_tijd = 90


def tijdstop(sp):
    """Toets 1: alle monsters staan even stil."""
    if sp._tr_energie < STOP_KOST or sp._tr_stop > 0:
        _meld(sp, "Te weinig tijd-energie!" if sp._tr_stop == 0 else "De tijd staat al stil")
        return False
    sp._tr_energie -= STOP_KOST
    sp._tr_stop = STOP_TIJD
    _meld(sp, "TIJDSTOP!")
    return True


def opname(sp):
    """Toets 2: begin met opnemen, of stop en laat je vroeger-ik los."""
    if not sp._tr_opnemen:
        sp._tr_opnemen = True
        sp._tr_opname = []
        sp._tr_echo = None                   # de oude vroeger-ik verdwijnt
        _meld(sp, "Opnemen... (druk nog eens op 2)")
        return True
    sp._tr_opnemen = False
    if len(sp._tr_opname) < 10:
        sp._tr_opname = []
        _meld(sp, "Opname te kort")
        return False
    x, y, r = sp._tr_opname[0]
    sp._tr_echo = EchoPlatform(x, y, sp.breedte, sp.hoogte)
    sp._tr_echo_i = 0
    sp._tr_echo_rechts = r
    _meld(sp, "Je vroeger-ik doet het na!")
    return True


def spoel(sp):
    """Terugspoelen (in plaats van gewoon bewegen). Geeft True als het lukte."""
    if not sp._tr_spoel or sp._tr_energie < SPOEL_KOST or not sp._tr_geschiedenis:
        sp._tr_spoelt = False
        return False
    for _ in range(SPOEL_SNELHEID):
        if sp._tr_geschiedenis:
            x, y, vx, vy, r = sp._tr_geschiedenis.pop()
    sp.x, sp.y, sp.snelheid_x, sp.snelheid_y, sp.kijkt_rechts = x, y, vx, vy, r
    sp.staat_op_grond = False
    sp._tr_energie -= SPOEL_KOST
    sp._tr_spoelt = True
    _stap_echo(sp)
    _tijd_loopt(sp)
    return True


def _stap_echo(sp):
    """Je vroeger-ik doet het volgende stapje van de opname na (en begint dan opnieuw)."""
    if sp._tr_echo is None or not sp._tr_opname:
        return
    sp._tr_echo_i = (sp._tr_echo_i + 1) % len(sp._tr_opname)
    x, y, r = sp._tr_opname[sp._tr_echo_i]
    e = sp._tr_echo
    e.dx = x - e.x if sp._tr_echo_i > 0 else 0   # (bij opnieuw beginnen niet meerijden)
    e.x, e.y = x, y
    sp._tr_echo_rechts = r


def _tijd_loopt(sp):
    sp._tr_t += 1
    if sp._tr_stop > 0:
        sp._tr_stop -= 1
    if sp._tr_melding_tijd > 0:
        sp._tr_melding_tijd -= 1


def stap(sp):
    """Elke gewone stap: onthouden waar je was, opnemen, vroeger-ik, energie."""
    sp._tr_spoelt = False
    sp._tr_geschiedenis.append((sp.x, sp.y, sp.snelheid_x, sp.snelheid_y, sp.kijkt_rechts))
    if len(sp._tr_geschiedenis) > GESCHIEDENIS:
        sp._tr_geschiedenis.pop(0)
    if sp._tr_opnemen:
        sp._tr_opname.append((sp.x, sp.y, sp.kijkt_rechts))
        if len(sp._tr_opname) >= OPNAME_MAX:
            opname(sp)                       # vol: vanzelf stoppen
    _stap_echo(sp)
    if not sp._tr_spoel:
        sp._tr_energie = min(ENERGIE_MAX, sp._tr_energie + BIJVULLEN)
    _tijd_loopt(sp)


def bevroren(sp):
    """Staat de tijd voor de monsters stil?"""
    return sp._tr_stop > 0


def echo_raakt(sp, v):
    e = sp._tr_echo
    return (e is not None and e.x < v.x + v.breedte and e.x + e.breedte > v.x
            and e.y < v.y + v.hoogte and e.y + e.hoogte > v.y)


# ===========================================================================
# Tekenen
# ===========================================================================
def _poppetje(x, y, w, h, rechts, alfa, t):
    """De tijdreiziger: lange jas, hoge hoed met een klokje, en een zakhorloge."""
    cx = x + w / 2
    k = 1 if rechts else -1
    jas = (70, 50, 120, alfa)
    arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y, y + h * 0.62, jas)
    sx = x + 2 if k > 0 else x + w - 2                 # de jaspunt wappert naar achteren
    arcade.draw_triangle_filled(sx, y + h * 0.35, sx, y, sx - k * 7, y - 2, jas)
    arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + h * 0.6, y + h - 7, (240, 205, 170, alfa))
    arcade.draw_circle_filled(cx - 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30, alfa))
    arcade.draw_circle_filled(cx + 4 + k * 3, y + h * 0.74, 2.5, (20, 20, 30, alfa))
    # Hoge hoed met een klokje erop
    arcade.draw_lrbt_rectangle_filled(x + 1, x + w - 1, y + h - 8, y + h - 5, (40, 30, 60, alfa))
    arcade.draw_lrbt_rectangle_filled(x + 7, x + w - 7, y + h - 5, y + h + 9, (40, 30, 60, alfa))
    arcade.draw_circle_filled(cx, y + h + 2, 4.5, (250, 220, 120, alfa))
    hoek = t * 0.1
    arcade.draw_line(cx, y + h + 2, cx + math.cos(hoek) * 3.5, y + h + 2 + math.sin(hoek) * 3.5, (40, 30, 60, alfa), 1)
    # Zakhorloge aan een kettinkje
    hx = x + w - 5 if k > 0 else x + 5
    arcade.draw_line(cx, y + h * 0.45, hx, y + h * 0.3, (250, 220, 120, alfa), 1)
    arcade.draw_circle_filled(hx, y + h * 0.28, 3.5, (250, 220, 120, alfa))


def teken(sp):
    t = sp._tr_t
    # Tijd-spoor: waar je de laatste tijd was (zie je vooral bij het terugspoelen)
    stapjes = sp._tr_geschiedenis[-120::8]
    for i, (x, y, vx, vy, r) in enumerate(stapjes):
        a = 30 + i * 4 if sp._tr_spoelt else 10 + i
        arcade.draw_circle_filled(x + sp.breedte / 2, y + sp.hoogte / 2, 4, (120, 200, 255, min(255, a)))
    # Vroeger-ik (doorzichtig blauw)
    e = sp._tr_echo
    if e is not None:
        arcade.draw_lrbt_rectangle_filled(e.x - 2, e.x + e.breedte + 2, e.y, e.y + e.hoogte + 2, (100, 180, 255, 60))
        _poppetje(e.x, e.y, e.breedte, e.hoogte, sp._tr_echo_rechts, 130, t)
    # Opname-lampje
    if sp._tr_opnemen and t % 30 < 20:
        arcade.draw_circle_filled(sp.x + sp.breedte / 2, sp.y + sp.hoogte + 22, 4, (255, 50, 50))
    # Blauwe gloed tijdens terugspoelen
    if sp._tr_spoelt:
        arcade.draw_ellipse_filled(sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2, sp.breedte + 18, sp.hoogte + 18,
                                   (120, 200, 255, 90))
    _poppetje(sp.x, sp.y, sp.breedte, sp.hoogte, sp.kijkt_rechts, 255, t)


def teken_bevroren(vijanden):
    """Bevroren monsters krijgen een blauw ijslaagje."""
    for v in vijanden:
        if not getattr(v, "is_spike", False):
            arcade.draw_lrbt_rectangle_filled(v.x - 2, v.x + v.breedte + 2, v.y, v.y + v.hoogte + 2, (150, 210, 255, 110))


def teken_hud(sp, x, y):
    arcade.draw_lrbt_rectangle_filled(x - 250, x + 250, y - 10, y + 22, (0, 0, 0, 155))
    arcade.draw_text("Tijd:", x - 240, y, (150, 210, 255), 12, bold=True)
    arcade.draw_lrbt_rectangle_filled(x - 195, x - 195 + 110 * sp._tr_energie / ENERGIE_MAX, y + 1, y + 13,
                                      (100, 180, 255))
    arcade.draw_lrbt_rectangle_outline(x - 195, x - 85, y + 1, y + 13, (200, 230, 255), 1)
    stop_kleur = (230, 230, 230) if sp._tr_energie >= STOP_KOST else (110, 110, 110)
    arcade.draw_text("omlaag=terug  1=stop  2=" + ("STOP opname" if sp._tr_opnemen else "opnemen"),
                     x - 75, y + 1, stop_kleur, 10)
    if sp._tr_melding_tijd > 0:
        arcade.draw_text(sp._tr_melding, x, y - 24, (200, 230, 255), 13, bold=True, anchor_x="center")

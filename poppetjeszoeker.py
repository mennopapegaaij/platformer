# poppetjeszoeker.py
# De POPPETJES-ZOEKER: een scherm waar je alle poppetjes kunt bekijken.
# Je ziet ze staan, leest hun naam en wat ze doen. Blader met de pijltjes.

import arcade
from speler import Speler, FLITS_INTERVAL
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE

# Alle poppetjes: (modus, naam, wat het doet)
POPPETJES = [
    ("blok", "Blokje", "De gewone held: loop en spring."),
    ("vliegtuig", "Vliegtuig", "Knop vasthouden = omhoog, loslaten = zakken."),
    ("ufo", "UFO", "Elke tik een sprongetje omhoog (flappy!)."),
    ("bal", "Bal", "Elke tik draait de zwaartekracht om."),
    ("golf", "Golf", "Vasthouden = schuin omhoog, loslaten = schuin omlaag."),
    ("robot", "Robot", "Hoe langer je vasthoudt, hoe hoger je springt."),
    ("spin", "Spin", "Elke tik teleporteer je naar vloer of plafond."),
    ("heli", "Helikopter", "Tik = omhoog, tik nog eens = omlaag."),
    ("draaibol", "Draaibol", "Elke tik draait de zwaartekracht een kwartslag."),
    ("ballon", "Ballon", "Zweeft vanzelf omhoog; knop = zakken."),
    ("raket", "Raket", "Snel omhoog schieten; loslaten = snel vallen."),
    ("kolibrie", "Kolibrie", "Blijf snel tikken om te blijven zweven."),
    ("draak", "Draak", "Zacht en zweverig vliegen; wiebelt na."),
    ("ijs", "IJsblokje", "Spiegelglad: je glijdt door en stopt bijna niet."),
    ("ninja", "Ninja", "Snel, en zet zich van muur naar muur af."),
    ("spiegel", "Spiegel", "Links en rechts zijn omgedraaid!"),
    ("magneet", "Magneet", "Wordt naar de dichtstbijzijnde muur getrokken."),
    ("flits", "Flits", "Loopt niet, maar teleporteert per blok."),
    ("dobbelsteen", "Dobbelsteen", "Elke sprong is een willekeurige hoogte."),
    ("vertraagd", "Vertraagd", "Je toetsen werken pas een halve seconde later."),
    ("chaos", "Chaos", "De zwaartekracht klapt willekeurig om."),
    ("dronken", "Dronken", "Zwabbert vanzelf op en neer; stuur ertegenin."),
    ("turbo", "Turbo", "Raast onstopbaar op topsnelheid vooruit."),
    ("ritme", "Ritme-flip", "De zwaartekracht flipt op een vaste maat."),
    ("stuiteraar", "Stuiteraar", "Stuitert altijd vanzelf; je kunt alleen sturen."),
    ("klimmer", "Klimmer", "Kan niet springen, alleen van muur naar muur."),
    ("draaisturing", "Draaibesturing", "De zwaartekracht draait langzaam rond."),
]

KOLOMMEN = 5                 # hoeveel poppetjes naast elkaar
CEL_B = SCHERM_BREEDTE / KOLOMMEN
CEL_H = 120                  # hoogte van één vakje
TOP = SCHERM_HOOGTE - 70     # onder de titelbalk begint het raster
ZICHT_RIJEN = 3              # hoeveel rijen je tegelijk ziet


class PoppetjeZoeker(arcade.View):
    """Blader door alle poppetjes: zie ze staan en lees wat ze doen."""

    def __init__(self, kaart):
        super().__init__()
        self.kaart = kaart          # om naar terug te gaan
        self.sel = 0                # welk poppetje is gekozen
        self.scroll_rij = 0         # welke rij staat bovenaan
        self._demo = Speler()       # één poppetje dat we in elke vorm tekenen
        self._t = 0.0               # tijd, om de poppetjes te laten bewegen

    def on_show_view(self):
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
        arcade.set_background_color((40, 40, 70))

    def on_update(self, dt):
        self._t += dt               # laat de poppetjes een beetje bewegen

    def _cel_positie(self, i):
        """Middelpunt-x en onderkant-y van vakje i (met scrollen meegerekend)."""
        rij = i // KOLOMMEN
        kol = i % KOLOMMEN
        cx = kol * CEL_B + CEL_B / 2
        cy = TOP - (rij - self.scroll_rij) * CEL_H
        return cx, cy

    def _zorg_zichtbaar(self):
        """Schuif zodat het gekozen poppetje in beeld blijft."""
        rij = self.sel // KOLOMMEN
        if rij < self.scroll_rij:
            self.scroll_rij = rij
        elif rij > self.scroll_rij + ZICHT_RIJEN - 1:
            self.scroll_rij = rij - ZICHT_RIJEN + 1

    def on_draw(self):
        self.clear()

        # Titelbalk
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, SCHERM_HOOGTE - 46,
                                          SCHERM_HOOGTE, (20, 20, 40))
        arcade.draw_text("🔎  Poppetjes-zoeker", SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 34,
                         arcade.color.WHITE, 22, bold=True, anchor_x="center")

        # Alle poppetjes in een raster
        for i, (modus, naam, _) in enumerate(POPPETJES):
            rij = i // KOLOMMEN
            if rij < self.scroll_rij or rij > self.scroll_rij + ZICHT_RIJEN - 1:
                continue
            cx, cy = self._cel_positie(i)
            gekozen = (i == self.sel)
            # Vakje-achtergrond (oplichten als het gekozen is)
            if gekozen:
                arcade.draw_lrbt_rectangle_filled(cx - CEL_B / 2 + 4, cx + CEL_B / 2 - 4,
                                                  cy - 24, cy + CEL_H - 30, (70, 90, 140))
                arcade.draw_lrbt_rectangle_outline(cx - CEL_B / 2 + 4, cx + CEL_B / 2 - 4,
                                                   cy - 24, cy + CEL_H - 30, (255, 230, 90), 3)
            # Het poppetje tekenen
            self._teken_poppetje(modus, cx, cy)
            # Naam eronder
            arcade.draw_text(naam, cx, cy - 20, arcade.color.WHITE, 11,
                             bold=True, anchor_x="center")

        # Onderbalk met de uitleg van het gekozen poppetje
        _, naam, uitleg = POPPETJES[self.sel]
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, 0, 52, (20, 20, 40))
        arcade.draw_text(naam, 16, 30, (255, 230, 90), 15, bold=True)
        arcade.draw_text(uitleg, 16, 10, arcade.color.WHITE, 12)
        arcade.draw_text("←→↑↓ bladeren  •  ESC = terug", SCHERM_BREEDTE - 16, 18,
                         (180, 180, 200), 10, anchor_x="right")

    def _teken_poppetje(self, modus, cx, cy):
        """Teken één poppetje in een bepaalde vorm op plek (cx, cy)."""
        d = self._demo
        d.modus = modus
        d.x = cx - d.breedte / 2
        d.y = cy
        # Een beetje leven in de poppetjes die draaien/bewegen
        d.rotatie = 0
        d._stuur_hoek = self._t
        d._flits_teller = int(self._t * 8) % FLITS_INTERVAL
        if modus in ("bal", "draaibol"):
            d.rotatie = (self._t * 60) % 360
        try:
            d.teken()
        except Exception:
            # Mocht een vorm iets missen, teken dan een simpel blokje (nooit crashen)
            arcade.draw_lrbt_rectangle_filled(d.x, d.x + d.breedte, d.y, d.y + d.hoogte,
                                              (200, 200, 200))

    def on_key_press(self, toets, modifiers):
        if toets == arcade.key.LEFT:
            self.sel = max(0, self.sel - 1)
        elif toets == arcade.key.RIGHT:
            self.sel = min(len(POPPETJES) - 1, self.sel + 1)
        elif toets == arcade.key.UP:
            self.sel = max(0, self.sel - KOLOMMEN)
        elif toets == arcade.key.DOWN:
            self.sel = min(len(POPPETJES) - 1, self.sel + KOLOMMEN)
        elif toets in (arcade.key.ESCAPE, arcade.key.K, arcade.key.P,
                       arcade.key.ENTER, arcade.key.NUM_ENTER):
            self.window.show_view(self.kaart)     # terug naar de kaart
        self._zorg_zichtbaar()

    def on_mouse_press(self, x, y, knop, modifiers):
        # Klik op een poppetje om het te kiezen
        for i in range(len(POPPETJES)):
            rij = i // KOLOMMEN
            if rij < self.scroll_rij or rij > self.scroll_rij + ZICHT_RIJEN - 1:
                continue
            cx, cy = self._cel_positie(i)
            if (cx - CEL_B / 2 <= x <= cx + CEL_B / 2 and
                    cy - 24 <= y <= cy + CEL_H - 30):
                self.sel = i
                self._zorg_zichtbaar()
                return

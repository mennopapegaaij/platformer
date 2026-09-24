# poppetjeszoeker.py
# De POPPETJES-ZOEKER: een scherm waar je alle poppetjes kunt bekijken.
# Je ziet ze staan, leest hun naam en wat ze doen. Je kunt TYPEN om te zoeken
# en poppetjes als FAVORIET markeren met een ster.

import arcade
from speler import Speler, FLITS_INTERVAL
from instellingen import SCHERM_BREEDTE, SCHERM_HOOGTE
import voortgang as voortgang_module

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
    ("boemerang", "Boemerang", "Een elastiek trekt je steeds terug naar je startpunt."),
    ("stamper", "Stamper", "Op de grond spring je; in de lucht stamp je keihard omlaag."),
    ("zweefspringer", "Zweefspringer", "Superlange, zwevende sprongen (lage zwaartekracht)."),
    ("groeier", "Groeier", "Hoe langer je loopt, hoe groter je wordt."),
    ("zwaargewicht", "Zwaargewicht", "Enorme zwaartekracht: je valt als een steen, springt laag."),
    ("versneller", "Versneller", "Hoe langer je één kant op loopt, hoe sneller je gaat."),
    ("wind", "Wind", "Een windvlaag duwt je opzij; hij draait op de maat om."),
    ("plakker", "Plakker", "Plakt aan muren en klimt in hopjes omhoog."),
    ("metronoom", "Metronoom", "Springen mag ALLEEN precies op de tel!"),
    ("katapult", "Katapult", "Wordt steeds in dezelfde boog weggeschoten; stuur klein bij."),
    ("krimpsprong", "Krimpsprong", "Elke sprong in de lucht is lager dan de vorige."),
    ("tegendraads", "Tegendraads", "Elke keer dat je landt draaien links en rechts om!"),
    ("turboflip", "Turbo-flip", "Onstopbaar vooruit én de zwaartekracht flipt op de maat."),
    ("spiegelkatapult", "Spiegel-katapult", "Weggeschoten in een boog, maar bijsturen is omgedraaid."),
    ("schaduw", "Schaduw", "Een schaduw loopt je oude route na; raakt hij je, dan ga je af!"),
    ("pingpong", "Ping-pong", "Kaatst vanzelf tussen vloer en plafond; elke kaats flipt de zwaartekracht."),
    ("spook", "Spook", "Zweeft griezelig en wordt steeds even onzichtbaar!"),
    ("vleermuis", "Vleermuis", "Fladdert omhoog bij elke tik en wiebelt eng heen en weer."),
    ("zombie", "Zombie", "Sjokt langzaam en zwaar vooruit en springt maar laag."),
    ("pompoenkop", "Pompoenkop", "Laat een vurig spoor achter en gloeit eng."),
    ("voorspeller", "Voorspeller", "Onstopbaar vooruit, en je sprong komt pas later!"),
    ("pendel", "Pendel", "Loopt vanzelf en keert op de maat om; jij kunt alleen springen."),
    ("blinde", "Blinde", "Je bent onzichtbaar en flitst alleen even op de maat."),
    ("dubbelflip", "Dubbelflip", "Elke sprong: zwaartekracht om én links/rechts wisselen."),
    ("vijfkamp", "Vijfkamp", "5 in 1: glad, tegendraads, krimpsprong, zwaar én een schaduw!"),
    ("tienkamp", "Tienkamp", "10 in 1: ondersteboven, glad, tegendraads, krimp, zwaar, harde landing, doorschieter, moe, nacht, hoofdpijn!"),
    ("vijftienkamp", "Vijftienkamp", "15 in 1: tienkamp + luchtrem, hoogtevrees, dikkerd, aanloop en eenrichting!"),
    ("twintigkamp", "Twintigkamp", "20 in 1: vijftienkamp + hete vloer, vasthouden, superglad, spike-magneet en donkerder!"),
    ("element", "Elementmeester", "Wisselt bij elke landing: vuur (snel), water (2x springen), lucht (glijden), aarde (stampen!)."),
    ("elementkoning", "Elementenkoning", "25 elementen! Bij elke landing de volgende, elk met een eigen kracht."),
    ("bouwmeester", "Bouwmeester", "Pijltje omlaag = blokje bouwen (3 stuks). Terug als je op echte grond landt."),
    ("portaalschieter", "Portaalschieter", "Pijltje omlaag: blauw portaal neerzetten, nog eens: oranje wegschieten. Loop erdoor!"),
    ("drakentemmer", "Drakentemmer", "Je draak groeit: ei, baby, jonge draak, grote draak. Fladderen, vuur spuwen (omlaag), vliegen!"),
    ("mierenkolonie", "Mierenkolonie", "4 mieren lopen achter je aan (je levens!). Omlaag: toren of brug van mieren."),
    ("evolutie", "Evolutie", "Verzamel DNA en kies zelf mutaties (1/2/3): vleugels, stekels, pantser... bouw je eigen wezen!"),
    ("schilder", "Schilder", "Spuit verf (omlaag), 8 kleuren (1-8): trampoline, snel, spikes weg, glad, teleport, lanceer, wolk, modder."),
    ("eigen", "Mijn poppetje", "Je zelfgemaakte poppetje uit de poppetjes-maker."),
]

KOLOMMEN = 5                 # hoeveel poppetjes naast elkaar
CEL_B = SCHERM_BREEDTE / KOLOMMEN
CEL_H = 120                  # hoogte van één vakje
TOP = SCHERM_HOOGTE - 96     # onder de titel + zoekbalk begint het raster
ZICHT_RIJEN = 3              # hoeveel rijen je tegelijk ziet


class PoppetjeZoeker(arcade.View):
    """Blader door alle poppetjes: zoek door te typen en markeer favorieten."""

    # Knop 'Alleen favorieten' (rechtsboven, in de zoekbalk)
    FAV_KNOP = (SCHERM_BREEDTE - 196, SCHERM_BREEDTE - 10, SCHERM_HOOGTE - 84, SCHERM_HOOGTE - 58)

    def __init__(self, terug, bouwer=None, kies_functie=None, alleen=None):
        super().__init__()
        self.terug = terug          # het scherm waar we naar terug gaan
        self.bouwer = bouwer        # als dit gezet is: kies een poppetje om te plaatsen
        self.kies_functie = kies_functie   # als dit gezet is: roep dit aan met de gekozen modus
        self.alleen = alleen        # None = alles; anders alleen deze modi tonen (een set)
        self.zoek = ""              # wat je hebt getypt om te zoeken
        self.alleen_fav = False     # alleen je favorieten laten zien?
        self.favorieten = set(voortgang_module.laad_voortgang().get("favorieten", []))
        self.sel = 0                # welk poppetje is gekozen (in de gefilterde lijst)
        self.scroll_rij = 0         # welke rij staat bovenaan
        self._demo = Speler()       # één poppetje dat we in elke vorm tekenen
        self._t = 0.0               # tijd, om de poppetjes te laten bewegen
        self._eigen_instel = voortgang_module.laad_voortgang().get("eigen_poppetje")

    def on_show_view(self):
        if self.window.width != SCHERM_BREEDTE or self.window.height != SCHERM_HOOGTE:
            self.window.set_size(SCHERM_BREEDTE, SCHERM_HOOGTE)
        arcade.set_background_color((40, 40, 70))

    def on_update(self, dt):
        self._t += dt               # laat de poppetjes een beetje bewegen

    # ---------- welke poppetjes laten we zien? ----------
    def _gefilterd(self):
        """De lijst poppetjes die past bij je zoektekst en de favorieten-knop."""
        z = self.zoek.lower()
        uit = []
        for modus, naam, uitleg in POPPETJES:
            if self.alleen is not None and modus not in self.alleen:
                continue                          # alleen bepaalde poppetjes tonen
            if z and z not in naam.lower() and z not in modus.lower():
                continue
            if self.alleen_fav and modus not in self.favorieten:
                continue
            uit.append((modus, naam, uitleg))
        return uit

    def _cel_positie(self, i):
        """Middelpunt-x en onderkant-y van vakje i (met scrollen meegerekend)."""
        rij = i // KOLOMMEN
        kol = i % KOLOMMEN
        cx = kol * CEL_B + CEL_B / 2
        cy = TOP - (rij - self.scroll_rij) * CEL_H
        return cx, cy

    def _ster_positie(self, cx, cy):
        """Waar het ster-knopje van een vakje staat (rechtsboven in het vakje)."""
        return cx + CEL_B / 2 - 20, cy + 74

    def _zorg_zichtbaar(self, aantal):
        """Schuif zodat het gekozen poppetje in beeld blijft."""
        self.sel = max(0, min(self.sel, aantal - 1)) if aantal else 0
        rij = self.sel // KOLOMMEN
        if rij < self.scroll_rij:
            self.scroll_rij = rij
        elif rij > self.scroll_rij + ZICHT_RIJEN - 1:
            self.scroll_rij = rij - ZICHT_RIJEN + 1

    # ---------- tekenen ----------
    def on_draw(self):
        self.clear()
        lijst = self._gefilterd()
        self.sel = max(0, min(self.sel, len(lijst) - 1)) if lijst else 0

        # Titelbalk
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, SCHERM_HOOGTE - 46,
                                          SCHERM_HOOGTE, (20, 20, 40))
        titel = ("🎯  Kies je poppetje voor Frame Perfect"
                 if self.kies_functie is not None else "🔎  Poppetjes-zoeker")
        arcade.draw_text(titel, 16, SCHERM_HOOGTE - 34, arcade.color.WHITE, 18, bold=True)

        # Zoekbalk
        arcade.draw_lrbt_rectangle_filled(16, SCHERM_BREEDTE - 210, SCHERM_HOOGTE - 84,
                                          SCHERM_HOOGTE - 58, (60, 60, 90))
        arcade.draw_lrbt_rectangle_outline(16, SCHERM_BREEDTE - 210, SCHERM_HOOGTE - 84,
                                           SCHERM_HOOGTE - 58, (150, 150, 190), 2)
        toon = self.zoek if self.zoek else "typ om te zoeken..."
        kleur = arcade.color.WHITE if self.zoek else (150, 150, 170)
        arcade.draw_text("Zoek: " + toon + "|", 24, SCHERM_HOOGTE - 79, kleur, 13, bold=True)

        # Knop 'Alleen favorieten'
        fl, fr, fb, ft = self.FAV_KNOP
        fav_kl = (200, 170, 40) if self.alleen_fav else (70, 70, 100)
        arcade.draw_lrbt_rectangle_filled(fl, fr, fb, ft, fav_kl)
        arcade.draw_lrbt_rectangle_outline(fl, fr, fb, ft, (255, 220, 120), 2)
        arcade.draw_text("⭐ Alleen favorieten", (fl + fr) // 2, (fb + ft) // 2 - 6,
                         arcade.color.WHITE, 10, bold=True, anchor_x="center")

        # Niets gevonden?
        if not lijst:
            arcade.draw_text("Niks gevonden — probeer iets anders te typen.",
                             SCHERM_BREEDTE // 2, SCHERM_HOOGTE // 2,
                             arcade.color.WHITE, 15, bold=True, anchor_x="center")
        else:
            # Alle poppetjes in een raster
            for i, (modus, naam, _) in enumerate(lijst):
                rij = i // KOLOMMEN
                if rij < self.scroll_rij or rij > self.scroll_rij + ZICHT_RIJEN - 1:
                    continue
                cx, cy = self._cel_positie(i)
                gekozen = (i == self.sel)
                if gekozen:
                    arcade.draw_lrbt_rectangle_filled(cx - CEL_B / 2 + 4, cx + CEL_B / 2 - 4,
                                                      cy - 24, cy + CEL_H - 30, (70, 90, 140))
                    arcade.draw_lrbt_rectangle_outline(cx - CEL_B / 2 + 4, cx + CEL_B / 2 - 4,
                                                       cy - 24, cy + CEL_H - 30, (255, 230, 90), 3)
                self._teken_poppetje(modus, cx, cy)
                arcade.draw_text(naam, cx, cy - 20, arcade.color.WHITE, 11,
                                 bold=True, anchor_x="center")
                # Ster: goud als favoriet, anders een grijze omtrek-ster
                sx, sy = self._ster_positie(cx, cy)
                if modus in self.favorieten:
                    arcade.draw_text("⭐", sx, sy, arcade.color.GOLD, 15, anchor_x="center")
                else:
                    arcade.draw_text("☆", sx, sy, (170, 170, 190), 15, anchor_x="center")

        # Onderbalk met de uitleg van het gekozen poppetje
        arcade.draw_lrbt_rectangle_filled(0, SCHERM_BREEDTE, 0, 52, (20, 20, 40))
        if lijst:
            modus, naam, uitleg = lijst[self.sel]
            ster = "⭐ " if modus in self.favorieten else ""
            arcade.draw_text(ster + naam, 16, 30, (255, 230, 90), 15, bold=True)
            arcade.draw_text(uitleg, 16, 10, arcade.color.WHITE, 12)
        if self.kies_functie is not None:
            hint = "Klik of Enter = met dit poppetje spelen  •  typ = zoeken  •  ESC = terug"
        elif self.bouwer is not None:
            hint = "Klik = plaatsen  •  klik ster = favoriet  •  Tab = favoriet  •  ESC = terug"
        else:
            hint = "Klik ster = favoriet  •  Tab = favoriet  •  typ = zoeken  •  ESC = terug"
        arcade.draw_text(hint, SCHERM_BREEDTE - 16, 4, (180, 180, 200), 9, anchor_x="right")

    def _teken_poppetje(self, modus, cx, cy):
        """Teken één poppetje in een bepaalde vorm op plek (cx, cy)."""
        d = self._demo
        d.modus = modus
        if modus == "eigen":
            d.eigen_instel = self._eigen_instel     # jouw zelfgemaakte instellingen
        d.x = cx - d.breedte / 2
        d.y = cy
        d.rotatie = 0
        d._stuur_hoek = self._t
        d._flits_teller = int(self._t * 8) % FLITS_INTERVAL
        if modus in ("bal", "draaibol"):
            d.rotatie = (self._t * 60) % 360
        try:
            d.teken()
        except Exception:
            arcade.draw_lrbt_rectangle_filled(d.x, d.x + d.breedte, d.y, d.y + d.hoogte,
                                              (200, 200, 200))

    # ---------- favorieten ----------
    def _wissel_favoriet(self, modus):
        """Zet een poppetje aan/uit in je favorieten en bewaar het."""
        if modus in self.favorieten:
            self.favorieten.discard(modus)
        else:
            self.favorieten.add(modus)
        voortgang_module.sla_favorieten_op(self.favorieten)

    # ---------- kiezen (in de bouwmodus) ----------
    def _kies(self, lijst):
        """Kies het geselecteerde poppetje: start ermee (kies_functie) of plaats het (bouwer)."""
        if not lijst:
            return
        modus = lijst[self.sel][0]
        if self.kies_functie is not None:
            self.kies_functie(modus)          # bv. de frame-perfect race starten
            return
        self.bouwer.portaal_soort = modus
        self.bouwer.gekozen = "portaal"
        self.window.show_view(self.terug)

    # ---------- typen om te zoeken ----------
    def on_text(self, text):
        # Letters/cijfers die je typt komen in de zoektekst
        for ch in text:
            if ch.isprintable() and ch not in ("\r", "\n", "\t") and len(self.zoek) < 18:
                self.zoek += ch
        self.sel = 0
        self.scroll_rij = 0

    def on_key_press(self, toets, modifiers):
        lijst = self._gefilterd()
        if toets == arcade.key.BACKSPACE:
            self.zoek = self.zoek[:-1]     # laatste letter weg
            self.sel = 0
            self.scroll_rij = 0
            return
        if toets == arcade.key.LEFT:
            self.sel = max(0, self.sel - 1)
        elif toets == arcade.key.RIGHT:
            self.sel = min(len(lijst) - 1, self.sel + 1) if lijst else 0
        elif toets == arcade.key.UP:
            self.sel = max(0, self.sel - KOLOMMEN)
        elif toets == arcade.key.DOWN:
            self.sel = min(len(lijst) - 1, self.sel + KOLOMMEN) if lijst else 0
        elif toets == arcade.key.TAB:
            if lijst:
                self._wissel_favoriet(lijst[self.sel][0])   # favoriet aan/uit
        elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
            if self.bouwer is not None or self.kies_functie is not None:
                self._kies(lijst)          # dit poppetje plaatsen of ermee starten
            else:
                self.window.show_view(self.terug)
        elif toets == arcade.key.ESCAPE:
            self.window.show_view(self.terug)
        self._zorg_zichtbaar(len(lijst))

    def on_mouse_press(self, x, y, knop, modifiers):
        # Klik op de 'Alleen favorieten'-knop?
        fl, fr, fb, ft = self.FAV_KNOP
        if fl <= x <= fr and fb <= y <= ft:
            self.alleen_fav = not self.alleen_fav
            self.sel = 0
            self.scroll_rij = 0
            return
        lijst = self._gefilterd()
        for i in range(len(lijst)):
            rij = i // KOLOMMEN
            if rij < self.scroll_rij or rij > self.scroll_rij + ZICHT_RIJEN - 1:
                continue
            cx, cy = self._cel_positie(i)
            # Eerst: klik op de ster van dit vakje? -> favoriet aan/uit
            sx, sy = self._ster_positie(cx, cy)
            if abs(x - sx) <= 14 and abs(y - (sy + 6)) <= 14:
                self._wissel_favoriet(lijst[i][0])
                return
            # Anders: klik op het vakje zelf -> kies dit poppetje
            if (cx - CEL_B / 2 <= x <= cx + CEL_B / 2 and
                    cy - 24 <= y <= cy + CEL_H - 30):
                self.sel = i
                self._zorg_zichtbaar(len(lijst))
                if self.bouwer is not None or self.kies_functie is not None:
                    self._kies(lijst)      # meteen plaatsen of ermee starten
                return

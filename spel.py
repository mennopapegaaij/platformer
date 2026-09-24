# spel.py
# Het hoofdspel — brengt alles samen.
# De PlatformerSpel klasse beheert de game loop: tekenen, bijwerken, toetsen.

import arcade
import copy   # om bij een herstart verse kopieën van je eigen level te maken
import math   # voor het vuurwerk bij winst
import elementkoning as ek
import portaalschieter as ps
import drakentemmer as dt
import mierenkolonie as mk
import evolutie as evo
import schilder as sv
import levels as levels_module
import achtergrond as achtergrond_module
from geluid import geluid as geluid_manager
from instellingen import (SCHERM_BREEDTE, SCHERM_HOOGTE, TWEE_BREEDTE, TWEE_HOOGTE,
                           SPRING_KRACHT, LUCHT_KLEUR, VLAG_KLEUR,
                           VLAG_DOEK_KLEUR, LEVEL_NAMEN, AANTAL_LEVELS)
from speler import Speler, VLIEG_PLAFOND
from portaal import SNELHEID_FACTOR
from springers import SpringBol, SpringMat
from powerup import Kogel
import voortgang as voortgang_module


class PlatformerSpel(arcade.View):
    """Het hoofdspel — alles zit hierin."""

    def __init__(self, level_nummer, voltooid_levels, punten=0, levens=None,
                 arena=False, kaart_punten=0, kaart_levens=None, race=False,
                 eigen_level=None, vlucht=False, twee=False, aantal_spelers=None,
                 bouw_slot=1, testruimte=False, frameperfect=False, start_modus=None):
        super().__init__()
        # Op welke bouw-plek dit eigen level hoort (om er weer op terug te komen)
        self.bouw_slot = bouw_slot
        # Testruimte: een speelkamer om alle poppetjes te proberen (wissel met N)
        self.testruimte = testruimte
        # Frame Perfect-kamer: een pittige race-baan met een gekozen poppetje
        self.frameperfect = frameperfect
        self.start_modus = start_modus       # in welke vorm je begint (of None)
        self._test_index = 0
        if testruimte:
            from poppetjeszoeker import POPPETJES
            self._test_modi = [m for m, _, _ in POPPETJES]   # alle poppetjes op volgorde
        # Eigen (zelfgebouwd) level uit de bouwmodus (of None)
        self.eigen = eigen_level is not None
        self.eigen_level_data = eigen_level
        # Onthoud welk level we starten en welke al gehaald zijn
        self.start_level = level_nummer
        self.voltooid = voltooid_levels
        # Bewaar punten en levens van het vorige level
        self.start_punten = punten
        self.start_levens = levens   # None = gebruik het standaard aantal levens
        # Vechtmodus (arena): aparte levels waar je alle monsters moet verslaan
        self.arena = arena
        # Racemodus: je rent vanzelf vooruit en springt over gaten/spikes/blokken
        self.race = race
        # Vliegtuig-modus: je vliegt vanzelf vooruit en houdt de knop vast om te stijgen
        self.vlucht = vlucht
        # Aantal spelers (1 t/m 4). "twee=True" betekent 2 spelers (voor de compatibiliteit).
        if aantal_spelers is None:
            aantal_spelers = 2 if twee else 1
        self.aantal = max(1, min(4, aantal_spelers))
        self.twee = self.aantal >= 2   # "twee" = meer dan 1 speler (split-screen)
        # De punten/levens van de gewone kaart, om terug te zetten na de arena
        self.kaart_punten = kaart_punten
        self.kaart_levens = kaart_levens
        # Elke speler krijgt een eigen poppetje en een eigen camera
        self.spelers = [Speler() for _ in range(self.aantal)]
        self.cameras = [arcade.camera.Camera2D() for _ in range(self.aantal)]
        self._vlieg = [False] * self.aantal   # of elke speler nu de knop vasthoudt
        self._finish = [False] * self.aantal  # of elke speler al gefinisht is
        self._vorige = [0.0] * self.aantal    # vorige x van elke speler (voor portaal-sweep)
        # Speler 1 en camera 1 hebben ook een 'gewone' naam (voor de 1-speler-code)
        self.speler = self.spelers[0]
        self.camera = self.cameras[0]
        self._vlieg_omhoog = False   # 1-speler: of de speler de vlieg-knop vasthoudt
        # Hoogste arena-level dat je mag kiezen met de pijltjes (groeit als je wint)
        self._arena_top = 1

    # Klik-vlakken voor de arena-pijltjes bovenin: (links, rechts, onder, boven)
    ARENA_PIJL_LINKS = (SCHERM_BREEDTE // 2 - 78, SCHERM_BREEDTE // 2 - 44,
                        SCHERM_HOOGTE - 42, SCHERM_HOOGTE - 14)
    ARENA_PIJL_RECHTS = (SCHERM_BREEDTE // 2 + 44, SCHERM_BREEDTE // 2 + 78,
                         SCHERM_HOOGTE - 42, SCHERM_HOOGTE - 14)
    # Klik-vlak voor de reset-knop rechtsboven
    ARENA_RESET_KNOP = (SCHERM_BREEDTE - 100, SCHERM_BREEDTE - 8,
                        SCHERM_HOOGTE - 70, SCHERM_HOOGTE - 44)

    def on_show_view(self):
        """Wordt aangeroepen als dit scherm zichtbaar wordt."""
        # Bij 2 spelers wordt het scherm groot (split-screen); anders de gewone maat
        # Venstermaat: 1 speler = 1 vak, 2 = naast elkaar, 3-4 = 2x2 (groter naar beneden)
        kol, rij = self._raster()
        gewenst = (SCHERM_BREEDTE * kol, SCHERM_HOOGTE * rij)
        if (self.window.width, self.window.height) != gewenst:
            self.window.set_size(*gewenst)
        arcade.set_background_color(LUCHT_KLEUR)
        self.huidig_level = self.start_level
        # Herstel punten van het vorige level
        self.punten = self.start_punten
        # Reset alle spelers (power-ups weg, positie terug naar start)
        for sp in self.spelers:
            sp.volledig_reset()
        # Herstel levens als die meegegeven zijn
        if self.start_levens is not None:
            self.speler.levens = self.start_levens
        # Herstel de snelheids- en sprongbonus die je met punten verdiend had
        # (in de vechtmodus geen bonus: daar speel je gewoon normaal)
        bonus = 0 if (self.arena or self.race or self.vlucht) else self.punten // 10
        self.speler.snelheid_bonus = bonus
        self.speler.sprong_bonus = bonus
        # In de arena: met de pijltjes mag je tot je hoogste bereikte level terug/vooruit
        if self.arena:
            record = voortgang_module.laad_voortgang().get("arena_record", 0)
            self._arena_top = max(self.start_level, record)
        self.maak_level(self.start_level)

    def maak_level(self, nummer):
        """Laad een level op basis van het nummer (1 t/m AANTAL_LEVELS)."""

        # Zet de speler terug naar de beginpositie (levens blijven bewaard!)
        self.speler.reset()

        # Spelstatus resetten
        self.gewonnen = False
        self.dood = False
        self.level_gehaald = False
        self.game_over = False

        # Punten worden NIET gereset bij level wisselen — alleen bij nieuw spel!
        if not hasattr(self, 'punten'):
            self.punten = 0

        # Haal de level-gegevens op: eigen level, racebaan, arena of gewone levels
        if self.eigen:
            # Verse kopie, zodat verslagen monsters en opgepakte hartjes bij een
            # herstart weer terug zijn (het opgeslagen level blijft ongewijzigd).
            data = copy.deepcopy(self.eigen_level_data)
            if self.race or self.vlucht:
                # Een zelfgebouwde race-/vliegbaan: je gaat vanzelf op rustige snelheid
                self.speler.snelheid_bonus = 1
                self.speler.sprong_bonus = 0
        elif self.vlucht:
            data = levels_module.maak_vlucht(nummer)
            # In de vliegtuig-modus vlieg je vanzelf vooruit (iets sneller per baan)
            self.speler.snelheid_bonus = levels_module.vlucht_snelheid_bonus(nummer)
            self.speler.sprong_bonus = 0
        elif self.race:
            data = levels_module.maak_race(nummer)
            # In de racemodus ren je vanzelf steeds sneller (past bij de blok-afstanden)
            self.speler.snelheid_bonus = levels_module.race_snelheid_bonus(nummer)
            self.speler.sprong_bonus = 0
        elif self.arena:
            data = levels_module.maak_arena(nummer)
        elif self.testruimte:
            from testruimte import maak_testruimte
            data = maak_testruimte()
        elif self.frameperfect:
            from frameperfect import frameperfect_baan
            data, self._fp_plafond, fp_bonus = frameperfect_baan(self.start_modus)
            self.speler.snelheid_bonus = fp_bonus   # baan + snelheid passen bij het poppetje
            self.speler.sprong_bonus = 0
        else:
            data = levels_module.maak_level(nummer)
        platforms = data[0]
        vijanden = data[1]
        powerups = data[2]
        vlag_x = data[3]
        vlag_y = data[4]
        level_breedte = data[5]
        # Portalen zijn optioneel (een 7e onderdeel); niet elk level heeft ze
        self.portalen = list(data[6]) if len(data) > 6 else []
        # Decoratie is optioneel (een 8e onderdeel); alleen zelfgebouwde levels hebben het
        self.decoraties = list(data[7]) if len(data) > 7 else []
        # Spring-bollen en spring-matten (een 9e onderdeel)
        self.springers = list(data[8]) if len(data) > 8 else []
        # Teleporters (een 10e onderdeel): blauw <-> oranje paren
        self.teleporters = list(data[9]) if len(data) > 9 else []
        # Achtergrond-zones (een 11e onderdeel): [(x, achtergrond-nummer), ...]
        self.acht_zones = list(data[10]) if len(data) > 10 else []
        # Zelfgemaakt deuntje (een 12e onderdeel): lijst noten (-1 = stilte)
        self.muziek = list(data[11]) if len(data) > 11 else []
        # Tekstbordjes (een 13e onderdeel)
        self.borden = list(data[12]) if len(data) > 12 else []
        # Checkpoints (een 14e onderdeel): tussenpunten om bij terug te komen
        self.checkpoints = list(data[13]) if len(data) > 13 else []
        # Eigen achtergrondkleur (een 15e onderdeel): None = het gewone thema
        self.acht_kleur = tuple(data[14]) if len(data) > 14 and data[14] else None
        # Alles-beweegt (een 16e onderdeel): HOE alle voorwerpen bewegen
        a = data[15] if len(data) > 15 else None
        if a is True:              # oud formaat (True/False) -> wiebel
            a = "wiebel"
        elif not a:
            a = "uit"
        self.anim_soort = a
        self._anim_t = 0.0
        # Muur-dood (een 17e onderdeel): ga je dood als je tegen een muur botst?
        # (Staat het uit, dan stop je gewoon tegen de muur.)
        self.muurdood = bool(data[16]) if len(data) > 16 else True
        # Respawn-punt onthouden tussen herstarts van HETZELFDE level.
        if not hasattr(self, "_respawn"):
            self._respawn = None
            self._respawn_nummer = None
        if self._respawn is not None and self._respawn_nummer == nummer and not self.twee:
            # Begin bij het laatst aangeraakte checkpoint i.p.v. helemaal opnieuw
            self.speler.x, self.speler.y = self._respawn
            for cp in self.checkpoints:
                if cp.x <= self._respawn[0] + 1:
                    cp.actief = True          # alle checkpoints t/m je startpunt kleuren groen
        else:
            self._respawn = None              # ander level -> respawn vergeten
            self._respawn_nummer = None
        self._vuurwerk = []           # deeltjes-vuurwerk bij winst
        self._heeft_muziek = any(n != -1 for n in self.muziek)
        self._muziek_stap = 0
        self._muziek_teller = 0.0
        self._verf_tijd = 0           # tikt door zodat meerdere kleuren overvloeien
        self.platforms = list(platforms)   # een kopie: zo blijven bouwblokjes niet in het level hangen
        # Volg-voorwerpen: alles waar je de 'volg mij'-verf op hebt gezet.
        # Die komen tijdens het spelen achter de speler aan (zie _update_volgers).
        self.volgers = [o for lijst in (platforms, vijanden, self.portalen,
                                        self.teleporters, self.springers,
                                        powerups, self.decoraties)
                        for o in lijst if getattr(o, "volg", False)]
        # Zet de begin-modus: vliegtuig in de vluchtmodus, anders het gewone blokje.
        # Portalen kunnen dit tijdens het spelen nog omzetten (ufo/bal/golf)!
        self.speler.modus = "vliegtuig" if self.vlucht else "blok"
        self.speler.zwaartekracht_richting = 1
        # Frame Perfect: begin in het gekozen poppetje
        if self.start_modus and not self.twee:
            self._zet_vorm(self.speler, self.start_modus, 1)
        # Jouw gekozen kleur voor de speler (in 1-speler-modus)
        if not self.twee:
            gekozen = voortgang_module.laad_voortgang().get("speler_kleur")
            if gekozen:
                self.speler.kleur = tuple(gekozen)
        # Geen plafond voor de spelers: je kunt oneindig omhoog (de camera gaat mee).
        # In de Frame Perfect-kamer wél een plafond, zodat vliegers er niet bovenlangs cheesen.
        # In de Frame Perfect-kamer hoort bij elk poppetje een eigen plafond (of geen).
        plafond = getattr(self, "_fp_plafond", None) if self.frameperfect else None
        for sp in self.spelers:
            sp.plafond = plafond
        # Deuren die met een sleutel opengaan
        self._deuren = [p for p in platforms if getattr(p, "is_deur", False)]
        # Onthoud de vorige x van de speler (voor de snelheid-portaal 'sweep'-check)
        self._vorige_speler_x = self.speler.x
        # --- Meerdere spelers: zet alle spelers klaar en verdeel het scherm ---
        if self.twee:
            self._zet_multi_klaar()
        # Onthoud welke blokken je kunnen doden als je tegen de ZIJKANT aan botst
        # (net als Geometry Dash). In de race-, vlucht- en bouwmodus tellen ALLE
        # blokken mee (ook de grasblokken); in de gewone levels doen we dit niet,
        # anders zou springen op zwevende platforms ineens dodelijk zijn.
        if self.race or self.vlucht or self.eigen or self.frameperfect:
            # alle blokken tellen mee, behalve hellingen (daar loop je overheen)
            # en behalve deuren (daar ga je niet dood van, die houden je alleen tegen)
            self._blokken = [p for p in platforms
                             if not getattr(p, "is_schuin", False)
                             and not getattr(p, "is_deur", False)
                             and not getattr(p, "doorheen", False)]
        else:
            self._blokken = []                       # gewone levels: geen zijkant-dood
        # Muur-dood uit (knop in de bouwmodus)? Dan stoppen spelers gewoon tegen de muren.
        muur_blokken = self._blokken if (self.eigen and not self.muurdood) else None
        for sp in self.spelers:
            sp._muur_blokken = muur_blokken
        self.vijanden = vijanden
        for v in vijanden:
            if getattr(v, "geverfd", False):
                v.geverfd = False                    # opnieuw beginnen: groene verf is er weer af
        self.powerups = powerups
        self.vlag_x = vlag_x
        self.vlag_y = vlag_y
        self.level_breedte = level_breedte
        self.kogels = []   # Lijst van actieve kogels
        # Alle voorwerpen met gekleurde verf verzamelen (om ze te laten overvloeien)
        self.gekleurd = [o for lijst in (self.platforms, self.vijanden, self.portalen,
                                         self.teleporters, self.springers, self.powerups,
                                         self.decoraties)
                         for o in lijst if getattr(o, "verf_kleuren", None)]
        self._werk_verf_bij()   # meteen de goede kleur zetten (voor de eerste frame)

        # --- Tijd & topscore: houd bij hoe snel je het level haalt ---
        self._speel_tijd = 0.0        # hoe lang je al bezig bent (seconden)
        self._record = False          # heb je je beste tijd verbeterd?
        self._tijd_opgeslagen = False
        if self.twee or self.arena:
            self._tijd_id = None      # geen klok bij meerdere spelers of in de arena
        elif self.eigen:
            self._tijd_id = "eigen_%d" % self.bouw_slot
        elif self.race:
            self._tijd_id = "race_%d" % nummer
        elif self.vlucht:
            self._tijd_id = "vlucht_%d" % nummer
        else:
            self._tijd_id = "level_%d" % nummer
        self._beste_tijd = voortgang_module.beste_tijd(self._tijd_id) if self._tijd_id else None

        # Bepaal of de speler genoeg punten heeft voor dit bonus-level
        # (in de arena bestaat deze waarschuwing niet)
        benodigde_punten = {} if (self.arena or self.race or self.eigen) else {6: 10, 7: 20, 8: 30, 9: 70}
        if nummer in benodigde_punten and self.punten < benodigde_punten[nummer]:
            self._waarschuwing = (f"⚠️  Let op! Dit level heeft minimaal "
                                  f"{benodigde_punten[nummer]} punten nodig. "
                                  f"Jij hebt er {self.punten}. Verslaan monsters voor meer punten!")
            self._waarschuwing_teller = 300   # 5 seconden zichtbaar
        else:
            self._waarschuwing = ""
            self._waarschuwing_teller = 0

        # Start de juiste muziek voor dit level — of stop die als jij een eigen
        # deuntje hebt gemaakt (dat speelt dan in plaats van de level-muziek).
        if self._heeft_muziek:
            geluid_manager.stop_muziek()
        else:
            geluid_manager.speel_muziek(nummer)

    def on_draw(self):
        """Teken alles op het scherm."""
        self.clear()

        # In de 2-spelers-modus tekenen we het scherm (groot) in twee helften
        if self.twee:
            self._teken_acht(self.spelers[0].x, self.window.width, self.window.height)
            self._teken_twee()
            return

        # --- Teken eerst de achtergrond (kan per plek in het level verschillen) ---
        self._teken_acht(self.speler.x, SCHERM_BREEDTE, SCHERM_HOOGTE)

        # --- Alleen tekenen wat in beeld is (scheelt heel veel bij lange banen!) ---
        cam_x = max(SCHERM_BREEDTE / 2,
                    min(self.speler.x + self.speler.breedte / 2,
                        self.level_breedte - SCHERM_BREEDTE / 2))
        links_zicht = cam_x - SCHERM_BREEDTE / 2 - 60
        rechts_zicht = cam_x + SCHERM_BREEDTE / 2 + 60

        def in_beeld(obj, breedte=0):
            # Staat dit object (deels) in het zichtbare stuk?
            return obj.x + breedte >= links_zicht and obj.x <= rechts_zicht

        # --- Teken de spelwereld met de camera ---
        # Alles binnen dit blok beweegt mee met de camera
        with self.camera.activate():

            # Teken alleen de platforms die in beeld zijn (onzichtbare verf-blokken NIET)
            for platform in self.platforms:
                if in_beeld(platform, platform.breedte) and not getattr(platform, "onzichtbaar", False):
                    self._anim_teken(platform)

            # Teken alleen de vijanden die in beeld zijn
            for vijand in self.vijanden:
                if in_beeld(vijand, vijand.breedte) and not getattr(vijand, "onzichtbaar", False):
                    self._anim_teken(vijand)

            # Teken de spring-bollen en spring-matten
            for springer in self.springers:
                if in_beeld(springer, springer.breedte) and not getattr(springer, "onzichtbaar", False):
                    self._anim_teken(springer)

            # Teken de power-ups die nog niet opgepakt zijn en in beeld zijn
            for powerup in self.powerups:
                if (not powerup.opgepakt and in_beeld(powerup, powerup.breedte)
                        and not getattr(powerup, "onzichtbaar", False)):
                    self._anim_teken(powerup)

            # Teken de vlag (in de arena is er geen vlag)
            if not self.arena:
                self._teken_vlag(self.vlag_x, self.vlag_y)

            # Teken de checkpoints (tussenpunten)
            for cp in self.checkpoints:
                if in_beeld(cp, cp.breedte):
                    cp.teken()

            # Teken de portalen die in beeld zijn (vorm-wissel poortjes)
            for portaal in self.portalen:
                if in_beeld(portaal, portaal.breedte) and not getattr(portaal, "onzichtbaar", False):
                    self._anim_teken(portaal)

            # Teken de teleporters (blauw <-> oranje paren)
            for tele in self.teleporters:
                if in_beeld(tele, tele.breedte) and not getattr(tele, "onzichtbaar", False):
                    self._anim_teken(tele)

            # Decoratie helemaal VOORAAN tekenen (vóór blokken, spikes, alles) — geen botsing.
            # Met onzichtbare verf overgeschilderde decoratie tekenen we NIET.
            for deco in self.decoraties:
                if in_beeld(deco, deco.breedte) and not getattr(deco, "onzichtbaar", False):
                    self._anim_teken(deco)

            # Teken de tekstbordjes die in beeld zijn (bovenop de decoratie, goed leesbaar)
            for bord in self.borden:
                if in_beeld(bord, bord.breedte):
                    bord.teken()

            # Teken de kogels
            for kogel in self.kogels:
                kogel.teken()

            # Teken de speler (en zijn spiegel-kloon als die er is)
            self.speler.teken()
            self._teken_kloon(self.speler)

            # Tienkamp: het is nacht! Alleen rond jezelf is een lichtje.
            if self.speler._kamp("nacht") and not self.twee:
                self._teken_nacht(self.speler)

        # --- Teken de berichten buiten de camera (altijd midden op het scherm) ---

        # Levelnaam altijd bovenin (arena krijgt een korte naam + pijltjes in het midden)
        if self.frameperfect:
            naam_tekst = "🎯 Frame Perfect — spring precies op tijd!"
        elif self.testruimte:
            naam_tekst = "🧪 Testruimte — N = volgende, P = kiezen (nu: %s)" % self.speler.modus
        elif self.eigen:
            naam_tekst = "🔨 Jouw eigen level"
        elif self.vlucht:
            naam_tekst = f"✈️ Vlucht — Baan {self.huidig_level}"
        elif self.race:
            naam_tekst = f"🏁 {levels_module.race_naam(self.huidig_level)}"
        elif self.arena:
            naam_tekst = "⚔️ Vechtmodus"
        else:
            naam = LEVEL_NAMEN.get(self.huidig_level) or f"Oneindig Level {self.huidig_level}"
            naam_tekst = f"Level {self.huidig_level}: {naam}"
        arcade.draw_text(naam_tekst,
                         10, SCHERM_HOOGTE - 30, arcade.color.WHITE, 16, bold=True)

        # Klok: hoe lang je al bezig bent, en je beste tijd (midden bovenin)
        if self._tijd_id:
            tekst = "⏱ %.1fs" % self._speel_tijd
            if self._beste_tijd is not None:
                tekst += "   🏆 %.1fs" % self._beste_tijd
            arcade.draw_text(tekst, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 30,
                             arcade.color.WHITE, 15, bold=True, anchor_x="center")

        # Elementmeester: laat zien welke vorm je nu bent en welke hierna komt
        if self.speler.modus == "element" and not self.twee:
            self._teken_element_hud(self.speler)
        if self.speler.modus == "elementkoning" and not self.twee:
            ek.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 86)
        if self.speler.modus == "bouwmeester" and not self.twee:
            self._teken_bouw_hud(self.speler)
        if self.speler.modus == "portaalschieter" and not self.twee:
            ps.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 86)
        if self.speler.modus == "drakentemmer" and not self.twee:
            dt.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 96)
        if self.speler.modus == "mierenkolonie" and not self.twee:
            mk.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 86)
        if self.speler.modus == "schilder" and not self.twee:
            sv.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 92)
        if self.speler.modus == "evolutie" and not self.twee:
            evo.teken_hud(self.speler, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 86)
            if self.speler._evo_kiezen and not self.dood:
                evo.teken_keuze(self.speler)

        # Sleutel-teller (alleen tonen als je sleutels hebt)
        if self.speler.sleutels > 0:
            arcade.draw_text("🔑 x %d" % self.speler.sleutels, SCHERM_BREEDTE // 2, SCHERM_HOOGTE - 54,
                             (240, 200, 40), 14, bold=True, anchor_x="center")

        # Pijltjes bovenin het midden om van monster-level te wisselen (alleen arena)
        if self.arena:
            self._teken_arena_pijltjes()

        # Race- en vliegtuig-modus: voortgangsbalk bovenin (zoals in Geometry Dash!)
        if self.race or self.vlucht:
            self._teken_voortgangsbalk()
        elif not self.eigen:
            # Punten rechtsboven (niet in de race- of bouwmodus)
            snelheid_extra = self.speler.snelheid_bonus
            punten_tekst = f"⭐ {self.punten} punten"
            if snelheid_extra > 0:
                punten_tekst += f"  💨 +{snelheid_extra} snelheid"
            arcade.draw_text(punten_tekst, SCHERM_BREEDTE - 280, SCHERM_HOOGTE - 30,
                             arcade.color.YELLOW, 16, bold=True)

        # Levens weergeven (hartjes)
        self._teken_levens_hud()

        # Power-up icoontjes als een effect actief is
        self._teken_actieve_effecten()

        # Waarschuwing voor bonus-levels (als speler te weinig punten heeft)
        if self._waarschuwing_teller > 0:
            arcade.draw_lrbt_rectangle_filled(20, SCHERM_BREEDTE - 20, 60, 110, (80, 40, 0))
            arcade.draw_lrbt_rectangle_outline(20, SCHERM_BREEDTE - 20, 60, 110,
                                               arcade.color.ORANGE, 2)
            arcade.draw_text(self._waarschuwing, 30, 78,
                             arcade.color.ORANGE, 11, width=SCHERM_BREEDTE - 60,
                             multiline=True)

        # K-toets hint linksonder
        arcade.draw_text("K = kaart", 10, 10, arcade.color.WHITE, 13)

        # De berichten staan altijd netjes in het midden van het scherm
        mx = SCHERM_BREEDTE // 2
        my = SCHERM_HOOGTE // 2

        def bericht_box(kleur):
            arcade.draw_lrbt_rectangle_filled(mx - 300, mx + 300, my - 90, my + 90, kleur)

        def bericht(tekst, dy, kleur=arcade.color.WHITE, grootte=18, vet=False):
            arcade.draw_text(tekst, mx, my + dy, kleur, grootte, bold=vet, anchor_x="center")

        if self.game_over:
            bericht_box((80, 0, 0))
            bericht("💀 Game Over! 💀", 20, grootte=28, vet=True)
            if self.arena:
                bericht(f"Je haalde arena-level {self.huidig_level}!", -12,
                        arcade.color.YELLOW, 16, True)
                bericht("Druk op R om terug naar de kaart te gaan", -45, grootte=16)
            else:
                bericht("Druk op R om opnieuw te beginnen", -40)
        elif self.gewonnen:
            bericht_box(arcade.color.DARK_GREEN)
            bericht("🎉 Je hebt het hele spel uitgespeeld! 🎉", 20, grootte=22, vet=True)
            bericht("Druk op R om terug naar de kaart te gaan", -40)
        elif self.level_gehaald:
            bericht_box(arcade.color.DARK_BLUE)
            if self.eigen:
                bericht("🎉 Je eigen level gehaald! 🎉", 20, grootte=22, vet=True)
                bericht("ENTER of K = terug naar bouwen", -40, grootte=16)
            elif self.vlucht:
                bericht("✈️ Finish! Baan gevlogen! ✈️", 20, grootte=24, vet=True)
                bericht("ENTER = volgende baan  •  K = kaart", -40, grootte=16)
            elif self.race:
                bericht("🏁 Finish! Baan gehaald! 🏁", 20, grootte=24, vet=True)
                bericht("ENTER = volgende baan  •  K = kaart", -40, grootte=16)
            elif self.arena:
                bericht("Alle monsters verslagen! 🎉", 20, grootte=24, vet=True)
                bericht("ENTER = volgend monster-level  •  K = kaart", -40, grootte=16)
            else:
                bericht(f"Level {self.huidig_level} gehaald! 🎉", 20, grootte=26, vet=True)
                bericht("Druk op ENTER om terug naar de kaart te gaan", -40)
            # Je tijd en topscore laten zien
            if self._tijd_id and self._tijd_opgeslagen:
                t = "⏱ Tijd: %.1fs" % self._speel_tijd
                if self._record:
                    t += "   🏆 Nieuw record!"
                elif self._beste_tijd is not None:
                    t += "   Beste: %.1fs" % self._beste_tijd
                bericht(t, -12, arcade.color.YELLOW, 15, True)
        elif self.dood:
            bericht_box(arcade.color.DARK_RED)
            bericht("Oeps! Je ging af!", 20, grootte=26, vet=True)
            if self.arena or self.race or self.eigen:
                bericht("Maar je verliest GEEN leven! 😎", -12, arcade.color.YELLOW, 16, True)
                if self.race:
                    herstart = "Druk op R om deze baan opnieuw te racen"
                elif self.eigen:
                    herstart = "Druk op R om je eigen level opnieuw te spelen"
                else:
                    herstart = "Druk op R om dit monster-level opnieuw te doen"
                bericht(herstart, -45, grootte=16)
            else:
                bericht("Druk op R om dit level opnieuw te spelen", -40)

        # Vrolijk vuurwerk als je gewonnen hebt
        if self.level_gehaald or self.gewonnen:
            self._teken_vuurwerk()

    def _teken_vlag(self, x, y):
        """Teken een vlag op de gegeven positie."""
        # Vlaggestok
        arcade.draw_line(x, y, x, y + 60, VLAG_KLEUR, 3)
        # Vlagdoek (groen driehoekje)
        arcade.draw_triangle_filled(x, y + 60, x + 30, y + 48, x, y + 36, VLAG_DOEK_KLEUR)

    def _teken_levens_hud(self):
        """Teken de levens als hartjes rechtsboven in het scherm."""
        # In de vecht-, race- en bouwmodus heb je oneindig levens: toon één hartje met ∞
        if self.arena or self.race or self.eigen:
            cx = SCHERM_BREEDTE - 34
            cy = SCHERM_HOOGTE - 20
            arcade.draw_circle_filled(cx - 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_circle_filled(cx + 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_triangle_filled(cx - 10, cy + 2, cx + 10, cy + 2, cx, cy - 8,
                                        arcade.color.RED)
            arcade.draw_text("∞", cx + 14, cy - 10, arcade.color.WHITE, 20, bold=True)
            return
        for i in range(self.speler.levens):
            cx = SCHERM_BREEDTE - 30 - i * 36
            cy = SCHERM_HOOGTE - 20
            # Hartje (twee cirkeltjes + driehoekje)
            arcade.draw_circle_filled(cx - 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_circle_filled(cx + 5, cy + 4, 7, arcade.color.RED)
            arcade.draw_triangle_filled(cx - 10, cy + 2, cx + 10, cy + 2, cx, cy - 8,
                                        arcade.color.RED)

    def _teken_actieve_effecten(self):
        """Teken kleine icoontjes voor actieve power-up effecten."""
        x = 10
        y = SCHERM_HOOGTE - 60
        if self.speler.onkwetsbaar_timer > 0:
            arcade.draw_text("⭐", x, y, arcade.color.YELLOW, 18)
            x += 30
        if self.speler.snelheid_boost_timer > 0:
            arcade.draw_text("💨", x, y, arcade.color.WHITE, 18)
            x += 30
        if self.speler.dubbel_sprong_timer > 0:
            arcade.draw_text("🦘", x, y, arcade.color.WHITE, 18)
            x += 30
        if self.speler.schiet_timer > 0:
            arcade.draw_text("🔫", x, y, arcade.color.WHITE, 18)

    def _teken_arena_pijltjes(self):
        """Teken de klikbare pijltjes ◀ ▶ bovenin het midden (alleen vechtmodus)."""
        ll, lr, lb, lt = self.ARENA_PIJL_LINKS
        rl, rr, rb, rt = self.ARENA_PIJL_RECHTS
        lcy = (lb + lt) / 2
        rcy = (rb + rt) / 2
        kan_links = self.huidig_level > 1
        kan_rechts = self.huidig_level < self._arena_top

        # Knop-achtergrondjes
        arcade.draw_lrbt_rectangle_filled(ll, lr, lb, lt, (0, 0, 0, 150))
        arcade.draw_lrbt_rectangle_filled(rl, rr, rb, rt, (0, 0, 0, 150))

        # Linker pijl (wijst naar links) — grijs als je al op level 1 bent
        kleur_l = arcade.color.WHITE if kan_links else (110, 110, 110)
        arcade.draw_triangle_filled(ll + 8, lcy, lr - 7, lt - 6, lr - 7, lb + 6, kleur_l)

        # Rechter pijl (wijst naar rechts) — grijs als je al op je hoogste level bent
        kleur_r = arcade.color.WHITE if kan_rechts else (110, 110, 110)
        arcade.draw_triangle_filled(rr - 8, rcy, rl + 7, rt - 6, rl + 7, rb + 6, kleur_r)

        # Het levelnummer tussen de pijltjes
        arcade.draw_text(f"Level {self.huidig_level}", SCHERM_BREEDTE // 2, lb + 7,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

        # Reset-knop rechtsboven: begin helemaal opnieuw bij level 1
        # (dezelfde rode kleur als het hartje)
        pl, pr, pb, pt = self.ARENA_RESET_KNOP
        arcade.draw_lrbt_rectangle_filled(pl, pr, pb, pt, arcade.color.RED)
        arcade.draw_lrbt_rectangle_outline(pl, pr, pb, pt, (255, 220, 150), 2)
        arcade.draw_text("🔄 Reset", (pl + pr) / 2, pb + 6,
                         arcade.color.WHITE, 13, bold=True, anchor_x="center")

    def _teken_voortgangsbalk(self):
        """Teken bovenin een balk die laat zien hoe ver je in de baan bent."""
        doel = self.vlag_x if self.vlag_x > 0 else self.level_breedte
        voortgang = max(0.0, min(self.speler.x / doel, 1.0))
        l, r = SCHERM_BREEDTE // 2 - 520, SCHERM_BREEDTE // 2 + 520
        b, t = SCHERM_HOOGTE - 24, SCHERM_HOOGTE - 9
        # Achtergrond van de balk
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, (40, 40, 55))
        # Het groene gevulde deel (hoe ver je bent)
        if voortgang > 0:
            arcade.draw_lrbt_rectangle_filled(l, l + (r - l) * voortgang, b, t, (80, 220, 90))
        # Wit randje
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
        # Percentage in het midden
        arcade.draw_text(f"{int(voortgang * 100)}%", (l + r) / 2, b,
                         arcade.color.WHITE, 11, bold=True, anchor_x="center")

    def on_update(self, delta_time):
        """Werk het spel bij — dit wordt heel snel herhaald."""

        self._verf_tijd += 1        # tikt door voor de overvloeiende verf-kleuren
        self._werk_verf_bij()       # zet de huidige kleur op elk gekleurd voorwerp
        self._anim_t += delta_time  # tikt door voor 'alles beweegt'

        # Je eigen deuntje afspelen (loopt steeds rond)
        if self._heeft_muziek:
            self._muziek_teller += delta_time
            if self._muziek_teller >= 0.22:
                self._muziek_teller -= 0.22
                noot = self.muziek[self._muziek_stap]
                if noot != -1:
                    import muziek as muziek_module
                    muziek_module.speel_noot(noot)
                self._muziek_stap = (self._muziek_stap + 1) % len(self.muziek)

        # Vuurwerk zolang je gewonnen hebt
        if self.level_gehaald or self.gewonnen:
            self._update_vuurwerk(delta_time)

        # Level gehaald? Bewaar je tijd (en kijk of het een record is) — één keer.
        if (self.level_gehaald or self.gewonnen) and self._tijd_id and not self._tijd_opgeslagen:
            self._tijd_opgeslagen = True
            self._beste_tijd, self._record = voortgang_module.sla_tijd_op(
                self._tijd_id, self._speel_tijd)

        # 2-spelers-modus heeft zijn eigen (split-screen) update
        if self.twee:
            self._update_twee()
            return

        # Als het spel voorbij is, doe niets meer
        if self.gewonnen or self.game_over or self.level_gehaald:
            return

        # Als de speler dood is, wacht op toetsinvoer (wordt hierboven al getekend)
        if self.dood:
            return

        # Evolutie: tijdens het kiezen van een mutatie staat het spel even stil
        if self.speler.modus == "evolutie" and self.speler._evo_kiezen and not self.twee:
            return

        # De klok loopt terwijl je speelt (niet als je dood of klaar bent)
        if self._tijd_id:
            self._speel_tijd += delta_time

        self._update_platforms()      # verdwijnblokken aftellen

        # In de race-, vliegtuig- én frame-perfect-modus ga je VANZELF naar rechts
        if self.race or self.vlucht or self.frameperfect:
            if self.frameperfect and self.speler.modus == "spiegel":
                # Spiegel draait links/rechts om, dus 'links' indrukken = vooruit
                self.speler.links_ingedrukt = True
                self.speler.rechts_ingedrukt = False
            else:
                self.speler.rechts_ingedrukt = True
                self.speler.links_ingedrukt = False

        # In de vasthoud-modi (vliegtuig, golf, robot): geef door of de knop vastgehouden wordt
        if (self.speler.modus in ("vliegtuig", "golf", "robot", "ballon", "raket", "draak", "dronken", "spook")
                or self.speler._kamp("vasthouden")
                or self.speler.modus in ("element", "elementkoning", "drakentemmer", "evolutie")):
            self.speler.vlieg_omhoog = self._vlieg_omhoog

        # Laat de speler bewegen en botsingen controleren
        self.speler.bijwerken(self.level_breedte, self.platforms)

        # Ging de speler door een portaal? Dan wisselt zijn vorm of zijn snelheid
        self._pas_portalen_toe(self.speler, self._vorige_speler_x)
        self._vorige_speler_x = self.speler.x   # onthouden voor de volgende stap

        # Spring-matten (vanzelf) en spring-bollen (onthoud dat je erop staat)
        self._check_springers(self.speler)

        # Teleporters: spring van blauw naar oranje (en andersom)
        self._check_teleport(self.speler)

        # Deuren: open ze met een sleutel
        self._check_deuren(self.speler)

        # Checkpoints: raak je er een aan, dan is dat je nieuwe startpunt
        self._check_checkpoints(self.speler)

        # Volg-voorwerpen (volg-kwast) laten meelopen met de speler
        self._update_volgers()

        # Draaien hangt af van de modus
        self._pas_rotatie_toe(self.speler)

        # Botste de speler tegen de zijkant van een blok? Dan ga je dood.
        if self._check_blok_zijkant():
            return

        # Beweeg de kloon (dubbel-portaal) met de speler mee
        kloon_raakt = self._update_kloon(self.speler, self._vlieg_omhoog)

        # Waarschuwingstimer aftellen
        if self._waarschuwing_teller > 0:
            self._waarschuwing_teller -= 1

        # Is de speler in een kuil gevallen, of ging zijn kloon ergens tegenaan?
        if self.speler.is_gevallen() or kloon_raakt:
            self._speler_geraakt()
            return

        # Bouwmeester: op echte grond geland? Dan komen je oude blokjes terug
        if getattr(self.speler, "_bouw_terug", False):
            self.speler._bouw_terug = False
            self.platforms = [p for p in self.platforms if not getattr(p, "is_bouwblok", False)]

        # Schilder: witte wolkjes in het level zetten (en opgeloste weghalen)
        if self.speler.modus == "schilder" or any(getattr(p, "is_wolk", False) for p in self.platforms):
            wolken = self.speler._sv_wolken if self.speler.modus == "schilder" else []
            self.platforms = [p for p in self.platforms if not getattr(p, "is_wolk", False) or p in wolken]
            for w in wolken:
                if w not in self.platforms:
                    self.platforms.append(w)

        # Mierenkolonie: toren/brug in het level zetten, en raken de volg-mieren iets?
        if self.speler.modus == "mierenkolonie" or any(
                getattr(p, "is_mierwerk", False) for p in self.platforms):
            self._mier_sync(self.speler)
        if self.speler.modus == "mierenkolonie":
            self._mieren_geraakt(self.speler)

        # Drakentemmer: vuurballen en de vuurstorm verslaan monsters (en de storm smelt spikes)
        if self.speler.modus == "drakentemmer":
            self._draak_vuur(self.speler)

        # Elementmeester: een aarde-schokgolf blaast monsters in de buurt weg
        self._element_schokgolf(self.speler)

        # Kamp-onderdeel 'spike-magneet': spikes vlakbij trekken je naar zich toe
        if self.speler._kamp("spikemagneet"):
            self._spike_magneet(self.speler)

        # Tienkamp: te hard geland of je hoofd gestoten? Dan ga je af!
        if getattr(self.speler, "_au", False):
            self.speler._au = False
            if not self.speler.is_onkwetsbaar():
                self._speler_geraakt()
                return

        # Schaduw-poppetje: raakt de schaduw (je oude ik) je aan, dan ga je af!
        if ((self.speler.modus == "schaduw" or self.speler._kamp("schaduw"))
                and not self.speler.is_onkwetsbaar()):
            pos = self.speler.schaduw_pos()
            if (pos is not None
                    and abs(pos[0] - self.speler.x) < self.speler.breedte
                    and abs(pos[1] - self.speler.y) < self.speler.hoogte):
                self._speler_geraakt()
                return

        # --- Camera laten meebewegen met de speler ---
        cam_x = self.speler.x + self.speler.breedte / 2
        cam_x = max(SCHERM_BREEDTE / 2, min(cam_x, self.level_breedte - SCHERM_BREEDTE / 2))
        self.camera.position = cam_x, self._camera_y(self.speler)
        # Kamp-onderdeel 'ondersteboven': het hele beeld staat op z'n kop!
        if self.speler._kamp("ondersteboven"):
            self.camera.angle = 180
            # Op z'n kop staat de grond bovenin; zet de camera zo dat je het
            # poppetje goed ziet (een stukje boven het midden van het scherm)
            self.camera.position = cam_x, self.speler.y + self.speler.hoogte / 2 + 50
        else:
            self.camera.angle = 0

        # --- Power-ups bijwerken en oppakken ---
        for powerup in self.powerups:
            if not powerup.opgepakt:
                powerup.bijwerken()
                if powerup.raakt_speler(self.speler.x, self.speler.y,
                                        self.speler.breedte, self.speler.hoogte):
                    powerup.toepassen(self.speler)
                    powerup.opgepakt = True
                    geluid_manager.speel_powerup()  # 🎵 Power-up geluid!

        # --- Vijanden bijwerken en controleren ---
        vijanden_weg = []
        nieuwe_vijanden = []   # monsters die de arena-baas oproept
        speler_cx = self.speler.x + self.speler.breedte / 2
        for vijand in self.vijanden:
            if not (self.speler.modus == "schilder" and not getattr(vijand, "is_spike", False)
                    and sv.in_modder(self.speler, vijand)):
                vijand.bijwerken(speler_cx)          # (in bruine modder zit een monster vast)

            # De arena-baas kan kleine monsters oproepen
            if getattr(vijand, 'nieuwe_monsters', None):
                nieuwe_vijanden.extend(vijand.nieuwe_monsters)
                vijand.nieuwe_monsters = []

            # Landt de speler van bovenaf op de vijand?
            # Eerlijk: het telt als een stomp zodra je naar beneden valt,
            # OF als je voeten in de bovenste helft van het monster zitten.
            # Zo ga je niet meer 'af' als een monster omhoog in je springt.
            speler_voeten = self.speler.y
            vijand_midden = vijand.y + vijand.hoogte / 2
            van_boven = (self.speler.snelheid_y < 0) or (speler_voeten >= vijand_midden)
            if (van_boven and
                    vijand.speler_springt_erop(self.speler.x, self.speler.y,
                                               self.speler.breedte, self.speler.hoogte)):
                if hasattr(vijand, 'word_gestompt'):
                    vijand.word_gestompt()
                    if vijand.levens <= 0:
                        vijanden_weg.append(vijand)
                        self._voeg_punt_toe()   # 🏆 Punt voor stompen!
                else:
                    vijanden_weg.append(vijand)
                    self._voeg_punt_toe()       # 🏆 Punt voor stompen!
                self.speler.snelheid_y = SPRING_KRACHT / 2
                if self.speler.modus == "mierenkolonie":
                    mk.mier_erbij(self.speler)    # monster opgegeten: een nieuwe mier!
                if self.speler.modus == "evolutie":
                    evo.dna_erbij(self.speler, evo.DNA_PER_MONSTER)   # monster = DNA
                geluid_manager.speel_vijand_dood()  # 🎵 Boing!

            # Raakt de vijand de speler? Alleen gevaarlijk als de speler NIET onkwetsbaar is!
            elif (not self.speler.is_onkwetsbaar() and
                  vijand.raakt_speler(self.speler.x, self.speler.y,
                                      self.speler.breedte, self.speler.hoogte)):
                if getattr(vijand, "geverfd", False):
                    gevolg = "veilig"             # groen geverfde spike: onschadelijk
                else:
                    gevolg = self._elementkoning_raakt(vijand)
                if gevolg == "weg":
                    vijanden_weg.append(vijand)   # lava smolt de spike / gif versloeg het monster
                elif gevolg != "veilig":          # (veilig = kristal stuitert op de spike)
                    self._speler_geraakt()

        # Verwijder de dode vijanden uit de lijst
        for vijand in vijanden_weg:
            self.vijanden.remove(vijand)

        # Voeg de door de baas opgeroepen monsters toe
        self.vijanden.extend(nieuwe_vijanden)

        # --- Kogels bijwerken en vijanden raken ---
        for kogel in self.kogels:
            kogel.bijwerken(self.level_breedte)
            for vijand in self.vijanden[:]:
                if getattr(vijand, 'is_spike', False):
                    continue   # spikes kun je niet kapotschieten
                if kogel.actief and kogel.raakt_vijand(vijand):
                    kogel.actief = False
                    if hasattr(vijand, 'word_gestompt'):
                        vijand.word_gestompt()
                        if vijand.levens <= 0:
                            self.vijanden.remove(vijand)
                            self._voeg_punt_toe()   # 🏆 Punt voor kogel!
                    else:
                        self.vijanden.remove(vijand)
                        self._voeg_punt_toe()       # 🏆 Punt voor kogel!
                    geluid_manager.speel_vijand_dood()

        # Verwijder kogels die niet meer actief zijn
        self.kogels = [k for k in self.kogels if k.actief]

        # --- Eigen (zelfgebouwd) level: win als je de finishvlag bereikt ---
        if self.eigen:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    self.speler.y < self.vlag_y + 60 and not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
            return

        # --- Vliegtuig-modus: win als je de finishvlag bereikt ---
        if self.vlucht:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                voortgang_module.sla_vlucht_record_op(self.huidig_level)  # record bewaren
            return

        # --- Racemodus: win als je de finishvlag bereikt ---
        if self.race:
            if (self.speler.x + self.speler.breedte > self.vlag_x and
                    self.speler.y < self.vlag_y + 60 and not self.level_gehaald):
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                voortgang_module.sla_race_record_op(self.huidig_level)   # record bewaren
            return

        # --- Arena/vechtmodus: win als ALLE monsters verslagen zijn ---
        # (spikes tellen niet mee — die kun je toch niet doden!)
        if self.arena:
            levende = [v for v in self.vijanden if not getattr(v, 'is_spike', False)]
            if len(levende) == 0 and not self.level_gehaald:
                self.level_gehaald = True
                geluid_manager.speel_level_gehaald()
                # Bewaar het record (hoogste gehaalde arena-level)
                voortgang_module.sla_arena_record_op(self.huidig_level)
            return

        # --- In level 9: win als de eindbaas verslagen is ---
        if self.huidig_level == AANTAL_LEVELS and len(self.vijanden) == 0:
            self.voltooid = voortgang_module.markeer_level_voltooid(
                self.huidig_level, self.voltooid, self.punten, self.speler.levens)
            self.gewonnen = True
            geluid_manager.speel_level_gehaald()
            return

        # --- Heeft de speler de vlag bereikt? ---
        if (self.speler.x + self.speler.breedte > self.vlag_x and
                self.speler.x < self.vlag_x + 10 and
                self.speler.y < self.vlag_y + 60):
            # Markeer dit level als voltooid (sla op in het bestand)
            self.voltooid = voortgang_module.markeer_level_voltooid(
                self.huidig_level, self.voltooid, self.punten, self.speler.levens)
            # In een oneindig spel is er geen 'laatste' level:
            # elke vlag betekent gewoon "level gehaald, door naar het volgende!"
            self.level_gehaald = True
            geluid_manager.speel_level_gehaald()  # 🎵 Fanfare!

    def _voeg_punt_toe(self):
        """Geef de speler 1 punt. Elke 10 punten: sneller én hoger springen!"""
        self.punten += 1
        # De speciale modi (vecht/race/vlucht/bouw) tellen apart: geen bonus, geen opslaan.
        if not (self.arena or self.race or self.vlucht or self.eigen):
            bonus = self.punten // 10
            self.speler.snelheid_bonus = bonus
            self.speler.sprong_bonus = bonus  # Elke 10 punten ook iets hoger springen
            try:
                voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
            except Exception:
                pass

    # Welke modus hoort bij welk portaal-soort
    PORTAAL_MODUS = {"vlucht": "vliegtuig", "blok": "blok",
                     "ufo": "ufo", "bal": "bal", "golf": "golf",
                     "robot": "robot", "spin": "spin", "heli": "heli",
                     "draaibol": "draaibol", "ballon": "ballon", "raket": "raket",
                     "kolibrie": "kolibrie", "draak": "draak", "ijs": "ijs", "ninja": "ninja",
                     "spiegel": "spiegel", "magneet": "magneet", "flits": "flits",
                     "dobbelsteen": "dobbelsteen", "vertraagd": "vertraagd",
                     "chaos": "chaos", "dronken": "dronken",
                     "turbo": "turbo", "ritme": "ritme",
                     "stuiteraar": "stuiteraar", "klimmer": "klimmer",
                     "draaisturing": "draaisturing", "boemerang": "boemerang",
                     "stamper": "stamper", "zweefspringer": "zweefspringer", "groeier": "groeier",
                     "zwaargewicht": "zwaargewicht", "versneller": "versneller",
                     "wind": "wind", "plakker": "plakker",
                     "metronoom": "metronoom", "katapult": "katapult",
                     "krimpsprong": "krimpsprong", "tegendraads": "tegendraads",
                     "turboflip": "turboflip", "spiegelkatapult": "spiegelkatapult",
                     "schaduw": "schaduw", "pingpong": "pingpong",
                     "spook": "spook", "vleermuis": "vleermuis",
                     "zombie": "zombie", "pompoenkop": "pompoenkop",
                     "voorspeller": "voorspeller", "pendel": "pendel",
                     "blinde": "blinde", "dubbelflip": "dubbelflip",
                     "vijfkamp": "vijfkamp", "tienkamp": "tienkamp",
                     "vijftienkamp": "vijftienkamp", "twintigkamp": "twintigkamp",
                     "element": "element", "elementkoning": "elementkoning",
                     "bouwmeester": "bouwmeester", "portaalschieter": "portaalschieter",
                     "drakentemmer": "drakentemmer", "mierenkolonie": "mierenkolonie",
                     "evolutie": "evolutie", "schilder": "schilder",
                     "eigen": "eigen"}

    def _pas_rotatie_toe(self, sp):
        """Zet de draai-stand van een speler op basis van zijn modus."""
        modus = sp.modus
        if modus == "vliegtuig":
            sp.rotatie = max(-35, min(35, sp.snelheid_y * 5))     # neus kantelt
        elif modus == "golf":
            sp.rotatie = 35 if sp.vlieg_omhoog else -35            # schuin omhoog/omlaag
        elif modus == "bal":
            sp.rotatie = (sp.rotatie - 7) % 360                    # rollen
        elif modus == "draaibol":
            pass                                                  # tolt al in zijn eigen natuurkunde
        elif modus == "eigen":
            # Zelfgemaakt poppetje: tolt rond als het 'Draaien'-kunstje aanstaat, anders recht
            if sp.eigen_instel and sp.eigen_instel.get("draaien"):
                sp.rotatie = (sp.rotatie + 6) % 360
            else:
                sp.rotatie = 0
        elif modus in ("ufo", "robot", "spin", "heli", "ballon", "raket",
                       "kolibrie", "draak", "ijs", "ninja",
                       "spiegel", "magneet", "flits",
                       "dobbelsteen", "vertraagd", "chaos", "dronken",
                       "turbo", "ritme", "stuiteraar", "klimmer", "draaisturing",
                       "boemerang", "stamper", "zweefspringer", "groeier",
                       "zwaargewicht", "versneller", "wind", "plakker",
                       "metronoom", "katapult", "krimpsprong", "tegendraads",
                       "turboflip", "spiegelkatapult", "schaduw", "pingpong",
                       "spook", "vleermuis", "zombie", "pompoenkop",
                       "voorspeller", "pendel", "blinde", "dubbelflip", "vijfkamp", "tienkamp",
                       "vijftienkamp", "twintigkamp", "element",
                       "elementkoning", "bouwmeester", "portaalschieter", "drakentemmer",
                       "mierenkolonie", "evolutie", "schilder"):
            sp.rotatie = 0                                         # recht
        elif self.race or self.vlucht:
            if sp.staat_op_grond:
                sp.rotatie = round(sp.rotatie / 90) * 90 % 360
            else:
                sp.rotatie = (sp.rotatie + 8) % 360                # tollen in de lucht

    def _spin_teleport(self, sp):
        """Spin-modus: draai de zwaartekracht om en teleporteer naar de andere kant."""
        sp.zwaartekracht_richting *= -1
        sp.snelheid_y = 0
        overlap = lambda p: p.x < sp.x + sp.breedte and p.x + p.breedte > sp.x
        if sp.zwaartekracht_richting == -1:
            # Zwaartekracht omhoog: zoek een platform boven je (of ga naar het plafond)
            doel = VLIEG_PLAFOND - sp.hoogte
            for p in self.platforms:
                if overlap(p) and p.y >= sp.y + sp.hoogte:
                    doel = min(doel, p.y - sp.hoogte)
            sp.y = doel
        else:
            # Zwaartekracht omlaag: zoek een platform onder je (of blijf staan)
            doel = None
            for p in self.platforms:
                if overlap(p) and p.y + p.hoogte <= sp.y:
                    top = p.y + p.hoogte
                    doel = top if doel is None else max(doel, top)
            if doel is not None:
                sp.y = doel

    def _raakt_portaal(self, sp, vorige_x, portaal):
        """Ging deze speler dit frame door het portaal? (Ook bij hoge snelheid via 'sweep'.)"""
        links = min(vorige_x, sp.x)
        rechts = max(vorige_x, sp.x) + sp.breedte
        horizontaal = rechts > portaal.x and links < portaal.x + portaal.breedte
        verticaal = sp.y + sp.hoogte > portaal.y and sp.y < portaal.y + portaal.hoogte
        return horizontaal and verticaal

    def _pas_portalen_toe(self, sp, vorige_x):
        """Ga je door een portaal? Dan verander je van vorm OF van snelheid."""
        for portaal in self.portalen:
            if not self._raakt_portaal(sp, vorige_x, portaal):
                continue
            if portaal.soort == "dubbel":
                # Dubbel-portaal: er komt een tweede kopie van jou uit het portaal
                if sp.kloon is None:
                    self._maak_kloon(sp)
                    geluid_manager.speel_powerup()
            elif portaal.soort == "enkel":
                # Enkel-portaal: je wordt weer één
                if sp.kloon is not None:
                    sp.kloon = None
                    geluid_manager.speel_powerup()
            elif portaal.soort in SNELHEID_FACTOR:
                # Snelheid-portaal: ga langzamer of sneller (x0.5 ... x10)
                # Alleen de speler (de onderste) verandert — de kloon heeft eigen portalen.
                factor = SNELHEID_FACTOR[portaal.soort]
                if sp.snelheid_factor != factor:
                    sp.snelheid_factor = factor
                    geluid_manager.speel_powerup()
            else:
                # Vorm-portaal: verander van poppetje.
                # Alleen de speler verandert; de kloon heeft zijn eigen portalen.
                nieuwe_modus = self.PORTAAL_MODUS.get(portaal.soort, "blok")
                if sp.modus != nieuwe_modus:
                    self._zet_vorm(sp, nieuwe_modus, 1)
                    geluid_manager.speel_powerup()   # 🎵 vorm-wissel geluidje

    def _test_kies(self, modus):
        """Testruimte: je koos een poppetje in de zoeker -> terug naar de testruimte ermee."""
        if modus in self._test_modi:
            self._test_index = self._test_modi.index(modus)
        self.start_modus = modus          # ook na doodgaan blijf je dit poppetje
        self.window.show_view(self)       # terug naar de testruimte (begint netjes opnieuw)

    def _test_volgende(self, stap):
        """Testruimte: wissel naar het volgende (of vorige) poppetje en maak alles schoon."""
        self._test_index = (self._test_index + stap) % len(self._test_modi)
        modus = self._test_modi[self._test_index]
        self.start_modus = modus          # ook na doodgaan blijf je dit poppetje
        sp = self.speler
        self._zet_vorm(sp, modus, 1)
        # Extra dingen netjes terugzetten zodat elk poppetje fris begint
        sp.zet_grootte(1.0, 0)
        sp._anker_x = None
        sp._versnel = 0.0
        sp._versnel_richting = 0
        sp._wind_teller = 0
        sp._wind_richting = 1
        sp._stuur_hoek = 0.0
        sp._flits_teller = 0
        sp._ritme_teller = 0
        self._vlieg_omhoog = False
        geluid_manager.speel_powerup()

    def _zet_vorm(self, sp, nieuwe_modus, richting):
        """Zet een speler (of kloon) netjes in een nieuwe vorm."""
        if nieuwe_modus == "eigen":
            # Zelfgemaakt poppetje: laad de instellingen uit de maker
            sp.eigen_instel = voortgang_module.laad_voortgang().get("eigen_poppetje")
            # Start-grootte: Klein, Groot of gewoon
            if sp.eigen_instel and sp.eigen_instel.get("klein"):
                sp.zet_grootte(0.6, 0)
            elif sp.eigen_instel and sp.eigen_instel.get("groot"):
                sp.zet_grootte(1.6, 0)
            else:
                sp.zet_grootte(1.0, 0)
        sp.modus = nieuwe_modus
        sp.snelheid_y = 0                # netjes overschakelen (geen wilde sprong)
        sp.vlieg_omhoog = False
        sp.zwaartekracht_richting = richting   # kloon = -1 (ondersteboven), speler = 1
        sp._grav_d = 0                   # draaibol begint met zwaartekracht naar beneden
        sp._val_snelheid = 0
        if nieuwe_modus != "vliegtuig":
            sp.rotatie = 0               # weer recht (behalve vliegtuig kantelt)

    def _verf_kleur(self, kleuren):
        """Geef de huidige verf-kleur. Bij meer kleuren vloeit hij langzaam van de
        ene kleur naar de andere (en weer terug)."""
        if len(kleuren) == 1:
            return kleuren[0]
        per = 45                                  # frames per kleur-overgang
        n = len(kleuren)
        t = self._verf_tijd % (per * n)
        i = t // per
        f = (t % per) / per                       # 0.0 -> 1.0 binnen deze overgang
        a = kleuren[i]
        b = kleuren[(i + 1) % n]
        meng = lambda p, q: int(p + (q - p) * f)  # tussen twee getallen in
        return (meng(a[0], b[0]), meng(a[1], b[1]), meng(a[2], b[2]))

    def _werk_verf_bij(self):
        """Zet bij elk gekleurd voorwerp de huidige (overvloeiende) verf-kleur."""
        for o in self.gekleurd:
            o.verf_kleur = self._verf_kleur(o.verf_kleuren)

    def _update_vuurwerk(self, dt):
        """Maak steeds nieuwe vuurwerk-knallen en laat de oude uitdoven."""
        import random
        self._vw_teller = getattr(self, "_vw_teller", 0.0) + dt
        if self._vw_teller >= 0.35:
            self._vw_teller = 0.0
            kleur = random.choice([(255, 80, 80), (255, 220, 60), (90, 200, 255),
                                   (120, 255, 120), (255, 140, 220), (255, 170, 40)])
            self._vuurwerk.append({
                "x": random.randint(80, SCHERM_BREEDTE - 80),
                "y": random.randint(SCHERM_HOOGTE // 2, SCHERM_HOOGTE - 60),
                "kleur": kleur, "t": 0})
        for v in self._vuurwerk:
            v["t"] += 1
        self._vuurwerk = [v for v in self._vuurwerk if v["t"] < 40]

    def _teken_vuurwerk(self):
        """Teken de vuurwerk-knallen (gekleurde deeltjes die naar buiten spatten)."""
        for v in self._vuurwerk:
            t = v["t"]
            r = t * 4
            grootte = max(1, 5 - t * 0.1)
            for hoek in range(0, 360, 30):
                rad = math.radians(hoek)
                px = v["x"] + math.cos(rad) * r
                py = v["y"] + math.sin(rad) * r
                arcade.draw_circle_filled(px, py, grootte, v["kleur"])

    def _anim_teken(self, obj):
        """Teken een voorwerp. Het beweegt in zijn eigen stijl (beweeg-kwast) of, als
        die er niet is, in de stijl van 'alles beweegt'. Alleen visueel; botsing blijft."""
        soort = getattr(obj, "beweeg", None) or getattr(self, "anim_soort", "uit")
        if soort == "draai":
            # Ronddraaien rond het eigen midden (als een wiel). De hoek loopt rond.
            fase = obj.x * 0.5
            hoek = (self._anim_t * 180.0 + fase) % 360
            self._teken_draaiend(obj, hoek)
        elif soort and soort != "uit":
            fase = obj.x * 0.03
            t = self._anim_t
            if soort == "opneer":
                dx, dy = 0, math.sin(t * 3.0 + fase) * 70
            elif soort == "zij":
                dx, dy = math.sin(t * 3.0 + fase) * 70, 0
            elif soort == "rondje":
                dx, dy = math.cos(t * 3.0 + fase) * 50, math.sin(t * 3.0 + fase) * 50
            else:  # wiebel
                dx, dy = math.cos(t * 2.0 + fase) * 30, math.sin(t * 3.0 + fase) * 50
            obj.x += dx
            obj.y += dy
            obj.teken()
            obj.x -= dx
            obj.y -= dy
        else:
            obj.teken()

    def _teken_draaiend(self, obj, hoek):
        """Teken een voorwerp dat rond zijn eigen midden draait (als een wiel).
        Slim trucje: we laten ALLE teken-opdrachten even 'meedraaien' rond het
        midden. Zo kan elk voorwerp draaien zonder dat we het apart hoeven aan te
        passen. Na het tekenen zetten we de gewone teken-opdrachten weer terug."""
        cx = obj.x + getattr(obj, "breedte", 32) / 2
        cy = obj.y + getattr(obj, "hoogte", 32) / 2
        rad = math.radians(hoek)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def rp(px, py):
            """Draai één puntje rond het midden."""
            dx, dy = px - cx, py - cy
            return (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)

        # De ECHTE teken-functies onthouden zodat we ze straks terugzetten
        namen = ("draw_circle_filled", "draw_circle_outline",
                 "draw_lrbt_rectangle_filled", "draw_lrbt_rectangle_outline",
                 "draw_line", "draw_triangle_filled", "draw_triangle_outline",
                 "draw_polygon_filled", "draw_polygon_outline",
                 "draw_ellipse_filled", "draw_ellipse_outline",
                 "draw_arc_outline", "draw_text")
        echt = {n: getattr(arcade, n) for n in namen}

        def cirkel_f(x, y, r, kleur, tilt_angle=0, num_segments=-1):
            nx, ny = rp(x, y)
            echt["draw_circle_filled"](nx, ny, r, kleur, tilt_angle, num_segments)

        def cirkel_o(x, y, r, kleur, border_width=1, tilt_angle=0, num_segments=-1):
            nx, ny = rp(x, y)
            echt["draw_circle_outline"](nx, ny, r, kleur, border_width, tilt_angle, num_segments)

        def rect_f(l, r, b, t, kleur):
            echt["draw_polygon_filled"]([rp(l, b), rp(r, b), rp(r, t), rp(l, t)], kleur)

        def rect_o(l, r, b, t, kleur, border_width=1):
            echt["draw_polygon_outline"]([rp(l, b), rp(r, b), rp(r, t), rp(l, t)], kleur, border_width)

        def lijn(x1, y1, x2, y2, kleur, line_width=1):
            p1, p2 = rp(x1, y1), rp(x2, y2)
            echt["draw_line"](p1[0], p1[1], p2[0], p2[1], kleur, line_width)

        def drie_f(x1, y1, x2, y2, x3, y3, kleur):
            p1, p2, p3 = rp(x1, y1), rp(x2, y2), rp(x3, y3)
            echt["draw_triangle_filled"](p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], kleur)

        def drie_o(x1, y1, x2, y2, x3, y3, kleur, border_width=1):
            p1, p2, p3 = rp(x1, y1), rp(x2, y2), rp(x3, y3)
            echt["draw_triangle_outline"](p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], kleur, border_width)

        def poly_f(punten, kleur):
            echt["draw_polygon_filled"]([rp(px, py) for (px, py) in punten], kleur)

        def poly_o(punten, kleur, line_width=1.0):
            echt["draw_polygon_outline"]([rp(px, py) for (px, py) in punten], kleur, line_width)

        def ellips_f(x, y, w, h, kleur, tilt_angle=0, num_segments=-1):
            nx, ny = rp(x, y)
            echt["draw_ellipse_filled"](nx, ny, w, h, kleur, tilt_angle + hoek, num_segments)

        def ellips_o(x, y, w, h, kleur, border_width=1, tilt_angle=0, num_segments=-1):
            nx, ny = rp(x, y)
            echt["draw_ellipse_outline"](nx, ny, w, h, kleur, border_width, tilt_angle + hoek, num_segments)

        def boog_o(x, y, w, h, kleur, start_angle, end_angle, border_width=1, tilt_angle=0, num_segments=128):
            nx, ny = rp(x, y)
            echt["draw_arc_outline"](nx, ny, w, h, kleur, start_angle, end_angle,
                                     border_width, tilt_angle + hoek, num_segments)

        def tekst(text, x, y, *args, **kwargs):
            nx, ny = rp(x, y)
            kwargs["rotation"] = kwargs.get("rotation", 0) + hoek
            echt["draw_text"](text, nx, ny, *args, **kwargs)

        arcade.draw_circle_filled = cirkel_f
        arcade.draw_circle_outline = cirkel_o
        arcade.draw_lrbt_rectangle_filled = rect_f
        arcade.draw_lrbt_rectangle_outline = rect_o
        arcade.draw_line = lijn
        arcade.draw_triangle_filled = drie_f
        arcade.draw_triangle_outline = drie_o
        arcade.draw_polygon_filled = poly_f
        arcade.draw_polygon_outline = poly_o
        arcade.draw_ellipse_filled = ellips_f
        arcade.draw_ellipse_outline = ellips_o
        arcade.draw_arc_outline = boog_o
        arcade.draw_text = tekst
        try:
            obj.teken()
        finally:
            # Altijd terugzetten, ook als er iets misgaat tijdens het tekenen
            for n, f in echt.items():
                setattr(arcade, n, f)

    def _element_schokgolf(self, sp):
        """Is er net een aarde-schokgolf? Dan gaan monsters in de buurt weg (geen spikes)."""
        sg = getattr(sp, "_schokgolf", None)
        if sg is None or sg["klaar"]:
            return
        sg["klaar"] = True                         # elke schokgolf werkt maar één keer
        from speler import ELEM_SCHOK_BEREIK
        weg = []
        for v in self.vijanden:
            if getattr(v, "is_spike", False):
                continue                           # spikes, draaimotoren en bosses blijven
            vx = v.x + getattr(v, "breedte", 32) / 2
            vy = v.y + getattr(v, "hoogte", 32) / 2
            if abs(vx - sg["x"]) < ELEM_SCHOK_BEREIK and abs(vy - sg["y"]) < 90:
                weg.append(v)
        for v in weg:
            self.vijanden.remove(v)
            self._voeg_punt_toe()                  # een punt voor elk weggeblazen monster
            if sp.modus == "evolutie":
                evo.dna_erbij(sp, evo.DNA_PER_MONSTER)
        if weg:
            geluid_manager.speel_vijand_dood()

    def _mier_sync(self, sp):
        """Zorg dat alleen de toren/brug van nu in het level staat."""
        werk = getattr(sp, "_mk_werk", None) if sp.modus == "mierenkolonie" else None
        self.platforms = [p for p in self.platforms
                          if not getattr(p, "is_mierwerk", False) or p is werk]
        if werk is not None and werk not in self.platforms:
            self.platforms.append(werk)

    def _mieren_geraakt(self, sp):
        """Raakt een volg-mier een spike of monster? Dan ben je die mier kwijt.
        (Net na een opoffering ben jij even onkwetsbaar, en je mieren dan ook: anders
        lopen ze allemaal achter elkaar dezelfde spike in.)"""
        if sp.onkwetsbaar_timer > 0:
            return
        for i, pos in enumerate(mk.mier_posities(sp)):
            mx, my, mb, mh = mk.mier_rechthoek(pos)
            for vijand in self.vijanden:
                if vijand.raakt_speler(mx, my, mb, mh):
                    mk.mier_kwijt(sp, i)
                    geluid_manager.speel_geraakt()
                    return                       # maar één mier per stapje

    def _draak_vuur(self, sp):
        """Vuurballen raken monsters; de vuurstorm verslaat alles in de buurt."""
        from vijand import Spikes
        weg = []
        storm = False
        for v in sp._dt_vuurballen:
            for vijand in self.vijanden:
                if (vijand not in weg and not getattr(vijand, "is_spike", False)
                        and dt.vuurbal_raakt(v, vijand)):
                    weg.append(vijand)
                    v[3] = 0                     # de vuurbal is op
                    break
        if sp._dt_storm_nieuw:
            sp._dt_storm_nieuw = False
            storm = True
            cx, cy = sp.x + sp.breedte / 2, sp.y + sp.hoogte / 2
            for vijand in self.vijanden:
                vx = vijand.x + getattr(vijand, "breedte", 32) / 2
                vy = vijand.y + getattr(vijand, "hoogte", 32) / 2
                if math.hypot(vx - cx, vy - cy) > dt.STORM_BEREIK or vijand in weg:
                    continue
                if isinstance(vijand, Spikes) or not getattr(vijand, "is_spike", False):
                    weg.append(vijand)           # spikes smelten, monsters gaan weg
        for vijand in weg:
            self.vijanden.remove(vijand)
            if not isinstance(vijand, Spikes):
                self._voeg_punt_toe()
                dt.monster_opgegeten(sp, super_vullen=not storm)   # je draak eet het monster op en groeit
        if weg:
            geluid_manager.speel_vijand_dood()

    def _bouw_blokje(self, sp):
        """Bouwmeester: zet een blokje neer (als je er nog hebt en als er plek is)."""
        if self.dood or self.gewonnen or self.game_over:
            return
        from platforms import BouwBlok
        from speler import BOUW_CEL
        plek = sp.bouw_plek(self.platforms)
        if plek is None:
            return
        self.platforms.append(BouwBlok(plek[0], plek[1], BOUW_CEL, BOUW_CEL))
        sp._bouw_over -= 1
        geluid_manager.speel_sprong()      # tok!

    def _elementkoning_raakt(self, vijand):
        """Elementenkoning: lava smelt spikes, gif verslaat monsters, kristal stuitert
        op spikes. Geeft "weg" (vijand weg), "veilig" (niks aan de hand) of None."""
        sp = self.speler
        if sp.modus == "evolutie":
            # Evolutie met stekels: monsters die je raken gaan dood (spikes niet)
            if evo.heeft(sp, "stekels") and not getattr(vijand, "is_spike", False):
                self._voeg_punt_toe()
                evo.dna_erbij(sp, evo.DNA_PER_MONSTER)
                geluid_manager.speel_vijand_dood()
                return "weg"
            return None
        if sp.modus != "elementkoning":
            return None
        from vijand import Spikes
        e = ek.element(sp)
        if e["smelt"] and isinstance(vijand, Spikes):
            return "weg"
        if isinstance(vijand, Spikes) and ek.spike_stuiter(sp):
            geluid_manager.speel_sprong()
            return "veilig"
        if e["gif"] and not getattr(vijand, "is_spike", False):
            self._voeg_punt_toe()
            geluid_manager.speel_vijand_dood()
            return "weg"
        return None

    def _spike_magneet(self, sp):
        """Trek de speler een stukje naar de dichtstbijzijnde spike (als die vlakbij is)."""
        from vijand import Spikes
        from speler import KAMP_SPIKE_MAGNEET, KAMP_SPIKE_BEREIK
        mid = sp.x + sp.breedte / 2
        beste = None
        for v in self.vijanden:
            if not isinstance(v, Spikes) or getattr(v, "doorheen", False):
                continue
            afstand = (v.x + v.breedte / 2) - mid
            if abs(afstand) < KAMP_SPIKE_BEREIK and (beste is None or abs(afstand) < abs(beste)):
                beste = afstand
        if beste is not None and beste != 0:
            sp.x += KAMP_SPIKE_MAGNEET if beste > 0 else -KAMP_SPIKE_MAGNEET

    def _teken_element_hud(self, sp):
        """Een balkje bovenin: je vorm nu (groot) -> de volgende vorm (klein)."""
        from speler import ELEMENT_NAAM, ELEMENT_KLEUR
        nu, straks = sp.element(), sp.volgend_element()
        x = SCHERM_BREEDTE // 2
        y = SCHERM_HOOGTE - 86           # onder de klok en de sleutel-teller
        arcade.draw_lrbt_rectangle_filled(x - 130, x + 130, y - 8, y + 20, (0, 0, 0, 140))
        arcade.draw_circle_filled(x - 110, y + 6, 8, ELEMENT_KLEUR[nu])
        arcade.draw_text("Nu: " + ELEMENT_NAAM[nu], x - 96, y, ELEMENT_KLEUR[nu], 13, bold=True)
        arcade.draw_text("-> daarna: " + ELEMENT_NAAM[straks], x + 5, y, (200, 200, 200), 11)

    def _teken_bouw_hud(self, sp):
        """Balkje bovenin: hoeveel blokjes je nog hebt en welke toets je gebruikt."""
        from speler import BOUW_MAX
        x = SCHERM_BREEDTE // 2
        y = SCHERM_HOOGTE - 86
        arcade.draw_lrbt_rectangle_filled(x - 170, x + 170, y - 10, y + 22, (0, 0, 0, 150))
        arcade.draw_text("Blokjes:", x - 160, y, (255, 220, 120), 13, bold=True)
        for i in range(BOUW_MAX):
            bx = x - 85 + i * 22
            if i < sp._bouw_over:
                arcade.draw_lrbt_rectangle_filled(bx, bx + 16, y - 2, y + 14, (235, 170, 60))
            arcade.draw_lrbt_rectangle_outline(bx, bx + 16, y - 2, y + 14, (200, 140, 50), 2)
        arcade.draw_text("pijltje omlaag = bouwen", x - 10, y, (220, 220, 220), 11)

    def _teken_nacht(self, sp):
        """Maak alles donker behalve een rond lichtje om de speler heen."""
        from speler import TIEN_LICHT, KAMP_DONKER_LICHT
        cx = sp.x + sp.breedte / 2
        cy = sp.y + sp.hoogte / 2

        def ring(r_binnen, r_buiten, kleur):
            # Een ring van 48 stukjes (vierhoekjes) tussen twee cirkels
            punten = []
            for i in range(49):
                h = 2 * math.pi * i / 48
                punten.append((math.cos(h), math.sin(h)))
            for i in range(48):
                (c1, s1), (c2, s2) = punten[i], punten[i + 1]
                arcade.draw_polygon_filled([(cx + c1 * r_binnen, cy + s1 * r_binnen),
                                            (cx + c2 * r_binnen, cy + s2 * r_binnen),
                                            (cx + c2 * r_buiten, cy + s2 * r_buiten),
                                            (cx + c1 * r_buiten, cy + s1 * r_buiten)], kleur)

        # Buiten het lichtje is alles pikdonker (tot ver buiten het scherm)
        licht = KAMP_DONKER_LICHT if sp._kamp("donker") else TIEN_LICHT
        ring(licht, 3000, (0, 0, 10, 250))

    def _update_volgers(self):
        """Laat de 'volg'-voorwerpen de speler volgen: hun x schuift naar de speler toe,
        maar ze blijven op de hoogte (y) waar je ze hebt neergezet."""
        if self.twee or not getattr(self, "volgers", None):
            return
        doel_x = self.speler.x + self.speler.breedte / 2
        for o in self.volgers:
            if hasattr(o, "mx"):
                # Een draai-motor (draad): schuif het HELE midden mee, dan draait
                # het draaiende paar keurig achter de speler aan.
                o.mx += (doel_x - o.mx) * 0.06
                o.x = o.mx - o.breedte / 2
            else:
                mid = o.x + o.breedte / 2
                o.x += (doel_x - mid) * 0.06    # rustig naar de speler toe (met vertraging)

    def _teken_acht(self, px, w, h):
        """Teken de achtergrond: een eigen gekozen kleur, of anders het gewone thema."""
        if getattr(self, "acht_kleur", None):
            arcade.draw_lrbt_rectangle_filled(0, w, 0, h, self.acht_kleur)
        else:
            achtergrond_module.teken_achtergrond(self._achtergrond_nummer(px), w, h)

    def _achtergrond_nummer(self, px):
        """Welke achtergrond hoort bij de plek px? (verandert per zone in eigen levels)."""
        n = self.huidig_level
        for zx, zn in self.acht_zones:      # gesorteerd op x
            if px >= zx:
                n = zn
            else:
                break
        return n

    def _camera_y(self, sp):
        """Hoogte van de camera: normaal onderin (grond in beeld), maar gaat mee
        omhoog zodra je hoog komt — zo kun je oneindig omhoog en zie je jezelf nog."""
        top_grens = SCHERM_HOOGTE * 0.70          # pas boven deze lijn beweegt de camera mee
        speler_midden = sp.y + sp.hoogte / 2
        return SCHERM_HOOGTE / 2 + max(0, speler_midden - top_grens)

    def _check_teleport(self, sp):
        """Raakt de speler een teleporter? Dan spring je naar de dichtstbijzijnde
        teleporter van DEZELFDE kleur. Is er geen andere van die kleur, dan naar de
        dichtstbijzijnde van een andere kleur (zo blijven oude blauw/oranje-levels werken)."""
        raakt_nu = None
        for t in self.teleporters:
            if t.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                raakt_nu = t
                break
        if raakt_nu is None:
            sp._teleport_klaar = True     # niet meer op een teleporter -> weer klaar
            return
        # Net geteleporteerd? Eerst even weglopen voordat het weer mag (geen heen-en-weer)
        if not getattr(sp, "_teleport_klaar", True):
            return
        # Zoek de dichtstbijzijnde teleporter van DEZELFDE kleur (anders van een andere)
        doel_zelfde, best_z = None, None
        doel_ander, best_a = None, None
        for t in self.teleporters:
            if t is raakt_nu:
                continue
            afstand = abs(t.x - raakt_nu.x)
            if t.kleur == raakt_nu.kleur:
                if best_z is None or afstand < best_z:
                    best_z, doel_zelfde = afstand, t
            else:
                if best_a is None or afstand < best_a:
                    best_a, doel_ander = afstand, t
        doel = doel_zelfde if doel_zelfde is not None else doel_ander
        if doel is None:
            return                        # geen andere teleporter om heen te gaan
        # Spring naar het midden van de doel-teleporter
        sp.x = doel.x + (doel.breedte - sp.breedte) / 2
        sp.y = doel.y + (doel.hoogte - sp.hoogte) / 2
        sp._teleport_klaar = False
        geluid_manager.speel_powerup()

    def _check_deuren(self, sp):
        """Heb je een sleutel en raak je een dichte deur aan? Dan gaat hij open
        (en kost het één sleutel)."""
        if sp.sleutels <= 0:
            return
        marge = 5   # een beetje speling: zo open je de deur ook van boven of onder
        for d in self._deuren:
            if d.open:
                continue
            if (sp.x < d.x + d.breedte + marge and sp.x + sp.breedte > d.x - marge and
                    sp.y < d.y + d.hoogte + marge and sp.y + sp.hoogte > d.y - marge):
                d.open = True
                sp.sleutels -= 1
                geluid_manager.speel_powerup()
                break                      # één sleutel opent één deur

    def _check_checkpoints(self, sp):
        """Raakt de speler een checkpoint? Dan wordt dat zijn nieuwe startplek."""
        if self.twee:
            return                        # checkpoints alleen in 1-speler-modus
        for cp in self.checkpoints:
            if not cp.actief and cp.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                cp.actief = True
                self._respawn = (cp.x, cp.y)   # hier kom je terug na doodgaan
                self._respawn_nummer = self.huidig_level
                geluid_manager.speel_powerup()  # 🎵 fijn geluidje

    def _check_springers(self, sp):
        """Spring-matten (vanzelf springen) en spring-bollen (onthoud dat je erop staat)."""
        sp._bol_kracht = None
        sp._draai_bol = False
        for s in self.springers:
            if not s.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                continue
            if isinstance(s, SpringMat):
                # Mat: spring VANZELF omhoog (alleen als je niet al omhoog schiet)
                if sp.snelheid_y <= 0.5:
                    sp.snelheid_y = s.kracht
                    geluid_manager.speel_sprong()
            elif getattr(s, "draai", False):
                sp._draai_bol = True        # draai-bol: druk om de zwaartekracht om te draaien
            else:
                sp._bol_kracht = s.kracht   # gewone bol: druk om te springen

    def _springboost(self, sp):
        """Sta je op een spring-bol en druk je op springen? Dan gebeurt er iets:
        gewone bol = springen, draai-bol = zwaartekracht omdraaien (je valt de andere kant op)."""
        if getattr(sp, "_draai_bol", False):
            sp.zwaartekracht_richting *= -1
            sp.snelheid_y = -6 * sp.zwaartekracht_richting   # duwtje de nieuwe kant op
            sp.rotatie = 180 if sp.zwaartekracht_richting == -1 else 0  # op z'n kop
            geluid_manager.speel_sprong()
            return True
        if getattr(sp, "_bol_kracht", None) is not None:
            sp.snelheid_y = sp._bol_kracht
            geluid_manager.speel_sprong()
            return True
        return False

    def _maak_kloon(self, sp):
        """Maak een tweede kopie die UIT het portaal komt en de andere kant op valt.

        De kloon start op dezelfde plek als de speler (dus niet in een blok) en
        heeft omgekeerde zwaartekracht: hij valt omhoog terwijl de speler omlaag valt.
        """
        k = Speler()
        k.x = sp.x
        k.y = sp.y
        k.modus = sp.modus
        k.snelheid_bonus = sp.snelheid_bonus
        k.sprong_bonus = sp.sprong_bonus
        k.snelheid_factor = sp.snelheid_factor
        k.kleur = sp.kleur
        k.zwaartekracht_richting = -1     # de kloon valt naar BOVEN
        k.plafond = VLIEG_PLAFOND         # de kloon houdt WEL een plafond (rolt langs het dak)
        sp.kloon = k

    def _kloon_actie(self, sp):
        """Laat de kloon dezelfde actie doen als de speler (springen enz.)."""
        k = sp.kloon
        if k is None:
            return
        m = k.modus
        if m == "robot":
            k.robot_sprong()
        elif m == "ufo":
            k.flap()
        elif m == "bal":
            k.flip_zwaartekracht()
        elif m == "spin":
            self._spin_teleport(k)
        elif m == "heli":
            k.heli_wissel()
        elif m == "draaibol":
            k.draaibol_draai()
        elif m == "kolibrie":
            k.kolibrie_flap()
        elif m == "vleermuis":
            k.vleermuis_flap()
        elif m not in ("vliegtuig", "golf", "ballon", "raket", "draak", "dronken", "spook"):   # gewoon blok: springen
            k.spring()

    def _update_kloon(self, sp, knop_vast=False):
        """Beweeg de kloon met de speler mee. Geeft True als hij ergens tegenaan gaat.

        `knop_vast` is of de knop nu ingedrukt wordt (voor de vasthoud-vormen van de kloon)."""
        k = sp.kloon
        if k is None:
            return False
        vorige_x = getattr(k, "_vorige_x", k.x)
        k.rechts_ingedrukt = sp.rechts_ingedrukt
        k.links_ingedrukt = sp.links_ingedrukt
        # De kloon heeft misschien een ándere vorm dan de speler, dus we gebruiken
        # de 'rauwe' knop-vasthouden (niet die van de speler).
        if k.modus in ("vliegtuig", "golf", "robot", "ballon", "raket", "draak", "dronken", "spook"):
            k.vlieg_omhoog = knop_vast
        k.bijwerken(self.level_breedte, self.platforms)
        k.x = sp.x                       # blijf horizontaal gelijk met de speler
        self._kloon_portalen(k, vorige_x)   # de kloon kan zelf door portalen
        k._vorige_x = k.x
        self._pas_rotatie_toe(k)
        # De kloon gaat af als hij een blok-zijkant of een spike raakt, of eraf valt
        if self._raakt_blok_zijkant(k):
            return True
        for v in self.vijanden:
            if getattr(v, "is_spike", False) and v.raakt_speler(k.x, k.y, k.breedte, k.hoogte):
                return True
        if k.y < -50 or k.y > SCHERM_HOOGTE + 50:
            return True
        return False

    def _kloon_portalen(self, k, vorige_x):
        """Raakt de KLOON zelf een portaal? Dan verandert alleen de kloon (niet de speler).

        Dubbel/enkel-portalen slaan we over — die horen bij de gewone speler."""
        for portaal in self.portalen:
            if not self._raakt_portaal(k, vorige_x, portaal):
                continue
            if portaal.soort in SNELHEID_FACTOR:
                factor = SNELHEID_FACTOR[portaal.soort]
                if k.snelheid_factor != factor:
                    k.snelheid_factor = factor
                    geluid_manager.speel_powerup()
            elif portaal.soort in self.PORTAAL_MODUS:
                nieuwe_modus = self.PORTAAL_MODUS[portaal.soort]
                if k.modus != nieuwe_modus:
                    self._zet_vorm(k, nieuwe_modus, -1)   # kloon blijft ondersteboven
                    geluid_manager.speel_powerup()

    def _teken_kloon(self, sp):
        """Teken de kloon (als die er is)."""
        if sp.kloon is not None:
            sp.kloon.teken()

    def _update_platforms(self):
        """Werk bijzondere blokken bij (zoals het verdwijnblok dat aftelt)."""
        for p in self.platforms:
            if hasattr(p, "bijwerken"):
                p.bijwerken()

    def _raakt_blok_zijkant(self, sp):
        """Botst deze speler tegen de ZIJKANT van een blok? (Geometry Dash-dood.)
        Staat muur-dood uit (bouwmodus-knop), dan stop je tegen de muur en ga je niet af."""
        p, van_links = self._muur_botsing(sp)
        if p is None:
            return False
        if getattr(self, "muurdood", True):
            return True
        # Muur-dood staat uit: zet de speler netjes tegen de muur aan
        sp.x = p.x - sp.breedte if van_links else p.x + p.breedte
        sp.snelheid_x = 0
        return False

    def _muur_botsing(self, sp):
        """Tegen welk blok botst deze speler van opzij? Geeft (blok, van_links) of (None, False)."""
        if (sp.modus in ("draaibol", "ninja", "magneet", "klimmer", "draaisturing", "plakker")
                or sp._kamp("magneet")):
            return None, False  # deze modi botsen juist tegen muren (rollen/afzetten/aangetrokken) -> niet dood
        if (sp.modus == "eigen" and getattr(sp, "eigen_instel", None)
                and (sp.eigen_instel.get("muur") or sp.eigen_instel.get("magneet")
                     or sp.eigen_instel.get("plakken"))):
            return None, False  # eigen poppetje met muur/magneet/plakken botst tegen muren -> niet dood
        for p in self._blokken:
            if not getattr(p, "vast", True):
                continue                       # verdwenen blok: geen botsing
            top = p.y + p.hoogte
            # Overlapt de speler verticaal met het blok, maar staat hij er niet bovenop?
            if not (sp.y + sp.hoogte > p.y + 4 and sp.y < top - 6):
                continue
            raakt_links = (sp.snelheid_x > 0 and sp.x < p.x and sp.x + sp.breedte > p.x)
            raakt_rechts = (sp.snelheid_x < 0 and sp.x + sp.breedte > p.x + p.breedte and sp.x < p.x + p.breedte)
            if raakt_links or raakt_rechts:
                return p, raakt_links
        return None, False

    def _check_blok_zijkant(self):
        """Eén-speler: ga dood als je tegen de zijkant van een blok botst."""
        if self._raakt_blok_zijkant(self.speler):
            self._speler_geraakt()
            return True
        return False

    # ============== MEERDERE SPELERS (split-screen, 1 t/m 4) ==============

    SPELER_KLEUREN = [(60, 140, 255), (255, 80, 80), (80, 200, 90), (255, 170, 40)]

    # Spring-knop per speler (0..3)
    SPRING_TOETS = {arcade.key.W: 0, arcade.key.SPACE: 0, arcade.key.UP: 1,
                    arcade.key.T: 2, arcade.key.I: 3}
    # Links/rechts-knoppen per speler: toets -> (speler, "links"/"rechts")
    BEWEEG_TOETS = {
        arcade.key.A: (0, "links"), arcade.key.D: (0, "rechts"),
        arcade.key.LEFT: (1, "links"), arcade.key.RIGHT: (1, "rechts"),
        arcade.key.F: (2, "links"), arcade.key.H: (2, "rechts"),
        arcade.key.J: (3, "links"), arcade.key.L: (3, "rechts"),
    }

    def _raster(self):
        """Hoeveel kolommen en rijen het scherm heeft (op basis van het aantal spelers)."""
        kol = 2 if self.aantal >= 2 else 1
        rij = 2 if self.aantal >= 3 else 1
        return kol, rij

    def _vak(self, i):
        """Het scherm-vak (viewport) van speler i: (x, y, breedte, hoogte)."""
        kol, rij = self._raster()
        c = i % kol
        r = i // kol                       # 0 = bovenste rij
        return (c * SCHERM_BREEDTE, (rij - 1 - r) * SCHERM_HOOGTE,
                SCHERM_BREEDTE, SCHERM_HOOGTE)

    def _zet_multi_klaar(self):
        """Zet alle spelers op de start en verdeel het scherm in vakken."""
        for i, sp in enumerate(self.spelers):
            if i > 0:
                sp.reset()
                sp.modus = self.speler.modus
                sp.snelheid_bonus = self.speler.snelheid_bonus
                sp.sprong_bonus = self.speler.sprong_bonus
            sp.kleur = self.SPELER_KLEUREN[i]
            self._vlieg[i] = False
            self._finish[i] = False
            self._vorige[i] = sp.x
        self.winnaar = None
        # Elke camera krijgt zijn eigen vak (niet uitgerekt)
        for i, cam in enumerate(self.cameras):
            vx, vy, vw, vh = self._vak(i)
            cam.viewport = arcade.LBWH(vx, vy, vw, vh)
            cam.projection = arcade.LRBT(-vw / 2, vw / 2, -vh / 2, vh / 2)

    def _is_klaar(self, i):
        """Is speler i klaar (gefinisht)? In de vechtmodus nooit (samen tot het eind)."""
        return self._finish[i]

    def _racer_dood(self, sp, i):
        """Een speler ging af: terug naar de start (geen leven kwijt)."""
        sp.reset()
        sp.modus = "vliegtuig" if self.vlucht else "blok"
        geluid_manager.speel_geraakt()
        self._vorige[i] = sp.x

    def _beweeg_speler_multi(self, sp, i):
        """Beweeg één speler (auto-run of handmatig), met portalen en botsingen."""
        if self.race or self.vlucht:
            sp.rechts_ingedrukt = True          # auto-run modi: vanzelf naar rechts
            sp.links_ingedrukt = False
        if (sp.modus in ("vliegtuig", "golf", "robot", "ballon", "raket", "draak", "dronken", "spook")
                or sp._kamp("vasthouden")
                or sp.modus in ("element", "elementkoning", "drakentemmer", "evolutie")):
            sp.vlieg_omhoog = self._vlieg[i]
        sp.bijwerken(self.level_breedte, self.platforms)
        self._pas_portalen_toe(sp, self._vorige[i])
        self._vorige[i] = sp.x
        self._check_springers(sp)
        self._check_teleport(sp)
        self._check_deuren(sp)
        self._pas_rotatie_toe(sp)
        kloon_raakt = self._update_kloon(sp, self._vlieg[i])
        if self._raakt_blok_zijkant(sp) or sp.is_gevallen() or kloon_raakt:
            self._racer_dood(sp, i)

    def _update_monsters_multi(self):
        """Werk de monsters bij; elke speler kan stompen of geraakt worden."""
        weg = []
        nieuw = []
        centers = [s.x + s.breedte / 2 for s in self.spelers]
        for vijand in self.vijanden:
            vc = vijand.x + vijand.breedte / 2
            doel = min(centers, key=lambda c: abs(c - vc))   # dichtstbijzijnde speler
            vijand.bijwerken(doel)
            if getattr(vijand, 'nieuwe_monsters', None):
                nieuw.extend(vijand.nieuwe_monsters)
                vijand.nieuwe_monsters = []
            for i, sp in enumerate(self.spelers):
                if self._is_klaar(i):
                    continue
                van_boven = (sp.snelheid_y < 0) or (sp.y >= vijand.y + vijand.hoogte / 2)
                if van_boven and vijand.speler_springt_erop(sp.x, sp.y, sp.breedte, sp.hoogte):
                    if hasattr(vijand, 'word_gestompt'):
                        vijand.word_gestompt()
                        if vijand.levens <= 0 and vijand not in weg:
                            weg.append(vijand)
                    elif vijand not in weg:
                        weg.append(vijand)
                    sp.snelheid_y = SPRING_KRACHT / 2
                    geluid_manager.speel_vijand_dood()
                elif not sp.is_onkwetsbaar() and vijand.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                    self._racer_dood(sp, i)
        for v in weg:
            if v in self.vijanden:
                self.vijanden.remove(v)
        self.vijanden.extend(nieuw)

    def _check_win_multi(self):
        """Bepaal per modus of er gewonnen is."""
        if self.arena:
            levende = [v for v in self.vijanden if not getattr(v, 'is_spike', False)]
            if not levende and not self.level_gehaald:
                self.level_gehaald = True    # iedereen gewonnen!
                geluid_manager.speel_level_gehaald()
            return
        for i, sp in enumerate(self.spelers):
            if self._is_klaar(i):
                continue
            y_ok = True if self.vlucht else sp.y < self.vlag_y + 60
            if sp.x + sp.breedte > self.vlag_x and y_ok:
                self._finish[i] = True
                if not self.winnaar:
                    self.winnaar = i + 1
                    geluid_manager.speel_level_gehaald()

    def _update_twee(self):
        """Werk alle spelers + de monsters bij en laat de camera's meebewegen."""
        if self.winnaar or self.level_gehaald:
            return
        self._update_platforms()      # verdwijnblokken aftellen
        for i, sp in enumerate(self.spelers):
            if not self._is_klaar(i):
                self._beweeg_speler_multi(sp, i)
        self._update_monsters_multi()
        # Power-ups: elke speler kan ze oppakken
        for pu in self.powerups:
            if not pu.opgepakt:
                pu.bijwerken()
                for i, sp in enumerate(self.spelers):
                    if not self._is_klaar(i) and pu.raakt_speler(sp.x, sp.y, sp.breedte, sp.hoogte):
                        pu.toepassen(sp)
                        pu.opgepakt = True
                        geluid_manager.speel_powerup()
                        break
        self._check_win_multi()
        # Camera's laten meebewegen (elke volgt zijn eigen speler)
        for sp, cam in zip(self.spelers, self.cameras):
            cx = sp.x + sp.breedte / 2
            cx = max(SCHERM_BREEDTE / 2, min(cx, self.level_breedte - SCHERM_BREEDTE / 2))
            cam.position = cx, self._camera_y(sp)

    def _actie_druk(self, sp, i):
        """Speler i drukt op zijn knop: doe de actie die bij zijn modus hoort."""
        self._vlieg[i] = True   # knop vastgehouden (ook voor de kloon zijn eigen vorm)
        self._kloon_actie(sp)   # de kloon (dubbel-portaal) doet zijn eigen actie mee
        # Sta je op een spring-bol? Dan spring je (ook in de lucht), wat je modus ook is.
        if self._springboost(sp):
            return
        m = sp.modus
        if m in ("vliegtuig", "golf", "ballon", "raket", "draak", "dronken", "spook"):
            self._vlieg[i] = True
        elif m == "robot":
            self._vlieg[i] = True
            sp.robot_sprong()
            geluid_manager.speel_sprong()
        elif m == "ufo":
            sp.flap()
            geluid_manager.speel_sprong()
        elif m == "kolibrie":
            sp.kolibrie_flap()
            geluid_manager.speel_sprong()
        elif m == "vleermuis":
            sp.vleermuis_flap()
            geluid_manager.speel_sprong()
        elif m == "bal":
            sp.flip_zwaartekracht()
            geluid_manager.speel_sprong()
        elif m == "spin":
            self._spin_teleport(sp)
            geluid_manager.speel_sprong()
        elif m == "heli":
            sp.heli_wissel()
            geluid_manager.speel_sprong()
        elif m == "draaibol":
            sp.draaibol_draai()
            geluid_manager.speel_sprong()
        else:
            op_grond = sp.staat_op_grond
            sp.spring()
            if op_grond:
                geluid_manager.speel_sprong()

    def _volgende_twee_baan(self):
        """Ga met alle spelers naar de volgende baan/level."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _teken_twee(self):
        """Teken het scherm in vakken: elke speler zijn eigen vak."""
        for sp, cam in zip(self.spelers, self.cameras):
            with cam.activate():
                cx = cam.position[0]
                links = cx - SCHERM_BREEDTE / 2 - 60
                rechts = cx + SCHERM_BREEDTE / 2 + 60

                def zicht(o, b=0):
                    return o.x + b >= links and o.x <= rechts

                for p in self.platforms:
                    if zicht(p, p.breedte) and not getattr(p, "onzichtbaar", False):
                        p.teken()
                for v in self.vijanden:
                    if zicht(v, v.breedte) and not getattr(v, "onzichtbaar", False):
                        v.teken()
                for springer in self.springers:
                    if zicht(springer, springer.breedte) and not getattr(springer, "onzichtbaar", False):
                        springer.teken()
                for portaal in self.portalen:
                    if zicht(portaal, portaal.breedte) and not getattr(portaal, "onzichtbaar", False):
                        portaal.teken()
                for tele in self.teleporters:
                    if zicht(tele, tele.breedte) and not getattr(tele, "onzichtbaar", False):
                        tele.teken()
                # Decoratie helemaal vooraan (vóór blokken, spikes, alles)
                for deco in self.decoraties:
                    if zicht(deco, deco.breedte) and not getattr(deco, "onzichtbaar", False):
                        deco.teken()
                for bord in self.borden:
                    if zicht(bord, bord.breedte):
                        bord.teken()
                if not self.arena:                 # in de vechtmodus is er geen vlag
                    self._teken_vlag(self.vlag_x, self.vlag_y)
                # Teken ALLE spelers (en hun spiegel-klonen), zodat je elkaar ziet
                for speler in self.spelers:
                    if zicht(speler, speler.breedte):
                        speler.teken()
                        self._teken_kloon(speler)
        # Scheidingslijnen tussen de vakken
        W, H = self.window.width, self.window.height
        kol, rij = self._raster()
        if kol == 2:
            arcade.draw_lrbt_rectangle_filled(W // 2 - 3, W // 2 + 3, 0, H, (20, 20, 30))
        if rij == 2:
            arcade.draw_lrbt_rectangle_filled(0, W, H // 2 - 3, H // 2 + 3, (20, 20, 30))
        self._teken_twee_hud()
        # Banner: iemand wint (race/vlucht) of iedereen wint (vechtmodus)
        if self.winnaar or (self.arena and self.level_gehaald):
            mx, my = W // 2, H // 2
            arcade.draw_lrbt_rectangle_filled(mx - 340, mx + 340, my - 60, my + 60, (20, 70, 20))
            arcade.draw_lrbt_rectangle_outline(mx - 340, mx + 340, my - 60, my + 60,
                                               arcade.color.WHITE, 3)
            if self.winnaar:
                titel = f"🏆 Speler {self.winnaar} wint!"
                hint = "ENTER = nieuwe baan   •   K = kaart"
            else:
                titel = "🎉 Iedereen gewonnen! 🎉"
                hint = "ENTER = volgend monster-level   •   K = kaart"
            arcade.draw_text(titel, mx, my + 8, (255, 230, 80), 30, bold=True, anchor_x="center")
            arcade.draw_text(hint, mx, my - 34, arcade.color.WHITE, 16, anchor_x="center")

    def _teken_twee_hud(self):
        """Teken in elk vak een naam + (in race/vlucht) een voortgangsbalk."""
        doel = self.vlag_x if self.vlag_x > 0 else self.level_breedte
        for i, sp in enumerate(self.spelers):
            vx, vy, vw, vh = self._vak(i)
            midden = vx + vw // 2
            boven = vy + vh                    # bovenkant van dit vak
            kleur = self.SPELER_KLEUREN[i]
            if self.arena:
                arcade.draw_text(f"Speler {i + 1}  —  Vechten! ⚔️", midden, boven - 26,
                                 kleur, 15, bold=True, anchor_x="center")
                continue
            pct = max(0.0, min(sp.x / doel, 1.0))
            bl, br = midden - 130, midden + 130
            bb, bt = boven - 22, boven - 10
            arcade.draw_lrbt_rectangle_filled(bl, br, bb, bt, (40, 40, 55))
            if pct > 0:
                arcade.draw_lrbt_rectangle_filled(bl, bl + (br - bl) * pct, bb, bt, (80, 220, 90))
            arcade.draw_lrbt_rectangle_outline(bl, br, bb, bt, arcade.color.WHITE, 2)
            kop = (f"Speler {i + 1} — FINISH! 🏁" if self._finish[i]
                   else f"Speler {i + 1} — {int(pct * 100)}%")
            arcade.draw_text(kop, midden, boven - 44, kleur, 14, bold=True, anchor_x="center")

    def _speler_geraakt(self):
        """Verwerk dat de speler geraakt wordt: leven aftrekken of game over."""
        # Evolutie met pantser: het pantser houdt de klap tegen (niet in een kuil)
        if (self.speler.modus == "evolutie" and not self.speler.is_gevallen()
                and evo.bescherm(self.speler)):
            geluid_manager.speel_geraakt()
            return
        # Mierenkolonie: de achterste mier offert zich op (maar niet als je in een kuil valt)
        if (self.speler.modus == "mierenkolonie" and not self.speler.is_gevallen()
                and mk.bescherm(self.speler)):
            geluid_manager.speel_geraakt()
            return
        # Elementenkoning als metaal: het schild houdt één klap tegen
        if self.speler.modus == "elementkoning" and getattr(self.speler, "_ek_schild", False):
            self.speler._ek_schild = False
            self.speler.onkwetsbaar_timer = 45       # even knipperen, dan weer gewoon
            geluid_manager.speel_geraakt()
            return
        # Zelfgemaakt poppetje met het 'Schild'-kunstje kan niet geraakt worden
        if (self.speler.modus == "eigen" and getattr(self.speler, "eigen_instel", None)
                and self.speler.eigen_instel.get("schild")):
            return
        # In de vecht-, race-, vlucht- en bouwmodus ga je wel 'af' (opnieuw proberen),
        # maar je verliest GEEN leven en het is nooit game-over.
        if (self.arena or self.race or self.vlucht or self.eigen
                or self.testruimte or self.frameperfect):
            geluid_manager.speel_geraakt()  # 🎵 Bonk!
            self.dood = True
            return
        self.speler.levens -= 1
        geluid_manager.speel_geraakt()  # 🎵 Bonk!
        # Sla voortgang op (update levens) — in de arena NIET
        if not self.arena:
            try:
                voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
            except Exception:
                pass
        if self.speler.levens <= 0:
            self.game_over = True
            geluid_manager.stop_muziek()
            geluid_manager.speel_game_over()  # 🎵 Game over melodie
        else:
            self.dood = True

    def on_key_press(self, toets, modifiers):
        """Wordt aangeroepen als je een toets indrukt."""
        # Meerdere spelers: elke speler heeft eigen knoppen (springen + links/rechts).
        # Speler 1 = W + A/D, speler 2 = pijltjes, speler 3 = T + F/H, speler 4 = I + J/L
        if self.twee:
            if toets in self.SPRING_TOETS:
                i = self.SPRING_TOETS[toets]
                if i < self.aantal and not self.winnaar and not self.level_gehaald \
                        and not self._finish[i]:
                    self._actie_druk(self.spelers[i], i)
            elif toets in self.BEWEEG_TOETS:
                i, kant = self.BEWEEG_TOETS[toets]
                if i < self.aantal:
                    if kant == "links":
                        self.spelers[i].links_ingedrukt = True
                    else:
                        self.spelers[i].rechts_ingedrukt = True
            elif toets in (arcade.key.ENTER, arcade.key.NUM_ENTER):
                if self.winnaar or self.level_gehaald:
                    if self.eigen:
                        self._naar_bouwer()          # terug naar de bouwmodus
                    else:
                        self._volgende_twee_baan()
            elif toets == arcade.key.K:
                if self.eigen:
                    self._naar_bouwer()              # terug naar de bouwmodus
                else:
                    self._verlaat_arena()            # terug naar de kaart
            return
        # Schilder: kies een verfkleur met 1 t/m 8
        if self.speler.modus == "schilder":
            kleur = {arcade.key.KEY_1: 1, arcade.key.KEY_2: 2, arcade.key.KEY_3: 3, arcade.key.KEY_4: 4,
                     arcade.key.KEY_5: 5, arcade.key.KEY_6: 6, arcade.key.KEY_7: 7, arcade.key.KEY_8: 8,
                     arcade.key.NUM_1: 1, arcade.key.NUM_2: 2, arcade.key.NUM_3: 3, arcade.key.NUM_4: 4,
                     arcade.key.NUM_5: 5, arcade.key.NUM_6: 6, arcade.key.NUM_7: 7,
                     arcade.key.NUM_8: 8}.get(toets)
            if kleur:
                sv.kies_kleur(self.speler, kleur)
                return
        # Evolutie: kies een mutatie met 1, 2 of 3 (het spel staat dan even stil)
        if self.speler.modus == "evolutie" and self.speler._evo_kiezen:
            keuze = {arcade.key.KEY_1: 1, arcade.key.KEY_2: 2, arcade.key.KEY_3: 3,
                     arcade.key.NUM_1: 1, arcade.key.NUM_2: 2, arcade.key.NUM_3: 3}.get(toets)
            if keuze and evo.kies(self.speler, keuze):
                geluid_manager.speel_powerup()
            if toets == arcade.key.LEFT:
                self.speler.links_ingedrukt = True     # (loslaten/indrukken blijft kloppen)
            elif toets == arcade.key.RIGHT:
                self.speler.rechts_ingedrukt = True
            return
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = True
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = True
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            self._vlieg_omhoog = True         # knop vastgehouden (ook voor de kloon zijn eigen vorm)
            self._kloon_actie(self.speler)    # de kloon (dubbel-portaal) doet zijn eigen actie mee
            # Sta je op een spring-bol? Dan spring je meteen (ook in de lucht)
            if self._springboost(self.speler):
                return
            modus = self.speler.modus
            if modus in ("vliegtuig", "golf", "ballon", "raket", "draak", "dronken", "spook"):
                # Vasthoud-modi: knop ingedrukt = omhoog (stuwen of schuin omhoog)
                self._vlieg_omhoog = True
            elif modus == "robot":
                # Robot: vasthouden = hoger springen; de sprong begint hier
                self._vlieg_omhoog = True
                self.speler.robot_sprong()
                geluid_manager.speel_sprong()
            elif modus == "ufo":
                # UFO: elke tik een sprongetje omhoog
                self.speler.flap()
                geluid_manager.speel_sprong()
            elif modus == "kolibrie":
                # Kolibrie: klein wiekje per tik -> blijf snel tikken om te zweven
                self.speler.kolibrie_flap()
                geluid_manager.speel_sprong()
            elif modus == "vleermuis":
                # Vleermuis: een vleugelslag omhoog per tik (fladderen)
                self.speler.vleermuis_flap()
                geluid_manager.speel_sprong()
            elif modus == "bal":
                # Bal: elke tik draait de zwaartekracht om
                self.speler.flip_zwaartekracht()
                geluid_manager.speel_sprong()
            elif modus == "spin":
                # Spin: elke tik teleporteer je naar de vloer of het plafond
                self._spin_teleport(self.speler)
                geluid_manager.speel_sprong()
            elif modus == "heli":
                # Helikopter: elke tik wisselen tussen omhoog en omlaag
                self.speler.heli_wissel()
                geluid_manager.speel_sprong()
            elif modus == "draaibol":
                # Draaibol: elke tik draait de zwaartekracht een kwartslag
                self.speler.draaibol_draai()
                geluid_manager.speel_sprong()
            else:
                # Gewoon blokje: springen
                voor_sprong = self.speler.staat_op_grond or (
                    self.speler.dubbel_sprong_timer > 0 and not self.speler.heeft_dubbel_gesprongen)
                self.speler.spring()
                if voor_sprong:
                    geluid_manager.speel_sprong()  # 🎵 Sprong-piepje!
        elif toets == arcade.key.Z:
            # Z = schieten (alleen als schiet power-up actief is)
            if self.speler.schiet_timer > 0 and not self.gewonnen and not self.game_over and not self.dood:
                richting = 1 if self.speler.kijkt_rechts else -1
                kogel_x = (self.speler.x + self.speler.breedte + 4 if richting == 1
                           else self.speler.x - 4)
                kogel_y = self.speler.y + self.speler.hoogte // 2
                self.kogels.append(Kogel(kogel_x, kogel_y, richting))
        elif toets == arcade.key.N and self.testruimte:
            # In de testruimte: wissel naar het volgende poppetje
            self._test_volgende(1)
        elif toets == arcade.key.DOWN and self.speler.modus == "bouwmeester":
            # Bouwmeester: zet een blokje neer
            self._bouw_blokje(self.speler)
        elif toets == arcade.key.DOWN and self.speler.modus == "schilder":
            # Schilder: spuit een verfvlek op de grond onder je
            if (not (self.dood or self.gewonnen or self.game_over)
                    and sv.spuit(self.speler, self.platforms, self.vijanden)):
                geluid_manager.speel_sprong()
        elif toets == arcade.key.DOWN and self.speler.modus == "evolutie":
            # Evolutie met stamppoten: stampen in de lucht
            if not (self.dood or self.gewonnen or self.game_over) and evo.omlaag(self.speler):
                geluid_manager.speel_sprong()
        elif toets == arcade.key.DOWN and self.speler.modus == "mierenkolonie":
            # Mierenkolonie: toren (op de grond) of brug (in de lucht), of weer loslaten
            if not (self.dood or self.gewonnen or self.game_over):
                mk.bouw(self.speler)
                self._mier_sync(self.speler)
                geluid_manager.speel_sprong()
        elif toets == arcade.key.DOWN and self.speler.modus == "drakentemmer":
            # Drakentemmer: vuurbal spuwen (of vuurstorm als de superbalk vol is)
            if not (self.dood or self.gewonnen or self.game_over) and dt.vuur(self.speler):
                geluid_manager.speel_sprong()
        elif toets == arcade.key.DOWN and self.speler.modus == "portaalschieter":
            # Portaalschieter: blauw portaal neerzetten of oranje wegschieten
            if not (self.dood or self.gewonnen or self.game_over):
                ps.schiet(self.speler)
                geluid_manager.speel_sprong()
        elif toets == arcade.key.P and self.testruimte:
            # In de testruimte: open de poppetjes-zoeker en kies er zelf één
            from poppetjeszoeker import PoppetjeZoeker
            self.window.show_view(PoppetjeZoeker(self, kies_functie=self._test_kies))
        elif toets == arcade.key.KEY_2 and self.arena:
            # Geheime sprong-toets: spring meteen naar level 250 (om te proberen!)
            self.huidig_level = 250
            self._arena_top = max(self._arena_top, 250)
            self.maak_level(250)
        elif toets == arcade.key.K:
            # K = terug (naar de bouwmodus, of naar de kaart)
            if self.eigen:
                self._naar_bouwer()
            elif (self.arena or self.race or self.vlucht or self.testruimte
                  or self.frameperfect):
                self._verlaat_arena()   # zet de kaart-punten/levens terug
            else:
                self._naar_kaart()
        elif toets == arcade.key.ENTER or toets == arcade.key.NUM_ENTER:
            # ENTER = door na een gehaald level
            if self.level_gehaald:
                if self.eigen:
                    self._naar_bouwer()            # Terug naar de bouwmodus
                elif self.testruimte or self.frameperfect:
                    self._verlaat_arena()          # Testruimte/Frame Perfect: terug naar de kaart
                elif self.vlucht:
                    self._volgende_vlucht_baan()   # Door naar de volgende vliegbaan!
                elif self.race:
                    self._volgende_race_baan()     # Door naar de volgende racebaan!
                elif self.arena:
                    self._volgende_arena_level()   # Door naar het volgende monster-level!
                else:
                    self._naar_kaart()
        elif toets == arcade.key.R:
            if self.arena and self.game_over:
                self._verlaat_arena()              # Na game-over in de arena: terug naar de kaart
            elif self.gewonnen and (self.testruimte or self.frameperfect):
                self._verlaat_arena()              # Testruimte/Frame Perfect: kaart-punten terug
            elif self.gewonnen:
                self._naar_kaart()                 # Terug naar de kaart na winst
            elif self.game_over:
                # Opnieuw beginnen bij level 1! Alles wordt gereset
                self.punten = 0
                self.start_level = 1
                self.huidig_level = 1
                self.speler.volledig_reset()
                # Voortgang wissen — alle levels weer op slot
                self.voltooid.clear()
                # Sla op: geen voltooide levels meer, punten en levens terug naar 0/None
                voortgang_module.sla_voortgang_op(self.voltooid, 0, None)
                self.maak_level(1)
            elif self.dood:
                self.maak_level(self.huidig_level) # Zelfde level opnieuw (levens blijven!)
            elif self.testruimte:
                self.maak_level(self.huidig_level) # Testruimte opnieuw opzetten

    def on_mouse_press(self, x, y, knop, modifiers):
        """In de vechtmodus: klik op de pijltjes of de reset-knop bovenin."""
        if not self.arena:
            return
        ll, lr, lb, lt = self.ARENA_PIJL_LINKS
        rl, rr, rb, rt = self.ARENA_PIJL_RECHTS
        pl, pr, pb, pt = self.ARENA_RESET_KNOP
        if ll <= x <= lr and lb <= y <= lt:
            self._ga_naar_arena_level(self.huidig_level - 1)   # ◀ vorige level
        elif rl <= x <= rr and rb <= y <= rt:
            self._ga_naar_arena_level(self.huidig_level + 1)   # ▶ volgende level
        elif pl <= x <= pr and pb <= y <= pt:
            self._arena_reset()                                 # 🔄 helemaal opnieuw

    def _arena_reset(self):
        """Begin de vechtmodus helemaal opnieuw bij level 1.

        Ook je hoogste-bereikte level gaat terug naar 1, dus met ▶ kun je
        niet meer naar de hogere levels springen — die moet je opnieuw winnen.
        """
        self.huidig_level = 1
        self._arena_top = 1
        voortgang_module.reset_arena_record()   # record ook terug naar 0
        self.maak_level(1)

    def on_key_release(self, toets, modifiers):
        """Wordt aangeroepen als je een toets loslaat."""
        # Meerdere spelers: knoppen loslaten
        if self.twee:
            if toets in self.SPRING_TOETS:
                i = self.SPRING_TOETS[toets]
                if i < self.aantal:
                    self._vlieg[i] = False       # vasthoud-modi loslaten
            elif toets in self.BEWEEG_TOETS:
                i, kant = self.BEWEEG_TOETS[toets]
                if i < self.aantal:
                    if kant == "links":
                        self.spelers[i].links_ingedrukt = False
                    else:
                        self.spelers[i].rechts_ingedrukt = False
            return
        if toets == arcade.key.LEFT:
            self.speler.links_ingedrukt = False
        elif toets == arcade.key.RIGHT:
            self.speler.rechts_ingedrukt = False
        elif toets == arcade.key.UP or toets == arcade.key.SPACE:
            # Vliegtuig-modus: knop losgelaten = niet meer stuwen (je zakt)
            self._vlieg_omhoog = False

    def _naar_kaart(self):
        """Ga terug naar de levelkaart — punten en levens worden bewaard."""
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        # Sla voortgang op vóór je naar de kaart gaat
        try:
            voortgang_module.sla_voortgang_op(self.voltooid, self.punten, self.speler.levens)
        except Exception:
            pass
        data = voortgang_module.laad_voortgang()
        kaart = LevelKaartView(self.voltooid, self.punten, self.speler.levens,
                               data.get("arena_record", 0), data.get("race_record", 0),
                               data.get("vlucht_record", 0))
        self.window.show_view(kaart)

    def _naar_bouwer(self):
        """Ga terug naar de bouwmodus (met dezelfde kaart-gegevens)."""
        from bouwer import BouwerView
        geluid_manager.stop_muziek()
        data = voortgang_module.laad_voortgang()
        b = BouwerView(self.voltooid, self.kaart_punten, self.kaart_levens,
                       data.get("arena_record", 0), data.get("race_record", 0),
                       data.get("vlucht_record", 0), aantal_spelers=self.aantal,
                       start_slot=self.bouw_slot)   # terug naar dezelfde plek
        self.window.show_view(b)

    def _volgende_arena_level(self):
        """Ga naar het volgende monster-level (punten en levens blijven behouden)."""
        self.huidig_level += 1
        # Onthoud dat je nu zo hoog bent geweest (zodat je met ▶ hier terug kunt)
        self._arena_top = max(self._arena_top, self.huidig_level)
        self.maak_level(self.huidig_level)

    def _volgende_race_baan(self):
        """Ga naar de volgende (langere, snellere) racebaan."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _volgende_vlucht_baan(self):
        """Ga naar de volgende (langere) vliegtuig-baan."""
        self.huidig_level += 1
        self.maak_level(self.huidig_level)

    def _ga_naar_arena_level(self, nummer):
        """Spring naar een ander arena-level met de pijltjes (tussen 1 en je hoogste)."""
        nummer = max(1, min(nummer, self._arena_top))
        if nummer != self.huidig_level:
            self.huidig_level = nummer
            self.maak_level(nummer)

    def _verlaat_arena(self):
        """Verlaat de vechtmodus en ga terug naar de kaart.

        De gewone punten en levens van de kaart worden teruggezet
        (de arena telt helemaal apart).
        """
        from levelkaart import LevelKaartView
        geluid_manager.stop_muziek()
        data = voortgang_module.laad_voortgang()
        kaart = LevelKaartView(self.voltooid, self.kaart_punten, self.kaart_levens,
                               data.get("arena_record", 0), data.get("race_record", 0),
                               data.get("vlucht_record", 0))
        self.window.show_view(kaart)

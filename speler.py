# speler.py
# De Speler klasse — alles over het poppetje dat jij bestuurt.

import arcade
import math
import random
from instellingen import (SPELER_SNELHEID, SPRING_KRACHT, ZWAARTEKRACHT,
                           SPELER_KLEUR, OOG_KLEUR)

LEVENS_BEGIN = 3  # Hoeveel levens de speler krijgt bij het begin

# --- Vliegtuig-modus (Geometry Dash raket) ---
VLIEG_STUW = 0.9       # Hoeveel duw omhoog als je de knop vasthoudt
VLIEG_ZWAARTE = 0.45   # Hoe hard je zakt als je loslaat
VLIEG_MAX = 6          # Hoogste omhoog/omlaag snelheid (zo blijft het bestuurbaar)
VLIEG_PLAFOND = 460    # Zo hoog mag je maximaal vliegen (net onder de balk bovenin)

# --- UFO-modus: bij elke tik een sprongetje omhoog (zoals Flappy Bird) ---
FLAP_KRACHT = 7        # Hoe groot het sprongetje is bij een tik

# --- Robot-modus: hoe langer je vasthoudt, hoe hoger je springt ---
ROBOT_START = 7        # Beginkracht van de sprong
ROBOT_EXTRA = 0.7      # Extra duw omhoog per frame terwijl je vasthoudt
ROBOT_BOOST_FRAMES = 16  # Hoeveel frames je kunt blijven duwen (langer = hoger)

# --- Helikopter-modus: druk = omhoog, druk nog eens = omlaag ---
HELI_SNELHEID = 4      # Hoe snel de helikopter omhoog of omlaag gaat

# --- Ballon-modus: zweeft vanzelf omhoog, knop vasthouden = zakken ---
BALLON_ZWEEF = 0.35    # hoe hard je vanzelf omhoog drijft
BALLON_ZAK = 0.75      # hoe hard je zakt als je de knop vasthoudt

# --- Raket-modus: knop vasthouden = snel omhoog schieten, loslaten = snel vallen ---
RAKET_STUW = 1.3       # sterke duw omhoog (harder dan het vliegtuig)
RAKET_ZWAARTE = 0.7    # je valt snel als je loslaat
RAKET_MAX = 8          # topsnelheid omhoog/omlaag (pittig!)

# --- Kolibrie-modus: klein wiekje per tik; blijf snel tikken om te zweven ---
KOLIBRIE_FLAP = 4.2    # klein sprongetje per tik (kleiner dan de UFO, dus lastiger)

# --- Draak-modus: vrij vliegen, maar heel zweverig en wiebelig ---
DRAAK_STUW = 0.55      # zachte duw omhoog als je vasthoudt
DRAAK_ZWAARTE = 0.32   # zachte val als je loslaat -> hij blijft nazweven (wiebelig!)
DRAAK_MAX = 7          # topsnelheid omhoog/omlaag

# --- IJsblokje-modus: spiegelglad, je glijdt door en stopt bijna niet ---
IJS_GRIP = 0.06        # hoe snel je naar je doelsnelheid glijdt (klein = heel glad)

# --- Ninja-modus: snel, en kan zich tegen een muur afzetten (muursprong) ---
NINJA_SNELHEID = 1.4   # keer zo snel als een gewoon blokje
NINJA_MUURSPRONG = 6   # hoe hard je van de muur wegspringt

# --- Magneet-modus: je wordt naar de dichtstbijzijnde muur getrokken ---
MAGNEET_KRACHT = 1.6   # hoe hard de magneet je naar een muur trekt (per stapje)

# --- Flits-modus: loopt niet, maar teleporteert met sprongetjes vooruit ---
FLITS_INTERVAL = 9     # om de hoeveel stapjes je een flits maakt (kleiner = vaker)
FLITS_BLOK = 40        # grootte van één blok: elke flits verspringt precies één blok

# --- Dobbelsteen-modus: elke sprong is een willekeurige hoogte ---
DOBBEL_MIN = 6         # laagste sprong
DOBBEL_MAX = 18        # hoogste sprong (soms mega!)

# --- Vertraagd-modus: je toetsen werken pas een halve seconde later ---
VERT_DELAY = 30        # hoeveel stapjes je invoer vertraagd wordt (~halve seconde)

# --- Chaos-modus: de zwaartekracht draait op willekeurige momenten vanzelf om ---
CHAOS_KANS = 0.012     # kans per stapje dat de zwaartekracht omklapt

# --- Dronken-modus: zwabbert vanzelf op en neer, je stuurt ertegenin ---
DRONKEN_SNELHEID = 0.18   # hoe snel de wiebel gaat
DRONKEN_AMP = 4.5         # hoe hard hij op en neer zwabbert
DRONKEN_DUW = 3.0         # extra duw omhoog als je de knop vasthoudt

# --- Turbo-modus: rent altijd op topsnelheid vooruit, kan niet stoppen (keihard!) ---
TURBO_SNELHEID = 9        # hoe snel je onstopbaar vooruit raast

# --- Ritme-flip-modus: de zwaartekracht draait op een VASTE maat om (geen toeval) ---
RITME_INTERVAL = 42       # om de hoeveel stapjes de zwaartekracht omklapt

# --- Stuiteraar-modus: stuitert altijd vanzelf (als op een trampoline) ---
STUITER_KRACHT = 13       # hoe hoog je elke keer automatisch stuitert

# --- Draaibesturing-modus: een blokje met echte zwaartekracht, maar de stuur-richting
#     draait langzaam rond (geen toeval). Rechts/links duwen in die draaiende richting. ---
DRAAI_SNELHEID = 0.0075   # hoe snel de stuur-richting ronddraait (nog eens 2x langzamer)

# --- Boemerang-modus: een elastiek trekt je steeds terug naar je startpunt ---
BOEM_VEER = 0.06          # hoe hard het elastiek terugtrekt (hoe verder weg, hoe sterker)

# --- Stamper-modus: knop in de lucht = keihard naar beneden stampen ---
STAMP_KRACHT = 20         # hoe snel je naar beneden stampt

# --- Zweefspringer-modus: lage zwaartekracht -> lange, zwevende sprongen ---
ZWEEF_ZWAARTE = 0.35      # welk deel van de gewone zwaartekracht je voelt (lichter = zweveriger)

# --- Groeier-modus: hoe langer je loopt, hoe groter je wordt ---
GROEI_STAP = 0.01         # hoeveel je per stapje groeit/krimpt
GROEI_MAX = 2.5           # hoe groot je maximaal wordt

# --- Zwaargewicht-modus: enorme zwaartekracht (valt als een steen, springt laag) ---
ZWAAR_FACTOR = 2.3        # hoeveel keer sterker de zwaartekracht is

# --- Versneller-modus: hoe langer je één kant op loopt, hoe sneller je gaat ---
VERSNEL_STAP = 0.12       # hoeveel snelheid je er per stapje bij krijgt
VERSNEL_MAX = 8           # hoeveel extra snelheid je maximaal krijgt

# --- Wind-modus: een windvlaag duwt je opzij; hij draait op een vaste maat om ---
WIND_KRACHT = 2.2         # hoe hard de wind je opzij duwt
WIND_INTERVAL = 120       # om de hoeveel stapjes de wind van kant wisselt

# --- Metronoom-modus: springen mag ALLEEN precies op de tel (geen toeval) ---
METRO_INTERVAL = 30       # om de hoeveel stapjes er een 'tik' is (30 = elke halve seconde)
METRO_VENSTER = 4         # hoeveel stapjes rond de tik je sprong nog telt (klein = moeilijk)

# --- Katapult-modus: je wordt steeds in dezelfde boog weggeschoten ---
KATA_OMHOOG = 13          # hoe hard je omhoog wordt geschoten bij elke lancering
KATA_VOORUIT = 6          # hoe hard je vooruit wordt geschoten bij elke lancering
KATA_STUUR = 0.25         # hoe klein beetje je in de lucht mag bijsturen

# --- Krimpsprong-modus: elke sprong in de lucht is lager dan de vorige ---
KRIMP_AF = 0.62           # elke volgende sprong is nog maar dit deel van de vorige
KRIMP_MIN = 0.18          # kleiner dan dit -> geen sprong meer (tot je weer land)

# --- Turbo-flip: turbo-snelheid + de zwaartekracht flipt op de maat (heel moeilijk) ---
#     (gebruikt TURBO_SNELHEID en RITME_INTERVAL die hierboven al bestaan)

# --- Spiegel-katapult: als katapult, maar je bijsturen is omgedraaid (gebruikt KATA_-waarden) ---

# --- Schaduw: een schaduw loopt je oude route na; raakt hij je, dan ga je af ---
SCHADUW_DELAY = 45        # hoeveel stapjes de schaduw achter je aan loopt (~0.75 sec)

# --- Ping-pong: kaatst vanzelf tussen vloer en plafond; elke kaats flipt de zwaartekracht ---
PINGPONG_SNELHEID = 7     # hoe snel je op en neer kaatst

# --- Spook: zweeft zacht (knop = omhoog) en wordt steeds even onzichtbaar ---
SPOOK_STUW = 0.4          # hoe hard de knop je omhoog duwt
SPOOK_ZWAARTE = 0.22      # hoe zacht je zakt (zweverig)
SPOOK_MAX = 5             # hoogste zweefsnelheid
SPOOK_ONZICHT_NA = 80     # om de zoveel stapjes verdwijnt hij even
SPOOK_ONZICHT_DUUR = 22   # hoelang hij dan (bijna) onzichtbaar is

# --- Vleermuis: fladdert (tik = vleugelslag omhoog) en wiebelt griezelig heen en weer ---
VLEERMUIS_FLAP = 6        # hoe hard elke vleugelslag omhoog duwt
VLEERMUIS_ZWAARTE = 0.35  # lichte zwaartekracht (zweverig)
VLEERMUIS_WIEBEL = 1.8    # hoe ver hij vanzelf heen en weer wiebelt

# --- Zombie: sjokt langzaam en zwaar, springt maar laag ---
ZOMBIE_TRAAG = 0.55       # zombie loopt maar half zo snel
ZOMBIE_SPRONG = 0.62      # zombie springt maar laag
ZOMBIE_ZWAARTE = 1.4      # iets zwaardere val (voelt log)

# --- Pompoenkop: laat een vurig spoor achter en gloeit eng ---
POMP_SPOOR = 14           # hoeveel vuur-plekjes er achter je aan zweven

# --- Draaibol-modus: elke druk draait de zwaartekracht een kwartslag ---
# Bij elke stand hoort een zwaartekracht-richting (x, y):
#   0 = naar beneden, 1 = naar rechts, 2 = naar boven, 3 = naar links
GRAV_VEC = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}


class Speler:
    """Het poppetje dat de speler bestuurt: een geel vierkantje met een gezichtje."""

    def __init__(self):
        # Startpositie
        self.x = 50
        self.y = 100
        self.BASIS_BREEDTE = 32          # normale grootte
        self.BASIS_HOOGTE = 32
        self.breedte = 32
        self.hoogte = 32
        self.grootte_factor = 1.0        # 1 = normaal, >1 = groot, <1 = klein
        self.grootte_timer = 0           # hoelang het groot/klein-effect nog duurt
        self.sleutels = 0                # hoeveel sleutels je hebt (voor deuren)

        # Bewegingssnelheid
        self.snelheid_x = 0
        self.snelheid_y = 0

        # Is de speler op de grond? (nodig voor springen)
        self.staat_op_grond = False

        # Welke toetsen zijn ingedrukt?
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False

        # --- Levens ---
        self.levens = LEVENS_BEGIN

        # --- Power-up timers (tellen af per frame) ---
        self.onkwetsbaar_timer = 0      # ⭐ Ster: niet geraakt kunnen worden
        self.snelheid_boost_timer = 0   # 💨 Snelheid: dubbel zo snel
        self.dubbel_sprong_timer = 0    # 🦘 Dubbel springen: nog een keer springen
        self.schiet_timer = 0           # 🔫 Schieten: kogels afschieten met Z

        # Heeft de speler zijn extra sprong al gebruikt?
        self.heeft_dubbel_gesprongen = False

        # Richting waar de speler naar kijkt (True = rechts, False = links)
        self.kijkt_rechts = True

        # Extra snelheid en spronghoogte door punten (elke 10 punten = +1)
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

        # Knippercyclus voor als de speler onkwetsbaar is
        self._knippering = 0

        # Draai-stand (graden) — voor de tollende kubus in de racemodus
        self.rotatie = 0

        # Kleur van het poppetje (standaard geel; bij 2 spelers blauw/rood)
        self.kleur = SPELER_KLEUR

        # --- Speciale modi (Geometry Dash): blok/vliegtuig/ufo/bal/golf/robot/spin ---
        self.modus = "blok"              # in welke vorm ben je nu?
        self.vlieg_omhoog = False        # knop-vasthouden (vliegtuig, golf, robot)
        self.zwaartekracht_richting = 1  # 1 = omlaag, -1 = omhoog (bal en spin)
        self._robot_boost = 0            # hoeveel frames de robot nog omhoog mag duwen
        self._heli_omhoog = True         # helikopter: gaat hij nu omhoog (True) of omlaag (False)?
        self._grav_d = 0                 # draaibol: welke kant valt de zwaartekracht (0..3)
        self._val_snelheid = 0           # draaibol: hoe snel je in de zwaartekracht-richting valt
        self.plafond = VLIEG_PLAFOND     # hoogste hoogte; None = geen plafond (oneindig omhoog)
        self.kloon = None                # dubbel-portaal: een tweede kopie van jou (of None)
        self.snelheid_factor = 1.0       # snelheid-portaal (x0.5 / x1 / x2 / x5 / x10)
        self._muur_kant = 0              # ninja: raak je nu een muur? (-1 links, 1 rechts, 0 nee)
        self._flits_teller = 0           # flits: hoelang geleden je laatste teleport-sprongetje was
        self._vert_buffer = []           # vertraagd: bewaarde toetsen (voor de vertraging)
        self._vert_spring_wacht = 0      # vertraagd: hoelang nog tot je sprong echt komt
        self._dronken_fase = 0.0         # dronken: waar we in de op-en-neer-wiebel zitten
        self._ritme_teller = 0           # ritme-flip: tel tot de volgende zwaartekracht-flip
        self._stuur_hoek = 0.0           # draaibesturing: welke kant 'rechts' nu op wijst
        self._anker_x = None             # boemerang: het punt waar het elastiek je heen trekt
        self._versnel = 0.0              # versneller: hoeveel extra snelheid je nu hebt
        self._versnel_richting = 0       # versneller: welke kant je op versnelt (-1/0/1)
        self._wind_teller = 0            # wind: tel tot de wind van kant wisselt
        self._wind_richting = 1          # wind: welke kant de wind nu op blaast (1/-1)
        self.eigen_instel = None         # zelfgemaakt poppetje: dict met vorm/kleur/kunstjes
        self._lucht_sprongen = 0         # eigen poppetje: hoeveel keer je al in de lucht sprong
        self._metro_teller = 0           # metronoom: tel tot de volgende 'tik'
        self._krimp_nr = 0               # krimpsprong: hoeveelste sprong sinds je laatst stond
        self._tegen_flip = False         # tegendraads: zijn links/rechts nu omgedraaid?
        self._vorige_grond = False       # onthoud of je vorige stap op de grond stond
        self._schaduw_pad = []           # schaduw: bewaarde plekjes (x, y) van je route
        self._spook_teller = 0           # spook: tel tot hij weer even onzichtbaar wordt
        self._vleer_fase = 0.0           # vleermuis: waar we in de wiebel zitten
        self._pomp_spoor = []            # pompoenkop: bewaarde plekjes voor het vuur-spoor

    def reset(self):
        """Zet de speler terug naar de beginpositie (bij het opnieuw spelen van een level)."""
        self.x = 50
        self.y = 100
        self.snelheid_x = 0
        self.snelheid_y = 0
        self.staat_op_grond = False
        self.links_ingedrukt = False
        self.rechts_ingedrukt = False
        # Power-up effecten stoppen bij het herstarten
        self.onkwetsbaar_timer = 0
        self.snelheid_boost_timer = 0
        self.dubbel_sprong_timer = 0
        self.schiet_timer = 0
        self.heeft_dubbel_gesprongen = False
        self.rotatie = 0
        self.vlieg_omhoog = False           # knop-vasthouden reset
        self.modus = "blok"                 # begin weer als gewoon blokje
        self.zwaartekracht_richting = 1     # zwaartekracht weer gewoon omlaag
        self._robot_boost = 0               # robot-duw reset
        self._heli_omhoog = True            # helikopter begint omhoog
        self._grav_d = 0                    # draaibol: zwaartekracht weer naar beneden
        self._val_snelheid = 0              # draaibol: valsnelheid reset
        self.snelheid_factor = 1.0          # snelheid weer normaal
        self.grootte_factor = 1.0           # weer normale grootte
        self.grootte_timer = 0
        self.breedte = self.BASIS_BREEDTE
        self.hoogte = self.BASIS_HOOGTE
        self.sleutels = 0                   # sleutels kwijt bij herstart
        self.kloon = None                   # kloon weg bij herstart
        self._muur_kant = 0                 # ninja: geen muur meer geraakt
        self._flits_teller = 0              # flits: teller reset
        self._vert_buffer = []              # vertraagd: buffer leeg
        self._vert_spring_wacht = 0         # vertraagd: geen wachtende sprong
        self._dronken_fase = 0.0            # dronken: wiebel terug naar begin
        self._ritme_teller = 0              # ritme-flip: teller reset
        self._stuur_hoek = 0.0              # draaibesturing: stuur-richting terug naar begin
        self._anker_x = None                # boemerang: ankerpunt reset
        self._versnel = 0.0                 # versneller: reset
        self._versnel_richting = 0
        self._wind_teller = 0               # wind: reset
        self._wind_richting = 1
        self._lucht_sprongen = 0            # eigen poppetje: luchtsprongen reset
        self._metro_teller = 0              # metronoom: teller terug naar begin
        self._krimp_nr = 0                  # krimpsprong: teller reset
        self._tegen_flip = False            # tegendraads: links/rechts weer gewoon
        self._vorige_grond = False          # grond-onthoud reset
        self._schaduw_pad = []              # schaduw: route-geheugen leeg
        self._spook_teller = 0              # spook: onzichtbaar-teller reset
        self._vleer_fase = 0.0              # vleermuis: wiebel terug naar begin
        self._pomp_spoor = []               # pompoenkop: vuur-spoor leeg

    def volledig_reset(self):
        """Reset alles inclusief levens (voor een nieuw spel)."""
        self.reset()
        self.levens = LEVENS_BEGIN
        # Bonussen ook resetten — anders is de speler na game over nog steeds snel
        self.snelheid_bonus = 0
        self.sprong_bonus = 0

    def bijwerken(self, level_breedte, platforms):
        """Beweeg de speler en controleer botsingen met platforms."""

        # Timers aftikken
        if self.onkwetsbaar_timer > 0:
            self.onkwetsbaar_timer -= 1
            self._knippering = (self._knippering + 1) % 6
        if self.snelheid_boost_timer > 0:
            self.snelheid_boost_timer -= 1
        if self.dubbel_sprong_timer > 0:
            self.dubbel_sprong_timer -= 1
            if self.dubbel_sprong_timer == 0:
                self.heeft_dubbel_gesprongen = False
        if self.schiet_timer > 0:
            self.schiet_timer -= 1
        if self.grootte_timer > 0:
            self.grootte_timer -= 1
            if self.grootte_timer == 0:
                self.zet_grootte(1.0, 0)     # weer normale grootte

        # Draaibol heeft zijn eigen natuurkunde (zwaartekracht kan 4 kanten op)
        if self.modus == "draaibol":
            self._draaibol_bijwerken(level_breedte, platforms)
            return

        # Draaibesturing heeft zijn eigen natuurkunde (de stuur-richting draait rond)
        if self.modus == "draaisturing":
            self._draaisturing_bijwerken(level_breedte, platforms)
            return

        # Chaos: de zwaartekracht klapt op willekeurige momenten vanzelf om
        if self.modus == "chaos" and random.random() < CHAOS_KANS:
            self.zwaartekracht_richting *= -1

        # Ritme-flip (en turbo-flip): de zwaartekracht klapt op een VASTE maat om
        if self.modus in ("ritme", "turboflip"):
            self._ritme_teller += 1
            if self._ritme_teller >= RITME_INTERVAL:
                self._ritme_teller = 0
                self.zwaartekracht_richting *= -1

        # Schaduw: bewaar elke stap je plekje, zodat de schaduw je oude route kan nalopen
        if self.modus == "schaduw":
            self._schaduw_pad.append((self.x, self.y))
            if len(self._schaduw_pad) > SCHADUW_DELAY:
                self._schaduw_pad.pop(0)

        # Spook: tel door zodat hij steeds een moment (bijna) onzichtbaar wordt
        if self.modus == "spook":
            self._spook_teller = (self._spook_teller + 1) % (SPOOK_ONZICHT_NA + SPOOK_ONZICHT_DUUR)

        # Pompoenkop: bewaar plekjes voor het vurige spoor achter je aan
        if self.modus == "pompoenkop":
            self._pomp_spoor.append((self.x + self.breedte / 2, self.y + self.hoogte / 2))
            if len(self._pomp_spoor) > POMP_SPOOR:
                self._pomp_spoor.pop(0)

        # Metronoom: tel de maat mee. Springen mag straks alleen precies op de 'tik'.
        if self.modus == "metronoom":
            self._metro_teller += 1
            if self._metro_teller >= METRO_INTERVAL:
                self._metro_teller = 0

        # Bepaal de snelheid: normaal + snelheidsboost power-up + punten-bonus
        snelheid = SPELER_SNELHEID + self.snelheid_bonus
        if self.snelheid_boost_timer > 0:
            snelheid *= 2   # Dubbel bij snelheidsboost power-up
        snelheid *= self.snelheid_factor   # snelheid-portaal (x0.5 / x2 / x10 ...)
        if self.modus == "ninja":
            snelheid *= NINJA_SNELHEID     # de ninja is lekker snel
        if self.modus == "zombie":
            snelheid *= ZOMBIE_TRAAG       # de zombie sjokt langzaam
        if self.modus == "eigen" and self._eigen("snel"):
            snelheid *= 1.6                # zelfgemaakt poppetje met het 'Snel'-kunstje

        # Horizontale beweging — elke modus doet het net iets anders
        if self.modus == "flits":
            # Flits: loopt niet, maar teleporteert met sprongetjes vooruit.
            self._flits_teller += 1
            self.snelheid_x = 0
            f_richting = 0
            if self.rechts_ingedrukt:
                f_richting = 1
                self.kijkt_rechts = True
            elif self.links_ingedrukt:
                f_richting = -1
                self.kijkt_rechts = False
            if f_richting != 0 and self._flits_teller >= FLITS_INTERVAL:
                self._flits_teller = 0
                oude_x = self.x
                # Spring precies naar de VOLGENDE blok-rand (netjes uitgelijnd op de blokjes)
                if f_richting > 0:
                    doel = (math.floor(self.x / FLITS_BLOK) + 1) * FLITS_BLOK
                else:
                    doel = (math.ceil(self.x / FLITS_BLOK) - 1) * FLITS_BLOK
                self.x = max(0, min(level_breedte - self.breedte, doel))
                # niet dwars ín een muur teleporteren -> blijf dan staan
                for p in platforms:
                    if (getattr(p, "vast", True) and not getattr(p, "is_schuin", False)
                            and self._overlapt(p)):
                        self.x = oude_x
                        break
        else:
            # Vertraagd: gebruik de toetsen van een halve seconde geleden (superlastig!)
            if self.modus == "vertraagd":
                self._vert_buffer.append((self.links_ingedrukt, self.rechts_ingedrukt))
                if len(self._vert_buffer) > VERT_DELAY:
                    L, R = self._vert_buffer.pop(0)
                else:
                    L, R = False, False       # buffer nog niet vol -> nog niks doen
            else:
                L, R = self.links_ingedrukt, self.rechts_ingedrukt

            # Eigen poppetje met 'Spiegel': links en rechts omdraaien
            if self.modus == "eigen" and self._eigen("spiegel"):
                L, R = R, L

            if (self.modus in ("turbo", "turboflip")
                    or (self.modus == "eigen" and self._eigen("turbo"))):
                # Turbo: je raast altijd op topsnelheid naar rechts en kunt NIET stoppen!
                # (Turbo-flip doet dit óók, plus de zwaartekracht flipt op de maat.)
                self.snelheid_x = TURBO_SNELHEID
                self.kijkt_rechts = True
            elif self.modus == "versneller":
                # Versneller: hoe langer je dezelfde kant op loopt, hoe sneller je gaat
                if L and not R:
                    if self._versnel_richting != -1:
                        self._versnel = 0        # net van kant gewisseld -> opnieuw beginnen
                    self._versnel_richting = -1
                    self._versnel = min(self._versnel + VERSNEL_STAP, VERSNEL_MAX)
                    self.snelheid_x = -(snelheid + self._versnel)
                    self.kijkt_rechts = False
                elif R and not L:
                    if self._versnel_richting != 1:
                        self._versnel = 0
                    self._versnel_richting = 1
                    self._versnel = min(self._versnel + VERSNEL_STAP, VERSNEL_MAX)
                    self.snelheid_x = snelheid + self._versnel
                    self.kijkt_rechts = True
                else:
                    self._versnel = 0            # stilstaan -> snelheid weer kwijt
                    self._versnel_richting = 0
                    self.snelheid_x = 0
            elif self.modus == "ijs":
                # IJs: spiegelglad! Je snelheid verandert maar langzaam naar wat je wilt,
                # dus je glijdt door en stopt bijna niet.
                if L:
                    doel = -snelheid
                    self.kijkt_rechts = False
                elif R:
                    doel = snelheid
                    self.kijkt_rechts = True
                else:
                    doel = 0
                self.snelheid_x += (doel - self.snelheid_x) * IJS_GRIP
            elif self.modus == "spiegel":
                # Spiegel: links en rechts zijn OMGEDRAAID!
                if L:
                    self.snelheid_x = snelheid    # links ingedrukt -> ga naar rechts
                    self.kijkt_rechts = True
                elif R:
                    self.snelheid_x = -snelheid   # rechts ingedrukt -> ga naar links
                    self.kijkt_rechts = False
                else:
                    self.snelheid_x = 0
            elif self.modus == "eigen" and self._eigen("glad"):
                # Zelfgemaakt poppetje met het 'Glad'-kunstje: je glijdt door (als op ijs)
                if L:
                    doel = -snelheid
                    self.kijkt_rechts = False
                elif R:
                    doel = snelheid
                    self.kijkt_rechts = True
                else:
                    doel = 0
                self.snelheid_x += (doel - self.snelheid_x) * IJS_GRIP
            elif self.modus == "tegendraads":
                # Tegendraads: elke keer dat je landt wisselen links en rechts (zie onderaan).
                Lt, Rt = (R, L) if self._tegen_flip else (L, R)
                if Lt:
                    self.snelheid_x = -snelheid
                    self.kijkt_rechts = False
                elif Rt:
                    self.snelheid_x = snelheid
                    self.kijkt_rechts = True
                else:
                    self.snelheid_x = 0
            elif self.modus in ("katapult", "spiegelkatapult"):
                # Katapult: je stuurt maar een heel klein beetje bij; de vaste boog doet de rest.
                # Spiegel-katapult: het bijsturen is OMGEDRAAID (links duwt naar rechts).
                omgekeerd = self.modus == "spiegelkatapult"
                links_duw = R if omgekeerd else L
                rechts_duw = L if omgekeerd else R
                if links_duw:
                    self.snelheid_x -= KATA_STUUR
                    self.kijkt_rechts = False
                elif rechts_duw:
                    self.snelheid_x += KATA_STUUR
                    self.kijkt_rechts = True
                self.snelheid_x *= 0.99         # een piepklein beetje luchtweerstand
            elif self.modus == "vleermuis":
                # Vleermuis: gewone links/rechts, plus een griezelige wiebel heen en weer
                self._vleer_fase += 0.15
                wiebel = math.sin(self._vleer_fase) * VLEERMUIS_WIEBEL
                if L:
                    self.snelheid_x = -snelheid + wiebel
                    self.kijkt_rechts = False
                elif R:
                    self.snelheid_x = snelheid + wiebel
                    self.kijkt_rechts = True
                else:
                    self.snelheid_x = wiebel
            elif L:
                self.snelheid_x = -snelheid
                self.kijkt_rechts = False   # Speler kijkt naar links
            elif R:
                self.snelheid_x = snelheid
                self.kijkt_rechts = True    # Speler kijkt naar rechts
            else:
                self.snelheid_x = 0

            # Magneet: je wordt naar de dichtstbijzijnde muur naast je toe getrokken
            if self.modus == "magneet" or (self.modus == "eigen" and self._eigen("magneet")):
                mx = self.x + self.breedte / 2
                dichtst = None
                beste = 1e9
                for p in platforms:
                    if not getattr(p, "vast", True) or getattr(p, "is_schuin", False):
                        continue
                    # alleen blokken die naast je zitten (op jouw hoogte) tellen als 'muur'
                    if not (self.y + self.hoogte > p.y + 4 and self.y < p.y + p.hoogte - 4):
                        continue
                    for rand in (p.x, p.x + p.breedte):
                        d = abs(rand - mx)
                        if d < beste:
                            beste = d
                            dichtst = rand
                if dichtst is not None:
                    self.snelheid_x += (MAGNEET_KRACHT if dichtst > mx else -MAGNEET_KRACHT)

            # Boemerang: een elastiek trekt je steeds terug naar je startpunt
            if self.modus == "boemerang":
                if self._anker_x is None:
                    self._anker_x = self.x       # onthoud waar je begon
                self.snelheid_x += (self._anker_x - self.x) * BOEM_VEER

            # Wind: een windvlaag duwt je opzij; om de zoveel tijd draait hij om
            if self.modus == "wind" or (self.modus == "eigen" and self._eigen("wind")):
                self._wind_teller += 1
                if self._wind_teller >= WIND_INTERVAL:
                    self._wind_teller = 0
                    self._wind_richting *= -1
                self.snelheid_x += WIND_KRACHT * self._wind_richting

            self.x += self.snelheid_x

        # Ninja, magneet én klimmer: stop tegen een muur (i.p.v. erdoor of dood) en onthoud de kant.
        # Zo kunnen ninja en klimmer zich later van de muur afzetten (muursprong).
        if (self.modus in ("ninja", "magneet", "klimmer", "plakker")
                or (self.modus == "eigen"
                    and (self._eigen("muur") or self._eigen("magneet") or self._eigen("plakken")))):
            self._muur_kant = 0
            for p in platforms:
                if not getattr(p, "vast", True) or getattr(p, "is_schuin", False):
                    continue
                if self._overlapt(p):
                    if self.snelheid_x > 0:
                        self.x = p.x - self.breedte
                        self._muur_kant = 1     # muur zit rechts van je
                    elif self.snelheid_x < 0:
                        self.x = p.x + p.breedte
                        self._muur_kant = -1    # muur zit links van je

        # Niet buiten het level lopen
        if self.x < 0:
            self.x = 0
        if self.x + self.breedte > level_breedte:
            self.x = level_breedte - self.breedte

        # Dichte deuren houden je tegen (je gaat er NIET dood van, je stopt ervoor)
        for p in platforms:
            if getattr(p, "is_deur", False) and not p.open:
                if (self.x < p.x + p.breedte and self.x + self.breedte > p.x and
                        self.y < p.y + p.hoogte and self.y + self.hoogte > p.y):
                    if self.snelheid_x > 0:
                        self.x = p.x - self.breedte
                    elif self.snelheid_x < 0:
                        self.x = p.x + p.breedte

        # Groeier: hoe langer je loopt, hoe groter je wordt (stilstaan = weer krimpen)
        if self.modus == "groeier" or (self.modus == "eigen" and self._eigen("groeien")):
            if self.links_ingedrukt or self.rechts_ingedrukt:
                doel = min(self.grootte_factor + GROEI_STAP, GROEI_MAX)
            else:
                doel = max(self.grootte_factor - GROEI_STAP, 1.0)
            if abs(doel - self.grootte_factor) > 0.0001:
                self.zet_grootte(doel, 0)     # frames=0 -> geen automatische terugkeer

        # Vertraagd: een gevraagde sprong komt pas ná de vertraging echt
        if self.modus == "vertraagd" and self._vert_spring_wacht > 0:
            self._vert_spring_wacht -= 1
            if self._vert_spring_wacht == 0:
                self._doe_sprong()

        # Verticale beweging hangt af van de modus
        richting = self.zwaartekracht_richting   # 1 = gewoon, -1 = alles omgedraaid (kloon!)
        if self.modus == "dronken":
            # Dronken: zwabbert vanzelf op en neer; knop vasthouden = extra duwtje omhoog.
            self._dronken_fase += DRONKEN_SNELHEID
            self.snelheid_y = math.sin(self._dronken_fase) * DRONKEN_AMP
            if self.vlieg_omhoog:
                self.snelheid_y += DRONKEN_DUW
        elif self.modus == "vliegtuig":
            # Vliegtuig: knop vasthouden = stuw omhoog, anders zak je langzaam.
            # Maal met de richting, zodat de kloon ondersteboven kan vliegen.
            if self.vlieg_omhoog:
                self.snelheid_y += VLIEG_STUW * richting
            self.snelheid_y -= VLIEG_ZWAARTE * richting
            self.snelheid_y = max(-VLIEG_MAX, min(VLIEG_MAX, self.snelheid_y))
        elif self.modus == "golf":
            # Golf: schuin omhoog als je vasthoudt, anders schuin omlaag (45 graden).
            # Maal met de richting zodat de kloon precies de andere kant op golft.
            self.snelheid_y = (snelheid if self.vlieg_omhoog else -snelheid) * richting
        elif self.modus == "heli":
            # Helikopter: druk = omhoog, druk nog eens = omlaag (steeds wisselen).
            # Maal met de richting zodat de kloon de andere kant op vliegt.
            self.snelheid_y = (HELI_SNELHEID if self._heli_omhoog else -HELI_SNELHEID) * richting
        elif self.modus == "ballon":
            # Ballon: zweeft vanzelf omhoog; knop vasthouden = zakken.
            if self.vlieg_omhoog:
                self.snelheid_y -= BALLON_ZAK * richting
            else:
                self.snelheid_y += BALLON_ZWEEF * richting
            self.snelheid_y = max(-VLIEG_MAX, min(VLIEG_MAX, self.snelheid_y))
        elif self.modus == "raket":
            # Raket: knop vasthouden = snel omhoog schieten, loslaten = snel vallen.
            # Maal met de richting zodat de kloon ondersteboven ook werkt.
            if self.vlieg_omhoog:
                self.snelheid_y += RAKET_STUW * richting
            self.snelheid_y -= RAKET_ZWAARTE * richting
            self.snelheid_y = max(-RAKET_MAX, min(RAKET_MAX, self.snelheid_y))
        elif self.modus == "draak":
            # Draak: zachte duw omhoog, zachte val -> hij blijft nazweven.
            # Doordat alles zo zacht is, wiebelt hij door en is hij lastig recht te houden.
            if self.vlieg_omhoog:
                self.snelheid_y += DRAAK_STUW * richting
            self.snelheid_y -= DRAAK_ZWAARTE * richting
            self.snelheid_y = max(-DRAAK_MAX, min(DRAAK_MAX, self.snelheid_y))
        elif self.modus == "spook":
            # Spook: zweeft zacht. Knop vasthouden = omhoog, anders zak je langzaam.
            if self.vlieg_omhoog:
                self.snelheid_y += SPOOK_STUW * richting
            self.snelheid_y -= SPOOK_ZWAARTE * richting
            self.snelheid_y = max(-SPOOK_MAX, min(SPOOK_MAX, self.snelheid_y))
        elif self.modus == "vleermuis":
            # Vleermuis: lichte zwaartekracht (zweverig); elke tik geeft een vleugelslag omhoog.
            self.snelheid_y -= ZWAARTEKRACHT * VLEERMUIS_ZWAARTE * self.zwaartekracht_richting
            self.snelheid_y = max(-8, min(8, self.snelheid_y))
        elif self.modus == "zombie":
            # Zombie: iets zwaardere val, voelt log en zwaar.
            self.snelheid_y -= ZWAARTEKRACHT * ZOMBIE_ZWAARTE * self.zwaartekracht_richting
        elif self.modus == "pingpong":
            # Ping-pong: constante snelheid op of neer. De richting flipt bij elke kaats
            # tegen de vloer of het plafond (zie de botsingen hieronder).
            self.snelheid_y = PINGPONG_SNELHEID * (-self.zwaartekracht_richting)
        elif self.modus in ("bal", "spin"):
            # Bal/spin: zwaartekracht in de huidige richting (kan omgedraaid zijn)
            self.snelheid_y -= ZWAARTEKRACHT * 1.3 * self.zwaartekracht_richting
            self.snelheid_y = max(-11, min(11, self.snelheid_y))
        elif self.modus == "robot":
            # Robot: terwijl je vasthoudt blijf je omhoog duwen (langer = hoger).
            # Maal met de richting zodat de kloon ondersteboven ook hoger kan springen.
            if self.vlieg_omhoog and self._robot_boost > 0 and self.snelheid_y * richting > 0:
                self.snelheid_y += ROBOT_EXTRA * richting
                self._robot_boost -= 1
            self.snelheid_y -= ZWAARTEKRACHT * richting
        elif self.modus == "zweefspringer":
            # Zweefspringer: lage zwaartekracht -> je blijft lang in de lucht hangen.
            self.snelheid_y -= ZWAARTEKRACHT * ZWEEF_ZWAARTE * self.zwaartekracht_richting
        elif self.modus == "zwaargewicht":
            # Zwaargewicht: enorme zwaartekracht, je valt als een steen.
            self.snelheid_y -= ZWAARTEKRACHT * ZWAAR_FACTOR * self.zwaartekracht_richting
        elif self.modus == "plakker":
            # Plakker: raak je een muur, dan blijf je eraan plakken (glijdt niet omlaag).
            if self._muur_kant != 0 and self.snelheid_y <= 0:
                self.snelheid_y = 0
            else:
                self.snelheid_y -= ZWAARTEKRACHT * self.zwaartekracht_richting
        elif self.modus == "eigen":
            # Plakken: aan een muur blijf je hangen (glijdt niet naar beneden)
            if self._eigen("plakken") and self._muur_kant != 0 and self.snelheid_y <= 0:
                self.snelheid_y = 0
            else:
                # 'Zweven' = lichter, 'Zwaar' = valt sneller
                if self._eigen("zweef"):
                    deel = ZWEEF_ZWAARTE
                elif self._eigen("zwaar"):
                    deel = ZWAAR_FACTOR
                else:
                    deel = 1.0
                self.snelheid_y -= ZWAARTEKRACHT * deel * self.zwaartekracht_richting
        else:
            # Blok en UFO: gewone zwaartekracht. De richting kan omgedraaid zijn door
            # een draai-bol (dan val je juist naar BOVEN).
            self.snelheid_y -= ZWAARTEKRACHT * self.zwaartekracht_richting
        self.y += self.snelheid_y
        self.staat_op_grond = False
        omgedraaid = self.zwaartekracht_richting == -1

        # Botsingen met platforms
        for platform in platforms:
            # Landen op het platform (van bovenaf)
            if platform.raakt(self.x, self.y, self.breedte, self.hoogte):
                self.y = platform.y + platform.hoogte
                self.x += getattr(platform, "dx", 0)  # meerijden op een bewegend blok
                self.heeft_dubbel_gesprongen = False  # Op de grond: extra sprong herlaadbaar
                self._lucht_sprongen = 0              # eigen poppetje: luchtsprongen herladen
                self._robot_boost = 0                 # robot mag pas na een nieuwe tik duwen
                self._krimp_nr = 0                    # krimpsprong: weer op volle hoogte beginnen
                # Verdwijnblok: laat het weten dat je erop staat (het gaat dan verdwijnen)
                if hasattr(platform, "aangeraakt"):
                    platform.aangeraakt()
                # Stuiterblok: stuiter omhoog i.p.v. blijven staan
                stuiter = getattr(platform, "stuiter", 0)
                eigen_stuiter = self.modus == "eigen" and self._eigen("stuiter")
                if self.modus == "pingpong":
                    # Ping-pong: raak je de vloer, dan flipt de zwaartekracht en kaats je omhoog
                    self.zwaartekracht_richting = -1
                elif (self.modus == "stuiteraar" or eigen_stuiter) and not omgedraaid:
                    # Stuiteraar (of eigen poppetje met Stuiteren): altijd omhoog stuiteren
                    self.snelheid_y = STUITER_KRACHT
                elif stuiter and not omgedraaid:
                    self.snelheid_y = stuiter
                else:
                    self.snelheid_y = 0
                    if not omgedraaid:
                        self.staat_op_grond = True
            # Hoofd stoot tegen onderkant platform
            elif (self.snelheid_y > 0 and
                  platform.raakt_van_onder(self.x, self.y, self.breedte, self.hoogte)):
                self.y = platform.y - self.hoogte
                if self.modus == "pingpong":
                    # Ping-pong: raak je het plafond, dan flipt de zwaartekracht en kaats je omlaag
                    self.zwaartekracht_richting = 1
                else:
                    self.snelheid_y = 0
                    # Met omgekeerde zwaartekracht 'sta' je ONDER een platform
                    if omgedraaid:
                        self.staat_op_grond = True

        # Schuine blokken (hellingen): loop er soepel overheen omhoog/omlaag
        if not omgedraaid:
            midden = self.x + self.breedte / 2
            for platform in platforms:
                if not getattr(platform, "is_schuin", False):
                    continue
                if platform.x <= midden <= platform.x + platform.breedte:
                    opp = platform.hoogte_op(midden)      # hoogte van de helling hier
                    if self.snelheid_y <= 0 and self.y <= opp and self.y + self.hoogte > opp:
                        self.y = opp
                        self.snelheid_y = 0
                        self.staat_op_grond = True
                        self.heeft_dubbel_gesprongen = False
                        self._robot_boost = 0

        # In de speciale modi (of bij omgedraaide zwaartekracht): niet door het plafond.
        # Is self.plafond None, dan is er GEEN plafond en kun je oneindig omhoog.
        if (self.plafond is not None
                and (self.modus in ("vliegtuig", "ufo", "bal", "golf", "spin", "heli", "ballon", "raket", "kolibrie", "draak", "dronken", "pingpong", "spook", "vleermuis") or omgedraaid)
                and self.y + self.hoogte > self.plafond):
            self.y = self.plafond - self.hoogte
            if self.snelheid_y > 0:
                if self.modus == "pingpong":
                    self.zwaartekracht_richting = 1   # tegen het plafond -> kaats omlaag
                else:
                    self.snelheid_y = 0
                    if omgedraaid or self.modus in ("bal", "spin"):
                        self.staat_op_grond = True   # je 'ligt' tegen het plafond

        # Net geland (van de lucht op de grond)? Sommige poppetjes doen dan iets speciaals.
        net_geland = self.staat_op_grond and not self._vorige_grond
        if self.modus == "tegendraads" and net_geland:
            self._tegen_flip = not self._tegen_flip     # links en rechts wisselen om
        if self.modus in ("katapult", "spiegelkatapult") and self.staat_op_grond:
            # Meteen weer in precies dezelfde boog wegschieten (omhoog én vooruit)
            self.snelheid_y = KATA_OMHOOG
            self.snelheid_x = KATA_VOORUIT
            self.staat_op_grond = False
        self._vorige_grond = self.staat_op_grond

    def _eigen(self, sleutel):
        """Hulpje voor het zelfgemaakte poppetje: geef een instelling terug (of None)."""
        if not self.eigen_instel:
            return None
        return self.eigen_instel.get(sleutel)

    def flap(self):
        """UFO-modus: geef een klein sprongetje (bij elke tik).

        Maal met de richting zodat de kloon ondersteboven juist naar beneden flapt."""
        self.snelheid_y = FLAP_KRACHT * self.zwaartekracht_richting

    def kolibrie_flap(self):
        """Kolibrie: een KLEIN wiekje per tik. Je moet snel blijven tikken om te zweven."""
        self.snelheid_y = KOLIBRIE_FLAP * self.zwaartekracht_richting

    def vleermuis_flap(self):
        """Vleermuis: een vleugelslag omhoog bij elke tik (fladderen)."""
        self.snelheid_y = VLEERMUIS_FLAP * self.zwaartekracht_richting

    def zet_grootte(self, factor, frames):
        """Maak de speler groter of kleiner (factor) voor een aantal frames."""
        self.grootte_factor = factor
        self.grootte_timer = frames
        self.breedte = int(self.BASIS_BREEDTE * factor)
        self.hoogte = int(self.BASIS_HOOGTE * factor)

    def flip_zwaartekracht(self):
        """Bal-modus: draai de zwaartekracht om (van vloer naar plafond en terug)."""
        self.zwaartekracht_richting *= -1

    def heli_wissel(self):
        """Helikopter-modus: wissel tussen omhoog en omlaag vliegen (bij elke tik)."""
        self._heli_omhoog = not self._heli_omhoog

    def draaibol_draai(self):
        """Draaibol-modus: draai de zwaartekracht een kwartslag verder (0->1->2->3->0)."""
        self._grav_d = (self._grav_d + 1) % 4
        self._val_snelheid = 0     # begin schoon te vallen in de nieuwe richting

    def _overlapt(self, p):
        """Hulpje: overlapt de speler dit platform (rechthoek)?"""
        return (self.x < p.x + p.breedte and self.x + self.breedte > p.x and
                self.y < p.y + p.hoogte and self.y + self.hoogte > p.y)

    def _draaibol_bijwerken(self, level_breedte, platforms):
        """Draaibol: de zwaartekracht kan 4 kanten op. Je rolt langs de vloer/muur en
        met elke druk draait de zwaartekracht een kwartslag (zo rol je tegen muren op)."""
        gx, gy = GRAV_VEC[self._grav_d]     # zwaartekracht-richting
        fx, fy = -gy, gx                    # 'vooruit' = een kwartslag naast de zwaartekracht

        # Loop-snelheid langs de vloer (of muur)
        snelheid = SPELER_SNELHEID + self.snelheid_bonus
        if self.snelheid_boost_timer > 0:
            snelheid *= 2
        snelheid *= self.snelheid_factor
        run = 0
        if self.rechts_ingedrukt:
            run = snelheid
            self.kijkt_rechts = True
        elif self.links_ingedrukt:
            run = -snelheid
            self.kijkt_rechts = False

        # Vallen versnelt in de zwaartekracht-richting
        self._val_snelheid = min(self._val_snelheid + ZWAARTEKRACHT * 1.3, 11)

        # Zet loop + val om naar een gewone x- en y-snelheid
        self.snelheid_x = run * fx + self._val_snelheid * gx
        self.snelheid_y = run * fy + self._val_snelheid * gy
        self.staat_op_grond = False

        # Alleen vaste, rechte blokken tellen als muur/vloer
        vast = [p for p in platforms
                if getattr(p, "vast", True) and not getattr(p, "is_schuin", False)]

        # Eerst in de x-richting bewegen en botsingen oplossen
        self.x += self.snelheid_x
        for p in vast:
            if self._overlapt(p):
                if self.snelheid_x > 0:
                    self.x = p.x - self.breedte
                elif self.snelheid_x < 0:
                    self.x = p.x + p.breedte
                if gx != 0:                 # zwaartekracht wijst opzij -> je 'staat' tegen de muur
                    self._val_snelheid = 0
                    self.staat_op_grond = True

        # Daarna in de y-richting
        self.y += self.snelheid_y
        for p in vast:
            if self._overlapt(p):
                if self.snelheid_y > 0:
                    self.y = p.y - self.hoogte
                elif self.snelheid_y < 0:
                    self.y = p.y + p.hoogte
                if gy != 0:                 # zwaartekracht wijst omhoog/omlaag -> je staat op vloer/plafond
                    self._val_snelheid = 0
                    self.staat_op_grond = True

        # Binnen het speelveld blijven
        if self.x < 0:
            self.x = 0
        if self.x + self.breedte > level_breedte:
            self.x = level_breedte - self.breedte
        # Alleen een plafond als self.plafond niet None is (anders oneindig omhoog)
        if self.plafond is not None and self.y + self.hoogte > self.plafond:
            self.y = self.plafond - self.hoogte
            if gy > 0:
                self._val_snelheid = 0
                self.staat_op_grond = True

        # De bol tolt mee terwijl hij rolt (voor het plaatje)
        self.rotatie = (self.rotatie - run * 3) % 360

    def _draaisturing_bijwerken(self, level_breedte, platforms):
        """Draaibesturing: net als de draaibol, maar de zwaartekracht draait CONTINU mee
        met het blok. 'Beneden' draait dus rond: soms val je opzij, soms naar boven.
        Links/rechts = langs de vloer/muur rollen; springen = weg van de vloer."""
        # De hoek (en dus de zwaartekracht-richting) draait langzaam rond
        self._stuur_hoek += DRAAI_SNELHEID
        gx = math.sin(self._stuur_hoek)         # zwaartekracht-richting (bij hoek 0 = omlaag)
        gy = -math.cos(self._stuur_hoek)
        fx, fy = -gy, gx                        # 'vooruit' = een kwartslag naast de zwaartekracht

        # Loop-snelheid langs de vloer (of muur)
        snelheid = SPELER_SNELHEID + self.snelheid_bonus
        if self.snelheid_boost_timer > 0:
            snelheid *= 2
        snelheid *= self.snelheid_factor
        run = 0
        if self.rechts_ingedrukt:
            run = snelheid
            self.kijkt_rechts = True
        elif self.links_ingedrukt:
            run = -snelheid
            self.kijkt_rechts = False

        # Vallen versnelt in de zwaartekracht-richting
        self._val_snelheid = min(self._val_snelheid + ZWAARTEKRACHT * 1.3, 11)

        # Zet loop + val om naar een gewone x- en y-snelheid
        self.snelheid_x = run * fx + self._val_snelheid * gx
        self.snelheid_y = run * fy + self._val_snelheid * gy
        self.staat_op_grond = False

        # Alleen vaste, rechte blokken tellen als muur/vloer
        vast = [p for p in platforms
                if getattr(p, "vast", True) and not getattr(p, "is_schuin", False)]

        # Eerst x bewegen en botsingen oplossen
        self.x += self.snelheid_x
        for p in vast:
            if self._overlapt(p):
                if self.snelheid_x > 0:
                    self.x = p.x - self.breedte
                elif self.snelheid_x < 0:
                    self.x = p.x + p.breedte
                if abs(gx) > 0.3:               # zwaartekracht wijst opzij -> je 'staat' tegen de muur
                    self._val_snelheid = 0
                    self.staat_op_grond = True

        # Daarna y bewegen en botsingen oplossen
        self.y += self.snelheid_y
        for p in vast:
            if self._overlapt(p):
                if self.snelheid_y > 0:
                    self.y = p.y - self.hoogte
                elif self.snelheid_y < 0:
                    self.y = p.y + p.hoogte
                if abs(gy) > 0.3:              # zwaartekracht wijst omhoog/omlaag -> vloer/plafond
                    self._val_snelheid = 0
                    self.staat_op_grond = True

        # Binnen het speelveld blijven
        if self.x < 0:
            self.x = 0
        if self.x + self.breedte > level_breedte:
            self.x = level_breedte - self.breedte

    def robot_sprong(self):
        """Robot-modus: begin een sprong (vasthouden maakt hem hoger)."""
        if self.staat_op_grond:
            # Bij omgekeerde zwaartekracht spring je juist naar beneden
            self.snelheid_y = ROBOT_START * self.zwaartekracht_richting
            self._robot_boost = ROBOT_BOOST_FRAMES

    def spring(self):
        """Vraag een sprong aan. De meeste modi springen meteen, maar:
        - Vertraagd: de sprong komt pas een halve seconde later.
        - Dobbelsteen: de spronghoogte is elke keer willekeurig."""
        if self.modus == "vertraagd":
            self._vert_spring_wacht = VERT_DELAY   # de sprong komt straks pas echt
            return
        if self.modus == "metronoom":
            # Springen mag ALLEEN precies op de tel. Vlak vóór of ná de tik telt ook nog.
            op_de_tel = (self._metro_teller <= METRO_VENSTER
                         or self._metro_teller >= METRO_INTERVAL - METRO_VENSTER)
            if op_de_tel:
                self._doe_sprong()
            return
        if self.modus in ("katapult", "spiegelkatapult", "pingpong"):
            return                                 # deze poppetjes bewegen vanzelf, springen doet niks
        if self.modus == "krimpsprong":
            # Elke sprong in de lucht is lager dan de vorige; op de grond weer vol.
            factor = KRIMP_AF ** self._krimp_nr
            if factor < KRIMP_MIN:
                return                             # geen sprong meer tot je weer land
            self.snelheid_y = ((SPRING_KRACHT + self.sprong_bonus)
                               * factor * self.zwaartekracht_richting)
            self._krimp_nr += 1
            return
        if self.modus == "draaisturing":
            # Springen = wegschieten tegen de huidige (draaiende) zwaartekracht in
            if self.staat_op_grond:
                self._val_snelheid = -(SPRING_KRACHT + self.sprong_bonus)
            return
        if self.modus == "stamper":
            # Stamper: op de grond spring je; in de lucht STAMP je keihard naar beneden
            if self.staat_op_grond:
                self.snelheid_y = (SPRING_KRACHT + self.sprong_bonus) * self.zwaartekracht_richting
            else:
                self.snelheid_y = -STAMP_KRACHT * self.zwaartekracht_richting
            return
        if self.modus == "plakker":
            # Plakker: op de grond spring je; aan een muur klim je in hopjes omhoog
            if self.staat_op_grond:
                self.snelheid_y = (SPRING_KRACHT + self.sprong_bonus) * self.zwaartekracht_richting
            elif self._muur_kant != 0:
                self.snelheid_y = (SPRING_KRACHT * 0.7) * self.zwaartekracht_richting
            return
        if self.modus == "eigen":
            # Zelfgemaakt poppetje: springhoogte + extra kunstjes
            if self._eigen("superhoog"):
                hoog = 1.9
            elif self._eigen("hoog"):
                hoog = 1.4
            else:
                hoog = 1.0
            kracht = (SPRING_KRACHT + self.sprong_bonus) * hoog * self.zwaartekracht_richting
            if self.staat_op_grond:
                self.snelheid_y = kracht
                self._lucht_sprongen = 0
            elif self._muur_kant != 0 and (self._eigen("muur") or self._eigen("plakken")):
                # Muursprong (Muur duwt weg van de muur; Plakken klimt recht omhoog)
                self.snelheid_y = kracht
                if self._eigen("muur"):
                    self.snelheid_x = -self._muur_kant * NINJA_MUURSPRONG
                self._muur_kant = 0
            else:
                # Dubbelsprong = 1 keer in de lucht, Driesprong = 2 keer in de lucht
                max_lucht = 2 if self._eigen("driesprong") else (1 if self._eigen("dubbel") else 0)
                if self._lucht_sprongen < max_lucht:
                    self.snelheid_y = kracht
                    self._lucht_sprongen += 1
            return
        self._doe_sprong()

    def _doe_sprong(self):
        """Doe de sprong nu echt (hoger naarmate je meer punten hebt).

        Bij omgekeerde zwaartekracht (na een draai-bol) spring je juist naar BENEDEN,
        zodat je van het plafond af komt."""
        if self.modus == "dobbelsteen":
            # Dobbelsteen: een willekeurige spronghoogte (soms mini, soms mega!)
            sprongkracht = random.uniform(DOBBEL_MIN, DOBBEL_MAX) * self.zwaartekracht_richting
        elif self.modus == "zombie":
            # Zombie springt maar laag (log en zwaar)
            sprongkracht = (SPRING_KRACHT + self.sprong_bonus) * ZOMBIE_SPRONG * self.zwaartekracht_richting
        else:
            sprongkracht = (SPRING_KRACHT + self.sprong_bonus) * self.zwaartekracht_richting
        if self.modus == "klimmer":
            # Klimmer: kan NIET vanaf de grond springen, alleen zich van een muur afzetten
            if self._muur_kant != 0:
                self.snelheid_y = sprongkracht
                self.snelheid_x = -self._muur_kant * NINJA_MUURSPRONG
                self._muur_kant = 0
            return
        if self.staat_op_grond:
            self.snelheid_y = sprongkracht
        elif self.modus == "ninja" and self._muur_kant != 0:
            # Ninja-muursprong: spring omhoog EN duw jezelf van de muur af.
            self.snelheid_y = sprongkracht
            self.snelheid_x = -self._muur_kant * NINJA_MUURSPRONG
            self._muur_kant = 0
        elif (self.dubbel_sprong_timer > 0 and not self.heeft_dubbel_gesprongen):
            self.snelheid_y = sprongkracht
            self.heeft_dubbel_gesprongen = True

    def is_gevallen(self):
        """Geeft True terug als de speler te ver naar beneden is gevallen."""
        return self.y < -50

    def is_onkwetsbaar(self):
        """Geeft True terug als de speler nu onkwetsbaar is (ster-effect)."""
        return self.onkwetsbaar_timer > 0

    def teken(self):
        """Teken de speler — elke modus heeft zijn eigen poppetje!"""
        # Knipperen als de speler onkwetsbaar is
        if self.onkwetsbaar_timer > 0 and self._knippering < 3:
            return  # Niet tekenen = onzichtbaar in de knippercyclus

        # Elke speciale modus heeft zijn eigen vorm
        if self.modus == "vliegtuig":
            self._teken_vliegtuig()
            return
        if self.modus == "ufo":
            self._teken_ufo()
            return
        if self.modus == "bal":
            self._teken_bal()
            return
        if self.modus == "golf":
            self._teken_golf()
            return
        if self.modus == "robot":
            self._teken_robot()
            return
        if self.modus == "spin":
            self._teken_spin()
            return
        if self.modus == "heli":
            self._teken_heli()
            return
        if self.modus == "draaibol":
            self._teken_draaibol()
            return
        if self.modus == "ballon":
            self._teken_ballon()
            return
        if self.modus == "raket":
            self._teken_raket()
            return
        if self.modus == "kolibrie":
            self._teken_kolibrie()
            return
        if self.modus == "draak":
            self._teken_draak()
            return
        if self.modus == "ijs":
            self._teken_ijs()
            return
        if self.modus == "ninja":
            self._teken_ninja()
            return
        if self.modus == "spiegel":
            self._teken_spiegel()
            return
        if self.modus == "magneet":
            self._teken_magneet()
            return
        if self.modus == "flits":
            self._teken_flits()
            return
        if self.modus == "dobbelsteen":
            self._teken_dobbelsteen()
            return
        if self.modus == "vertraagd":
            self._teken_vertraagd()
            return
        if self.modus == "chaos":
            self._teken_chaos()
            return
        if self.modus == "dronken":
            self._teken_dronken()
            return
        if self.modus == "turbo":
            self._teken_turbo()
            return
        if self.modus == "ritme":
            self._teken_ritme()
            return
        if self.modus == "stuiteraar":
            self._teken_stuiteraar()
            return
        if self.modus == "klimmer":
            self._teken_klimmer()
            return
        if self.modus == "draaisturing":
            self._teken_draaisturing()
            return
        if self.modus == "boemerang":
            self._teken_boemerang()
            return
        if self.modus == "stamper":
            self._teken_stamper()
            return
        if self.modus == "zweefspringer":
            self._teken_zweefspringer()
            return
        if self.modus == "groeier":
            self._teken_groeier()
            return
        if self.modus == "zwaargewicht":
            self._teken_zwaargewicht()
            return
        if self.modus == "versneller":
            self._teken_versneller()
            return
        if self.modus == "wind":
            self._teken_wind()
            return
        if self.modus == "plakker":
            self._teken_plakker()
            return
        if self.modus == "metronoom":
            self._teken_metronoom()
            return
        if self.modus == "katapult":
            self._teken_katapult()
            return
        if self.modus == "krimpsprong":
            self._teken_krimpsprong()
            return
        if self.modus == "tegendraads":
            self._teken_tegendraads()
            return
        if self.modus == "turboflip":
            self._teken_turboflip()
            return
        if self.modus == "spiegelkatapult":
            self._teken_spiegelkatapult()
            return
        if self.modus == "schaduw":
            self._teken_schaduw()
            return
        if self.modus == "pingpong":
            self._teken_pingpong()
            return
        if self.modus == "spook":
            self._teken_spook()
            return
        if self.modus == "vleermuis":
            self._teken_vleermuis_dier()
            return
        if self.modus == "zombie":
            self._teken_zombie()
            return
        if self.modus == "pompoenkop":
            self._teken_pompoenkop()
            return
        if self.modus == "eigen":
            self._teken_eigen()
            return

        # Gewoon blokje: in de racemodus tolt het door de lucht → teken het gedraaid
        if self.rotatie != 0:
            self._teken_gedraaid()
            return

        x = self.x
        y = self.y
        w = self.breedte
        h = self.hoogte

        # Lijf (geel, of goudgeel bij snelheidsboost)
        lijf_kleur = (255, 220, 0) if self.snelheid_boost_timer > 0 else self.kleur
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, lijf_kleur)

        # Rand: oranje normaal, rood bij dubbel-sprong, lichtblauw bij onkwetsbaar
        if self.onkwetsbaar_timer > 0:
            rand_kleur = arcade.color.YELLOW
        elif self.dubbel_sprong_timer > 0:
            rand_kleur = arcade.color.CYAN
        else:
            rand_kleur = arcade.color.ORANGE
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, rand_kleur, 3)

        # Linker oog
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        # Rechter oog
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        # Lachend mondje
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

    def _teken_gedraaid(self):
        """Teken het blokje gedraaid (de tollende kubus van Geometry Dash)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        hoek = math.radians(self.rotatie)
        cos_h, sin_h = math.cos(hoek), math.sin(hoek)

        def draai(dx, dy):
            # Draai een punt (dx, dy) rond het midden van het blokje
            return (cx + dx * cos_h - dy * sin_h, cy + dx * sin_h + dy * cos_h)

        hw, hh = self.breedte / 2, self.hoogte / 2
        hoeken = [draai(-hw, -hh), draai(hw, -hh), draai(hw, hh), draai(-hw, hh)]

        # Lijf (geel, of goudgeel bij snelheidsboost)
        lijf_kleur = (255, 220, 0) if self.snelheid_boost_timer > 0 else self.kleur
        arcade.draw_polygon_filled(hoeken, lijf_kleur)
        arcade.draw_polygon_outline(hoeken, arcade.color.ORANGE, 3)

        # Oogjes draaien mee
        for ox in (-7, 7):
            ex, ey = draai(ox, 5)
            arcade.draw_circle_filled(ex, ey, 3, OOG_KLEUR)

    def _draai(self, dx, dy):
        """Hulpje: draai een punt (dx, dy) rond het midden van de speler.

        Gebruikt de huidige rotatie (voor het vliegtuig, de bal en de golf).
        """
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        hoek = math.radians(self.rotatie)
        c, s = math.cos(hoek), math.sin(hoek)
        return (cx + dx * c - dy * s, cy + dx * s + dy * c)

    def _teken_vliegtuig(self):
        """Teken een raket/vliegtuigje dat mee kantelt met de neus (paars)."""
        romp = [self._draai(*p) for p in [(-14, -8), (8, -8), (18, 0), (8, 8), (-14, 8)]]
        arcade.draw_polygon_filled(romp, self.kleur)
        arcade.draw_polygon_outline(romp, (150, 90, 220), 3)
        # Vinnen achteraan
        arcade.draw_polygon_filled([self._draai(*p) for p in [(-14, 6), (-22, 13), (-10, 2)]],
                                   (150, 90, 220))
        arcade.draw_polygon_filled([self._draai(*p) for p in [(-14, -6), (-22, -13), (-10, -2)]],
                                   (150, 90, 220))
        # Raampje
        rx, ry = self._draai(3, 1)
        arcade.draw_circle_filled(rx, ry, 4, (150, 220, 255))

    def _teken_ufo(self):
        """Teken een UFO: een schotel met een koepel en lichtjes (blauw)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # Schotel
        arcade.draw_ellipse_filled(cx, cy - 2, 34, 14, self.kleur)
        arcade.draw_ellipse_outline(cx, cy - 2, 34, 14, (40, 150, 210), 3)
        # Koepel bovenop
        arcade.draw_ellipse_filled(cx, cy + 4, 18, 14, (150, 210, 255))
        # Lichtjes eronder
        for dx in (-10, 0, 10):
            arcade.draw_circle_filled(cx + dx, cy - 8, 2.5, (255, 240, 120))

    def _teken_bal(self):
        """Teken een bal die rolt (oranje strepen die meedraaien)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        r = 15
        arcade.draw_circle_filled(cx, cy, r, self.kleur)
        arcade.draw_circle_outline(cx, cy, r, (230, 140, 40), 3)
        # Twee strepen die meedraaien -> je ziet hem rollen
        a, b = self._draai(-r + 2, 0), self._draai(r - 2, 0)
        arcade.draw_line(a[0], a[1], b[0], b[1], (230, 140, 40), 3)
        c, d = self._draai(0, -r + 2), self._draai(0, r - 2)
        arcade.draw_line(c[0], c[1], d[0], d[1], (230, 140, 40), 2)

    def _teken_golf(self):
        """Teken een pijltje/ruit dat schuin omhoog of omlaag wijst (roze)."""
        ruit = [self._draai(*p) for p in [(15, 0), (0, 10), (-12, 0), (0, -10)]]
        arcade.draw_polygon_filled(ruit, self.kleur)
        arcade.draw_polygon_outline(ruit, (220, 60, 120), 3)
        # Puntje aan de voorkant
        px, py = self._draai(15, 0)
        arcade.draw_circle_filled(px, py, 3, (255, 150, 190))

    def _teken_robot(self):
        """Teken een klein robotje: pootjes, een lijf en een kop met antenne (grijs)."""
        x = self.x
        y = self.y
        w = self.breedte
        cx = x + w / 2
        romp = (120, 190, 90)   # groen-grijs lijf
        metaal = (90, 100, 120)
        # Pootjes
        arcade.draw_lrbt_rectangle_filled(x + 4, x + 12, y, y + 8, metaal)
        arcade.draw_lrbt_rectangle_filled(x + w - 12, x + w - 4, y, y + 8, metaal)
        # Lijf
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 7, y + 24, self.kleur)
        arcade.draw_lrbt_rectangle_outline(x + 3, x + w - 3, y + 7, y + 24, metaal, 2)
        # Kop
        arcade.draw_lrbt_rectangle_filled(x + 6, x + w - 6, y + 24, y + 32, romp)
        arcade.draw_lrbt_rectangle_outline(x + 6, x + w - 6, y + 24, y + 32, metaal, 2)
        # Oogje en antenne
        arcade.draw_circle_filled(cx, y + 28, 3, OOG_KLEUR)
        arcade.draw_line(cx, y + 32, cx, y + 37, metaal, 2)
        arcade.draw_circle_filled(cx, y + 38, 2, (255, 80, 80))

    def _teken_heli(self):
        """Teken een helikoptertje met een draaiende rotor bovenop (lichtblauw)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        cy = y + h / 2
        romp_kleur = self.kleur
        donker = (40, 110, 160)
        # Romp (afgeronde bak)
        arcade.draw_ellipse_filled(cx, cy - 1, w - 4, h - 8, romp_kleur)
        arcade.draw_ellipse_outline(cx, cy - 1, w - 4, h - 8, donker, 3)
        # Raampje
        arcade.draw_circle_filled(cx + 5, cy, 4, (200, 240, 255))
        # Staart naar achteren
        arcade.draw_line(cx - w / 2 + 4, cy, x - 4, cy + 3, donker, 3)
        # Landingsglijders eronder
        arcade.draw_line(x + 4, y + 2, x + w - 4, y + 2, donker, 2)
        # Rotor bovenop (een lange balk die "draait")
        arcade.draw_line(x - 2, y + h - 2, x + w + 2, y + h - 2, donker, 3)
        arcade.draw_line(cx, y + h - 4, cx, y + h, donker, 2)
        # Pijltje dat laat zien of hij nu omhoog of omlaag gaat
        if self._heli_omhoog:
            arcade.draw_triangle_filled(cx - 4, cy - 2, cx + 4, cy - 2, cx, cy + 5, (255, 255, 255))
        else:
            arcade.draw_triangle_filled(cx - 4, cy + 3, cx + 4, cy + 3, cx, cy - 4, (255, 255, 255))

    def _teken_draaibol(self):
        """Teken een rollende bol met een pijltje dat wijst waar de zwaartekracht heen valt."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        r = 15
        # Lijf van de bol (groen-blauw, zodat hij verschilt van de gewone bal)
        arcade.draw_circle_filled(cx, cy, r, (80, 200, 180))
        arcade.draw_circle_outline(cx, cy, r, (30, 130, 120), 3)
        # Twee strepen die meedraaien -> je ziet hem rollen
        a, b = self._draai(-r + 2, 0), self._draai(r - 2, 0)
        arcade.draw_line(a[0], a[1], b[0], b[1], (30, 130, 120), 3)
        c, d = self._draai(0, -r + 2), self._draai(0, r - 2)
        arcade.draw_line(c[0], c[1], d[0], d[1], (30, 130, 120), 2)
        # Pijltje in de zwaartekracht-richting (zo zie je welke kant 'beneden' nu is)
        gx, gy = GRAV_VEC[self._grav_d]
        px, py = cx + gx * 10, cy + gy * 10
        arcade.draw_line(cx, cy, px, py, (255, 255, 255), 3)
        arcade.draw_circle_filled(px, py, 3, (255, 255, 255))

    def _teken_ballon(self):
        """Teken een ballon met een mandje eronder (in de spelerkleur)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # De ballon zelf (grote ovaal in de spelerkleur)
        arcade.draw_ellipse_filled(cx, cy + 8, self.breedte * 0.9, self.hoogte * 1.1, self.kleur)
        arcade.draw_ellipse_outline(cx, cy + 8, self.breedte * 0.9, self.hoogte * 1.1, (60, 60, 70), 2)
        # Glimlichtje
        arcade.draw_circle_filled(cx - 5, cy + 12, 3, (255, 255, 255))
        # Touwtje naar het mandje
        arcade.draw_line(cx, cy - 8, cx, cy - 16, (120, 90, 50), 2)
        # Mandje
        arcade.draw_lrbt_rectangle_filled(cx - 6, cx + 6, cy - 22, cy - 16, (150, 100, 50))

    def _teken_raket(self):
        """Teken een rechtopstaande raket met een vuurstraal eronder (in de spelerkleur)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        w = self.breedte
        h = self.hoogte
        donker = (150, 40, 40)
        # De romp (een langwerpige buis)
        arcade.draw_lrbt_rectangle_filled(cx - w * 0.22, cx + w * 0.22, cy - h * 0.35, cy + h * 0.25, self.kleur)
        arcade.draw_lrbt_rectangle_outline(cx - w * 0.22, cx + w * 0.22, cy - h * 0.35, cy + h * 0.25, donker, 2)
        # De neus (een puntige driehoek bovenop)
        arcade.draw_triangle_filled(cx - w * 0.22, cy + h * 0.25,
                                    cx + w * 0.22, cy + h * 0.25,
                                    cx, cy + h * 0.5, donker)
        # Twee vinnen onderaan
        arcade.draw_triangle_filled(cx - w * 0.22, cy - h * 0.35, cx - w * 0.22, cy - h * 0.1,
                                    cx - w * 0.42, cy - h * 0.35, donker)
        arcade.draw_triangle_filled(cx + w * 0.22, cy - h * 0.35, cx + w * 0.22, cy - h * 0.1,
                                    cx + w * 0.42, cy - h * 0.35, donker)
        # Raampje
        arcade.draw_circle_filled(cx, cy + h * 0.05, w * 0.12, (150, 220, 255))
        arcade.draw_circle_outline(cx, cy + h * 0.05, w * 0.12, donker, 2)
        # Vuurstraal eronder: groot als je gas geeft, klein als je loslaat
        vlam = h * 0.5 if self.vlieg_omhoog else h * 0.22
        arcade.draw_triangle_filled(cx - w * 0.15, cy - h * 0.35,
                                    cx + w * 0.15, cy - h * 0.35,
                                    cx, cy - h * 0.35 - vlam, (255, 160, 40))
        arcade.draw_triangle_filled(cx - w * 0.08, cy - h * 0.35,
                                    cx + w * 0.08, cy - h * 0.35,
                                    cx, cy - h * 0.35 - vlam * 0.6, (255, 240, 120))

    def _teken_kolibrie(self):
        """Teken een kolibrie: klein vogeltje met een lange snavel en trillende vleugels."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        donker = (30, 90, 80)
        # Lijfje (klein ovaal in de spelerkleur)
        arcade.draw_ellipse_filled(cx, cy, self.breedte * 0.5, self.hoogte * 0.6, self.kleur)
        arcade.draw_ellipse_outline(cx, cy, self.breedte * 0.5, self.hoogte * 0.6, donker, 2)
        # Lange dunne snavel naar voren
        snavel = 12 if self.kijkt_rechts else -12
        arcade.draw_line(cx, cy + 2, cx + snavel, cy + 2, donker, 2)
        # Vleugels die op en neer "trillen" (staan hoger als je omhoog gaat)
        wiek = 8 if self.snelheid_y > 0 else -3
        arcade.draw_line(cx, cy + 2, cx - 6, cy + wiek, donker, 3)
        arcade.draw_line(cx, cy + 2, cx + 6, cy + wiek, donker, 3)
        # Oogje
        arcade.draw_circle_filled(cx + (4 if self.kijkt_rechts else -4), cy + 4, 2, OOG_KLEUR)

    def _teken_draak(self):
        """Teken een draakje: lijf, kop met een vlammetje, een vleugel en een staart."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        r = 1 if self.kijkt_rechts else -1     # spiegelen als hij naar links kijkt
        donker = (40, 110, 60)
        # Lijf
        arcade.draw_ellipse_filled(cx, cy, self.breedte * 0.8, self.hoogte * 0.6, self.kleur)
        arcade.draw_ellipse_outline(cx, cy, self.breedte * 0.8, self.hoogte * 0.6, donker, 2)
        # Staart naar achteren
        arcade.draw_triangle_filled(cx - 12 * r, cy, cx - 20 * r, cy + 5, cx - 20 * r, cy - 5, donker)
        # Vleugel bovenop
        arcade.draw_triangle_filled(cx - 2 * r, cy + 4, cx - 10 * r, cy + 16, cx + 6 * r, cy + 8, (120, 200, 130))
        # Kop
        arcade.draw_circle_filled(cx + 12 * r, cy + 3, 7, self.kleur)
        arcade.draw_circle_outline(cx + 12 * r, cy + 3, 7, donker, 2)
        arcade.draw_circle_filled(cx + 14 * r, cy + 5, 2, OOG_KLEUR)
        # Klein vlammetje uit de bek
        arcade.draw_triangle_filled(cx + 18 * r, cy + 1, cx + 18 * r, cy + 5,
                                    cx + 26 * r, cy + 3, (255, 150, 40))

    def _teken_ijs(self):
        """Teken een ijsblokje: een lichtblauw doorschijnend blok met glinstering."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        # Lijf (ijsblauw)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (170, 225, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 160, 210), 3)
        # Glinstering: een paar witte streepjes en een sterretje
        arcade.draw_line(x + 5, y + h - 6, x + 12, y + h - 13, (255, 255, 255), 2)
        arcade.draw_line(x + w - 12, y + 8, x + w - 5, y + 15, (255, 255, 255), 2)
        arcade.draw_circle_filled(x + w - 9, y + h - 9, 2, (255, 255, 255))
        # Oogjes zodat het nog een poppetje blijft
        arcade.draw_circle_filled(x + 10, y + h // 2, 3, (60, 110, 160))
        arcade.draw_circle_filled(x + w - 10, y + h // 2, 3, (60, 110, 160))

    def _teken_ninja(self):
        """Teken een ninja: donker poppetje met een hoofdband en een ogenspleet."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        donker = (40, 45, 60)
        band = (200, 40, 40)
        # Lijf (donker pak, of de spelerkleur als die gekozen is)
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y, y + h, self.kleur if self.kleur != SPELER_KLEUR else donker)
        arcade.draw_lrbt_rectangle_outline(x + 3, x + w - 3, y, y + h, (20, 20, 30), 2)
        # Hoofdband (rood) met twee wapperende slierten
        by = y + h - 10
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, by, by + 6, band)
        kant = -1 if self.kijkt_rechts else 1
        arcade.draw_line(x + (3 if kant < 0 else w - 3), by + 3,
                         x + (3 if kant < 0 else w - 3) + kant * 8, by, band, 2)
        # Ogenspleet (twee witte oogjes)
        arcade.draw_circle_filled(cx - 5, by - 5, 2.5, (240, 240, 240))
        arcade.draw_circle_filled(cx + 5, by - 5, 2.5, (240, 240, 240))

    def _teken_spiegel(self):
        """Teken een spiegel-poppetje: een blok met een glimmend spiegel-vlak en pijltjes
        die de verkeerde kant op wijzen (want links/rechts zijn omgedraaid)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        # Lijf (zilverachtig spiegelblauw)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (190, 210, 230))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (120, 140, 170), 3)
        # Spiegel-glans (een schuine witte streep)
        arcade.draw_line(x + 6, y + 6, x + w - 8, y + h - 6, (255, 255, 255), 3)
        arcade.draw_line(x + 14, y + 6, x + w - 2, y + h - 12, (235, 245, 255), 2)
        # Twee pijltjes die naar buiten wijzen (de 'omgedraaide' besturing)
        cy = y + h / 2
        arcade.draw_triangle_filled(x + 5, cy, x + 11, cy - 4, x + 11, cy + 4, (90, 60, 140))
        arcade.draw_triangle_filled(x + w - 5, cy, x + w - 11, cy - 4, x + w - 11, cy + 4, (90, 60, 140))

    def _teken_magneet(self):
        """Teken een hoefijzer-magneet met twee rode/grijze polen."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        # De U-vorm van de magneet (rode buitenkant)
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w - 3, y + 4, y + h, (210, 50, 50))
        # Binnenkant weghappen zodat het een U wordt (achtergrondkleur-gat)
        arcade.draw_lrbt_rectangle_filled(x + 9, x + w - 9, y + 12, y + h + 2, (30, 30, 50))
        # De twee polen onderaan (grijze uiteinden)
        arcade.draw_lrbt_rectangle_filled(x + 3, x + 9, y, y + 12, (200, 200, 210))
        arcade.draw_lrbt_rectangle_filled(x + w - 9, x + w - 3, y, y + 12, (200, 200, 210))
        # Kleine + en - tekentjes op de polen
        arcade.draw_text("+", x + 2, y + 1, (40, 40, 60), 9, bold=True)
        arcade.draw_text("-", x + w - 9, y + 1, (40, 40, 60), 9, bold=True)
        # Oogjes bovenop
        arcade.draw_circle_filled(cx - 5, y + h - 6, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 5, y + h - 6, 2, OOG_KLEUR)

    def _teken_flits(self):
        """Teken een bliksemschicht-poppetje (geel, met een gloed die 'oplaadt')."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        # Gloed die feller wordt vlak voordat hij weer flitst.
        # min(...) zodat de kleur nooit boven 255 komt (ook als je lang stilstaat).
        gloed = min(160, 40 + int(60 * (self._flits_teller / max(1, FLITS_INTERVAL))))
        arcade.draw_circle_filled(cx, y + h / 2, w * 0.6, (gloed, gloed, 0))
        # De bliksemschicht (een zigzag) in de spelerkleur (of fel geel)
        kleur = self.kleur if self.kleur != SPELER_KLEUR else (255, 230, 40)
        punten = [(cx + 4, y + h - 2), (cx - 6, y + h * 0.55),
                  (cx + 1, y + h * 0.55), (cx - 6, y + 2),
                  (cx + 8, y + h * 0.5), (cx + 1, y + h * 0.5)]
        arcade.draw_polygon_filled(punten, kleur)
        arcade.draw_polygon_outline(punten, (200, 150, 0), 2)

    def _teken_dobbelsteen(self):
        """Teken een dobbelsteen: een wit blokje met zwarte stippen (5-ogen)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (245, 245, 250))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (60, 60, 80), 3)
        # Vijf stippen (zoals de 5 op een dobbelsteen)
        cx, cy = x + w / 2, y + h / 2
        for dx, dy in [(-8, 8), (8, 8), (0, 0), (-8, -8), (8, -8)]:
            arcade.draw_circle_filled(cx + dx, cy + dy, 3, (40, 40, 55))

    def _teken_vertraagd(self):
        """Teken een klokje (want je toetsen werken vertraagd)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx, cy = x + w / 2, y + h / 2
        r = w * 0.42
        arcade.draw_circle_filled(cx, cy, r, (235, 225, 180))
        arcade.draw_circle_outline(cx, cy, r, (120, 90, 40), 3)
        # De wijzers
        arcade.draw_line(cx, cy, cx, cy + r * 0.7, (90, 60, 30), 3)     # grote wijzer
        arcade.draw_line(cx, cy, cx + r * 0.5, cy, (90, 60, 30), 3)     # kleine wijzer
        arcade.draw_circle_filled(cx, cy, 2, (90, 60, 30))

    def _teken_chaos(self):
        """Teken een chaos-bal: een paarse bol met wilde vonkjes eromheen."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        arcade.draw_circle_filled(cx, cy, 12, (150, 60, 200))
        arcade.draw_circle_outline(cx, cy, 12, (90, 30, 130), 3)
        # Vonkjes die alle kanten op schieten (elk frame anders -> ziet er wild uit)
        for _ in range(5):
            hoek = random.uniform(0, 6.28)
            lengte = random.uniform(12, 20)
            ex, ey = cx + math.cos(hoek) * lengte, cy + math.sin(hoek) * lengte
            arcade.draw_line(cx, cy, ex, ey, (255, 230, 90), 2)
        # Twee draaierige oogjes
        arcade.draw_circle_filled(cx - 4, cy + 2, 2, (255, 255, 255))
        arcade.draw_circle_filled(cx + 4, cy + 2, 2, (255, 255, 255))

    def _teken_dronken(self):
        """Teken een duizelig poppetje met draai-oogjes en een golvend mondje (groen)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        arcade.draw_circle_filled(cx, cy, 13, (120, 200, 120))
        arcade.draw_circle_outline(cx, cy, 13, (60, 130, 60), 3)
        # Draai-oogjes (spiraaltjes = duizelig)
        for ox in (-5, 5):
            arcade.draw_circle_outline(cx + ox, cy + 3, 3, (40, 60, 40), 1)
            arcade.draw_circle_filled(cx + ox, cy + 3, 1, (40, 60, 40))
        # Golvend (wiebelig) mondje
        arcade.draw_line(cx - 6, cy - 5, cx - 2, cy - 3, (40, 60, 40), 2)
        arcade.draw_line(cx - 2, cy - 3, cx + 2, cy - 5, (40, 60, 40), 2)
        arcade.draw_line(cx + 2, cy - 5, cx + 6, cy - 3, (40, 60, 40), 2)

    def _teken_turbo(self):
        """Teken een raceblokje met snelheidsstrepen erachter (rood, superstoer)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        # Snelheidsstrepen achter je (aan de linkerkant, want je raast naar rechts)
        for i, dy in enumerate((h * 0.25, h * 0.5, h * 0.75)):
            arcade.draw_line(x - 14 - i * 3, y + dy, x, y + dy, (255, 200, 80), 2)
        # Het lijf (fel rood)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (230, 60, 50))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (120, 20, 20), 3)
        # Een pijl naar voren
        cy = y + h / 2
        arcade.draw_triangle_filled(x + w - 4, cy, x + w - 14, cy - 7, x + w - 14, cy + 7, (255, 240, 120))
        # Vastberaden oogjes
        arcade.draw_circle_filled(x + 9, y + h - 10, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 3, OOG_KLEUR)

    def _teken_ritme(self):
        """Teken een blokje met twee pijlen (omhoog + omlaag): de zwaartekracht flipt op de maat."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 130, 230))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 60, 140), 3)
        wit = (255, 255, 255)
        # Pijl omhoog en pijl omlaag (de zwaartekracht wisselt steeds)
        arcade.draw_triangle_filled(cx, y + h - 4, cx - 6, y + h - 12, cx + 6, y + h - 12, wit)
        arcade.draw_triangle_filled(cx, y + 4, cx - 6, y + 12, cx + 6, y + 12, wit)
        # Oogjes in het midden
        arcade.draw_circle_filled(cx - 5, y + h / 2, 2.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 5, y + h / 2, 2.5, OOG_KLEUR)

    def _teken_stuiteraar(self):
        """Teken een stuiterbal met een veer eronder (oranje)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # De bal
        arcade.draw_circle_filled(cx, cy + 3, 12, (255, 140, 40))
        arcade.draw_circle_outline(cx, cy + 3, 12, (180, 80, 10), 3)
        # Een veertje eronder (zigzag) -> hij stuitert altijd
        vx = self.x + self.breedte / 2
        vb = self.y + 2
        arcade.draw_line(vx - 6, vb, vx + 6, vb + 4, (200, 200, 210), 2)
        arcade.draw_line(vx + 6, vb + 4, vx - 6, vb + 8, (200, 200, 210), 2)
        # Blije oogjes
        arcade.draw_circle_filled(cx - 4, cy + 5, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy + 5, 2, OOG_KLEUR)

    def _teken_klimmer(self):
        """Teken een klimmertje met grijphandjes (kan alleen via muren omhoog)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        # Lijf (paars klimpak)
        arcade.draw_lrbt_rectangle_filled(x + 5, x + w - 5, y + 2, y + h - 4, (130, 90, 200))
        arcade.draw_lrbt_rectangle_outline(x + 5, x + w - 5, y + 2, y + h - 4, (70, 40, 120), 2)
        # Kopje
        arcade.draw_circle_filled(cx, y + h - 6, 6, (235, 200, 170))
        arcade.draw_circle_filled(cx - 2, y + h - 6, 1.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 2, y + h - 6, 1.5, OOG_KLEUR)
        # Twee grijphandjes die opzij reiken (naar de muren)
        arcade.draw_circle_filled(x + 3, y + h / 2, 3, (235, 200, 170))
        arcade.draw_circle_filled(x + w - 3, y + h / 2, 3, (235, 200, 170))

    def _teken_draaisturing(self):
        """Teken een blokje dat MEEDRAAIT met de stuur-richting (net zo snel als de wijzer)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        hoek = self._stuur_hoek                 # het blok draait met de stuur-richting mee
        cos_h, sin_h = math.cos(hoek), math.sin(hoek)

        def draai(dx, dy):
            # Draai een punt (dx, dy) rond het midden van het blokje
            return (cx + dx * cos_h - dy * sin_h, cy + dx * sin_h + dy * cos_h)

        hw, hh = self.breedte / 2, self.hoogte / 2
        hoeken = [draai(-hw, -hh), draai(hw, -hh), draai(hw, hh), draai(-hw, hh)]
        # Het gedraaide blokje (blauwgrijs)
        arcade.draw_polygon_filled(hoeken, (120, 150, 210))
        arcade.draw_polygon_outline(hoeken, (50, 70, 130), 3)
        # De stuur-pijl wijst de kant op waar 'rechts' nu heen duwt (draait mee)
        px, py = draai(hw, 0)
        arcade.draw_line(cx, cy, px, py, (255, 240, 90), 3)
        arcade.draw_circle_filled(px, py, 3, (255, 240, 90))
        # Oogjes draaien mee met het blok
        for ox in (-7, 7):
            ex, ey = draai(ox, 6)
            arcade.draw_circle_filled(ex, ey, 3, OOG_KLEUR)

    def _teken_boemerang(self):
        """Teken een boemerang (een V-vorm) met een elastiek-lijntje naar het ankerpunt."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # Elastiek naar het ankerpunt (als dat er is)
        if self._anker_x is not None:
            arcade.draw_line(self._anker_x + self.breedte / 2, cy, cx, cy, (200, 200, 210), 1)
        # De boemerang: twee dikke armen in een V
        kl = self.kleur
        arcade.draw_polygon_filled([(cx - 12, cy + 10), (cx - 4, cy + 8), (cx, cy - 2),
                                    (cx - 6, cy - 4), (cx - 12, cy + 2)], kl)
        arcade.draw_polygon_filled([(cx + 12, cy + 10), (cx + 4, cy + 8), (cx, cy - 2),
                                    (cx + 6, cy - 4), (cx + 12, cy + 2)], kl)
        arcade.draw_circle_filled(cx, cy - 1, 3, (120, 70, 30))
        arcade.draw_circle_filled(cx - 2, cy + 6, 1.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 2, cy + 6, 1.5, OOG_KLEUR)

    def _teken_stamper(self):
        """Teken een zwaar blok (donkere onderkant) met een dikke pijl naar beneden."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (110, 110, 130))
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + 8, (60, 60, 80))   # zware onderkant
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (40, 40, 55), 3)
        # Dikke pijl naar beneden (stampen!)
        arcade.draw_lrbt_rectangle_filled(cx - 3, cx + 3, y + h * 0.45, y + h - 6, (255, 230, 90))
        arcade.draw_triangle_filled(cx - 8, y + h * 0.45, cx + 8, y + h * 0.45,
                                    cx, y + h * 0.2, (255, 230, 90))
        # Oogjes bovenin
        arcade.draw_circle_filled(x + 9, y + h - 9, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 9, 3, OOG_KLEUR)

    def _teken_metronoom(self):
        """Teken een metronoom: een blokje met een tikkende wijzer. Op de 'tik' licht hij op."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        # Op (of vlak bij) de tik kleurt het blokje fel op — zo zie je wanneer je mag springen
        op_de_tel = (self._metro_teller <= METRO_VENSTER
                     or self._metro_teller >= METRO_INTERVAL - METRO_VENSTER)
        lijf = (255, 235, 120) if op_de_tel else (170, 130, 60)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, lijf)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 60, 20), 3)
        # De wijzer zwaait heen en weer met de maat (links op tik 0, rechts op de helft)
        deel = self._metro_teller / max(1, METRO_INTERVAL)     # 0.0 .. 1.0
        zwaai = math.sin(deel * 2 * math.pi) * 0.7             # heen en weer
        px = cx + math.sin(zwaai) * (w * 0.35)
        py = y + h - 4
        arcade.draw_line(cx, y + 6, px, py, (60, 40, 10), 3)
        arcade.draw_circle_filled(px, py, 3, (200, 40, 40))
        # Oogjes onderin
        arcade.draw_circle_filled(cx - 5, y + 9, 2.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 5, y + 9, 2.5, OOG_KLEUR)

    def _teken_katapult(self):
        """Teken een katapult-steentje met een boog-pijltje (het wordt weggeschoten)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        cy = y + h / 2
        # Rond steentje
        arcade.draw_circle_filled(cx, cy, 11, (140, 120, 100))
        arcade.draw_circle_outline(cx, cy, 11, (80, 60, 40), 3)
        # Een boogje omhoog-vooruit (laat de vaste boog zien)
        arcade.draw_arc_outline(cx, cy - 2, 26, 20, (255, 230, 120), 20, 160, 2)
        # Pijlpunt rechtsboven op de boog
        arcade.draw_triangle_filled(cx + 13, cy + 6, cx + 6, cy + 6, cx + 11, cy + 13, (255, 230, 120))
        # Vastberaden oogjes
        arcade.draw_circle_filled(cx - 4, cy + 2, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy + 2, 2, OOG_KLEUR)

    def _teken_krimpsprong(self):
        """Teken een blokje met steeds kleinere pijltjes omhoog (elke sprong lager)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 200, 160))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (30, 110, 90), 3)
        wit = (255, 255, 255)
        # Drie pijltjes omhoog die steeds kleiner worden
        for i, gr in enumerate((7, 5, 3)):
            ax = x + 8 + i * 9
            arcade.draw_triangle_filled(ax, y + h - 6, ax - gr / 2, y + h - 6 - gr,
                                        ax + gr / 2, y + h - 6 - gr, wit)
        # Oogjes onderin
        arcade.draw_circle_filled(cx - 5, y + 9, 2.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 5, y + 9, 2.5, OOG_KLEUR)

    def _teken_tegendraads(self):
        """Teken een blokje met twee tegengestelde pijlen (links/rechts wisselen om)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        cy = y + h / 2
        # Als links/rechts nu omgedraaid is, kleurt hij anders zodat je het ziet
        lijf = (230, 120, 200) if self._tegen_flip else (150, 120, 230)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, lijf)
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (70, 40, 120), 3)
        wit = (255, 255, 255)
        # Pijl naar links en pijl naar rechts (ze wisselen steeds van rol)
        arcade.draw_triangle_filled(x + 5, cy, x + 12, cy - 5, x + 12, cy + 5, wit)
        arcade.draw_triangle_filled(x + w - 5, cy, x + w - 12, cy - 5, x + w - 12, cy + 5, wit)
        # Oogjes bovenin
        arcade.draw_circle_filled(cx - 5, y + h - 9, 2.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 5, y + h - 9, 2.5, OOG_KLEUR)

    def schaduw_pos(self):
        """Waar staat de schaduw nu? (de plek waar jij ~SCHADUW_DELAY stapjes geleden was)
        Geeft (x, y) terug, of None als er nog geen schaduw is."""
        if self.modus != "schaduw" or len(self._schaduw_pad) < SCHADUW_DELAY:
            return None
        return self._schaduw_pad[0]

    def _teken_turboflip(self):
        """Teken een raceblokje (turbo) met twee flip-pijlen (de zwaartekracht flipt op de maat)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        # Snelheidsstrepen achter je
        for i, dy in enumerate((h * 0.3, h * 0.6)):
            arcade.draw_line(x - 12 - i * 3, y + dy, x, y + dy, (255, 200, 80), 2)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (210, 70, 130))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (110, 20, 60), 3)
        wit = (255, 255, 255)
        # Pijl omhoog + pijl omlaag (de zwaartekracht wisselt)
        arcade.draw_triangle_filled(cx, y + h - 4, cx - 5, y + h - 11, cx + 5, y + h - 11, wit)
        arcade.draw_triangle_filled(cx, y + 4, cx - 5, y + 11, cx + 5, y + 11, wit)
        # Vastberaden oogjes
        arcade.draw_circle_filled(cx - 6, y + h / 2, 2.5, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 6, y + h / 2, 2.5, OOG_KLEUR)

    def _teken_spiegelkatapult(self):
        """Teken een katapult-steentje met een spiegel-glans (het bijsturen is omgedraaid)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        cy = y + h / 2
        # Zilverachtig steentje (spiegel)
        arcade.draw_circle_filled(cx, cy, 11, (170, 180, 200))
        arcade.draw_circle_outline(cx, cy, 11, (90, 100, 120), 3)
        # Spiegel-glans (een schuine witte streep)
        arcade.draw_line(cx - 6, cy + 6, cx + 4, cy - 6, (240, 245, 255), 3)
        # Twee tegengestelde pijltjes (omgedraaid sturen)
        arcade.draw_triangle_filled(cx - 12, cy - 8, cx - 6, cy - 11, cx - 6, cy - 5, (60, 60, 80))
        arcade.draw_triangle_filled(cx + 12, cy - 8, cx + 6, cy - 11, cx + 6, cy - 5, (60, 60, 80))
        # Oogjes
        arcade.draw_circle_filled(cx - 4, cy + 2, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy + 2, 2, OOG_KLEUR)

    def _teken_schaduw(self):
        """Teken eerst de donkere schaduw (op je oude plek), dan het gewone poppetje."""
        pos = self.schaduw_pos()
        if pos is not None:
            sx, sy = pos
            w, h = self.breedte, self.hoogte
            arcade.draw_lrbt_rectangle_filled(sx, sx + w, sy, sy + h, (40, 40, 60))
            arcade.draw_lrbt_rectangle_outline(sx, sx + w, sy, sy + h, (110, 90, 150), 2)
            # Griezelige spookoogjes
            arcade.draw_circle_filled(sx + 9, sy + h - 10, 3, (210, 90, 210))
            arcade.draw_circle_filled(sx + w - 9, sy + h - 10, 3, (210, 90, 210))
        # Het gewone poppetje (paarsblauw zodat het bij de schaduw past)
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 150, 230))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (70, 70, 140), 3)
        arcade.draw_circle_filled(x + 9, y + h - 10, 4, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 4, OOG_KLEUR)
        arcade.draw_arc_outline(x + w // 2, y + 9, 10, 6, OOG_KLEUR, 200, 340, 2)

    def _teken_pingpong(self):
        """Teken een pingpong-balletje met dubbele pijl (kaatst tussen vloer en plafond)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        # Wit balletje
        arcade.draw_circle_filled(cx, cy, 11, (245, 245, 250))
        arcade.draw_circle_outline(cx, cy, 11, (120, 120, 140), 3)
        # Dubbele pijl (omhoog + omlaag): het kaatst op en neer
        rood = (220, 60, 60)
        arcade.draw_triangle_filled(cx, cy + 9, cx - 5, cy + 3, cx + 5, cy + 3, rood)
        arcade.draw_triangle_filled(cx, cy - 9, cx - 5, cy - 3, cx + 5, cy - 3, rood)
        # Oogjes
        arcade.draw_circle_filled(cx - 4, cy, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy, 2, OOG_KLEUR)

    def _teken_spook(self):
        """Teken een zwevend spookje dat steeds even (bijna) onzichtbaar wordt."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        onzichtbaar = self._spook_teller >= SPOOK_ONZICHT_NA
        a = 45 if onzichtbaar else 215            # bijna doorzichtig als hij 'verdwijnt'
        oog_a = 60 if onzichtbaar else 255
        wit = (235, 235, 255, a)
        # Ronde kop + lijf
        arcade.draw_circle_filled(cx, y + h * 0.6, w * 0.5, wit)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h * 0.22, y + h * 0.6, wit)
        # Golvende onderrand (drie bochtjes)
        for i in range(3):
            bx = x + w * (i + 0.5) / 3
            arcade.draw_circle_filled(bx, y + h * 0.22, w / 6, wit)
        # Donkere spookoogjes + mondje
        donker = (30, 30, 55, oog_a)
        arcade.draw_circle_filled(cx - 6, y + h * 0.62, 3, donker)
        arcade.draw_circle_filled(cx + 6, y + h * 0.62, 3, donker)
        arcade.draw_circle_filled(cx, y + h * 0.45, 3, donker)

    def _teken_vleermuis_dier(self):
        """Teken een fladderende vleermuis met klappende vleugels en rode oogjes."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx, cy = x + w / 2, y + h / 2
        flap = math.sin(self._vleer_fase * 2) * 5      # de vleugels klappen op en neer
        zwart = (45, 25, 65)
        # Vleugels links en rechts (klappen mee)
        arcade.draw_triangle_filled(cx - 4, cy, x - 7, cy + flap + 7, x - 7, cy + flap - 5, zwart)
        arcade.draw_triangle_filled(cx + 4, cy, x + w + 7, cy + flap + 7, x + w + 7, cy + flap - 5, zwart)
        # Lijfje
        arcade.draw_circle_filled(cx, cy, 8, zwart)
        # Twee spitse oortjes
        arcade.draw_triangle_filled(cx - 6, cy + 6, cx - 1, cy + 13, cx - 9, cy + 10, zwart)
        arcade.draw_triangle_filled(cx + 6, cy + 6, cx + 1, cy + 13, cx + 9, cy + 10, zwart)
        # Rode oogjes
        arcade.draw_circle_filled(cx - 3, cy + 2, 2, (255, 60, 60))
        arcade.draw_circle_filled(cx + 3, cy + 2, 2, (255, 60, 60))

    def _teken_zombie(self):
        """Teken een groen zombie-blokje met holle oogjes en een naad."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (110, 150, 80))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (60, 90, 40), 3)
        # Scheve, holle oogjes (eng)
        arcade.draw_circle_filled(x + 9, y + h - 11, 4, (25, 35, 18))
        arcade.draw_circle_filled(x + w - 9, y + h - 13, 4, (25, 35, 18))
        # Een naad met stiksel dwars over zijn gezicht
        ny = y + h * 0.5
        arcade.draw_line(x + 4, ny, x + w - 4, ny, (60, 90, 40), 2)
        for sx in range(int(x + 7), int(x + w - 4), 6):
            arcade.draw_line(sx, ny - 3, sx, ny + 3, (60, 90, 40), 1)
        # Scheve mond
        arcade.draw_line(cx - 6, y + 8, cx + 6, y + 6, (25, 35, 18), 2)

    def _teken_pompoenkop(self):
        """Teken een pompoenkop met een vurig spoor dat achter hem aan zweeft."""
        # Eerst het vurige spoor (oud = klein en donker, nieuw = groot en fel)
        n = len(self._pomp_spoor)
        for i, (px, py) in enumerate(self._pomp_spoor):
            deel = (i + 1) / max(1, n)
            r = 3 + deel * 7
            kl = (255, int(120 + 100 * deel), 20, int(50 + 130 * deel))
            arcade.draw_circle_filled(px, py, r, kl)
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx, cy = x + w / 2, y + h / 2
        # Oranje pompoen
        arcade.draw_circle_filled(cx, cy, w * 0.55, (240, 130, 20))
        arcade.draw_circle_outline(cx, cy, w * 0.55, (180, 80, 10), 2)
        # Ribbels
        arcade.draw_line(cx - 6, cy - 8, cx - 6, cy + 8, (200, 90, 10), 2)
        arcade.draw_line(cx + 6, cy - 8, cx + 6, cy + 8, (200, 90, 10), 2)
        # Steeltje bovenop
        arcade.draw_lrbt_rectangle_filled(cx - 2, cx + 2, cy + w * 0.5, cy + w * 0.5 + 5, (90, 150, 40))
        # Enge, gloeiende driehoek-oogjes en een getande mond
        geel = (255, 240, 120)
        arcade.draw_triangle_filled(cx - 9, cy + 4, cx - 2, cy + 4, cx - 5, cy - 3, geel)
        arcade.draw_triangle_filled(cx + 9, cy + 4, cx + 2, cy + 4, cx + 5, cy - 3, geel)
        arcade.draw_triangle_filled(cx - 8, cy - 6, cx + 8, cy - 6, cx, cy - 12, geel)

    def _teken_zweefspringer(self):
        """Teken een licht blokje met twee vleugeltjes (zweeft lang in de lucht)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        # Vleugeltjes aan de zijkanten
        arcade.draw_triangle_filled(x, y + h * 0.6, x, y + h - 2, x - 10, y + h * 0.8, (240, 240, 255))
        arcade.draw_triangle_filled(x + w, y + h * 0.6, x + w, y + h - 2, x + w + 10, y + h * 0.8, (240, 240, 255))
        # Lijf (lichtblauw = licht/luchtig)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (150, 210, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (80, 150, 210), 3)
        # Oogjes en een klein omhoog-pijltje
        arcade.draw_circle_filled(x + 9, y + h - 10, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 3, OOG_KLEUR)
        cx = x + w / 2
        arcade.draw_triangle_filled(cx, y + h * 0.55, cx - 5, y + h * 0.35, cx + 5, y + h * 0.35, (255, 255, 255))

    def _teken_groeier(self):
        """Teken een vriendelijk blokje met groei-pijltjes (het wordt vanzelf groter)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (120, 200, 120))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (50, 130, 50), 3)
        # Groei-pijltjes (naar buiten) in de hoeken
        wit = (245, 255, 245)
        arcade.draw_text("↗", x + w - 12, y + h - 14, wit, 10, bold=True)
        arcade.draw_text("↙", x + 2, y + 2, wit, 10, bold=True)
        # Blije oogjes en een lach
        arcade.draw_circle_filled(x + w * 0.35, y + h * 0.6, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w * 0.65, y + h * 0.6, 3, OOG_KLEUR)
        arcade.draw_arc_outline(x + w / 2, y + h * 0.4, w * 0.4, h * 0.3, OOG_KLEUR, 200, 340, 2)

    def _teken_zwaargewicht(self):
        """Teken een zwaar rotsblok (donker, stevig) met een gewicht-tekentje."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (90, 90, 100))
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h * 0.4, (60, 60, 70))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (30, 30, 40), 3)
        # Barstjes zodat het op zwaar gesteente lijkt
        arcade.draw_line(x + w * 0.3, y + h, x + w * 0.4, y + h * 0.5, (40, 40, 50), 1)
        arcade.draw_line(x + w * 0.7, y + h, x + w * 0.6, y + h * 0.5, (40, 40, 50), 1)
        # Gewicht-tekentje
        arcade.draw_text("kg", cx, y + h * 0.5, (230, 230, 240), 9, bold=True, anchor_x="center")
        arcade.draw_circle_filled(x + 9, y + h - 9, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 9, 3, OOG_KLEUR)

    def _teken_versneller(self):
        """Teken een raceblokje; meer snelheidsstrepen naarmate je harder gaat."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (60, 140, 210))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (30, 80, 140), 3)
        # Aantal streepjes hangt af van hoe snel je nu gaat
        n = 1 + int(self._versnel / (VERSNEL_MAX / 3 + 0.01))     # 1, 2 of 3 streepjes
        kant = -1 if self.kijkt_rechts else 1                     # strepen achter je
        for i in range(min(n, 3)):
            sx = x if self.kijkt_rechts else x + w
            arcade.draw_line(sx + kant * (4 + i * 5), y + h * 0.3,
                             sx + kant * (4 + i * 5), y + h * 0.7, (255, 230, 90), 2)
        arcade.draw_circle_filled(x + 9, y + h - 10, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 3, OOG_KLEUR)

    def _teken_wind(self):
        """Teken een blokje met wind-vlaagjes die de kant op waaien waar de wind heen blaast."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (170, 210, 230))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (90, 140, 170), 3)
        # Windvlaagjes (kleine boogjes) naar de kant waar de wind heen blaast
        r = self._wind_richting
        for dy in (h * 0.35, h * 0.6):
            bx = x + w / 2
            arcade.draw_line(bx - 10 * r, y + dy, bx + 10 * r, y + dy, (255, 255, 255), 2)
            arcade.draw_line(bx + 10 * r, y + dy, bx + 5 * r, y + dy + 4, (255, 255, 255), 2)
        arcade.draw_circle_filled(x + 9, y + h - 10, 3, OOG_KLEUR)
        arcade.draw_circle_filled(x + w - 9, y + h - 10, 3, OOG_KLEUR)

    def _teken_plakker(self):
        """Teken een gekko-achtig plakkertje met grijphandjes (plakt aan muren)."""
        x, y, w, h = self.x, self.y, self.breedte, self.hoogte
        cx = x + w / 2
        arcade.draw_lrbt_rectangle_filled(x + 2, x + w - 2, y + 2, y + h - 2, (110, 200, 130))
        arcade.draw_lrbt_rectangle_outline(x + 2, x + w - 2, y + 2, y + h - 2, (50, 130, 70), 2)
        # Grijp-voetjes aan de zijkanten (zuignapjes)
        for sy in (y + h * 0.3, y + h * 0.7):
            arcade.draw_circle_filled(x + 2, sy, 3, (70, 160, 90))
            arcade.draw_circle_filled(x + w - 2, sy, 3, (70, 160, 90))
        # Grote gekko-oogjes bovenop
        arcade.draw_circle_filled(cx - 6, y + h - 8, 4, (255, 255, 255))
        arcade.draw_circle_filled(cx + 6, y + h - 8, 4, (255, 255, 255))
        arcade.draw_circle_filled(cx - 6, y + h - 8, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 6, y + h - 8, 2, OOG_KLEUR)

    def _teken_eigen(self):
        """Teken het ZELFGEMAAKTE poppetje: vorm, kleur en ogen zoals in de maker gekozen."""
        w, h = self.breedte, self.hoogte
        cx, cy = self.x + w / 2, self.y + h / 2
        kleur = tuple(self._eigen("kleur") or (255, 120, 60))
        rand = tuple(max(0, c - 70) for c in kleur)
        vorm = self._eigen("vorm") or "blok"
        hw, hh = w / 2, h / 2
        hoek = math.radians(self.rotatie)      # voor het 'Draaien'-kunstje
        c_h, s_h = math.cos(hoek), math.sin(hoek)

        def draai(dx, dy):
            return (cx + dx * c_h - dy * s_h, cy + dx * s_h + dy * c_h)

        # Ronde vormen tekenen we los (draaien maakt daar toch niks uit)
        if vorm == "rond":
            arcade.draw_circle_filled(cx, cy, hw, kleur)
            arcade.draw_circle_outline(cx, cy, hw, rand, 3)
        elif vorm == "ei":
            arcade.draw_ellipse_filled(cx, cy, w * 0.8, h, kleur)
            arcade.draw_ellipse_outline(cx, cy, w * 0.8, h, rand, 3)
        elif vorm == "hart":
            arcade.draw_circle_filled(cx - hw * 0.45, cy + hh * 0.35, hw * 0.5, kleur)
            arcade.draw_circle_filled(cx + hw * 0.45, cy + hh * 0.35, hw * 0.5, kleur)
            arcade.draw_triangle_filled(cx - hw * 0.9, cy + hh * 0.4, cx + hw * 0.9, cy + hh * 0.4,
                                        cx, cy - hh, kleur)
        else:
            # Hoekige vormen als een lijst punten die we kunnen draaien
            if vorm == "driehoek":
                punten = [(-hw, -hh), (hw, -hh), (0, hh)]
            elif vorm == "diamant":
                punten = [(0, hh), (hw, 0), (0, -hh), (-hw, 0)]
            elif vorm == "zeshoek":
                punten = [(hw * math.cos(math.radians(a)), hh * math.sin(math.radians(a)))
                          for a in range(0, 360, 60)]
            elif vorm == "ster":
                punten = []
                for k in range(10):
                    r = hw if k % 2 == 0 else hw * 0.45
                    a = math.radians(-90 + k * 36)
                    punten.append((r * math.cos(a), r * math.sin(a)))
            else:  # blok
                punten = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            gedraaid = [draai(dx, dy) for dx, dy in punten]
            arcade.draw_polygon_filled(gedraaid, kleur)
            arcade.draw_polygon_outline(gedraaid, rand, 3)

        # Oogjes (als dat aanstaat) — draaien mee met het poppetje
        if self._eigen("ogen") is not False:
            lx, ly = draai(-6, hh * 0.35)
            rx, ry = draai(6, hh * 0.35)
            arcade.draw_circle_filled(lx, ly, 3, OOG_KLEUR)
            arcade.draw_circle_filled(rx, ry, 3, OOG_KLEUR)

    def _teken_spin(self):
        """Teken een spinnetje: een rond lijf met acht pootjes (donkerrood)."""
        cx = self.x + self.breedte / 2
        cy = self.y + self.hoogte / 2
        poot = (60, 30, 40)
        # Acht pootjes
        for dx in (-15, -11, 11, 15):
            arcade.draw_line(cx, cy, cx + dx, cy + 12, poot, 2)
            arcade.draw_line(cx, cy, cx + dx, cy - 12, poot, 2)
        # Lijf
        arcade.draw_circle_filled(cx, cy, 11, self.kleur)
        arcade.draw_circle_outline(cx, cy, 11, (150, 40, 40), 3)
        # Twee oogjes
        arcade.draw_circle_filled(cx - 4, cy + 3, 2, OOG_KLEUR)
        arcade.draw_circle_filled(cx + 4, cy + 3, 2, OOG_KLEUR)

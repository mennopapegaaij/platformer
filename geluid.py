# geluid.py
# Beheert alle geluiden en muziek in het spel.
# De GeluidManager laadt de bestanden en biedt functies om ze af te spelen.

import arcade
import os


class GeluidManager:
    """Laadt alle geluiden en speelt ze af op het juiste moment."""

    def __init__(self):
        self._geladen = False
        self._muziek_speler = None          # De huidige muziekspeler
        self._huidig_muziek_nummer = None   # Welk muzieknummer speelt er?

    def laad_alles(self):
        """Laad alle geluidsbestanden. Als een bestand ontbreekt, gaat het spel gewoon door."""
        map_naam = "geluiden"

        # Probeer elk geluidsbestand te laden
        try:
            self.sprong = arcade.load_sound(f"{map_naam}/sprong.wav")
            self.vijand_dood = arcade.load_sound(f"{map_naam}/vijand_dood.wav")
            self.powerup = arcade.load_sound(f"{map_naam}/powerup.wav")
            self.geraakt = arcade.load_sound(f"{map_naam}/geraakt.wav")
            self.level_gehaald = arcade.load_sound(f"{map_naam}/level_gehaald.wav")
            self.game_over = arcade.load_sound(f"{map_naam}/game_over.wav")
            self.muziek_vrolijk = arcade.load_sound(f"{map_naam}/muziek_vrolijk.wav")
            self.muziek_spannend = arcade.load_sound(f"{map_naam}/muziek_spannend.wav")
            self.muziek_episch = arcade.load_sound(f"{map_naam}/muziek_episch.wav")
            self._geladen = True
            print("Geluiden geladen!")
        except Exception as fout:
            print(f"Let op: geluiden konden niet worden geladen ({fout})")
            print("Tip: run 'python geluiden_maken.py' om de geluiden aan te maken.")
            self._geladen = False

    def _speel(self, geluid, volume=0.7):
        """Intern: speel een geluidseffect af (alleen als geluiden geladen zijn)."""
        if self._geladen:
            arcade.play_sound(geluid, volume=volume)

    # =============================================
    # Geluidseffecten
    # =============================================

    def speel_sprong(self):
        """Sprong-geluid: snel oplopend piepje."""
        self._speel(self.sprong, volume=0.5)

    def speel_vijand_dood(self):
        """Boing-geluid als je op een vijand springt."""
        self._speel(self.vijand_dood, volume=0.7)

    def speel_powerup(self):
        """Glinsterende toon als je een power-up pakt."""
        self._speel(self.powerup, volume=0.6)

    def speel_geraakt(self):
        """Bonk-geluid als je geraakt wordt."""
        self._speel(self.geraakt, volume=0.8)

    def speel_level_gehaald(self):
        """Vrolijke fanfare als je het level haalt."""
        self._speel(self.level_gehaald, volume=0.7)

    def speel_game_over(self):
        """Droevige tonen als je geen levens meer hebt."""
        self._speel(self.game_over, volume=0.7)

    # =============================================
    # Muziek
    # =============================================

    def speel_muziek(self, niveau):
        """
        Speel de passende muziek voor het gegeven level.
        - Levels 1-2: vrolijke muziek
        - Levels 3-4: spannende muziek
        - Level 5: epische muziek
        """
        if not self._geladen:
            return

        # Welk muzieknummer hoort bij dit level?
        if niveau <= 2:
            nieuw_nummer = "vrolijk"
            muziek = self.muziek_vrolijk
        elif niveau <= 4:
            nieuw_nummer = "spannend"
            muziek = self.muziek_spannend
        else:
            nieuw_nummer = "episch"
            muziek = self.muziek_episch

        # Wissel alleen als het een ander nummer is
        if nieuw_nummer != self._huidig_muziek_nummer:
            self.stop_muziek()
            self._muziek_speler = arcade.play_sound(muziek, volume=0.3, loop=True)
            self._huidig_muziek_nummer = nieuw_nummer

    def stop_muziek(self):
        """Stop de muziek die nu speelt."""
        if self._muziek_speler is not None:
            try:
                arcade.stop_sound(self._muziek_speler)
            except Exception:
                pass
            self._muziek_speler = None
            self._huidig_muziek_nummer = None


# Eén gedeelde GeluidManager voor het hele spel
geluid = GeluidManager()

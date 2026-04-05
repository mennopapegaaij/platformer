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

        try:
            self.sprong = arcade.load_sound(f"{map_naam}/sprong.wav")
            self.vijand_dood = arcade.load_sound(f"{map_naam}/vijand_dood.wav")
            self.powerup = arcade.load_sound(f"{map_naam}/powerup.wav")
            self.geraakt = arcade.load_sound(f"{map_naam}/geraakt.wav")
            self.level_gehaald = arcade.load_sound(f"{map_naam}/level_gehaald.wav")
            self.game_over = arcade.load_sound(f"{map_naam}/game_over.wav")
            # Elk level heeft zijn eigen muziek!
            self.muziek_levels = [
                arcade.load_sound(f"{map_naam}/muziek_level{i}.wav")
                for i in range(1, 6)
            ]
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
        self._speel(self.sprong, volume=1.0)

    def speel_vijand_dood(self):
        """Boing-geluid als je op een vijand springt."""
        self._speel(self.vijand_dood, volume=1.0)

    def speel_powerup(self):
        """Glinsterende toon als je een power-up pakt."""
        self._speel(self.powerup, volume=1.0)

    def speel_geraakt(self):
        """Bonk-geluid als je geraakt wordt."""
        self._speel(self.geraakt, volume=1.0)

    def speel_level_gehaald(self):
        """Vrolijke fanfare als je het level haalt."""
        self._speel(self.level_gehaald, volume=1.0)

    def speel_game_over(self):
        """Droevige tonen als je geen levens meer hebt."""
        self._speel(self.game_over, volume=1.0)

    # =============================================
    # Muziek
    # =============================================

    def speel_muziek(self, niveau):
        """
        Speel de muziek die bij dit level hoort.
        Elk level heeft zijn eigen uniek deuntje!
        """
        if not self._geladen:
            return

        # Bepaal het level-nummer (1 t/m 5, of begrens als het buiten bereik is)
        idx = max(0, min(niveau - 1, len(self.muziek_levels) - 1))
        nieuw_nummer = f"level{niveau}"

        # Wissel alleen als het een ander level-nummer is
        if nieuw_nummer != self._huidig_muziek_nummer:
            self.stop_muziek()
            self._muziek_speler = arcade.play_sound(self.muziek_levels[idx], volume=0.9, loop=True)
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

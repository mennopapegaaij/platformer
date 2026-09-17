# muziek.py
# Maakt zelf muziek-toontjes (do-re-mi) en speelt ze af.
# Zo kun je in de bouwmodus je EIGEN deuntje maken en in je level stoppen!
# Alle toontjes worden zelf gemaakt (sinus-golfjes) — geen bestaande liedjes.

import wave
import struct
import math
import os
import arcade

SAMPLE_RATE = 22050        # geluidskwaliteit (genoeg voor toontjes)
MAP = "muziek_tonen"       # hier worden de toon-bestanden bewaard

# De MAGISCHE noten (een pentatonische toonladder): do re mi so la, en dan hoger.
# Bij deze noten botst er nooit iets, dus ALLES wat je aanklikt klinkt mooi samen!
# (De 'lastige' noten fa en ti zijn eruit gelaten, want die kunnen vals klinken.)
NOOT_NAMEN = ["do", "re", "mi", "so", "la", "do₂", "re₂", "mi₂"]
NOOT_FREQ = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]

# Versie van de klank/noten. Verander je de tonen? Zet dit dan 1 hoger,
# dan worden de toon-bestanden opnieuw (mooi) aangemaakt.
TOON_VERSIE = 2

# Kant-en-klare liedjes die je kunt KIEZEN in de muziekmaker.
# Elk getal is een noot (0..7 = de rijen do..mi₂), en -1 is even stil.
# Allemaal zelf verzonnen met de magische noten, dus ze klinken sowieso mooi!
KLAAR_LIEDJES = [
    ("Vrolijk", [0, 2, 4, 4, 3, 4, 5, -1, 4, 3, 2, 3, 4, 2, 0, -1]),
    ("Rustig",  [0, -1, 2, -1, 4, -1, 3, -1, 2, -1, 4, -1, 5, -1, 4, -1]),
    ("Stoer",   [5, 4, 3, 4, 5, -1, 7, -1, 6, 5, 4, 3, 4, -1, 0, -1]),
    ("Trapje",  [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0, -1]),
    ("Springerig", [0, 4, 2, 5, 3, 7, 4, -1, 5, 2, 4, 0, 3, 5, 0, -1]),
    ("Dromerig", [4, 5, 7, 5, 4, -1, 2, 4, 3, 2, 0, -1, 2, 3, 4, -1]),
]

_tonen = None              # geladen geluidjes (of [] als geluid niet lukt)


# Elke piano-toon is opgebouwd uit boventonen (harmonischen).
# Per boventoon: (welke keer de frequentie, hoe sterk, hoe snel hij uitdooft).
# Hogere boventonen doven sneller uit -> dat klinkt warm en zacht, net als een piano.
PIANO_HARMONISCHEN = [
    (1, 1.00, 2.8),
    (2, 0.55, 4.0),
    (3, 0.35, 5.5),
    (4, 0.20, 7.5),
    (5, 0.12, 9.5),
    (6, 0.07, 12.0),
]


def _maak_toon_bestand(pad, freq, duur=0.85):
    """Maak één piano-achtige toon: een snelle aanslag en een lange uitdoofstaart."""
    n = int(SAMPLE_RATE * duur)
    ruw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        s = 0.0
        # tel alle boventonen bij elkaar op; elke dooft exponentieel uit
        for keer, sterkte, verval_snelheid in PIANO_HARMONISCHEN:
            s += (math.sin(2 * math.pi * freq * keer * t)
                  * sterkte * math.exp(-verval_snelheid * t))
        # supersnelle aanslag (zoals een pianohamer) van ~4 milliseconden
        aanval = min(1.0, t / 0.004)
        ruw.append(s * aanval)

    # Normaliseer: maak de toon lekker luid, maar zorg dat hij niet vervormt (kraakt)
    piek = max(1e-6, max(abs(x) for x in ruw))
    schaal = 0.9 / piek
    data = [max(-32767, min(32767, int(x * schaal * 32767))) for x in ruw]

    with wave.open(pad, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack("<%dh" % len(data), *data))


def _zorg_voor_tonen():
    """Maak de toon-bestanden aan als ze er nog niet zijn (maar één keer nodig)."""
    os.makedirs(MAP, exist_ok=True)
    for i, freq in enumerate(NOOT_FREQ):
        pad = "%s/piano_v%d_%d.wav" % (MAP, TOON_VERSIE, i)
        if not os.path.exists(pad):
            _maak_toon_bestand(pad, freq)


def laad_tonen():
    """Laad de toontjes (maak ze eerst als het moet). Geeft een lijst geluiden."""
    global _tonen
    if _tonen is not None:
        return _tonen
    try:
        _zorg_voor_tonen()
        _tonen = [arcade.load_sound("%s/piano_v%d_%d.wav" % (MAP, TOON_VERSIE, i))
                  for i in range(len(NOOT_FREQ))]
    except Exception:
        _tonen = []            # geluid lukt niet (bv. zonder scherm) -> gewoon stil
    return _tonen


def speel_noot(index):
    """Speel de noot met dit nummer (0 t/m 7)."""
    tonen = laad_tonen()
    if tonen and 0 <= index < len(tonen):
        try:
            arcade.play_sound(tonen[index], volume=0.6)
        except Exception:
            pass

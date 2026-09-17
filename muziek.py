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

# 8 noten: do re mi fa so la ti do (de C-majtoonladder), laag -> hoog
NOOT_NAMEN = ["do", "re", "mi", "fa", "so", "la", "ti", "do₂"]
NOOT_FREQ = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

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
        pad = "%s/piano%d.wav" % (MAP, i)
        if not os.path.exists(pad):
            _maak_toon_bestand(pad, freq)


def laad_tonen():
    """Laad de toontjes (maak ze eerst als het moet). Geeft een lijst geluiden."""
    global _tonen
    if _tonen is not None:
        return _tonen
    try:
        _zorg_voor_tonen()
        _tonen = [arcade.load_sound("%s/piano%d.wav" % (MAP, i))
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

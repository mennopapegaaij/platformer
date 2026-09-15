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


def _maak_toon_bestand(pad, freq, duur=0.26, volume=0.5):
    """Maak één toon-bestand (een sinus-golf met een zachte begin/eind-rand)."""
    n = int(SAMPLE_RATE * duur)
    data = []
    for i in range(n):
        t = i / SAMPLE_RATE
        s = (math.sin(2 * math.pi * freq * t) * 0.6 +
             math.sin(2 * math.pi * freq * 2 * t) * 0.25 +
             math.sin(2 * math.pi * freq * 3 * t) * 0.1)
        aanval = min(1.0, i / (SAMPLE_RATE * 0.01))            # zacht beginnen
        verval = max(0.0, 1.0 - (i - n * 0.3) / (n * 0.7))     # zacht uitdoven
        s *= aanval * verval * volume
        data.append(max(-32767, min(32767, int(s * 32767))))
    with wave.open(pad, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack("<%dh" % len(data), *data))


def _zorg_voor_tonen():
    """Maak de toon-bestanden aan als ze er nog niet zijn (maar één keer nodig)."""
    os.makedirs(MAP, exist_ok=True)
    for i, freq in enumerate(NOOT_FREQ):
        pad = "%s/noot%d.wav" % (MAP, i)
        if not os.path.exists(pad):
            _maak_toon_bestand(pad, freq)


def laad_tonen():
    """Laad de toontjes (maak ze eerst als het moet). Geeft een lijst geluiden."""
    global _tonen
    if _tonen is not None:
        return _tonen
    try:
        _zorg_voor_tonen()
        _tonen = [arcade.load_sound("%s/noot%d.wav" % (MAP, i))
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

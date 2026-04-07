# geluiden_maken.py
# Dit script maakt alle geluidsbestanden voor het spel.
# Je hoeft dit maar één keer te starten!
# Daarna staan de bestanden in de map 'geluiden/'.

import wave
import struct
import math
import os

# Maak de map 'geluiden' aan als die er nog niet is
os.makedirs("geluiden", exist_ok=True)

SAMPLE_RATE = 44100  # Kwaliteit van het geluid (standaard CD-kwaliteit)


# =============================================
# Hulpfuncties om geluid te maken
# =============================================

def schrijf_wav(bestandsnaam, samples):
    """Sla een lijst van samples op als WAV-bestand."""
    # Zet alle samples om naar 16-bit gehele getallen
    data = [max(-32767, min(32767, int(s * 32767))) for s in samples]
    with wave.open(f"geluiden/{bestandsnaam}", "w") as f:
        f.setnchannels(1)       # Mono geluid
        f.setsampwidth(2)       # 16-bit
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack(f"<{len(data)}h", *data))


def toon(freq, duur, volume=0.5, vervaag=True):
    """Maak één toon (sinus-golf) met een opgaande en neergaande rand."""
    n = int(SAMPLE_RATE * duur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Rijker geluid: mix meerdere harmonischen
        s = (math.sin(2 * math.pi * freq * t) * 0.6 +
             math.sin(2 * math.pi * freq * 2 * t) * 0.25 +
             math.sin(2 * math.pi * freq * 3 * t) * 0.1)
        if vervaag:
            # Begin zacht, wordt iets luider, en vervaagt dan
            aanval = min(1.0, i / (SAMPLE_RATE * 0.01))
            verval = max(0.0, 1.0 - (i - n * 0.2) / (n * 0.8))
            s *= aanval * verval
        samples.append(s * volume)
    return samples


def arpeggio(noten, duur_per_noot, volume=0.5):
    """Speel een reeks noten achter elkaar."""
    samples = []
    for freq in noten:
        samples.extend(toon(freq, duur_per_noot, volume))
    return samples


def rust(duur):
    """Stilte voor een bepaalde tijd."""
    return [0.0] * int(SAMPLE_RATE * duur)


def melodie_geluidseffect(noten_lijst, bpm=140, volume=0.35):
    """Maak een melodie voor geluidseffecten (gebruikt door level_gehaald en game_over)."""
    samples = []
    sec_per_beat = 60 / bpm
    for freq, beats in noten_lijst:
        duur = beats * sec_per_beat
        if freq == 0:
            samples.extend(rust(duur))
        else:
            n = int(SAMPLE_RATE * duur)
            for i in range(n):
                t = i / SAMPLE_RATE
                s = (math.sin(2 * math.pi * freq * t) * 0.55 +
                     math.sin(2 * math.pi * freq * 2 * t) * 0.25 +
                     math.sin(2 * math.pi * freq * 0.5 * t) * 0.1)
                aanval = min(1.0, i / max(1, SAMPLE_RATE * 0.02))
                release = max(0.0, 1.0 - (i / max(1, n * 0.85 - 1)) * 0.5)
                samples.append(s * aanval * release * volume)
    return samples


# =============================================
# Noot-frequenties (in Hz)
# =============================================
C3, D3, E3, F3, G3, A3, B3 = 131, 147, 165, 175, 196, 220, 247
C4, D4, E4, F4, G4, A4, B4 = 262, 294, 330, 349, 392, 440, 494
C5, D5, E5, F5, G5, A5, B5 = 523, 587, 659, 698, 784, 880, 988


# =============================================
# GELUIDSEFFECTEN
# =============================================

print("Geluidseffecten maken...")

# Sprong: snel oplopend piepje
schrijf_wav("sprong.wav",
    toon(330, 0.04, 0.8) +
    toon(440, 0.04, 0.8) +
    toon(550, 0.06, 0.75))

# Vijand dood: vrolijk "boing"
schrijf_wav("vijand_dood.wav",
    toon(300, 0.05, 0.9) +
    toon(400, 0.05, 0.9) +
    toon(500, 0.08, 0.85) +
    toon(600, 0.08, 0.8))

# Power-up: glinsterende arpeggio omhoog
schrijf_wav("powerup.wav",
    arpeggio([E4, G4, B4, E5, G5], 0.06, 0.85))

# Geraakt: laag bonk + daling
schrijf_wav("geraakt.wav",
    toon(150, 0.05, 0.95) +
    toon(110, 0.08, 0.9) +
    toon(80, 0.12, 0.85))

# Level gehaald: kleine fanfare omhoog
schrijf_wav("level_gehaald.wav",
    toon(C4, 0.1, 0.85) +
    toon(E4, 0.1, 0.85) +
    toon(G4, 0.1, 0.85) +
    toon(C5, 0.25, 0.9) +
    rust(0.05) +
    toon(C5, 0.3, 0.9))

# Game over: droevige dalende tonen
schrijf_wav("game_over.wav",
    toon(G4, 0.18, 0.85) +
    toon(E4, 0.18, 0.85) +
    toon(C4, 0.18, 0.85) +
    toon(A3, 0.3, 0.85) +
    toon(G3, 0.4, 0.8))

print("  Geluidseffecten klaar!")


# =============================================
# Extra hulpfuncties voor muziek
# =============================================

def melodie(noten_lijst, bpm=140, volume=0.35):
    """
    Maak een melodie van noten.
    noten_lijst = lijst van (frequentie, aantal_beats) tuples.
    Gebruik 0 als frequentie voor stilte.
    """
    samples = []
    sec_per_beat = 60 / bpm
    for freq, beats in noten_lijst:
        duur = beats * sec_per_beat
        n = int(SAMPLE_RATE * duur)
        if freq == 0:
            samples.extend([0.0] * n)
        else:
            # Gebruik 88% van de tijd voor de noot, 12% stilte (mooier dan alles aan elkaar)
            noot_n = int(n * 0.88)
            for i in range(noot_n):
                t = i / SAMPLE_RATE
                s = (math.sin(2 * math.pi * freq * t) * 0.55 +
                     math.sin(2 * math.pi * freq * 2 * t) * 0.25 +
                     math.sin(2 * math.pi * freq * 0.5 * t) * 0.1)
                aanval = min(1.0, i / max(1, SAMPLE_RATE * 0.02))
                release = max(0.0, 1.0 - (i / max(1, noot_n * 0.85 - 1)) * 0.4)
                samples.append(s * aanval * release * volume)
            samples.extend([0.0] * (n - noot_n))
    return samples


def baslijn(noten_lijst, bpm=140, volume=0.22):
    """
    Maak een zware bas-lijn.
    Klinkt voller dan de melodie (meer sub-octaaf erin).
    """
    samples = []
    sec_per_beat = 60 / bpm
    for freq, beats in noten_lijst:
        duur = beats * sec_per_beat
        n = int(SAMPLE_RATE * duur)
        if freq == 0:
            samples.extend([0.0] * n)
        else:
            noot_n = int(n * 0.75)   # Bas heeft kortere noten (meer staccato)
            for i in range(noot_n):
                t = i / SAMPLE_RATE
                # Dikke bas: veel sub-octaaf (halve frequentie)
                s = (math.sin(2 * math.pi * freq * t) * 0.6 +
                     math.sin(2 * math.pi * freq * 0.5 * t) * 0.4)
                aanval = min(1.0, i / max(1, SAMPLE_RATE * 0.01))
                verval = max(0.0, 1.0 - i / max(1, noot_n - 1))
                samples.append(s * aanval * verval * volume)
            samples.extend([0.0] * (n - noot_n))
    return samples


def kick(volume=0.5):
    """Bas-drum: korte dreunende toon met snel verval."""
    duur = 0.18
    n = int(SAMPLE_RATE * duur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 90 * math.exp(-25 * t)   # Dalende toonhoogte (echte kick!)
        s = math.sin(2 * math.pi * freq * t)
        envelope = math.exp(-18 * t)
        samples.append(s * envelope * volume)
    return samples


def snare(volume=0.28):
    """Snare-drum: ruis met snel verval."""
    import random
    duur = 0.12
    n = int(SAMPLE_RATE * duur)
    samples = []
    rng = random.Random(42)  # Vaste seed zodat het altijd hetzelfde klinkt
    for i in range(n):
        t = i / SAMPLE_RATE
        s = rng.uniform(-1, 1)  # Witte ruis
        envelope = math.exp(-28 * t)
        samples.append(s * envelope * volume)
    return samples


def beat_patroon(beats, bpm):
    """
    Maak een drumbeat: kick op slag 1 en 3, snare op slag 2 en 4.
    Geschikt om als achtergrond mee te mixen.
    """
    sec_per_beat = 60 / bpm
    samples = []
    for i in range(beats):
        slag = i % 4
        if slag == 0 or slag == 2:
            s = kick(volume=0.45)
        else:
            s = snare(volume=0.25)
        # Vul aan tot precies één slag
        n_slag = int(SAMPLE_RATE * sec_per_beat)
        s = s + [0.0] * max(0, n_slag - len(s))
        samples.extend(s[:n_slag])
    return samples


def meng(s1, s2):
    """Mix twee geluidsreeksen samen (het langste bepaalt de lengte)."""
    lengte = max(len(s1), len(s2))
    s1 = s1 + [0.0] * (lengte - len(s1))
    s2 = s2 + [0.0] * (lengte - len(s2))
    # Verlaag iets zodat de mix niet te luid wordt
    return [(a + b) * 0.65 for a, b in zip(s1, s2)]


# =============================================
# MUZIEK per level — elk level heeft zijn eigen deuntje!
# =============================================

print("Muziek componeren...")

# ──────────────────────────────────────────────
# LEVEL 1: De Groene Vlakte
# Vrolijk en huppelend! C-groot, 150 BPM.
# ──────────────────────────────────────────────
muz1_m = melodie([
    # Thema A: Opgewekt omhoog
    (C5, .5), (B4, .25), (A4, .25), (G4, 1),
    (E4, .5), (G4, .5), (C5, 1),
    (D5, .5), (C5, .25), (B4, .25), (A4, .5), (G4, .5),
    (G4, 1), (0, 1),
    # Thema B: Speelse respons
    (E5, .5), (D5, .5), (C5, 1),
    (B4, .5), (A4, .5), (G4, 1),
    (A4, .5), (G4, .25), (F4, .25), (E4, .5), (D4, .5),
    (C4, 2),
    # Thema C: Klim-loopje omhoog
    (G4, .25), (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .25), (F5, .25), (G5, .25),
    (G5, .5), (E5, .5), (C5, .5), (G4, .5),
    (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .5), (D5, .5),
    (C5, 1), (0, 1),
    # Thema D: Feestelijk slot
    (E5, .5), (G5, .5), (E5, .5), (C5, .5),
    (D5, .5), (F5, .5), (D5, .5), (B4, .5),
    (C5, .5), (E5, .5), (G5, .5), (E5, .5),
    (C5, 2),
], bpm=150, volume=0.75)

muz1_b = baslijn([
    (C3, 2), (G3, 2), (F3, 2), (G3, 2),
    (C3, 2), (G3, 2), (A3, 2), (C3, 2),
    (C3, 2), (G3, 2), (C3, 2), (G3, 2),
    (C3, 2), (G3, 2), (F3, 2), (C3, 2),
], bpm=150, volume=0.55)

schrijf_wav("muziek_level1.wav", meng(muz1_m, muz1_b) * 2)
print("  muziek_level1.wav klaar! (De Groene Vlakte - vrolijk)")


# ──────────────────────────────────────────────
# LEVEL 2: Het Bos
# Mysterieus maar vriendelijk. A-klein, 118 BPM.
# Rustig en vloeiend, zoals wandelen door de bomen.
# ──────────────────────────────────────────────
muz2_m = melodie([
    # Mysterieuze opening
    (A4, 1), (0, .5), (E4, .5),
    (A4, .5), (C5, .5), (B4, 1),
    (G4, .5), (A4, .25), (B4, .25), (A4, 1),
    (E4, 1.5), (0, .5),
    # Vloeiend door de bomen
    (A4, .5), (B4, .5), (C5, .5), (B4, .5),
    (A4, .5), (G4, .5), (E4, 1),
    (F4, .5), (G4, .5), (A4, .5), (B4, .5),
    (C5, 2),
    # Iets donkerder deel
    (E5, .5), (D5, .5), (C5, 1),
    (B4, .5), (A4, .5), (G4, 1),
    (A4, .5), (C5, .5), (E5, .5), (D5, .5),
    (C5, 1), (0, 1),
    # Terugkeer naar A
    (G4, .5), (A4, .5), (B4, .5), (C5, .5),
    (B4, .5), (A4, .5), (G4, .5), (E4, .5),
    (F4, .5), (G4, .5), (A4, .5), (G4, .5),
    (A4, 2),
], bpm=118, volume=0.75)

muz2_b = baslijn([
    (A3, 2), (E3, 2), (A3, 2), (E3, 2),
    (A3, 2), (E3, 2), (F3, 2), (C3, 2),
    (A3, 2), (E3, 2), (A3, 2), (G3, 2),
    (A3, 2), (E3, 2), (F3, 2), (A3, 2),
], bpm=118, volume=0.50)

schrijf_wav("muziek_level2.wav", meng(muz2_m, muz2_b) * 2)
print("  muziek_level2.wav klaar! (Het Bos - mysterieus)")


# ──────────────────────────────────────────────
# LEVEL 3: De Bergen
# Energiek en heroïsch! C-groot, 162 BPM.
# Klimmende runs en grote sprongen — voelt als avontuur!
# ──────────────────────────────────────────────
muz3_m = melodie([
    # Stijgende runs — klimmen naar de top!
    (G4, .25), (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .25), (F5, .25), (G5, .25),
    (G5, .5), (E5, .5), (C5, .5), (G4, .5),
    (A4, .25), (C5, .25), (E5, .25), (G5, .25), (F5, .5), (E5, .5),
    (D5, 1.5), (0, .5),
    # Krachtige bergmelodie
    (C5, .5), (E5, .5), (G5, 1),
    (B4, .5), (D5, .5), (G4, 1),
    (A4, .5), (C5, .5), (E5, 1),
    (F5, .5), (E5, .5), (D5, 1),
    # Afdaling en nieuwe opbouw
    (C5, .25), (B4, .25), (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .25), (C4, .25),
    (E4, .5), (G4, .5), (C5, .5), (E5, .5),
    (G5, .5), (F5, .5), (E5, .25), (D5, .25), (C5, .5),
    (0, 1), (G4, 1),
    # Heroïsch slot
    (C5, .5), (D5, .5), (E5, .5), (F5, .5),
    (G5, 1.5), (E5, .5),
    (F5, .5), (E5, .5), (D5, .5), (C5, .5),
    (G4, 2),
], bpm=162, volume=0.75)

muz3_b = baslijn([
    (C3, 2), (C3, 2), (F3, 2), (G3, 2),
    (C3, 2), (G3, 2), (A3, 2), (D3, 2),
    (C3, 2), (C3, 2), (G3, 2), (G3, 2),
    (C3, 2), (C3, 2), (F3, 2), (C3, 2),
], bpm=162, volume=0.55)

schrijf_wav("muziek_level3.wav", meng(muz3_m, muz3_b) * 2)
print("  muziek_level3.wav klaar! (De Bergen - heroïsch)")


# ──────────────────────────────────────────────
# LEVEL 4: De Nacht
# Langzaam en spookachtig. A-klein, 88 BPM.
# Veel stiltes voor sfeer — klinkt als een donker kasteel.
# ──────────────────────────────────────────────
muz4_m = melodie([
    # Duistere opening — veel pauzes voor sfeer
    (A4, 1.5), (0, .5),
    (E4, 1), (G4, 1),
    (A4, 1), (C5, 1),
    (B4, 1.5), (0, .5),
    # Spookachtige melodie
    (G4, .5), (A4, .5), (B4, 1),
    (C5, .5), (B4, .5), (A4, 1),
    (G4, .5), (E4, .5), (G4, .5), (A4, .5),
    (E4, 2),
    # Spanning opbouwen
    (A4, .5), (C5, .5), (E5, 1),
    (D5, .5), (C5, .5), (B4, 1),
    (A4, .5), (B4, .5), (C5, .5), (B4, .5),
    (A4, 2),
    # Nachtelijk slot
    (E5, 1), (0, .5), (D5, .5),
    (C5, 1), (B4, 1),
    (A4, .5), (G4, .5), (F4, .5), (E4, .5),
    (A3, 2),
], bpm=88, volume=0.75)

muz4_b = baslijn([
    (A3, 2), (E3, 2), (A3, 2), (G3, 2),
    (E3, 2), (A3, 2), (E3, 2), (A3, 2),
    (A3, 2), (G3, 2), (A3, 2), (A3, 2),
    (A3, 2), (E3, 2), (A3, 2), (A3, 2),
], bpm=88, volume=0.50)

schrijf_wav("muziek_level4.wav", meng(muz4_m, muz4_b) * 2)
print("  muziek_level4.wav klaar! (De Nacht - spookachtig)")


# ──────────────────────────────────────────────
# LEVEL 5: De Eindstrijd
# Razend snel en episch! D-klein, 185 BPM.
# Met echte drums (kick + snare) — dit is de grote finale!
# ──────────────────────────────────────────────
muz5_m = melodie([
    # Stormachtig begin — razende 16e noten!
    (D4, .25), (F4, .25), (A4, .25), (D5, .25), (A4, .25), (F4, .25), (D4, .25), (A3, .25),
    (E4, .25), (G4, .25), (B4, .25), (E5, .25), (B4, .25), (G4, .25), (E4, .25), (B3, .25),
    # Krachtige melodie
    (F4, .5), (A4, .5), (C5, .5), (F5, .5),
    (E5, .5), (D5, .5), (C5, .5), (A4, .5),
    # Dalende reeks
    (D5, .25), (C5, .25), (B4, .25), (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .25),
    (A4, .5), (C5, .5), (E5, .5), (A5, .5),
    # Hoogtepunt
    (G5, .5), (F5, .5), (E5, .25), (D5, .25), (C5, .5),
    (D5, .5), (E5, .5), (F5, .5), (E5, .5),
    # Opnieuw omhoog
    (D5, .25), (C5, .25), (B4, .25), (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .25),
    (E4, .5), (G4, .5), (B4, .5), (E5, .5),
    # Epische opbouw
    (D5, .5), (E5, .5), (F5, .5), (G5, .5),
    (A5, 1), (0, 1),
    # Razend slot
    (D5, .25), (F5, .25), (A5, .25), (F5, .25), (D5, .25), (C5, .25), (B4, .25), (A4, .25),
    (G4, .25), (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .25), (F5, .25), (G5, .25),
    # Finale
    (A5, .5), (G5, .5), (F5, .5), (E5, .5),
    (D5, 2),
], bpm=185, volume=0.70)

muz5_b = baslijn([
    (D3, 2), (D3, 2), (E3, 2), (G3, 2),
    (F3, 2), (D3, 2), (A3, 2), (A3, 2),
    (D3, 2), (A3, 2), (F3, 2), (G3, 2),
    (D3, 2), (E3, 2), (F3, 2), (D3, 2),
], bpm=185, volume=0.50)

# Drums voor level 5 (kick op 1&3, snare op 2&4)!
muz5_drums = beat_patroon(32, bpm=185)

# Mix alles: melodie + bas + drums
muz5 = meng(meng(muz5_m, muz5_b), muz5_drums)
schrijf_wav("muziek_level5.wav", muz5 * 2)
print("  muziek_level5.wav klaar! (De Eindstrijd - episch met drums)")

# ──────────────────────────────────────────────
# LEVEL 6: De Snelheids Tempel
# Woestijn/tempel — exotisch en snel! E-Phrygisch, 175 BPM.
# Phrygisch klinkt Arabisch-achtig (b2 toon = F na E geeft die sfeer).
# ──────────────────────────────────────────────

# Extra noten die we nodig hebben
Fis4 = 370   # F# (verhoogde Fa)
Fis5 = 740
Es4  = 311   # Eb (verlaagde Mi)
As4  = 415   # Ab (verlaagde La)

muz6_m = melodie([
    # Exotische opening — typisch Arabisch loopje
    (E4, .25), (F4, .25), (E4, .25), (D4, .25), (E4, 1),
    (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .5), (E4, .5),
    (B4, .5), (A4, .25), (G4, .25), (F4, .25), (E4, .75),
    (E4, 1.5), (0, .5),
    # Snelle tempel-run
    (E4, .25), (F4, .25), (G4, .25), (A4, .25), (B4, .25), (C5, .25), (B4, .25), (A4, .25),
    (G4, .5), (A4, .5), (B4, 1),
    (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .5), (E4, .5),
    (E5, 1), (0, 1),
    # Mysterieuze middenpartij
    (C5, .5), (B4, .5), (A4, 1),
    (G4, .5), (F4, .5), (E4, 1),
    (F4, .5), (G4, .5), (A4, .5), (B4, .5),
    (C5, 2),
    # Razende finale — snel omhoog en omlaag
    (E4, .25), (F4, .25), (G4, .25), (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .25),
    (E5, .5), (D5, .5), (C5, .5), (B4, .5),
    (A4, .25), (G4, .25), (F4, .25), (E4, .25), (D4, .5), (E4, .5),
    (E4, 2),
], bpm=175, volume=0.75)

muz6_b = baslijn([
    (E3, 2), (A3, 2), (E3, 2), (G3, 2),
    (E3, 2), (A3, 2), (D3, 2), (E3, 2),
    (E3, 2), (F3, 2), (E3, 2), (A3, 2),
    (E3, 2), (A3, 2), (E3, 2), (E3, 2),
], bpm=175, volume=0.55)

muz6_drums = beat_patroon(32, bpm=175)
muz6 = meng(meng(muz6_m, muz6_b), muz6_drums)
schrijf_wav("muziek_level6.wav", muz6 * 2)
print("  muziek_level6.wav klaar! (De Snelheids Tempel - exotisch met drums)")


# ──────────────────────────────────────────────
# LEVEL 7: De Wolken
# Licht en zweefachtig! D-groot, 125 BPM.
# Hoge noten, vloeiende melodie — je zweeft door de lucht.
# ──────────────────────────────────────────────

# Extra noten
Fis4 = 370   # F# in D-groot
Fis5 = 740
Cis5 = 554   # C# in D-groot

muz7_m = melodie([
    # Zweefende opening — lange noten, alsof je drijft op de wolken
    (D5, 1), (Fis5, 1),
    (A5, 1.5), (0, .5),
    (G5, .5), (Fis5, .5), (E5, 1),
    (D5, 2),
    # Luchtige melodie omhoog en omlaag
    (Fis4, .5), (A4, .5), (D5, .5), (Fis5, .5),
    (E5, .5), (D5, .5), (Cis5, 1),
    (B4, .5), (A4, .5), (G4, .5), (Fis4, .5),
    (D4, 2),
    # Iets levendiger middenstuk
    (D5, .25), (E5, .25), (Fis5, .25), (G5, .25), (A5, 1),
    (G5, .5), (Fis5, .5), (E5, 1),
    (Fis5, .5), (E5, .5), (D5, .5), (Cis5, .5),
    (D5, 1.5), (0, .5),
    # Regenboog-loopje (hoog en tinkelend)
    (A4, .25), (B4, .25), (Cis5, .25), (D5, .25), (E5, .25), (Fis5, .25), (G5, .25), (A5, .25),
    (A5, .5), (G5, .5), (Fis5, .5), (E5, .5),
    (D5, .5), (Cis5, .5), (B4, .5), (A4, .5),
    (D5, 2),
], bpm=125, volume=0.75)

muz7_b = baslijn([
    (D3, 2), (A3, 2), (D3, 2), (A3, 2),
    (G3, 2), (D3, 2), (A3, 2), (D3, 2),
    (D3, 2), (A3, 2), (G3, 2), (A3, 2),
    (D3, 2), (A3, 2), (G3, 2), (D3, 2),
], bpm=125, volume=0.50)

schrijf_wav("muziek_level7.wav", meng(muz7_m, muz7_b) * 2)
print("  muziek_level7.wav klaar! (De Wolken - zweefachtig)")


# ──────────────────────────────────────────────
# LEVEL 8: Het Ultieme Dak
# Episch en dramatisch! C-klein, 100 BPM.
# Donker en krachtig — de allermoeilijkste uitdaging!
# Met echte drums voor maximale spanning.
# ──────────────────────────────────────────────

# Extra noten voor C-klein
Es4  = 311   # Eb (verlaagde Mi)
Es5  = 622
As3  = 208   # Ab laag
As4  = 415   # Ab
Bes4 = 466   # Bb

muz8_m = melodie([
    # Donkere, dramatische opening
    (C4, 1), (0, .5), (G3, .5),
    (C4, .5), (Es4, .5), (G4, 1),
    (As4, 1), (G4, .5), (F4, .5),
    (Es4, 2),
    # Spanning opbouwen
    (G4, .5), (As4, .5), (Bes4, 1),
    (C5, .5), (Bes4, .5), (As4, 1),
    (G4, .5), (Es4, .5), (G4, .5), (As4, .5),
    (G4, 2),
    # Krachtig hoogtepunt
    (C5, .5), (C5, .5), (Es5, .5), (Es5, .5),
    (G5, 1), (0, 1),
    (As4, .5), (Bes4, .5), (C5, 1),
    (G4, 2),
    # Razende finale — snelle dalende reeks
    (C5, .25), (Bes4, .25), (As4, .25), (G4, .25), (F4, .25), (Es4, .25), (D4, .25), (C4, .25),
    (Es4, .5), (G4, .5), (C5, .5), (Es5, .5),
    (G5, .5), (Es5, .5), (C5, .5), (G4, .5),
    (C4, 2),
], bpm=100, volume=0.75)

muz8_b = baslijn([
    (C3, 2), (G3, 2), (C3, 2), (G3, 2),
    (As3, 2), (E3, 2), (G3, 2), (C3, 2),
    (C3, 2), (G3, 2), (As3, 2), (G3, 2),
    (C3, 2), (G3, 2), (C3, 2), (C3, 2),
], bpm=100, volume=0.55)

muz8_drums = beat_patroon(32, bpm=100)
muz8 = meng(meng(muz8_m, muz8_b), muz8_drums)
schrijf_wav("muziek_level8.wav", muz8 * 2)
print("  muziek_level8.wav klaar! (Het Ultieme Dak - episch met drums)")


# ──────────────────────────────────────────────
# LEVEL 9: De Grote Achtervolging
# Spannende achtervolging — hartslag-ritme, 160 BPM.
# Donker en dreigend, maar ook razend snel!
# Klinkt als: DE EINDBAAS RENT WEG!
# ──────────────────────────────────────────────

# Extra noten
As3  = 208
Bes4 = 466
Es4  = 311

muz9_m = melodie([
    # Opzwepende spanning — steeds verder!
    (A4, .25), (G4, .25), (A4, .25), (C5, .25), (E5, .5), (D5, .5),
    (C5, .25), (B4, .25), (A4, .25), (G4, .25), (F4, .5), (E4, .5),
    (G4, .25), (A4, .25), (B4, .25), (C5, .25), (D5, .5), (C5, .5),
    (A4, 2),
    # Achtervolging versnelt!
    (E5, .5), (D5, .5), (C5, .5), (B4, .5),
    (A4, .25), (B4, .25), (C5, .25), (D5, .25), (E5, .5), (G5, .5),
    (A5, .5), (G5, .5), (E5, .5), (C5, .5),
    (A4, 2),
    # Gespannen middenstuk — bijna gepakt!
    (A4, .25), (0, .25), (A4, .25), (0, .25), (C5, .5), (E5, .5),
    (D5, .25), (0, .25), (D5, .25), (0, .25), (B4, .5), (G4, .5),
    (A4, .25), (C5, .25), (E5, .25), (G5, .25), (F5, .5), (E5, .5),
    (D5, 2),
    # Finale — alles of niets!
    (E5, .25), (F5, .25), (G5, .25), (A5, .25), (G5, .25), (F5, .25), (E5, .25), (D5, .25),
    (C5, .5), (E5, .5), (G5, .5), (A5, .5),
    (G5, .5), (F5, .5), (E5, .5), (D5, .5),
    (E5, 2),
], bpm=160, volume=0.75)

muz9_b = baslijn([
    (A3, 1), (E3, 1), (A3, 1), (C3, 1),
    (G3, 1), (E3, 1), (A3, 1), (E3, 1),
    (A3, 1), (G3, 1), (F3, 1), (E3, 1),
    (A3, 1), (E3, 1), (A3, 1), (A3, 1),
    (A3, 1), (E3, 1), (A3, 1), (C3, 1),
    (G3, 1), (E3, 1), (D3, 1), (E3, 1),
    (A3, 1), (G3, 1), (F3, 1), (E3, 1),
    (A3, 1), (E3, 1), (A3, 1), (A3, 1),
], bpm=160, volume=0.55)

# Snellere drums voor de achtervolging!
muz9_drums = beat_patroon(64, bpm=160)
muz9 = meng(meng(muz9_m, muz9_b), muz9_drums)
schrijf_wav("muziek_level9.wav", muz9 * 2)
print("  muziek_level9.wav klaar! (De Grote Achtervolging - spannend met drums!)")


print()
print("Klaar! Alle geluiden staan in de map 'geluiden/'.")



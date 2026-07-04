# voortgang.py
# Onthoudt welke levels Menno al heeft gehaald!
# De voortgang wordt opgeslagen in een bestandje zodat je hem niet kwijtraakt.

import json
import os

# Naam van het bestand waar de voortgang in wordt opgeslagen
BESTAND = "voortgang.json"


def laad_voortgang():
    """Laad de opgeslagen voortgang.

    Geeft een dict terug met:
      - 'voltooid' : set van voltooide level-nummers
      - 'punten'   : integer (hoeveel punten de speler had)
      - 'levens'   : integer of None (hoeveel levens over waren)

    Als het bestand ontbreekt of stuk is, wordt een lege voortgang teruggegeven.
    """
    if os.path.exists(BESTAND):
        try:
            with open(BESTAND, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "voltooid": set(data.get("voltooid", [])),
                    "punten": int(data.get("punten", 0)),
                    "levens": data.get("levens", None),
                }
        except Exception:
            pass  # Als het bestand kapot is, begin dan opnieuw
    return {"voltooid": set(), "punten": 0, "levens": None}


def sla_voortgang_op(voltooid, punten=0, levens=None):
    """Sla voortgang op (voltooide levels, punten en levens)."""
    data = {
        "voltooid": sorted(list(voltooid)),
        "punten": int(punten),
        "levens": (int(levens) if levens is not None else None),
    }
    with open(BESTAND, "w", encoding="utf-8") as f:
        json.dump(data, f)


def markeer_level_voltooid(niveau, voltooid, punten=0, levens=None):
    """Voeg een level toe aan de voltooide levels en sla meteen op.

    Retourneert de bijgewerkte set met voltooide levels.
    """
    voltooid.add(niveau)
    sla_voortgang_op(voltooid, punten, levens)
    return voltooid

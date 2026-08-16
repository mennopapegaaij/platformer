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
      - 'voltooid'     : set van voltooide level-nummers
      - 'punten'       : integer (hoeveel punten de speler had)
      - 'levens'       : integer of None (hoeveel levens over waren)
      - 'arena_record' : integer (hoogste vechtmodus-level dat je haalde)

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
                    "arena_record": int(data.get("arena_record", 0)),
                }
        except Exception:
            pass  # Als het bestand kapot is, begin dan opnieuw
    return {"voltooid": set(), "punten": 0, "levens": None, "arena_record": 0}


def sla_voortgang_op(voltooid, punten=0, levens=None, arena_record=None):
    """Sla voortgang op (voltooide levels, punten, levens en arena-record)."""
    # Behoud het arena-record als het niet wordt meegegeven
    if arena_record is None:
        arena_record = laad_voortgang().get("arena_record", 0)
    data = {
        "voltooid": sorted(list(voltooid)),
        "punten": int(punten),
        "levens": (int(levens) if levens is not None else None),
        "arena_record": int(arena_record),
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


def sla_arena_record_op(record):
    """Bewaar het hoogste vechtmodus-level (alleen als het een nieuw record is).

    De gewone voortgang (voltooide levels, punten, levens) blijft ongewijzigd.
    """
    data = laad_voortgang()
    if record > data.get("arena_record", 0):
        sla_voortgang_op(data["voltooid"], data["punten"], data["levens"], record)


def reset_arena_record():
    """Zet het vechtmodus-record terug op 0 (helemaal opnieuw beginnen).

    De gewone voortgang (voltooide levels, punten, levens) blijft ongewijzigd.
    """
    data = laad_voortgang()
    sla_voortgang_op(data["voltooid"], data["punten"], data["levens"], 0)

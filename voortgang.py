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
                    "race_record": int(data.get("race_record", 0)),
                    "vlucht_record": int(data.get("vlucht_record", 0)),
                    "tijden": data.get("tijden", {}),   # beste tijden per level
                    "speler_kleur": data.get("speler_kleur"),  # gekozen spelerkleur (of None)
                }
        except Exception:
            pass  # Als het bestand kapot is, begin dan opnieuw
    return {"voltooid": set(), "punten": 0, "levens": None,
            "arena_record": 0, "race_record": 0, "vlucht_record": 0, "tijden": {},
            "speler_kleur": None}


def sla_voortgang_op(voltooid, punten=0, levens=None, arena_record=None,
                     race_record=None, vlucht_record=None):
    """Sla voortgang op (voltooide levels, punten, levens en de records)."""
    # Behoud de records die niet worden meegegeven
    huidig = laad_voortgang()
    if arena_record is None:
        arena_record = huidig.get("arena_record", 0)
    if race_record is None:
        race_record = huidig.get("race_record", 0)
    if vlucht_record is None:
        vlucht_record = huidig.get("vlucht_record", 0)
    data = {
        "voltooid": sorted(list(voltooid)),
        "punten": int(punten),
        "levens": (int(levens) if levens is not None else None),
        "arena_record": int(arena_record),
        "race_record": int(race_record),
        "vlucht_record": int(vlucht_record),
        "tijden": huidig.get("tijden", {}),   # beste tijden blijven bewaard
        "speler_kleur": huidig.get("speler_kleur"),  # gekozen kleur blijft bewaard
    }
    with open(BESTAND, "w", encoding="utf-8") as f:
        json.dump(data, f)


def sla_speler_kleur_op(kleur):
    """Bewaar de gekozen spelerkleur (een lijst [r, g, b]). De rest blijft bewaard."""
    data = {}
    if os.path.exists(BESTAND):
        try:
            with open(BESTAND, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["speler_kleur"] = list(kleur)
    with open(BESTAND, "w", encoding="utf-8") as f:
        json.dump(data, f)


def beste_tijd(level_id):
    """De beste (kortste) tijd voor dit level, of None als er nog geen is."""
    return laad_voortgang().get("tijden", {}).get(level_id)


def sla_tijd_op(level_id, tijd):
    """Bewaar de tijd als hij beter (korter) is dan de vorige.

    Geeft (beste_tijd, is_record) terug."""
    data = {}
    if os.path.exists(BESTAND):
        try:
            with open(BESTAND, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    tijden = data.get("tijden", {})
    oud = tijden.get(level_id)
    record = (oud is None) or (tijd < oud)
    if record:
        tijden[level_id] = round(tijd, 2)
    data["tijden"] = tijden
    with open(BESTAND, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return tijden[level_id], record


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


def sla_race_record_op(record):
    """Bewaar de hoogste race-baan die je haalde (alleen als het een record is)."""
    data = laad_voortgang()
    if record > data.get("race_record", 0):
        sla_voortgang_op(data["voltooid"], data["punten"], data["levens"],
                         data["arena_record"], record)


def sla_vlucht_record_op(record):
    """Bewaar de hoogste vliegtuig-baan die je haalde (alleen als het een record is)."""
    data = laad_voortgang()
    if record > data.get("vlucht_record", 0):
        sla_voortgang_op(data["voltooid"], data["punten"], data["levens"],
                         data["arena_record"], data["race_record"], record)

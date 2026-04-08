# voortgang.py
# Onthoudt welke levels Menno al heeft gehaald!
# De voortgang wordt opgeslagen in een bestandje zodat je hem niet kwijtraakt.

import json
import os

# Naam van het bestand waar de voortgang in wordt opgeslagen
BESTAND = "voortgang.json"


def laad_voortgang():
    """Laad de opgeslagen voortgang. Geeft een set van voltooide level-nummers terug."""
    if os.path.exists(BESTAND):
        try:
            with open(BESTAND, "r") as f:
                data = json.load(f)
                # Zet de lijst om naar een set (zodat we snel kunnen opzoeken)
                return set(data.get("voltooid", []))
        except Exception:
            pass  # Als het bestand kapot is, begin dan opnieuw
    return set()  # Nog niets gehaald


def sla_voortgang_op(voltooid):
    """Sla op welke levels voltooid zijn."""
    with open(BESTAND, "w") as f:
        json.dump({"voltooid": sorted(list(voltooid))}, f)


def markeer_level_voltooid(niveau, voltooid):
    """Voeg een level toe aan de voltooide levels en sla meteen op."""
    voltooid.add(niveau)
    sla_voortgang_op(voltooid)
    return voltooid

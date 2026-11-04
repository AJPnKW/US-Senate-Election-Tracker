"""Validate the internal election feed contract. This is NOT AP's native schema."""
from datetime import datetime, timezone
STATES = {"AK", "IA", "KS", "ME", "MI", "OH", "TX", "NC"}
def normalize(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("races"), list):
        raise ValueError("Expected object containing races list")
    races = []
    seen = set()
    for race in payload["races"]:
        if not isinstance(race, dict):
            raise ValueError("Invalid race")
        state = race.get("state")
        if state not in STATES or state in seen or race.get("office") != "US Senate":
            raise ValueError("Unexpected/duplicate state or office")
        seen.add(state)
        candidates = race.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("Missing candidates")
        clean = []
        for c in candidates:
            if not isinstance(c, dict) or not isinstance(c.get("name"), str) or not c["name"].strip() or c.get("party") not in ("D", "R", "I", "O") or type(c.get("votes")) is not int or c["votes"] < 0:
                raise ValueError("Invalid candidate")
            clean.append({"name": c["name"].strip(), "party": c["party"], "votes": c["votes"]})
        progress = race.get("reporting_pct")
        if progress is not None and (type(progress) not in (int, float) or not 0 <= progress <= 100):
            raise ValueError("Invalid reporting progress")
        called = race.get("called_party")
        if called is not None and called not in {c["party"] for c in clean}:
            raise ValueError("Invalid race call")
        updated = race.get("updated_at")
        if updated is not None and not isinstance(updated, str):
            raise ValueError("Invalid timestamp")
        races.append({"state": state, "candidates": clean, "reporting_pct": progress, "called_party": called, "updated_at": updated})
    if not races:
        raise ValueError("Empty feed is not validated results")
    return {"source_validated": True, "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "races": races}

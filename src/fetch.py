"""Collect public official-state Senate vote counts via Open America; no credentials."""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://openamerica.io/elections/results.json?year=2026&office=Senate"
STATES = {"AK", "IA", "KS", "ME", "MI", "OH", "TX", "NC"}

def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def write(path, obj):
    target = ROOT / path
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)

def convert(payload):
    if not isinstance(payload, dict) or payload.get("api") != 1 or payload.get("year") != 2026 or str(payload.get("office")).lower() != "senate" or not isinstance(payload.get("races"), dict):
        raise ValueError("Unexpected Open America Senate response")
    races = []
    for state, raw in payload["races"].items():
        if state not in STATES or not isinstance(raw, dict):
            continue
        candidates = []
        for c in raw.get("cands", []):
            if not isinstance(c, dict) or not isinstance(c.get("n"), str) or type(c.get("v")) is not int or c["v"] < 0:
                continue
            party = c.get("p", "")
            candidates.append({"name": c["n"], "party": party if party in ("D", "R", "I") else "O", "votes": c["v"]})
        if not candidates:
            continue
        progress = raw.get("pct_in")
        if progress is not None and (type(progress) not in (int, float) or not 0 <= progress <= 100):
            progress = None
        races.append({"state": state, "candidates": candidates, "reporting_pct": progress, "called_party": None, "updated_at": payload.get("as_of")})
    return {"source_validated": True, "source": "Official state election offices via Open America", "updated_at": payload.get("as_of"), "races": races}

def main():
    try:
        request = urllib.request.Request(URL, headers={"Accept": "application/json", "Accept-Encoding": "identity", "User-Agent": "AJPnKW-US-Senate-Election-Tracker/1.0"})
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.load(response)
        result = convert(payload)
        write("data/results.json", result)
        write("data/fetch_status.json", {"checked_at": stamp(), "ok": True, "error": None, "source": result["source"]})
        print("Collected", len(result["races"]), "monitored states from Open America")
        return 0
    except Exception as exc:
        message = str(exc)[:240]
        write("data/fetch_status.json", {"checked_at": stamp(), "ok": False, "error": message})
        print("Collection failed:", message, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

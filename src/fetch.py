"""Server-side collector. The AP response must first be mapped to the internal contract."""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from normalize import normalize
ROOT = Path(__file__).resolve().parents[1]
def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
def write(path, obj):
    target = ROOT / path
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
def main():
    try:
        key = os.environ.get("AP_API_KEY")
        url = os.environ.get("AP_ELECTIONS_URL")
        if not key or not url:
            raise RuntimeError("AP_API_KEY or AP_ELECTIONS_URL missing; live results not configured")
        if not url.startswith("https://"):
            raise RuntimeError("Feed URL must use HTTPS")
        req = urllib.request.Request(url, headers={"x-api-key": key, "Accept": "application/json", "User-Agent": "US-Senate-Election-Tracker/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            if response.status != 200:
                raise RuntimeError("Feed HTTP status " + str(response.status))
            payload = json.load(response)
        normalized = normalize(payload)
        write("data/results.json", normalized)
        write("data/fetch_status.json", {"checked_at": stamp(), "ok": True, "error": None})
        print("Validated results saved")
        return 0
    except Exception as exc:
        msg = str(exc)
        if os.environ.get("AP_API_KEY"):
            msg = msg.replace(os.environ["AP_API_KEY"], "[REDACTED]")
        write("data/fetch_status.json", {"checked_at": stamp(), "ok": False, "error": msg[:240]})
        print("Collection failed: " + msg[:240], file=sys.stderr)
        return 1
if __name__ == "__main__":
    sys.exit(main())

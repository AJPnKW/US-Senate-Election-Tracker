"""Optional Election.org developer-key connectivity check.

This endpoint returns historical certified results, NOT live 2026 counts.
Never merge its response into the live Senate dashboard.
"""
import json
import os
import sys
import urllib.error
import urllib.request

URL = "https://election.org/api/developers/data/results?year=2024&state=MI&office=S"

def main():
    key = os.environ.get("ELECTION_ORG_API_KEY", "").strip()
    if not key:
        print("Election.org developer key not configured; skipping optional connectivity check")
        return 0
    request = urllib.request.Request(
        URL,
        headers={"Authorization": "Bearer " + key, "Accept": "application/json", "User-Agent": "US-Senate-Election-Tracker/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise ValueError("Unexpected response type")
        print("Election.org developer endpoint reachable; historical data only")
        return 0
    except Exception as exc:
        print("Election.org connectivity failed:", str(exc).replace(key, "[REDACTED]"), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

# U.S. Senate Election Tracker — 2026

Public, responsive GitHub Pages dashboard tracking eight U.S. Senate contests: AK, IA, KS, ME, MI, OH, TX and NC.

**Live data is not configured.** The application never invents election results or interprets missing data as zero. It intentionally displays DATA UNAVAILABLE until a validated, licensed source is connected.

## Architecture

- GitHub Pages: static HTML, CSS and JavaScript, reading data/results.json.
- GitHub Actions: scheduled and manual collector, tests, Pages deployment.
- AP API key is read only by GitHub Actions from a repository secret; never embedded in the website.
- Browser refreshes every 60 seconds. GitHub Actions schedules are best effort, not real-time guarantees.
- Failed collection preserves the previous verified snapshot and reports failure separately.

## Setup

1. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Obtain AP Elections API access **and redistribution rights** for public display.
3. Settings → Secrets and variables → Actions: create secret **AP_API_KEY** and variable **AP_ELECTIONS_URL** using the exact licensed URL.
4. Verify the actual AP response schema. The collector currently accepts only the internal normalized contract documented in docs/DESIGN.md. It does not claim this is AP's native schema. Adapt src/normalize.py based on official AP documentation and tests before enabling the feed.
5. Actions → Publish election dashboard → Run workflow. View the deployment in Actions.

Expected site URL: https://ajpnkw.github.io/US-Senate-Election-Tracker/

## Testing

Run: `python -m unittest discover -s tests -v`

For local preview: `python -m http.server 8000`.

National Senate balance requires an independently validated nationwide feed including holdover seats; the application explicitly marks it unavailable until implemented.

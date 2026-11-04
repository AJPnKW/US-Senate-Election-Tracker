# End-to-end design and acceptance criteria

## Goal

Mobile-first public GitHub Pages application with three sections: overall summary, national Senate balance and an eight-state Senate comparison (AK, IA, KS, ME, MI, OH, TX, NC).

## Data flow

Licensed AP endpoint → scheduled GitHub Actions Python collector → validation and normalization → atomic JSON snapshot → GitHub Pages → browser polling every 60 seconds.

## Trust and safety

No invented votes, candidates, calls, reporting percentages or national seat totals. Missing values are displayed as em dashes. A provider lead is not a race call. Do not publish AP data until the license permits redistribution. API secrets stay in GitHub Actions. Fetch errors preserve the last validated results and update status separately. Last successful data timestamp and last attempted fetch are distinguished.

## Internal adapter contract (NOT AP's native schema)

```json
{"races":[{"state":"TX","office":"US Senate","candidates":[{"name":"Candidate","party":"D","votes":123}],"reporting_pct":42.1,"called_party":null,"updated_at":"2026-11-03T23:00:00Z"}]}
```

The adapter must be mapped and tested against the licensed AP response before live deployment. A nationwide Senate feed with holdovers is separately required to compute national balance.

## Deployment acceptance

Repository contains source and tests; Actions tests pass; Pages workflow deploys; URL returns the dashboard; empty feed is explicitly unavailable; valid licensed AP feed is parsed without fabricated values; freshness and collection errors remain visible. Deployment and AP validation are separate gates.

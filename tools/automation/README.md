# Website Analyzer (Premium Auto Mode automation)

A standalone headless-browser tool that walks a target website, records
interaction telemetry, captures screenshots, collects page metrics, and
generates heuristic UX recommendations.

## Setup

```bash
npm install
```

## Usage

```bash
node automation_script.cjs <url> [analysis_id]

# Example
node automation_script.cjs https://example.com

# Optionally point at a running gateway
API_BASE_URL=http://localhost:8080 node automation_script.cjs https://example.com
```

## What it produces

- `analysis_results.json` — full analysis results, saved incrementally
  after every screenshot and every 5 tracked events, so an interrupted run
  still leaves usable partial output (`SIGINT`/`SIGTERM` trigger a final save)
- `screenshots/` — one capture per viewport height plus a full-page capture
- Tracked events (clicks, scrolls) with element metadata and bounding boxes
- Page metrics (element/image/link/button/form/heading counts, alt-text
  coverage, viewport meta presence) and derived recommendations

## Backend integration

If a gateway is reachable at `API_BASE_URL`, the script POSTs its results to
`$API_BASE_URL/api/questions/premium-auto/automation-results`.

> **Status:** that receiving endpoint is not implemented in the gateway yet —
> the Premium Auto Mode in the web UI currently returns demo data. Results
> are always written locally regardless of backend availability.

## Attribution

Uses [Puppeteer](https://pptr.dev/) with
[puppeteer-extra](https://github.com/berstend/puppeteer-extra) and its
stealth plugin.

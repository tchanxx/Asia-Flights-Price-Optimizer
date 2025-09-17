## Asia Flights Price Optimizer

### Overview
Evaluate multi-city Asia itineraries from NYC for December 2025 with a Hong Kong New Year’s anchor. Given a CSV of cheapest nonstop fares by date, the tool searches feasible city orders and lengths of stay, applies limited date flexibility, and returns the lowest-cost itineraries.

Key constraints baked in:
- Must be in Hong Kong from 2025-12-28 through 2026-01-01 inclusive.
- Depart NYC in one of three windows: early (Dec 6–10), mid (Dec 11–17), late (Dec 18–24).
- Total trip length between 17 and 25 days (inclusive).
- Default nights per city: Tokyo 5, Hong Kong 5, Taiwan 5, optionally Shanghai 3 — each with ±1 night flexibility, with a minimum of 4 nights enforced per city (so `SHA` defaults to 4).
- Nonstops only (stops must be 0).

Cities (IATA-like codes): `NYC`, `TYO` (Tokyo), `HKG` (Hong Kong), `TPE` (Taiwan), `SHA` (Shanghai).

### Requirements
- Python 3.9+
- No third-party dependencies (stdlib only)

Install (optional virtual environment):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CSV Schema (`flights.csv`)
One row per route per date representing the cheapest nonstop fare you found for that date.

Required columns:
- `origin_city`: one of `NYC`, `TYO`, `HKG`, `TPE`, `SHA`
- `destination_city`: one of `NYC`, `TYO`, `HKG`, `TPE`, `SHA`
- `date`: `YYYY-MM-DD`
- `price`: numeric (USD)
- `stops`: integer; must be `0` (rows with non-zero stops are ignored)

Optional (recommended for better tie-breaking/usability):
- `duration_minutes`: integer (used only for tie-breaks if prices are equal)
- `airline`: string (e.g., `JL`, `CX`, `BR`, `CI`)
- `booking_link`: string URL for booking

Notes:
- The tool keeps the cheapest entry for a given `(origin_city, destination_city, date)`; if prices tie, the shorter `duration_minutes` wins.
- Unknown/missing durations are treated as 0 for tie-breaking.

### Generate a template CSV
This writes a header and a few illustrative rows you can overwrite.
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --write-template /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv
```

### Run the optimizer
Basic run (top 10 itineraries total, across both with/without Shanghai):
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv
```

Top N results:
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv \
  --top 15
```

Filter to a specific departure window (choices: early, mid, late):
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv \
  --window mid
```

Only itineraries that include Shanghai (`SHA`):
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv \
  --include-shanghai
```

Only itineraries that exclude Shanghai:
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv \
  --exclude-shanghai
```

Summary matrix of cheapest prices by window (rows) and Shanghai inclusion (columns),
followed by printing those itineraries:
```bash
python3 /Users/travischan/Projects/Asia-Flights-Price-Optimizer/trip_calculator.py \
  --csv /Users/travischan/Projects/Asia-Flights-Price-Optimizer/flights.csv \
  --summary-table
```
Example output (prices illustrative):
```text
Summary price table (USD):
Window | with_SHA    | without_SHA
----------------------------------
early  | $2237       | $2168
mid    | $2237       | $2168
late   | -           | $2310

Itineraries in summary table:
[1] $2237 | window=mid | include_SHA=True
...
```

### Date flexibility and defaults
When selecting a flight for a preferred date (forward-only), the tool:
1) Searches on the preferred date, then up to +1 day (no earlier than the preferred date).
2) If none found, searches up to +7 days (still forward-only).
3) If still none, synthesizes a default-priced flight for the preferred date.

Default price rules (if no historical price for the route):
- Outbound NYC→Asia in Dec 2025: `NYC→TYO $900`, `NYC→HKG $1100`, `NYC→TPE $950`, `NYC→SHA $1200`.
- Inbound Asia→NYC in Jan 2026: `TYO→NYC $570`, `HKG→NYC $1070`, `TPE→NYC $839`, `SHA→NYC $1570`.
- Intra-Asia (selected pairs): `TYO↔HKG $120`, `HKG→TPE $70`, `TPE→HKG $55`, `TPE↔SHA ~$140–150`; others default to ~$120.

### Output
Each result prints:
- Total price, departure window (`early|mid|late`), and whether Shanghai is included.
- Route: `NYC -> ... -> NYC`.
- Nights per city and overall start/end dates (trip days ≈ arrival_back - start + 1).
- Hong Kong anchor dates (arrival and departure used to enforce 12/28–01/01).
- Segment list with `depart`, `arrive`, price, and optional `airline` and `booking_link`.

Example snippet (format abbreviated):
```text
[1] $2168 | window=mid | include_SHA=False
    Route: NYC -> TYO -> TPE -> HKG -> NYC
    Nights: TYO:6n, TPE:6n, HKG:6n
    Start: 2025-12-11  End: 2026-01-03  (≈ 24 days)
    HK: arrive 2025-12-27  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-12 arrive 2025-12-13 $900
      TYO->TPE  depart 2025-12-19 arrive 2025-12-20 $120
      TPE->HKG  depart 2025-12-26 arrive 2025-12-27 $48
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $1100

[2] $2168 | window=mid | include_SHA=False
    Route: NYC -> TYO -> TPE -> HKG -> NYC
    Nights: TYO:6n, TPE:6n, HKG:6n
    Start: 2025-12-12  End: 2026-01-03  (≈ 23 days)
    HK: arrive 2025-12-27  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-12 arrive 2025-12-13 $900
      TYO->TPE  depart 2025-12-19 arrive 2025-12-20 $120
      TPE->HKG  depart 2025-12-26 arrive 2025-12-27 $48
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $1100

[3] $2237 | window=mid | include_SHA=True
    Route: NYC -> TYO -> SHA -> TPE -> HKG -> NYC
    Nights: TYO:4n, SHA:4n, TPE:4n, HKG:5n
    Start: 2025-12-11  End: 2026-01-03  (≈ 24 days)
    HK: arrive 2025-12-28  depart 2026-01-02 (must cover 12/28-01/01)
    Segments:
      NYC->TYO  depart 2025-12-12 arrive 2025-12-13 $900
      TYO->SHA  depart 2025-12-17 arrive 2025-12-18 $120
      SHA->TPE  depart 2025-12-22 arrive 2025-12-23 $69
      TPE->HKG  depart 2025-12-27 arrive 2025-12-28 $48
      HKG->NYC  depart 2026-01-02 arrive 2026-01-03 $1100
```

### Data quality tips
- Prefer real, nonstop fares per date; one row per `(origin, destination, date)`.
- Include `duration_minutes` where possible for better tie-breaks.
- Use consistent city codes: `NYC`, `TYO`, `HKG`, `TPE`, `SHA`.

### File reference
- `trip_calculator.py`: CLI entry point and optimizer logic.
- `flights.csv`: Your input data file (can be generated via `--write-template`).
- `requirements.txt`: Notes Python version; no external packages needed.

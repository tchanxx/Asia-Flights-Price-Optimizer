from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import permutations, product
from typing import Dict, Iterable, List, Optional, Tuple

# ==============================
# Data models
# ==============================


@dataclass(frozen=True)
class FlightOption:
    """Represents a single flight option for a specific origin/destination on a given date.

    All money values are assumed to be USD. Dates are local calendar dates (no times).
    Stops should be the count of intermediate stops. Nonstop = 0 stops.
    Duration is optional (minutes). Unknown durations are treated as 0 only for tie-breaking.
    """

    origin_city: str
    destination_city: str
    date: date
    price: float
    stops: int
    duration_minutes: int = 0
    airline: str = ""
    booking_link: str = ""


@dataclass
class Segment:
    """A flown segment in an itinerary (chosen flight)."""

    origin_city: str
    destination_city: str
    depart_date: date
    arrive_date: date
    flight: FlightOption


@dataclass
class ItineraryResult:
    """An evaluated itinerary with pricing and schedule details."""

    include_shanghai: bool
    departure_window: str  # "early" | "mid" | "late"
    order: List[str]  # Asia city order (e.g., ["TYO", "HKG", "TPE"])
    nights_per_city: Dict[str, int]
    segments: List[Segment]
    total_price: float
    total_duration_minutes: int
    start_date: date
    end_date: date
    hk_arrival: Optional[date]
    hk_depart: Optional[date]

    def score_tuple(self) -> Tuple[float, int, date]:
        """Sort primarily by total price, then total duration, then earlier start date."""
        return (self.total_price, self.total_duration_minutes, self.start_date)


# ==============================
# CSV schema helpers
# ==============================


CSV_FIELDS = [
    "origin_city",
    "destination_city",
    "date",
    "price",
    "stops",
    "duration_minutes",
    "airline",
    "booking_link",
]


def write_csv_template(path: str) -> None:
    """Write a CSV template users can fill with cheapest nonstop fares by date.

    Notes:
    - Use city codes only: NYC, TYO, HKG, TPE, SHA
    - One row per route per date (cheapest fare).
    - Required fields: origin_city, destination_city, date (YYYY-MM-DD), price, stops
    - Nonstops only: stops must be 0. Rows with stops > 0 will be ignored.
    - duration_minutes/airline/booking_link are optional but help with tie-breaking and usability.
    """

    sample_rows = [
        {
            "origin_city": "NYC",
            "destination_city": "TYO",
            "date": "2025-12-06",
            "price": "780",
            "stops": "0",
            "duration_minutes": "840",
            "airline": "JL",
            "booking_link": "https://example.com/nyc-tyo-2025-12-06",
        },
        {
            "origin_city": "TYO",
            "destination_city": "HKG",
            "date": "2025-12-12",
            "price": "210",
            "stops": "0",
            "duration_minutes": "300",
            "airline": "CX",
            "booking_link": "https://example.com/tyo-hkg-2025-12-12",
        },
        {
            "origin_city": "HKG",
            "destination_city": "TPE",
            "date": "2025-12-31",
            "price": "150",
            "stops": "0",
            "duration_minutes": "95",
            "airline": "BR",
            "booking_link": "https://example.com/hkg-tpe-2025-12-31",
        },
        {
            "origin_city": "TPE",
            "destination_city": "NYC",
            "date": "2026-01-10",
            "price": "650",
            "stops": "0",
            "duration_minutes": "920",
            "airline": "CI",
            "booking_link": "https://example.com/tpe-nyc-2026-01-10",
        },
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in sample_rows:
            writer.writerow(row)


# ==============================
# Flight store and lookup
# ==============================


class FlightStore:
    """Stores flight options and provides efficient lookup with date flexibility.

    The store uses a dict keyed by (origin_city, destination_city, date) mapping to the
    cheapest nonstop flight on that date. If multiple rows exist for a given key, the
    cheapest is kept.
    """

    def __init__(self, flights: Iterable[FlightOption]):
        self._by_key: Dict[Tuple[str, str, date], FlightOption] = {}
        self._route_prices: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        for f in flights:
            if f.stops != 0:
                # Enforce nonstops-only policy
                continue
            key = (f.origin_city.upper(), f.destination_city.upper(), f.date)
            existing = self._by_key.get(key)
            if existing is None or f.price < existing.price or (
                f.price == existing.price and f.duration_minutes < existing.duration_minutes
            ):
                self._by_key[key] = f
            self._route_prices[(key[0], key[1])].append(f.price)

    def get_best_on_date_with_flex(
        self,
        origin_city: str,
        destination_city: str,
        preferred_date: date,
        flex_days: int = 1,
        fallback_days: int = 7,
        allow_default: bool = True,
    ):
        """Return (FlightOption, actual_date) with layered fallbacks.

        1) Search within ±flex_days
        2) If none, search within ±fallback_days
        3) If none and allow_default, synthesize a default-priced flight on preferred_date
        """

        origin = origin_city.upper()
        dest = destination_city.upper()
        candidates: List[Tuple[FlightOption, date]] = []
        for delta in range(-flex_days, flex_days + 1):
            d = preferred_date + timedelta(days=delta)
            # Do not allow flights earlier than preferred_date (monotonic schedule)
            if d < preferred_date:
                continue
            f = self._by_key.get((origin, dest, d))
            if f is not None:
                candidates.append((f, d))
        if not candidates:
            if fallback_days and fallback_days > flex_days:
                for delta in range(-fallback_days, fallback_days + 1):
                    d = preferred_date + timedelta(days=delta)
                    if d < preferred_date:
                        continue
                    f = self._by_key.get((origin, dest, d))
                    if f is not None:
                        candidates.append((f, d))
        if not candidates and allow_default:
            default_flight = self._synthesize_default_flight(origin, dest, preferred_date)
            return (default_flight, preferred_date)
        if not candidates:
            return None
        candidates.sort(key=lambda x: (x[0].price, x[0].duration_minutes, x[1]))
        return candidates[0]

    # ---------- Defaults helpers ----------

    def _synthesize_default_flight(self, origin: str, dest: str, d: date) -> FlightOption:
        price = self._compute_default_price(origin, dest, d)
        return FlightOption(
            origin_city=origin,
            destination_city=dest,
            date=d,
            price=price,
            stops=0,
            duration_minutes=0,
            airline="",
            booking_link="",
        )

    def _compute_default_price(self, origin: str, dest: str, d: date) -> float:
        # If we have historical prices for this route, use median
        route_prices = self._route_prices.get((origin, dest), [])
        if route_prices:
            try:
                return round(float(statistics.median(route_prices)), 2)
            except statistics.StatisticsError:
                pass

        ASIA_SET = {TOKYO, HONG_KONG, TAIWAN, SHANGHAI}

        # Longhaul outbound (NYC -> Asia) in Dec 2025
        if origin == NYC and dest in ASIA_SET and d.year == 2025 and d.month == 12:
            defaults = {
                TOKYO: 900.0,
                HONG_KONG: 1100.0,
                TAIWAN: 950.0,
                SHANGHAI: 1200.0,
            }
            return defaults.get(dest, 1000.0)

        # Longhaul inbound (Asia -> NYC) in Jan 2026
        if dest == NYC and origin in ASIA_SET and d.year == 2026 and d.month == 1:
            defaults = {
                TOKYO: 570.0,
                HONG_KONG: 1070.0,
                TAIWAN: 839.0,
                SHANGHAI: 1570.0,
            }
            return defaults.get(origin, 900.0)

        # Intra-Asia defaults (approx from provided ranges)
        defaults_intra_specific: Dict[Tuple[str, str], float] = {
            (TOKYO, HONG_KONG): 120.0,
            (HONG_KONG, TOKYO): 120.0,
            (HONG_KONG, TAIWAN): 70.0,
            (TAIWAN, HONG_KONG): 55.0,
            (TAIWAN, SHANGHAI): 140.0,
            (SHANGHAI, TAIWAN): 150.0,
        }
        if origin in ASIA_SET and dest in ASIA_SET:
            return defaults_intra_specific.get((origin, dest), 120.0)

        # Ultimate fallback
        return 1000.0


def parse_csv(path: str) -> List[FlightOption]:
    """Parse the flight CSV according to the expected schema.

    Skips rows that are missing required fields or have invalid values.
    Enforces nonstops-only by discarding rows with stops != 0.
    """

    flights: List[FlightOption] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for _, row in enumerate(reader, start=2):  # start=2 accounts for header line being 1
            try:
                origin_city = row.get("origin_city", "").strip().upper()
                destination_city = row.get("destination_city", "").strip().upper()
                if not origin_city or not destination_city:
                    continue

                # Date
                date_str = row.get("date", "").strip()
                if not date_str:
                    continue
                d = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Price
                price_str = row.get("price", "").strip()
                if not price_str:
                    continue
                price = float(price_str)

                # Stops
                stops_str = row.get("stops", "").strip()
                if stops_str == "":
                    # Unknown -> exclude to satisfy nonstops-only requirement
                    continue
                stops = int(stops_str)
                if stops != 0:
                    # Nonstops only
                    continue

                # Optional fields
                duration_minutes = 0
                dur_str = row.get("duration_minutes", "").strip()
                if dur_str:
                    duration_minutes = int(dur_str)

                airline = row.get("airline", "").strip()
                booking_link = row.get("booking_link", "").strip()

                flights.append(
                    FlightOption(
                        origin_city=origin_city,
                        destination_city=destination_city,
                        date=d,
                        price=price,
                        stops=stops,
                        duration_minutes=duration_minutes,
                        airline=airline,
                        booking_link=booking_link,
                    )
                )
            except Exception:
                # Skip malformed rows silently to keep tool robust
                continue
    return flights


# ==============================
# Scheduling and search
# ==============================


NYC = "NYC"
TOKYO = "TYO"
HONG_KONG = "HKG"
TAIWAN = "TPE"
SHANGHAI = "SHA"


def daterange(start: date, end: date) -> Iterable[date]:
    """Yield dates from start to end inclusive."""

    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def departure_windows_dec_2025() -> Dict[str, Tuple[date, date]]:
    """Define early/mid/late December 2025 windows given earliest departure Dec 6.

    - early: Dec 6–Dec 10
    - mid:   Dec 11–Dec 17
    - late:  Dec 18–Dec 24
    """

    return {
        "early": (date(2025, 12, 6), date(2025, 12, 10)),
        "mid": (date(2025, 12, 11), date(2025, 12, 17)),
        "late": (date(2025, 12, 18), date(2025, 12, 24)),
    }


def default_nights(include_shanghai: bool) -> Dict[str, int]:
    base = {
        TOKYO: 5,
        HONG_KONG: 4,  # must cover 12/28–1/1 inclusive
        TAIWAN: 4,
    }
    if include_shanghai:
        base[SHANGHAI] = 3
    return base


def nights_choices(nights: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    """Return min/max nights per city (±1 flexibility), enforcing at least 4 nights."""

    return {city: (max(4, n - 1), max(4, n + 1)) for city, n in nights.items()}


def enforce_hk_anchor(hk_arrival: date, hk_depart: date) -> bool:
    """Must be in HK from 2025-12-28 through 2026-01-01 inclusive.

    That implies arrival on/before 12/28 and departure on/after 01/02.
    """

    must_arrive_by = date(2025, 12, 28)
    earliest_depart = date(2026, 1, 2)
    return hk_arrival <= must_arrive_by and hk_depart >= earliest_depart


def build_itineraries(
    store: FlightStore,
    include_shanghai: bool,
    windows: Dict[str, Tuple[date, date]],
    top_k: int = 10,
    flex_days: int = 1,
    min_total_days: int = 17,
    max_total_days: int = 25,
) -> List[ItineraryResult]:
    """Search itineraries under constraints, returning top_k by price.

    Approach:
    - Generate permutations of city orders for target set (with/without Shanghai).
    - For each departure date in early/mid/late windows, try all combinations of nights (±1).
    - For each option, pick flights on preferred dates with ±flex_days to minimize price.
    - Assume flights consume 1 day (arrival = depart + 1 day). Rough estimate is acceptable.
    - Enforce HK anchor and total trip length 17–25 days.
    """

    cities = [TOKYO, HONG_KONG, TAIWAN] + ([SHANGHAI] if include_shanghai else [])
    base_n = default_nights(include_shanghai)
    ranges = nights_choices(base_n)

    results: List[ItineraryResult] = []
    for window_name, (start_d, end_d) in windows.items():
        for depart_d in daterange(start_d, end_d):
            for order in permutations(cities):
                # Iterate all combinations of nights per city within [min,max]
                bounds = [ranges[c] for c in order]
                for nights_tuple in product(*[range(lo, hi + 1) for lo, hi in bounds]):
                    nights_map = {city: nights_tuple[i] for i, city in enumerate(order)}

                    # Build schedule
                    segments: List[Segment] = []
                    total_price = 0.0
                    total_duration = 0

                    # NYC -> first city
                    current_depart_date = depart_d
                    first_city = order[0]
                    best = store.get_best_on_date_with_flex(
                        NYC, first_city, current_depart_date, flex_days
                    )
                    if best is None:
                        continue
                    flight0, used_d0 = best
                    arrive = used_d0 + timedelta(days=1)
                    segments.append(
                        Segment(NYC, first_city, used_d0, arrive, flight0)
                    )
                    total_price += flight0.price
                    total_duration += flight0.duration_minutes

                    # Stay in first city
                    current_depart_date = arrive + timedelta(days=nights_map[first_city])

                    hk_arrival: Optional[date] = arrive if first_city == HONG_KONG else None
                    hk_depart: Optional[date] = None

                    feasible = True
                    for i in range(len(order) - 1):
                        origin = order[i]
                        dest = order[i + 1]
                        best_leg = store.get_best_on_date_with_flex(
                            origin, dest, current_depart_date, flex_days
                        )
                        if best_leg is None:
                            feasible = False
                            break
                        flight, used_d = best_leg
                        arrive = used_d + timedelta(days=1)
                        segments.append(Segment(origin, dest, used_d, arrive, flight))
                        total_price += flight.price
                        total_duration += flight.duration_minutes

                        # Track HK anchor window
                        if dest == HONG_KONG and hk_arrival is None:
                            hk_arrival = arrive
                        if origin == HONG_KONG and hk_depart is None:
                            hk_depart = used_d

                        # Next depart after stay in destination (monotonic progression)
                        next_earliest = arrive + timedelta(days=nights_map[dest])
                        if next_earliest < current_depart_date:
                            feasible = False
                            break
                        current_depart_date = next_earliest

                    if not feasible:
                        continue

                    # Last city -> NYC
                    last_city = order[-1]
                    best_back = store.get_best_on_date_with_flex(last_city, NYC, current_depart_date, flex_days)
                    if best_back is None:
                        continue
                    flight_back, used_db = best_back
                    arrive_back = used_db + timedelta(days=1)
                    segments.append(
                        Segment(last_city, NYC, used_db, arrive_back, flight_back)
                    )
                    total_price += flight_back.price
                    total_duration += flight_back.duration_minutes

                    # If we never departed HKG (i.e., HKG is last city), set hk_depart to the NYC leg date
                    if hk_depart is None and last_city == HONG_KONG:
                        hk_depart = used_db

                    # Validate HK anchor
                    if hk_arrival is None or hk_depart is None:
                        # No HK present – invalid order for requirements
                        continue
                    if not enforce_hk_anchor(hk_arrival, hk_depart):
                        continue

                    # Validate total trip length
                    total_days = (arrive_back - depart_d).days + 1
                    if total_days < min_total_days or total_days > max_total_days:
                        continue

                    results.append(
                        ItineraryResult(
                            include_shanghai=include_shanghai,
                            departure_window=window_name,
                            order=list(order),
                            nights_per_city=nights_map,
                            segments=segments,
                            total_price=round(total_price, 2),
                            total_duration_minutes=total_duration,
                            start_date=depart_d,
                            end_date=arrive_back,
                            hk_arrival=hk_arrival,
                            hk_depart=hk_depart,
                        )
                    )

    # Sort and return top_k
    results.sort(key=lambda r: r.score_tuple())
    return results[:top_k]


# ==============================
# CLI
# ==============================


def print_results(results: List[ItineraryResult]) -> None:
    if not results:
        print("No valid itineraries found with current data and constraints.")
        return

    for idx, r in enumerate(results, start=1):
        order_str = " -> ".join([NYC] + r.order + [NYC])
        nights_str = ", ".join(f"{city}:{r.nights_per_city[city]}n" for city in r.order)
        print(f"[{idx}] ${r.total_price:.0f} | window={r.departure_window} | include_SHA={r.include_shanghai}")
        print(f"    Route: {order_str}")
        print(f"    Nights: {nights_str}")
        print(f"    Start: {r.start_date.isoformat()}  End: {r.end_date.isoformat()}  (\u2248 { (r.end_date - r.start_date).days + 1 } days)")
        print(f"    HK: arrive {r.hk_arrival}  depart {r.hk_depart} (must cover 12/28-01/01)")
        print("    Segments:")
        for s in r.segments:
            link = f"  link={s.flight.booking_link}" if s.flight.booking_link else ""
            airline = f"  airline={s.flight.airline}" if s.flight.airline else ""
            print(
                f"      {s.origin_city}->{s.destination_city}  depart {s.depart_date} arrive {s.arrive_date} "
                f"${s.flight.price:.0f}{airline}{link}"
            )
        print("")


def build_summary_matrix(
    store: FlightStore,
    windows: Dict[str, Tuple[date, date]],
    flex_days: int = 1,
    min_total_days: int = 17,
    max_total_days: int = 25,
) -> Tuple[List[str], Dict[str, Dict[str, Optional[ItineraryResult]]]]:
    """Compute the cheapest itinerary per (window x include_shanghai) cell.

    Returns (row_order, matrix) where matrix[row][col] is an ItineraryResult or None.
    Columns are the strings "with_SHA" and "without_SHA".
    """

    # Stable desired order
    desired_order = ["early", "mid", "late"]
    row_order = [w for w in desired_order if w in windows]

    matrix: Dict[str, Dict[str, Optional[ItineraryResult]]] = {}
    for w in row_order:
        win_dict = {w: windows[w]}
        best_with = build_itineraries(
            store,
            include_shanghai=True,
            windows=win_dict,
            top_k=1,
            flex_days=flex_days,
            min_total_days=min_total_days,
            max_total_days=max_total_days,
        )
        best_without = build_itineraries(
            store,
            include_shanghai=False,
            windows=win_dict,
            top_k=1,
            flex_days=flex_days,
            min_total_days=min_total_days,
            max_total_days=max_total_days,
        )

        matrix[w] = {
            "with_SHA": best_with[0] if best_with else None,
            "without_SHA": best_without[0] if best_without else None,
        }

    return row_order, matrix


def print_summary_price_table(row_order: List[str], matrix: Dict[str, Dict[str, Optional[ItineraryResult]]]) -> None:
    """Pretty-print the summary price table (rows: windows, columns: with/without SHA)."""

    # Compute column widths
    row_label = "Window"
    col_labels = ["with_SHA", "without_SHA"]
    row_w = max(len(row_label), *(len(r) for r in row_order)) if row_order else len(row_label)
    col_w = 11  # enough for '$123456789'

    # Header
    header = f"{row_label:<{row_w}} | {col_labels[0]:<{col_w}} | {col_labels[1]:<{col_w}}"
    print("Summary price table (USD):")
    print(header)
    print("-" * len(header))

    # Rows
    for r in row_order:
        with_cell = matrix[r]["with_SHA"]
        without_cell = matrix[r]["without_SHA"]
        with_str = f"${with_cell.total_price:.0f}" if with_cell else "-"
        without_str = f"${without_cell.total_price:.0f}" if without_cell else "-"
        print(f"{r:<{row_w}} | {with_str:<{col_w}} | {without_str:<{col_w}}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate multi-city Asia itineraries from NYC for Dec 2025 with HK NYE anchor.\n"
            "Provide a CSV of cheapest nonstops by date."
        )
    )
    parser.add_argument("--csv", dest="csv_path", required=False, help="Path to flights CSV")
    parser.add_argument("--write-template", dest="template_path", help="Write a CSV template to this path and exit")
    parser.add_argument("--top", type=int, default=10, help="Show top N results (default 10)")
    parser.add_argument(
        "--window",
        choices=["early", "mid", "late"],
        help="Only evaluate itineraries starting in this departure window",
    )
    parser.add_argument(
        "--include-shanghai",
        action="store_true",
        help="Only evaluate itineraries that include Shanghai (SHA)",
    )
    parser.add_argument(
        "--exclude-shanghai",
        action="store_true",
        help="Only evaluate itineraries that exclude Shanghai",
    )
    parser.add_argument(
        "--summary-table",
        action="store_true",
        help=(
            "Print a matrix of cheapest prices (rows: windows; columns: with/without SHA) "
            "and then print the itineraries included in that matrix"
        ),
    )
    args = parser.parse_args()

    if args.template_path:
        write_csv_template(args.template_path)
        print(f"Wrote CSV template to {args.template_path}")
        return

    if not args.csv_path:
        print("Error: --csv path to flights CSV is required unless using --write-template.")
        return

    flights = parse_csv(args.csv_path)
    store = FlightStore(flights)
    windows = departure_windows_dec_2025()
    if args.window:
        # Filter to a single requested window
        win = args.window
        if win in windows:
            windows = {win: windows[win]}

    if args.summary_table:
        # Build and print summary matrix
        row_order, matrix = build_summary_matrix(
            store,
            windows=windows,
            flex_days=1,
            min_total_days=16,
            max_total_days=25,
        )
        print_summary_price_table(row_order, matrix)

        # Gather the itineraries present in the table (ordered by rows, with then without)
        selected: List[ItineraryResult] = []
        for r in row_order:
            cell_with = matrix[r]["with_SHA"]
            cell_without = matrix[r]["without_SHA"]
            if cell_with is not None:
                selected.append(cell_with)
            if cell_without is not None:
                selected.append(cell_without)

        print("")
        if selected:
            print("Itineraries in summary table:")
            print("")
            print_results(selected)
        else:
            print("No valid itineraries found for the requested windows.")
        return

    # Default behavior: compute global top N across both include/exclude Shanghai sets
    results: List[ItineraryResult] = []
    if not args.exclude_shanghai:
        results += build_itineraries(
            store,
            include_shanghai=True,
            windows=windows,
            top_k=args.top,
        )
    if not args.include_shanghai:
        results += build_itineraries(
            store,
            include_shanghai=False,
            windows=windows,
            top_k=args.top,
        )

    # Keep global top N across both groups
    results.sort(key=lambda r: r.score_tuple())
    print_results(results[: args.top])


if __name__ == "__main__":
    main()



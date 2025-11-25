#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

import requests

from fluvius_fetch_token import FluviusAuthError, get_bearer_token_http

try:  # Python 3.9+
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - Windows without tzdata
    ZoneInfo = None  # type: ignore
    ZoneInfoNotFoundError = Exception  # type: ignore


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a Fluvius access token via the HTTP flow and download consumption data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--email", default=os.getenv("FLUVIUS_LOGIN"), help="Fluvius account email")
    parser.add_argument("--password", default=os.getenv("FLUVIUS_PASSWORD"), help="Fluvius account password")
    parser.add_argument("--ean", default=os.getenv("FLUVIUS_EAN"), help="EAN number for the meter")
    parser.add_argument("--meter-serial", default=os.getenv("FLUVIUS_METER_SERIAL"), help="Meter serial number")
    parser.add_argument("--days-back", type=int, default=7, help="How many days of history to request")
    parser.add_argument("--remember-me", action="store_true", help="Forward rememberMe flag during login")
    parser.add_argument(
        "--timezone",
        default=os.getenv("FLUVIUS_TIMEZONE", "Europe/Brussels"),
        help="IANA timezone used to build historyFrom/historyUntil (default: Europe/Brussels)",
    )
    parser.add_argument(
        "--granularity",
        default=os.getenv("FLUVIUS_GRANULARITY", "4"),
        help="Fluvius API granularity value (3=quarter-hour, 4=daily).",
    )
    parser.add_argument(
        "--bearer-token",
        help="Skip authentication and reuse an existing Bearer token (with or without the 'Bearer ' prefix).",
    )
    parser.add_argument("--output", default="fluvius_consumption_data.json", help="Path to store the raw JSON response")
    parser.add_argument("--quiet", action="store_true", help="Reduce log noise while fetching the token")

    args = parser.parse_args()
    if not args.bearer_token:
        if not args.email:
            parser.error("Missing --email (or FLUVIUS_LOGIN)")
        if not args.password:
            parser.error("Missing --password (or FLUVIUS_PASSWORD)")
    if not args.ean:
        parser.error("Missing --ean (or FLUVIUS_EAN)")
    if not args.meter_serial:
        parser.error("Missing --meter-serial (or FLUVIUS_METER_SERIAL)")
    return args


def _strip_bearer_prefix(token: str) -> str:
    lowered = token.strip()
    if lowered.lower().startswith("bearer "):
        return lowered.split(" ", 1)[1]
    return lowered


def request_access_token(args: argparse.Namespace) -> str:
    if args.bearer_token:
        return _strip_bearer_prefix(args.bearer_token)

    access_token, _ = get_bearer_token_http(
        args.email,
        args.password,
        remember_me=args.remember_me,
        verbose=not args.quiet,
    )
    return access_token


def _resolve_timezone(name: Optional[str]):
    if name and ZoneInfo is not None:
        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            print(f"Warning: timezone '{name}' not found, falling back to system local timezone.")
    local = datetime.now().astimezone().tzinfo
    if local:
        return local
    return timezone.utc


def _build_history_range(days_back: int, tz_name: Optional[str]) -> Dict[str, str]:
    tzinfo = _resolve_timezone(tz_name)
    local_now = datetime.now(tzinfo)
    start_date = (local_now - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = local_now.replace(hour=23, minute=59, second=59, microsecond=999000)
    return {
        "historyFrom": start_date.isoformat(timespec="milliseconds"),
        "historyUntil": end_date.isoformat(timespec="milliseconds"),
    }


def get_consumption_data(
    access_token: str,
    ean: str,
    meter_serial: str,
    days_back: int = 7,
    tz_name: Optional[str] = "Europe/Brussels",
    granularity: str = "4",
) -> Optional[List[Dict[str, Any]]]:
    date_range = _build_history_range(days_back, tz_name)

    url = f"https://mijn.fluvius.be/verbruik/api/meter-measurement-history/{ean}"
    params = {
        **date_range,
        "granularity": str(granularity),
        "asServiceProvider": "false",
        "meterSerialNumber": meter_serial,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    print(
        f"Getting {days_back} days of consumption data (granularity={params['granularity']}, tz={date_range['historyFrom'][-6:]})..."
    )
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"API call failed: {exc}")
        return None

    try:
        data = response.json()
    except ValueError as exc:
        print(f"Failed to parse JSON response: {exc}")
        return None

    print(f"Successfully retrieved {len(data)} days of data")
    return data


def analyze_consumption_data(data: Iterable[Dict[str, Any]]) -> None:
    sample = list(data)
    if not sample:
        print("No data to analyze")
        return

    print("\nCONSUMPTION ANALYSIS:")
    print("=" * 50)
    print(f"Period: {len(sample)} days")

    for day_idx, day_data in enumerate(sample):
        date = day_data.get("d", "Unknown date")
        values = day_data.get("v", [])
        
        # Calculate effective date (Belgium time)
        # API returns 23:00Z of previous day, which is 00:00 of the target day in BE
        display_header = date
        try:
            if date.endswith("Z"):
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                # Adding 1 hour is enough to push 23:00Z to the next day (00:00)
                effective_date = dt + timedelta(hours=1)
                date_str = effective_date.strftime("%Y-%m-%d")
                weekday = effective_date.strftime("%A")
                display_header = f"{date_str} ({weekday})"
        except ValueError:
            pass

        print(f"\n📅 Day {day_idx + 1}: {display_header}")
        if display_header != date:
            print(f"   (Raw start time: {date})")

        day_consumption = 0.0
        day_injection = 0.0
        for reading in values:
            dc_val = reading.get("dc", 0)
            t_val = reading.get("t", 0)
            value = float(reading.get("v", 0))
            
            # Mapping based on user observation:
            # t=1 => Consumption, t=2 => Injection
            # dc=1 => High tariff, dc=2 => Low tariff
            tariff_name = "High" if dc_val == 1 else "Low"

            if t_val == 1:
                day_consumption += value
                print(f"   Consumption ({tariff_name}): {value:.3f} kWh")
            elif t_val == 2:
                day_injection += value
                print(f"   Injection ({tariff_name}): {value:.3f} kWh")

        net_consumption = day_consumption - day_injection
        print(f"   Total consumption: {day_consumption:.3f} kWh")
        print(f"   Total injection: {day_injection:.3f} kWh")
        print(f"   Net consumption: {net_consumption:.3f} kWh")


def main() -> int:
    args = _parse_args()

    try:
        access_token = request_access_token(args)
    except FluviusAuthError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Network error while fetching token: {exc}", file=sys.stderr)
        return 1

    print("Authentication successful")

    data = get_consumption_data(
        access_token,
        args.ean,
        args.meter_serial,
        args.days_back,
        args.timezone,
        args.granularity,
    )
    if not data:
        return 1

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    print(f"Raw data saved to {args.output}")

    analyze_consumption_data(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

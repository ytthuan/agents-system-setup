#!/usr/bin/env python3
"""Check tool catalog source URL freshness without scraping tool names.

v1.8.0 intentionally ships a static, reviewable per-runtime tool catalog plus
emit-time and read-only audit discipline. Live upstream tool-name scraping is
explicitly deferred to v1.9.0, where each runtime can have parser robustness and
human review gates.

Verifies:
  - Each source_url returns HTTP 2xx/3xx within timeout.
  - Each last_verified date is no older than --max-age-days.

This script DOES NOT scrape tool names from upstream docs.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT_SEC = 15
DEFAULT_MAX_AGE_DAYS = 90


def head_url(url: str, timeout: int = DEFAULT_TIMEOUT_SEC) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "agents-system-setup-freshness/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, "ok"
    except Exception:
        try:
            req2 = urllib.request.Request(
                url,
                method="GET",
                headers={"User-Agent": "agents-system-setup-freshness/1.0"},
            )
            with urllib.request.urlopen(req2, timeout=timeout) as resp:
                return resp.status, "ok-via-get"
        except Exception as e2:
            return 0, f"error: {e2}"


def collect_last_verified(block: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    dates: list[str] = []
    for item in block.get("tools", []):
        if item.get("last_verified"):
            dates.append(item["last_verified"])
    for item in block.get("permission_keys", []):
        if item.get("last_verified"):
            dates.append(item["last_verified"])
    if not dates and catalog.get("last_updated"):
        dates.append(catalog["last_updated"])
    return dates


def parse_age_days(today: date, dates: list[str]) -> int | None:
    if not dates:
        return None
    try:
        youngest = max(datetime.strptime(value, "%Y-%m-%d").date() for value in dates)
    except ValueError:
        return None
    return (today - youngest).days


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="CI mode: exit non-zero on stale/dead URLs")
    ap.add_argument("--report", action="store_true", help="Report mode (default)")
    ap.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    ap.add_argument(
        "--catalog-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "plugins/agents-system-setup/skills/agents-system-setup/assets/tool-catalog.json",
    )
    args = ap.parse_args()

    if not args.catalog_path.exists():
        print(f"ERROR: catalog not found at {args.catalog_path}", file=sys.stderr)
        return 3

    catalog = json.loads(args.catalog_path.read_text())
    today = date.today()
    threshold = args.max_age_days

    stale: list[tuple[str, str, int]] = []
    dead: list[tuple[str, str, str]] = []
    ok: list[tuple[str, str, int | str]] = []

    for runtime_id, block in catalog.get("runtimes", {}).items():
        url = block.get("source_url")
        if not url:
            continue

        age = parse_age_days(today, collect_last_verified(block, catalog))
        status, msg = head_url(url)
        is_ok = bool(status and 200 <= status < 400)
        is_stale = age is not None and age > threshold

        if not is_ok:
            dead.append((runtime_id, url, msg))
        elif is_stale:
            stale.append((runtime_id, url, age if age is not None else -1))
        else:
            ok.append((runtime_id, url, age if age is not None else "n/a"))

    print(f"Tool catalog freshness report ({today}; threshold={threshold} days)")
    print(f"  Catalog: {args.catalog_path}")
    print(f"  OK     ({len(ok)}): {[runtime for runtime, _, _ in ok]}")
    print(f"  Stale  ({len(stale)}): {[(runtime, age) for runtime, _, age in stale]}")
    print(f"  Dead   ({len(dead)}): {[(runtime, msg) for runtime, _, msg in dead]}")

    if args.check:
        if dead:
            return 2
        if stale:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

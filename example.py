"""Which companies on a list are running Google ads right now, and which ads they keep running longest.

Usage:
    python example.py allbirds.com gymshark.com --region US
    python example.py --file domains.txt --days 7
    python example.py --from-json sample.json          # offline, no token, no cost

Calls the Apify actor rel8ble/google-ads-transparency-scraper (paid: $0.045 per 1,000 ads,
no start fee). Writes google_ads.csv and prints a per-advertiser summary.
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

ACTOR = "rel8ble/google-ads-transparency-scraper"
FIELDS = ["query", "advertiserName", "advertiserId", "creativeId", "format",
          "firstShown", "lastShown", "daysShown", "adUrl", "imageUrl", "previewUrl"]


def fetch(queries, region, fmt, max_ads):
    from apify_client import ApifyClient

    token = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
    client = ApifyClient(token)
    run = client.actor(ACTOR).call(run_input={
        "queries": queries,
        "region": region,
        "format": fmt,
        "maxAdsPerQuery": max_ads,
    })
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("queries", nargs="*", help="domains, advertiser names, AR... IDs or Transparency URLs")
    p.add_argument("--file", help="one query per line")
    p.add_argument("--region", default="anywhere", help='two-letter country, e.g. US, or "anywhere"')
    p.add_argument("--format", default="all", choices=["all", "text", "image", "video"])
    p.add_argument("--max-ads", type=int, default=100, help="ads per query (1 ad = 1 billed result)")
    p.add_argument("--days", type=int, default=7, help='"running now" = last shown within this many days')
    p.add_argument("--from-json", help="read rows from a saved dataset instead of calling the actor")
    a = p.parse_args()

    if a.from_json:
        with open(a.from_json, encoding="utf-8") as f:
            ads = json.load(f)
    else:
        queries = list(a.queries)
        if a.file:
            with open(a.file, encoding="utf-8") as f:
                queries += [line.strip() for line in f if line.strip()]
        if not queries:
            p.error("give at least one query, --file or --from-json")
        ads = fetch(queries, a.region, a.format, a.max_ads)

    with open("google_ads.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(ads)
    print(f"{len(ads)} ads -> google_ads.csv\n")

    # "Now" = the newest scrape time in the data, so offline runs on old samples still make sense.
    now = max((parse(ad.get("scrapedAt")) for ad in ads if ad.get("scrapedAt")), default=datetime.now(timezone.utc))
    cutoff = now - timedelta(days=a.days)

    by_query = defaultdict(list)
    for ad in ads:
        by_query[ad.get("query") or ad.get("advertiserName")].append(ad)

    print(f"{'query':<28} {'ads':>4} {'live':>5} {'formats':<26} longest-running")
    for q, rows in sorted(by_query.items(), key=lambda kv: -len(kv[1])):
        live = [r for r in rows if parse(r.get("lastShown")) and parse(r["lastShown"]) >= cutoff]
        formats = ", ".join(f"{k} {v}" for k, v in Counter(r.get("format") for r in rows).most_common())
        top = max(rows, key=lambda r: r.get("daysShown") or 0)
        print(f"{q[:28]:<28} {len(rows):>4} {len(live):>5} {formats[:26]:<26} "
              f"{top.get('daysShown')}d {top.get('format')} since {str(top.get('firstShown'))[:10]}")

    running = [q for q, rows in by_query.items()
               if any(parse(r.get("lastShown")) and parse(r["lastShown"]) >= cutoff for r in rows)]
    print(f"\nRunning Google ads in the last {a.days} days: {len(running)} of {len(by_query)} queries")
    for q in running:
        print("  ", q)


if __name__ == "__main__":
    main()

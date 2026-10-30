"""Log new Indeed listings for a search, each one once.

    python new_listings.py "data engineer" --location "New York" --country us

Asks for the listings posted in the last --days days, skips the job keys that
are already in the CSV and appends the rest with a UTC timestamp, so the file
grows into a log of new openings. Run it every morning from cron:

    0 7 * * *  cd /path/to/here && python new_listings.py "data engineer" --location "New York"

Needs a login (`indeed-scraper login`) or QUANTICDATA_API_KEY in the environment.
"""

import argparse
import csv
import os
from datetime import datetime, timezone

from quanticdata_indeed_scraper import IndeedScraper

FIELDS = ["found_at", "job_key", "posted_at", "title", "company", "location", "salary_text",
          "remote", "easy_apply", "urgently_hiring", "link"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", help="role or keywords")
    parser.add_argument("--location", help="city, state or postcode")
    parser.add_argument("--country", default="us", help="Indeed site, as an ISO country code")
    parser.add_argument("--days", type=int, default=3, help="only listings posted in the last N days (1-30)")
    parser.add_argument("--max", type=int, default=100, help="listings to check per run (max 300)")
    parser.add_argument("--out", default="new_listings.csv")
    args = parser.parse_args()

    new_file = not os.path.exists(args.out)
    seen = set()
    if not new_file:
        with open(args.out, newline="", encoding="utf-8") as fh:
            seen = {row["job_key"] for row in csv.DictReader(fh)}

    indeed = IndeedScraper()
    run = indeed.jobs(args.query, location=args.location, country=args.country,
                      posted_within_days=args.days, max_results=args.max)
    found_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fresh = [job for job in run if job["job_key"] not in seen]

    with open(args.out, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        for job in fresh:
            writer.writerow({"found_at": found_at, **job})
    print(f"{len(run)} listings checked, {len(fresh)} new, appended to {args.out}")


if __name__ == "__main__":
    main()

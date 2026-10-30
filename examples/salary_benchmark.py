"""Advertised salary ranges for one role across several cities, from Indeed.

    python salary_benchmark.py "data engineer" --cities "New York" "Austin" "Chicago" --country us

Keeps the listings that state a yearly salary, writes them to salaries.csv
(each with the city that found it) and prints, per city, how many listings
there were, how many state a salary, and the median low and high end of the
advertised range.
"""

import argparse
from statistics import median

from quanticdata_indeed_scraper import IndeedScraper, write


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("role")
    parser.add_argument("--cities", nargs="+", required=True)
    parser.add_argument("--country", default="us", help="Indeed site, as an ISO country code")
    parser.add_argument("--per-city", type=int, default=100, help="listings per city (max 300)")
    parser.add_argument("--out", default="salaries.csv")
    args = parser.parse_args()

    indeed = IndeedScraper()
    rows = []
    print(f"{'city':20} {'listings':>8} {'salary':>7} {'median low':>11} {'median high':>12}  currency")
    for city in args.cities:
        run = indeed.jobs(args.role, location=city, country=args.country, max_results=args.per_city)
        paid = [j for j in run if j.get("salary_period") == "yearly" and j.get("salary_min")]
        rows.extend({"search_city": city, **j} for j in paid)
        if not paid:
            print(f"{city:20} {len(run):8d} {0:7d}")
            continue
        low = median(j["salary_min"] for j in paid)
        high = median(j.get("salary_max") or j["salary_min"] for j in paid)
        currency = ", ".join(sorted({j.get("salary_currency") or "?" for j in paid}))
        print(f"{city:20} {len(run):8d} {len(paid):7d} {low:11,.0f} {high:12,.0f}  {currency}")

    write(rows, args.out)
    print(f"{len(rows)} listings with a yearly salary written to {args.out}")


if __name__ == "__main__":
    main()

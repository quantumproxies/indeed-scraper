"""Which employers post the most Indeed listings for a set of roles in one place.

    python hiring_companies.py --roles "data engineer" "data analyst" --location Chicago --country us

Listings are deduplicated by job key across roles. Writes employers.csv with
one row per employer: number of listings, the roles they hire for, their
Indeed rating and review count, and their Indeed company page.
"""

import argparse

from quanticdata_indeed_scraper import IndeedScraper, write


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--roles", nargs="+", required=True)
    parser.add_argument("--location", required=True, help="city, state or postcode")
    parser.add_argument("--country", default="us", help="Indeed site, as an ISO country code")
    parser.add_argument("--days", type=int, help="only listings posted in the last N days (1-30)")
    parser.add_argument("--per-role", type=int, default=150, help="listings per role (max 300)")
    parser.add_argument("--out", default="employers.csv")
    args = parser.parse_args()

    indeed = IndeedScraper()
    jobs = {}
    for role in args.roles:
        run = indeed.jobs(role, location=args.location, country=args.country,
                          posted_within_days=args.days, max_results=args.per_role)
        for job in run:
            jobs.setdefault(job["job_key"], {"role": role, **job})
        print(f"{role!r}: {len(run)} listings")

    employers = {}
    for job in jobs.values():
        name = job.get("company")
        if not name:
            continue
        e = employers.setdefault(name, {"company": name, "listings": 0, "roles": set(),
                                        "company_rating": job.get("company_rating"),
                                        "company_reviews": job.get("company_reviews"),
                                        "company_url": job.get("company_url")})
        e["listings"] += 1
        e["roles"].add(job["role"])

    rows = sorted(employers.values(), key=lambda e: -e["listings"])
    for e in rows:
        e["roles"] = sorted(e["roles"])
    write(rows, args.out)
    print(f"{len(jobs)} unique listings from {len(rows)} employers written to {args.out}")
    for e in rows[:10]:
        print(f"  {e['listings']:4d}  {e['company']}  (rating {e['company_rating'] or '-'})")


if __name__ == "__main__":
    main()

# Indeed Scraper

[![ci](https://github.com/quantumproxies/indeed-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/quantumproxies/indeed-scraper/actions/workflows/ci.yml) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

Scrape Indeed from Python or the command line: job listings for a role and a location, with the salary as Indeed prints it and as numbers (minimum, maximum, period, currency), benefits, schedules, remote model, employer rating and posting date, as JSON or CSV. The code is free and open source (MIT). It runs on the QuanticData Data API and reads public listings only, so there is no Indeed account, browser extension, proxy or headless browser involved: sign in to QuanticData once and run a command. The same collector works from Claude or any MCP client, and from n8n.

```bash
pip install git+https://github.com/quantumproxies/indeed-scraper
indeed-scraper login
indeed-scraper jobs "data engineer" --location "New York" --country us --max-results 50 -o jobs.csv
```

`login` opens the QuanticData sign-in page in your browser. New accounts get $2 of free usage every month, no card required: [create one](https://app.quanticdata.io/register?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper).

## What it scrapes

| Command | Input | Returns | Per run |
|---|---|---|---|
| `indeed-scraper jobs` | role, optional location | Title, company, location, salary range, benefits, posting date, 30 fields per row ([fields and price](https://quanticdata.io/collectors/indeed-jobs-api/?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper)) | up to 300 |

`--country` picks the local Indeed site (default `us`): `indeed-scraper jobs "sviluppatore backend" --location Milano --country it` searches the Italian one. Narrow the listings with `--location` (city, state or postcode) and `--posted-within-days` (1 to 30). Every salary comes back twice: as Indeed prints it (`salary_text`) and as numbers in `salary_min`, `salary_max`, `salary_period` and `salary_currency`.

## Sample output

A real row from `indeed-scraper jobs "data engineer" --location "New York" --country us --max-results 3` (2026-10-23):

```json
{
  "city": "New York",
  "link": "https://www.indeed.com/viewjob?jk=497fe5a6dfd14dec",
  "rank": 1,
  "state": "NY",
  "title": "Data Engineer",
  "posted": "30+ days ago",
  "remote": "REMOTE_HYBRID",
  "salary": "115000 - 130000 yearly",
  "company": "TheGuarantors",
  "job_key": "497fe5a6dfd14dec",
  "new_job": false,
  "snippet": "Collaboration: Collaborate with cross-functional teams including data analysts, data scientists, and business stakeholders to understand data requirements and…",
  "benefits": [
    "Health savings account",
    "Dental insurance",
    "401(k)",
    "Flexible spending account",
    "Disability insurance",
    "Vision insurance",
    "Parental leave",
    "Health insurance",
    "Paid parental leave",
    "Flexible schedule",
    "Paid time off"
  ],
  "location": "New York, NY 10007",
  "job_types": [
    "Full-time"
  ],
  "posted_at": "2026-08-25",
  "schedules": [],
  "sponsored": false,
  "easy_apply": true,
  "salary_max": 130000,
  "salary_min": 115000,
  "company_url": "https://www.indeed.com/cmp/Theguarantors",
  "postal_code": "10007",
  "salary_text": "$115,000 - $130,000 a year",
  "requirements": [],
  "salary_period": "yearly",
  "company_rating": 2.8,
  "company_reviews": 4,
  "salary_currency": "USD",
  "urgently_hiring": false
}
```

## Python

```python
from quanticdata_indeed_scraper import IndeedScraper

indeed = IndeedScraper()  # saved login, or QUANTICDATA_API_KEY

jobs = indeed.jobs("data engineer", location="New York", country="us", max_results=50)
for j in jobs:
    print(j["posted_at"], j["company"], j["salary_text"], j["title"])
jobs.to_csv("data_engineer_jobs.csv")

recent = indeed.jobs("sviluppatore backend", location="Milano", country="it", posted_within_days=14)
yearly = [j for j in recent if j["salary_period"] == "yearly"]
print(len(recent), "listings,", len(yearly), "with a yearly salary")
```

Each call returns a `Run`: iterate it for the rows (plain dicts), take `len()`, or save it with `to_csv()`, `to_json()`, `to_jsonl()` or `to_dataframe()` (pandas). Errors are specific: `InsufficientCredit`, `RateLimited`, `InvalidInput`, `JobFailed`, `AuthError`.

## Examples

- **Salary benchmarks**: Run one role in several cities and get the median advertised salary range per city, computed from the numeric salary fields, plus a CSV of every listing behind it. See [`examples/salary_benchmark.py`](examples/salary_benchmark.py).
- **New-listing log**: Check a search every morning and append only the listings you have not seen before, keyed by Indeed's job key, to one growing CSV. See [`examples/new_listings.py`](examples/new_listings.py).
- **Who is hiring**: Count the listings per employer for a few roles in one location, with each employer's Indeed rating, review count and company page. See [`examples/hiring_companies.py`](examples/hiring_companies.py).

## Command line

Results print as a table; `-o file.csv`, `-o file.json` or `-o file.jsonl` writes a file. List inputs take `a b c`, `a,b,c`, `@file.txt` (one per line) or `-` (stdin). `--no-wait` starts a long run in the background and prints its id; `indeed-scraper run <id> -o out.csv` collects it later.

### `indeed-scraper jobs`

Indeed job listings for a role and a location, with structured salary ranges, from the Indeed site of the country you pick.

```
indeed-scraper jobs QUERY [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `QUERY` | string |  | Job title or keywords, e.g. "data engineer". |
| `--location` | string |  | City, state or postcode, e.g. "New York". |
| `--posted-within-days` | integer |  | Only listings posted in the last N days (1–30). |
| `--country` | string |  | Which Indeed site to search, as an ISO country code: us (default) or another market's code, e.g. it for Italy. |
| `--max-results` | integer | `25` | How many jobs to deliver at most (1–300). You pay only for delivered jobs. |

## Output fields

<details><summary><code>indeed-scraper jobs</code>: 30 fields</summary>

| Field | Type | Description |
|---|---|---|
| `rank` | integer | 1-based position across pages. |
| `job_key` | string | Indeed job key (dedupe key). |
| `title` | string | Job title. |
| `company` | string or null | Employer. |
| `location` | string or null | Location as shown. |
| `remote` | string or null | Remote model (REMOTE, REMOTE_HYBRID…). |
| `salary` | string or null | Salary as a readable string. |
| `salary_min` | number or null | Salary range minimum. |
| `salary_max` | number or null | Salary range maximum. |
| `salary_period` | string or null | yearly / monthly / hourly. |
| `job_types` | string[] | Employment types when tagged. |
| `posted` | string or null | Posting age ("11 days ago"). |
| `snippet` | string or null | Listing summary, HTML stripped. |
| `company_rating` | number or null | Employer rating on Indeed. |
| `company_reviews` | integer or null | Employer review count. |
| `sponsored` | boolean | True for paid placements. |
| `link` | string | Listing URL. |
| `posted_at` | string or null | Publication date (YYYY-MM-DD). |
| `salary_text` | string or null | Salary as Indeed prints it ("$175,000 - $260,000 a year"). |
| `salary_currency` | string or null | ISO currency of the salary (USD, EUR, GBP…). |
| `city` | string or null | Job city. |
| `state` | string or null | State / region code. |
| `postal_code` | string or null | Postal code when the listing states one. |
| `benefits` | string[] | Benefits the employer tagged (health insurance, 401(k), paid time off…). |
| `schedules` | string[] | Schedule and shift tags (Monday to Friday, 8 hour shift…). |
| `requirements` | string[] | Skills and requirements listed on the card (SQL, Python, AWS…). |
| `company_url` | string or null | Employer page on Indeed. |
| `easy_apply` | boolean | True when the listing accepts an application on Indeed. |
| `urgently_hiring` | boolean | True when the employer marked the role as urgent. |
| `new_job` | boolean | True when Indeed flags the listing as new. |

</details>

## Sign-in and API keys

- `indeed-scraper login` signs you in with OAuth 2.1 and PKCE in the browser. The token is stored in `~/.config/quanticdata/credentials.json` (readable only by you) and refreshed automatically. One login serves every QuanticData tool on the machine.
- No browser on the machine (SSH, Docker, Colab): run `indeed-scraper login --no-browser`, open the link anywhere, then paste back the address the browser ends on.
- Scripts and CI: set `QUANTICDATA_API_KEY` to a key from the dashboard, or store one with `indeed-scraper login --api-key`.
- `indeed-scraper logout` revokes the token. The connection is listed under API keys in the dashboard as "API · QuanticData CLI"; deleting that key disconnects every machine that uses it.

## Pricing

The code is free and MIT-licensed. Runs are billed to your QuanticData account per delivered row, at the price shown on each collector page linked above; $2 of usage is free every month and failed runs are never billed. Plans with higher limits: [pricing](https://quanticdata.io/pricing/?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper).

## Other ways to call it

The same data over plain HTTP:

```bash
curl -X POST https://api.quanticdata.io/v1/scraper/collectors/indeed_jobs/run \
  -H "Authorization: Bearer $QUANTICDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"query": "data engineer", "location": "New York", "country": "us", "max_results": 3}}'
```

- [API reference](https://quanticdata.io/docs/?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper) with Python, Node, PHP and curl examples.
- [MCP server](https://quanticdata.io/mcp-server/?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper) to give Claude, Cursor or any MCP client the same tools.
- [n8n node](https://github.com/quantumproxies/n8n-nodes-quanticdata) for no-code workflows.

## FAQ

**Is this Indeed scraper free?**

The code is free and MIT-licensed. Scraping runs on your QuanticData account: $2 of usage is free every month with no card, then you pay per delivered row at the price shown on each collector page. Failed runs are never billed.

**Do I need proxies or a headless browser?**

No. You send a role and a location and get rows back; the requests run on QuanticData's side. There is no browser extension to install and no Indeed account to connect: it reads the public listings anyone can open.

**Does it work outside the US?**

Yes. --country picks the local Indeed site (default us); --country it with --location Milano searches the Italian one, for example. salary_currency tells you the currency of each salary.

**How many jobs can one run return?**

Up to 300 job listings per run; ask for fewer with --max-results and you pay only for what is delivered.

**Can I export to CSV or Excel?**

Add -o results.csv (or .json, .jsonl). Lists such as benefits, schedules and requirements are joined with '; ', so the CSV opens cleanly in Excel or Google Sheets.

**Can I run it on a schedule?**

Yes. Set QUANTICDATA_API_KEY in the environment and call the CLI or examples/new_listings.py from cron, GitHub Actions or any scheduler.

## Related scrapers

- [LinkedIn Scraper](https://github.com/quantumproxies/linkedin-scraper): LinkedIn scraper for Python and the command line.
- [Wellfound Scraper](https://github.com/quantumproxies/wellfound-scraper): Wellfound scraper for Python and the command line.
- [Google SERP API](https://github.com/quantumproxies/google-serp-api): Google SERP API for Python and the command line.

## License

MIT. Built and maintained by [QuanticData](https://quanticdata.io/?utm_source=github&utm_medium=readme&utm_campaign=indeed-scraper).

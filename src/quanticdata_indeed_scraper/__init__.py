"""Indeed Scraper: Indeed scraper for Python and the command line: job listings for a role and location with structured salary ranges, benefits, employer rating and posting date, as JSON or CSV. Free and open source; sign in with your QuanticData account, no browser extension, proxies or headless browser to run.

    from quanticdata_indeed_scraper import IndeedScraper

    scraper = IndeedScraper()   # saved login (`indeed-scraper login`) or QUANTICDATA_API_KEY
    run = scraper.jobs(...)   # Indeed job listings for a role and location
"""

from typing import Any, Dict, Optional, Sequence, Union

from ._qd.client import Client, Run
from ._qd.errors import (APIError, AuthError, InsufficientCredit, InvalidInput, JobFailed, JobTimeout,
                         QuanticDataError, RateLimited)
from ._qd.output import write

__version__ = "0.1.0"
__all__ = ["IndeedScraper", "Run", "write", "APIError", "AuthError", "InsufficientCredit", "InvalidInput",
           "JobFailed", "JobTimeout", "QuanticDataError", "RateLimited", "__version__"]


def _as_list(value: Any) -> Any:
    if value is None or isinstance(value, (list, tuple)):
        return list(value) if value is not None else None
    return [value]


class IndeedScraper:
    """Indeed Scraper on the QuanticData Data API.

    Every method runs one collector and returns a :class:`Run`: iterate it for the
    rows (plain dicts, typed in ``types``), or save it with ``to_csv()``,
    ``to_json()``, ``to_jsonl()`` or ``to_dataframe()``.
    """

    def __init__(self, api_key: Optional[str] = None, *, timeout: float = 180.0) -> None:
        self.client = Client(api_key, user_agent="indeed-scraper/0.1.0 (+https://github.com/quantumproxies/indeed-scraper)", timeout=timeout)

    def jobs(
        self, query: str,
        *,
        location: Optional[str] = None,
        posted_within_days: Optional[int] = None,
        country: Optional[str] = None,
        max_results: Optional[int] = None,
        wait: bool = True,
        timeout: float = 900.0,
    ) -> Run:
        """Indeed job listings for a role and a location, with structured salary ranges, from the Indeed site of the country you pick.

        Args:
            query: Job title or keywords, e.g. "data engineer".
            location: City, state or postcode, e.g. "New York".
            posted_within_days: Only listings posted in the last N days (1–30).
            country: Which Indeed site to search, as an ISO country code: us (default) or another market's code, e.g. it for Italy.
            max_results: How many jobs to deliver at most (1–300). You pay only for delivered jobs.
            wait: False starts the run in the background and returns its id at once.
            timeout: seconds to wait for a background run before giving up.

        Returns up to 300 rows, one per job: see ``types.IndeedJobsRow``.
        """
        payload = {
            "query": query,
            "location": location,
            "posted_within_days": posted_within_days,
            "country": country,
            "max_results": max_results,
        }
        return self.client.run_collector("indeed_jobs", payload, wait=wait, timeout=timeout)

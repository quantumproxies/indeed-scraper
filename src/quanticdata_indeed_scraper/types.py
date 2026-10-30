"""Row types of each command, for editors and type checkers (rows are plain dicts)."""

from typing import Any, Dict, List, Optional

try:  # Python 3.8+
    from typing import TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict  # type: ignore


class IndeedJobsRow(TypedDict, total=False):
    """One row of `indeed-scraper jobs` (indeed_jobs v1.1.1)."""

    rank: int
    """1-based position across pages."""
    job_key: str
    """Indeed job key (dedupe key)."""
    title: str
    """Job title."""
    company: Optional[str]
    """Employer."""
    location: Optional[str]
    """Location as shown."""
    remote: Optional[str]
    """Remote model (REMOTE, REMOTE_HYBRID…)."""
    salary: Optional[str]
    """Salary as a readable string."""
    salary_min: Optional[float]
    """Salary range minimum."""
    salary_max: Optional[float]
    """Salary range maximum."""
    salary_period: Optional[str]
    """yearly / monthly / hourly."""
    job_types: List[str]
    """Employment types when tagged."""
    posted: Optional[str]
    """Posting age ("11 days ago")."""
    snippet: Optional[str]
    """Listing summary, HTML stripped."""
    company_rating: Optional[float]
    """Employer rating on Indeed."""
    company_reviews: Optional[int]
    """Employer review count."""
    sponsored: bool
    """True for paid placements."""
    link: str
    """Listing URL."""
    posted_at: Optional[str]
    """Publication date (YYYY-MM-DD)."""
    salary_text: Optional[str]
    """Salary as Indeed prints it ("$175,000 - $260,000 a year")."""
    salary_currency: Optional[str]
    """ISO currency of the salary (USD, EUR, GBP…)."""
    city: Optional[str]
    """Job city."""
    state: Optional[str]
    """State / region code."""
    postal_code: Optional[str]
    """Postal code when the listing states one."""
    benefits: List[str]
    """Benefits the employer tagged (health insurance, 401(k), paid time off…)."""
    schedules: List[str]
    """Schedule and shift tags (Monday to Friday, 8 hour shift…)."""
    requirements: List[str]
    """Skills and requirements listed on the card (SQL, Python, AWS…)."""
    company_url: Optional[str]
    """Employer page on Indeed."""
    easy_apply: bool
    """True when the listing accepts an application on Indeed."""
    urgently_hiring: bool
    """True when the employer marked the role as urgent."""
    new_job: bool
    """True when Indeed flags the listing as new."""

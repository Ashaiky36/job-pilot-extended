import hashlib      # for generating unique job IDs with hashing
import requests     # for making HTTP requests to fetch job postings
import feedparser   # for parsing RSS feeds
from datetime import datetime, timezone   # for handling date and time
from typing import List, Dict, Optional   # for type hinting
import time         # for adding delays between requests
import re     
import os  
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# All roles you are targeting
TARGET_KEYWORDS = [
    "data analyst", "data analysis",
    "data scientist", "data science",
    "data engineer", "data engineering",
    "machine learning engineer", "ml engineer",
    "ai engineer", "artificial intelligence engineer",
    "business analyst", "analytics",
    "nlp", "business intelligence", "bi developer",
    "deep learning engineer", "analytics engineer",
    "intern", "fresher", "entry level", "associate"
]

TARGET_LOCATIONS = ["India", "Remote"]

# Target company career pages to monitor
CAREER_PAGES = [
    {
        "company": "Zepto",
        "url": "https://zepto.com/careers",
        "job_selector": "a[href*='job']",
        "base_url": "https://zepto.com"
    },
    {
        "company": "Razorpay",
        "url": "https://razorpay.com/jobs/",
        "job_selector": "a[href*='job']",
        "base_url": "https://razorpay.com"
    },
    {
        "company": "CRED",
        "url": "https://careers.cred.club/",
        "job_selector": "a[href*='job']",
        "base_url": "https://careers.cred.club"
    },
    {
        "company": "Groww",
        "url": "https://groww.in/careers",
        "job_selector": "a[href*='job']",
        "base_url": "https://groww.in"
    },
    {
        "company": "PhonePe",
        "url": "https://www.phonepe.com/careers/",
        "job_selector": "a[href*='job']",
        "base_url": "https://www.phonepe.com"
    },
]

RELEVANT_TITLE_KEYWORDS = [
    "data analyst", "data analysis",
    "data scientist", "data science",
    "machine learning", "ml engineer",
    "ai engineer", "artificial intelligence",
    "business analyst", "analytics",
    "data engineer", "nlp", "deep learning",
    "computer vision", "research scientist",
    "quantitative analyst", "statistician",
    "business intelligence", "bi developer",
    "intern", "fresher", "entry level", "associate"
]

# function to generate a unique job ID based on the job URL
def make_job_id(url: str) -> str:
    """Creates unique hash for any job URL."""
    return hashlib.md5(url.encode()).hexdigest()    # Generate a unique hash for the job URL using MD5 hashing algorithm.

# Funtion to clean the html tags and clean whitespace
def clean_html(text: str) -> str:
    """Removes HTML tags, fixes encoding, cleans whitespace."""
    if not text:
        return ""
    
    # Fix encoding issues
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator=" ", strip=True)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # Remove non-printable characters but keep unicode
    clean = "".join(
        char for char in clean
        if char.isprintable() or char in "\n\t"
    )
    
    return clean

def is_relevant_job(title: str) -> bool:
    """
    Returns True if job title matches any target role keyword.
    Filters out Sales, Marketing, HR, Cybersecurity, etc.
    """
    
    title_lower = title.lower()
    return any(kw in title_lower for kw in RELEVANT_TITLE_KEYWORDS)
     
# ----- SOURCE 1: RemoteOK -----
# function to fetch job postings from remoteok
def fetch_remoteok(keywords: list = None) -> list:

    """Fetches job postings from remoteok.io public API based on keywords and optional location."""

    url = "https://remoteok.com/api"      # URL for the RemoteOK API
    headers = {"User-Agent": "Mozilla/5.0 JobPilot/1.0",
               "Accept": "application/json"
    }     # Set a custom User-Agent header to identify the request source

    try:
        time.sleep(2)       # RemoteOK requires delay
        response = requests.get(url, headers=headers, timeout=15)      # Make a GET request to the RemoteOK API
        response.raise_for_status()       # Raise an error for bad responses (4xx or 5xx)
        data = response.json()        # Parse the JSON response(for example, [{"position": "Python Developer", "company": "TechCorp", "location": "Remote", "url": "https://remoteok.io/remote-jobs/12345", "tags": ["Python", "Django"], "salary": "$80k-$100k", "job_type": "full-time"}, ...])

        # First item is a legal notice, skip it(for example, {"id": 0, "date": "2021-01-01", "legal": "RemoteOK is a job board for remote work."})
        job_raw = [item for item in data if isinstance(item, dict) and "position" in item]    # Filter out non-job items from the response

        jobs = []    # Initialize an empty list to store the fetched jobs

        for job in job_raw:
            # Filter jobs based on keywords if provided
            title = job.get("position", "").lower()    # Get the job title in lowercase for case-insensitive comparison
            tags = " ".join(job.get("tags", [])).lower()    # Join job tags into a single string in lowercase for comparison, for ex - "python django flask" for a job with tags ["Python", "Django", "Flask"]
            combined = f"{title} {tags}"    # Combine title and tags for relevance checking

            if not is_relevant_job(combined):
                    continue    # Skip jobs that don't match the keywords

            job_url = job.get("url", "")    # Get the job URL
            if not job_url:
                continue    # Skip jobs without a URL

            jobs.append({
                "job_id": make_job_id(job_url),    # Unique job ID
                "title": job.get("position", ""),    # Job title
                "company": job.get("company", ""),    # Company name
                "location": job.get("location", "Remote"),    # Job location
                "url": job_url,    # Job URL
                "description": clean_html(job.get("description", "")),    # Job description cleaned of HTML tags
                "source": "remoteok",   # Source of the job posting
                "posted_at": datetime.fromtimestamp(job.get("epoch", time.time()), tz = timezone.utc).isoformat(),    # Date posted in ISO format
                "fetched_at": datetime.now(timezone.utc).isoformat(),   # Date fetched in ISO format
                "salary_range": job.get("salary", ""),    # Salary range if available
                "job_type": job.get("job_type", "remote")     # Job type (e.g., full-time, part-time)
            })

        print(f"[RemoteOK] Fetched {len(jobs)} relevant jobs.")    # Log the number of jobs fetched
        return jobs    # Return the list of fetched jobs

    except Exception as e:
        print(f"[RemoteOK] Error fetching jobs: {e}")    # Log any errors that occur during the fetch process
        return []    # Return an empty list in case of an error

# ----- SOURCE 2: INDEED RSS FEED -----
# function to fetch job postings from indeed rss feed
def fetch_indeed_rss(
    query: str,     # search query for Indeed
    location: str = "India",     # Default location for job search
    days_back: int = 1       # Default number of days back for job search
) -> list[dict]:
    """
    Fetches jobs from Indeed RSS feed.
    Note: Indeed has restricted RSS for India - returns 0 often.
    Kept for completeness, will be replaced with Naukri.
    """
    rss_url = (
        f"https://www.indeed.com/rss?"      # Construct the RSS feed URL for Indeed based on the provided query, location, and days_back parameters
        f"q={query.replace(' ', '+')}"     # Replace spaces in the query with '+' for URL encoding
        f"&l={location.replace(' ', '+')}"      # Replace spaces in the location with '+' for URL encoding
        f"&fromage={days_back}"     # Filter jobs posted within the last 'days_back' days
        f"&sort=date"       # Sort the results by date to get the most recent job postings first
    )

    try:
        feed = feedparser.parse(rss_url)      # Parse the RSS feed using feedparser
        jobs = []    # Initialize an empty list to store the fetched jobs

        for entry in feed.entries:
            job_url = entry.get("link", "")    # Get the job URL from the RSS entry

            if not job_url:
                continue    # Skip entries without a job URL
            # Parse published date
            published = entry.get("published", "")    # Get the published date from the RSS entry
            try:
                from email.utils import parsedate_to_datetime        # Import function to parse date strings into datetime objects
                posted_at = parsedate_to_datetime(published).isoformat()       # Convert the published date to ISO format, or use the current time if not available

            except Exception:
                posted_at = datetime.now(timezone.utc).isoformat()    # Use current time if published date is invalid

            jobs.append({
                "job_id": make_job_id(job_url),        # Unique job ID
                "title": entry.get("title", ""),      # Job title from the RSS entry
                "company": entry.get('source', {}).get('title', 'Unknown'),        # Company name (author) from the RSS entry
                "location": location,       # Location is set to the provided location parameter
                "url": job_url,        # Job URL
                "description": clean_html(entry.get("summary", "")),      # Job description from the RSS entry
                "source": "indeed",       # Source of the job posting
                "posted_at": posted_at,     # Date posted in ISO format
                "fetched_at": datetime.now(timezone.utc).isoformat(),     # Date fetched in ISO format (current time)
                "salary_range": "",       # Salary range is not available in the RSS feed
                "job_type": "full-time"         # Job type is not available in the RSS feed
            })

        print(f"[Indeed] Fetched {len(jobs)} jobs for {query} in {location}.")    # Log the number of jobs fetched
        return jobs    # Return the list of fetched jobs

    except Exception as e:
        print(f"[Indeed] Error fetching jobs: {e}")    # Log any errors that occur during the fetch process
        return []    # Return an empty list in case of an error

# ----- SOURCE 3: ADZUNA API -----
# function to fetch jobs from adzuna API
def fetch_adzuna(query: str) -> list:    # search query for Adzuna
    
    """
    Fetches jobs from Adzuna API.
    Free API key at: https://developer.adzuna.com/
    """
    api_id = os.getenv("ADZUNA_APP_ID", "")
    api_key = os.getenv("ADZUNA_APP_KEY", "")

    if not api_id or not api_key:
        print("[Adzuna] No API credentials provided in .env, skipping")
        return []      # Return an empty list if API credentials are not provided

    url = (
        f"https://api.adzuna.com/v1/api/jobs/in/search/1"       
        f"?app_id={api_id}"
        f"&app_key={api_key}"
        f"&results_per_page=20"
        f"&what={query.replace(' ', '+')}"
        f"&sort_by=date"
        f"&max_days_old=1"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        jobs = [] 
        for job in data.get("results", []):
            job_url = job.get("redirect_url", "")
            if not job_url:
                continue

            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            salary = (
                f"₹{salary_min:,.0f} - ₹{salary_max:,.0f}"
                if salary_min and salary_max else ""
            )

            jobs.append({
                "job_id": make_job_id(job_url),
                "title": job.get("title", ""),
                "company": job.get("company", {}).get("display_name", ""),
                "location": job.get("location", {}).get("display_name", ""),
                "url": job_url,
                "description": clean_html(job.get("description", "")),
                "source": "adzuna",
                "posted_at": job.get("created", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "salary_range": salary,
                "job_type": job.get("contract_time", "full-time")
            })

            print(f"[Adzuna] '{query}': {len(jobs)} jobs")
            return jobs

    except Exception as e:
        print(f"[Adzuna] Error for '{query}': {e}")   
        return []

# ----- SOURCE 4: Wellfound (AngelList) -----
def fetch_wellfound(query: str = "data") -> list:
    """
    Wellfound RSS feed for startup jobs.
    Best source for startup and early-stage company roles.
    """
    url = (
        f"https://wellfound.com/jobs.rss?"
        f"roles%5B%5D={query.replace(' ', '+')}"
    )

    try:
        headres = {"User-Agent": "Mozilla/5.0 JobPilot/1.0"}
        feed = feedparser.parse(url, request_headers=headres)       
        jobs = []

        for entry in feed.entries:
            job_url = entry.get("link", "")
            if not job_url:
                continue

            title = entry.get("title", "")
            if not is_relevant_job(title):
                continue

            jobs.append({
                "job_id": make_job_id(job_url),
                "title": title,
                "company": entry.get("author", "Startup"),
                "location": "Remote/Startup",
                "url": job_url,
                "description": clean_html(entry.get("summary", "")),
                "source": "wellfound",
                "posted_at": entry.get("published", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "salary_range": "",
                "job_type": "full-time"
            })

        print(f"[Wellfound] '{query}': {len(jobs)} jobs")
        return jobs

    except Exception as e:
        print(f"[Wellfound] Error: {e}")
        return []

# ----- SOURCE 5: Internshala -----
def fetch_internshala(query: str = "data-analyst") -> list[dict]:
    """
    Scrapes Internshala for internships and entry-level jobs.
    Best source for fresher and internship opportunities.
    """
    slug = query.lower().replace(" ", "-")
    url = f"https://internshala.com/internships/{slug}-internship"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = []
        # Internshala internship cards
        cards = soup.find_all("div", class_="internship_meta")

        for card in cards[:10]:  # Limit to top 10
            title_tag = card.find("h3", class_="heading_4_5")
            company_tag = card.find("p", class_="company_name")
            link_tag = card.find("a", href=True)

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True) if company_tag else ""
            href = link_tag["href"]
            job_url = (
                f"https://internshala.com{href}"
                if href.startswith("/") else href
            )

            jobs.append({
                "job_id": make_job_id(job_url),
                "title": title,
                "company": company,
                "location": "India",
                "url": job_url,
                "description": f"{title} internship at {company}",
                "source": "internshala",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "salary_range": "",
                "job_type": "internship"
            })

        print(f"[Internshala] '{query}': {len(jobs)} internships")
        return jobs

    except Exception as e:
        print(f"[Internshala] Error: {e}")
        return []

# ----- SOURCE 6: LinkedIn Public Search -----
def fetch_linkedin_rss(
        query: str,
        location: str = "India"
) -> list:
    """
    LinkedIn public job search page scraper.
    No login required for basic results.
    """
    url = (
        f"https://www.linkedin.com/jobs/search?"
        f"keywords={query.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        f"&f_TPR=r86400"
        f"&position=1&pageNum=0"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = []
        # LinkedIn job cards
        job_cards = soup.find_all("div", class_="base-card")

        for card in job_cards[:10]:  # Limit to top 10
            title_tag = card.find("h3", class_="base-search-card__title")
            company_tag = card.find("h4", class_="base-search-card__subtitle-link")
            link_tag = card.find("a", class_="base-card__full-link")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = (
                company_tag.get_text(strip=True) if company_tag else ""
            )
            job_url = link_tag.get("href", "")

            if not job_url or not is_relevant_job(title):
                continue

            jobs.append({
                "job_id": make_job_id(job_url),
                "title": title,
                "company": company,
                "location": "India",
                "url": job_url,
                "description": f"{title} at {company} - {location}",
                "source": "linkedin",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "salary_range": "",
                "job_type": "full-time"
            })

        print(f"[LinkedIn] '{query}' in {location}: {len(jobs)} jobs")
        return jobs

    except Exception as e:
        print(f"[LinkedIn] Error: {e}")
        return []

# ----- SOURCE 7: Company Career Pages -----

def fetch_career_page(company_info: dict) -> list:
    """
    Scrapes a company's career page for job postings.
    Expects a dictionary with 'company', 'url', 'job_selector', and 'base_url'.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
    }


    try:
        response = requests.get(company_info["url"], headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = []
        links = soup.select(company_info["job_selector"])

        for link in links[:20]:  # Limit to top 20
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if not title or not href or len(title) < 5:
                continue

            if not is_relevant_job(title):
                continue

            if href.startswith("/"):
                job_url = f"{company_info['base_url']}{href}"
            elif href.startswith("http"):
                job_url = href
            else:
                continue

            jobs.append({
                "job_id": make_job_id(job_url),
                "title": title,
                "company": company_info["company"],
                "location": "India",
                "url": job_url,
                "description": f"{title} at {company_info['company']}",
                "source": f"careers_{company_info['company'].lower()}",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "salary_range": "",
                "job_type": "full-time"
            })

        print(
            f"[{company_info['company']}] "
            f"{len(jobs)} relevant jobs"
        )
        return jobs

    except Exception as e:
        print(f"[{company_info['company']}] Error: {e}")
        return []

# function to fetch all the jobs as listed above(main orchestrator function)
def fetch_all_jobs() -> list:
    """
    Fetches from all sources, deduplicates, filters by relevance.
    Returns clean list of unique relevant jobs.
    """

    print(f"\n{'='*50}")
    print("JOBPILOT - FETCHING JOBS FROM ALL SOURCES")
    print(f"{'='*50}")

    all_jobs = []       # Empty list which will store all the jobs fetched from the respected platforms.

    # 1. RemoteOK
    print("\n[1/7] RemoteOK")
    all_jobs.extend(fetch_remoteok(keywords=TARGET_KEYWORDS))
    time.sleep(2)       # Be polite between requests

    # 2. Indeed RSS (limited in India but kept for completeness)
    print("\n[2/7] Indeed RSS")
    for keyword in TARGET_KEYWORDS[:3]:     # Limit to avoid rate limiting
        for location in TARGET_LOCATIONS:
            all_jobs.extend(fetch_indeed_rss(
                query=keyword,
                location=location,
                days_back=1
            ))
            time.sleep(1)

    # 3. Adzuna - one call per keyword
    print("\n[3/7] Adzuna API")
    for keyword in TARGET_KEYWORDS[:5]:     # Limit to avoid rate limiting
        all_jobs.extend(fetch_adzuna(query=keyword))
        time.sleep(1)

    # 4. Wellfound
    print("\n[4/7] Wellfound")
    for query in ["data", "machine-learning", "ai"]:
        all_jobs.extend(fetch_wellfound(query=query))
        time.sleep(1)

    # 5. Internshala
    print("\n[5/7] Internshala")
    for query in [
        "data-analyst", "data-science",
        "machine-learning", "artificial-intelligence"
    ]:
        all_jobs.extend(fetch_internshala(query=query))
        time.sleep(2)

    # 6. LinkedIn
    print("\n[6/7] LinkedIn")
    for keyword in TARGET_KEYWORDS[:3]:
        all_jobs.extend(fetch_linkedin_rss(keyword, "India"))
        time.sleep(2)

    # 7. Career Pages
    print("\n[7/7] Company Career Pages")
    for company in CAREER_PAGES:
        all_jobs.extend(fetch_career_page(company))
        time.sleep(2)

    # Deduplicate by job_id hash
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["job_id"] not in seen:
            seen.add(job["job_id"])
            unique_jobs.append(job)

    # Filter by relevance AFTER deduplication
    relevant_jobs = [
        job for job in unique_jobs
        if is_relevant_job(job.get("title", ""))
    ]

    print(f"\n{'='*60}")
    print(f"Raw collected:       {len(all_jobs)}")
    print(f"After dedup:         {len(unique_jobs)}")
    print(f"Irrelevant removed:  {len(unique_jobs) - len(relevant_jobs)}")
    print(f"Final relevant jobs: {len(relevant_jobs)}")
    print(f"{'='*60}")

    return relevant_jobs

if __name__ == "__main__":
    jobs = fetch_all_jobs()

    print(f"\n{'='*50}")

    print("SAMPLE JOBS BY SOURCE:")
    
    print('='*50)

    sources_seen = set()
    for job in jobs:
        source = job["source"]
        if source not in sources_seen:
            sources_seen.add(source)
            print(f"\n--- {source.upper()} ---")
            print(f"Title:   {job['title']}")
            print(f"Company: {job['company']}")
            location = job['location'].encode(
                'ascii', errors='replace'
            ).decode()
            print(f"Location: {location}")
            print(f"URL:     {job['url'][:70]}...")
            desc = job.get('description', 'No description')[:150]
            print(f"Preview: {desc}...")
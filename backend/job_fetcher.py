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
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "ML engineer",
    "AI engineer",
    "business analyst",
    "data engineer",
    "NLP engineer",
    "deep learning engineer",
    "analytics engineer"
]

TARGET_LOCATIONS = ["India", "Remote"]

# function to generate a unique job ID based on the job URL
def make_job_id(url: str) -> str:
    """Creates unique hash for any job URL."""
    return hashlib.md5(url.encode()).hexdigest()    # Generate a unique hash for the job URL using MD5 hashing algorithm.

# Funtion to clean the html tags and clean whitespace
def clean_html(text: str) -> str:

    """Remove HTML tags and clean whitespace."""

    if not text:
        return ""
    
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator=" ", strip=True)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

# function to fetch job postings from remoteok
def fetch_remoteok(keywords: list[str] = None) -> list[dict]:

    """Fetches job postings from remoteok.io public API based on keywords and optional location."""

    url = "https://remoteok.com/api"      # URL for the RemoteOK API
    headers = {"User-Agent": "JobPilot/1.0 job-search-tool"}     # Set a custom User-Agent header to identify the request source

    try:
        response = requests.get(url, headers=headers, timeout=15)      # Make a GET request to the RemoteOK API
        response.raise_for_status()       # Raise an error for bad responses (4xx or 5xx)
        data = response.json()        # Parse the JSON response(for example, [{"position": "Python Developer", "company": "TechCorp", "location": "Remote", "url": "https://remoteok.io/remote-jobs/12345", "tags": ["Python", "Django"], "salary": "$80k-$100k", "job_type": "full-time"}, ...])

        # First item is a legal notice, skip it(for example, {"id": 0, "date": "2021-01-01", "legal": "RemoteOK is a job board for remote work."})
        job_raw = [item for item in data if isinstance(item, dict) and 'position' in item]    # Filter out non-job items from the response

        jobs = []    # Initialize an empty list to store the fetched jobs

        for job in job_raw:
            # Filter jobs based on keywords if provided
            title = job.get('position', '').lower()    # Get the job title in lowercase for case-insensitive comparison
            tags = " ".join(job.get('tags', [])).lower()    # Join job tags into a single string in lowerc ase for comparison, for ex - "python django flask" for a job with tags ["Python", "Django", "Flask"]
            text = f"{title} {tags}"    # Combine title and tags into a single string for keyword matching

            if keywords:        # If keywords are provided, filter jobs based on them
                if not any(kw.lower() in text for kw in keywords):
                    continue    # Skip jobs that don't match the keywords

            job_url = job.get('url', '')    # Get the job URL
            if not job_url:
                continue    # Skip jobs without a URL

            jobs.append({
                "job_id": make_job_id(job_url),    # Unique job ID
                "title": job.get('position', ''),    # Job title
                "company": job.get('company', ''),    # Company name
                "location": job.get('location', 'Remote'),    # Job location
                "url": job_url,    # Job URL
                "source": "remoteok",   # Source of the job posting
                "posted_at": datetime.fromtimestamp(job.get("epoch", time.time()), tz = timezone.utc).isoformat(),    # Date posted in ISO format
                "fetched_at": datetime.now(timezone.utc).isoformat(),   # Date fetched in ISO format
                "salary_range": job.get('salary', ''),    # Salary range if available
                "job_type": job.get('job_type', 'remote')     # Job type (e.g., full-time, part-time)
            })

        print(f"[RemoteOK] Fetched {len(jobs)} jobs.")    # Log the number of jobs fetched
        return jobs    # Return the list of fetched jobs

    except Exception as e:
        print(f"[RemoteOK] Error fetching jobs: {e}")    # Log any errors that occur during the fetch process
        return []    # Return an empty list in case of an error

# function to fetch job postings from indeed rss feed
def fetch_indeed_rss(
    query: str,     # search query for Indeed
    location: str = "India",     # Default location for job search
    days_back: int = 1       # Default number of days back for job search
) -> list[dict]:
    """
    Fetches jobs from Indeed RSS feed.
    No API key needed.
    """
    rss_url = (
        f"https://www.indeed.com/rss?"      # Construct the RSS feed URL for Indeed based on the provided query, location, and days_back parameters
        f"q={query.replace(' ', '+')}&"     # Replace spaces in the query with '+' for URL encoding
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

# function to fetch jobs from adzuna API
def fetch_adzuna(
    query: str,     # search query for Adzuna
    location: str = "India",     # Default location for job search
    page: int = 1
) -> list[dict]:
    
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
        f"&where={location.replace(' ', '+')}"
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
        print(f"[Adzuna] Error: {e}")   
        return []

# function to fetch all the jobs as listed above
def fetch_all_jobs() -> list[dict]:
    """
    Fetches from all sources and combines results.
    Deduplicates by job_id hash.
    """

    print(f"\n[Fetcher] Starting job fetch for {len(TARGET_KEYWORDS)} roles")
    print(f"[Fetcher] Locations: {TARGET_LOCATIONS}")
    print("-" * 50)

    all_jobs = []       # Empty list which will store all the jobs fetched from the respected platforms.

    # Fetch from each source
    all_jobs.extend(fetch_remoteok(keywords=TARGET_KEYWORDS))
    time.sleep(2)       # Be polite between requests

    # Indeed - one call per keyword per location
    for keyword in TARGET_KEYWORDS[:5]:     # Limit to avoid rate limiting
        for location in TARGET_LOCATIONS:
            all_jobs.extend(fetch_indeed_rss(
                query=keyword,
                location=location,
                days_back=1
            ))
            time.sleep(1)

    # Adzuna - one call per keyword
    for keyword in TARGET_KEYWORDS[:5]:
        all_jobs.extend(fetch_adzuna(query=keyword))
        time.sleep(1)

    # Deduplicate by job_id
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["job_id"] not in seen:
            seen.add(job["job_id"])
            unique_jobs.append(job)

    duplicates_removed = len(all_jobs) - len(unique_jobs)

    print(f"\n[Fetcher] Raw jobs collected: {len(all_jobs)}")
    print(f"[Fetcher] Duplicates removed: {duplicates_removed}")
    print(f"[Fetcher] Unique jobs: {len(unique_jobs)}")

    return unique_jobs

if __name__ == "__main__":
    jobs = fetch_all_jobs()

    print(f"\n{'='*50}")
    print("SAMPLE JOBS:")
    print('='*50)

    for job in jobs[:5]:
        print(f"\nTitle:   {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location:{job['location']}")
        print(f"Source:  {job['source']}")
        print(f"URL:     {job['url'][:70]}...")
        desc_preview = job['description'][:150] if job['description'] else "No description"
        print(f"Preview: {desc_preview}...")
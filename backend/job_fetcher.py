import hashlib      # for generating unique job IDs with hashing
import requests     # for making HTTP requests to fetch job postings
import feedparser   # for parsing RSS feeds
from datetime import datetime, timezone   # for handling date and time
from typing import List, Dict, Optional   # for type hinting
import time         # for adding delays between requests

# function to generate a unique job ID based on the job URL
def make_job_id(url: str) -> str:
    """Creates unique hash for any job URL."""
    return hashlib.md5(url.encode()).hexdigest()    # Generate a unique hash for the job URL using MD5 hashing algorithm.

# function to fetch job postings from remoteok
def fetch_remoteok(keywords: List[str] = None) -> List[dict]:

    """Fetches job postings from remoteok.io public API based on keywords and optional location."""

    url = "https://remoteok.io/api"      # URL for the RemoteOK API
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
                "posted_at": datetime.now(timezone.utc).isoformat(),    # Date posted in ISO format
                "fetched_at": datetime.now(timezone.utc).isoformat(),   # Date fetched in ISO format
                "salary_range": job.get('salary', ''),    # Salary range if available
                "job_type": job.get('job_type', 'remote')     # Job type (e.g., full-time, part-time)
            })

        print(f"[RemoteOK] Fetched {len(jobs)} jobs.")    # Log the number of jobs fetched
        return jobs    # Return the list of fetched jobs

    except Exception as e:
        print(f"[RemoteOK] Error fetching jobs: {e}")    # Log any errors that occur during the fetch process
        return []    # Return an empty list in case of an error
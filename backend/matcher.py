# This file is responsible for matching job descriptions with candidate profiles based on skills, experience, and other relevant criteria. It uses the database module to fetch unprocessed jobs and profiles, and the resume_parser module to extract job requirements and calculate match scores.

import json     # used to load job requirements from JSON files  
import os       # used to handle file paths and directories
import time     # used to manage time-related functions, such as delays and timestamps
from database import (      # used to interact with the database for various operations
    get_connection, get_unprocessed_jobs,
    save_match, get_matches
)
from resume_parser import extract_job_requirements, calculate_match_score      # used to parse resumes and calculate match scores
from dotenv import load_dotenv      # used to load environment variables from a .env file
from pathlib import Path      # used to handle file paths in a platform-independent way
from notifier import send_job_notifications     # used to send job notification via email
from auto_apply import process_high_priority_jobs

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")      # Load environment variables from .env file in the project root

# function to get all profiles from the database
def get_all_profiles() -> list:
    conn = get_connection()     # establish a connection to the database
    cursor = conn.cursor()      # create a cursor object to execute SQL queries
    cursor.execute("SELECT * FROM profiles ORDER BY created_at DESC")     # execute a SQL query to select all profiles, ordered by creation date
    profiles = [dict(row) for row in cursor.fetchall()]     # fetch all rows from the executed query and convert each row to a dictionary
    conn.close()        # close the database connection to free up resources
    return profiles     # return the list of profile dictionaries to the caller

def select_best_profile(job_title: str, profiles: list) -> dict:
    """
    Selects the best matching profile for a given job title.
    Returns the profile with the highest match score.
    """
    title_lower = job_title.lower()     # convert the job title to lowercase for case-insensitive comparison
    role_map = {     # mapping of job titles to their corresponding roles for better matching
        "data_analyst": [
            "data analyst", "business analyst",
            "bi analyst", "analytics"
        ],
        "data_scientist": [
            "data scientist", "ml researcher",
            "research scientist"
        ],
        "ml_engineer": [
            "machine learning", "ml engineer",
            "ai engineer", "deep learning", "nlp"
        ],
        "data_engineer": [
            "data engineer", "etl", "pipeline"
        ]
    }
    for role_type, keywords in role_map.items():     # iterate through each role type and its associated keywords
        if any(kw in title_lower for kw in keywords):     # check if any keyword matches the job title
            for profile in profiles:     # iterate through each profile to find a match
                if profile.get("role_type") == role_type:     # check if the profile's role type matches the current role type
                    return profile     # return the matching profile if found
    return profiles[0] if profiles else None     # return the first profile if no match is found, or None if the list is empty       

# function to run the matching pipeline for unprocessed jobs
def run_matching_pipeline(batch_size: int = 20) -> dict:
    print("\n[Matcher] Starting pipeline...")

    profiles = get_all_profiles()
    if not profiles:
        print("[Matcher] No profiles found.")
        return {"error": "No profiles found"}

    jobs = get_unprocessed_jobs(limit=batch_size)
    if not jobs:
        print("[Matcher] No unprocessed jobs.")
        return {"processed": 0}

    print(f"[Matcher] Processing {len(jobs)} jobs...")

    results = {
        "processed": 0, "high_priority": 0,
        "review": 0, "skipped": 0, "errors": 0
    }

    for job in jobs:
        try:
            profile = select_best_profile(job["title"], profiles)
            profile_skills = json.loads(profile.get("skills", "[]"))
            profile_projects = json.loads(profile.get("projects", "[]"))

            profile_dict = {
                "skills": profile_skills,
                "experience_years": profile.get("experience_years", 0),
                "projects": profile_projects
            }

            jd_requirements = extract_job_requirements(job["description"])
            time.sleep(1)

            match_result = calculate_match_score(
                profile_dict, jd_requirements
            )
            time.sleep(1)

            save_match(
                job_db_id=job["id"],
                profile_id=profile["id"],
                match_result=match_result
            )

            score = match_result.get("match_score", 0)
            results["processed"] += 1

            if score >= 80:
                results["high_priority"] += 1
                print(f"  ✅ HIGH [{score}%] {job['title']} @ {job['company']}")
            elif score >= 50:
                results["review"] += 1
                print(f"  ⚠️ REVIEW [{score}%] {job['title']} @ {job['company']}")
            else:
                results["skipped"] += 1

        except Exception as e:
            print(f"  🚫 Error: {job.get('title')}: {e}")
            results["errors"] += 1

            # Send notifications for this batch
        if results["high_priority"] > 0:
            from database import get_matches, get_connection
            import json

            high_jobs = get_matches(priority="HIGH", limit=10)
            review_jobs = get_matches(priority="REVIEW", limit=5)

            # Get all profiles for auto-apply
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles")
            profiles = [dict(row) for row in cursor.fetchall()]
            conn.close()

            # Parse JSON fields in profiles
            for p in profiles:
                for field in ["skills", "experience", "education", "projects"]:
                    if p.get(field):
                        try:
                            p[field] = json.loads(p[field])
                        except Exception:
                            p[field] = []

            # Attempt auto-apply for high priority jobs
            # Get resume PDF path from first profile
            resume_path = profiles[0].get("pdf_path", "") if profiles else ""

            apply_results = process_high_priority_jobs(
                high_priority_jobs=high_jobs,
                profiles=profiles,
                resume_pdf_path=resume_path
            )

            results["auto_applied"] = apply_results.get("auto_applied", 0)
            results["notifications_sent"] = apply_results.get("notify_sent", 0)

            # Send review job notifications
            if results["review"] > 0:
                from notifier import send_job_notifications
                send_job_notifications(
                    high_jobs=[],
                    review_jobs=review_jobs
                )

        return results


if __name__ == "__main__":
    results = run_matching_pipeline(batch_size=5)
    print("\nHigh priority jobs:")
    for job in get_matches(priority="HIGH", limit=5):
        print(f"  {job['match_score']}% — {job['title']} @ {job['company']}")

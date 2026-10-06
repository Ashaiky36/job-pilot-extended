# This file is responsible for managing the SQLite database for the job matching application. It provides functions to initialize the database, save and retrieve profiles, jobs, matches, applications, and tracked companies. The database schema includes tables for profiles, jobs, matches, applications, and tracked companies, with appropriate relationships and indexes to optimize queries.

import sqlite3      # used to interact with SQLite database
import json     # used to serialize and deserialize JSON data for storing complex structures in the database
import os       # used to handle file paths and directories
from datetime import datetime, timezone     # used to manage timestamps and ensure they are stored in UTC format
from pathlib import Path        # used to handle file paths in a platform-independent way

DB_PATH = os.path.join(     # used to define the path to the SQLite database file
    os.path.dirname(__file__),
    "jobpilot.db"
)

def get_connection():       # returns a connection to the SQLite database, enabling interaction with the database for various operations
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)     # establishes a connection to the SQLite database file specified by DB_PATH
    conn.row_factory = sqlite3.Row      # configures the connection to return rows as dictionaries, allowing for easier access to column values by name
    conn.execute("PRAGMA foreign_keys = ON")        # enables foreign key support in SQLite, ensuring that relationships between tables are enforced
    return conn     # returns the established database connection

def init_database():        # initializes the database by creating all necessary tables
    """Creates all tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # executes a script containing multiple SQL statements to create the necessary tables in the database if they do not already exist
    cursor.executescript("""        
        CREATE TABLE IF NOT EXISTS profiles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            role_type   TEXT NOT NULL,
            name        TEXT,
            email       TEXT,
            phone       TEXT,
            location    TEXT,
            skills      TEXT,
            experience_years INTEGER DEFAULT 0,
            experience  TEXT,
            education   TEXT,
            projects    TEXT,
            resume_text TEXT,
            pdf_path    TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jobs(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id          TEXT UNIQUE NOT NULL,
            title           TEXT,
            company         TEXT,
            location        TEXT,
            url             TEXT,
            description     TEXT,
            source          TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            experience_min  INTEGER DEFAULT 0,
            experience_max  INTEGER DEFAULT 5,
            job_type        TEXT DEFAULT 'full-time',
            salary_range    TEXT,
            posted_at       DATETIME,
            fetched_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed       INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS matches (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id                INTEGER REFERENCES jobs(id),
            profile_id            INTEGER REFERENCES profiles(id),
            match_score           REAL,
            matched_skills        TEXT,
            missing_required      TEXT,
            missing_preferred     TEXT,
            experience_match      INTEGER DEFAULT 0,
            score_breakdown       TEXT,
            recommendation        TEXT,
            improvement_suggestions TEXT,
            priority              TEXT DEFAULT 'SKIPPED',
            cover_letter          TEXT,
            matched_at            DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id      INTEGER REFERENCES jobs(id),
            profile_id  INTEGER REFERENCES profiles(id),
            status      TEXT DEFAULT 'PENDING',
            method      TEXT DEFAULT 'MANUAL',
            applied_at  DATETIME,
            notes       TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tracked_companies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            careers_url TEXT,
            status      TEXT DEFAULT 'PENDING',
            crawlable   INTEGER DEFAULT 1,
            note        TEXT,
            added_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_job_id
            ON jobs(job_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_processed
            ON jobs(processed);
        CREATE INDEX IF NOT EXISTS idx_matches_priority
            ON matches(priority);
        CREATE INDEX IF NOT EXISTS idx_matches_score
            ON matches(match_score DESC);
    """)
    conn.commit()       # commits the changes made by the executed SQL script to the database, ensuring that the table structures are saved
    conn.close()        # closes the database connection, releasing any resources associated with it and ensuring that the connection is properly terminated
    print(f"[DB] Database initialised at {DB_PATH}")

def save_profile(profile_data: dict, role_type: str, pdf_path: str = "") -> int:        # saves or updates a resume profile in the database and returns the profile ID
    """Saves or updates a resume profile. Returns profile id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO profiles
            (role_type, name, email, phone, location,
             skills, experience_years, experience,
             education, projects, resume_text, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        role_type,
        profile_data.get("name", ""),
        profile_data.get("email", ""),
        profile_data.get("phone", ""),
        profile_data.get("location", ""),
        json.dumps(profile_data.get("skills", [])),
        profile_data.get("experience_years", 0),
        json.dumps(profile_data.get("experience", [])),
        json.dumps(profile_data.get("education", [])),
        json.dumps(profile_data.get("projects", [])),
        profile_data.get("resume_text", ""),
        pdf_path
    ))

    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"[DB] Profile saved: {profile_data.get('name')} ({role_type})")
    return profile_id

def save_jobs(jobs: list[dict]) -> int:     # saves new jobs to the database, skipping duplicates based on job_id hash, and returns the count of newly inserted jobs
    """
    Saves new jobs to database.
    Skips duplicates using job_id hash.
    Returns count of newly inserted jobs.
    """
    conn = get_connection()
    cursor = conn.cursor()
    new_count = 0

    for job in jobs:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO jobs
                    (job_id, title, company, location, url,
                     description, source, job_type,
                     salary_range, posted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,(
                job.get("job_id", ""),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("url", ""),
                job.get("description", ""),
                job.get("source", ""),
                job.get("job_type", "full-time"),
                job.get("salary_range", ""),
                job.get("posted_at", "")
            ))

            if cursor.rowcount > 0:
                new_count += 1

        except Exception as e:
            print(f"[DB] Error saving job {job.get('title')}: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"[DB] Saved {new_count} new jobs out of {len(jobs)} total")
    return new_count        # returns the count of newly inserted jobs

def get_unprocessed_jobs(limit: int = 50) -> list[dict]:        # retrieves jobs from the database that have not been processed yet, with an optional limit on the number of jobs returned
    """Returns jobs that have not been matched yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM jobs
        WHERE processed = 0
        AND description != ''
        AND length(description) > 50
        ORDER BY fetched_at DESC
        LIMIT ?
    """, (limit,))

    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

def save_match(     # saves a match result to the database and marks the corresponding job as processed, returning the match ID
    job_db_id: int,
    profile_id: int,
    match_result: dict
) -> int:
    """Saves a match result and marks job as processed."""
    conn = get_connection()
    cursor = conn.cursor()

    score = match_result.get("match_score", 0)      # retrieves the match score from the match_result dictionary, defaulting to 0 if not present

    # Determine priority based on match score
    if score >= 80:
        priority = "HIGH"
    elif score >= 50:
        priority = "REVIEW"
    else:
        priority = "SKIPPED"

    cursor.execute("""
        INSERT INTO matches
            (job_id, profile_id, match_score,
             matched_skills, missing_required,
             missing_preferred, experience_match,
             score_breakdown, recommendation,
             improvement_suggestions, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_db_id,
        profile_id,
        score,
        json.dumps(match_result.get("matched_skills", [])),
        json.dumps(match_result.get("missing_required_skills", [])),
        json.dumps(match_result.get("missing_preferred_skills", [])),
        1 if match_result.get("experience_match") else 0,
        json.dumps(match_result.get("score_breakdown", {})),
        match_result.get("recommendation", ""),
        json.dumps(match_result.get("improvement_suggestions", [])),
        priority
    ))

    match_id = cursor.lastrowid     # retrieves the ID of the newly inserted match record, which can be used for reference or further operations     

    # Mark job as processed
    cursor.execute("""
        UPDATE jobs SET processed = 1 WHERE id = ?
    """, (job_db_id,))

    conn.commit()
    conn.close()
    return match_id

def get_matches(priority: str = None, limit: int = 50) -> list:     # retrieves matches from the database, optionally filtered by priority, and returns a list of match dictionaries with full job details
    """Returns matches with full job details."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            j.id, j.title, j.company, j.location,
            j.url, j.source, j.salary_range,
            j.job_type, j.posted_at,
            m.match_score, m.matched_skills,
            m.missing_required, m.recommendation,
            m.improvement_suggestions,
            m.priority, m.matched_at
        FROM matches m
        JOIN jobs j ON m.job_id = j.id
        WHERE m.priority != 'SKIPPED'
    """

    if priority:
        query += " AND m.priority = ?"
        cursor.execute(query + " ORDER BY m.match_score DESC LIMIT ?",
                       (priority.upper(), limit))
    else:
        cursor.execute(query + " ORDER BY m.match_score DESC LIMIT ?",
                       (limit,))

    jobs = []
    for row in cursor.fetchall():
        job = dict(row)
        for field in ["matched_skills", "missing_required",
                      "improvement_suggestions"]:
            if job.get(field):
                try:
                    job[field] = json.loads(job[field])
                except Exception:
                    job[field] = []
        jobs.append(job)

    conn.close()
    return jobs

def get_high_priority_jobs(limit: int = 20) -> list[dict]: 
    """Returns HIGH priority matches with full job details."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            j.id, j.title, j.company, j.location,
            j.url, j.source, j.salary_range, j.job_type,
            m.match_score, m.matched_skills,
            m.missing_required, m.recommendation,
            m.improvement_suggestions, m.priority,
            m.matched_at
        FROM matches m
        JOIN jobs j ON m.job_id = j.id
        WHERE m.priority = 'HIGH'
        ORDER BY m.match_score DESC
        LIMIT ?
    """, (limit,))

    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

def get_dashboard_stats() -> dict:
    """Returns summary statistics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE processed = 1")
    processed_jobs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM matches WHERE priority = 'HIGH'"
    )
    high_priority = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM matches WHERE priority = 'REVIEW'"
    )
    review = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications")
    applications = cursor.fetchone()[0]

    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM jobs
        GROUP BY source
        ORDER BY count DESC
    """)
    by_source = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_jobs": total_jobs,
        "processed_jobs": processed_jobs,
        "high_priority": high_priority,
        "review": review,
        "skipped": processed_jobs - high_priority - review,
        "applications": applications,
        "by_source": by_source
    }

def save_tracked_company(name: str, careers_url: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tracked_companies (name, careers_url)
        VALUES (?, ?)
    """, (name, careers_url))
    company_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return company_id

def get_tracked_companies() -> list:            
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tracked_companies ORDER BY added_at DESC"
    )
    companies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return companies

def update_company_crawl_status(        # updates the crawlable status and note for a tracked company in the database
    company_id: int,
    crawlable: bool,
    note: str = ""
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tracked_companies
        SET crawlable = ?, note = ?, status = 'CHECKED'
        WHERE id = ?
    """, (1 if crawlable else 0, note, company_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("[DB] All tables created successfully")

    stats = get_dashboard_stats()
    print(f"[DB] Stats: {stats}")
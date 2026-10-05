import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "jobpilot.db"
)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    """Creates all tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

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

        CREATE INDEX IF NOT EXISTS idx_jobs_job_id
            ON jobs(job_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_processed
            ON jobs(processed);
        CREATE INDEX IF NOT EXISTS idx_matches_priority
            ON matches(priority);
        CREATE INDEX IF NOT EXISTS idx_matches_score
            ON matches(match_score DESC
        );
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Database initialised at {DB_PATH}")

def save_profile(profile_data: dict, role_type: str, pdf_path: str = "") -> int:
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

def save_jobs(jobs: list[dict]) -> int:
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
    return new_count

def get_unprocessed_jobs(limit: int = 50) -> list[dict]:
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

def save_match(
    job_db_id: int,
    profile_id: int,
    match_result: dict
) -> int:
    """Saves a match result and marks job as processed."""
    conn = get_connection()
    cursor = conn.cursor()

    score = match_result.get("match_score", 0)

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

    match_id = cursor.lastrowid

    # Mark job as processed
    cursor.execute("""
        UPDATE jobs SET processed = 1 WHERE id = ?
    """, (job_db_id,))

    conn.commit()
    conn.close()
    return match_id

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


if __name__ == "__main__":
    init_database()
    print("[DB] All tables created successfully")

    stats = get_dashboard_stats()
    print(f"[DB] Stats: {stats}")
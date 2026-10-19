import smtplib
import os
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from dotenv import load_dotenv
from database import get_connection, save_match
from cover_letter import generate_email_application

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

SENDER = os.getenv("EMAIL_SENDER", "")
PASSWORD = os.getenv("EMAIL_PASSWORD", "")

def extract_apply_email(job_description: str, job_url: str) -> str:
    """
    Attempts to find an apply-via-email address in the job description.
    Returns email string if found, empty string otherwise.
    """
    if not job_description:
        return ""

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, job_description)

    apply_keywords = ["apply", "send", "resume", "cv", "careers", "hr", "hiring"]

    for email in emails:
        email_lower = email.lower()
        if any(kw in email_lower for kw in apply_keywords):
            return email

    if emails:
        return emails[0]

    return ""


def send_application_email(
    application: dict,
    resume_pdf_path: str = None
) -> bool:
    """
    Sends a job application email with optional resume attachment.
    """
    if not SENDER or not PASSWORD:
        print("[AutoApply] No email credentials configured")
        return False

    try:
        msg = MIMEMultipart()
        msg["Subject"] = application["subject"]
        msg["From"] = f"{application['candidate_name']} <{SENDER}>"
        msg["To"] = application["to"]

        msg.attach(MIMEText(application["body"], "plain"))

        # Attach resume PDF if provided
        if resume_pdf_path and Path(resume_pdf_path).exists():
            with open(resume_pdf_path, "rb") as f:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                filename = Path(resume_pdf_path).name
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}"
                )
                msg.attach(attachment)
            print(f"[AutoApply] Resume attached: {filename}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, application["to"], msg.as_string())

        print(f"[AutoApply] Application sent to {application['to']}")
        return True

    except Exception as e:
        print(f"[AutoApply] Send failed: {e}")
        return False

def attempt_auto_apply(
    job: dict,
    candidate_profile: dict,
    match_result: dict,
    resume_pdf_path: str = None
) -> dict:
    """
    Main auto-apply function.
    Checks if email apply is possible, generates application, sends it.

    Returns:
        dict with success, method, and message
    """
    job_description = job.get("description", "")
    job_url = job.get("url", "")

    # Check if email apply is possible
    apply_email = extract_apply_email(job_description, job_url)

    if not apply_email:
        return {
            "success": False,
            "method": "none",
            "message": (
                "No email application address found. "
                "Manual application required."
            ),
            "apply_url": job_url
        }

    # Generate application package
    print(
        f"[AutoApply] Generating application for "
        f"{job.get('title')} at {job.get('company')}"
    )

    application = generate_email_application(
        candidate_profile=candidate_profile,
        job=job,
        match_result=match_result,
        apply_email=apply_email
    )

    # Send the application
    sent = send_application_email(
        application=application,
        resume_pdf_path=resume_pdf_path
    )

    if sent:
        # Log to database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications
                (job_id, profile_id, status, method, applied_at, notes)
            VALUES (?, ?, 'APPLIED', 'AUTO_EMAIL', CURRENT_TIMESTAMP, ?)
        """, (
            job.get("id"),
            candidate_profile.get("id", 1),
            f"Auto-applied via email to {apply_email}"
        ))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "method": "email",
            "message": f"Application sent to {apply_email}",
            "apply_email": apply_email
        }
    else:
        return {
            "success": False,
            "method": "email_failed",
            "message": "Email send failed. Manual application required.",
            "apply_url": job_url
        }

def process_high_priority_jobs(
    high_priority_jobs: list,
    profiles: list,
    resume_pdf_path: str = None
) -> list:
    """
    Processes all HIGH priority jobs.
    Attempts auto-apply where possible.
    Returns list of results for notification.
    """
    from notifier import send_job_notifications

    auto_applied = []
    needs_manual = []

    for job in high_priority_jobs:
        # Select best profile for this job
        from matcher import select_best_profile
        profile = select_best_profile(job.get("title", ""), profiles)

        # Get match result from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM matches
            WHERE job_id = ?
            ORDER BY matched_at DESC
            LIMIT 1
        """, (job.get("id"),))
        match_row = cursor.fetchone()
        conn.close()

        if not match_row:
            continue

        match_result = dict(match_row)
        for field in ["matched_skills", "missing_required",
                      "improvement_suggestions"]:
            if match_result.get(field):
                try:
                    match_result[field] = json.loads(match_result[field])
                except Exception:
                    match_result[field] = []

        # Attempt auto-apply
        result = attempt_auto_apply(
            job=job,
            candidate_profile=profile,
            match_result=match_result,
            resume_pdf_path=resume_pdf_path
        )

        if result["success"]:
            auto_applied.append({**job, **result})
            print(
                f"  ✅ Auto-applied: {job.get('title')} "
                f"at {job.get('company')}"
            )
        else:
            needs_manual.append({**job, **result})
            print(
                f"  📧 Notify needed: {job.get('title')} "
                f"at {job.get('company')}"
            )

    # Send notifications for jobs that need manual application
    if needs_manual:
        send_job_notifications(
            high_jobs=needs_manual,
            review_jobs=[]
        )

    return {
        "auto_applied": len(auto_applied),
        "notify_sent": len(needs_manual),
        "total": len(high_priority_jobs)
    }


if __name__ == "__main__":
    # Test cover letter generation
    from cover_letter import generate_cover_letter

    sample_profile = {
        "name": "Mohd Sami",
        "email": "test@gmail.com",
        "skills": ["Python", "SQL", "Power BI", "Pandas", "ML"],
        "experience_years": 0,
        "projects": [
            {
                "name": "AI Steam Market Intelligence",
                "technologies": ["Python", "BeautifulSoup", "Power BI"]
            }
        ]
    }

    sample_job = {
        "title": "Data Analyst",
        "company": "Analytics Corp",
        "location": "Mumbai",
        "description": "Apply to careers@analyticscorp.com"
    }

    sample_match = {
        "match_score": 88,
        "matched_skills": ["Python", "SQL", "Power BI"],
        "missing_required_skills": ["Tableau"],
        "improvement_suggestions": ["Add Tableau to your skillset"]
    }

    print("Testing auto-apply flow...")
    email_found = extract_apply_email(
        sample_job["description"],
        ""
    )
    print(f"Apply email found: {email_found}")

    letter = generate_cover_letter(
        sample_profile,
        sample_job,
        sample_match
    )
    print(f"\nCover letter preview:\n{letter[:300]}...")
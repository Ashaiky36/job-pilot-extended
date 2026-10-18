import smtplib      # for communiting with email servers
import os
import json
from email.mime.multipart import MIMEMultipart      # It combines multiple parts into one email, such as an HTML version and a plain-text version
from email.mime.text import MIMEText        # represents a text-based email part
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

SENDER = os.getenv("EMAIL_SENDER", "")
PASSWORD = os.getenv("EMAIL_PASSWORD", "")
RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")

def send_email(subject: str, html_body: str, text_body: str = "") -> bool:      
    """
    Sends an HTML email via Gmail SMTP.
    Returns True if sent successfully, False otherwise.
    """
    if not SENDER or not PASSWORD:
        print("[Email] No credentials configured, skipping")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"JobPilot <{SENDER}>"
        msg["To"] = RECIPIENT

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())

        print(f"[Email] Sent: {subject}")
        return True

    except Exception as e:
        print(f"[Email] Failed: {e}")
        return False

def build_job_digest_email(jobs: list) -> tuple[str, str]:
    """
    Builds HTML and plain text for a job digest email.
    Used when multiple HIGH priority jobs are found.
    """
    count = len(jobs)
    date_str = datetime.now().strftime("%d %B %Y")

    rows = ""
    for job in jobs:
        score = job.get("match_score", 0)
        matched = ", ".join(job.get("matched_skills", [])[:4])
        missing = ", ".join(job.get("missing_required", [])[:3])

        rows += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #30363d">
                <strong style="color:#e6edf3">{job.get('title','')}</strong><br>
                <span style="color:#8b949e;font-size:13px">{job.get('company','')}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #30363d;color:#8b949e;font-size:13px">
                {job.get('location','')}
            </td>
            <td style="padding:12px;border-bottom:1px solid #30363d">
                <span style="background:rgba(63,185,80,0.2);color:#3fb950;
                      padding:3px 8px;border-radius:12px;font-size:12px;font-weight:600">
                    {score}%
                </span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #30363d;
                       font-size:12px;color:#8b949e">
                {matched}
            </td>
            <td style="padding:12px;border-bottom:1px solid #30363d">
                {"<span style='color:#f85149;font-size:12px'>" + missing + "</span>"
                 if missing else
                 "<span style='color:#3fb950;font-size:12px'>All matched</span>"}
            </td>
            <td style="padding:12px;border-bottom:1px solid #30363d">
                <a href="{job.get('url','#')}"
                   style="background:#58a6ff;color:#0d1117;padding:6px 12px;
                          border-radius:6px;text-decoration:none;font-size:12px;
                          font-weight:600">
                    Apply →
                </a>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background:#0d1117;font-family:-apple-system,
                 BlinkMacSystemFont,'Segoe UI',sans-serif">
        <div style="max-width:800px;margin:0 auto;padding:32px 16px">

            <!-- Header -->
            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:12px;padding:24px;margin-bottom:20px">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <span style="font-size:24px">✈</span>
                    <span style="color:#58a6ff;font-size:20px;font-weight:700">
                        JobPilot
                    </span>
                </div>
                <h1 style="color:#e6edf3;font-size:22px;margin:0 0 8px 0">
                    🚨 {count} High Priority Job{"s" if count > 1 else ""} Found
                </h1>
                <p style="color:#8b949e;margin:0;font-size:14px">
                    {date_str} - AI matched these roles against your resume
                </p>
            </div>

            <!-- Stats bar -->
            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:16px;margin-bottom:20px;
                        display:flex;gap:24px">
                <div style="text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#3fb950">
                        {count}
                    </div>
                    <div style="font-size:12px;color:#8b949e">High Priority</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#58a6ff">
                        {max((j.get('match_score',0) for j in jobs), default=0)}%
                    </div>
                    <div style="font-size:12px;color:#8b949e">Best Match</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#e6edf3">
                        {len(set(j.get('source','') for j in jobs))}
                    </div>
                    <div style="font-size:12px;color:#8b949e">Sources</div>
                </div>
            </div>

            <!-- Jobs table -->
            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:8px;overflow:hidden;margin-bottom:20px">
                <table style="width:100%;border-collapse:collapse">
                    <thead>
                        <tr style="background:#21262d">
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Job
                            </th>
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Location
                            </th>
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Match
                            </th>
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Skills Matched
                            </th>
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Missing
                            </th>
                            <th style="padding:12px;text-align:left;
                                       color:#8b949e;font-size:12px;
                                       font-weight:600;text-transform:uppercase">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>

            <!-- Footer -->
            <div style="text-align:center;color:#8b949e;font-size:12px;
                        padding-top:16px;border-top:1px solid #30363d">
                Sent by JobPilot AI - Your automated job discovery system<br>
                <a href="http://localhost:8000"
                   style="color:#58a6ff;text-decoration:none">
                    Open Dashboard
                </a>
            </div>

        </div>
    </body>
    </html>
    """

    text = f"JobPilot - {count} High Priority Jobs Found\n\n"
    for job in jobs:
        text += (
            f"• {job.get('title')} at {job.get('company')} "
            f"- {job.get('match_score')}% match\n"
            f"  Apply: {job.get('url')}\n\n"
        )

    return html, text

def build_single_job_email(job: dict) -> tuple[str, str]:
    """
    Builds email for a single HIGH priority job.
    Sent immediately when exactly one match is found.
    """
    score = job.get("match_score", 0)
    matched = job.get("matched_skills", [])
    missing = job.get("missing_required", [])
    suggestions = job.get("improvement_suggestions", [])

    matched_html = "".join(
        f'<span style="background:rgba(88,166,255,0.15);color:#58a6ff;'
        f'padding:3px 8px;border-radius:12px;font-size:12px;'
        f'margin:2px;display:inline-block">{s}</span>'
        for s in matched[:8]
    )

    missing_html = "".join(
        f'<span style="background:rgba(248,81,73,0.15);color:#f85149;'
        f'padding:3px 8px;border-radius:12px;font-size:12px;'
        f'margin:2px;display:inline-block">⚠ {s}</span>'
        for s in missing[:5]
    )

    suggestions_html = "".join(
        f'<li style="color:#8b949e;font-size:13px;margin-bottom:4px">{s}</li>'
        for s in suggestions[:3]
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0d1117;
                 font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
        <div style="max-width:600px;margin:0 auto;padding:32px 16px">

            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:12px;padding:24px;margin-bottom:16px">
                <div style="color:#58a6ff;font-size:18px;font-weight:700;
                             margin-bottom:16px">✈ JobPilot Alert</div>
                <h1 style="color:#e6edf3;font-size:20px;margin:0 0 4px 0">
                    🚨 High Priority Match Found
                </h1>
                <div style="background:rgba(63,185,80,0.1);
                            border:1px solid rgba(63,185,80,0.2);
                            border-radius:8px;padding:16px;margin-top:16px">
                    <div style="font-size:18px;font-weight:600;
                                color:#e6edf3;margin-bottom:4px">
                        {job.get('title','')}
                    </div>
                    <div style="color:#8b949e;font-size:14px;margin-bottom:12px">
                        {job.get('company','')} • {job.get('location','')}
                    </div>
                    <div style="display:inline-block;background:rgba(63,185,80,0.2);
                                color:#3fb950;padding:6px 14px;border-radius:20px;
                                font-size:16px;font-weight:700">
                        {score}% Match
                    </div>
                </div>
            </div>

            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:20px;margin-bottom:16px">
                <div style="color:#e6edf3;font-size:14px;
                             font-weight:600;margin-bottom:10px">
                    ✅ Matched Skills
                </div>
                <div>{matched_html}</div>
            </div>

            {f'''
            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:20px;margin-bottom:16px">
                <div style="color:#e6edf3;font-size:14px;
                             font-weight:600;margin-bottom:10px">
                    ⚠️ Missing Skills
                </div>
                <div>{missing_html}</div>
            </div>
            ''' if missing else ''}

            {f'''
            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:20px;margin-bottom:16px">
                <div style="color:#e6edf3;font-size:14px;
                             font-weight:600;margin-bottom:10px">
                    💡 How to Strengthen This Application
                </div>
                <ul style="margin:0;padding-left:16px">
                    {suggestions_html}
                </ul>
            </div>
            ''' if suggestions else ''}

            <div style="text-align:center;padding:20px">
                <a href="{job.get('url','#')}"
                   style="background:#58a6ff;color:#0d1117;padding:14px 32px;
                          border-radius:8px;text-decoration:none;font-size:16px;
                          font-weight:700;display:inline-block">
                    Apply Now →
                </a>
            </div>

        </div>
    </body>
    </html>
    """

    text = (
        f"High Priority Job Match - {score}%\n\n"
        f"{job.get('title')} at {job.get('company')}\n"
        f"Location: {job.get('location')}\n"
        f"Apply: {job.get('url')}\n\n"
        f"Matched skills: {', '.join(matched)}\n"
        f"Missing: {', '.join(missing)}\n"
    )

    return html, text

def build_review_job_email(job: dict) -> tuple[str, str]:
    """
    Builds email for REVIEW jobs (50-79% match).
    Asks user if they have the missing skills.
    """
    score = job.get("match_score", 0)
    missing = job.get("missing_required", [])
    missing_str = ", ".join(missing)

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0d1117;
                 font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
        <div style="max-width:600px;margin:0 auto;padding:32px 16px">

            <div style="background:#161b22;border:1px solid #30363d;
                        border-radius:12px;padding:24px">
                <div style="color:#58a6ff;font-size:18px;font-weight:700;
                             margin-bottom:16px">✈ JobPilot</div>
                <h1 style="color:#e6edf3;font-size:20px;margin:0 0 8px 0">
                    👀 Possible Match - Your Input Needed
                </h1>
                <p style="color:#8b949e;font-size:14px;margin:0 0 20px 0">
                    We found a job that partially matches your profile.
                    You scored <strong style="color:#d29922">{score}%</strong>
                    but are missing a few skills.
                </p>

                <div style="background:#21262d;border-radius:8px;
                            padding:16px;margin-bottom:20px">
                    <div style="font-size:16px;font-weight:600;
                                color:#e6edf3;margin-bottom:4px">
                        {job.get('title','')}
                    </div>
                    <div style="color:#8b949e;font-size:13px">
                        {job.get('company','')} • {job.get('location','')}
                    </div>
                </div>

                <div style="background:rgba(210,153,34,0.1);
                            border:1px solid rgba(210,153,34,0.2);
                            border-radius:8px;padding:16px;margin-bottom:20px">
                    <div style="color:#d29922;font-weight:600;
                                margin-bottom:8px;font-size:14px">
                        ⚠️ Skills you may be missing:
                    </div>
                    <div style="color:#e6edf3;font-size:14px">{missing_str}</div>
                </div>

                <p style="color:#8b949e;font-size:14px;margin-bottom:20px">
                    Do you actually have these skills but they are not on your resume?
                    If yes, you should still apply - your practical experience matters.
                </p>

                <div style="display:flex;gap:12px;justify-content:center">
                    <a href="{job.get('url','#')}"
                       style="background:#3fb950;color:#0d1117;padding:12px 24px;
                              border-radius:8px;text-decoration:none;
                              font-size:14px;font-weight:700">
                        ✅ Yes, I have these skills - Apply
                    </a>
                    <a href="http://localhost:8000"
                       style="background:#21262d;color:#8b949e;padding:12px 24px;
                              border-radius:8px;text-decoration:none;
                              font-size:14px;border:1px solid #30363d">
                        ❌ No, Skip This Job
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text = (
        f"Possible Match - {score}%\n\n"
        f"{job.get('title')} at {job.get('company')}\n\n"
        f"Missing skills: {missing_str}\n\n"
        f"Do you have these skills? If yes, apply here:\n{job.get('url')}\n"
    )

    return html, text

def send_job_notifications(
    high_jobs: list,
    review_jobs: list = None
) -> dict:
    """
    Main notification dispatcher.
    Implements hybrid approach:
    - 1 high priority job → immediate single email
    - 2+ high priority jobs → digest email
    - Review jobs → individual emails asking for confirmation
    """
    results = {"high_sent": 0, "review_sent": 0, "errors": 0}

    # HIGH PRIORITY - hybrid dispatch
    if len(high_jobs) == 1:
        html, text = build_single_job_email(high_jobs[0])
        subject = (
            f"🚨 High Priority Match: "
            f"{high_jobs[0].get('title')} - "
            f"{high_jobs[0].get('match_score')}%"
        )
        if send_email(subject, html, text):
            results["high_sent"] += 1
        else:
            results["errors"] += 1

    elif len(high_jobs) > 1:
        html, text = build_job_digest_email(high_jobs)
        subject = f"🚨 {len(high_jobs)} High Priority Jobs Found - JobPilot"
        if send_email(subject, html, text):
            results["high_sent"] += len(high_jobs)
        else:
            results["errors"] += 1

    # REVIEW JOBS - individual confirmation emails
    if review_jobs:
        for job in review_jobs[:3]:  # Max 3 review emails per run
            html, text = build_review_job_email(job)
            subject = (
                f"👀 Review Match ({job.get('match_score')}%): "
                f"{job.get('title')} at {job.get('company')}"
            )
            if send_email(subject, html, text):
                results["review_sent"] += 1
            else:
                results["errors"] += 1

    print(f"[Notifier] Sent: {results}")
    return results


if __name__ == "__main__":
    # Test email with sample data
    test_jobs = [
        {
            "title": "Data Analyst",
            "company": "Test Company",
            "location": "Mumbai, India",
            "url": "https://example.com/job/1",
            "match_score": 85,
            "matched_skills": ["Python", "SQL", "Power BI", "Pandas"],
            "missing_required": ["Tableau"],
            "improvement_suggestions": [
                "Learn Tableau to complete the required visualization toolset",
                "Add more business impact metrics to your projects"
            ],
            "source": "linkedin"
        }
    ]

    print("Testing single job email...")
    html, text = build_single_job_email(test_jobs[0])
    sent = send_email(
        "Test: JobPilot Job Alert",
        html,
        text
    )
    print(f"Email sent: {sent}")
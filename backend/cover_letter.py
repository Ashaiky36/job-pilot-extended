import os
import json
from google import genai        
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")      

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_cover_letter(
    candidate_profile: dict,
    job: dict,
    match_result: dict
) -> str:
    """
    Generates a personalised cover letter using Gemini.
    Uses candidate profile, job details, and match analysis
    to create a targeted, non-generic letter.
    """

    skills_matched = match_result.get("matched_skills", [])
    skills_missing = match_result.get("missing_required_skills", [])
    projects = candidate_profile.get("projects", [])

    project_summaries = "\n".join([
        f"- {p.get('name','')}: {', '.join(p.get('technologies',[]))}"
        for p in projects[:3]
    ])

    prompt = f"""Write a professional cover letter for this job application.

CANDIDATE PROFILE:
Name: {candidate_profile.get('name', '')}
Skills: {', '.join(candidate_profile.get('skills', [])[:15])}
Experience: {candidate_profile.get('experience_years', 0)} years
Key Projects:
{project_summaries}

JOB DETAILS:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Location: {job.get('location', '')}
Description: {job.get('description', '')[:800]}

MATCH ANALYSIS:
Matched Skills: {', '.join(skills_matched[:8])}
Missing Skills: {', '.join(skills_missing[:3])}
Match Score: {match_result.get('match_score', 0)}%

INSTRUCTIONS:
- Write in first person, professional but warm tone
- Start with a strong opening that mentions the specific role and company
- Highlight 2-3 most relevant skills from the matched skills list
- Reference 1-2 specific projects that demonstrate relevant experience
- Address missing skills positively - show willingness to learn
- Close with a clear call to action
- Keep it under 300 words
- Do NOT use generic phrases like "I am writing to express my interest"
- Do NOT use placeholder text like [Your Name]
- Make it sound like a real person wrote it, not a template

Write only the cover letter body. No subject line, no date, no address."""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )
    return response.text.strip()

def generate_email_application(
    candidate_profile: dict,
    job: dict,
    match_result: dict,
    apply_email: str
) -> dict:
    """
    Generates a complete email application package.
    Returns subject, body, and cover letter ready to send.
    """

    cover_letter = generate_cover_letter(
        candidate_profile, job, match_result
    )

    name = candidate_profile.get("name", "Candidate")
    title = job.get("title", "the position")
    company = job.get("company", "your company")

    subject = f"Application for {title} - {name}"

    email_body = f"""Dear Hiring Team,

{cover_letter}

I have attached my resume for your consideration. I would welcome the opportunity to discuss how my background aligns with your needs.

Thank you for your time.

Best regards,
{name}
{candidate_profile.get('email', '')}
{candidate_profile.get('phone', '')}"""

    return {
        "to": apply_email,
        "subject": subject,
        "body": email_body,
        "cover_letter": cover_letter,
        "candidate_name": name,
        "job_title": title,
        "company": company
    }


if __name__ == "__main__":
    # Test with sample data
    sample_profile = {
        "name": "Mohd Sami",
        "email": "test@gmail.com",
        "phone": "+91 9999999999",
        "skills": [
            "Python", "SQL", "Power BI", "Pandas",
            "NumPy", "Machine Learning", "EDA"
        ],
        "experience_years": 0,
        "projects": [
            {
                "name": "AI-Powered Steam Market Intelligence Platform",
                "technologies": ["Python", "BeautifulSoup", "Pandas", "Power BI"]
            },
            {
                "name": "Data Science Salary Dashboard",
                "technologies": ["Python", "SQL", "Power BI", "EDA"]
            }
        ]
    }

    sample_job = {
        "title": "Data Analyst",
        "company": "TechCorp India",
        "location": "Mumbai, India",
        "description": (
            "We are looking for a Data Analyst with strong Python and SQL skills "
            "to analyze business data, build dashboards, and present insights to stakeholders."
        )
    }

    sample_match = {
        "match_score": 85,
        "matched_skills": ["Python", "SQL", "Power BI", "Pandas"],
        "missing_required_skills": ["Tableau"],
        "improvement_suggestions": [
            "Learn Tableau to complement Power BI expertise"
        ]
    }

    print("Generating cover letter...")
    letter = generate_cover_letter(sample_profile, sample_job, sample_match)
    print("\n" + "="*60)
    print("GENERATED COVER LETTER:")
    print("="*60)
    print(letter)

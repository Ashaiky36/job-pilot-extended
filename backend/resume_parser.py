import google.generativeai as genai
import json
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def parse_resume(pdf_path: str) -> dict:
    """
    Sends resume PDF to Gemini and extracts structured profile data.
    Returns a clean dict with skills, experience, education.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Read PDF as bytes
    pdf_bytes = Path(pdf_path).read_bytes()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    prompt = """Extract the following information from this resume.
Return ONLY valid JSON with no markdown, no backticks, no explanation.

Required JSON structure:
{
    "name": "full name",
    "email": "email address",
    "phone": "phone number",
    "location": "city, country",
    "skills": ["skill1", "skill2", "skill3"],
    "experience_years": 2,
    "experience": [
        {
            "title": "job title",
            "company": "company name",
            "duration": "Jan 2023 - Present",
            "description": "brief description"
        }
    ],
    "education": [
        {
            "degree": "degree name",
            "institution": "university name",
            "year": "2024"
        }
    ],
    "projects": [
        {
            "name": "project name",
            "technologies": ["tech1", "tech2"],
            "description": "brief description"
        }
    ],
    "target_roles": ["Data Analyst", "ML Engineer"]
}

If any field is not found, use null for strings and [] for arrays.
Extract ALL skills mentioned anywhere in the resume including
from project descriptions and work experience."""

    response = model.generate_content([
        {
            "mime_type": "application/pdf",
            "data": pdf_base64
        },
        prompt
    ])

    # Clean and parse response
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    profile = json.loads(text)
    return profile


def extract_job_requirements(jd_text: str) -> dict:
    """
    Extracts structured requirements from a raw job description.
    Returns clean dict with required skills, experience, etc.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""Extract structured information from this job description.
Return ONLY valid JSON with no markdown, no backticks, no explanation.

Required JSON structure:
{{
    "title": "exact job title",
    "company": "company name if mentioned",
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill1", "skill2"],
    "experience_years_min": 0,
    "experience_years_max": 3,
    "education_required": "Bachelor's in Computer Science or similar",
    "job_type": "full-time",
    "location": "city or remote",
    "salary_min": null,
    "salary_max": null,
    "currency": null,
    "key_responsibilities": ["responsibility1", "responsibility2"]
}}

Job Description:
{jd_text}

Extract ALL technical skills, tools, frameworks, and technologies mentioned.
Separate required from preferred/nice-to-have skills.
If salary is not mentioned use null."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    requirements = json.loads(text)
    return requirements


def calculate_match_score(profile: dict, requirements: dict) -> dict:
    """
    Calculates match score between resume profile and job requirements.
    Uses Gemini for semantic matching — catches synonyms like
    "ML" matching "machine learning", "Py" matching "Python".
    Returns score and detailed breakdown.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""You are a technical recruiter evaluating a candidate for a job.

CANDIDATE PROFILE:
Skills: {profile.get("skills", [])}
Experience: {profile.get("experience_years", 0)} years
Projects: {[p.get("name") for p in profile.get("projects", [])]}
Technologies used in projects: {[t for p in profile.get("projects", []) for t in p.get("technologies", [])]}

JOB REQUIREMENTS:
Required Skills: {requirements.get("required_skills", [])}
Preferred Skills: {requirements.get("preferred_skills", [])}
Experience Required: {requirements.get("experience_years_min", 0)}-{requirements.get("experience_years_max", 5)} years
Role: {requirements.get("title", "")}

Calculate a match score from 0 to 100.
Return ONLY valid JSON with no markdown:

{{
    "match_score": 75,
    "matched_skills": ["skill1", "skill2"],
    "missing_required_skills": ["skill1"],
    "missing_preferred_skills": ["skill1"],
    "experience_match": true,
    "score_breakdown": {{
        "required_skills_score": 80,
        "preferred_skills_score": 60,
        "experience_score": 90,
        "overall": 75
    }},
    "recommendation": "Strong match. Apply immediately.",
    "improvement_suggestions": ["Learn Docker", "Add SQL projects to portfolio"]
}}

Be semantic in matching — Python matches py, ML matches machine learning,
NLP matches natural language processing."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    match_result = json.loads(text)
    return match_result


if __name__ == "__main__":
    # Test with a sample resume
    import sys

    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py path/to/resume.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    print("Parsing resume...")
    profile = parse_resume(pdf_path)
    print(f"Name: {profile.get('name')}")
    print(f"Skills found: {len(profile.get('skills', []))}")
    print(f"Skills: {profile.get('skills', [])}")
    print(f"Experience: {profile.get('experience_years')} years")

    # Test with a sample JD
    sample_jd = """
    We are looking for a Data Analyst with 1-3 years of experience.
    Required: Python, SQL, Excel, Power BI or Tableau
    Nice to have: Machine Learning, pandas, numpy
    Location: Mumbai (Hybrid)
    You will analyze business data, create dashboards, and present insights.
    """

    print("\nExtracting job requirements...")
    requirements = extract_job_requirements(sample_jd)
    print(f"Required skills: {requirements.get('required_skills')}")

    print("\nCalculating match score...")
    match = calculate_match_score(profile, requirements)
    print(f"Match score: {match.get('match_score')}")
    print(f"Missing skills: {match.get('missing_required_skills')}")
    print(f"Recommendation: {match.get('recommendation')}")
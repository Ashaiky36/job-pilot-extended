from google import genai        # Google Gen-AI client library for interacting with Gemini models.    
from google.genai import types      # types module for creating content parts (like PDF bytes)
import json
import os
from pathlib import Path        # For file-path handling
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))      # Initialize Gemini client Api from environment variables.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")       # Get model name from env variable.


def parse_resume(pdf_path: str) -> dict:        
    """
    Sends resume PDF to Gemini and extracts structured profile data.
    """
    pdf_bytes = Path(pdf_path).read_bytes()     # read the reusme.pdf file as bytes

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
Extract ALL skills mentioned anywhere including project descriptions."""

    # Send request to Gemini model to analyze the PDF and extract info.
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf"
            ),
            prompt
        ]
    )

    # Get the response text and remove any whitespace from start/end
    text = response.text.strip()
    # Remove any markdown code block markers that might wrap the JSON
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        # Parse the cleaned text into a Python dictionary using JSON
        profile = json.loads(text)
    except json.JSONDecodeError:
        # If JSON parsing fails, print warning with first 500 chars of response
        print(f"[Warning] JSON parse failed. Raw response:\n{text[:500]}")
        # Return empty dictionary as fallback
        profile = {}

    return profile      # return the parsed profile dictionary.


def extract_job_requirements(jd_text: str) -> dict:
    """
    Extracts structured requirements from raw job description text.
    """
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

Extract ALL technical skills, tools, frameworks mentioned.
Separate required from preferred skills.
Use null for salary if not mentioned."""

    # Send request to Gemini with just the prompt(no files needed)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    # Cleaning the response by removing whitespce
    text = response.text.strip()
    # Remove any markdown code block markers
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        # Parse cleaned text into Python dictionary
        requirements = json.loads(text)
    except json.JSONDecodeError:
        print(f"[Warning] JSON parse failed. Raw response:\n{text[:500]}")
        requirements = {}

    return requirements


def calculate_match_score(profile: dict, requirements: dict) -> dict:
    """
    Uses Gemini semantic matching to score resume against job.
    """
    prompt = f"""You are a technical recruiter evaluating a candidate.

CANDIDATE PROFILE:
Skills: {profile.get("skills", [])}
Experience: {profile.get("experience_years", 0)} years
Project technologies: {[t for p in profile.get("projects", []) for t in p.get("technologies", [])]}

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
    "improvement_suggestions": ["Learn Docker", "Add SQL projects"]
}}

Use semantic matching — PyTorch matches deep learning frameworks,
pandas matches python libraries, SQL matches database querying."""

    # Send request to Gemini to calculate match score
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    # Clean the response text
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        # Parse JSON response into Python dictionary
        match_result = json.loads(text)
    except json.JSONDecodeError:
        print(f"[Warning] JSON parse failed. Raw response:\n{text[:500]}")
        match_result = {"match_score": 0}

    return match_result

# This block executes only when the script is run directly (not imported)
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py path/to/resume.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    print("Parsing resume...")
    profile = parse_resume(pdf_path)    # Call parse_resume function with PDF path
    print(f"\nName: {profile.get('name')}")
    print(f"Skills found: {len(profile.get('skills', []))}")
    print(f"Skills: {profile.get('skills', [])}")
    print(f"Experience: {profile.get('experience_years')} years")
    print(f"Projects: {[p.get('name') for p in profile.get('projects', [])]}")

    print("\n--- Testing JD Extraction ---")
    sample_jd = """
    We are looking for a Data Analyst with 1-3 years of experience.
    Required: Python, SQL, Excel, Power BI or Tableau
    Nice to have: Machine Learning, pandas, numpy
    Location: Mumbai (Hybrid)
    You will analyze business data, create dashboards, and present insights.
    """

    requirements = extract_job_requirements(sample_jd)
    print(f"Required skills: {requirements.get('required_skills')}")
    print(f"Preferred skills: {requirements.get('preferred_skills')}")

    print("\n--- Testing Match Score ---")
    match = calculate_match_score(profile, requirements)
    print(f"Match score: {match.get('match_score')}")
    print(f"Matched skills: {match.get('matched_skills')}")
    print(f"Missing skills: {match.get('missing_required_skills')}")
    print(f"Recommendation: {match.get('recommendation')}")
    print(f"Suggestions: {match.get('improvement_suggestions')}")
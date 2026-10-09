# This file is the main entry point for the FastAPI backend application. It sets up the API endpoints, initializes the database, and handles job fetching, resume parsing, and matching logic.

import os       # used for interacting with the operating system, such as file and directory operations.      
import sys
import json
import asyncio      # used for writing asynchronous code, allowing for concurrent execution of tasks.
import requests     # used for making HTTP requests to external APIs or services.
from concurrent.futures import ThreadPoolExecutor       # used for managing a pool of threads to execute tasks concurrently, improving performance for I/O-bound operations.
from fastapi import FastAPI, HTTPException, UploadFile, File, Form      # used for creating the FastAPI application, handling HTTP exceptions, and managing file uploads and form data.
from fastapi.middleware.cors import CORSMiddleware      # used for enabling Cross-Origin Resource Sharing (CORS) to allow requests from different origins.
from fastapi.staticfiles import StaticFiles     # used for serving static files, such as HTML, CSS, and JavaScript, from a specified directory.
from fastapi.responses import FileResponse      # used for sending files as responses to client requests.
from pydantic import BaseModel      # used for data validation and serialization of request and response models in FastAPI.
from bs4 import BeautifulSoup       # used for parsing and navigating HTML and XML documents, often used for web scraping.
import uvicorn      # used for running the FastAPI application with an ASGI server, providing high performance and support for asynchronous operations.

sys.path.append(os.path.dirname(__file__))      # adds the current directory to the Python module search path, allowing for importing modules from the same directory.

from database import (      # used for interacting with the database, including initializing the database, saving profiles and jobs, retrieving unprocessed jobs, getting matches, fetching dashboard statistics, managing connections, and handling tracked companies.
    init_database, save_profile, save_jobs, get_unprocessed_jobs, get_matches,
    get_dashboard_stats, get_connection, save_tracked_company, get_tracked_companies,
    update_company_crawl_status
)
from job_fetcher import fetch_all_jobs, is_relevant_job     # used for fetching job listings from external sources and determining if a job is relevant based on certain criteria.
from resume_parser import parse_resume
from matcher import run_matching_pipeline

app = FastAPI(      # initializes the FastAPI application with metadata such as title, description, and version.
    title = "JobPilot API",
    description = "AI-powered job discovery and application system",
    version = "1.0.0"
)

app.add_middleware(     # adds middleware to the FastAPI application to handle Cross-Origin Resource Sharing (CORS), allowing requests from any origin and supporting credentials, methods, and headers.
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

executor = ThreadPoolExecutor(max_workers=3)        # used for managing a pool of threads to execute tasks concurrently, allowing for efficient handling of I/O-bound operations and improving the performance of the application.

class RunPipelineRequest(BaseModel):      # defines a Pydantic model for the request body of the /run_pipeline endpoint, containing a single field for the resume file path.
    batch_size: int = 20        # defines the batch size(batch size means the number of jobs processed in each batch) for processing jobs in the matching pipeline, with a default value of 20.

class ApplyRequest(BaseModel):      # defines a Pydantic model for the request body of the /apply endpoint, containing fields for the job ID and resume file path.
    job_id: int
    status: str
    notes: str = ""

class AddCompanyRequest(BaseModel):      # defines a Pydantic model for the request body of the /add_company endpoint, containing a single field for the company name.
    name: str
    careers_url: str = ""

# Now, defining the API endpoints for the FastAPI application.
@app.get("/")       # defines a GET endpoint at the root URL ("/") that returns a simple JSON message indicating that the JobPilot API is running.
async def serve_frontend():     # serves the frontend of the application by checking if the index.html file exists in the frontend directory. If it does, it returns the file as a response; otherwise, it returns a JSON message indicating that the JobPilot API is running.
    index_path = os.path.join(FRONTEND_DIR, "index.html")       # defines the path to the index.html file in the frontend directory, which is used to serve the frontend of the application when a request is made to the root URL ("/").
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "JobPilot API is running."}

@app.get("/health")     # defines a GET endpoint at "/health" that returns a JSON message indicating that the API is healthy and running.
async def health():
    return {"status": "healthy", "stats": get_dashboard_stats()}        # returns a JSON response containing the health status of the API and relevant dashboard statistics, which can be used for monitoring and diagnostics.

@app.post("/upload_resume")      # defines a POST endpoint at "/upload_resume" that accepts a resume file upload, saves the file to the assets directory, and returns the file path as a JSON response.
async def upload_resume(        # the endpoint accepts a file upload and an optional role type (defaulting to "data_analyst"). It checks if the uploaded file is of a valid type (PDF or DOCX) and raises an HTTP exception if not.
    file: UploadFile = File(...),       # defines the file parameter as an UploadFile object, which represents the uploaded resume file. The File(...) indicates that this parameter is required and must be provided in the request.
    role_type: str = Form(default="data_analyst")
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")

    pdf_path = os.path.join(ASSETS_DIR, file.filename)      # defines the path where the uploaded resume file will be saved in the assets directory. It uses the original filename of the uploaded file to create the full path.
    content = await file.read()     # reads the content of the uploaded file asynchronously, allowing for efficient handling of file uploads without blocking the main thread. This is particularly useful for large files or high-concurrency scenarios.
    with open(pdf_path, "wb") as f:     # opens the specified file path in write-binary mode, allowing for writing the content of the uploaded file to the server's filesystem. The "wb" mode ensures that the file is created if it doesn't exist and that any existing content is overwritten.
        f.write(content)

    try:
        loop = asyncio.get_event_loop()      # retrieves the current event loop for asynchronous operations. If no event loop is running, it creates a new one. This is necessary for running asynchronous tasks in the FastAPI application.
        profile = await loop.run_in_executor(executor, lambda: parse_resume(pdf_path))      # parses the uploaded resume file using the parse_resume function in a separate thread from the thread pool executor. This allows for non-blocking execution of the resume parsing logic, improving performance and responsiveness of the API.
        profile_id = save_profile(profile, role_type, pdf_path)      # saves the parsed profile data to the database and retrieves the unique profile ID assigned to the saved profile. This ID can be used for future reference or retrieval of the profile data.

        return {
            "success": True,
            "profile_id": profile_id,
            "name": profile.get("name"),
            "skills_found": len(profile.get("skills", [])),
            "skills": profile.get("skills", []),
            "experience_years": profile.get("experience_years", 0),
            "role_type": role_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}"
        )

@app.post("/fetch_jobs")      # defines a POST endpoint at "/fetch_jobs" that fetches job listings from external sources, filters them based on relevance, saves the relevant jobs to the database, and returns the count of fetched and saved jobs as a JSON response.
async def fetch_jobs_endpoint():
    try:
        loop = asyncio.get_event_loop()      # retrieves the current event loop for asynchronous operations. If no event loop is running, it creates a new one. This is necessary for running asynchronous tasks in the FastAPI application.
        jobs = await loop.run_in_executor(executor, fetch_all_jobs)      # fetches all job listings from external sources using the fetch_all_jobs function in a separate thread from the thread pool executor. This allows for non-blocking execution of the job fetching logic, improving performance and responsiveness of the API.
        new_count = save_jobs(jobs)      # saves the fetched job listings to the database and retrieves the count of newly saved jobs. This count can be used for reporting or monitoring purposes.
        return {
            "success": True,
            "total_fetched": len(jobs),
            "new_jobs": new_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job fetching failed: {str(e)}")

@app.post("/run_matching")      # defines a POST endpoint at "/run_matching" that runs the matching pipeline for a given profile ID and batch size, returning the count of matched jobs as a JSON response.
async def run_matching(request: RunPipelineRequest):
    try:
        loop = asyncio.get_event_loop()      # retrieves the current event loop for asynchronous operations. If no event loop is running, it creates a new one. This is necessary for running asynchronous tasks in the FastAPI application.
        results = await loop.run_in_executor(executor, lambda: run_matching_pipeline(request.batch_size))      # runs the matching pipeline using the run_matching_pipeline function in a separate thread from the thread pool executor. This allows for non-blocking execution of the matching logic, improving performance and responsiveness of the API.
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching pipeline failed: {str(e)}")

@app.get("/jobs")      # defines a GET endpoint at "/jobs" that retrieves unprocessed job listings from the database and returns them as a JSON response.
async def get_jobs(priority: str = None, limit: int = 50):    # the endpoint accepts optional query parameters for filtering jobs by priority and limiting the number of returned jobs. The default limit is set to 50.
    try:
        jobs = get_matches(priority = priority, limit = limit)      # retrieves unprocessed job listings from the database based on the specified priority and limit. This allows for efficient retrieval of job data for further processing or display.
        return {
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

@app.get("/stats")
async def get_stats():      # defines a GET endpoint at "/stats" that retrieves dashboard statistics from the database and returns them as a JSON response.
    return get_dashboard_stats()

@app.post("/apply/{job_id}")        # defines a POST endpoint at "/apply/{job_id}" that applies job applications for a given job ID, saving the application details to the database and returning a success response.
async def mark_applied(job_id: int, request: ApplyRequest):     # the endpoint accepts a job ID as a path parameter and an ApplyRequest object in the request body, which contains the application status and optional notes. It saves the application details to the database and returns a success response.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications
            (job_id, profile_id, status, method, applied_at, notes)
        VALUES (?, 1, ?, 'MANUAL', CURRENT_TIMESTAMP, ?)
    """, (job_id, request.status, request.notes))
    conn.commit()
    conn.close()
    return {"success": True, "job_id": job_id}

@app.get("/applications")       # defines a GET endpoint at "/applications" that retrieves all job applications from the database and returns them as a JSON response.
async def get_applications():       # the endpoint fetches all job applications from the database, joining the applications table with the jobs table to include job details such as title, company, URL, and location. The results are ordered by creation date in descending order and converted into a list of dictionaries for easy JSON serialization. It returns a JSON response containing a list of job applications, including details such as application ID, status, method, applied date, notes, job title, company name, job URL, and location.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.status, a.method, a.applied_at, a.notes,
               j.title, j.company, j.url, j.location
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.created_at DESC
    """)
    apps = [dict(row) for row in cursor.fetchall()]     # fetches all job applications from the database, joining the applications table with the jobs table to include job details such as title, company, URL, and location. The results are ordered by creation date in descending order and converted into a list of dictionaries for easy JSON serialization.
    conn.close()
    return {"applications": apps}       # returns a JSON response containing a list of job applications, including details such as application ID, status, method, applied date, notes, job title, company name, job URL, and location. The applications are ordered by creation date in descending order.

@app.post("/companies/add")     # defines a POST endpoint at "/companies/add" that adds a new company to the tracked companies list in the database, saving the company details and returning a success response.
async def add_company(request: AddCompanyRequest):      # the endpoint accepts an AddCompanyRequest
    """
    User adds a company to track.
    System auto-detects careers URL if not provided.
    Tests crawlability immediately.

    """
    name = request.name.strip()     # strips whitespace from the company name
    careers_url = request.careers_url.strip()     # strips whitespace from the careers URL

    # Auto-detect careers URL if not provided
    if not careers_url:
        guesses = [
            f"https://{name.lower().replace(' ', '')}.com/careers",
            f"https://{name.lower().replace(' ', '')}.in/careers",
            f"https://careers.{name.lower().replace(' ', '')}.com",
        ]
        for guess in guesses:       # iterates through a list of guessed careers URLs based on the company name, attempting to find a valid URL by making HTTP GET requests to each guess. If a valid URL is found (status code 200), it is set as the careers URL for the company.
            try:
                r = requests.get(guess, timeout=5)
                if r.status_code == 200:
                    careers_url = guess
                    break
            except Exception:
                continue

    # Test crawlability of the careers URL
    crawlable = False
    note = ""
    jobs_found = 0

    if careers_url:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(
                careers_url, headers=headers, timeout=10
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                body_text = soup.get_text()

                # Check if it has meaningful content
                if len(body_text) > 500:
                    # Look for job-related links
                    job_links = soup.find_all("a", href=True)
                    relevant = [
                        l for l in job_links
                        if is_relevant_job(l.get_text(strip=True))
                    ]
                    jobs_found = len(relevant)

                    if jobs_found > 0:
                        crawlable = True
                        note = f"Found {jobs_found} relevant job links"
                    else:
                        # Check if JS-rendered
                        has_react = (
                            'id="root"' in response.text or
                            'id="app"' in response.text or
                            "data-reactroot" in response.text
                        )
                        if has_react:
                            crawlable = False
                            note = (
                                "JavaScript-rendered page — "
                                "cannot auto-fetch. "
                                "Please visit the careers page manually."
                            )
                        else:
                            crawlable = True
                            note = "Page accessible but no data roles found currently"
                else:
                    crawlable = False
                    note = "Page returned minimal content — may require login"

            elif response.status_code == 403:
                crawlable = False
                note = "Access blocked (403) — this company does not allow automated access"
            elif response.status_code == 404:
                crawlable = False
                note = "Careers page not found — please provide the exact URL"
            else:
                crawlable = False
                note = f"Unexpected response: {response.status_code}"

        except Exception as e:
            crawlable = False
            note = f"Could not reach careers page — {str(e)}"
    else:
        crawlable = False
        note = "Could not auto-detect careers URL — please provide it manually"

    # Save to database
    company_id = save_tracked_company(name, careers_url)
    update_company_crawl_status(company_id, crawlable, note)

    return {
        "success": True,
        "company_id": company_id,
        "name": name,
        "careers_url": careers_url,
        "crawlable": crawlable,
        "jobs_found": jobs_found,
        "note": note,
        "message": (
            f"✅ {name} is trackable — {jobs_found} relevant jobs found"
            if crawlable and jobs_found > 0
            else f"⚠️  {name}: {note}"
        )
    }

@app.get("/companies")      
async def list_companies():
    return {"companies": get_tracked_companies()}

@app.delete("/companies/{company_id}")
async def remove_company(company_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tracked_companies WHERE id = ?", (company_id,)
    )
    conn.commit()
    conn.close()
    return {"success": True}

if __name__ == "__main__":
    print("[Startup] Initialising database...")
    init_database()
    print("[Startup] Ready. Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)


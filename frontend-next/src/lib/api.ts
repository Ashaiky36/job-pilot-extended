const API_BASE = "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────
export interface DashboardStats {
  total_jobs: number;
  processed_jobs: number;
  high_priority: number;
  review: number;
  skipped: number;
  applications: number;
  by_source: Record<string, number>;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  url: string;
  source: string;
  salary_range: string;
  job_type: string;
  posted_at: string;
  match_score: number;
  matched_skills: string[];
  missing_required: string[];
  recommendation: string;
  improvement_suggestions: string[];
  priority: "HIGH" | "REVIEW" | "SKIPPED";
  matched_at: string;
}

export interface Application {
  id: number;
  status: string;
  method: string;
  applied_at: string;
  notes: string;
  title: string;
  company: string;
  url: string;
  location: string;
}

export interface Company {
  id: number;
  name: string;
  careers_url: string;
  status: string;
  crawlable: number;
  note: string;
  added_at: string;
}

export interface ResumeUploadResult {
  success: boolean;
  profile_id: number;
  name: string;
  skills_found: number;
  skills: string[];
  experience_years: number;
  role_type: string;
}

// ─── API Functions ───────────────────────────────────────────────────

export async function getStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function getJobs(
  priority?: string,
  limit: number = 50
): Promise<{ jobs: Job[]; count: number }> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (priority && priority !== "all") params.set("priority", priority);
  const res = await fetch(`${API_BASE}/jobs?${params}`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function fetchNewJobs(): Promise<{
  success: boolean;
  total_fetched: number;
  new_jobs: number;
}> {
  const res = await fetch(`${API_BASE}/fetch-jobs`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function runMatching(
  batchSize: number = 20
): Promise<{
  success: boolean;
  results: {
    processed: number;
    high_priority: number;
    review: number;
    skipped: number;
  };
}> {
  const res = await fetch(`${API_BASE}/run-matching`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ batch_size: batchSize }),
  });
  if (!res.ok) throw new Error("Failed to run matching");
  return res.json();
}

export async function markApplied(
  jobId: number,
  status: string = "APPLIED",
  notes: string = ""
): Promise<{ success: boolean; job_id: number }> {
  const res = await fetch(`${API_BASE}/apply/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id: jobId, status, notes }),
  });
  if (!res.ok) throw new Error("Failed to mark applied");
  return res.json();
}

export async function getApplications(): Promise<{
  applications: Application[];
}> {
  const res = await fetch(`${API_BASE}/applications`);
  if (!res.ok) throw new Error("Failed to fetch applications");
  return res.json();
}

export async function getCompanies(): Promise<{ companies: Company[] }> {
  const res = await fetch(`${API_BASE}/companies`);
  if (!res.ok) throw new Error("Failed to fetch companies");
  return res.json();
}

export async function addCompany(
  name: string,
  careersUrl: string = ""
): Promise<{
  success: boolean;
  company_id: number;
  name: string;
  careers_url: string;
  crawlable: boolean;
  jobs_found: number;
  note: string;
  message: string;
}> {
  const res = await fetch(`${API_BASE}/companies/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, careers_url: careersUrl }),
  });
  if (!res.ok) throw new Error("Failed to add company");
  return res.json();
}

export async function removeCompany(
  companyId: number
): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/companies/${companyId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to remove company");
  return res.json();
}

export async function uploadResume(
  file: File,
  roleType: string
): Promise<ResumeUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("role_type", roleType);
  const res = await fetch(`${API_BASE}/upload-resume`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

export async function sendNotifications(): Promise<{
  success: boolean;
  results: unknown;
}> {
  const res = await fetch(`${API_BASE}/send-notifications`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to send notifications");
  return res.json();
}

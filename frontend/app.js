const API = "http://localhost:8000";        // local backend API URL

// TAB NAVIGATION

// This function is called when a tab button is clicked. It shows the corresponding tab and loads its content.
function showTab(name) {        
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`tab-${name}`).classList.add('active');
    event.target.classList.add('active');

    if (name === 'dashboard') loadDashboard();
    if (name === 'jobs') loadJobs('all');
    if (name === 'applications') loadApplications();
    if (name === 'companies') loadCompanies();
}

// DASHBOARD
// This function loads the dashboard stats and high priority jobs from the backend API and updates the corresponding elements in the DOM.
async function loadDashboard() {        // Load dashboard stats and high priority jobs
    try {
        const res = await fetch(`${API}/stats`);
        const data = await res.json();

        document.getElementById('statTotal').textContent =
            data.total_jobs || 0;
        document.getElementById('statHigh').textContent =
            data.high_priority || 0;
        document.getElementById('statReview').textContent =
            data.review || 0;
        document.getElementById('statApps').textContent =
            data.applications || 0;

    } catch (err) {
        console.error('Stats load failed:', err);
    }

    // Load high priority jobs
    try {
        const res = await fetch(`${API}/jobs?priority=HIGH&limit=5`);
        const data = await res.json();      // Fetch high priority jobs with a limit of 5 in JSON format
        const container = document.getElementById('highPriorityList');      // Get the container element for high priority jobs of list

        if (data.jobs.length === 0) {
            container.innerHTML = '<div class="empty-state">No high priority jobs yet. Fetch jobs and run AI matching to get started.</div>';
        } else {
            container.innerHTML = data.jobs.map(renderJobCard).join('');
        }
    } catch (err) {
        console.error('High priority load failed:', err);
    }
}

// This function fetches jobs from all sources and updates the dashboard with the results.
async function fetchJobs() {
    setStatus('statusMsg', '🔍 Fetching jobs from all sources...', 'loading');

    try {
        const res = await fetch(`${API}/fetch-jobs`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            setStatus(
                'statusMsg',
                `✅ Fetched ${data.total_fetched} jobs, ${data.new_jobs} new added`,
                'success'
            );
            loadDashboard();
        }
    } catch (err) {
        setStatus('statusMsg', `❌ Fetch failed: ${err.message}`, 'error');
    }
}

// This function runs the AI matching algorithm on the fetched jobs and updates the dashboard with the results.
async function runMatching() {
    setStatus('statusMsg', '🤖 Running AI matching... this takes a few minutes', 'loading');

    try {
        const res = await fetch(`${API}/run-matching`, {        // Run AI matching on fetched jobs
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_size: 20 })
        });
        const data = await res.json();

        if (data.success) {
            const r = data.results;
            setStatus(
                'statusMsg',
                `✅ Matched ${r.processed} jobs - ${r.high_priority} high priority, ${r.review} review`,
                'success'
            );
            loadDashboard();
        }
    } catch (err) {
        setStatus('statusMsg', `❌ Matching failed: ${err.message}`, 'error');
    }
}

// JOBS
let currentFilter = 'all';

// This function loads jobs based on the selected filter and updates the job list in the DOM.
async function loadJobs(filter = 'all') {        // Load jobs based on the selected filter
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));        // Remove active class from all filter buttons
    event?.target?.classList.add('active');      // Add active class to the clicked filter button(here active class means the button is selected like a toggle button)

    const url = filter === 'all' ? `${API}/jobs?limit=50` : `${API}/jobs?priority=${filter}&limit=50`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        const container = document.getElementById('jobsList');

        if (data.jobs.length === 0) {
            container.innerHTML = '<div class="empty-state">No jobs found. Run job fetch and AI matching first.</div>';
        } else {
            container.innerHTML = data.jobs.map(renderJobCard).join('');
        }
    } catch (err) {
        console.error('Jobs load failed:', err);
    }
}

// This function filters all jobs and loads them
function filterJobs(filter) {
    loadJobs(filter);
}

function renderJobCard(job) {
    const isHigh = job.priority === 'HIGH';
    const scoreClass = isHigh ? 'score-high' : 'score-review';
    const cardClass = isHigh ? 'high' : 'review';

    const matchedSkills = (job.matched_skills || [])
        .slice(0, 5)
        .map(s => `<span class="skill-tag">${escHtml(s)}</span>`)
        .join('');

    const missingSkills = (job.missing_required || [])
        .slice(0, 3)
        .map(s => `<span class="skill-tag missing-tag">⚠ ${escHtml(s)}</span>`)
        .join('');

    const suggestions = (job.improvement_suggestions || [])
        .slice(0, 2)
        .map(s => `<li>${escHtml(s)}</li>`)
        .join('');

    return `
        <div class="job-card ${cardClass}">
            <div class="job-header">
                <div>
                    <div class="job-title">${escHtml(job.title || '')}</div>
                    <div class="job-company">${escHtml(job.company || 'Unknown company')}</div>
                </div>
                <span class="score-badge ${scoreClass}">
                    ${job.match_score || 0}% match
                </span>
            </div>
            <div class="job-meta">
                <span>📍 ${escHtml(job.location || '')}</span>
                <span>🏷 ${escHtml(job.source || '')}</span>
                ${job.salary_range ? `<span>💰 ${escHtml(job.salary_range)}</span>` : ''}
                ${job.job_type ? `<span>⏱ ${escHtml(job.job_type)}</span>` : ''}
            </div>
            <div class="skill-tags">${matchedSkills}${missingSkills}</div>
            ${job.recommendation
                ? `<div style="font-size:12px;color:var(--muted);margin-bottom:6px">${escHtml(job.recommendation)}</div>`
                : ''}
            ${suggestions
                ? `<ul style="font-size:12px;color:var(--muted);padding-left:16px;margin-bottom:8px">${suggestions}</ul>`
                : ''}
            <div class="job-actions">
                <a href="${job.url}" target="_blank" class="btn-sm btn-secondary" style="text-decoration:none;padding:5px 10px;font-size:12px;border:1px solid var(--border);border-radius:6px;color:var(--text)">
                    View Job ↗
                </a>
                <button class="btn-sm btn-apply" onclick="markApplied(${job.id})">
                    ✓ Mark Applied
                </button>
            </div>
        </div>
    `;
}


async function markApplied(jobId) {
    try {
        await fetch(`${API}/apply/${jobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                status: 'APPLIED',
                notes: ''
            })
        });
        loadDashboard();
        alert('Marked as applied!');
    } catch (err) {
        console.error('Apply failed:', err);
    }
}


// APPLICATIONS

async function loadApplications() {
    try {
        const res = await fetch(`${API}/applications`);
        const data = await res.json();
        const container = document.getElementById('applicationsList');

        if (data.applications.length === 0) {
            container.innerHTML = '<div class="empty-state">No applications tracked yet. Mark jobs as applied from the Jobs tab.</div>';
            return;
        }

        container.innerHTML = data.applications.map(app => `
            <div class="job-card">
                <div class="job-header">
                    <div>
                        <div class="job-title">${escHtml(app.title || '')}</div>
                        <div class="job-company">${escHtml(app.company || '')}</div>
                    </div>
                    <span class="score-badge score-high">${escHtml(app.status)}</span>
                </div>
                <div class="job-meta">
                    <span>📅 Applied: ${app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'N/A'}</span>
                    <span>🔧 ${escHtml(app.method || '')}</span>
                </div>
                <a href="${app.url}" target="_blank" style="font-size:12px;color:var(--accent)">View Job ↗</a>
            </div>
        `).join('');

    } catch (err) {
        console.error('Applications load failed:', err);
    }
}


// COMPANIES 

async function addCompany() {
    const name = document.getElementById('companyName').value.trim();
    const careersUrl = document.getElementById('companyCareersUrl').value.trim();

    if (!name) {
        setStatus('addCompanyStatus', 'Please enter a company name', 'error');
        return;
    }

    setStatus('addCompanyStatus', `🔍 Checking ${name} careers page...`, 'loading');

    try {
        const res = await fetch(`${API}/companies/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, careers_url: careersUrl })
        });
        const data = await res.json();

        setStatus(
            'addCompanyStatus',
            data.message,
            data.crawlable ? 'success' : 'error'
        );

        document.getElementById('companyName').value = '';
        document.getElementById('companyCareersUrl').value = '';
        loadCompanies();

    } catch (err) {
        setStatus('addCompanyStatus', `Failed: ${err.message}`, 'error');
    }
}


async function loadCompanies() {
    try {
        const res = await fetch(`${API}/companies`);
        const data = await res.json();
        const container = document.getElementById('companiesList');

        if (data.companies.length === 0) {
            container.innerHTML = '<div class="empty-state">No companies tracked yet. Add companies above.</div>';
            return;
        }

        container.innerHTML = data.companies.map(company => `
            <div class="company-card">
                <div>
                    <div class="company-name">${escHtml(company.name)}</div>
                    ${company.careers_url
                        ? `<a href="${company.careers_url}" target="_blank" style="font-size:12px;color:var(--accent)">${company.careers_url}</a>`
                        : '<span style="font-size:12px;color:var(--muted)">No URL found</span>'
                    }
                    ${company.note
                        ? `<div class="company-note">${escHtml(company.note)}</div>`
                        : ''
                    }
                </div>
                <div style="display:flex;align-items:center;gap:12px">
                    <span class="company-status ${company.crawlable ? 'status-ok' : 'status-blocked'}">
                        ${company.crawlable ? '✅ Trackable' : '⚠️ Manual'}
                    </span>
                    <button
                        class="btn-sm btn-secondary"
                        onclick="removeCompany(${company.id})"
                        style="font-size:11px"
                    >Remove</button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error('Companies load failed:', err);
    }
}


async function removeCompany(companyId) {
    await fetch(`${API}/companies/${companyId}`, { method: 'DELETE' });
    loadCompanies();
}


// RESUME UPLOAD

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('resumeFile');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) uploadResume(file);
        });
    }

    const uploadBox = document.getElementById('uploadBox');
    if (uploadBox) {
        uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadBox.style.borderColor = 'var(--accent)';
        });
        uploadBox.addEventListener('dragleave', () => {
            uploadBox.style.borderColor = 'var(--border)';
        });
        uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadBox.style.borderColor = 'var(--border)';
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.pdf')) uploadResume(file);
        });
    }

    loadDashboard();
});


// async function uploadResume(file) {
//     const roleType = document.getElementById('roleType').value;
//     setStatus('uploadStatus', `📤 Uploading ${file.name}...`, 'loading');

//     const formData = new FormData();
//     formData.append('file', file);
//     formData.append('role_type', roleType);

//     try {
//         const res = await fetch(`${API}/upload-resume`, {
//             method: 'POST',
//             body: formData
//         });
//         const data = await res.json();

//         if (data.success) {
//             setStatus(
//                 'uploadStatus',
//                 `✅ Resume uploaded for ${roleType.replace('_', ' ')}`,
//                 'success'
//             );

//             const preview = document.getElementById('resumePreview');
//             preview.classList.add('visible');
//             preview.innerHTML = `
//                 <strong>${escHtml(data.name || 'Your Profile')}</strong>
//                 <div style="margin-top:4px;color:var(--muted);font-size:12px">
//                     ${data.experience_years} years experience •
//                     ${data.skills_found} skills found
//                 </div>
//                 <div class="skill-list">
//                     ${(data.skills || []).slice(0, 15).map(s =>
//                         `<span class="skill-tag">${escHtml(s)}</span>`
//                     ).join('')}
//                 </div>
//             `;
//         }
//     } catch (err) {
//         setStatus('uploadStatus', `❌ Upload failed: ${err.message}`, 'error');
//     }
// }


async function uploadResume(file) {
    const roleType = document.getElementById('roleType').value;

    setStatus(
        'uploadStatus',
        `📤 Uploading ${file.name}...`,
        'loading'
    );

    const formData = new FormData();
    formData.append('file', file);
    formData.append('role_type', roleType);

    try {
        const res = await fetch(`${API}/upload-resume`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        // Display errors returned by FastAPI.
        if (!res.ok) {
            console.error('Resume upload error:', data);
            setStatus(
                'uploadStatus',
                `❌ ${data.detail || `Upload failed (${res.status})`}`,
                'error'
            );
            return;
        }

        if (data.success) {
            setStatus(
                'uploadStatus',
                `✅ Resume uploaded for ${roleType.replace('_', ' ')}`,
                'success'
            );

            const preview = document.getElementById('resumePreview');

            preview.classList.add('visible');
            preview.innerHTML = `
                <strong>${escHtml(data.name || 'Your Profile')}</strong>
                <div style="margin-top:4px;color:var(--muted);font-size:12px">
                    ${data.experience_years} years experience •
                    ${data.skills_found} skills found
                </div>
                <div class="skill-list">
                    ${(data.skills || []).slice(0, 15).map(s =>
                        `<span class="skill-tag">${escHtml(s)}</span>`
                    ).join('')}
                </div>
            `;
        }
    } catch (err) {
        console.error('Upload request failed:', err);
        setStatus(
            'uploadStatus',
            `❌ Upload failed: ${err.message}`,
            'error'
        );
    }
}



// UTILITIES 

function setStatus(elementId, message, type = '') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.className = `status-msg ${type}`;
}

function escHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(String(text || '')));
    return div.innerHTML;
}




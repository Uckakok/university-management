/* admin.js */
'use strict';

const API = 'http://127.0.0.1:8000';

/* ─────────────────────────────────────────
   Toast notification system
───────────────────────────────────────── */
function toast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  el.innerHTML = `<span>${icons[type] ?? 'ℹ'}</span><span>${escapeHtml(message)}</span>`;
  container.appendChild(el);
  // auto-remove
  const remove = () => {
    el.classList.add('out');
    el.addEventListener('animationend', () => el.remove(), { once: true });
  };
  const timer = setTimeout(remove, 4000);
  el.addEventListener('click', () => { clearTimeout(timer); remove(); });
}

/* ─────────────────────────────────────────
   Utilities
───────────────────────────────────────── */
function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/[&<>"']/g, m =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}

function getToken() { return sessionStorage.getItem('token'); }

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (options.json) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.json);
    delete options.json;
  }
  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

/* ─────────────────────────────────────────
   View routing
───────────────────────────────────────── */
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function setNavAuth(authed) {
  document.getElementById('nav-dashboard').style.display = authed ? '' : 'none';
  document.getElementById('nav-logout').style.display   = authed ? '' : 'none';
}

/* ─────────────────────────────────────────
   Auth
───────────────────────────────────────── */
async function login() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  if (!username || !password) { toast('Please enter your credentials.', 'error'); return; }

  const btn = document.getElementById('login-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Authenticating…';

  try {
    const form = new URLSearchParams({ username: username, password: password });
    const { ok, data } = await apiFetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    if (!ok) throw new Error(data.detail || 'Invalid credentials');
    sessionStorage.setItem('token', data.access_token);
    setNavAuth(true);
    await openDashboard();
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Sign in';
  }
}

function logout() {
  sessionStorage.removeItem('token');
  setNavAuth(false);
  showView('login-view');
  toast('Signed out successfully.', 'info');
}

/* ─────────────────────────────────────────
   Dashboard
───────────────────────────────────────── */
async function openDashboard() {
  showView('dashboard-view');

  // Admin identity
  try {
    const { ok, data } = await apiFetch('/get_dashboard_data');
    if (ok) {
      document.getElementById('admin-badge').textContent = `${data.login} — Administrator`;
    }
  } catch { /* silent */ }

  await Promise.all([loadRegistrations(), loadApplications()]);
  switchTab('registrations');
}

/* ─────────────────────────────────────────
   Tab switching
───────────────────────────────────────── */
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active-tab'));

  document.querySelector(`[data-tab="${name}"]`).classList.add('active');
  document.getElementById(`tab-${name}`).classList.add('active-tab');
}

/* ─────────────────────────────────────────
   Registrations
───────────────────────────────────────── */
async function loadRegistrations() {
  const container = document.getElementById('registrations-list');
  container.innerHTML = stateBox('⏳', 'Fetching registrations…');

  try {
    const { ok, data } = await apiFetch('/get_registrations');
    if (!ok) throw new Error(data.detail || 'Failed to load');

    const list = data.registrations || [];
    if (!list.length) {
      container.innerHTML = stateBox('📭', 'No active registrations found.');
      return;
    }
    container.innerHTML = '';
    list.forEach(reg => container.appendChild(buildRegistrationCard(reg)));
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

function buildRegistrationCard(reg) {
  const card = document.createElement('div');
  card.className = 'reg-card';
  card.dataset.regId = reg.id_registration;

  card.innerHTML = `
    <div class="reg-card-header">
      <span class="card-title">${escapeHtml(reg.course_name || 'Unnamed Course')}</span>
      <span class="card-meta">Reg #${reg.id_registration}</span>
    </div>
    <div class="card-details">
      <div class="detail-row"><strong>Student</strong>${escapeHtml(reg.name)} ${escapeHtml(reg.surname)} (ID ${reg.id_student})</div>
      <div class="detail-row"><strong>Course in Cycle</strong>${reg.id_course_in_cycle}</div>
    </div>
    <div class="divider"></div>
    <div class="grade-panel">
      <h4>Issue Grade</h4>
      <div class="grade-row">
        <div class="field"><input type="text" id="gv-${reg.id_registration}" placeholder="e.g. 5.0, 4.5, 3.0, 2.0" maxlength="8"></div>
        <div class="field" style="flex:2"><input type="text" id="gc-${reg.id_registration}" placeholder="Optional comment"></div>
      </div>
      <label class="checkbox-label">
        <input type="checkbox" id="gp-${reg.id_registration}">
        Mark as positive (pass) — also completes this course
      </label>
      <div class="action-row">
        <button class="btn btn-sm btn-primary"
          onclick="issueGrade(${reg.id_registration}, ${reg.id_student}, ${reg.id_course_in_cycle})">
          Issue Grade
        </button>
        <button class="btn btn-sm btn-warning"
          onclick="completeCourseOnly(${reg.id_student}, ${reg.id_course_in_cycle})">
          Complete (no grade)
        </button>
        <button class="btn btn-sm btn-ghost"
          onclick="semesterTransition(${reg.id_student})">
          Semester Transition
        </button>
      </div>
    </div>
  `;
  return card;
}

async function issueGrade(regId, studentId, cicId) {
  const gradeValue = document.getElementById(`gv-${regId}`).value.trim();
  const comment    = document.getElementById(`gc-${regId}`).value.trim() || 'No comment';
  const positive   = document.getElementById(`gp-${regId}`).checked;

  if (!gradeValue) { toast('Please enter a grade value.', 'error'); return; }
  if (!confirm(`Issue grade "${gradeValue}" for registration #${regId}?${positive ? '\n\nCourse will also be marked as completed.' : ''}`)) return;

  try {
    const { ok, data } = await apiFetch('/issue_grade', {
      method: 'POST',
      json: { id_registration: regId, grade_value: gradeValue, comment },
    });
    if (!ok) throw new Error(data.detail || 'Grade failed');
    toast(`Grade "${gradeValue}" issued for registration #${regId}.`, 'success');

    if (positive) await completeCourse(studentId, cicId, true);
    await loadRegistrations();
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function completeCourseOnly(studentId, cicId) {
  if (!confirm(`Complete course (cycle ID ${cicId}) for student ${studentId} without issuing a grade?`)) return;
  await completeCourse(studentId, cicId);
  await loadRegistrations();
}

async function completeCourse(studentId, cicId, silent = false) {
  try {
    const { ok, data } = await apiFetch('/complete_course', {
      method: 'POST',
      json: { id_student: Number(studentId), id_course_in_cycle: Number(cicId) },
    });
    if (!ok) throw new Error(data.detail || 'Complete course failed');
    if (!silent) toast(`Course completed for student ${studentId}.`, 'success');
  } catch (err) {
    toast(err.message, 'error');
    throw err;
  }
}

async function semesterTransition(studentId) {
  if (!confirm(`Process semester transition for student ID ${studentId}?\n\nThis will advance their academic progress based on completed courses.`)) return;
  try {
    const { ok, data } = await apiFetch('/process_semester_transition', {
      method: 'POST',
      json: { id_student: studentId },
    });
    if (!ok) throw new Error(data.detail || 'Transition failed');
    toast(`Semester transition processed for student ${studentId}.`, 'success');
    await loadRegistrations();
  } catch (err) {
    toast(err.message, 'error');
  }
}

/* ─────────────────────────────────────────
   Applications
───────────────────────────────────────── */
async function loadApplications() {
  const container = document.getElementById('applications-list');
  container.innerHTML = stateBox('⏳', 'Loading applications…');

  try {
    const { ok, data } = await apiFetch('/get_applications');
    if (!ok) throw new Error(data.detail || 'Failed to load');

    const list = data.applications || [];
    if (!list.length) {
      container.innerHTML = stateBox('📭', 'No applications found.');
      return;
    }
    container.innerHTML = '';
    list.forEach(app => container.appendChild(buildApplicationCard(app)));
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

function buildApplicationCard(app) {
  const card = document.createElement('div');
  card.className = 'reg-card card-orange';

  const status = (app.status || 'pending').toLowerCase();
  const isPending = status === 'pending';
  const badgeClass = status === 'accepted' || status === 'approved' ? 'badge-accepted'
    : status === 'rejected' ? 'badge-rejected' : 'badge-pending';

  const motivation = (app.motivation_letter || 'No motivation provided').substring(0, 240);
  const submitted  = app.submitted_at ? new Date(app.submitted_at).toLocaleString() : 'N/A';

  card.innerHTML = `
    <div class="reg-card-header">
      <span class="card-title">${escapeHtml(app.programme_name || 'Unknown Programme')}</span>
      <span class="badge ${badgeClass}">${escapeHtml(app.status || 'Pending')}</span>
    </div>
    <div class="card-details">
      <div class="detail-row"><strong>Applicant</strong>${escapeHtml(app.student_name || `ID ${app.id_student}`)}</div>
      <div class="detail-row"><strong>Submitted</strong>${submitted}</div>
      <div class="detail-row"><strong>Application ID</strong>#${app.id_application}</div>
    </div>
    <div class="motivation-box">"${escapeHtml(motivation)}${motivation.length === 240 ? '…' : ''}"</div>
    <div class="action-row" style="margin-top:14px;">
      ${isPending
        ? `<button class="btn btn-sm btn-success" onclick="acceptApplication(${app.id_application})">Accept</button>
           <button class="btn btn-sm btn-danger"  onclick="rejectApplication(${app.id_application})">Reject</button>`
        : `<button class="btn btn-sm" disabled style="opacity:.45;cursor:not-allowed;background:var(--bg-surface);border:1px solid var(--border);color:var(--text-muted);">${escapeHtml(app.status)}</button>`}
    </div>
  `;
  return card;
}

async function acceptApplication(id) {
  if (!confirm(`Accept application #${id}?`)) return;
  try {
    const { ok, data } = await apiFetch('/approve_application', { method: 'POST', json: { id_application: id } });
    if (!ok) throw new Error(data.detail || 'Failed');
    toast(`Application #${id} accepted.`, 'success');
    await loadApplications();
  } catch (err) { toast(err.message, 'error'); }
}

async function rejectApplication(id) {
  if (!confirm(`Reject application #${id}?`)) return;
  try {
    const { ok, data } = await apiFetch('/reject_application', { method: 'POST', json: { id_application: id } });
    if (!ok) throw new Error(data.detail || 'Failed');
    toast(`Application #${id} rejected.`, 'info');
    await loadApplications();
  } catch (err) { toast(err.message, 'error'); }
}

/* ─────────────────────────────────────────
   Helpers
───────────────────────────────────────── */
function stateBox(icon, text) {
  return `<div class="state-box"><span class="state-icon">${icon}</span>${escapeHtml(text)}</div>`;
}

/* ─────────────────────────────────────────
   Boot
───────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', async () => {
  const token = getToken();
  setNavAuth(!!token);

  if (token) {
    try {
      const { ok } = await apiFetch('/get_dashboard_data');
      if (ok) { await openDashboard(); return; }
    } catch { /* fall through */ }
    sessionStorage.removeItem('token');
    setNavAuth(false);
  }
  showView('login-view');
});

/* expose to inline onclick handlers */
Object.assign(window, {
  login, logout, openDashboard,
  switchTab,
  loadRegistrations, issueGrade, completeCourseOnly, semesterTransition,
  loadApplications, acceptApplication, rejectApplication,
});
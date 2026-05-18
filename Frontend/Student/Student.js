/* student.js */
'use strict';

const API = 'http://127.0.0.1:8000';

/* ─────────────────────────────────────────
   Toast
───────────────────────────────────────── */
function toast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  el.innerHTML = `<span>${icons[type] ?? 'ℹ'}</span><span>${escapeHtml(message)}</span>`;
  container.appendChild(el);
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
  if (options.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.json);
    delete options.json;
  }
  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

function stateBox(icon, text) {
  return `<div class="state-box"><span class="state-icon">${icon}</span>${escapeHtml(text)}</div>`;
}

/* ─────────────────────────────────────────
   View routing
───────────────────────────────────────── */
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');

  // highlight active nav link
  document.querySelectorAll('.nav-link[data-view]').forEach(a => {
    a.classList.toggle('active', a.dataset.view === id);
  });
}

function setNavAuth(authed) {
  document.getElementById('nav-dashboard').style.display = authed ? '' : 'none';
  document.getElementById('nav-logout').style.display   = authed ? '' : 'none';
  document.getElementById('nav-sep').style.display      = authed ? '' : 'none';
  document.getElementById('nav-login').style.display    = authed ? 'none' : '';
  document.getElementById('nav-register').style.display = authed ? 'none' : '';
}

/* ─────────────────────────────────────────
   Auth — Register
───────────────────────────────────────── */
async function register() {
  const name        = document.getElementById('reg-name').value.trim();
  const secondName  = document.getElementById('reg-second-name').value.trim();
  const surname     = document.getElementById('reg-surname').value.trim();
  const gender      = document.getElementById('reg-gender').value;
  const login       = document.getElementById('reg-login').value.trim();
  const password    = document.getElementById('reg-password').value;

  if (!name || !surname || !gender || !login || !password) {
    toast('Please fill in all required fields.', 'error');
    return;
  }

  const btn = document.getElementById('reg-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Creating account…';

  try {
    const { ok, data } = await apiFetch('/register', {
      method: 'POST',
      json: { name, second_name: secondName, surname, gender, login, password: password },
    });
    if (!ok) throw new Error(
      Array.isArray(data.detail)
        ? data.detail.map(e => `${e.loc?.[1] ?? 'field'}: ${e.msg}`).join(', ')
        : data.detail || 'Registration failed'
    );
    toast('Account created! You can now sign in.', 'success');
    showView('login-view');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create account';
  }
}

/* ─────────────────────────────────────────
   Auth — Login
───────────────────────────────────────── */
async function login() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  if (!username || !password) { toast('Please enter your credentials.', 'error'); return; }

  const btn = document.getElementById('login-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Signing in…';

  try {
    const form = new URLSearchParams({ username, password: password });
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
    btn.textContent = 'Sign in';
  }
}

function logout() {
  sessionStorage.removeItem('token');
  setNavAuth(false);
  showView('login-view');
  toast('Signed out.', 'info');
}

/* ─────────────────────────────────────────
   Dashboard
───────────────────────────────────────── */
async function openDashboard() {
  showView('dashboard-view');

  const { ok, data } = await apiFetch('/get_dashboard_data').catch(() => ({ ok: false, data: {} }));

  if (!ok) {
    toast('Could not load your profile.', 'error');
    return;
  }

  // User badge
  document.getElementById('user-badge').textContent = data.login || 'Student';

  // Status bar
  const statusText = document.getElementById('status-text');
  const statusDot  = document.getElementById('status-dot');

  if (!data.has_profile) {
    statusText.textContent = 'No candidate profile — complete your application to get started.';
    statusDot.className = 'status-dot yellow';
    showPanel('panel-profile');
    hidePanel('panel-programmes');
    hidePanel('panel-courses');
    hidePanel('panel-applications');
  } else {
    statusText.textContent = 'Candidate profile active.';
    statusDot.className = 'status-dot green';
    hidePanel('panel-profile');
    showPanel('panel-programmes');
    showPanel('panel-courses');
    showPanel('panel-applications');
    // Kick off background loads
    loadProgrammes();
  }
}

/* ─────────────────────────────────────────
   Panel helpers
───────────────────────────────────────── */
function showPanel(id) { document.getElementById(id).style.display = ''; }
function hidePanel(id) { document.getElementById(id).style.display = 'none'; }

function togglePanel(id) {
  const panel = document.getElementById(id);
  panel.classList.toggle('open');
}

/* ─────────────────────────────────────────
   Candidate profile
───────────────────────────────────────── */
async function submitCandidateProfile() {
  const fields = ['can-nationality', 'can-pesel', 'can-email', 'can-phone', 'can-address'];
  const [nationality, pesel, email_address, phone_number, address] =
    fields.map(id => document.getElementById(id).value.trim());

  if (!nationality || !pesel || !email_address || !phone_number || !address) {
    toast('Please fill in all fields.', 'error');
    return;
  }

  const btn = document.getElementById('profile-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Submitting…';

  try {
    const { ok, data } = await apiFetch('/register_candidate', {
      method: 'POST',
      json: { nationality, pesel, email_address, phone_number, address },
    });
    if (!ok) throw new Error(
      Array.isArray(data.detail)
        ? data.detail[0]?.msg || JSON.stringify(data.detail)
        : data.detail || 'Submission failed'
    );
    toast('Candidate profile created!', 'success');
    await openDashboard();
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit profile';
  }
}

/* ─────────────────────────────────────────
   Programmes
───────────────────────────────────────── */
async function loadProgrammes() {
  const container = document.getElementById('programmes-list');
  container.innerHTML = stateBox('⏳', 'Loading programmes…');

  try {
    const { ok, data } = await apiFetch('/get_available_programmes');
    if (!ok) throw new Error(data.detail || 'Failed to load');

    const list = data.programmes || [];
    if (!list.length) {
      container.innerHTML = stateBox('📭', 'No programmes available right now.');
      return;
    }

    container.innerHTML = '';
    list.forEach(p => {
      const card = document.createElement('div');
      card.className = 'programme-card';
      card.innerHTML = `
        <div class="prog-name">${escapeHtml(p.programme_name)}</div>
        <div class="prog-meta">
          <span>🏛 ${escapeHtml(p.department_name)}</span>
          <span>🎓 ${escapeHtml(p.degree)}</span>
          <span>🌐 ${escapeHtml(p.language)}</span>
        </div>
        <div class="apply-hint">Click to apply →</div>
      `;
      card.addEventListener('click', () => openApplyModal(p.id_programme, p.programme_name));
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

/* ─────────────────────────────────────────
   Apply modal (replaces browser prompt())
───────────────────────────────────────── */
let _pendingProgrammeId = null;

function openApplyModal(programmeId, programmeName) {
  _pendingProgrammeId = programmeId;
  document.getElementById('modal-prog-name').textContent = programmeName;
  document.getElementById('modal-motivation').value = '';
  document.getElementById('apply-modal').classList.remove('hidden');
  document.getElementById('modal-motivation').focus();
}

function closeApplyModal() {
  document.getElementById('apply-modal').classList.add('hidden');
  _pendingProgrammeId = null;
}

async function submitApplication() {
  const motivation = document.getElementById('modal-motivation').value.trim();
  if (!motivation) { toast('Please write a motivation letter.', 'error'); return; }

  const btn = document.getElementById('modal-submit-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Submitting…';

  try {
    const { ok, data } = await apiFetch('/submit_application', {
      method: 'POST',
      json: { id_programme: _pendingProgrammeId, motivation_letter: motivation },
    });
    if (!ok) throw new Error(data.detail || 'Submission failed');
    toast('Application submitted!', 'success');
    closeApplyModal();
    // Reload applications if panel is open
    if (document.getElementById('panel-applications').classList.contains('open')) {
      loadApplications();
    }
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit application';
  }
}

/* ─────────────────────────────────────────
   Applications
───────────────────────────────────────── */
async function loadApplications() {
  const container = document.getElementById('applications-list');
  container.innerHTML = stateBox('⏳', 'Loading applications…');

  try {
    const { ok, data } = await apiFetch('/view_applications');
    if (!ok) throw new Error(data.detail || 'Failed');

    const list = data.applications || [];
    if (!list.length) {
      container.innerHTML = stateBox('📭', 'No applications yet. Apply to a programme above.');
      return;
    }

    container.innerHTML = '';
    list.forEach(a => {
      const status = (a.status || 'pending').toLowerCase();
      const badgeClass = status === 'accepted' || status === 'approved' ? 'badge-accepted'
        : status === 'rejected' ? 'badge-rejected' : 'badge-pending';
      const submitted = a.submitted_at ? new Date(a.submitted_at).toLocaleDateString() : 'N/A';
      const processed = a.processed_at ? new Date(a.processed_at).toLocaleDateString() : '—';
      const motivation = (a.motivation_letter || '').substring(0, 280);

      const card = document.createElement('div');
      card.className = 'application-card';
      card.innerHTML = `
        <div class="app-header">
          <span class="app-name">${escapeHtml(a.programme_name)}</span>
          <span class="badge ${badgeClass}">${escapeHtml(a.status || 'Pending')}</span>
        </div>
        <div class="app-meta">Submitted ${submitted} · Processed ${processed}</div>
        <div class="motivation-box">"${escapeHtml(motivation)}${motivation.length === 280 ? '…' : ''}"</div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

/* ─────────────────────────────────────────
   Courses — current
───────────────────────────────────────── */
async function loadCurrentCourses() {
  const container = document.getElementById('current-courses-list');
  container.innerHTML = stateBox('⏳', 'Loading your courses…');

  try {
    const { ok, data } = await apiFetch('/get_current_courses');
    if (!ok) throw new Error(data.detail || 'Failed');

    const courses = data.current_courses || [];
    if (!courses.length) {
      container.innerHTML = stateBox('📭', 'You are not enrolled in any courses yet.');
      return;
    }

    const enrolled  = courses.filter(c => c.course_status === 'current');
    const completed = courses.filter(c => c.course_status === 'completed');
    container.innerHTML = '';

    if (enrolled.length) {
      container.innerHTML += `<div class="sub-title">Currently enrolled</div>`;
      enrolled.forEach(c => container.appendChild(buildCourseCard(c, 'enrolled')));
    }
    if (completed.length) {
      container.innerHTML += `<div class="sub-title" style="margin-top:${enrolled.length ? '20' : '0'}px;">Completed</div>`;
      completed.forEach(c => container.appendChild(buildCourseCard(c, 'completed')));
    }
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

function buildCourseCard(c, type) {
  const card = document.createElement('div');
  card.className = `course-card ${type}`;

  let gradeHtml = '';
  if (c.grade_value) {
    const isPass = parseFloat(c.grade_value) >= 3.0;
    gradeHtml = `<span class="grade-pill ${isPass ? 'pass' : 'fail'}">${escapeHtml(c.grade_value)}</span>`;
    if (c.corrected_grade) gradeHtml += ` <span class="grade-pill pass">↗ ${escapeHtml(c.corrected_grade)}</span>`;
  } else {
    gradeHtml = `<span class="grade-pill none">Not graded</span>`;
  }

  const instructor = c.instructor_name ? escapeHtml(c.instructor_name) : 'Not assigned';
  const semester   = [c.semester_name, c.academic_year].filter(Boolean).map(escapeHtml).join(' ');
  const issuedAt   = c.issued_at ? ` · Issued ${new Date(c.issued_at).toLocaleDateString()}` : '';

  card.innerHTML = `
    <div class="course-name">
      ${escapeHtml(c.course_name)}
      ${c.course_code ? `<span class="course-code">${escapeHtml(c.course_code)}</span>` : ''}
    </div>
    <div class="course-meta">
      <span>📅 ${semester || '—'}</span>
      <span>👤 ${instructor}</span>
    </div>
    <div style="margin-top:6px;">${gradeHtml}${issuedAt}</div>
  `;
  return card;
}

/* ─────────────────────────────────────────
   Courses — eligible
───────────────────────────────────────── */
async function loadEligibleCourses() {
  const container = document.getElementById('eligible-courses-list');
  container.innerHTML = stateBox('⏳', 'Loading eligible courses…');

  try {
    const { ok, data } = await apiFetch('/get_eligible_courses');
    if (!ok) throw new Error(data.detail || 'Failed');

    const courses = data.eligible_courses || [];
    if (!courses.length) {
      container.innerHTML = stateBox('✨', 'No eligible courses available right now.');
      return;
    }

    container.innerHTML = `<div class="sub-title">Click a course to register</div>`;
    courses.forEach(c => {
      const isFull   = c.spots_left === 0;
      const spotsNum = c.spots_left;
      const spotsText = isFull ? 'Full' : (spotsNum > 0 ? `${spotsNum} spots left` : 'Open');

      const card = document.createElement('div');
      card.className = `course-card eligible${isFull ? ' full' : ''}`;

      card.innerHTML = `
        <div class="course-name">
          ${escapeHtml(c.course_name)}
          <span class="spots-badge ${isFull ? 'full' : 'ok'}">${spotsText}</span>
        </div>
        <div class="course-meta">
          <span>📂 ${escapeHtml(c.group_type || 'Standard')}</span>
        </div>
      `;

      if (!isFull) {
        card.addEventListener('click', () => confirmCourseRegistration(c.id_course_groupe, c.course_name));
      }
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = stateBox('⚠️', err.message);
    toast(err.message, 'error');
  }
}

async function confirmCourseRegistration(groupId, courseName) {
  if (!confirm(`Register for "${courseName}"?\n\nThis action cannot be undone.`)) return;

  toast(`Registering for ${courseName}…`, 'info');

  try {
    const { ok, data } = await apiFetch('/register_for_course', {
      method: 'POST',
      json: { course_id: groupId },
    });
    if (!ok) throw new Error(data.detail || 'Registration failed');
    toast(`Registered for ${courseName}!`, 'success');
    // Refresh both panels
    loadEligibleCourses();
    loadCurrentCourses();
  } catch (err) {
    toast(err.message, 'error');
  }
}

/* ─────────────────────────────────────────
   Panel toggle with lazy load
───────────────────────────────────────── */
function handlePanelToggle(panelId) {
  const panel = document.getElementById(panelId);
  panel.classList.toggle('open');
  if (!panel.classList.contains('open')) return;

  // Lazy-load content on first open
  switch (panelId) {
    case 'panel-programmes':   loadProgrammes();     break;
    case 'panel-applications': loadApplications();   break;
    case 'panel-current':      loadCurrentCourses(); break;
    case 'panel-eligible':     loadEligibleCourses();break;
  }
}

/* ─────────────────────────────────────────
   Boot
───────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', async () => {
  // Load gender options
  try {
    const res = await fetch(`${API}/metadata/genders`);
    if (res.ok) {
      const genders = await res.json();
      const sel = document.getElementById('reg-gender');
      genders.forEach(g => {
        const opt = document.createElement('option');
        opt.value = opt.textContent = g;
        sel.appendChild(opt);
      });
    }
  } catch { /* ignore */ }

  // Restore session
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

/* expose to HTML onclick / onkeydown */
Object.assign(window, {
  showView, login, logout, register, openDashboard,
  submitCandidateProfile,
  loadProgrammes, openApplyModal, closeApplyModal, submitApplication,
  loadApplications,
  loadCurrentCourses, loadEligibleCourses, confirmCourseRegistration,
  handlePanelToggle,
});
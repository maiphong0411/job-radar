const $ = (selector) => document.querySelector(selector);
const splitList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean);
const normalize = (value) => String(value ?? '').trim();
const tokenSet = (value) => new Set(normalize(value).toLowerCase().match(/[a-z0-9+#.]+/g)?.map((x) => x.replace(/^\.+|\.+$/g, '')) ?? []);
let analyzedJobs = [];

$('#chooseFile').addEventListener('click', () => $('#csvFile').click());
$('#csvFile').addEventListener('change', async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  $('#fileStatus').textContent = `${file.name} · ${(file.size / 1024).toFixed(1)} KB`;
  try {
    const rows = parseCsv(await file.text());
    analyzeRows(rows);
  } catch (error) {
    $('#fileStatus').textContent = `Could not read file: ${error.message}`;
  }
});

['titles', 'skills', 'locations'].forEach((id) => {
  $(`#${id}`).addEventListener('change', () => {
    if (window.currentRows) analyzeRows(window.currentRows);
  });
});
$('#filter').addEventListener('change', renderJobs);

function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i], next = text[i + 1];
    if (char === '"' && quoted && next === '"') { field += '"'; i += 1; }
    else if (char === '"') quoted = !quoted;
    else if (char === ',' && !quoted) { row.push(field); field = ''; }
    else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && next === '\n') i += 1;
      row.push(field); field = ''; if (row.some(Boolean)) rows.push(row); row = [];
    } else field += char;
  }
  row.push(field); if (row.some(Boolean)) rows.push(row);
  if (rows.length < 2) throw new Error('CSV has no data rows');
  const headers = rows.shift().map((header) => header.replace(/^\uFEFF/, '').trim());
  return rows.map((values) => Object.fromEntries(headers.map((header, index) => [header, normalize(values[index])])));
}

function pick(row, ...fields) { return fields.map((field) => row[field]).find(Boolean) ?? ''; }
function includesPhrase(text, phrase) { return text.toLowerCase().includes(phrase.toLowerCase()); }

function analyzeRows(rows) {
  window.currentRows = rows;
  const profile = {
    titles: splitList($('#titles').value), skills: splitList($('#skills').value),
    locations: splitList($('#locations').value)
  };
  analyzedJobs = rows.map((row) => ({
    title: pick(row, 'title', 'job_title'), company: pick(row, 'company', 'company_name'),
    location: pick(row, 'location', 'job_location'), description: pick(row, 'description', 'job_description'),
    url: pick(row, 'url', 'job_url', 'source_url'), evidence: pick(row, 'eligibility_evidence'),
    status: pick(row, 'status') || 'new'
  })).filter((job) => job.status.toLowerCase() !== 'closed').map((job) => scoreJob(job, profile))
    .sort((a, b) => b.score - a.score);
  $('#emptyState').hidden = true; $('#results').hidden = false;
  $('#activeCount').textContent = analyzedJobs.length;
  $('#applyCount').textContent = analyzedJobs.filter((job) => job.recommendation === 'apply_now').length;
  $('#averageScore').textContent = analyzedJobs.length ? Math.round(analyzedJobs.reduce((sum, job) => sum + job.score, 0) / analyzedJobs.length) : 0;
  renderJobs();
}

function scoreJob(job, profile) {
  const searchable = `${job.title} ${job.location} ${job.description} ${job.evidence}`;
  const tokens = tokenSet(searchable);
  const blockers = ['us only', 'united states only', 'must be located in the us', 'no international', 'not available in vietnam'];
  const eligible = !blockers.some((blocker) => `${job.location} ${job.evidence}`.toLowerCase().includes(blocker));
  const titleMatch = profile.titles.some((title) => includesPhrase(job.title, title));
  const locationMatch = profile.locations.some((location) => includesPhrase(`${job.location} ${job.evidence}`, location));
  const matchedSkills = profile.skills.filter((skill) => [...tokenSet(skill)].every((token) => tokens.has(token)));
  let score = Math.round(45 * matchedSkills.length / Math.max(profile.skills.length, 1) + 30 * Number(titleMatch) + 25 * Number(locationMatch));
  if (!eligible) score = Math.min(score, 39);
  const recommendation = !eligible ? 'skip' : score >= 80 ? 'apply_now' : score >= 60 ? 'review' : 'low_priority';
  return { ...job, score, eligible, matchedSkills, recommendation };
}

function renderJobs() {
  const filter = $('#filter').value;
  const jobs = analyzedJobs.filter((job) => filter === 'all' || job.recommendation === filter);
  $('#jobList').innerHTML = jobs.map((job) => `
    <article class="job">
      <div class="score">${job.score}</div>
      <div><h3>${escapeHtml(job.title || 'Untitled role')}</h3><p class="meta">${escapeHtml(job.company || 'Unknown company')} · ${escapeHtml(job.location || 'Location not listed')}</p>
      <div class="chips">${job.matchedSkills.map((skill) => `<span class="chip">${escapeHtml(skill)}</span>`).join('') || '<span class="chip">No profile skills detected</span>'}</div>
      ${safeUrl(job.url) ? `<a class="job-link" href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer">View original role ↗</a>` : ''}</div>
      <span class="action ${job.recommendation}">${job.recommendation.replace('_', ' ')}</span>
    </article>`).join('') || '<p>No jobs match this filter.</p>';
}

function safeUrl(value) { try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol); } catch { return false; } }
function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }

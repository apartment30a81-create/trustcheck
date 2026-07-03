/* =======================================
   TRUSTCHECK — Main Application
   ======================================= */

import { analyzeFile } from './metadata.js';
import { analyzeWithVenice, validateVeniceKey } from './venice-ai.js';

// State
let currentFile = null;
let currentResult = null;
let veniceConnected = false;
let veniceKey = localStorage.getItem('trustcheck-venice-key') || '';

// DOM refs
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const results = document.getElementById('results');
const meterScore = document.getElementById('meter-score');
const meterRing = document.getElementById('meter-ring');
const meterVerdict = document.getElementById('meter-verdict');
const verdictDot = document.getElementById('verdict-dot');
const verdictText = document.getElementById('verdict-text');
const verdictConfidence = document.getElementById('verdict-confidence');
const tags = document.getElementById('tags');
const evidenceList = document.getElementById('evidence-list');
const metadataTable = document.getElementById('metadata-table');
const detailsToggle = document.getElementById('details-toggle');
const toggleArrow = document.getElementById('toggle-arrow');
const detailsPanel = document.getElementById('details-panel');
const newBtn = document.getElementById('new-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

// Venice
const veniceKeyInput = document.getElementById('venice-key');
const veniceConnectBtn = document.getElementById('venice-connect-btn');
const veniceStatus = document.getElementById('venice-status');
const veniceStatusText = document.getElementById('venice-status-text');
const veniceResults = document.getElementById('venice-results');
const veniceEvidence = document.getElementById('venice-evidence');

// Quick panel Venice
const veniceKeyQuick = document.getElementById('venice-key-quick');
const veniceConnectQuickBtn = document.getElementById('venice-connect-quick-btn');
const venicePanelStatus = document.getElementById('venice-panel-status');

// Sync both inputs
function syncVeniceInputs() {
  if (veniceKeyQuick && veniceKey) {
    veniceKeyQuick.value = '•'.repeat(Math.min(veniceKey.length, 20));
    venicePanelStatus.textContent = '✅';
  } else if (veniceKeyQuick) {
    veniceKeyQuick.value = '';
    venicePanelStatus.textContent = '';
  }
}

// Tab switching
document.querySelectorAll('.detail-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
  });
});

// Details toggle
detailsToggle.addEventListener('click', () => {
  const isOpen = !detailsPanel.hidden;
  detailsPanel.hidden = isOpen;
  toggleArrow.classList.toggle('open', !isOpen);
});

// Upload handlers
dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
  if (e.target.files.length) handleFile(e.target.files[0]);
});

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

// New analysis
newBtn.addEventListener('click', resetUI);

// Venice
if (veniceKey) {
  veniceKeyInput.value = '•'.repeat(veniceKey.length);
  veniceConnected = true;
  showVeniceStatus('Connected');
}

veniceConnectBtn.addEventListener('click', handleVeniceConnect);
if (veniceConnectQuickBtn) {
  veniceConnectQuickBtn.addEventListener('click', () => {
    if (veniceKeyQuick) {
      veniceKeyInput.value = veniceKeyQuick.value;
    }
    handleVeniceConnect();
    syncVeniceInputs();
  });
}

// Sync initial state
syncVeniceInputs();

/* ---- Core Logic ---- */

async function handleFile(file) {
  currentFile = file;
  statusDot.className = 'status-dot analyzing';
  statusText.textContent = 'Analyzing...';
  uploadSection.hidden = true;
  results.hidden = false;
  detailsPanel.hidden = true;
  veniceResults.hidden = true;

  // Show analyzing state on meter
  meterScore.textContent = '...';
  meterScore.style.color = 'var(--text-muted)';
  meterRing.style.background = 'conic-gradient(var(--border) 0% 100%)';
  meterVerdict.style.background = 'transparent';

  // Run analysis
  const result = await analyzeFile(file);
  currentResult = result;

  // Update UI with local-only results
  renderMeter(result);
  renderTags(result.tags);
  renderEvidence(result.evidence);
  renderFileMetadata(file);
  renderFileName(file);

  // Run Venice AI analysis automatically if connected
  if (veniceConnected && file.type.startsWith('image/')) {
    statusText.textContent = 'Running deep AI analysis...';
    const veniceResult = await runVeniceAnalysis(file, true);
    if (veniceResult) {
      // Merge Venice results into main score
      mergeVeniceIntoMain(result, veniceResult);
      // Re-render with merged data
      renderMeter(result);
      renderTags(result.tags);
      renderEvidence(result.evidence);
      // Add Venice enhanced badge
      addVeniceBadge();
    }
  }

  statusDot.className = 'status-dot';
  statusText.textContent = 'Complete';
}

function renderMeter(result) {
  const score = result.trustScore;
  meterScore.textContent = score + '%';
  meterScore.style.color = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)';

  // Ring colors
  const color = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)';
  meterRing.style.background = `conic-gradient(${color} 0% ${score}%, var(--border) ${score}% 100%)`;

  // Verdict
  const verdictColor = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)';
  const verdictBg = score >= 70 ? 'var(--success-muted)' : score >= 40 ? 'var(--warning-muted)' : 'var(--danger-muted)';

  meterVerdict.style.background = verdictBg;
  verdictDot.style.background = verdictColor;
  verdictText.textContent = result.verdict;
  verdictText.style.color = verdictColor;
  verdictConfidence.textContent = score >= 70 ? '✓ Consistent' : score >= 40 ? '⚠ Further verification needed' : 'AI artifacts detected';
}

function renderTags(tagList) {
  tags.innerHTML = '';
  tagList.forEach((t, i) => {
    const el = document.createElement('span');
    el.className = `tag ${t.type}`;
    el.textContent = t.label;
    el.style.animationDelay = `${i * 80}ms`;
    tags.appendChild(el);
  });
}

function renderEvidence(evidence) {
  evidenceList.innerHTML = '';
  evidence.forEach(item => {
    const el = document.createElement('div');
    el.className = `evidence-item ${item.severity}`;
    el.innerHTML = `
      <div class="evidence-left">
        <div class="evidence-label">${item.label}</div>
        <div class="evidence-desc">${item.desc}</div>
      </div>
      ${item.score !== null ? `<div class="evidence-score ${item.severity}">${Math.round(item.score)}%</div>` : ''}
    `;
    evidenceList.appendChild(el);
  });
}

function renderFileMetadata(file) {
  const rows = [
    { label: 'File name', value: file.name },
    { label: 'File size', value: formatSize(file.size) },
    { label: 'File type', value: file.type || 'Unknown' },
    { label: 'Last modified', value: new Date(file.lastModified).toLocaleDateString() },
    { label: 'Analysis mode', value: 'Local (privacy-first)' }
  ];

  metadataTable.innerHTML = '';
  rows.forEach(row => {
    const el = document.createElement('div');
    el.className = 'metadata-row';
    el.innerHTML = `
      <span class="metadata-label">${row.label}</span>
      <span class="metadata-value">${row.value}</span>
    `;
    metadataTable.appendChild(el);
  });
}

function renderFileName(file) {
  // Update status text to show file name
  statusText.textContent = file.name;
}

/* ---- Venice AI ---- */

function showVeniceStatus(msg) {
  veniceStatus.hidden = false;
  veniceStatusText.textContent = msg;
}

async function runVeniceAnalysis(file, autoMerge = false) {
  if (!veniceConnected || !veniceKey) return null;

  if (!autoMerge) {
    // Manual mode: show in Venice tab
    veniceResults.hidden = false;
  }
  veniceEvidence.innerHTML = '<p style="color:var(--text-muted);font-size:0.875rem">Running AI analysis...</p>';

  try {
    const result = await analyzeWithVenice(veniceKey, file);
    if (autoMerge) return result;

    // Manual mode UI update (existing behavior)
    veniceEvidence.innerHTML = '';
    if (result.is_ai_generated !== null) {
      const summaryEl = document.createElement('div');
      summaryEl.className = `evidence-item ${result.is_ai_generated ? 'high' : 'clean'}`;
      summaryEl.innerHTML = `
        <div class="evidence-left">
          <div class="evidence-label">Overall Assessment</div>
          <div class="evidence-desc">${result.summary || ''}</div>
        </div>
        <div class="evidence-score ${result.is_ai_generated ? 'high' : 'clean'}">${result.confidence_percent}%</div>
      `;
      veniceEvidence.appendChild(summaryEl);
    }
    if (result.evidence) {
      result.evidence.forEach(item => {
        const el = document.createElement('div');
        el.className = `evidence-item ${item.severity === 'high' ? 'high' : item.severity === 'medium' ? 'medium' : 'low'}`;
        el.innerHTML = `
          <div class="evidence-left">
            <div class="evidence-label">${item.finding}</div>
            <div class="evidence-desc">${item.explanation || ''}</div>
          </div>`;
        veniceEvidence.appendChild(el);
      });
    }
    return null;
  } catch (err) {
    veniceEvidence.innerHTML = `<p style="color:var(--danger);font-size:0.875rem">Error: ${err.message}</p>`;
    return null;
  }
}

/**
 * Merge Venice AI results into the main analytics result object
 */
function mergeVeniceIntoMain(result, veniceResult) {
  if (!veniceResult || veniceResult.is_ai_generated === null) return;

  const aiScore = veniceResult.confidence_percent;
  const localScore = result.trustScore;

  // Weighted blend: 60% local, 40% Venice
  const blendedScore = localScore * 0.6 + (100 - aiScore) * 0.4;
  result.trustScore = Math.max(0, Math.min(100, Math.round(blendedScore)));

  // Update verdict
  result.verdict = result.trustScore >= 70 ? 'Likely Authentic'
    : result.trustScore >= 40 ? 'Uncertain'
    : 'Likely AI-Generated';

  // Add Venice evidence to main list
  result.evidence.push({
    label: 'Venice AI Vision Analysis',
    desc: veniceResult.summary || `${aiScore}% AI probability`,
    severity: aiScore > 70 ? 'high' : aiScore > 40 ? 'medium' : 'clean',
    score: aiScore
  });

  // Add Venice tag
  result.tags.push({ label: '🧠 AI Analyzed', type: aiScore > 50 ? 'ai' : 'clean' });

  // Update analysis mode metadata
  const modeRow = document.querySelector('.metadata-row:last-child');
  if (modeRow) {
    modeRow.querySelector('.metadata-value').textContent = 'Local + Venice AI';
  }
}

/**
 * Show "Venice Enhanced" badge on the meter
 */
function addVeniceBadge() {
  const existing = document.querySelector('.venice-enhanced-badge');
  if (existing) return;

  const badge = document.createElement('div');
  badge.className = 'venice-enhanced-badge';
  badge.innerHTML = '🧠 Venice AI Enhanced';
  badge.style.cssText = `
    display: inline-flex; align-items: center; gap: 4px;
    margin-top: 12px; padding: 6px 14px;
    border-radius: 20px; font-size: 0.8125rem; font-weight: 500;
    background: var(--primary-muted); color: var(--primary);
    animation: fadeUp 300ms ease;
  `;
  document.querySelector('.meter-section').appendChild(badge);
}

// Update handleVeniceConnect to re-run on existing file
async function handleVeniceConnect() {
  const key = veniceKeyInput.value.trim();

  if (veniceConnected) {
    veniceConnected = false;
    veniceKey = '';
    localStorage.removeItem('trustcheck-venice-key');
    veniceStatus.hidden = true;
    veniceConnectBtn.textContent = 'Connect';
    veniceResults.hidden = true;
    veniceKeyInput.value = '';
    document.querySelector('.venice-enhanced-badge')?.remove();
    syncVeniceInputs();
    return;
  }

  if (!key) return;

  veniceConnectBtn.textContent = 'Verifying...';
  veniceConnectBtn.disabled = true;

  const valid = await validateVeniceKey(key);
  if (valid) {
    veniceConnected = true;
    veniceKey = key;
    localStorage.setItem('trustcheck-venice-key', key);
    showVeniceStatus('Connected');
    veniceConnectBtn.textContent = 'Disconnect';
    veniceConnectBtn.disabled = false;
    syncVeniceInputs();

    if (currentFile && currentFile.type.startsWith('image/') && currentResult) {
      statusText.textContent = 'Running deep AI analysis...';
      const veniceResult = await runVeniceAnalysis(currentFile, true);
      if (veniceResult) {
        mergeVeniceIntoMain(currentResult, veniceResult);
        renderMeter(currentResult);
        renderTags(currentResult.tags);
        renderEvidence(currentResult.evidence);
        addVeniceBadge();
        statusText.textContent = 'Complete';
      }
    }
  } else {
    veniceConnectBtn.textContent = 'Invalid key';
    setTimeout(() => {
      veniceConnectBtn.textContent = 'Connect';
      veniceConnectBtn.disabled = false;
    }, 2000);
  }
}

/* ---- Helpers ---- */

function formatSize(bytes) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / 1048576).toFixed(1) + 'MB';
}

function resetUI() {
  currentFile = null;
  currentResult = null;
  uploadSection.hidden = false;
  results.hidden = true;
  fileInput.value = '';
  statusDot.className = 'status-dot';
  statusText.textContent = 'Ready';
  veniceResults.hidden = true;
}

// Keyboard accessibility for dropzone
dropzone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
});
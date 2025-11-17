// --- Demo Data (fallback if flat files can't be loaded) -----------------
const DemoData = {
  incidents: [
    {
      id: "INC-1023",
      title: "Suspicious PowerShell Activity on DC01",
      severity: "High",
      status: "In Progress",
      owner: "analyst.jane",
      source: "EDR",
      createdAt: "2025-11-13T09:02:00Z",
      updatedAt: "2025-11-13T10:15:00Z",
      tags: ["PowerShell", "EDR", "Lateral Movement"],
      relatedAlerts: ["ALRT-4432", "ALRT-4438"],
      fullText:
        "Incident INC-1023\n\nSummary:\nEDR detected suspicious PowerShell command execution on DC01.\n\nDetails:\n- Encoded PowerShell launched from Office macro.\n- Network connections to rare external IPs.\n- Mimikatz-like strings observed in memory.\n\nPlanned Actions:\n- Isolate host.\n- Collect memory image.\n- Reset domain admin credentials if compromise confirmed.",
      notes: []
    },
    {
      id: "INC-1024",
      title: "Multiple Failed Logons from Rare Country",
      severity: "Medium",
      status: "New",
      owner: "unassigned",
      source: "SIEM",
      createdAt: "2025-11-13T07:12:00Z",
      updatedAt: "2025-11-13T07:12:00Z",
      tags: ["Authentication", "Geo Anomaly"],
      relatedAlerts: ["ALRT-4440"],
      fullText:
        "SIEM use case 'Rare Country Logins' fired multiple times against user HR-USER-12.\n\nAuthentication attempts from IPs in a country not seen in the last 90 days.\n\nUser is normally office-based with no travel scheduled.",
      notes: []
    },
    {
      id: "INC-1025",
      title: "Possible Phishing Campaign via O365",
      severity: "Critical",
      status: "New",
      owner: "analyst.mike",
      source: "EmailSec",
      createdAt: "2025-11-13T06:45:00Z",
      updatedAt: "2025-11-13T06:50:00Z",
      tags: ["Phishing", "O365", "Credential Theft"],
      relatedAlerts: ["ALRT-4441", "ALRT-4442"],
      fullText:
        "Email security gateway detected multiple inbound messages with suspicious links imitating MFA prompts.\n\nTargets include finance and executive assistants.\nLanding pages observed collecting O365 credentials.\n\nBlocklist has been updated and retroactive search performed.",
      notes: []
    }
  ],
  alerts: [
    {
      id: "ALRT-4432",
      rule: "Suspicious PowerShell Command Line",
      severity: "High",
      status: "Escalated",
      source: "EDR",
      firstSeen: "2025-11-13T08:55:00Z",
      lastSeen: "2025-11-13T09:10:00Z",
      count: 12,
      assetId: "ASSET-01",
      incidentId: "INC-1023",
      fullText:
        "Alert: Suspicious PowerShell Command Line\n\nEDR telemetry:\n- Parent process: WINWORD.EXE\n- Command line: powershell.exe -enc <redacted>\n- User: CORP\\jdoe\n- MITRE: T1059 PowerShell\n\nRaw JSON payload omitted for brevity.",
      notes: []
    },
    {
      id: "ALRT-4438",
      rule: "Powershell DownloadFile from Rare Domain",
      severity: "High",
      status: "New",
      source: "EDR",
      firstSeen: "2025-11-13T09:05:00Z",
      lastSeen: "2025-11-13T09:06:00Z",
      count: 3,
      assetId: "ASSET-01",
      incidentId: "INC-1023",
      fullText:
        "Detected PowerShell WebClient DownloadFile to https://example-bad-domain[.]com from DC01.\n\nUser: CORP\\jdoe\n\nHTTP headers and payload recorded in EDR telemetry.",
      notes: []
    },
    {
      id: "ALRT-4440",
      rule: "Rare Country Logins",
      severity: "Medium",
      status: "New",
      source: "SIEM",
      firstSeen: "2025-11-13T07:05:00Z",
      lastSeen: "2025-11-13T07:10:00Z",
      count: 5,
      assetId: "ASSET-03",
      incidentId: "INC-1024",
      fullText:
        "Multiple authentication failures from IP 203.0.113.10 (Country X) against HR-USER-12.\n\nGeo profile: Country X not seen in last 90 days for this user or peer group.\n\nSource: VPN gateway logs normalized in SIEM.",
      notes: []
    },
    {
      id: "ALRT-4441",
      rule: "Inbound Email with Suspicious MFA Link",
      severity: "Critical",
      status: "Escalated",
      source: "EmailSec",
      firstSeen: "2025-11-13T06:40:00Z",
      lastSeen: "2025-11-13T06:42:00Z",
      count: 18,
      assetId: "ASSET-02",
      incidentId: "INC-1025",
      fullText:
        "EmailSubject: 'Action Required: Confirm Your MFA Settings'\n\nLinks redirect through multiple URL shorteners to a fake O365 login page.\n\nDetection engine score: 95/100 (phishing).",
      notes: []
    },
    {
      id: "ALRT-4442",
      rule: "User Clicked Phishing Link",
      severity: "Critical",
      status: "New",
      source: "EmailSec",
      firstSeen: "2025-11-13T06:46:00Z",
      lastSeen: "2025-11-13T06:46:00Z",
      count: 4,
      assetId: "ASSET-02",
      incidentId: "INC-1025",
      fullText:
        "Click telemetry indicates that four users followed the phishing link within 5 minutes of delivery.\n\nNo MFA prompt observed downstream; credential theft suspected.",
      notes: []
    }
  ],
  assets: [
    {
      id: "ASSET-01",
      hostname: "DC01.internal.local",
      ip: "10.0.0.10",
      owner: "IT Ops",
      department: "Infrastructure",
      criticality: "Critical",
      os: "Windows Server 2019",
      lastSeen: "2025-11-13T10:00:00Z",
      alertCount: 15,
      incidentCount: 1,
      tags: ["Domain Controller", "AD", "Tier0"],
      fullText:
        "Domain controller for INTERNAL domain.\nHosts AD DS, DNS, and DHCP.\nConsidered Tier 0 / crown jewel asset.\n\nChange control required for all reboots and patches.",
      notes: [],
      retired: false
    },
    {
      id: "ASSET-02",
      hostname: "EXCH01.internal.local",
      ip: "10.0.0.20",
      owner: "Messaging",
      department: "IT",
      criticality: "High",
      os: "Windows Server 2016",
      lastSeen: "2025-11-13T09:45:00Z",
      alertCount: 8,
      incidentCount: 1,
      tags: ["Email", "O365 Hybrid"],
      fullText:
        "On-prem Exchange hybrid server.\nUsed for mail relay and coexistence with O365.\n\nAlerts here may indicate phishing campaigns or relay abuse.",
      notes: [],
      retired: false
    },
    {
      id: "ASSET-03",
      hostname: "VPN-GW01.internal.local",
      ip: "10.0.0.30",
      owner: "Network",
      department: "Infrastructure",
      criticality: "High",
      os: "Linux",
      lastSeen: "2025-11-13T09:55:00Z",
      alertCount: 12,
      incidentCount: 1,
      tags: ["VPN", "Remote Access"],
      fullText:
        "Primary VPN gateway for remote users.\nLogs feed directly into SIEM.\n\nFrequent target for credential stuffing and brute force attacks.",
      notes: [],
      retired: false
    }
  ],
  users: [
    {
      id: "USR-1001",
      name: "Jane Doe",
      email: "jane.doe@corp.local",
      role: "Incident Responder",
      department: "Security",
      privileged: true,
      lastLogon: "2025-11-13T10:05:00Z",
      lastDevice: "DC01.internal.local",
      lastLocation: "HQ SOC",
      phone: "+1-555-0101",
      retired: false
    },
    {
      id: "USR-1002",
      name: "Mike Lee",
      email: "mike.lee@corp.local",
      role: "SOC Engineer",
      department: "Security",
      privileged: false,
      lastLogon: "2025-11-13T08:20:00Z",
      lastDevice: "VPN-GW01.internal.local",
      lastLocation: "Remote (Seattle)",
      phone: "+1-555-0102",
      retired: false
    },
    {
      id: "USR-1003",
      name: "Priya Patel",
      email: "priya.patel@corp.local",
      role: "IR Manager",
      department: "Security",
      privileged: true,
      lastLogon: "2025-11-13T07:55:00Z",
      lastDevice: "Laptop-IR-03",
      lastLocation: "HQ SOC",
      phone: "+1-555-0103",
      retired: false
    }
  ]
};

const SAMPLE_DOWNLOAD_FILENAME = 'soc-dashboard-sample';
const REFRESH_INTERVAL_MS = 15 * 60 * 1000;

const ChartColors = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
  accent: '#4f8cff',
  neutral: '#94a3b8'
};

function getSampleDownloadContent(category = 'incidents') {
  const dataMap = {
    incidents: DemoData.incidents.slice(0, 2),
    alerts: DemoData.alerts.slice(0, 2),
    assets: DemoData.assets.slice(0, 2),
    users: DemoData.users.slice(0, 2)
  };
  const payload = dataMap[category] || [];
  return JSON.stringify(payload, null, 2);
}

// --- State & Storage ----------------------------------------------------
let refreshTimerId = null;
let refreshInProgress = false;

const state = {
  activeTab: 'overview',
  selectedItem: null,
  data: {
    incidents: [],
    alerts: [],
    assets: [],
    users: []
  },
  lastUpdated: null,
  notes: {
    perItem: {},
    perTab: {}
  },
  preferences: {
    theme: 'dark',
    lastTab: 'overview',
    analystName: 'Analyst'
  },
  filters: {
    incidents: { severity: 'all', status: 'all', search: '' },
    alerts: { severity: 'all', status: 'all', search: '' },
    assets: { criticality: 'all', search: '' }
  }
};

const Storage = {
  loadPreferences() {
    try {
      const raw = localStorage.getItem('socdash-preferences');
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  },
  savePreferences(prefs) {
    try {
      localStorage.setItem('socdash-preferences', JSON.stringify(prefs));
    } catch {}
  },
  loadNotes() {
    try {
      const raw = localStorage.getItem('socdash-notes');
      if (!raw) return { perItem: {}, perTab: {} };
      const parsed = JSON.parse(raw);
      if (!parsed.perItem) parsed.perItem = {};
      if (!parsed.perTab) parsed.perTab = {};
      return parsed;
    } catch {
      return { perItem: {}, perTab: {} };
    }
  },
  saveNotes(notes) {
    try {
      localStorage.setItem('socdash-notes', JSON.stringify(notes));
    } catch {}
  }
};

// --- Data Loading from Flat Files --------------------------------------
async function loadFlatData() {
  try {
    const [incRes, altRes, asRes, userRes] = await Promise.all([
      fetch('data/incidents.json'),
      fetch('data/alerts.json'),
      fetch('data/assets.json'),
      fetch('data/users.json')
    ]);

    if (!incRes.ok || !altRes.ok || !asRes.ok || !userRes.ok) {
      throw new Error('One or more data files missing');
    }

    const [incidents, alerts, assets, users] = await Promise.all([
      incRes.json(),
      altRes.json(),
      asRes.json(),
      userRes.json()
    ]);

    return {
      incidents,
      alerts,
      assets: normalizeAssets(assets),
      users: normalizeUsers(users)
    };
  } catch (err) {
    console.warn('Failed to load flat files; falling back to DemoData:', err);
    return {
      incidents: DemoData.incidents.map(item => ({ ...item })),
      alerts: DemoData.alerts.map(item => ({ ...item })),
      assets: normalizeAssets(DemoData.assets.map(item => ({ ...item }))),
      users: normalizeUsers(DemoData.users.map(item => ({ ...item })))
    };
  }
}

function applyLoadedData(loaded) {
  state.data.incidents = loaded.incidents || [];
  state.data.alerts = loaded.alerts || [];
  state.data.assets = normalizeAssets(loaded.assets || []);
  state.data.users = normalizeUsers(loaded.users || []);
}

// --- Init ---------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  init().catch(err => console.error('Init failed', err));
});

async function init() {
  // Load from flat files (or fallback)
  const loaded = await loadFlatData();
  applyLoadedData(loaded);

  const savedPrefs = Storage.loadPreferences();
  Object.assign(state.preferences, savedPrefs);

  const savedNotes = Storage.loadNotes();
  if (savedNotes && savedNotes.perItem && savedNotes.perTab) {
    state.notes = savedNotes;
  }

  applyTheme(state.preferences.theme);

  renderOverview();
  renderIncidents();
  renderAlerts();
  renderAssets();
  renderUsers();
  renderSettings();
  renderDashboard();
  markLastUpdated();

  setupTabNotes();
  bindTabEvents();
  bindDrawerEvents();
  bindDrawerTabEvents();
  bindSettingsEvents();
  bindUploadEvents();
  bindDownloadEvents();
  bindRefreshEvents();
  bindFilterEvents();
  bindAddEvents();
  startClock();
  updateLastUpdatedLabel();
  startAutoRefresh();

  setActiveTab(state.preferences.lastTab || 'overview');
}

// --- General UI helpers -------------------------------------------------
function setActiveTab(tabName) {
  state.activeTab = tabName;
  state.preferences.lastTab = tabName;
  Storage.savePreferences(state.preferences);

  document.querySelectorAll('.tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === 'tab-' + tabName);
  });

  if (tabName === 'dashboard') {
    renderDashboard();
  }
}

function applyTheme(theme) {
  const body = document.body;
  body.classList.remove('theme-dark', 'theme-light');
  if (theme === 'light') {
    body.classList.add('theme-light');
  } else {
    body.classList.add('theme-dark');
    theme = 'dark';
  }
  state.preferences.theme = theme;
  Storage.savePreferences(state.preferences);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.checked = theme === 'dark';
}

function bindTabEvents() {
  document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => setActiveTab(btn.dataset.tab));
  });
}

function startClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  function update() {
    const now = new Date();
    el.textContent = now.toLocaleTimeString();
  }
  update();
  setInterval(update, 1000);
}

// --- Filters ------------------------------------------------------------
function bindFilterEvents() {
  // Incidents
  const iSev = document.getElementById('incident-filter-severity');
  const iStat = document.getElementById('incident-filter-status');
  const iSearch = document.getElementById('incident-filter-search');
  if (iSev) iSev.addEventListener('change', () => {
    state.filters.incidents.severity = iSev.value;
    renderIncidents();
    renderOverview();
  });
  if (iStat) iStat.addEventListener('change', () => {
    state.filters.incidents.status = iStat.value;
    renderIncidents();
    renderOverview();
  });
  if (iSearch) iSearch.addEventListener('input', () => {
    state.filters.incidents.search = iSearch.value;
    renderIncidents();
  });

  // Alerts
  const aSev = document.getElementById('alert-filter-severity');
  const aStat = document.getElementById('alert-filter-status');
  const aSearch = document.getElementById('alert-filter-search');
  if (aSev) aSev.addEventListener('change', () => {
    state.filters.alerts.severity = aSev.value;
    renderAlerts();
    renderOverview();
  });
  if (aStat) aStat.addEventListener('change', () => {
    state.filters.alerts.status = aStat.value;
    renderAlerts();
  });
  if (aSearch) aSearch.addEventListener('input', () => {
    state.filters.alerts.search = aSearch.value;
    renderAlerts();
  });

  // Assets
  const asCrit = document.getElementById('asset-filter-criticality');
  const asSearch = document.getElementById('asset-filter-search');
  if (asCrit) asCrit.addEventListener('change', () => {
    state.filters.assets.criticality = asCrit.value;
    renderAssets();
  });
  if (asSearch) asSearch.addEventListener('input', () => {
    state.filters.assets.search = asSearch.value;
    renderAssets();
  });
}

function getFilteredIncidents() {
  const f = state.filters.incidents;
  return state.data.incidents.filter(inc => {
    if (f.severity !== 'all' && inc.severity !== f.severity) return false;
    if (f.status !== 'all' && inc.status !== f.status) return false;
    if (f.search) {
      const term = f.search.toLowerCase();
      const hay = (inc.id + ' ' + inc.title + ' ' + inc.owner + ' ' + inc.source).toLowerCase();
      if (!hay.includes(term)) return false;
    }
    return true;
  });
}

function getFilteredAlerts() {
  const f = state.filters.alerts;
  return state.data.alerts.filter(a => {
    if (f.severity !== 'all' && a.severity !== f.severity) return false;
    if (f.status !== 'all' && a.status !== f.status) return false;
    if (f.search) {
      const term = f.search.toLowerCase();
      const hay = (a.id + ' ' + a.rule + ' ' + a.source + ' ' + (a.assetId || '')).toLowerCase();
      if (!hay.includes(term)) return false;
    }
    return true;
  });
}

function getFilteredAssets() {
  const f = state.filters.assets;
  return state.data.assets.filter(as => {
    if (f.criticality !== 'all' && as.criticality !== f.criticality) return false;
    if (f.search) {
      const term = f.search.toLowerCase();
      const hay = (as.id + ' ' + as.hostname + ' ' + as.ip + ' ' + as.owner).toLowerCase();
      if (!hay.includes(term)) return false;
    }
    return true;
  });
}

// --- Overview Rendering -------------------------------------------------
function renderOverview() {
  const incidents = state.data.incidents;
  const alerts = state.data.alerts;

  const openIncidents = incidents.filter(i => i.status !== 'Closed');
  const criticalOpen = openIncidents.filter(i => i.severity === 'Critical').length;
  const highOpen = openIncidents.filter(i => i.severity === 'High').length;
  const mediumOpen = openIncidents.filter(i => i.severity === 'Medium').length;
  const lowOpen = openIncidents.filter(i => i.severity === 'Low').length;

  const kpisEl = document.getElementById('overview-kpis');
  if (kpisEl) {
    kpisEl.innerHTML = `
      <div class="card kpi">
        <div class="kpi-label">Open Incidents</div>
        <div class="kpi-value">${openIncidents.length}</div>
        <div class="kpi-sub">Critical: ${criticalOpen}, High: ${highOpen}, Med: ${mediumOpen}, Low: ${lowOpen}</div>
      </div>
      <div class="card kpi">
        <div class="kpi-label">Total Alerts</div>
        <div class="kpi-value">${alerts.length}</div>
        <div class="kpi-sub">Current dataset</div>
      </div>
      <div class="card kpi">
        <div class="kpi-label">Assets with Alerts</div>
        <div class="kpi-value">${new Set(alerts.map(a => a.assetId)).size}</div>
        <div class="kpi-sub">From current dataset</div>
      </div>
    `;
  }

  const newAlerts = alerts.filter(a => String(a.status || '').toLowerCase() === 'new').length;
  updateAlertsIndicator(newAlerts);

  const tbody = document.getElementById('overview-alerts-tbody');
  if (tbody) {
    tbody.innerHTML = '';
    const sortedAlerts = [...alerts].sort((a, b) =>
      new Date(b.lastSeen || b.firstSeen) - new Date(a.lastSeen || a.firstSeen)
    );
    sortedAlerts.slice(0, 5).forEach(alert => {
      const tr = document.createElement('tr');
      tr.dataset.id = alert.id;
      tr.innerHTML = `
        <td>${alert.id}</td>
        <td>${escapeHtml(alert.rule)}</td>
        <td>${renderSeverityBadge(alert.severity)}</td>
        <td>${escapeHtml(alert.source)}</td>
        <td>${formatShortDate(alert.lastSeen || alert.firstSeen)}</td>
      `;
      tr.addEventListener('click', () => openDrawerForItem('alert', alert.id));
      tbody.appendChild(tr);
    });
  }
}

// --- Incidents / Alerts / Assets Rendering -----------------------------
function renderIncidents() {
  const tbody = document.getElementById('incidents-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const incidents = getFilteredIncidents();
  incidents.forEach(incident => {
    const tr = document.createElement('tr');
    tr.dataset.id = incident.id;
    tr.innerHTML = `
      <td>${incident.id}</td>
      <td>${escapeHtml(incident.title)}</td>
      <td>${renderSeverityBadge(incident.severity)}</td>
      <td><span class="status-pill-small">${escapeHtml(incident.status)}</span></td>
      <td>${escapeHtml(incident.owner)}</td>
      <td>${escapeHtml(incident.source)}</td>
      <td>${formatShortDate(incident.createdAt)}</td>
      <td>
        <button class="btn btn-danger btn-small row-delete">Delete</button>
      </td>
    `;
    tr.addEventListener('click', (e) => {
      if (e.target && e.target.closest('.row-delete')) return;
      openDrawerForItem('incident', incident.id);
    });
    const delBtn = tr.querySelector('.row-delete');
    if (delBtn) {
      delBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteItem('incident', incident.id);
      });
    }
    tbody.appendChild(tr);
  });
}

function renderAlerts() {
  const tbody = document.getElementById('alerts-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const alerts = getFilteredAlerts();
  alerts.forEach(alert => {
    const tr = document.createElement('tr');
    tr.dataset.id = alert.id;
    tr.innerHTML = `
      <td>${alert.id}</td>
      <td>${escapeHtml(alert.rule)}</td>
      <td>${renderSeverityBadge(alert.severity)}</td>
      <td><span class="status-pill-small">${escapeHtml(alert.status)}</span></td>
      <td>${escapeHtml(alert.source)}</td>
      <td>${escapeHtml(alert.assetId || "")}</td>
      <td>${formatShortDate(alert.lastSeen || alert.firstSeen)}</td>
      <td>
        <button class="btn btn-danger btn-small row-delete">Delete</button>
      </td>
    `;
    tr.addEventListener('click', (e) => {
      if (e.target && e.target.closest('.row-delete')) return;
      openDrawerForItem('alert', alert.id);
    });
    const delBtn = tr.querySelector('.row-delete');
    if (delBtn) {
      delBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteItem('alert', alert.id);
      });
    }
    tbody.appendChild(tr);
  });
}

function renderAssets() {
  const tbody = document.getElementById('assets-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const assets = getFilteredAssets();
  assets.forEach(asset => {
    const tr = document.createElement('tr');
    tr.dataset.id = asset.id;
    tr.classList.toggle('row-retired', !!asset.retired);
    tr.innerHTML = `
      <td>${asset.id}</td>
      <td>${escapeHtml(asset.hostname)}</td>
      <td>${escapeHtml(asset.ip)}</td>
      <td>${renderSeverityBadge(asset.criticality)}</td>
      <td>${escapeHtml(asset.owner)}</td>
      <td>${escapeHtml(asset.os)}</td>
      <td>${formatShortDate(asset.lastSeen)}</td>
      <td>${renderRetiredBadge(asset.retired)}</td>
      <td>
        <button class="btn btn-small row-toggle">${asset.retired ? 'Activate' : 'Retire'}</button>
      </td>
    `;
    tr.addEventListener('click', (e) => {
      if (e.target && e.target.closest('.row-toggle')) return;
      openDrawerForItem('asset', asset.id);
    });
    const toggleBtn = tr.querySelector('.row-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleRetirement('asset', asset.id);
      });
    }
    tbody.appendChild(tr);
  });
}

function renderUsers() {
  const tbody = document.getElementById('users-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  state.data.users.forEach(user => {
    const tr = document.createElement('tr');
    tr.dataset.id = user.id;
    tr.classList.toggle('row-retired', !!user.retired);
    tr.innerHTML = `
      <td>${user.id}</td>
      <td>${escapeHtml(user.name)}</td>
      <td>${escapeHtml(user.email || '')}</td>
      <td>${escapeHtml(user.role || '')}</td>
      <td>${escapeHtml(user.department || '')}</td>
      <td>${renderPrivilegeBadge(user.privileged)}</td>
      <td>${renderRetiredBadge(user.retired)}</td>
      <td><button class="btn btn-small row-toggle">${user.retired ? 'Activate' : 'Retire'}</button></td>
    `;
    tr.addEventListener('click', (e) => {
      if (e.target && e.target.closest('.row-toggle')) return;
      openDrawerForItem('user', user.id);
    });
    const toggleBtn = tr.querySelector('.row-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleRetirement('user', user.id);
      });
    }
    tbody.appendChild(tr);
  });
}

function renderDashboard() {
  updateDashboardKpis();
  renderIncidentsSeverityChart();
  renderAlertsTrendChart();
  renderAssetsCriticalityChart();
}

function updateDashboardKpis() {
  const incidentsTotal = state.data.incidents.length;
  const incidentsOpen = state.data.incidents.filter(i => String(i.status || '').toLowerCase() !== 'closed').length;
  setDashboardText('dashboard-incidents-total', incidentsTotal);
  setDashboardText('dashboard-incidents-open', 'Open: ' + incidentsOpen);

  const alertsTotal = state.data.alerts.length;
  const alertsCritical = state.data.alerts.filter(a => String(a.severity || '').toLowerCase() === 'critical').length;
  setDashboardText('dashboard-alerts-total', alertsTotal);
  setDashboardText('dashboard-alerts-critical', 'Critical: ' + alertsCritical);

  const activeAssets = state.data.assets.filter(a => !a.retired);
  const assetsTotal = activeAssets.length;
  const assetsCritical = activeAssets.filter(a => String(a.criticality || '').toLowerCase() === 'critical').length;
  setDashboardText('dashboard-assets-total', assetsTotal);
  setDashboardText('dashboard-assets-critical', 'Critical: ' + assetsCritical);
}

function renderIncidentsSeverityChart() {
  const labels = ['Critical', 'High', 'Medium', 'Low'];
  const colors = [ChartColors.critical, ChartColors.high, ChartColors.medium, ChartColors.low];
  const values = labels.map(label =>
    state.data.incidents.filter(inc => String(inc.severity || '').toLowerCase() === label.toLowerCase()).length
  );
  drawBarChart('dashboard-incidents-chart', labels, values, colors);
  renderLegend('dashboard-incidents-legend', labels.map((label, idx) => ({
    label: `${label}: ${values[idx]}`,
    color: colors[idx]
  })));
}

function renderAlertsTrendChart() {
  const trend = buildAlertTrendData(7);
  drawLineChart('dashboard-alerts-chart', trend.labels, trend.values, ChartColors.accent);
  const total = trend.values.reduce((sum, val) => sum + val, 0);
  renderLegend('dashboard-alerts-legend', [{
    label: `Total alerts (7d): ${total}`,
    color: ChartColors.accent
  }]);
}

function renderAssetsCriticalityChart() {
  const labels = ['Critical', 'High', 'Medium', 'Low'];
  const colors = [ChartColors.critical, ChartColors.high, ChartColors.medium, ChartColors.low];
  const activeAssets = state.data.assets.filter(asset => !asset.retired);
  const values = labels.map(label =>
    activeAssets.filter(asset => String(asset.criticality || '').toLowerCase() === label.toLowerCase()).length
  );
  drawDonutChart('dashboard-assets-chart', labels, values, colors);
  renderLegend('dashboard-assets-legend', labels.map((label, idx) => ({
    label: `${label}: ${values[idx]}`,
    color: colors[idx]
  })));
}

// --- Add Items ----------------------------------------------------------
function bindAddEvents() {
  const addIncBtn = document.getElementById('add-incident-button');
  if (addIncBtn) addIncBtn.addEventListener('click', handleAddIncident);

  const addAltBtn = document.getElementById('add-alert-button');
  if (addAltBtn) addAltBtn.addEventListener('click', handleAddAlert);

  const addAsBtn = document.getElementById('add-asset-button');
  if (addAsBtn) addAsBtn.addEventListener('click', handleAddAsset);

  const addUserBtn = document.getElementById('add-user-button');
  if (addUserBtn) addUserBtn.addEventListener('click', handleAddUser);
}

function generateNextId(prefix, existingIds) {
  let maxNum = 0;
  existingIds.forEach(id => {
    if (id.startsWith(prefix + '-')) {
      const numPart = parseInt(id.split('-')[1], 10);
      if (!isNaN(numPart) && numPart > maxNum) maxNum = numPart;
    }
  });
  return prefix + '-' + (maxNum + 1);
}

function handleAddIncident() {
  const titleEl = document.getElementById('add-incident-title');
  const sevEl = document.getElementById('add-incident-severity');
  const statEl = document.getElementById('add-incident-status');
  const ownerEl = document.getElementById('add-incident-owner');
  const srcEl = document.getElementById('add-incident-source');
  const fullEl = document.getElementById('add-incident-fulltext');

  const title = titleEl.value.trim();
  if (!title) return;

  const nowIso = new Date().toISOString();
  const ids = state.data.incidents.map(i => i.id);
  const id = generateNextId('INC', ids);

  const incident = {
    id,
    title,
    severity: sevEl.value || 'High',
    status: statEl.value || 'New',
    owner: ownerEl.value.trim() || 'unassigned',
    source: srcEl.value.trim() || 'Manual',
    createdAt: nowIso,
    updatedAt: nowIso,
    tags: [],
    relatedAlerts: [],
    fullText: fullEl.value.trim() || 'No full text provided.',
    notes: []
  };

  state.data.incidents.push(incident);
  titleEl.value = '';
  ownerEl.value = '';
  srcEl.value = '';
  fullEl.value = '';

  renderIncidents();
  renderOverview();
  renderDashboard();
  markLastUpdated();
}

function handleAddAlert() {
  const ruleEl = document.getElementById('add-alert-rule');
  const sevEl = document.getElementById('add-alert-severity');
  const statEl = document.getElementById('add-alert-status');
  const srcEl = document.getElementById('add-alert-source');
  const assetEl = document.getElementById('add-alert-asset');
  const fullEl = document.getElementById('add-alert-fulltext');

  const rule = ruleEl.value.trim();
  if (!rule) return;

  const nowIso = new Date().toISOString();
  const ids = state.data.alerts.map(a => a.id);
  const id = generateNextId('ALRT', ids);

  const alert = {
    id,
    rule,
    severity: sevEl.value || 'High',
    status: statEl.value || 'New',
    source: srcEl.value.trim() || 'Manual',
    firstSeen: nowIso,
    lastSeen: nowIso,
    count: 1,
    assetId: assetEl.value.trim() || '',
    incidentId: '',
    fullText: fullEl.value.trim() || 'No full text provided.',
    notes: []
  };

  state.data.alerts.push(alert);
  ruleEl.value = '';
  srcEl.value = '';
  assetEl.value = '';
  fullEl.value = '';

  renderAlerts();
  renderOverview();
  renderDashboard();
  markLastUpdated();
}

function handleAddAsset() {
  const hostEl = document.getElementById('add-asset-hostname');
  const ipEl = document.getElementById('add-asset-ip');
  const critEl = document.getElementById('add-asset-criticality');
  const ownerEl = document.getElementById('add-asset-owner');
  const osEl = document.getElementById('add-asset-os');
  const fullEl = document.getElementById('add-asset-fulltext');

  const hostname = hostEl.value.trim();
  if (!hostname) return;

  const nowIso = new Date().toISOString();
  const ids = state.data.assets.map(a => a.id);
  const id = generateNextId('ASSET', ids);

  const asset = {
    id,
    hostname,
    ip: ipEl.value.trim() || '',
    owner: ownerEl.value.trim() || '',
    department: '',
    criticality: critEl.value || 'High',
    os: osEl.value.trim() || '',
    lastSeen: nowIso,
    alertCount: 0,
    incidentCount: 0,
    tags: [],
    fullText: fullEl.value.trim() || 'No full text provided.',
    notes: [],
    retired: false
  };

  state.data.assets.push(asset);
  hostEl.value = '';
  ipEl.value = '';
  ownerEl.value = '';
  osEl.value = '';
  fullEl.value = '';

  renderAssets();
  renderOverview();
  renderDashboard();
  markLastUpdated();
}

function handleAddUser() {
  const nameEl = document.getElementById('add-user-name');
  const emailEl = document.getElementById('add-user-email');
  const roleEl = document.getElementById('add-user-role');
  const deptEl = document.getElementById('add-user-dept');
  const privEl = document.getElementById('add-user-privileged');

  if (!nameEl || !emailEl || !roleEl || !deptEl || !privEl) return;
  const name = nameEl.value.trim();
  const email = emailEl.value.trim();
  if (!name || !email) return;

  const ids = state.data.users.map(u => u.id);
  const id = generateNextId('USR', ids);

  const user = {
    id,
    name,
    email,
    role: roleEl.value.trim() || 'Analyst',
    department: deptEl.value.trim() || 'Security',
    privileged: !!privEl.checked,
    retired: false
  };

  state.data.users.push(user);
  nameEl.value = '';
  emailEl.value = '';
  roleEl.value = '';
  deptEl.value = '';
  privEl.checked = false;

  renderUsers();
  markLastUpdated();
}

// --- Delete Items -------------------------------------------------------
function deleteItem(type, id) {
  let arrKey = null;
  if (type === 'incident') arrKey = 'incidents';
  if (type === 'alert') arrKey = 'alerts';
  if (type === 'asset') arrKey = 'assets';
  if (type === 'user') arrKey = 'users';
  if (!arrKey) return;

  const arr = state.data[arrKey];
  const idx = arr.findIndex(x => x.id === id);
  if (idx >= 0) arr.splice(idx, 1);

  const key = type + ':' + id;
  delete state.notes.perItem[key];
  Storage.saveNotes(state.notes);

  if (state.selectedItem && state.selectedItem.type === type && state.selectedItem.id === id) {
    closeDrawer();
  }

  if (type === 'incident') renderIncidents();
  if (type === 'alert') renderAlerts();
  if (type === 'asset') renderAssets();
  if (type === 'user') renderUsers();
  renderOverview();
  renderDashboard();
  markLastUpdated();
}

function toggleRetirement(type, id) {
  let list = null;
  if (type === 'asset') list = state.data.assets;
  else if (type === 'user') list = state.data.users;
  if (!list) return;

  const item = list.find(entry => entry.id === id);
  if (!item) return;
  item.retired = !item.retired;

  if (type === 'asset') {
    renderAssets();
  } else if (type === 'user') {
    renderUsers();
  }
  renderDashboard();
  markLastUpdated();

  if (state.selectedItem && state.selectedItem.type === type && state.selectedItem.id === id) {
    const notes = state.notes.perItem[type + ':' + id] || [];
    renderDrawer(item, type, notes);
  }
}

// --- Tab Notes ----------------------------------------------------------
function setupTabNotes() {
  document.querySelectorAll('.tab-notes-input').forEach(textarea => {
    const tab = textarea.dataset.tab;
    textarea.value = state.notes.perTab[tab] || '';
    textarea.addEventListener('input', () => {
      state.notes.perTab[tab] = textarea.value;
      Storage.saveNotes(state.notes);
    });
  });
}

// --- Drawer -------------------------------------------------------------
function bindDrawerEvents() {
  const closeBtn = document.getElementById('drawer-close');
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
}

function bindDrawerTabEvents() {
  const tabs = document.querySelectorAll('.drawer-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.dtab;
      tabs.forEach(t => t.classList.toggle('active', t === tab));
      document.querySelectorAll('.drawer-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === 'drawer-' + target);
      });
    });
  });
}

function openDrawerForItem(type, id) {
  state.selectedItem = { type, id };
  const item = findItemById(type, id);
  if (!item) return;

  const key = type + ':' + id;
  const itemNotes = state.notes.perItem[key] || [];
  renderDrawer(item, type, itemNotes);

  const drawer = document.getElementById('detail-drawer');
  if (drawer) drawer.classList.add('open');
}

function closeDrawer() {
  const drawer = document.getElementById('detail-drawer');
  if (drawer) drawer.classList.remove('open');
  state.selectedItem = null;
}

function findItemById(type, id) {
  if (type === 'incident') return state.data.incidents.find(i => i.id === id);
  if (type === 'alert') return state.data.alerts.find(a => a.id === id);
  if (type === 'asset') return state.data.assets.find(a => a.id === id);
  if (type === 'user') return state.data.users.find(u => u.id === id);
  return null;
}

function renderDrawer(item, type, notes) {
  const titleEl = document.getElementById('drawer-title');
  const metaEl = document.getElementById('drawer-meta');
  const summaryEl = document.getElementById('drawer-summary');
  const fullTextEl = document.getElementById('drawer-fulltext');

  if (titleEl) {
    let label = '';
    if (type === 'incident') label = 'Incident';
    if (type === 'alert') label = 'Alert';
    if (type === 'asset') label = 'Asset';
     if (type === 'user') label = 'User';
    titleEl.textContent = `${label} ${item.id}`;
  }

  if (metaEl) {
    if (type === 'user') {
      const privilege = renderPrivilegeBadge(item.privileged);
      const roleHtml = item.role ? `<span class="status-pill-small">${escapeHtml(item.role)}</span>` : '';
      const deptHtml = item.department ? `<span class="status-pill-small">${escapeHtml(item.department)}</span>` : '';
      metaEl.innerHTML = `
        ${privilege ? '<span>' + privilege + '</span>' : ''}
        ${roleHtml}
        ${deptHtml}
        ${item.retired ? '<span class="status-pill-small status-pill-retired">Retired</span>' : ''}
      `;
    } else {
      const sev = item.severity || item.criticality;
      const severityHtml = sev ? renderSeverityBadge(sev) : '';
      const statusHtml = item.status ? `<span class="status-pill-small">${escapeHtml(item.status)}</span>` : '';
      metaEl.innerHTML = `
        ${severityHtml ? '<span>' + severityHtml + '</span>' : ''}
        ${statusHtml ? '<span>' + statusHtml + '</span>' : ''}
        ${item.owner ? '<span>Owner: ' + escapeHtml(item.owner) + '</span>' : ''}
        ${item.source ? '<span>Source: ' + escapeHtml(item.source) + '</span>' : ''}
        ${item.retired ? '<span class="status-pill-small status-pill-retired">Retired</span>' : ''}
      `;
    }
  }

  if (summaryEl) {
    summaryEl.innerHTML = renderSummaryPanel(item, type);
  }

  if (fullTextEl) {
    let text = item.fullText || '(no full text available)';
    if (type === 'user') text = buildUserFullText(item);
    fullTextEl.innerHTML = `<pre class="fulltext">${escapeHtml(text)}</pre>`;
  }

  renderDrawerNotesPanel(notes);
}

function renderSummaryPanel(item, type) {
  const rows = [];
  const pushRow = (label, value) => {
    if (value === undefined || value === null || value === '') return;
    rows.push(`
      <div class="summary-row">
        <div class="summary-label">${label}</div>
        <div class="summary-value">${escapeHtml(String(value))}</div>
      </div>
    `);
  };

  if (type === 'incident') {
    pushRow('Title', item.title);
    pushRow('Severity', item.severity);
    pushRow('Status', item.status);
    pushRow('Owner', item.owner);
    pushRow('Source', item.source);
    pushRow('Created', formatFullDate(item.createdAt));
    pushRow('Updated', formatFullDate(item.updatedAt));
    pushRow('Tags', (item.tags || []).join(', '));
    pushRow('Related Alerts', (item.relatedAlerts || []).join(', '));
  } else if (type === 'alert') {
    pushRow('Rule', item.rule);
    pushRow('Severity', item.severity);
    pushRow('Status', item.status);
    pushRow('Source', item.source);
    pushRow('Asset ID', item.assetId);
    pushRow('Incident ID', item.incidentId || '');
    pushRow('First Seen', formatFullDate(item.firstSeen));
    pushRow('Last Seen', formatFullDate(item.lastSeen));
    pushRow('Count', item.count);
  } else if (type === 'asset') {
    pushRow('Hostname', item.hostname);
    pushRow('IP', item.ip);
    pushRow('Criticality', item.criticality);
    pushRow('Owner', item.owner);
    pushRow('Department', item.department);
    pushRow('OS', item.os);
    pushRow('Last Seen', formatFullDate(item.lastSeen));
    pushRow('Alert Count', item.alertCount);
    pushRow('Incident Count', item.incidentCount);
    pushRow('Tags', (item.tags || []).join(', '));
    pushRow('Status', item.retired ? 'Retired' : 'Active');
  } else if (type === 'user') {
    pushRow('Name', item.name);
    pushRow('Email', item.email);
    pushRow('Role', item.role);
    pushRow('Department', item.department);
    pushRow('Privileged', item.privileged ? 'Yes' : 'No');
    pushRow('Status', item.retired ? 'Retired' : 'Active');
    pushRow('Last Logon', formatFullDate(item.lastLogon));
    pushRow('Last Device', item.lastDevice);
    pushRow('Last Location', item.lastLocation);
    pushRow('Phone', item.phone);
  }

  return `<div class="summary-grid">${rows.join('')}</div>`;
}

function buildUserFullText(user) {
  const lines = [
    `Name: ${user.name || ''}`,
    `Email: ${user.email || ''}`,
    `Role: ${user.role || ''}`,
    `Department: ${user.department || ''}`,
    `Privileged: ${user.privileged ? 'Yes' : 'No'}`,
    `Status: ${user.retired ? 'Retired' : 'Active'}`,
    `Last Logon: ${formatFullDate(user.lastLogon) || ''}`,
    `Last Device: ${user.lastDevice || ''}`,
    `Last Location: ${user.lastLocation || ''}`,
    `Phone: ${user.phone || ''}`
  ].filter(Boolean);
  return lines.join('\n');
}

function renderDrawerNotesPanel(notes) {
  const notesEl = document.getElementById('drawer-notes');
  if (!notesEl) return;

  const itemsHtml = notes.map(note => `
    <div class="note-item">
      <div class="note-meta">${escapeHtml(note.author || 'Analyst')} · ${formatFullDate(note.createdAt)}</div>
      <div class="note-text">${escapeHtml(note.text)}</div>
    </div>
  `).join('');

  notesEl.innerHTML = `
    <div class="notes-list">
      ${itemsHtml || '<div style="font-size:0.8rem; opacity:0.7;">No notes yet.</div>'}
    </div>
    <div class="note-new">
      <textarea id="note-input" placeholder="Add a note for this item..."></textarea>
      <div style="margin-top:0.4rem; text-align:right;">
        <button id="add-note-button" class="btn btn-primary">Add Note</button>
      </div>
    </div>
  `;

  const btn = document.getElementById('add-note-button');
  const textarea = document.getElementById('note-input');
  if (btn && textarea) {
    btn.addEventListener('click', () => {
      const text = textarea.value.trim();
      if (!text || !state.selectedItem) return;
      addNoteForSelectedItem(text);
      textarea.value = '';
    });
  }
}

function addNoteForSelectedItem(text) {
  const sel = state.selectedItem;
  if (!sel) return;
  const key = sel.type + ':' + sel.id;
  const existing = state.notes.perItem[key] || [];

  const note = {
    id: 'note-' + Date.now(),
    author: state.preferences.analystName || 'Analyst',
    createdAt: new Date().toISOString(),
    text
  };

  const updated = [note, ...existing];
  state.notes.perItem[key] = updated;
  Storage.saveNotes(state.notes);
  renderDrawerNotesPanel(updated);
}

// --- Settings -----------------------------------------------------------
function renderSettings() {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.checked = state.preferences.theme === 'dark';
  const analystInput = document.getElementById('analyst-name-input');
  if (analystInput) analystInput.value = state.preferences.analystName || '';
}

function bindSettingsEvents() {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('change', () => {
      applyTheme(themeToggle.checked ? 'dark' : 'light');
    });
  }

  const analystInput = document.getElementById('analyst-name-input');
  if (analystInput) {
    analystInput.addEventListener('input', () => {
      state.preferences.analystName = analystInput.value || 'Analyst';
      Storage.savePreferences(state.preferences);
    });
  }
}

function bindUploadEvents() {
  const fileInput = document.getElementById('data-upload-input');
  const uploadBtn = document.getElementById('data-upload-button');
  const statusEl = document.getElementById('data-upload-status');
  const categorySelect = document.getElementById('data-upload-category');
  if (!fileInput || !uploadBtn || !statusEl) return;

  const setStatus = (message, tone) => {
    statusEl.textContent = message;
    statusEl.classList.remove('upload-status-success', 'upload-status-error');
    if (tone === 'success') statusEl.classList.add('upload-status-success');
    else if (tone === 'error') statusEl.classList.add('upload-status-error');
  };

  fileInput.addEventListener('change', () => {
    if (!fileInput.files || fileInput.files.length === 0) {
      setStatus('No file selected');
      return;
    }
    const file = fileInput.files[0];
    setStatus(`${file.name} ready to upload`);
  });

  uploadBtn.addEventListener('click', () => {
    if (!fileInput.files || fileInput.files.length === 0) {
      setStatus('Choose a file before uploading.', 'error');
      return;
    }
    if (!categorySelect || !categorySelect.value) {
      setStatus('Select a category for the upload.', 'error');
      return;
    }

    const file = fileInput.files[0];
    setStatus(`Uploading ${file.name}...`);

    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(reader.result);
        const records = extractRecordsFromUpload(parsed, categorySelect.value);
        if (!Array.isArray(records)) {
          setStatus('Uploaded file must be an array or contain an array for the selected category.', 'error');
          return;
        }
        applyUploadedData(categorySelect.value, records);
        setStatus(`${file.name} loaded for ${categorySelect.options[categorySelect.selectedIndex].text} (${records.length} records).`, 'success');
      } catch (err) {
        console.error('Upload parse error', err);
        setStatus('Failed to parse file: ' + err.message, 'error');
      }
    };
    reader.onerror = () => {
      setStatus('Failed to read the file.', 'error');
    };
    reader.readAsText(file);
  });
}

function bindDownloadEvents() {
  const downloadBtn = document.getElementById('download-sample-button');
  const categorySelect = document.getElementById('data-upload-category');
  if (!downloadBtn) return;

  downloadBtn.addEventListener('click', () => {
    const category = categorySelect && categorySelect.value ? categorySelect.value : 'incidents';
    const blob = new Blob([getSampleDownloadContent(category)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${SAMPLE_DOWNLOAD_FILENAME}-${category}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}

// --- Utilities ----------------------------------------------------------
function renderSeverityBadge(sev) {
  if (!sev) return '';
  const s = String(sev).toLowerCase();
  let cls = 'sev-low';
  if (s === 'critical') cls = 'sev-critical';
  else if (s === 'high') cls = 'sev-high';
  else if (s === 'medium') cls = 'sev-medium';
  return `<span class="badge ${cls}">${escapeHtml(sev)}</span>`;
}

function renderPrivilegeBadge(isPrivileged) {
  const cls = isPrivileged ? 'badge-privileged' : 'badge-standard';
  return `<span class="badge ${cls}">${isPrivileged ? 'Privileged' : 'Standard'}</span>`;
}

function renderRetiredBadge(isRetired) {
  return `<span class="badge badge-retired">${isRetired ? 'Retired' : 'Active'}</span>`;
}

function updateAlertsIndicator(count) {
  const indicator = document.getElementById('alerts-indicator');
  if (!indicator) return;
  if (!count) {
    indicator.textContent = 'Alerts: none new';
    indicator.classList.remove('has-events');
  } else {
    indicator.textContent = `Alerts: ${count} new`;
    indicator.classList.add('has-events');
  }
}

function extractRecordsFromUpload(payload, category) {
  if (!payload) return null;
  if (Array.isArray(payload)) return payload;
  if (typeof payload === 'object') {
    if (Array.isArray(payload[category])) return payload[category];
    const arrKey = Object.keys(payload).find(key => Array.isArray(payload[key]));
    if (arrKey) return payload[arrKey];
  }
  return null;
}

function applyUploadedData(category, records) {
  if (!Array.isArray(records)) return;
  const sanitized = records.map(rec => ({ ...rec }));
  if (category === 'incidents') {
    state.data.incidents = sanitized;
    renderIncidents();
    renderOverview();
  } else if (category === 'alerts') {
    state.data.alerts = sanitized;
    renderAlerts();
    renderOverview();
  } else if (category === 'assets') {
    state.data.assets = normalizeAssets(sanitized);
    renderAssets();
  } else if (category === 'users') {
    state.data.users = normalizeUsers(sanitized);
    renderUsers();
  }
  renderDashboard();
  markLastUpdated();
}

function normalizeAssets(assets = []) {
  return assets.map(asset => ({ ...asset, retired: !!asset.retired }));
}

function normalizeUsers(users = []) {
  return users.map(user => ({ ...user, retired: !!user.retired }));
}

function formatShortDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatFullDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleString();
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// --- Dashboard Helpers --------------------------------------------------
function setDashboardText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function renderLegend(containerId, items) {
  const container = document.getElementById(containerId);
  if (!container) return;
  if (!items || !items.length) {
    container.innerHTML = '<span style="opacity:0.6;">No data</span>';
    return;
  }
  container.innerHTML = items.map(item => `
    <span class="dashboard-legend-item">
      <span class="dashboard-legend-swatch" style="background:${item.color};"></span>
      ${escapeHtml(item.label)}
    </span>
  `).join('');
}

function buildAlertTrendData(days = 7) {
  const now = new Date();
  const keys = [];
  const labels = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(now.getDate() - i);
    keys.push(formatDateKey(d));
    labels.push(d.toLocaleDateString(undefined, { weekday: 'short' }));
  }
  const counts = Object.fromEntries(keys.map(key => [key, 0]));
  state.data.alerts.forEach(alert => {
    const dateStr = alert.lastSeen || alert.firstSeen;
    if (!dateStr) return;
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) return;
    const key = formatDateKey(parsed);
    if (counts[key] !== undefined) counts[key] += 1;
  });
  const values = keys.map(key => counts[key] || 0);
  return { labels, values };
}

function formatDateKey(date) {
  if (!(date instanceof Date) || isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}

function prepareCanvasById(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  return prepareCanvas(canvas);
}

function prepareCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const width = rect.width || canvas.parentElement?.clientWidth || 320;
  const height = rect.height || canvas.parentElement?.clientHeight || 200;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  return { ctx, width, height };
}

function drawBarChart(canvasId, labels, values, colors) {
  const ctxInfo = prepareCanvasById(canvasId);
  if (!ctxInfo) return;
  const { ctx, width, height } = ctxInfo;
  const padding = 24;
  const chartHeight = height - padding * 2;
  const chartWidth = width - padding * 2;
  const slots = labels.length || 1;
  const slotWidth = chartWidth / slots;
  const barWidth = Math.min(slotWidth * 0.6, 60);
  const maxValue = Math.max(...values, 1);
  const textColor = getCanvasTextColor();

  ctx.strokeStyle = 'rgba(148,163,184,0.4)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  labels.forEach((label, idx) => {
    const value = values[idx] || 0;
    const barHeight = (value / maxValue) * chartHeight;
    const x = padding + idx * slotWidth + (slotWidth - barWidth) / 2;
    const y = height - padding - barHeight;
    ctx.fillStyle = colors[idx % colors.length];
    ctx.fillRect(x, y, barWidth, barHeight);

    ctx.fillStyle = textColor;
    ctx.font = '12px "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(String(value), x + barWidth / 2, y - 6);
    ctx.textBaseline = 'top';
    ctx.fillText(label, x + barWidth / 2, height - padding + 6);
  });
}

function drawLineChart(canvasId, labels, values, color) {
  const ctxInfo = prepareCanvasById(canvasId);
  if (!ctxInfo) return;
  const { ctx, width, height } = ctxInfo;
  const padding = 28;
  const chartHeight = height - padding * 2;
  const chartWidth = width - padding * 2;
  const steps = Math.max(labels.length - 1, 1);
  const stepX = chartWidth / steps;
  const maxValue = Math.max(...values, 1);
  const textColor = getCanvasTextColor();

  ctx.strokeStyle = 'rgba(148,163,184,0.25)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  values.forEach((value, idx) => {
    const x = padding + stepX * idx;
    const y = height - padding - (value / maxValue) * chartHeight;
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.fillStyle = color;
  values.forEach((value, idx) => {
    const x = padding + stepX * idx;
    const y = height - padding - (value / maxValue) * chartHeight;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.fillStyle = textColor;
  ctx.font = '12px "Segoe UI", sans-serif';
  ctx.textAlign = 'center';
  labels.forEach((label, idx) => {
    const x = padding + stepX * idx;
    ctx.fillText(label, x, height - padding + 12);
  });
}

function drawDonutChart(canvasId, labels, values, colors) {
  const ctxInfo = prepareCanvasById(canvasId);
  if (!ctxInfo) return;
  const { ctx, width, height } = ctxInfo;
  const total = values.reduce((sum, v) => sum + v, 0);
  const textColor = getCanvasTextColor();
  if (total <= 0) {
    ctx.fillStyle = textColor;
    ctx.textAlign = 'center';
    ctx.font = '14px "Segoe UI", sans-serif';
    ctx.fillText('No data', width / 2, height / 2);
    return;
  }
  const radius = Math.min(width, height) / 2 - 10;
  const innerRadius = radius * 0.55;
  const centerX = width / 2;
  const centerY = height / 2;
  let start = -Math.PI / 2;

  values.forEach((value, idx) => {
    const angle = (value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.fillStyle = colors[idx % colors.length];
    ctx.arc(centerX, centerY, radius, start, start + angle);
    ctx.lineTo(centerX, centerY);
    ctx.fill();
    start += angle;
  });

  ctx.globalCompositeOperation = 'destination-out';
  ctx.beginPath();
  ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalCompositeOperation = 'source-over';

  ctx.fillStyle = textColor;
  ctx.textAlign = 'center';
  ctx.font = '12px "Segoe UI", sans-serif';
  ctx.fillText('Total Assets', centerX, centerY - 4);
  ctx.font = '16px "Segoe UI", sans-serif';
  ctx.fillText(String(total), centerX, centerY + 16);
}

function getCanvasTextColor() {
  const color = getComputedStyle(document.body).color;
  return color || '#e2e8f0';
}

// --- Refresh & Header Helpers -------------------------------------------
function bindRefreshEvents() {
  const btn = document.getElementById('refresh-button');
  if (!btn) return;
  btn.addEventListener('click', () => {
    refreshData();
  });

  const alertsChip = document.getElementById('alerts-indicator');
  if (alertsChip) {
    alertsChip.addEventListener('click', () => {
      setActiveTab('alerts');
      const alertsPanel = document.getElementById('tab-alerts');
      if (alertsPanel) alertsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
}

function setRefreshButtonState(isRefreshing) {
  const btn = document.getElementById('refresh-button');
  if (!btn) return;
  btn.disabled = isRefreshing;
  btn.textContent = isRefreshing ? 'Refreshing...' : 'Refresh';
}

function startAutoRefresh() {
  if (refreshTimerId) clearInterval(refreshTimerId);
  refreshTimerId = setInterval(() => {
    refreshData();
  }, REFRESH_INTERVAL_MS);
}

async function refreshData() {
  if (refreshInProgress) return;
  refreshInProgress = true;
  setRefreshButtonState(true);
  try {
    const loaded = await loadFlatData();
    applyLoadedData(loaded);
    renderOverview();
    renderIncidents();
    renderAlerts();
    renderAssets();
    renderUsers();
    renderDashboard();
    markLastUpdated();
    startAutoRefresh();
  } catch (err) {
    console.error('Refresh failed', err);
  } finally {
    refreshInProgress = false;
    setRefreshButtonState(false);
  }
}

function markLastUpdated() {
  state.lastUpdated = new Date();
  updateLastUpdatedLabel();
}

function updateLastUpdatedLabel() {
  const label = document.getElementById('last-updated-label');
  if (!label) return;
  if (!state.lastUpdated) {
    label.textContent = 'Last updated: --';
  } else {
    label.textContent = 'Last updated: ' + state.lastUpdated.toLocaleTimeString();
  }
}

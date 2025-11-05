// SpendSense Dashboard JavaScript

const API_BASE = '/api';

// State
let currentPage = 0;
let currentFilter = '';
const PAGE_SIZE = 10;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initGenerateForm();
    initProfilesTab();
    loadPersonas();
});

// Tab Management
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // Load data for specific tabs
            if (tabName === 'profiles') {
                loadProfiles();
            } else if (tabName === 'stats') {
                loadStats();
            }
        });
    });
}

// Generate Profiles
function initGenerateForm() {
    const form = document.getElementById('generate-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const numUsers = parseInt(document.getElementById('num-users').value);
        const seed = parseInt(document.getElementById('seed').value);
        const resultDiv = document.getElementById('generate-result');

        // Show loading
        resultDiv.className = 'result';
        resultDiv.innerHTML = '<div class="spinner"></div> Generating profiles...';
        resultDiv.classList.remove('hidden');

        try {
            const response = await fetch(`${API_BASE}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ num_users: numUsers, seed: seed })
            });

            const data = await response.json();

            if (response.ok) {
                resultDiv.className = 'result success';
                resultDiv.innerHTML = `
                    <h3>✓ Success!</h3>
                    <p>${data.message}</p>
                    <ul>
                        <li><strong>Total Profiles:</strong> ${data.num_profiles}</li>
                        <li><strong>Validation:</strong> ${data.validation.valid ? 'Passed ✓' : 'Failed ✗'}</li>
                    </ul>
                    ${!data.validation.valid ? `<p><strong>Errors:</strong> ${data.validation.errors.join(', ')}</p>` : ''}
                `;
            } else {
                throw new Error(data.detail || 'Generation failed');
            }
        } catch (error) {
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `
                <h3>✗ Error</h3>
                <p>${error.message}</p>
            `;
        }
    });
}

// Profiles Tab
function initProfilesTab() {
    const filterSelect = document.getElementById('persona-filter');
    const refreshButton = document.getElementById('refresh-profiles');

    filterSelect.addEventListener('change', (e) => {
        currentFilter = e.target.value;
        currentPage = 0;
        loadProfiles();
    });

    refreshButton.addEventListener('click', () => {
        loadProfiles();
    });
}

async function loadProfiles() {
    const listDiv = document.getElementById('profiles-list');
    listDiv.innerHTML = '<div class="spinner"></div> Loading profiles...';

    try {
        const params = new URLSearchParams({
            limit: PAGE_SIZE,
            offset: currentPage * PAGE_SIZE
        });

        if (currentFilter) {
            params.append('persona', currentFilter);
        }

        const response = await fetch(`${API_BASE}/profiles?${params}`);
        const data = await response.json();

        if (response.ok) {
            if (data.profiles.length === 0) {
                listDiv.innerHTML = '<p class="text-muted">No profiles found. Generate some profiles first!</p>';
                return;
            }

            listDiv.innerHTML = data.profiles.map(profile => renderProfile(profile)).join('');
            renderPagination(data.total);
        } else {
            listDiv.innerHTML = `<p class="text-muted">${data.detail}</p>`;
        }
    } catch (error) {
        listDiv.innerHTML = `<p class="text-muted">Error loading profiles: ${error.message}</p>`;
    }
}

function renderProfile(profile) {
    return `
        <div class="profile-card">
            <div class="profile-header">
                <div>
                    <div class="profile-id">${profile.user_id}</div>
                    <div class="profile-name">${profile.name}</div>
                </div>
                <span class="persona-badge">${formatPersona(profile.persona)}</span>
            </div>
            <div class="profile-details">
                <div class="profile-detail">
                    <span class="profile-detail-label">Annual Income</span>
                    <span class="profile-detail-value">$${profile.annual_income.toLocaleString()}</span>
                </div>
                <div class="profile-detail">
                    <span class="profile-detail-label">Credit Utilization Target</span>
                    <span class="profile-detail-value">${(profile.characteristics.target_credit_utilization * 100).toFixed(0)}%</span>
                </div>
                <div class="profile-detail">
                    <span class="profile-detail-label">Monthly Savings Target</span>
                    <span class="profile-detail-value">$${profile.characteristics.target_savings_monthly.toFixed(0)}</span>
                </div>
                <div class="profile-detail">
                    <span class="profile-detail-label">Income Stability</span>
                    <span class="profile-detail-value">${profile.characteristics.income_stability}</span>
                </div>
                <div class="profile-detail">
                    <span class="profile-detail-label">Subscriptions</span>
                    <span class="profile-detail-value">${profile.characteristics.subscription_count_target}</span>
                </div>
                <div class="profile-detail">
                    <span class="profile-detail-label">Accounts</span>
                    <span class="profile-detail-value">${profile.accounts.length}</span>
                </div>
            </div>
        </div>
    `;
}

function renderPagination(total) {
    const paginationDiv = document.getElementById('profile-pagination');
    const totalPages = Math.ceil(total / PAGE_SIZE);

    if (totalPages <= 1) {
        paginationDiv.classList.add('hidden');
        return;
    }

    paginationDiv.classList.remove('hidden');
    paginationDiv.innerHTML = `
        <button ${currentPage === 0 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">Previous</button>
        <span>Page ${currentPage + 1} of ${totalPages}</span>
        <button ${currentPage >= totalPages - 1 ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">Next</button>
    `;
}

function changePage(page) {
    currentPage = page;
    loadProfiles();
}

// Statistics
async function loadStats() {
    const statsDiv = document.getElementById('stats-content');
    statsDiv.innerHTML = '<div class="spinner"></div> Loading statistics...';

    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        if (response.ok) {
            statsDiv.innerHTML = renderStats(data);
        } else {
            statsDiv.innerHTML = `<p class="text-muted">${data.detail}</p>`;
        }
    } catch (error) {
        statsDiv.innerHTML = `<p class="text-muted">Error loading stats: ${error.message}</p>`;
    }
}

function renderStats(stats) {
    const personaPercentages = stats.validation.persona_percentages || {};

    return `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Profiles</div>
                <div class="stat-value">${stats.total_profiles}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Min Income</div>
                <div class="stat-value">$${(stats.income_range[0] / 1000).toFixed(0)}K</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Max Income</div>
                <div class="stat-value">$${(stats.income_range[1] / 1000).toFixed(0)}K</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Validation</div>
                <div class="stat-value">${stats.validation.valid ? '✓' : '✗'}</div>
            </div>
        </div>

        <h3>Persona Distribution</h3>
        <div class="chart">
            ${Object.entries(stats.persona_distribution)
                .map(([persona, count]) => {
                    const percentage = personaPercentages[persona] || 0;
                    return `
                        <div class="chart-bar">
                            <div class="chart-label">${formatPersona(persona)}</div>
                            <div class="chart-bar-container">
                                <div class="chart-bar-fill" style="width: ${percentage}%">
                                    ${count} (${percentage.toFixed(1)}%)
                                </div>
                            </div>
                        </div>
                    `;
                })
                .join('')}
        </div>

        ${!stats.validation.valid ? `
            <div class="result error" style="margin-top: 2rem;">
                <h3>Validation Errors</h3>
                <ul>
                    ${stats.validation.errors.map(err => `<li>${err}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
    `;
}

// Personas
async function loadPersonas() {
    const personasDiv = document.getElementById('personas-content');

    try {
        const response = await fetch(`${API_BASE}/personas`);
        const personas = await response.json();

        personasDiv.innerHTML = Object.entries(personas)
            .map(([key, persona]) => `
                <div class="persona-card">
                    <h3>${persona.name}</h3>
                    <p>${persona.description}</p>
                </div>
            `)
            .join('');
    } catch (error) {
        personasDiv.innerHTML = `<p class="text-muted">Error loading personas: ${error.message}</p>`;
    }
}

// Utilities
function formatPersona(persona) {
    return persona.replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// ===== Behavioral Signals Tab =====
const signalsForm = document.getElementById('signals-form');
const signalsResult = document.getElementById('signals-result');

if (signalsForm) {
    signalsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userId = document.getElementById('signals-user-id').value;
        const windowDays = document.getElementById('signals-window').value;

        signalsResult.innerHTML = '<p class="loading">Loading behavioral signals...</p>';
        signalsResult.classList.remove('hidden');

        try {
            const response = await fetch(`/api/signals/${userId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch signals');
            }

            displayBehavioralSignals(data, windowDays);
        } catch (error) {
            signalsResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    });
}

function displayBehavioralSignals(data, windowDays) {
    const window = windowDays === '30' ? '30d' : '180d';

    const subscriptions = data.subscriptions[window];
    const savings = data.savings[window];
    const credit = data.credit[window];
    const income = data.income[window];

    const html = `
        <div class="signals-grid">
            <!-- Subscription Signals -->
            <div class="signal-card">
                <h3>📺 Subscriptions</h3>
                <div class="signal-metric">
                    <span class="label">Subscription Count:</span>
                    <span class="value">${subscriptions.subscription_count}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Monthly Recurring:</span>
                    <span class="value">$${subscriptions.monthly_recurring_spend.toFixed(2)}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Share of Spend:</span>
                    <span class="value">${(subscriptions.subscription_share * 100).toFixed(1)}%</span>
                </div>
            </div>

            <!-- Savings Signals -->
            <div class="signal-card">
                <h3>💰 Savings</h3>
                <div class="signal-metric">
                    <span class="label">Has Savings:</span>
                    <span class="value ${savings.has_savings_accounts ? 'success' : 'muted'}">
                        ${savings.has_savings_accounts ? 'Yes' : 'No'}
                    </span>
                </div>
                <div class="signal-metric">
                    <span class="label">Total Balance:</span>
                    <span class="value">$${savings.total_savings_balance.toFixed(2)}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Growth Rate:</span>
                    <span class="value ${savings.savings_growth_rate > 0 ? 'success' : ''}">
                        ${(savings.savings_growth_rate * 100).toFixed(1)}%
                    </span>
                </div>
                <div class="signal-metric">
                    <span class="label">Emergency Fund:</span>
                    <span class="value">${savings.emergency_fund_months.toFixed(1)} months</span>
                </div>
            </div>

            <!-- Credit Signals -->
            <div class="signal-card">
                <h3>💳 Credit</h3>
                <div class="signal-metric">
                    <span class="label">Credit Cards:</span>
                    <span class="value">${credit.num_credit_cards}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Aggregate Utilization:</span>
                    <span class="value ${getUtilizationClass(credit.aggregate_utilization)}">
                        ${(credit.aggregate_utilization * 100).toFixed(1)}%
                    </span>
                </div>
                <div class="signal-metric">
                    <span class="label">High Utilization:</span>
                    <span class="value ${credit.high_utilization_count > 0 ? 'warning' : ''}">
                        ${credit.high_utilization_count} cards
                    </span>
                </div>
                <div class="signal-metric">
                    <span class="label">Overdue:</span>
                    <span class="value ${credit.overdue_count > 0 ? 'error' : 'success'}">
                        ${credit.overdue_count} accounts
                    </span>
                </div>
            </div>

            <!-- Income Signals -->
            <div class="signal-card">
                <h3>💵 Income</h3>
                <div class="signal-metric">
                    <span class="label">Payment Frequency:</span>
                    <span class="value">${income.payment_frequency}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Income Transactions:</span>
                    <span class="value">${income.num_income_transactions}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Total Income:</span>
                    <span class="value">$${income.total_income.toFixed(2)}</span>
                </div>
                <div class="signal-metric">
                    <span class="label">Regular Income:</span>
                    <span class="value ${income.has_regular_income ? 'success' : 'muted'}">
                        ${income.has_regular_income ? 'Yes' : 'No'}
                    </span>
                </div>
            </div>
        </div>

        <!-- Metadata -->
        <div class="signals-metadata">
            <h4>Analysis Metadata</h4>
            <p><strong>Generated:</strong> ${data.generated_at}</p>
            <p><strong>Window:</strong> ${windowDays} days</p>
            <p><strong>Data Completeness:</strong> ${JSON.stringify(data.metadata.data_completeness, null, 2)}</p>
        </div>
    `;

    signalsResult.innerHTML = html;
}

function getUtilizationClass(utilization) {
    if (utilization >= 0.80) return 'error';
    if (utilization >= 0.50) return 'warning';
    if (utilization >= 0.30) return 'caution';
    return 'success';
}

// ===== Persona Assignment Tab =====
const assignmentForm = document.getElementById('assignment-form');
const assignmentResult = document.getElementById('assignment-result');

if (assignmentForm) {
    assignmentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userId = document.getElementById('assignment-user-id').value;
        const timeWindow = document.getElementById('assignment-window').value;

        assignmentResult.innerHTML = '<p class="loading">Loading persona assignment...</p>';
        assignmentResult.classList.remove('hidden');

        try {
            let url = `/api/profile/${userId}`;
            if (timeWindow) {
                url += `?time_window=${timeWindow}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch assignment');
            }

            displayPersonaAssignment(data, timeWindow);
        } catch (error) {
            assignmentResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    });
}

function displayPersonaAssignment(data, requestedWindow) {
    const assignments = data.assignments;
    const windows = requestedWindow ? [requestedWindow] : Object.keys(assignments).filter(w => assignments[w]);

    if (windows.length === 0) {
        assignmentResult.innerHTML = `
            <div class="info">
                <h3>No Assignments Found</h3>
                <p>User <strong>${data.user_id}</strong> has no persona assignments yet.</p>
                <p class="text-muted">Run persona assignment for this user first.</p>
            </div>
        `;
        return;
    }

    const html = windows.map(window => {
        const assignment = assignments[window];
        if (!assignment) return '';

        const personaName = formatPersonaName(assignment.assigned_persona_id);
        const priorityClass = getPriorityClass(assignment.priority);
        const isUnclassified = assignment.assigned_persona_id === 'unclassified';

        return `
            <div class="assignment-window-card">
                <div class="assignment-header">
                    <h3>${window === '30d' ? '30-Day' : '180-Day'} Window</h3>
                    <span class="badge ${priorityClass}">
                        ${isUnclassified ? 'Unclassified' : `Priority ${assignment.priority}`}
                    </span>
                </div>

                <div class="assignment-details">
                    <div class="persona-assignment ${priorityClass}">
                        <div class="persona-name">
                            ${getPersonaIcon(assignment.assigned_persona_id)} ${personaName}
                        </div>
                        <div class="assignment-meta">
                            <small>Assigned: ${formatDateTime(assignment.assigned_at)}</small>
                        </div>
                    </div>

                    ${!isUnclassified ? `
                        <div class="qualifying-personas">
                            <h4>All Qualifying Personas</h4>
                            <div class="persona-chips">
                                ${assignment.all_qualifying_personas.map(pid => `
                                    <span class="persona-chip ${pid === assignment.assigned_persona_id ? 'primary' : ''}">
                                        ${formatPersonaName(pid)}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <div class="prioritization-reason">
                        <h4>Selection Reasoning</h4>
                        <p>${assignment.prioritization_reason}</p>
                    </div>

                    <div class="match-evidence">
                        <h4>Match Evidence</h4>
                        <details>
                            <summary>View all ${Object.keys(assignment.match_evidence).length} persona evaluations</summary>
                            <div class="evidence-grid">
                                ${Object.entries(assignment.match_evidence).map(([personaId, evidence]) => `
                                    <div class="evidence-card ${evidence.matched ? 'matched' : 'not-matched'}">
                                        <div class="evidence-header">
                                            <span class="persona-label">${formatPersonaName(personaId)}</span>
                                            <span class="match-status ${evidence.matched ? 'success' : 'muted'}">
                                                ${evidence.matched ? '✓ Matched' : '✗ No Match'}
                                            </span>
                                        </div>
                                        ${evidence.matched && evidence.matched_conditions && evidence.matched_conditions.length > 0 ? `
                                            <div class="matched-conditions">
                                                <strong>Conditions:</strong>
                                                <ul>
                                                    ${evidence.matched_conditions.map(cond => `<li>${cond}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}
                                        ${Object.keys(evidence.evidence).length > 0 ? `
                                            <div class="evidence-values">
                                                <strong>Signals:</strong>
                                                <pre>${JSON.stringify(evidence.evidence, null, 2)}</pre>
                                            </div>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </details>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    assignmentResult.innerHTML = `
        <div class="assignment-dashboard-content">
            <h3>Persona Assignment for ${data.user_id}</h3>
            ${html}
        </div>
    `;
}

function formatPersonaName(personaId) {
    if (personaId === 'unclassified') return 'Unclassified';
    return personaId.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function getPersonaIcon(personaId) {
    const icons = {
        'high_utilization': '💳',
        'irregular_income': '📊',
        'low_savings': '💰',
        'subscription_heavy': '📺',
        'cash_flow_optimizer': '🎯',
        'young_professional': '👤',
        'unclassified': '❓'
    };
    return icons[personaId] || '📌';
}

function getPriorityClass(priority) {
    if (priority === null) return 'unclassified';
    if (priority === 1) return 'priority-1';
    if (priority === 2) return 'priority-2';
    if (priority === 3) return 'priority-3';
    if (priority <= 5) return 'priority-medium';
    return 'priority-low';
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

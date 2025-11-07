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

// ===== Recommendations Tab (Epic 4) =====

document.getElementById('recommendations-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userId = document.getElementById('rec-user-id').value;
    const timeWindow = document.getElementById('rec-window').value;
    const forceGenerate = document.getElementById('rec-force-generate').checked;

    const loadingDiv = document.getElementById('recommendations-loading');
    const resultDiv = document.getElementById('recommendations-result');
    const errorDiv = document.getElementById('recommendations-error');

    // Show loading
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    try {
        const response = await fetch(
            `/api/recommendations/${userId}?time_window=${timeWindow}&generate=${forceGenerate}`
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch recommendations');
        }

        const data = await response.json();
        displayRecommendations(data);

    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.classList.remove('hidden');
    } finally {
        loadingDiv.classList.add('hidden');
    }
});

function displayRecommendations(data) {
    const resultDiv = document.getElementById('recommendations-result');

    // Summary
    document.getElementById('rec-persona').textContent = formatPersonaName(data.persona_id);
    document.getElementById('rec-window-badge').textContent = data.time_window;
    document.getElementById('rec-time').textContent = `${data.metadata.generation_time_ms.toFixed(1)}ms`;

    // Disclaimer
    document.getElementById('rec-disclaimer').textContent = data.disclaimer;

    // Signals
    const signalsDiv = document.getElementById('rec-signals');
    if (data.metadata.signals_detected && data.metadata.signals_detected.length > 0) {
        signalsDiv.innerHTML = data.metadata.signals_detected
            .map(signal => `<span class="badge badge-info">${formatSignalName(signal)}</span>`)
            .join(' ');
    } else {
        signalsDiv.innerHTML = '<span class="text-muted">No specific signals detected</span>';
    }

    // Recommendations
    const itemsDiv = document.getElementById('rec-items');
    itemsDiv.innerHTML = data.recommendations.map((rec, index) =>
        createRecommendationCard(rec, index + 1)
    ).join('');

    // Metadata
    document.getElementById('rec-metadata').textContent = JSON.stringify({
        total_recommendations: data.metadata.total_recommendations,
        education_count: data.metadata.education_count,
        partner_offer_count: data.metadata.partner_offer_count,
        generation_time_ms: data.metadata.generation_time_ms,
        signals_detected: data.metadata.signals_detected,
        generated_at: data.generated_at
    }, null, 2);

    resultDiv.classList.remove('hidden');
}

function createRecommendationCard(rec, index) {
    const isEducation = rec.item_type === 'education';
    const typeIcon = isEducation ? '📚' : '🎁';
    const typeLabel = isEducation ? 'Educational Content' : 'Partner Offer';
    const typeBadge = isEducation ? 'badge-primary' : 'badge-success';

    return `
        <div class="recommendation-card">
            <div class="rec-header">
                <div class="rec-number">${index}</div>
                <div class="rec-title-section">
                    <div class="rec-type">
                        ${typeIcon} <span class="badge ${typeBadge}">${typeLabel}</span>
                    </div>
                    <h4 class="rec-title">${rec.content.title}</h4>
                    ${rec.content.provider ? `<p class="rec-provider">by ${rec.content.provider}</p>` : ''}
                </div>
            </div>

            <div class="rec-body">
                <p class="rec-description">${rec.content.description}</p>

                <div class="rec-rationale-box">
                    <strong>💬 Why this recommendation:</strong>
                    <p>${rec.rationale}</p>
                </div>

                <div class="rec-persona-match">
                    <strong>🎯 Persona Match:</strong>
                    <p>${rec.persona_match_reason}</p>
                </div>

                ${rec.signal_citations && rec.signal_citations.length > 0 ? `
                    <div class="rec-citations">
                        <strong>📊 Data Citations:</strong>
                        <ul>
                            ${rec.signal_citations.map(citation => `<li>${citation}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                <div class="rec-details">
                    ${isEducation ? `
                        <span class="badge">${rec.content.type}</span>
                        <span class="badge ${getPriorityClass(rec.content.priority)}">Priority ${rec.content.priority}</span>
                        <span class="badge">${rec.content.difficulty}</span>
                        <span class="badge">${rec.content.time_commitment}</span>
                        <span class="badge">${rec.content.estimated_impact} impact</span>
                    ` : `
                        <span class="badge">${rec.content.type}</span>
                        <span class="badge ${getPriorityClass(rec.content.priority)}">Priority ${rec.content.priority}</span>
                    `}
                </div>

                ${rec.content.key_benefits && rec.content.key_benefits.length > 0 ? `
                    <div class="rec-benefits">
                        <strong>✨ Key Benefits:</strong>
                        <ul>
                            ${rec.content.key_benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${rec.content.content_url || rec.content.offer_url ? `
                    <a href="${rec.content.content_url || rec.content.offer_url}"
                       target="_blank"
                       class="btn btn-primary btn-sm">
                        Learn More →
                    </a>
                ` : ''}
            </div>
        </div>
    `;
}

function formatPersonaName(personaId) {
    const names = {
        'high_utilization': 'High Utilization',
        'irregular_income': 'Irregular Income',
        'low_savings': 'Low Savings',
        'subscription_heavy': 'Subscription Heavy',
        'cash_flow_optimizer': 'Cash Flow Optimizer',
        'young_professional': 'Young Professional'
    };
    return names[personaId] || personaId;
}

function formatSignalName(signal) {
    const names = {
        'credit_utilization': 'Credit Utilization',
        'irregular_income': 'Irregular Income',
        'savings_balance': 'Low Savings',
        'subscription_count': 'High Subscriptions'
    };
    return names[signal] || signal;
}

// ===== Evaluation Metrics Tab (Epic 7) =====

let metricsCharts = {};

// Initialize metrics tab
document.addEventListener('DOMContentLoaded', () => {
    const metricsRefreshBtn = document.getElementById('metrics-refresh-btn');
    if (metricsRefreshBtn) {
        metricsRefreshBtn.addEventListener('click', loadEvaluationMetrics);
    }

    // Load metrics when tab is activated
    const metricsTab = document.querySelector('[data-tab="metrics"]');
    if (metricsTab) {
        metricsTab.addEventListener('click', () => {
            setTimeout(loadEvaluationMetrics, 100);
        });
    }
});

async function loadEvaluationMetrics() {
    const loadingDiv = document.getElementById('metrics-loading');
    const contentDiv = document.getElementById('metrics-content');
    const errorDiv = document.getElementById('metrics-error');

    loadingDiv.classList.remove('hidden');
    contentDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    try {
        const response = await fetch('/api/operator/metrics/latest');

        if (!response.ok) {
            throw new Error(`Failed to load metrics: ${response.statusText}`);
        }

        const data = await response.json();
        displayEvaluationMetrics(data);
        contentDiv.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading metrics:', error);
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.classList.remove('hidden');
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

function displayEvaluationMetrics(data) {
    // Update timestamp
    const timestamp = new Date(data.timestamp).toLocaleString();
    document.getElementById('metrics-timestamp').textContent = `Updated: ${timestamp}`;

    // Update overall score
    const overall = data.overall || {};
    document.getElementById('overall-score').textContent = overall.score || '--';
    document.getElementById('overall-grade').textContent = overall.grade || '--';

    const statusBadge = document.getElementById('overall-status');
    statusBadge.textContent = overall.status || '--';
    statusBadge.className = 'badge ' + getStatusClass(overall.status);

    // Update individual metrics
    updateCoverageMetrics(data.coverage, overall.components?.coverage);
    updateExplainabilityMetrics(data.explainability, overall.components?.explainability);
    updatePerformanceMetrics(data.performance, overall.components?.performance);
    updateAuditabilityMetrics(data.auditability, overall.components?.auditability);
    updateFairnessMetrics(data.fairness, overall.components?.fairness);
    updateComponentsChart(overall.components);
}

function updateCoverageMetrics(coverage, componentScore) {
    if (!coverage || coverage.error) {
        document.getElementById('coverage-status').textContent = 'N/A';
        document.getElementById('coverage-persona').textContent = '--';
        document.getElementById('coverage-signals').textContent = '--';
        document.getElementById('coverage-score').textContent = '--';
        return;
    }

    const personaRate = (coverage.persona_assignment_rate * 100).toFixed(1);
    const signalRate = (coverage.behavioral_signal_rate * 100).toFixed(1);

    document.getElementById('coverage-persona').textContent = `${personaRate}%`;
    document.getElementById('coverage-signals').textContent = `${signalRate}%`;
    document.getElementById('coverage-score').textContent = componentScore ? componentScore.toFixed(1) : '--';

    const status = personaRate >= 90 && signalRate >= 90 ? 'PASS' : 'WARNING';
    const statusBadge = document.getElementById('coverage-status');
    statusBadge.textContent = status;
    statusBadge.className = 'metric-badge ' + getStatusClass(status);

    // Create chart
    createBarChart('coverage-chart', ['Persona Assignment', 'Signal Detection'],
        [parseFloat(personaRate), parseFloat(signalRate)]);
}

function updateExplainabilityMetrics(explainability, componentScore) {
    if (!explainability || explainability.error) {
        document.getElementById('explainability-status').textContent = 'N/A';
        document.getElementById('explainability-presence').textContent = '--';
        document.getElementById('explainability-quality').textContent = '--';
        document.getElementById('explainability-score').textContent = '--';
        return;
    }

    // Check if data is nested in explainability_metrics
    const metrics = explainability.explainability_metrics || explainability;

    const presenceRate = metrics.rationale_presence_rate ? (metrics.rationale_presence_rate * 100).toFixed(1) : '--';
    const qualityScore = metrics.average_quality_score?.toFixed(1) || '--';

    document.getElementById('explainability-presence').textContent = presenceRate !== '--' ? `${presenceRate}%` : '--';
    document.getElementById('explainability-quality').textContent = qualityScore !== '--' ? `${qualityScore}/5` : '--';
    document.getElementById('explainability-score').textContent = componentScore ? componentScore.toFixed(1) : '--';

    const status = (presenceRate !== '--' && parseFloat(presenceRate) >= 90) &&
                   (qualityScore !== '--' && parseFloat(qualityScore) >= 3) ? 'PASS' : 'WARNING';
    const statusBadge = document.getElementById('explainability-status');
    statusBadge.textContent = status;
    statusBadge.className = 'metric-badge ' + getStatusClass(status);

    // Create chart
    if (presenceRate !== '--') {
        createDoughnutChart('explainability-chart',
            ['Has Rationale', 'Missing Rationale'],
            [parseFloat(presenceRate), 100 - parseFloat(presenceRate)]);
    }
}

function updatePerformanceMetrics(performance, componentScore) {
    if (!performance || performance.error) {
        document.getElementById('performance-status').textContent = 'N/A';
        document.getElementById('performance-latency').textContent = '--';
        document.getElementById('performance-throughput').textContent = '--';
        document.getElementById('performance-score').textContent = '--';
        return;
    }

    const latency = performance.average_latency_per_user?.toFixed(2) || '--';
    const throughput = performance.throughput_users_per_minute?.toFixed(1) || '--';

    document.getElementById('performance-latency').textContent = `${latency}s`;
    document.getElementById('performance-throughput').textContent = `${throughput} u/min`;
    document.getElementById('performance-score').textContent = componentScore ? componentScore.toFixed(1) : '--';

    const status = parseFloat(latency) < 5 ? 'PASS' : 'WARNING';
    const statusBadge = document.getElementById('performance-status');
    statusBadge.textContent = status;
    statusBadge.className = 'metric-badge ' + getStatusClass(status);

    // Create chart
    const percentiles = performance.latency_percentiles || {};
    createLineChart('performance-chart',
        ['p50', 'p95', 'p99'],
        [percentiles.p50 || 0, percentiles.p95 || 0, percentiles.p99 || 0]);
}

function updateAuditabilityMetrics(auditability, componentScore) {
    if (!auditability || auditability.error) {
        document.getElementById('auditability-status').textContent = 'N/A';
        document.getElementById('auditability-consent').textContent = '--';
        document.getElementById('auditability-compliance').textContent = '--';
        document.getElementById('auditability-score').textContent = '--';
        return;
    }

    // Check if data is nested in metrics or compliance_report
    const metrics = auditability.metrics || auditability;
    const compliance = auditability.compliance_report || {};

    const consentRate = metrics.consent_compliance_rate ? metrics.consent_compliance_rate.toFixed(1) :
                       (compliance.consent_adherence?.compliance_rate ? (compliance.consent_adherence.compliance_rate * 100).toFixed(1) : '--');
    const overallCompliance = metrics.overall_compliance_score?.toFixed(1) || '--';

    document.getElementById('auditability-consent').textContent = consentRate !== '--' ? `${consentRate}%` : '--';
    document.getElementById('auditability-compliance').textContent = overallCompliance !== '--' ? `${overallCompliance}%` : '--';
    document.getElementById('auditability-score').textContent = componentScore ? componentScore.toFixed(1) : '--';

    const status = consentRate !== '--' && parseFloat(consentRate) >= 99 ? 'PASS' : 'CRITICAL';
    const statusBadge = document.getElementById('auditability-status');
    statusBadge.textContent = status;
    statusBadge.className = 'metric-badge ' + getStatusClass(status);

    // Create chart
    const guardrails = metrics.guardrail_compliance || compliance.guardrail_checks || {};
    const consentVal = guardrails.consent || (compliance.consent_adherence?.compliance_rate ? compliance.consent_adherence.compliance_rate * 100 : 0);
    const eligibilityVal = guardrails.eligibility || (compliance.eligibility_validation?.compliance_rate ? compliance.eligibility_validation.compliance_rate * 100 : 0);
    const toneVal = guardrails.tone || (compliance.tone_validation?.compliance_rate ? compliance.tone_validation.compliance_rate * 100 : 0);
    const disclaimerVal = guardrails.disclaimer || (compliance.disclaimer_presence?.compliance_rate ? compliance.disclaimer_presence.compliance_rate * 100 : 0);

    createRadarChart('auditability-chart',
        ['Consent', 'Eligibility', 'Tone', 'Disclaimer'],
        [consentVal, eligibilityVal, toneVal, disclaimerVal]);
}

function updateFairnessMetrics(fairness, componentScore) {
    if (!fairness || fairness.error) {
        document.getElementById('fairness-status').textContent = 'N/A';
        document.getElementById('fairness-parity').textContent = '--';
        document.getElementById('fairness-assessment').textContent = '--';
        document.getElementById('fairness-score').textContent = '--';
        return;
    }

    const parityRatio = fairness.demographic_parity_ratio?.toFixed(2) || '--';
    const assessment = fairness.overall_fairness_assessment || 'N/A';

    document.getElementById('fairness-parity').textContent = parityRatio;
    document.getElementById('fairness-assessment').textContent = assessment;
    document.getElementById('fairness-score').textContent = componentScore ? componentScore.toFixed(1) : '--';

    const statusBadge = document.getElementById('fairness-status');
    statusBadge.textContent = assessment;
    statusBadge.className = 'metric-badge ' + getStatusClass(assessment);

    // Create chart
    const biasCount = fairness.bias_indicators_detected || 0;
    createDoughnutChart('fairness-chart',
        ['No Bias', 'Bias Detected'],
        [100 - (biasCount * 10), biasCount * 10]);
}

function updateComponentsChart(components) {
    if (!components) return;

    const labels = ['Coverage', 'Explainability', 'Performance', 'Auditability', 'Fairness'];
    const scores = [
        components.coverage || 0,
        components.explainability || 0,
        components.performance || 0,
        components.auditability || 0,
        components.fairness || 0
    ];

    createBarChart('components-chart', labels, scores, true);
}

// Chart creation helpers
function createBarChart(canvasId, labels, data, horizontal = false) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Destroy existing chart
    if (metricsCharts[canvasId]) {
        metricsCharts[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    metricsCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: horizontal ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: value => value + '%' }
                }
            }
        }
    });
}

function createDoughnutChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (metricsCharts[canvasId]) {
        metricsCharts[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    metricsCharts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(229, 231, 235, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function createLineChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (metricsCharts[canvasId]) {
        metricsCharts[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    metricsCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Latency (s)',
                data: data,
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createRadarChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (metricsCharts[canvasId]) {
        metricsCharts[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    metricsCharts[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Compliance %',
                data: data,
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: value => value + '%' }
                }
            }
        }
    });
}

function getStatusClass(status) {
    if (!status) return '';

    const statusUpper = status.toString().toUpperCase();

    if (statusUpper === 'PASS') return 'status-pass';
    if (statusUpper === 'WARNING' || statusUpper === 'CONCERN') return 'status-warning';
    if (statusUpper === 'FAIL' || statusUpper === 'CRITICAL') return 'status-fail';

    return 'status-default';
}

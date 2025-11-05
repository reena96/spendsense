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

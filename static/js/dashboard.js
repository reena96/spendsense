// SpendSense Evaluation Dashboard JavaScript

class EvaluationDashboard {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        // Load initial data
        this.loadMetrics();

        // Set up refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadMetrics();
        });

        // Auto-refresh every 30 seconds
        setInterval(() => this.loadMetrics(), 30000);
    }

    async loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();

            this.updateDashboard(data);
            this.updateLastUpdate();
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    }

    updateDashboard(data) {
        // Update overall score
        this.updateOverallScore(data.overall);

        // Update individual metric cards
        if (data.coverage) this.updateCoverageCard(data.coverage);
        if (data.explainability) this.updateExplainabilityCard(data.explainability);
        if (data.performance) this.updatePerformanceCard(data.performance);
        if (data.auditability) this.updateAuditabilityCard(data.auditability);
        if (data.fairness) this.updateFairnessCard(data.fairness);

        // Update component scores chart
        if (data.overall && data.overall.components) {
            this.updateComponentScoresChart(data.overall.components);
        }
    }

    updateOverallScore(overall) {
        if (!overall) return;

        document.getElementById('overallScore').querySelector('.score-value').textContent = overall.score || '--';
        document.getElementById('scoreGrade').textContent = `Grade: ${overall.grade || '--'}`;
        document.getElementById('scoreStatus').textContent = overall.status || '--';

        // Update status styling
        const scoreCard = document.querySelector('.score-card');
        scoreCard.className = 'score-card';
        if (overall.status === 'PASS') {
            scoreCard.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        } else if (overall.status === 'WARNING') {
            scoreCard.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
        } else if (overall.status === 'FAIL') {
            scoreCard.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        }
    }

    updateCoverageCard(coverage) {
        const personaRate = (coverage.persona_assignment_rate * 100).toFixed(1);
        const signalRate = (coverage.behavioral_signal_rate * 100).toFixed(1);

        document.getElementById('personaRate').textContent = `${personaRate}%`;
        document.getElementById('signalRate').textContent = `${signalRate}%`;
        document.getElementById('totalUsers').textContent = coverage.total_users || '--';

        // Update status badge
        const status = personaRate >= 95 && signalRate >= 95 ? 'pass' : personaRate >= 80 ? 'warning' : 'fail';
        this.updateStatusBadge('coverageStatus', status);

        // Update chart
        this.updateCoverageChart(coverage);
    }

    updateExplainabilityCard(explainability) {
        const rationalePresence = (explainability.rationale_presence_rate * 100).toFixed(1);
        const qualityScore = explainability.rationale_quality_score.toFixed(1);
        const traceCompleteness = (explainability.decision_trace_completeness * 100).toFixed(1);

        document.getElementById('rationalePresence').textContent = `${rationalePresence}%`;
        document.getElementById('qualityScore').textContent = `${qualityScore}/5`;
        document.getElementById('traceCompleteness').textContent = `${traceCompleteness}%`;

        // Update status
        const status = rationalePresence >= 95 && qualityScore >= 3 ? 'pass' : 'warning';
        this.updateStatusBadge('explainabilityStatus', status);

        // Update chart
        this.updateExplainabilityChart(explainability);
    }

    updatePerformanceCard(performance) {
        const avgLatency = performance.average_latency_per_user.toFixed(2);
        const throughput = performance.throughput.toFixed(1);
        const memoryUsage = performance.resource_utilization?.end?.memory_mb?.toFixed(0) || '--';

        document.getElementById('avgLatency').textContent = `${avgLatency}s`;
        document.getElementById('throughput').textContent = throughput;
        document.getElementById('memoryUsage').textContent = `${memoryUsage} MB`;

        // Update status (target: <5s)
        const status = avgLatency < 5 ? 'pass' : avgLatency < 10 ? 'warning' : 'fail';
        this.updateStatusBadge('performanceStatus', status);

        // Update chart
        this.updatePerformanceChart(performance);
    }

    updateAuditabilityCard(auditability) {
        const complianceScore = auditability.overall_compliance_score.toFixed(1);
        const consentCompliance = (auditability.consent_compliance_rate * 100).toFixed(1);
        const eligibilityCompliance = (auditability.eligibility_compliance_rate * 100).toFixed(1);

        document.getElementById('complianceScore').textContent = `${complianceScore}%`;
        document.getElementById('consentCompliance').textContent = `${consentCompliance}%`;
        document.getElementById('eligibilityCompliance').textContent = `${eligibilityCompliance}%`;

        // Consent must be 100%
        if (consentCompliance < 100) {
            document.getElementById('consentCompliance').style.color = 'var(--danger-color)';
        }

        // Update status
        const status = complianceScore >= 90 ? 'pass' : complianceScore >= 70 ? 'warning' : 'fail';
        this.updateStatusBadge('auditabilityStatus', status);

        // Update chart
        this.updateAuditabilityChart(auditability);
    }

    updateFairnessCard(fairness) {
        const assessment = fairness.overall_fairness_assessment || 'N/A';
        const parityRatio = fairness.demographic_parity_ratio?.toFixed(2) || 'N/A';
        const biasCount = fairness.bias_indicators?.length || 0;

        document.getElementById('fairnessAssessment').textContent = assessment;
        document.getElementById('parityRatio').textContent = parityRatio;
        document.getElementById('biasIndicators').textContent = biasCount === 0 ? 'None' : biasCount;

        // Update status
        const statusMap = { 'PASS': 'pass', 'CONCERN': 'warning', 'FAIL': 'fail', 'N/A': 'warning' };
        this.updateStatusBadge('fairnessStatus', statusMap[assessment] || 'warning');

        // Update chart
        this.updateFairnessChart(fairness);
    }

    updateStatusBadge(elementId, status) {
        const element = document.getElementById(elementId);
        element.className = `metric-status ${status}`;
        element.textContent = status.toUpperCase();
    }

    updateCoverageChart(coverage) {
        const ctx = document.getElementById('coverageChart');
        if (!ctx) return;

        if (this.charts.coverage) {
            this.charts.coverage.destroy();
        }

        this.charts.coverage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Persona Assignment', 'Behavioral Signals'],
                datasets: [{
                    label: 'Coverage Rate (%)',
                    data: [
                        coverage.persona_assignment_rate * 100,
                        coverage.behavioral_signal_rate * 100
                    ],
                    backgroundColor: ['#2563eb', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
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

    updateExplainabilityChart(explainability) {
        const ctx = document.getElementById('explainabilityChart');
        if (!ctx) return;

        if (this.charts.explainability) {
            this.charts.explainability.destroy();
        }

        this.charts.explainability = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Presence', 'Quality (scaled)', 'Trace Completeness'],
                datasets: [{
                    data: [
                        explainability.rationale_presence_rate * 100,
                        (explainability.rationale_quality_score / 5) * 100,
                        explainability.decision_trace_completeness * 100
                    ],
                    backgroundColor: ['#2563eb', '#10b981', '#f59e0b'],
                    borderWidth: 2,
                    borderColor: '#fff'
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

    updatePerformanceChart(performance) {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        if (this.charts.performance) {
            this.charts.performance.destroy();
        }

        const percentiles = performance.latency_percentiles || {};

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['p50', 'p95', 'p99'],
                datasets: [{
                    label: 'Latency (seconds)',
                    data: [percentiles.p50, percentiles.p95, percentiles.p99],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
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
                    y: {
                        beginAtZero: true,
                        ticks: { callback: value => value + 's' }
                    }
                }
            }
        });
    }

    updateAuditabilityChart(auditability) {
        const ctx = document.getElementById('auditabilityChart');
        if (!ctx) return;

        if (this.charts.auditability) {
            this.charts.auditability.destroy();
        }

        this.charts.auditability = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Consent', 'Eligibility', 'Tone', 'Disclaimer', 'Decision Trace', 'Audit Log'],
                datasets: [{
                    label: 'Compliance Rate (%)',
                    data: [
                        auditability.consent_compliance_rate * 100,
                        auditability.eligibility_compliance_rate * 100,
                        auditability.tone_compliance_rate * 100,
                        auditability.disclaimer_presence_rate * 100,
                        auditability.decision_trace_completeness * 100,
                        auditability.audit_log_completeness * 100
                    ],
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: '#10b981',
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

    updateFairnessChart(fairness) {
        const ctx = document.getElementById('fairnessChart');
        if (!ctx) return;

        if (this.charts.fairness) {
            this.charts.fairness.destroy();
        }

        // Show message if no demographic data
        if (!fairness.demographic_attributes_available) {
            ctx.parentElement.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">No demographic data available for fairness analysis</p>';
            return;
        }

        this.charts.fairness = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Demographic Parity', 'Equal Opportunity'],
                datasets: [{
                    label: 'Fairness Metrics',
                    data: [
                        fairness.demographic_parity_ratio || 0,
                        1 - (fairness.equal_opportunity_difference || 0)
                    ],
                    backgroundColor: ['#2563eb', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }

    updateComponentScoresChart(components) {
        const ctx = document.getElementById('componentScoresChart');
        if (!ctx) return;

        if (this.charts.componentScores) {
            this.charts.componentScores.destroy();
        }

        const labels = Object.keys(components);
        const data = Object.values(components);

        this.charts.componentScores = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{
                    label: 'Component Score (%)',
                    data: data,
                    backgroundColor: [
                        '#2563eb',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6'
                    ],
                    borderRadius: 8
                }]
            },
            options: {
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

    updateLastUpdate() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('lastUpdate').textContent = `Last updated: ${timeString}`;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EvaluationDashboard();
});

/**
 * Compliance Metrics Dashboard - Epic 6 Story 6.5
 *
 * Visual dashboard displaying compliance metrics: consent opt-in rates,
 * eligibility failure reasons, tone validation issues, and operator actions.
 * Requires admin or compliance role.
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ConsentMetrics {
  total_users: number;
  opted_in_count: number;
  opted_out_count: number;
  opt_in_rate_pct: number;
}

interface EligibilityMetrics {
  total_checks: number;
  passed: number;
  failed: number;
  pass_rate_pct: number;
  failure_reasons: Array<{ reason: string; count: number }>;
}

interface ToneMetrics {
  total_validations: number;
  passed: number;
  failed: number;
  pass_rate_pct: number;
  violations_by_category: Array<{ category: string; count: number }>;
}

interface OperatorMetrics {
  total_actions: number;
  approvals: number;
  overrides: number;
  flags: number;
  actions_by_operator: Array<{ operator_id: string; count: number }>;
}

interface ComplianceMetricsResponse {
  consent_metrics: ConsentMetrics;
  eligibility_metrics: EligibilityMetrics;
  tone_metrics: ToneMetrics;
  operator_metrics: OperatorMetrics;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

const TIME_RANGES = [
  { label: 'Last 30 Days', days: 30 },
  { label: 'Last 90 Days', days: 90 },
  { label: 'Last Year', days: 365 },
  { label: 'All Time', days: null },
];

export default function ComplianceMetrics() {
  const [timeRangeDays, setTimeRangeDays] = useState<number | null>(30);

  const { data, isLoading, error } = useQuery<ComplianceMetricsResponse>({
    queryKey: ['complianceMetrics', timeRangeDays],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (timeRangeDays !== null) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - timeRangeDays);
        params.append('start_date', startDate.toISOString());
        params.append('end_date', endDate.toISOString());
      }

      const response = await fetch(`/api/operator/audit/metrics?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('operator_token')}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('AUTHENTICATION_REQUIRED');
        }
        throw new Error('Failed to fetch compliance metrics');
      }

      return response.json();
    },
  });

  // Handle authentication error
  if (error && (error as Error).message === 'AUTHENTICATION_REQUIRED') {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
            <h3 className="text-lg font-medium text-yellow-800 mb-3">Authentication Required</h3>
            <p className="text-sm text-yellow-700 mb-3">
              This page requires admin or compliance role authentication.
              To test, open your browser console (F12) and run:
            </p>
            <pre className="p-3 bg-yellow-100 rounded text-xs overflow-x-auto font-mono mb-3">
localStorage.setItem('operator_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X2FkbWluIiwidXNlcm5hbWUiOiJhZG1pbl91c2VyIiwicm9sZSI6ImFkbWluIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTc2MjQ1ODg0OCwiaWF0IjoxNzYyNDU1MjQ4fQ.rPA76eg6jrehg1cT4NrhOIXHpj3XkUHbSIiN6x-ebQ0')
            </pre>
            <p className="text-sm text-yellow-700">Then refresh the page.</p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="text-center py-12 text-gray-500">Loading compliance metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="text-center py-12 text-red-600">
          Error loading metrics: {(error as Error).message}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const consentData = [
    { name: 'Opted In', value: data.consent_metrics.opted_in_count },
    { name: 'Opted Out', value: data.consent_metrics.opted_out_count },
  ];

  const eligibilityData = [
    { name: 'Passed', value: data.eligibility_metrics.passed },
    { name: 'Failed', value: data.eligibility_metrics.failed },
  ];

  const operatorActionsData = [
    { name: 'Approvals', value: data.operator_metrics.approvals },
    { name: 'Overrides', value: data.operator_metrics.overrides },
    { name: 'Flags', value: data.operator_metrics.flags },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Compliance Metrics Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Monitor system compliance across consent, eligibility, tone, and operator actions
        </p>
      </div>

      {/* Time Range Selector */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-3">
          {TIME_RANGES.map((range) => (
            <button
              key={range.label}
              onClick={() => setTimeRangeDays(range.days)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                timeRangeDays === range.days
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Consent Metrics Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Consent Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Users</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {data.consent_metrics.total_users.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Opted In</div>
            <div className="text-3xl font-bold text-green-600 mt-2">
              {data.consent_metrics.opted_in_count.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Opted Out</div>
            <div className="text-3xl font-bold text-red-600 mt-2">
              {data.consent_metrics.opted_out_count.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Opt-In Rate</div>
            <div className="text-3xl font-bold text-indigo-600 mt-2">
              {data.consent_metrics.opt_in_rate_pct.toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Consent Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={consentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {consentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Eligibility Metrics Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Eligibility Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Checks</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {data.eligibility_metrics.total_checks.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Passed</div>
            <div className="text-3xl font-bold text-green-600 mt-2">
              {data.eligibility_metrics.passed.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Failed</div>
            <div className="text-3xl font-bold text-red-600 mt-2">
              {data.eligibility_metrics.failed.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Pass Rate</div>
            <div className="text-3xl font-bold text-indigo-600 mt-2">
              {data.eligibility_metrics.pass_rate_pct.toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Pass/Fail Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={eligibilityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {eligibilityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Failure Reasons</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.eligibility_metrics.failure_reasons.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="reason" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tone Metrics Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Tone Validation Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Validations</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {data.tone_metrics.total_validations.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Passed</div>
            <div className="text-3xl font-bold text-green-600 mt-2">
              {data.tone_metrics.passed.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Failed</div>
            <div className="text-3xl font-bold text-red-600 mt-2">
              {data.tone_metrics.failed.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Pass Rate</div>
            <div className="text-3xl font-bold text-indigo-600 mt-2">
              {data.tone_metrics.pass_rate_pct.toFixed(1)}%
            </div>
          </div>
        </div>

        {data.tone_metrics.violations_by_category.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Violations by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.tone_metrics.violations_by_category.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Operator Action Metrics Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Operator Action Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Actions</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {data.operator_metrics.total_actions.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Approvals</div>
            <div className="text-3xl font-bold text-green-600 mt-2">
              {data.operator_metrics.approvals.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Overrides</div>
            <div className="text-3xl font-bold text-orange-600 mt-2">
              {data.operator_metrics.overrides.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Flags</div>
            <div className="text-3xl font-bold text-red-600 mt-2">
              {data.operator_metrics.flags.toLocaleString()}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Action Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={operatorActionsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6">
                  {operatorActionsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Actions by Operator</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.operator_metrics.actions_by_operator.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="operator_id" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

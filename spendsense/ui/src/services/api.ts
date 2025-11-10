/**
 * API Service
 * Centralized API calls for SpendSense
 */

import { getApiUrl } from '../config/api';

export interface SignalEvidence {
  matched: boolean;
  evidence: Record<string, any>;
  matched_conditions: string[];
}

export interface PersonaAssignment {
  assignment_id: string;
  assigned_persona_id: string;
  priority: number;
  assigned_at: string;
  all_qualifying_personas: string[];
  prioritization_reason: string;
  match_evidence: Record<string, SignalEvidence>;
}

export interface UserProfile {
  user_id: string;
  assignments: {
    '30d'?: PersonaAssignment;
    '180d'?: PersonaAssignment;
  };
}

export interface SignalData {
  name: string;
  metric: string;
  status: 'good' | 'warning' | 'attention' | 'neutral';
  value: number | string;
  path: string;
}

/**
 * Fetch user profile with persona assignments and behavioral signals
 */
export async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const response = await fetch(getApiUrl(`/api/profile/${userId}`));

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch profile' }));
    throw new Error(error.detail || 'Failed to fetch profile');
  }

  return response.json();
}

/**
 * Extract signal data from persona assignment for dashboard display
 */
export function extractSignalData(assignment: PersonaAssignment | undefined): SignalData[] {
  if (!assignment || !assignment.match_evidence) {
    return getDefaultSignalData();
  }

  const signals: SignalData[] = [];
  const evidence = assignment.match_evidence;

  // Credit Utilization Signal
  if (evidence.high_utilization) {
    const utilization = evidence.high_utilization.evidence.credit_max_utilization_pct;
    const pct = Math.round((utilization || 0) * 100);
    signals.push({
      name: 'Credit Utilization',
      metric: `${pct}%`,
      value: pct,
      status: pct > 70 ? 'warning' : pct > 50 ? 'attention' : 'good',
      path: '/dashboard/signals/credit',
    });
  }

  // Subscriptions Signal
  if (evidence.subscription_heavy) {
    const subCount = evidence.subscription_heavy.evidence.subscription_count || 0;
    const subPct = evidence.subscription_heavy.evidence.subscription_pct_income || 0;
    signals.push({
      name: 'Subscriptions',
      metric: `${subCount} active`,
      value: subCount,
      status: subPct > 0.15 ? 'warning' : subPct > 0.10 ? 'attention' : 'neutral',
      path: '/dashboard/signals/subscriptions',
    });
  }

  // Savings Signal
  if (evidence.low_savings) {
    const efund = evidence.low_savings.evidence.savings_emergency_fund_months || 0;
    signals.push({
      name: 'Savings',
      metric: `${efund.toFixed(1)} months`,
      value: efund,
      status: efund < 3 ? 'attention' : efund < 6 ? 'warning' : 'good',
      path: '/dashboard/signals/savings',
    });
  }

  // Income Signal
  if (evidence.irregular_income) {
    const payGap = evidence.irregular_income.evidence.income_median_pay_gap_days || 14;
    const isRegular = payGap <= 16; // Bi-weekly or more frequent
    signals.push({
      name: 'Income',
      metric: isRegular ? 'Stable' : 'Variable',
      value: payGap,
      status: isRegular ? 'good' : 'attention',
      path: '/dashboard/signals/income',
    });
  }

  // If we have fewer than 4 signals, fill with defaults
  while (signals.length < 4) {
    const defaultSignals = getDefaultSignalData();
    const missing = defaultSignals.find(
      (ds) => !signals.some((s) => s.name === ds.name)
    );
    if (missing) signals.push(missing);
    else break;
  }

  return signals;
}

/**
 * Get default signal data when no real data is available
 */
function getDefaultSignalData(): SignalData[] {
  return [
    {
      name: 'Credit Utilization',
      metric: 'N/A',
      value: 0,
      status: 'neutral',
      path: '/dashboard/signals/credit',
    },
    {
      name: 'Subscriptions',
      metric: 'N/A',
      value: 0,
      status: 'neutral',
      path: '/dashboard/signals/subscriptions',
    },
    {
      name: 'Savings',
      metric: 'N/A',
      value: 0,
      status: 'neutral',
      path: '/dashboard/signals/savings',
    },
    {
      name: 'Income',
      metric: 'N/A',
      value: 0,
      status: 'neutral',
      path: '/dashboard/signals/income',
    },
  ];
}

/**
 * Format signal value for display
 */
export function formatSignalValue(signalName: string, value: number): string {
  switch (signalName) {
    case 'Credit Utilization':
      return `${Math.round(value * 100)}%`;
    case 'Subscriptions':
      return `${value} active`;
    case 'Savings':
      return `${value.toFixed(1)} months`;
    case 'Income':
      return value <= 16 ? 'Stable' : 'Variable';
    default:
      return String(value);
  }
}

/**
 * Recommendation API Types
 */
export interface RecommendationContent {
  id: string;
  type: string;
  title: string;
  description: string;
  category?: string;
  priority: number;
  content_url?: string;
  offer_url?: string;
  key_benefits?: string[];
  provider?: string;
}

export interface Recommendation {
  item_type: 'education' | 'partner_offer';
  item_id: string;
  content: RecommendationContent;
  rationale: string;
  persona_match_reason: string;
  signal_citations: string[];
}

export interface RecommendationsResponse {
  user_id: string;
  persona_id: string;
  time_window: string;
  recommendations: Recommendation[];
  disclaimer: string;
  metadata: {
    total_recommendations: number;
    education_count: number;
    partner_offer_count: number;
  };
}

/**
 * Fetch personalized recommendations for a user
 */
export async function fetchRecommendations(
  userId: string,
  timeWindow: '30d' | '180d' = '30d'
): Promise<RecommendationsResponse> {
  const response = await fetch(
    getApiUrl(`/api/recommendations/${userId}?time_window=${timeWindow}`)
  );

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error('Consent required to view recommendations');
    }
    if (response.status === 404) {
      throw new Error('User not found');
    }
    throw new Error('Failed to load recommendations');
  }

  return response.json();
}

/**
 * Signal API Interfaces and Methods
 */

// Subscriptions Signal
export interface DetectedSubscription {
  merchant_name: string;
  cadence: string;
  avg_amount: number;
  transaction_count: number;
  last_charge_date: string;
  median_gap_days: number;
}

export interface SubscriptionsSignalResponse {
  user_id: string;
  window_days: number;
  reference_date: string;
  subscription_count: number;
  monthly_recurring_spend: number;
  total_spend: number;
  subscription_share: number;
  detected_subscriptions: DetectedSubscription[];
}

export async function fetchSubscriptionsSignal(userId: string): Promise<SubscriptionsSignalResponse> {
  const response = await fetch(getApiUrl(`/api/signals/${userId}/subscriptions`));

  if (!response.ok) {
    throw new Error('Failed to load subscriptions data');
  }

  return response.json();
}

// Credit Utilization Signal
export interface CreditCardDetail {
  account_id: string;
  balance: number;
  limit: number;
  utilization: number;
  utilization_tier: string;
  is_overdue: boolean;
  has_interest_charges: boolean;
}

export interface CreditSignalResponse {
  user_id: string;
  window_days: number;
  reference_date: string;
  num_credit_cards: number;
  aggregate_utilization: number;
  high_utilization_count: number;
  very_high_utilization_count: number;
  minimum_payment_only_count: number;
  overdue_count: number;
  has_interest_charges: boolean;
  per_card_details: CreditCardDetail[];
}

export async function fetchCreditSignal(userId: string): Promise<CreditSignalResponse> {
  const response = await fetch(getApiUrl(`/api/signals/${userId}/credit`));

  if (!response.ok) {
    throw new Error('Failed to load credit data');
  }

  return response.json();
}

// Savings Signal
export interface SavingsSignalResponse {
  user_id: string;
  window_days: number;
  reference_date: string;
  net_inflow: number;
  savings_growth_rate: number;
  emergency_fund_months: number;
  total_savings_balance: number;
  avg_monthly_expenses: number;
  has_savings_accounts: boolean;
}

export async function fetchSavingsSignal(userId: string): Promise<SavingsSignalResponse> {
  const response = await fetch(getApiUrl(`/api/signals/${userId}/savings`));

  if (!response.ok) {
    throw new Error('Failed to load savings data');
  }

  return response.json();
}

// Income Signal
export interface IncomeSignalResponse {
  user_id: string;
  window_days: number;
  reference_date: string;
  num_income_transactions: number;
  total_income: number;
  avg_income_per_payment: number;
  payment_frequency: string;
  median_pay_gap_days: number;
  income_variability_cv: number;
  cash_flow_buffer_months: number;
  has_regular_income: boolean;
  payroll_dates: string[];
}

export async function fetchIncomeSignal(userId: string): Promise<IncomeSignalResponse> {
  const response = await fetch(getApiUrl(`/api/signals/${userId}/income`));

  if (!response.ok) {
    throw new Error('Failed to load income data');
  }

  return response.json();
}

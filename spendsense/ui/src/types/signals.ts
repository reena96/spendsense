/**
 * TypeScript types for Signal Dashboard (Story 6.2)
 */

export interface UserSearchResult {
  user_id: string;
  name: string;
  persona: string;
}

export interface SubscriptionMetrics {
  recurring_merchants: number;
  monthly_spend: number;
  subscription_share_pct: number;
  total_spend: number;
  detected_subscriptions: Array<{
    merchant_name: string;
    monthly_amount: number;
  }>;
}

export interface SavingsMetrics {
  net_inflow: number;
  growth_rate_pct: number;
  emergency_fund_months: number;
  total_balance: number;
  avg_monthly_expenses: number;
  has_savings_accounts: boolean;
}

export interface CreditMetrics {
  max_utilization_pct: number;
  has_interest_charges: boolean;
  minimum_payment_only: boolean;
  overdue_status: boolean;
  num_cards: number;
  high_utilization_count: number;
  utilization_by_card: Array<{
    card_name: string;
    utilization_pct: number;
  }>;
}

export interface IncomeMetrics {
  payroll_count: number;
  median_pay_gap_days: number;
  cash_flow_buffer_months: number;
  total_income: number;
  payment_frequency: string;
  has_regular_income: boolean;
}

export interface SignalMetrics {
  time_window: string;
  computed_at: string;
  subscription: SubscriptionMetrics;
  savings: SavingsMetrics;
  credit: CreditMetrics;
  income: IncomeMetrics;
  metadata: {
    data_completeness: Record<string, boolean>;
    fallbacks_applied: string[];
  };
}

export interface UserSignals {
  user_id: string;
  data_30d: SignalMetrics | null;
  data_180d: SignalMetrics | null;
}

export type TimeWindow = '30d' | '180d' | 'both';
export type ExportFormat = 'csv' | 'json';

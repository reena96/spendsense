/**
 * Formatting utilities for Signal Dashboard
 */

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

export function formatPercent(value: number | undefined | null, decimals: number = 1): string {
  if (value === undefined || value === null || isNaN(value)) {
    return 'N/A';
  }
  return `${value.toFixed(decimals)}%`;
}

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getUtilizationColor(utilization: number | undefined | null): string {
  if (utilization === undefined || utilization === null || isNaN(utilization)) {
    return 'text-gray-600 bg-gray-50';
  }
  if (utilization >= 70) return 'text-red-600 bg-red-50';
  if (utilization >= 30) return 'text-yellow-600 bg-yellow-50';
  return 'text-green-600 bg-green-50';
}

export function getSavingsColor(months: number): string {
  if (months >= 3) return 'text-green-600';
  if (months >= 1) return 'text-yellow-600';
  return 'text-red-600';
}

export function getPaymentFrequencyLabel(frequency: string): string {
  const labels: Record<string, string> = {
    'biweekly': 'Bi-weekly',
    'monthly': 'Monthly',
    'semimonthly': 'Semi-monthly',
    'weekly': 'Weekly',
    'irregular': 'Irregular',
    'unknown': 'Unknown',
  };
  return labels[frequency] || frequency;
}

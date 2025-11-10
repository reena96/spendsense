/**
 * Time Window Toggle Component (Story 6.2 - Task 2, AC #7)
 * Allows switching between 30-day, 180-day, and side-by-side views
 */

import type { TimeWindow } from '../types/signals';

interface TimeWindowToggleProps {
  selected: TimeWindow;
  onChange: (window: TimeWindow) => void;
}

export function TimeWindowToggle({ selected, onChange }: TimeWindowToggleProps) {
  const options: Array<{ value: TimeWindow; label: string }> = [
    { value: '30d', label: '30 Days' },
    { value: '180d', label: '180 Days' },
    { value: 'both', label: 'Side-by-Side' },
  ];

  return (
    <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-colors
            ${
              selected === option.value
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-700 hover:bg-gray-50'
            }
          `}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

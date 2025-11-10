/**
 * Time Window Toggle Component
 * Allows users to switch between 30-day, 180-day, and comparison views
 * Stores preference in localStorage
 */

import React, { useState, useEffect } from 'react';

export type TimeWindow = '30d' | '180d' | 'compare';

interface TimeWindowToggleProps {
  onChange?: (window: TimeWindow) => void;
  selected?: TimeWindow;
}

const TimeWindowToggle: React.FC<TimeWindowToggleProps> = ({ onChange, selected: controlledSelected }) => {
  const [internalSelected, setInternalSelected] = useState<TimeWindow>(() => {
    const stored = localStorage.getItem('spendsense_time_window');
    return (stored as TimeWindow) || '30d';
  });

  // Use controlled value if provided, otherwise use internal state
  const selected = controlledSelected !== undefined ? controlledSelected : internalSelected;

  useEffect(() => {
    if (controlledSelected === undefined) {
      localStorage.setItem('spendsense_time_window', internalSelected);
      onChange?.(internalSelected);
    }
  }, [internalSelected, onChange, controlledSelected]);

  const options: Array<{ value: TimeWindow; label: string }> = [
    { value: '30d', label: '30-Day View' },
    { value: '180d', label: '180-Day View' },
    { value: 'compare', label: 'Compare Both' },
  ];

  const handleClick = (value: TimeWindow) => {
    if (controlledSelected === undefined) {
      setInternalSelected(value);
    }
    onChange?.(value);
  };

  return (
    <div className="inline-flex rounded-lg bg-gray-100 p-1 gap-1" role="group" aria-label="Time window selection">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => handleClick(option.value)}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-colors
            focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-1
            ${
              selected === option.value
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-gray-700 hover:bg-gray-200'
            }
          `}
          aria-pressed={selected === option.value}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default TimeWindowToggle;

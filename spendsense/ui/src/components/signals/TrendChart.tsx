/**
 * Trend Chart Component
 * Reusable line/bar chart for displaying signal trends over time
 * Uses simple SVG implementation (can be replaced with Recharts/Chart.js later)
 */

import React from 'react';

export interface ChartDataPoint {
  label: string;
  value: number;
  date?: string;
}

interface TrendChartProps {
  data: ChartDataPoint[];
  type?: 'line' | 'bar';
  color?: string;
  height?: number;
  showGrid?: boolean;
  formatValue?: (value: number) => string;
}

const TrendChart: React.FC<TrendChartProps> = ({
  data,
  type = 'line',
  color = '#0891b2', // cyan-600
  height = 200,
  showGrid = true,
  formatValue = (v) => v.toString(),
}) => {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center bg-gray-50 rounded-lg" style={{ height }}>
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.value));
  const minValue = Math.min(...data.map((d) => d.value));
  const range = maxValue - minValue || 1;

  const padding = 40;
  const chartWidth = 600;
  const chartHeight = height - padding;
  const stepX = (chartWidth - padding * 2) / (data.length - 1 || 1);

  const getY = (value: number) => {
    const normalized = (value - minValue) / range;
    return chartHeight - normalized * (chartHeight - padding) + padding / 2;
  };

  return (
    <div className="w-full overflow-x-auto">
      <svg width="100%" height={height} viewBox={`0 0 ${chartWidth} ${height}`} className="bg-white rounded-lg">
        {/* Grid Lines */}
        {showGrid && (
          <g className="grid-lines">
            {[0, 0.25, 0.5, 0.75, 1].map((percent, i) => {
              const y = chartHeight - percent * (chartHeight - padding) + padding / 2;
              const value = minValue + percent * range;
              return (
                <g key={i}>
                  <line
                    x1={padding}
                    y1={y}
                    x2={chartWidth - padding}
                    y2={y}
                    stroke="#e5e7eb"
                    strokeWidth="1"
                  />
                  <text
                    x={padding - 10}
                    y={y + 4}
                    textAnchor="end"
                    fontSize="12"
                    fill="#6b7280"
                  >
                    {formatValue(value)}
                  </text>
                </g>
              );
            })}
          </g>
        )}

        {/* Chart Content */}
        {type === 'line' ? (
          <>
            {/* Line Path */}
            <path
              d={data
                .map((point, i) => {
                  const x = padding + i * stepX;
                  const y = getY(point.value);
                  return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                })
                .join(' ')}
              fill="none"
              stroke={color}
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data Points */}
            {data.map((point, i) => {
              const x = padding + i * stepX;
              const y = getY(point.value);
              return (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r="4"
                  fill={color}
                  stroke="white"
                  strokeWidth="2"
                  className="hover:r-6 transition-all"
                >
                  <title>{`${point.label}: ${formatValue(point.value)}`}</title>
                </circle>
              );
            })}
          </>
        ) : (
          <>
            {/* Bars */}
            {data.map((point, i) => {
              const x = padding + i * stepX - 15;
              const y = getY(point.value);
              const barHeight = chartHeight - y + padding / 2;
              return (
                <rect
                  key={i}
                  x={x}
                  y={y}
                  width="30"
                  height={barHeight}
                  fill={color}
                  opacity="0.8"
                  rx="4"
                  className="hover:opacity-100 transition-opacity"
                >
                  <title>{`${point.label}: ${formatValue(point.value)}`}</title>
                </rect>
              );
            })}
          </>
        )}

        {/* X-Axis Labels */}
        {data.map((point, i) => {
          const x = padding + i * stepX;
          return (
            <text
              key={i}
              x={x}
              y={chartHeight + padding}
              textAnchor="middle"
              fontSize="11"
              fill="#6b7280"
            >
              {point.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

export default TrendChart;

import React from 'react';

interface SeverityGaugeProps {
  score: number;
  label: string;
}

function getSeverityColor(label: string): string {
  switch (label?.toLowerCase()) {
    case 'critical': return '#D9534F';
    case 'high': return '#C95E45';
    case 'medium': return '#C98255';
    default: return '#55C98A';
  }
}

export const SeverityGauge: React.FC<SeverityGaugeProps> = ({ score, label }) => {
  const color = getSeverityColor(label);
  const clampedScore = Math.max(0, Math.min(100, score));

  // SVG arc gauge: 180° arc from left to right
  const cx = 80;
  const cy = 80;
  const r = 60;
  const startAngle = 180; // degrees
  const totalArc = 180;   // degrees sweep

  function polarToCartesian(angle: number) {
    const rad = (angle * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  }

  function describeArc(startDeg: number, endDeg: number) {
    const s = polarToCartesian(startDeg);
    const e = polarToCartesian(endDeg);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  }

  // Fill angle: from 180° to (180 + score/100 * 180)°
  const fillEndAngle = startAngle + (clampedScore / 100) * totalArc;

  // Track arc (grey)
  const trackPath = describeArc(startAngle, startAngle + totalArc);
  // Fill arc (colored)
  const fillPath = clampedScore > 0 ? describeArc(startAngle, fillEndAngle) : null;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="160" height="90" viewBox="0 0 160 90">
        {/* Background track */}
        <path
          d={trackPath}
          fill="none"
          stroke="#1B1D20"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* Color fill */}
        {fillPath && (
          <path
            d={fillPath}
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
          />
        )}
        {/* Center score text */}
        <text
          x={cx}
          y={cy - 2}
          textAnchor="middle"
          fill="#D4D9DF"
          fontSize="20"
          fontFamily="IBM Plex Mono, monospace"
          fontWeight="700"
        >
          {clampedScore}
        </text>
        <text
          x={cx}
          y={cy + 14}
          textAnchor="middle"
          fill="#798690"
          fontSize="9"
          fontFamily="IBM Plex Mono, monospace"
        >
          / 100
        </text>
      </svg>
      <div
        className="font-mono text-xs font-bold px-3 py-1 rounded border uppercase tracking-wider"
        style={{ color, borderColor: color + '60', background: color + '12' }}
      >
        {label?.toUpperCase() || 'HIGH'} SEVERITY
      </div>
    </div>
  );
};

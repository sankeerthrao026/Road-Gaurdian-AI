import React from 'react';

interface ShapChartProps {
  shapValues: Record<string, number>;
}

const FRIENDLY_NAMES: Record<string, string> = {
  vehicle_count: 'Vehicle Count',
  person_on_road: 'Person on Road',
  fire_smoke: 'Fire / Smoke',
  rollover: 'Vehicle Rollover',
  traffic_impact: 'Traffic Impact',
};

export const ShapChart: React.FC<ShapChartProps> = ({ shapValues }) => {
  const entries = Object.entries(shapValues);
  if (!entries.length) return null;

  const maxAbs = Math.max(...entries.map(([, v]) => Math.abs(v)), 0.01);

  return (
    <div className="w-full space-y-2.5">
      <div className="font-mono text-[10px] font-bold text-[#999EA5] uppercase tracking-wider mb-1">
        SHAP Feature Attribution
      </div>
      {entries.map(([feat, val]) => {
        const isPositive = val >= 0;
        const pct = Math.min(Math.abs(val) / maxAbs, 1) * 100;
        const color = isPositive ? '#C98255' : '#55C98A';
        const label = FRIENDLY_NAMES[feat] ?? feat.replace(/_/g, ' ');

        return (
          <div key={feat} className="text-xs font-mono">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[#999EA5] capitalize">{label}</span>
              <span
                className="font-bold text-[10px]"
                style={{ color }}
              >
                {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
              </span>
            </div>
            {/* Bar track */}
            <div className="w-full bg-[#1B1D20] h-1.5 rounded overflow-hidden">
              <div
                className="h-full rounded transition-all duration-500"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

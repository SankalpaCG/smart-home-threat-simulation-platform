import React from 'react';

const ThreatHeatmap = ({ data }) => {
  // We want to show the last 30 data points across 4 core metrics
  const recentData = data.slice(-30);
  const padding = Array(Math.max(0, 30 - recentData.length)).fill(null);
  const displayData = [...padding, ...recentData];

  // Normalize helper
  const normalize = (val, max) => Math.min(1, Math.max(0, (val || 0) / max));

  const metrics = [
    { key: 'packets_per_second', label: 'Network Vol', max: 50000, color: '16, 185, 129' }, // emerald-500
    { key: 'auth_attempt_rate', label: 'Auth Load', max: 20000, color: '249, 115, 22' },    // orange-500
    { key: 'broker_response_latency_ms', label: 'Latency', max: 50, color: '244, 63, 94' },    // rose-500
    { key: 'payload_entropy', label: 'Entropy', max: 8, color: '168, 85, 247' },          // purple-500
  ];

  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-80 flex flex-col">
      <h2 className="text-lg font-bold mb-4 text-emerald-400">Threat Matrix Heatmap</h2>
      <div className="flex-1 flex flex-col justify-around">
        {metrics.map((m) => (
          <div key={m.key} className="flex items-center space-x-1">
            <div className="w-24 text-xs font-semibold text-slate-400 text-right truncate pr-2 tracking-wide uppercase">{m.label}</div>
            <div className="flex-1 flex space-x-[2px] h-10">
              {displayData.map((d, i) => {
                if (!d) return <div key={i} className="flex-1 bg-slate-900 rounded-[2px]" />;
                const intensity = normalize(d[m.key], m.max);
                // Ensure at least 0.1 opacity so the cell is visible, max 1.0
                const opacity = 0.1 + (intensity * 0.9);
                return (
                  <div 
                    key={i} 
                    className="flex-1 rounded-[2px] transition-all duration-300 border border-slate-800/50"
                    style={{ backgroundColor: `rgba(${m.color}, ${opacity})` }}
                    title={`${m.label}: ${Number(d[m.key]).toFixed(2)}`}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <div className="flex justify-between items-center mt-2 px-24">
        <span className="text-[10px] text-slate-500">T - 30s</span>
        <span className="text-[10px] text-slate-500">Live</span>
      </div>
    </div>
  );
};

export default ThreatHeatmap;

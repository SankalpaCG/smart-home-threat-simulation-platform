import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';

const AnomalyScatter = ({ data }) => {
  // We plot Packets/s vs Broker Response Latency
  const chartData = data.map((d, index) => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    packets: d.packets_per_second || 0,
    latency: d.broker_response_latency_ms || 0,
    z: 1, // Constant size for simple scatter
    prediction: d.prediction || 0
  }));

  const normalData = chartData.filter(d => d.prediction === 0);
  const anomalyData = chartData.filter(d => d.prediction !== 0);

  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-80">
      <h2 className="text-lg font-bold mb-2 text-rose-400">Volumetric Scatter (Packets vs Latency)</h2>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis type="number" dataKey="packets" name="Packets/s" stroke="#94a3b8" fontSize={12} tickCount={5} domain={['auto', 'auto']} />
          <YAxis type="number" dataKey="latency" name="Latency (ms)" stroke="#94a3b8" fontSize={12} tickCount={5} domain={['auto', 'auto']} />
          <ZAxis type="number" dataKey="z" range={[20, 20]} />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Scatter name="Normal" data={normalData} fill="#10b981" isAnimationActive={false} />
          <Scatter name="Anomaly" data={anomalyData} fill="#ef4444" isAnimationActive={false} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AnomalyScatter;

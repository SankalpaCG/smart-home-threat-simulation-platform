import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const LiveGraph = ({ data }) => {
  const chartData = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    packets: d.packets_per_second || 0,
    latency: d.broker_response_latency_ms || 0
  }));

  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-80">
      <h2 className="text-lg font-bold mb-2 text-cyan-400">Network Volumetrics</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
          <YAxis yAxisId="left" stroke="#94a3b8" fontSize={12} />
          <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" fontSize={12} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="packets" name="Packets/s" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line yAxisId="right" type="monotone" dataKey="latency" name="Latency (ms)" stroke="#f43f5e" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiveGraph;

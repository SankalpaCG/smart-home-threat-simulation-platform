import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AuthGraph = ({ data }) => {
  const chartData = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    attempts: d.auth_attempt_rate || 0,
    failures: d.auth_failure_rate || 0,
  }));

  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-80">
      <h2 className="text-lg font-bold mb-2 text-orange-400">Authentication Activity</h2>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorAttempts" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorFailures" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Area type="monotone" dataKey="attempts" stroke="#f97316" fillOpacity={1} fill="url(#colorAttempts)" name="Auth Attempts/s" isAnimationActive={false} />
          <Area type="monotone" dataKey="failures" stroke="#ef4444" fillOpacity={1} fill="url(#colorFailures)" name="Auth Failures/s" isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AuthGraph;

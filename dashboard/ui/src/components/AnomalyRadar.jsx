import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

const AnomalyRadar = ({ data }) => {
  const latest = data[data.length - 1] || {};
  
  const radarData = [
    { subject: 'Entropy', A: latest.payload_entropy || 0, fullMark: 8 },
    { subject: 'Dup Rate', A: (latest.duplicate_payload_rate || 0) * 10, fullMark: 10 },
    { subject: 'Lat Z-Score', A: Math.abs(latest.latency_zscore || 0), fullMark: 5 },
    { subject: 'Cons Failures', A: Math.min((latest.consecutive_failures || 0) / 10, 10), fullMark: 10 },
    { subject: 'Publish Rate', A: Math.min((latest.mqtt_publish_rate || 0) / 100, 10), fullMark: 10 },
  ];

  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-80 flex flex-col">
      <h2 className="text-lg font-bold mb-0 text-purple-400">Anomaly Signature</h2>
      <div className="flex-1 -mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
            <PolarGrid stroke="#475569" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 'dataMax']} tick={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Radar name="Anomaly Score" dataKey="A" stroke="#a855f7" fill="#a855f7" fillOpacity={0.5} isAnimationActive={true} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default AnomalyRadar;

import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import LiveGraph from './components/LiveGraph';
import AuthGraph from './components/AuthGraph';
import ThreatHeatmap from './components/ThreatHeatmap';
import AnomalyScatter from './components/AnomalyScatter';
import AnomalyRadar from './components/AnomalyRadar';
import AttackControls from './components/AttackControls';
import AlertLog from './components/AlertLog';
import { ShieldCheck } from 'lucide-react';

const API_URL = 'http://localhost:3001';
const socket = io(API_URL);

function App() {
  const [telemetry, setTelemetry] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));
    
    socket.on('history', (data) => setTelemetry(data));
    socket.on('alert_history', (data) => setAlerts(data));

    socket.on('telemetry', (data) => {
      setTelemetry((prev) => {
        const next = [...prev, data];
        if (next.length > 100) next.shift(); // Keep last 100 points
        return next;
      });
    });

    socket.on('alert', (alert) => {
      setAlerts((prev) => {
        const next = [alert, ...prev];
        if (next.length > 100) next.pop();
        return next;
      });
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('history');
      socket.off('alert_history');
      socket.off('telemetry');
      socket.off('alert');
    };
  }, []);

  // Compute some quick stats for the header
  const latest = telemetry[telemetry.length - 1] || {};
  const currentAttempts = latest.auth_attempt_rate || 0;
  const currentPPS = latest.packets_per_second || 0;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 p-6 font-sans">
      
      {/* Header */}
      <header className="flex justify-between items-center mb-6 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-md">
        <div className="flex items-center space-x-4">
          <div className="bg-cyan-500/20 p-3 rounded-lg border border-cyan-500/50">
            <ShieldCheck size={32} className="text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Sovereignty OS
            </h1>
            <p className="text-slate-400 text-sm tracking-widest uppercase">Active ML-IPS Deployment Node</p>
          </div>
        </div>
        
        <div className="flex space-x-6 text-sm">
          <div className="flex flex-col items-end">
            <span className="text-slate-500">Backend Status</span>
            <span className={connected ? "text-emerald-400 font-bold" : "text-rose-500 font-bold"}>
              {connected ? "ONLINE" : "OFFLINE"}
            </span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-slate-500">Current Load (Auth/s)</span>
            <span className="text-cyan-400 font-mono text-lg">{currentAttempts.toFixed(2)}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-slate-500">Network (Pkt/s)</span>
            <span className="text-emerald-400 font-mono text-lg">{currentPPS.toFixed(2)}</span>
          </div>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 mb-6">
        
        {/* Left Column (Graphs) */}
        <div className="xl:col-span-3 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <LiveGraph data={telemetry} />
            <AuthGraph data={telemetry} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ThreatHeatmap data={telemetry} />
            <AnomalyScatter data={telemetry} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <AnomalyRadar data={telemetry} />
            </div>
            <div className="md:col-span-2">
              <AttackControls apiUrl={API_URL} />
            </div>
          </div>
        </div>
        
        {/* Right Column (Alerts) */}
        <div className="xl:col-span-1">
          <AlertLog alerts={alerts} />
        </div>
      </div>

    </div>
  );
}

export default App;

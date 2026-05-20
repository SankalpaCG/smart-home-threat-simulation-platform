import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Activity, Wifi } from 'lucide-react';
import clsx from 'clsx';

const AttackControls = ({ apiUrl }) => {
  const [status, setStatus] = useState({
    normal: false,
    bruteforce: false,
    dos: false,
    replay: false,
  });

  const [targetIp, setTargetIp] = useState('192.168.21.165');
  const [espIp, setEspIp] = useState('192.168.1.107');
  const [pcapLinks, setPcapLinks] = useState({});

  useEffect(() => {
    fetch(`${apiUrl}/api/attack/status`)
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error("Error fetching status:", err));
  }, [apiUrl]);

  const toggleAttack = async (type) => {
    const isRunning = status[type];
    const endpoint = isRunning ? '/api/attack/stop' : '/api/attack/start';
    const ipToUse = type === 'dos' ? espIp : targetIp;
    
    try {
      const res = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, targetIp: ipToUse })
      });
      
      const data = await res.json();
      if (res.ok) {
        setStatus(prev => ({ ...prev, [type]: !isRunning }));
        if (!isRunning && data.pcap) {
            setPcapLinks(prev => ({ ...prev, [type]: data.pcap }));
        }
      }
    } catch (err) {
      console.error(`Error toggling ${type}:`, err);
    }
  };

  const controls = [
    { id: 'normal', label: 'Normal Traffic', icon: Activity, color: 'text-emerald-400', bg: 'bg-emerald-500/20', hover: 'hover:bg-emerald-500/30' },
    { id: 'bruteforce', label: 'Brute Force', icon: ShieldAlert, color: 'text-orange-400', bg: 'bg-orange-500/20', hover: 'hover:bg-orange-500/30' },
    { id: 'dos', label: 'Volumetric DoS', icon: Wifi, color: 'text-red-400', bg: 'bg-red-500/20', hover: 'hover:bg-red-500/30' },
    { id: 'replay', label: 'Replay Attack', icon: Shield, color: 'text-purple-400', bg: 'bg-purple-500/20', hover: 'hover:bg-purple-500/30' }
  ];

  return (
    <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-slate-200">Simulation Controls</h2>
        <div className="flex space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-xs text-slate-400">Broker IP:</label>
            <input type="text" value={targetIp} onChange={e => setTargetIp(e.target.value)} className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-cyan-300 w-32 focus:outline-none focus:border-cyan-500" />
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-xs text-slate-400">ESP32 IP (DoS):</label>
            <input type="text" value={espIp} onChange={e => setEspIp(e.target.value)} className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-rose-300 w-32 focus:outline-none focus:border-rose-500" />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
        {controls.map(({ id, label, icon: Icon, color, bg, hover }) => {
          const isActive = status[id];
          return (
            <div key={id} className="relative group flex flex-col">
              <button
                onClick={() => toggleAttack(id)}
                className={clsx(
                  "flex-1 flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all duration-200",
                  isActive ? `border-${color.split('-')[1]}-500 shadow-[0_0_15px_rgba(0,0,0,0.5)] ${bg}` : "border-slate-700 bg-slate-900 hover:border-slate-500"
                )}
              >
                <Icon size={28} className={clsx("mb-2", isActive ? color : "text-slate-400")} />
                <span className={clsx("font-semibold text-sm", isActive ? "text-white" : "text-slate-400")}>
                  {label}
                </span>
                <span className={clsx("text-[10px] mt-1 px-2 py-0.5 rounded-full font-bold tracking-wider", isActive ? "bg-red-500/20 text-red-300" : "bg-slate-800 text-slate-500")}>
                  {isActive ? 'ACTIVE' : 'IDLE'}
                </span>
              </button>
              
              {/* PCAP Download Button - Appears if a PCAP is available for this attack */}
              {pcapLinks[id] && (
                <a 
                  href={pcapLinks[id]} 
                  download 
                  className="absolute top-2 right-2 bg-slate-800/80 hover:bg-cyan-500/20 border border-slate-600 hover:border-cyan-500 text-xs text-slate-300 hover:text-cyan-300 px-2 py-1 rounded transition-colors"
                  title="Download Session PCAP"
                >
                  PCAP
                </a>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AttackControls;

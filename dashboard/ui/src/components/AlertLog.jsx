import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';
import clsx from 'clsx';

const AlertLog = ({ alerts }) => {
  return (
    <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 h-full flex flex-col min-h-[300px]">
      <h2 className="text-xl font-bold mb-4 text-rose-400 flex items-center">
        <ShieldAlert className="mr-2" /> IPS Intervention Log
      </h2>
      <div className="flex-1 overflow-y-auto pr-2 space-y-3">
        {alerts.length === 0 ? (
          <div className="text-slate-500 flex flex-col items-center justify-center h-full">
            <Info size={32} className="mb-2 opacity-50" />
            <p>No threats detected yet.</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div 
              key={index} 
              className={clsx(
                "p-3 rounded-lg border-l-4 animate-in fade-in slide-in-from-bottom-2",
                "bg-slate-900 border-rose-500 shadow-[0_0_10px_rgba(225,29,72,0.1)]"
              )}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-rose-400">{alert.reason}</span>
                <span className="text-xs text-slate-400">{new Date(alert.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="text-sm text-slate-300">
                Blocked IP: <span className="font-mono text-cyan-300">{alert.ip}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertLog;

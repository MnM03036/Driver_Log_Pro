import React from "react";
import { Compass, Clock, RefreshCw, CheckCircle, Info, ShieldCheck } from "lucide-react";

export default function SummaryCards({ simulationData }) {
  const { total_miles, daily_logs, markers } = simulationData;
  const numDays = daily_logs.length;
  
  // Extract summary stats from markers
  const breakStops = markers.filter(m => m.type === "break").length;
  const resetStops = markers.filter(m => m.type === "rest").length;
  const restartStops = markers.filter(m => m.type === "restart").length;
  const fuelStops = markers.filter(m => m.type === "fuel").length;

  // Compute total travel duration
  const startLog = daily_logs[0]?.events[0]?.start_time || "00:00";
  const finalLog = daily_logs[numDays - 1]?.events[daily_logs[numDays - 1].events.length - 1]?.end_time || "24:00";
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Distance Card */}
      <div className="glass p-5 rounded-2xl glow-sky flex items-start gap-4">
        <div className="p-3 bg-sky-500/10 rounded-xl border border-sky-500/20 text-sky-400">
          <Compass className="w-6 h-6" />
        </div>
        <div>
          <span className="block text-xs font-semibold text-slate-400">Total Distance</span>
          <span className="text-2xl font-black text-white">{total_miles.toLocaleString()} mi</span>
          <span className="block text-[10px] text-slate-500 mt-1">Via OSRM Highway Route</span>
        </div>
      </div>

      {/* Duration Card */}
      <div className="glass p-5 rounded-2xl glow-sky flex items-start gap-4">
        <div className="p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
          <Clock className="w-6 h-6" />
        </div>
        <div>
          <span className="block text-xs font-semibold text-slate-400">Log Duration</span>
          <span className="text-2xl font-black text-white">{numDays} Daily Sheets</span>
          <span className="block text-[10px] text-indigo-400 font-semibold mt-1">Complete 24h Segments</span>
        </div>
      </div>

      {/* HOS Compliance Resets */}
      <div className="glass p-5 rounded-2xl glow-sky flex items-start gap-4">
        <div className="p-3 bg-purple-500/10 rounded-xl border border-purple-500/20 text-purple-400">
          <RefreshCw className="w-6 h-6" />
        </div>
        <div>
          <span className="block text-xs font-semibold text-slate-400">HOS Duty Cycles</span>
          <div className="flex gap-3 mt-1">
            <div>
              <span className="block text-xs font-bold text-purple-300">{resetStops}</span>
              <span className="text-[9px] text-slate-500">10h Resets</span>
            </div>
            <div className="border-l border-slate-800 h-6"></div>
            <div>
              <span className="block text-xs font-bold text-amber-300">{breakStops}</span>
              <span className="text-[9px] text-slate-500">30m Breaks</span>
            </div>
            <div className="border-l border-slate-800 h-6"></div>
            <div>
              <span className="block text-xs font-bold text-indigo-300">{restartStops}</span>
              <span className="text-[9px] text-slate-500">34h Restarts</span>
            </div>
          </div>
        </div>
      </div>

      {/* Verification Status */}
      <div className="glass p-5 rounded-2xl glow-emerald flex items-start gap-4">
        <div className="p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
          <ShieldCheck className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <span className="block text-xs font-semibold text-slate-400">HOS Status</span>
          <span className="text-lg font-black text-emerald-400 flex items-center gap-1.5 mt-0.5">
            <CheckCircle className="w-4 h-4" /> Compliant
          </span>
          <span className="block text-[10px] text-slate-400 mt-1 flex items-center gap-1">
            <Info className="w-3 h-3 text-slate-500" /> Fuel stops made: {fuelStops}
          </span>
        </div>
      </div>
    </div>
  );
}

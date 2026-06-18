import React, { useState } from "react";
import { Navigation, Truck, MapPin, ShieldAlert, FileText, User, Clipboard } from "lucide-react";

export default function SimulationForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    current_location: "New York, NY",
    pickup_location: "Chicago, IL",
    dropoff_location: "Los Angeles, CA",
    cycle_hours_used: 35.0,
    driver_name: "James 'Logan' Carter",
    carrier_name: "Roadrunner Freight Lines LLC",
    vehicle_num: "TRK-5520-X",
    doc_num: "BOL-990812A",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "cycle_hours_used" ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Locations Card */}
      <div className="glass p-5 rounded-2xl glow-sky space-y-4">
        <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <Navigation className="w-4 h-4 text-sky-400" /> Route Parameters
        </h3>
        
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Start Location</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="current_location"
                value={formData.current_location}
                onChange={handleChange}
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition"
                placeholder="e.g. New York, NY"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Pickup Location</label>
            <div className="relative">
              <Truck className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="pickup_location"
                value={formData.pickup_location}
                onChange={handleChange}
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition"
                placeholder="e.g. Chicago, IL"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Drop-off Location</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="dropoff_location"
                value={formData.dropoff_location}
                onChange={handleChange}
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition"
                placeholder="e.g. Los Angeles, CA"
              />
            </div>
          </div>
        </div>
      </div>

      {/* HOS Cycle Slider */}
      <div className="glass p-5 rounded-2xl glow-sky space-y-4">
        <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400" /> Active HOS Cycle
        </h3>

        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-xs font-semibold text-slate-400">Hours Used (70hr/8day)</label>
            <span className="text-sm font-bold text-sky-400">{formData.cycle_hours_used} hours</span>
          </div>
          <input
            type="range"
            name="cycle_hours_used"
            min="0"
            max="70"
            step="0.5"
            value={formData.cycle_hours_used}
            onChange={handleChange}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>0.0h (Fresh Restart)</span>
            <span>70.0h (Limit)</span>
          </div>
        </div>
      </div>

      {/* ELD Log Headers metadata */}
      <div className="glass p-5 rounded-2xl glow-sky space-y-4">
        <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <FileText className="w-4 h-4 text-emerald-400" /> ELD Document Meta
        </h3>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 mb-0.5">Driver Name</label>
            <div className="relative">
              <User className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500" />
              <input
                type="text"
                name="driver_name"
                value={formData.driver_name}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-2 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-400 mb-0.5">Carrier</label>
            <div className="relative">
              <Clipboard className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500" />
              <input
                type="text"
                name="carrier_name"
                value={formData.carrier_name}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-2 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-400 mb-0.5">Truck / Vehicle</label>
            <input
              type="text"
              name="vehicle_num"
              value={formData.vehicle_num}
              onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-400 mb-0.5">BOL/Shipping Doc</label>
            <input
              type="text"
              name="doc_num"
              value={formData.doc_num}
              onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-sky-500 to-brand-600 hover:from-sky-400 hover:to-brand-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg transition duration-200 transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 text-sm"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5.5 w-5.5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Running Chronological HOS Simulation...
          </>
        ) : (
          "Run Simulation & Generate Logs"
        )}
      </button>
    </form>
  );
}

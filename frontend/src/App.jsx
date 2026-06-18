import React, { useState, Component } from "react";
import SimulationForm from "./components/SimulationForm";
import RouteMap from "./components/Map";
import LogGrid from "./components/LogGrid";
import SummaryCards from "./components/SummaryCards";
import { Truck, MapPin, AlertCircle, FileText, ChevronLeft, ChevronRight, Navigation2, ShieldAlert } from "lucide-react";

// ─── Error Boundary ─────────────────────────────────────────────────────────
// Catches any rendering crashes inside the results panel and shows a friendly
// error message instead of a completely blank screen.
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: "" };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, errorMessage: error?.message || "Unknown render error" };
  }

  componentDidCatch(error, info) {
    console.error("[ErrorBoundary] Render crash:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 flex items-start gap-4">
          <AlertCircle className="w-7 h-7 text-red-500 shrink-0 mt-0.5" />
          <div>
            <h3 className="font-bold text-red-400 text-sm">Display Error</h3>
            <p className="text-xs text-red-300/80 mt-1 leading-relaxed">
              A component crashed while rendering the simulation results.
            </p>
            <pre className="mt-3 text-[10px] text-red-400 bg-red-950/30 p-3 rounded border border-red-500/10 font-mono overflow-auto max-h-40 whitespace-pre-wrap">
              {this.state.errorMessage}
            </pre>
            <button
              onClick={() => this.setState({ hasError: false, errorMessage: "" })}
              className="mt-3 text-xs text-red-400 underline hover:text-red-300"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [simulationData, setSimulationData] = useState(null);
  const [error, setError] = useState(null);
  
  // Selection states
  const [selectedDayIdx, setSelectedDayIdx] = useState(0);
  const [driverMeta, setDriverMeta] = useState({
    driver_name: "",
    carrier_name: "",
    vehicle_num: "",
    doc_num: "",
  });
  const [tripParams, setTripParams] = useState(null);

  // Quick demos list
  const demoRoutes = [
    {
      name: "⚡ Coast to Coast (NY ➔ LA)",
      current: "New York, NY",
      pickup: "Chicago, IL",
      dropoff: "Los Angeles, CA",
      hours: 45.0,
      desc: "2,800+ miles. Stress-tests 34h restarts, multiple 10h sleeper resets, 30m breaks, and 1,000-mile fueling rules."
    },
    {
      name: "🚛 Midwest Run (Chicago ➔ Dallas)",
      current: "Chicago, IL",
      pickup: "St. Louis, MO",
      dropoff: "Dallas, TX",
      hours: 15.0,
      desc: "950+ miles. Triggers a 30m driving break and a 10h sleeper reset mid-route."
    },
    {
      name: "🚀 Regional Haul (Houston ➔ Dallas)",
      current: "Houston, TX",
      pickup: "Houston, TX",
      dropoff: "Dallas, TX",
      hours: 0.0,
      desc: "240 miles. Short, clean trip. Fits entirely within a single day's 14h duty window."
    }
  ];

  // Submit trigger
  const runSimulation = async (formData) => {
    setIsLoading(true);
    setError(null);
    setSelectedDayIdx(0);
    
    // Save metadata for canvas drawing
    setDriverMeta({
      driver_name: formData.driver_name,
      carrier_name: formData.carrier_name,
      vehicle_num: formData.vehicle_num,
      doc_num: formData.doc_num,
    });
    
    // Save params for SVG downloads
    setTripParams({
      current_location: formData.current_location,
      pickup_location: formData.pickup_location,
      dropoff_location: formData.dropoff_location,
      cycle_hours_used: formData.cycle_hours_used,
    });

    try {
      // Dynamically use Render backend URL if provided via VITE_API_URL, fallback to relative path
      const apiUrl = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/simulate` 
        : "/api/simulate";

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_location: formData.current_location,
          pickup_location: formData.pickup_location,
          dropoff_location: formData.dropoff_location,
          cycle_hours_used: formData.cycle_hours_used,
        }),
      });

      if (!response.ok) {
        const errorJson = await response.json().catch(() => ({}));
        throw new Error(errorJson.error || `Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      if (!data || !data.daily_logs || !data.markers) {
        throw new Error("Invalid response from server: missing daily_logs or markers.");
      }
      setSimulationData(data);
    } catch (err) {
      console.error(err);
      setSimulationData(null);
      setError(err.message || "Failed to connect to the API. Check the Vercel function logs.");
    } finally {
      setIsLoading(false);
    }
  };

  const loadDemo = (demo) => {
    // Fill values and run simulation
    runSimulation({
      current_location: demo.current,
      pickup_location: demo.pickup,
      dropoff_location: demo.dropoff,
      cycle_hours_used: demo.hours,
      driver_name: "James 'Logan' Carter",
      carrier_name: "Roadrunner Freight Lines LLC",
      vehicle_num: "TRK-5520-X",
      doc_num: "BOL-990812A",
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="glass border-b border-slate-900 sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-sky-500/10 p-2 rounded-xl border border-sky-500/20 text-sky-400">
            <Truck className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tight text-white flex items-center gap-2">
              APEX LOGISTICS HOS SIMULATOR
              <span className="text-[10px] bg-sky-500/20 text-sky-400 px-2 py-0.5 rounded-full font-bold">ELD COMPLIANCE</span>
            </h1>
            <p className="text-[10px] text-slate-400">FMCSA Hours of Service Chronological Rules Engine</p>
          </div>
        </div>
        <div className="text-right hidden md:block">
          <span className="block text-xs font-semibold text-slate-400">Current Session</span>
          <span className="text-[11px] text-slate-500 font-mono">Jun 18, 2026 UTC</span>
        </div>
      </header>

      {/* Main Dashboard Layout */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column - Inputs (4 spans) */}
        <div className="lg:col-span-4 space-y-6">
          <SimulationForm onSubmit={runSimulation} isLoading={isLoading} />
          
          {/* Quick Demo Selector */}
          <div className="glass p-5 rounded-2xl glow-sky">
            <h3 className="text-xs font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2 mb-4">
              <Navigation2 className="w-4 h-4 text-sky-400" /> Presets &amp; HOS Test Cases
            </h3>
            <div className="space-y-3">
              {demoRoutes.map((demo, idx) => (
                <button
                  key={idx}
                  onClick={() => loadDemo(demo)}
                  disabled={isLoading}
                  className="w-full text-left bg-slate-900/40 hover:bg-slate-900 border border-slate-800 hover:border-slate-700/80 p-3 rounded-xl transition duration-200 group text-xs space-y-1"
                >
                  <div className="font-bold text-slate-200 group-hover:text-sky-400 transition-colors">
                    {demo.name}
                  </div>
                  <div className="text-slate-400 text-[10px] leading-relaxed">
                    {demo.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Map and Logs (8 spans) */}
        <div className="lg:col-span-8 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5 flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-red-500 shrink-0" />
              <div>
                <h3 className="font-bold text-red-400 text-sm">Simulation Failure</h3>
                <p className="text-xs text-red-300/80 mt-1 leading-relaxed">{error}</p>
                <div className="mt-3 text-[10px] text-red-500 bg-red-950/20 p-2 rounded border border-red-500/10 font-mono">
                  Check the Vercel function logs for details: Vercel Dashboard → Project → Functions
                </div>
              </div>
            </div>
          )}

          {!simulationData && !error && !isLoading ? (
            /* Intro Hero State */
            <div className="glass p-12 rounded-3xl glow-sky flex flex-col items-center text-center justify-center min-h-[450px] space-y-6">
              <div className="p-4 bg-sky-500/5 rounded-full border border-sky-500/15 text-sky-400">
                <Truck className="w-12 h-12" />
              </div>
              <div className="max-w-md space-y-2">
                <h2 className="text-2xl font-black text-white">Chronological HOS Analyzer</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Enter addresses to run a simulated logistics journey. The engine plots the OSRM route, evaluates FMCSA limits, injects resets, and prints daily driver logs automatically.
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-4 max-w-sm text-left">
                <div className="p-3 bg-slate-900/30 rounded-xl border border-slate-800/60">
                  <span className="block text-xs font-bold text-slate-300">Rules Integrated:</span>
                  <span className="block text-[10px] text-slate-500 mt-1">11h Driving, 14h Window, 30m Breaks, 70h/8d cycle restart.</span>
                </div>
                <div className="p-3 bg-slate-900/30 rounded-xl border border-slate-800/60">
                  <span className="block text-xs font-bold text-slate-300">Outputs Rendered:</span>
                  <span className="block text-[10px] text-slate-500 mt-1">Leaflet Route, compliance stops, SVG sheets, and Canvas editor.</span>
                </div>
              </div>
              <div className="text-[11px] text-sky-400 font-bold bg-sky-950/30 px-4 py-1.5 rounded-full border border-sky-500/20">
                💡 Tip: Click one of the Presets on the left to run a simulation instantly!
              </div>
            </div>
          ) : isLoading ? (
            /* Loading State */
            <div className="glass p-12 rounded-3xl glow-sky flex flex-col items-center text-center justify-center min-h-[450px] space-y-6">
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-sky-500/20 border-t-sky-400 animate-spin"></div>
                <Truck className="w-6 h-6 text-sky-400 absolute inset-0 m-auto animate-pulse" />
              </div>
              <div className="space-y-2">
                <h3 className="font-bold text-white text-lg">Computing Dispatch Log...</h3>
                <p className="text-slate-400 text-xs">Geocoding addresses &amp; calculating optimal routing paths...</p>
              </div>
              <div className="text-[10px] font-mono text-slate-500 max-w-xs leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-900">
                Fetching path coordinates via Open Source Routing Machine (OSRM)...
              </div>
            </div>
          ) : simulationData ? (
            /* Main Outputs Render (Map, KPIs, Logs) — wrapped in ErrorBoundary */
            <ErrorBoundary>
              <div className="space-y-6">
                {/* KPIs Header */}
                <SummaryCards simulationData={simulationData} />

                {/* Map & Stop Listing Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Map (2 spans) */}
                  <div className="lg:col-span-2 h-[380px]">
                    <RouteMap
                      routeCoords={simulationData.route_coordinates}
                      markers={simulationData.markers}
                    />
                  </div>

                  {/* Markers & Stops list (1 span) */}
                  <div className="lg:col-span-1 glass p-4 rounded-2xl glow-sky flex flex-col h-[380px] overflow-hidden">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-purple-400" /> Chronological Stops
                    </h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                      {simulationData.markers.map((marker, idx) => {
                        const typeColors = {
                          start: "text-sky-400 border-sky-500/20 bg-sky-500/5",
                          pickup: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5",
                          dropoff: "text-rose-400 border-rose-500/20 bg-rose-500/5",
                          rest: "text-purple-400 border-purple-500/20 bg-purple-500/5",
                          break: "text-amber-400 border-amber-500/20 bg-amber-500/5",
                          fuel: "text-cyan-400 border-cyan-500/20 bg-cyan-500/5",
                          restart: "text-indigo-400 border-indigo-500/20 bg-indigo-500/5",
                        };

                        const timeStr = marker.time
                          ? new Date(marker.time).toLocaleTimeString("en-US", {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "Start";

                        return (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-xl border flex gap-3 text-xs ${
                              typeColors[marker.type] || "text-slate-400 border-slate-800"
                            }`}
                          >
                            <div className="font-bold font-mono py-0.5">{timeStr}</div>
                            <div>
                              <div className="font-bold text-[11px] uppercase">{marker.label}</div>
                              <div className="text-[10px] opacity-80 mt-0.5 leading-relaxed">{marker.description}</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* daily ELD Logs Carousel Section */}
                <div className="glass p-5 rounded-2xl glow-sky space-y-5">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-900 pb-4">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-sky-400" />
                      <div>
                        <h3 className="text-sm font-bold tracking-tight text-white uppercase">Daily Logs</h3>
                        <p className="text-[10px] text-slate-400">Select day sheet to view and export</p>
                      </div>
                    </div>

                    {/* Day Navigation Controls (Carousel Tabs) */}
                    <div className="flex items-center gap-2 bg-slate-900/60 p-1 rounded-xl border border-slate-800/40">
                      <button
                        onClick={() => setSelectedDayIdx(prev => Math.max(0, prev - 1))}
                        disabled={selectedDayIdx === 0}
                        className="p-1 rounded bg-slate-900 border border-slate-800 text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 transition"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      
                      <div className="flex gap-1">
                        {simulationData.daily_logs.map((log, idx) => (
                          <button
                            key={idx}
                            onClick={() => setSelectedDayIdx(idx)}
                            className={`px-3 py-1 rounded text-xs font-bold transition ${
                              selectedDayIdx === idx
                                ? "bg-sky-500 text-white shadow"
                                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                            }`}
                          >
                            Day {log.day_number}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={() => setSelectedDayIdx(prev => Math.min(simulationData.daily_logs.length - 1, prev + 1))}
                        disabled={selectedDayIdx === simulationData.daily_logs.length - 1}
                        className="p-1 rounded bg-slate-900 border border-slate-800 text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 transition"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Canvas grid rendering */}
                  <LogGrid
                    dayLog={simulationData.daily_logs[selectedDayIdx]}
                    driverName={driverMeta.driver_name || "James Carter"}
                    carrierName={driverMeta.carrier_name || "Roadrunner Freight LLC"}
                    vehicleNum={driverMeta.vehicle_num || "TRK-5520"}
                    docNum={driverMeta.doc_num || "BOL-9908"}
                    tripParams={tripParams}
                  />
                </div>
              </div>
            </ErrorBoundary>
          ) : null}
        </div>
      </main>

      {/* Footer */}
      <footer className="glass border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>&copy; 2026 HOS Simulator &amp; ELD Generator. Apex Fleet Management Systems.</p>
        <p className="mt-1 font-mono text-[10px] text-slate-600">Built using Django, React-Leaflet, and Tailwind CSS. Compliant with 49 CFR Part 395.</p>
      </footer>
    </div>
  );
}

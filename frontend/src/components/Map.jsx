import React, { useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { Calendar, Clock, MapPin, Fuel, Coffee, RotateCcw, AlertTriangle } from "lucide-react";

// Inline custom SVG marker generator to prevent Leaflet asset resolution bugs
const getSvgIcon = (color) => {
  return L.divIcon({
    html: `
      <div class="relative flex items-center justify-center">
        <!-- Pulse ring for key terminals -->
        ${["#10b981", "#f43f5e"].includes(color) ? `<div class="absolute w-6 h-6 rounded-full bg-[${color}] opacity-25 animate-ping"></div>` : ""}
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" fill="${color}" stroke="#0f172a" stroke-width="1.5"/>
          <circle cx="12" cy="9" r="3.5" fill="#ffffff"/>
        </svg>
      </div>
    `,
    className: "custom-leaflet-marker",
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  });
};

// Colors mapping for marker types
const markerColors = {
  start: "#38bdf8",     // Sky Blue
  pickup: "#10b981",    // Emerald Green
  dropoff: "#f43f5e",   // Rose Red
  rest: "#a855f7",      // Purple (10h sleep)
  break: "#f59e0b",     // Amber (30m break)
  fuel: "#06b6d4",      // Cyan (fuel stop)
  restart: "#6366f1"    // Indigo (34h restart)
};

// Icon components for popup rendering
const getMarkerIconComponent = (type) => {
  const cls = "w-4 h-4 mr-1.5";
  switch (type) {
    case "start": return <MapPin className={`${cls} text-sky-400`} />;
    case "pickup": return <MapPin className={`${cls} text-emerald-400`} />;
    case "dropoff": return <MapPin className={`${cls} text-rose-400`} />;
    case "fuel": return <Fuel className={`${cls} text-cyan-400`} />;
    case "break": return <Coffee className={`${cls} text-amber-400`} />;
    case "rest": return <AlertTriangle className={`${cls} text-purple-400`} />;
    case "restart": return <RotateCcw className={`${cls} text-indigo-400`} />;
    default: return <MapPin className={`${cls} text-slate-400`} />;
  }
};

// Component to handle auto-panning and fitting map bounds
function ChangeView({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [bounds, map]);
  return null;
}

export default function RouteMap({ routeCoords, markers }) {
  // Guard: routeCoords may be null/undefined if OSRM call failed
  const safeCoords = Array.isArray(routeCoords) ? routeCoords : [];

  // Convert OSRM GeoJSON format [lon, lat] to Leaflet [lat, lon]
  const leafletCoords = safeCoords
    .filter((c) => Array.isArray(c) && c.length >= 2)
    .map((coord) => [Number(coord[1]), Number(coord[0])]);

  // Guard: markers may be null/undefined
  const safeMarkers = Array.isArray(markers) ? markers : [];

  // Build bounds to auto-fit
  const bounds = leafletCoords.length > 0 ? leafletCoords : [[39.8283, -98.5795]]; // Center of USA default

  // Formatter for markers dates/times
  const formatTime = (isoString) => {
    if (!isoString) return "Pending Arrival";
    try {
      const date = new Date(isoString);
      return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return "N/A";
    }
  };

  return (
    <div className="w-full h-full relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl">
      <MapContainer
        center={[39.8283, -98.5795]}
        zoom={4}
        style={{ width: "100%", height: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <ChangeView bounds={bounds} />

        {/* Plot Route Line */}
        {leafletCoords.length > 0 && (
          <Polyline
            positions={leafletCoords}
            color="#0ea5e9"
            weight={4.5}
            opacity={0.85}
            lineJoin="round"
          />
        )}

        {/* Plot Stop & Break Markers */}
        {safeMarkers.map((marker, idx) => {
          // Coerce to numbers — backend may return strings
          const lat = Number(marker.lat);
          const lon = Number(marker.lon);
          if (isNaN(lat) || isNaN(lon)) return null; // skip invalid markers
          const color = markerColors[marker.type] || "#64748b";
          const position = [lat, lon];
          
          return (
            <Marker
              key={idx}
              position={position}
              icon={getSvgIcon(color)}
            >
              <Popup>
                <div className="p-1 min-w-[200px] text-slate-100 bg-slate-950 font-sans">
                  <div className="flex items-center font-bold text-sm text-white border-b border-slate-800 pb-1.5 mb-1.5 uppercase tracking-wide">
                    {getMarkerIconComponent(marker.type)}
                    {marker.label}
                  </div>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center text-slate-400">
                      <Clock className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
                      <span>{formatTime(marker.time)}</span>
                    </div>
                    <div className="text-slate-300 font-medium leading-relaxed bg-slate-900/60 p-1.5 rounded border border-slate-800/40">
                      {marker.description}
                    </div>
                    <div className="text-[10px] text-slate-500 flex justify-between">
                      <span>Lat: {marker.lat.toFixed(4)}</span>
                      <span>Lon: {marker.lon.toFixed(4)}</span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

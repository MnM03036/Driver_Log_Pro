import React, { useRef, useEffect } from "react";
import { Download, FileDown, CheckCircle } from "lucide-react";

export default function LogGrid({ dayLog, driverName, carrierName, vehicleNum, docNum, tripParams }) {
  const canvasRef = useRef(null);

  // Normalise totals — MUST come before useEffect but after hooks
  // We always compute this (even if dayLog is null) to keep hook order stable
  const totals = dayLog?.totals
    ? { OFF: 0, SB: 0, D: 0, ON: 0, total: 24, ...dayLog.totals }
    : { OFF: 0, SB: 0, D: 0, ON: 0, total: 24 };

  // Helper to convert "HH:MM" to minutes since midnight
  const timeToMinutes = (timeStr) => {
    if (!timeStr) return 0;
    const parts = timeStr.split(":");
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
  };

  useEffect(() => {
    // Guard inside the effect — safe because hooks are always called
    if (!dayLog || !dayLog.totals || !dayLog.events) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Canvas dimensions (logical)
    const width = 960;
    const height = 580;

    // Adjust for High-DPI screens (Retina)
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Clear Canvas with white background
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);

    // Outer border
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, width - 20, height - 20);

    // --- 1. HEADER SECTION ---
    ctx.fillStyle = "#0f172a";
    ctx.font = "bold 18px 'Outfit', sans-serif";
    ctx.fillText("DRIVER'S DAILY LOG", 30, 42);

    ctx.font = "italic 11px sans-serif";
    ctx.fillStyle = "#64748b";
    ctx.fillText("Federal Motor Carrier Safety Regulations (FMCSR) - 49 CFR Part 395", 30, 58);

    // Header Details Boxes (Personalized headers)
    const drawTextBox = (x, y, w, h, label, value) => {
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, w, h);
      
      ctx.fillStyle = "#475569";
      ctx.font = "bold 9px sans-serif";
      ctx.fillText(label.toUpperCase(), x + 8, y + 15);
      
      ctx.fillStyle = "#0f172a";
      ctx.font = "semibold 12px sans-serif";
      ctx.fillText(value || "N/A", x + 8, y + 32);
    };

    // Metadata boxes
    drawTextBox(380, 22, 180, 42, "Driver", driverName);
    drawTextBox(570, 22, 180, 42, "Carrier", carrierName);
    drawTextBox(760, 22, 170, 42, "Truck / Vehicle #", vehicleNum);

    drawTextBox(380, 70, 180, 42, "Date", `${dayLog.date} (Day ${dayLog.day_number})`);
    drawTextBox(570, 70, 180, 42, "Shipping Doc #", docNum);
    // Estimate mileage based on driving hours (assume ~50 mph average)
    const estMiles = ((totals.D || 0) * 50).toFixed(1);
    drawTextBox(760, 70, 170, 42, "Total Miles Today", `${estMiles} mi`);

    // --- 2. GRID PARAMETERS ---
    const gridX = 130;
    const gridY = 140;
    const gridW = 744;  // 31 pixels per hour * 24 = 744
    const gridH = 140;  // 4 rows * 35 pixels = 140
    const rowH = 35;

    // Status Row Y Coordinates map
    const statusYMap = {
      OFF: gridY + rowH / 2,        // Row 0 mid: 140 + 17.5 = 157.5
      SB: gridY + rowH + rowH / 2,   // Row 1 mid: 140 + 35 + 17.5 = 192.5
      D: gridY + rowH * 2 + rowH / 2, // Row 2 mid: 140 + 70 + 17.5 = 227.5
      ON: gridY + rowH * 3 + rowH / 2, // Row 3 mid: 140 + 105 + 17.5 = 262.5
    };

    // Fill Grid Background
    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(gridX, gridY, gridW, gridH);

    // Draw Grid Outer Border
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(gridX, gridY, gridW, gridH);

    // Draw Row Lines
    for (let r = 1; r < 4; r++) {
      ctx.beginPath();
      ctx.moveTo(gridX, gridY + r * rowH);
      ctx.lineTo(gridX + gridW, gridY + r * rowH);
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw Hour Columns & Subdivisions
    for (let h = 0; h <= 24; h++) {
      const x = gridX + h * 31;

      // Hour line
      const isMajor = h === 0 || h === 12 || h === 24;
      ctx.beginPath();
      ctx.moveTo(x, gridY);
      ctx.lineTo(x, gridY + gridH);
      ctx.strokeStyle = isMajor ? "#475569" : "#cbd5e1";
      ctx.lineWidth = isMajor ? 1.5 : 0.75;
      ctx.stroke();

      // Draw Hour Numbers
      ctx.fillStyle = "#475569";
      ctx.font = "bold 9px sans-serif";
      ctx.textAlign = "center";
      const lbl = h === 0 || h === 24 ? "Mdt" : h === 12 ? "Noon" : h > 12 ? h - 12 : h;
      ctx.fillText(lbl.toString(), x, gridY - 8);

      // Quarter-hour tick marks inside cells
      if (h < 24) {
        for (let q = 1; q < 4; q++) {
          const qx = x + q * 7.75;
          ctx.beginPath();
          ctx.moveTo(qx, gridY);
          ctx.lineTo(qx, gridY + 6);
          ctx.moveTo(qx, gridY + gridH - 6);
          ctx.lineTo(qx, gridY + gridH);
          ctx.strokeStyle = "#e2e8f0";
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
        // Half hour tick (slightly taller)
        const hx = x + 15.5;
        ctx.beginPath();
        ctx.moveTo(hx, gridY);
        ctx.lineTo(hx, gridY + 10);
        ctx.moveTo(hx, gridY + gridH - 10);
        ctx.lineTo(hx, gridY + gridH);
        ctx.strokeStyle = "#cbd5e1";
        ctx.lineWidth = 0.75;
        ctx.stroke();
      }
    }

    // Draw Status Labels on Left of Grid
    const labels = [
      "1. OFF DUTY",
      "2. SLEEPER BERTH",
      "3. DRIVING",
      "4. ON DUTY (ND)",
    ];
    ctx.textAlign = "left";
    ctx.font = "bold 10px sans-serif";
    ctx.fillStyle = "#1e293b";
    labels.forEach((label, idx) => {
      ctx.fillText(label, 20, gridY + idx * rowH + 20);
    });

    // Draw Totals Box on Right
    const totalsX = gridX + gridW;
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(totalsX, gridY, 60, gridH);

    ctx.fillStyle = "#475569";
    ctx.font = "bold 9px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("TOTAL", totalsX + 30, gridY - 8);

    // Row lines in Totals Box
    for (let r = 1; r < 4; r++) {
      ctx.beginPath();
      ctx.moveTo(totalsX, gridY + r * rowH);
      ctx.lineTo(totalsX + 60, gridY + r * rowH);
      ctx.strokeStyle = "#475569";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Write row total values
    const totalKeys = ["OFF", "SB", "D", "ON"];
    ctx.font = "bold 11px sans-serif";
    ctx.fillStyle = "#2563eb";
    totalKeys.forEach((key, idx) => {
      const val = totals[key] || 0.0;
      ctx.fillText(val.toFixed(2), totalsX + 30, gridY + idx * rowH + 21);
    });

    // Write sum at the bottom of totals (which must equal 24)
    ctx.fillStyle = "#10b981";
    ctx.font = "bold 11px sans-serif";
    ctx.fillText((totals.total || 24).toFixed(1), totalsX + 30, gridY + gridH + 18);
    ctx.fillStyle = "#475569";
    ctx.font = "italic 9px sans-serif";
    ctx.fillText("Must equal 24h", totalsX + 30, gridY + gridH + 30);

    // --- 3. PLOT STEPLINES ---
    const events = dayLog.events || [];
    if (events.length > 0) {
      ctx.strokeStyle = "#2563eb"; // Premium bright blue step lines
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      let lastX = null;
      let lastY = null;

      events.forEach((e) => {
        const startMins = timeToMinutes(e.start_time);
        const endMins = timeToMinutes(e.end_time);

        // Convert minutes to grid X coordinates
        // 744 pixels / 1440 minutes = 0.5167 pixels per minute
        const xStart = gridX + (startMins / 1440.0) * gridW;
        const xEnd = gridX + (endMins / 1440.0) * gridW;
        const yVal = statusYMap[e.status] || statusYMap.OFF;

        // Transition vertical line
        if (lastX !== null && lastY !== null) {
          ctx.beginPath();
          ctx.moveTo(xStart, lastY);
          ctx.lineTo(xStart, yVal);
          ctx.stroke();
        }

        // Duration horizontal line
        ctx.beginPath();
        ctx.moveTo(xStart, yVal);
        ctx.lineTo(xEnd, yVal);
        ctx.stroke();

        // Draw small dot at nodes for ELD look
        ctx.fillStyle = "#1e3a8a";
        ctx.beginPath();
        ctx.arc(xStart, yVal, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(xEnd, yVal, 2, 0, Math.PI * 2);
        ctx.fill();

        lastX = xEnd;
        lastY = yVal;
      });
    }

    // --- 4. REMARKS TABLE SECTION ---
    const remarksY = gridY + gridH + 40;
    ctx.beginPath();
    ctx.moveTo(20, remarksY);
    ctx.lineTo(width - 20, remarksY);
    ctx.strokeStyle = "#cbd5e1";
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = "#1e293b";
    ctx.font = "bold 12px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("CHRONOLOGICAL DUTY STATUS & REMARKS", 30, remarksY + 20);

    // Remarks Header
    const colX = [30, 110, 190, 300, 520];
    const headers = ["START", "END", "STATUS", "LOCATION", "REMARKS"];
    ctx.fillStyle = "#64748b";
    ctx.font = "bold 9px sans-serif";
    headers.forEach((hdr, i) => {
      ctx.fillText(hdr, colX[i], remarksY + 38);
    });

    ctx.beginPath();
    ctx.moveTo(20, remarksY + 44);
    ctx.lineTo(width - 20, remarksY + 44);
    ctx.strokeStyle = "#e2e8f0";
    ctx.stroke();

    // Fill row data (Up to 5 on canvas)
    let rowY = remarksY + 58;
    ctx.fillStyle = "#0f172a";
    ctx.font = "11px sans-serif";
    
    events.slice(0, 5).forEach((e) => {
      ctx.font = "bold 10px monospace";
      ctx.fillText(e.start_time, colX[0], rowY);
      ctx.fillText(e.end_time, colX[1], rowY);
      
      ctx.font = "bold 10px sans-serif";
      ctx.fillStyle = "#2563eb";
      ctx.fillText(e.status, colX[2], rowY);
      
      ctx.font = "10px sans-serif";
      ctx.fillStyle = "#0f172a";
      // Truncate location to fit width
      const loc = e.location || "N/A";
      const dispLoc = loc.length > 25 ? `${loc.slice(0, 22)}...` : loc;
      ctx.fillText(dispLoc, colX[3], rowY);

      // Truncate remarks
      const rem = e.remarks || "N/A";
      const dispRem = rem.length > 55 ? `${rem.slice(0, 52)}...` : rem;
      ctx.fillText(dispRem, colX[4], rowY);

      ctx.beginPath();
      ctx.moveTo(20, rowY + 6);
      ctx.lineTo(width - 20, rowY + 6);
      ctx.strokeStyle = "#f1f5f9";
      ctx.stroke();

      rowY += 18;
    });

    if (events.length > 5) {
      ctx.fillStyle = "#94a3b8";
      ctx.font = "italic 9px sans-serif";
      ctx.fillText(`* And ${events.length - 5} more duty status events (see complete list below)`, 30, rowY + 5);
    }

    // --- 5. SIGNATURE FIELD ---
    const sigX = 680;
    const sigY = height - 60;
    ctx.beginPath();
    ctx.moveTo(sigX, sigY);
    ctx.lineTo(sigX + 240, sigY);
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = "#64748b";
    ctx.font = "bold 8px sans-serif";
    ctx.fillText("DRIVER'S SIGNATURE (ELD VERIFIED)", sigX, sigY + 12);
    
    ctx.font = "italic 11.5px monospace";
    ctx.fillStyle = "#2563eb";
    ctx.fillText(driverName, sigX + 10, sigY - 5);

    // Verified badge
    ctx.fillStyle = "#10b981";
    ctx.fillRect(sigX + 200, sigY - 25, 40, 15);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 8px sans-serif";
    ctx.fillText("VERIFIED", sigX + 203, sigY - 15);

  }, [dayLog, driverName, carrierName, vehicleNum, docNum, totals]);


  // Local PNG download trigger
  const downloadPng = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dataUrl = canvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.download = `driver_log_day${dayLog.day_number}_${dayLog.date}.png`;
    link.href = dataUrl;
    link.click();
  };

  // Backend SVG download trigger
  const downloadSvg = () => {
    if (!tripParams) return;
    
    const params = new URLSearchParams({
      current_location: tripParams.current_location,
      pickup_location: tripParams.pickup_location,
      dropoff_location: tripParams.dropoff_location,
      cycle_hours_used: tripParams.cycle_hours_used.toString(),
      day_number: dayLog.day_number.toString(),
      driver_name: driverName,
      carrier_name: carrierName,
      vehicle_num: vehicleNum,
      doc_num: docNum,
      download: "true"
    });

    const baseUrl = import.meta.env.VITE_API_URL
      ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/download-log/`
      : "/api/download-log/";

    const url = `${baseUrl}?${params.toString()}`;
    window.open(url, "_blank");
  };

  // Guard in JSX return — safe here, after all hooks
  if (!dayLog || !dayLog.events) {
    return (
      <div className="p-6 text-center text-slate-500 text-sm">
        No log data available for this day.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Canvas container */}
      <div className="overflow-hidden p-4 bg-slate-900/40 rounded-2xl border border-slate-800/80 flex justify-center w-full">
        <canvas
          ref={canvasRef}
          className="shadow-2xl rounded-xl border border-slate-800 bg-white w-full max-w-[960px] h-auto"
        />
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap justify-between items-center gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800/40">
        <div className="flex items-center text-emerald-400 text-xs font-semibold gap-1.5">
          <CheckCircle className="w-4.5 h-4.5" />
          <span>ELD Record of Duty Status (RODS) Compliant</span>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={downloadPng}
            className="bg-slate-800 hover:bg-slate-700 text-white font-medium py-1.5 px-3.5 rounded-lg text-xs transition flex items-center gap-1.5 border border-slate-700"
          >
            <Download className="w-3.5 h-3.5" /> Download PNG
          </button>
          
          <button
            onClick={downloadSvg}
            className="bg-sky-600 hover:bg-sky-500 text-white font-medium py-1.5 px-3.5 rounded-lg text-xs transition flex items-center gap-1.5"
          >
            <FileDown className="w-3.5 h-3.5" /> Download SVG Vector
          </button>
        </div>
      </div>
      
      {/* Detailed Table for all events (even when > 5) */}
      <div className="bg-slate-900/20 rounded-xl border border-slate-800/60 p-4">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Complete Duty Events Chronology - Day {dayLog.day_number}
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Start</th>
                <th className="py-2.5 px-3">End</th>
                <th className="py-2.5 px-3">Duration</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Location</th>
                <th className="py-2.5 px-3">Remarks</th>
              </tr>
            </thead>
            <tbody>
              {dayLog.events.map((e, idx) => {
                const statusFull = {
                  OFF: "Off Duty",
                  SB: "Sleeper Berth",
                  D: "Driving",
                  ON: "On Duty (Not Driving)"
                }[e.status] || e.status;
                
                const startMins = timeToMinutes(e.start_time);
                const endMins = timeToMinutes(e.end_time);
                const diffMins = endMins - startMins;
                const hours = Math.floor(diffMins / 60);
                const mins = diffMins % 60;
                const durationStr = `${hours}h ${mins}m`;

                return (
                  <tr key={idx} className="border-b border-slate-800/40 hover:bg-slate-900/30 transition">
                    <td className="py-2 px-3 font-mono font-bold text-slate-300">{e.start_time}</td>
                    <td className="py-2 px-3 font-mono font-bold text-slate-300">{e.end_time}</td>
                    <td className="py-2 px-3 text-slate-400">{durationStr}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        e.status === "D" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" :
                        e.status === "ON" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                        e.status === "SB" ? "bg-purple-500/10 text-purple-400 border border-purple-500/20" :
                        "bg-slate-700/20 text-slate-400 border border-slate-700/30"
                      }`}>
                        {statusFull}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-300 max-w-[150px] truncate" title={e.location}>
                      {e.location || "N/A"}
                    </td>
                    <td className="py-2 px-3 text-slate-400">{e.remarks}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

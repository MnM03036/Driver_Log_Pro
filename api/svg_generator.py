import datetime

def time_to_minutes(time_str):
    """
    Convert "HH:MM" string to minutes since midnight.
    """
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0

def generate_svg_log(day_log, driver_name="John Doe", carrier="Elite Logistics", vehicle_num="TRK-9000", doc_num="DOC-123456"):
    """
    Generate an SVG image representation of a 24-hour daily driver log sheet.
    """
    # SVG parameters
    width = 1000
    height = 650
    
    # Grid coordinates
    grid_x = 130
    grid_y = 120
    grid_w = 768  # 32 pixels per hour (32 * 24 = 768)
    grid_h = 160  # 4 rows * 40 pixels = 160
    
    row_height = 40
    status_y_map = {
        "OFF": grid_y + 20,           # Row 0 midpoint: 140
        "SB": grid_y + 60,            # Row 1 midpoint: 180
        "D": grid_y + 100,            # Row 2 midpoint: 220
        "ON": grid_y + 140            # Row 3 midpoint: 260
    }
    
    date_str = day_log.get("date", str(datetime.date.today()))
    day_num = day_log.get("day_number", 1)
    totals = day_log.get("totals", {"OFF": 24.0, "SB": 0.0, "D": 0.0, "ON": 0.0, "total": 24.0})
    events = day_log.get("events", [])
    
    # Start SVG string
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">')
    
    # Add Styles
    svg.append("""
    <style>
        .title { font-size: 20px; font-weight: 800; fill: #1e293b; }
        .subtitle { font-size: 13px; font-weight: 500; fill: #64748b; }
        .label { font-size: 11px; font-weight: 700; fill: #475569; }
        .value { font-size: 12px; font-weight: 500; fill: #0f172a; }
        .grid-axis { font-size: 10px; font-weight: 600; fill: #475569; text-anchor: middle; }
        .grid-row-lbl { font-size: 11px; font-weight: 700; fill: #1e293b; }
        .total-lbl { font-size: 12px; font-weight: 800; fill: #1e293b; text-anchor: middle; }
        .remark-hdr { font-size: 11px; font-weight: 700; fill: #475569; }
        .remark-row { font-size: 11px; fill: #0f172a; }
    </style>
    """)
    
    # 1. Main Border and Shadow-like border
    svg.append(f'<rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>')
    
    # Header Section
    svg.append(f'<text x="30" y="45" class="title">DRIVER DAILY LOG SHEET</text>')
    svg.append(f'<text x="30" y="62" class="subtitle">FMCSA Hours of Service (HOS) Compliance Log</text>')
    
    # Header Details Boxes
    # Box 1: General Info
    svg.append(f'<rect x="420" y="25" width="260" height="75" rx="4" fill="none" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="430" y="42" class="label">DRIVER:</text><text x="490" y="42" class="value">{driver_name}</text>')
    svg.append(f'<text x="430" y="62" class="label">CARRIER:</text><text x="490" y="62" class="value">{carrier}</text>')
    svg.append(f'<text x="430" y="82" class="label">VEHICLE:</text><text x="490" y="82" class="value">{vehicle_num}</text>')
    
    # Box 2: Log details
    svg.append(f'<rect x="700" y="25" width="270" height="75" rx="4" fill="none" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="710" y="42" class="label">DATE:</text><text x="780" y="42" class="value">{date_str} (Day {day_num})</text>')
    svg.append(f'<text x="710" y="62" class="label">DOC NO:</text><text x="780" y="62" class="value">{doc_num}</text>')
    svg.append(f'<text x="710" y="82" class="label">TOTAL MILES:</text><text x="780" y="82" class="value">{totals.get("D", 0.0) * 50:.1f} mi</text>') # Estimated odometer based on driving
    
    # --- 2. 24-Hour Grid Drawing ---
    # Background for grid
    svg.append(f'<rect x="{grid_x}" y="{grid_y}" width="{grid_w}" height="{grid_h}" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>')
    
    # Row separators
    for r in range(1, 4):
        y = grid_y + r * row_height
        svg.append(f'<line x1="{grid_x}" y1="{y}" x2="{grid_x + grid_w}" y2="{y}" stroke="#cbd5e1" stroke-width="1"/>')
        
    # Vertical grid lines (every 1 hour, half-hour, and quarter-hour)
    for h in range(25):
        x = grid_x + h * 32
        
        # 1-hour line
        is_midnight_or_noon = h in [0, 12, 24]
        stroke_color = "#475569" if is_midnight_or_noon else "#94a3b8"
        stroke_width = "1.5" if is_midnight_or_noon else "1"
        
        if h < 24:
            # Draw quarter hours
            for q in range(1, 4):
                xq = x + q * 8
                svg.append(f'<line x1="{xq}" y1="{grid_y}" x2="{xq}" y2="{grid_y + grid_h}" stroke="#e2e8f0" stroke-dasharray="1 1" stroke-width="0.5"/>')
            # Draw half hour ticks (shorter lines or full dotted)
            xh = x + 16
            svg.append(f'<line x1="{xh}" y1="{grid_y}" x2="{xh}" y2="{grid_y + grid_h}" stroke="#cbd5e1" stroke-dasharray="2 2" stroke-width="0.75"/>')
            
        # Draw hour line
        if h > 0 and h < 24:
            svg.append(f'<line x1="{x}" y1="{grid_y}" x2="{x}" y2="{grid_y + grid_h}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>')
            
        # Draw hour text labels at the top
        lbl = "Mdt" if h in [0, 24] else ("Noon" if h == 12 else str(h if h <= 12 else h - 12))
        svg.append(f'<text x="{x}" y="{grid_y - 8}" class="grid-axis">{lbl}</text>')
        
    # Status Row Labels on Left
    row_labels = [
        ("OFF DUTY", "OFF"),
        ("SLEEPER BERTH", "SB"),
        ("DRIVING", "D"),
        ("ON DUTY (ND)", "ON")
    ]
    for idx, (label, code) in enumerate(row_labels):
        y = grid_y + idx * row_height + 25
        svg.append(f'<text x="25" y="{y}" class="grid-row-lbl">{idx+1}. {label}</text>')
        
    # Totals column on right
    totals_header_x = grid_x + grid_w + 40
    svg.append(f'<text x="{totals_header_x}" y="{grid_y - 8}" class="total-lbl">TOTAL</text>')
    svg.append(f'<rect x="{grid_x + grid_w}" y="{grid_y}" width="80" height="{grid_h}" fill="none" stroke="#94a3b8" stroke-width="1.5"/>')
    for r in range(1, 4):
        y = grid_y + r * row_height
        svg.append(f'<line x1="{grid_x + grid_w}" y1="{y}" x2="{grid_x + grid_w + 80}" y2="{y}" stroke="#94a3b8" stroke-width="1.5"/>')
        
    # Write totals values
    row_codes = ["OFF", "SB", "D", "ON"]
    for idx, code in enumerate(row_codes):
        y = grid_y + idx * row_height + 25
        val = totals.get(code, 0.0)
        svg.append(f'<text x="{totals_header_x}" y="{y}" class="total-lbl" style="fill: #2563eb;">{val:.2f}</text>')
        
    # --- 3. Plotting the Step Duty-Status Lines ---
    if events:
        path_cmds = []
        last_x = None
        last_y = None
        
        for idx, e in enumerate(events):
            status = e["status"]
            start_mins = time_to_minutes(e["start_time"])
            end_mins = time_to_minutes(e["end_time"])
            
            # Map mins to grid X coordinate
            # 768 pixels total / 1440 minutes = 0.5333 pixels per minute
            x_start = grid_x + (start_mins / 1440.0) * grid_w
            x_end = grid_x + (end_mins / 1440.0) * grid_w
            y_val = status_y_map.get(status, status_y_map["OFF"])
            
            # Connect status transitions with vertical lines
            if last_x is not None and last_y is not None:
                # Vertical line from last status Y to current status Y at current X
                svg.append(f'<line x1="{x_start}" y1="{last_y}" x2="{x_start}" y2="{y_val}" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>')
                
            # Horizontal line for current event duration
            svg.append(f'<line x1="{x_start}" y1="{y_val}" x2="{x_end}" y2="{y_val}" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>')
            
            # Draw circle endpoints at transitions
            svg.append(f'<circle cx="{x_start}" cy="{y_val}" r="2" fill="#1e3a8a"/>')
            svg.append(f'<circle cx="{x_end}" cy="{y_val}" r="2" fill="#1e3a8a"/>')
            
            last_x = x_end
            last_y = y_val

    # --- 4. Remarks and Events List at Bottom ---
    remarks_y = grid_y + grid_h + 35
    svg.append(f'<line x1="25" y1="{remarks_y}" x2="{width - 25}" y2="{remarks_y}" stroke="#cbd5e1" stroke-width="1.5"/>')
    svg.append(f'<text x="30" y="{remarks_y + 20}" class="title" style="font-size: 14px;">DUTY STATUS CHANGES &amp; REMARKS</text>')
    
    # Remarks Table Header
    tbl_hdr_y = remarks_y + 40
    svg.append(f'<text x="30" y="{tbl_hdr_y}" class="remark-hdr">START TIME</text>')
    svg.append(f'<text x="120" y="{tbl_hdr_y}" class="remark-hdr">END TIME</text>')
    svg.append(f'<text x="210" y="{tbl_hdr_y}" class="remark-hdr">STATUS</text>')
    svg.append(f'<text x="310" y="{tbl_hdr_y}" class="remark-hdr">LOCATION</text>')
    svg.append(f'<text x="530" y="{tbl_hdr_y}" class="remark-hdr">REMARKS</text>')
    svg.append(f'<line x1="25" y1="{tbl_hdr_y + 8}" x2="{width - 25}" y2="{tbl_hdr_y + 8}" stroke="#e2e8f0" stroke-width="1"/>')
    
    # Write up to 8 remarks (scrollable or formatted nicely)
    row_y = tbl_hdr_y + 24
    max_visible_events = 7
    for idx, e in enumerate(events[:max_visible_events]):
        status_full = {
            "OFF": "OFF-DUTY",
            "SB": "SLEEPER BERTH",
            "D": "DRIVING",
            "ON": "ON-DUTY NOT DRIVING"
        }.get(e["status"], e["status"])
        
        svg.append(f'<text x="30" y="{row_y}" class="remark-row">{e["start_time"]}</text>')
        svg.append(f'<text x="120" y="{row_y}" class="remark-row">{e["end_time"]}</text>')
        svg.append(f'<text x="210" y="{row_y}" class="remark-row" style="font-weight: 700; fill: #2563eb;">{status_full}</text>')
        
        # Shorten location to fit
        loc = e["location"] or "N/A"
        if len(loc) > 30:
            loc = loc[:27] + "..."
        svg.append(f'<text x="310" y="{row_y}" class="remark-row">{loc}</text>')
        
        # Shorten remark to fit
        rem = e["remarks"] or "N/A"
        if len(rem) > 50:
            rem = rem[:47] + "..."
        svg.append(f'<text x="530" y="{row_y}" class="remark-row">{rem}</text>')
        
        svg.append(f'<line x1="25" y1="{row_y + 6}" x2="{width - 25}" y2="{row_y + 6}" stroke="#f1f5f9" stroke-width="1"/>')
        row_y += 20
        
    if len(events) > max_visible_events:
        svg.append(f'<text x="30" y="{row_y + 5}" class="remark-row" style="fill: #94a3b8; font-style: italic;">+ {len(events) - max_visible_events} more events on this day (displayed on dashboard)</text>')

    svg.append('</svg>')
    return "\n".join(svg)

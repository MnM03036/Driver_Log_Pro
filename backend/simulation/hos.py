import os
import math
import requests
from datetime import datetime, timedelta

# Free, no-key-required public APIs
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"


# ─────────────────────────────────────────────────────────────────────────────
# Geocoding & Routing helpers
# ─────────────────────────────────────────────────────────────────────────────

def geocode_address(address):
    """Geocode address → (lat, lon, display_name) via Nominatim."""
    if not address:
        return 39.0997, -94.5786, str(address)

    headers = {"User-Agent": "LogFillerApp/1.0 (contact@logfiller.com)"}
    params  = {"q": address, "format": "json", "limit": 1}

    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", address)
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")

    # Hard-coded fallbacks for common US cities (prevents total failure when
    # Nominatim is rate-limited or the serverless function has no outbound access)
    fallbacks = {
        "new york":     (40.7128, -74.0060,   "New York, NY, USA"),
        "los angeles":  (34.0522, -118.2437,  "Los Angeles, CA, USA"),
        "chicago":      (41.8781, -87.6298,   "Chicago, IL, USA"),
        "houston":      (29.7604, -95.3698,   "Houston, TX, USA"),
        "phoenix":      (33.4484, -112.0740,  "Phoenix, AZ, USA"),
        "philadelphia": (39.9526, -75.1652,   "Philadelphia, PA, USA"),
        "san antonio":  (29.4241, -98.4936,   "San Antonio, TX, USA"),
        "san diego":    (32.7157, -117.1611,  "San Diego, CA, USA"),
        "dallas":       (32.7767, -96.7970,   "Dallas, TX, USA"),
        "san jose":     (37.3387, -121.8853,  "San Jose, CA, USA"),
        "austin":       (30.2672, -97.7431,   "Austin, TX, USA"),
        "jacksonville": (30.3322, -81.6557,   "Jacksonville, FL, USA"),
        "fort worth":   (32.7555, -97.3308,   "Fort Worth, TX, USA"),
        "columbus":     (39.9612, -82.9988,   "Columbus, OH, USA"),
        "charlotte":    (35.2271, -80.8431,   "Charlotte, NC, USA"),
        "san francisco":(37.7749, -122.4194,  "San Francisco, CA, USA"),
        "seattle":      (47.6062, -122.3321,  "Seattle, WA, USA"),
        "denver":       (39.7392, -104.9903,  "Denver, CO, USA"),
        "washington":   (38.9072, -77.0369,   "Washington, DC, USA"),
        "boston":       (42.3601, -71.0589,   "Boston, MA, USA"),
        "st. louis":    (38.6270, -90.1994,   "St. Louis, MO, USA"),
        "st louis":     (38.6270, -90.1994,   "St. Louis, MO, USA"),
        "memphis":      (35.1495, -90.0490,   "Memphis, TN, USA"),
        "nashville":    (36.1627, -86.7816,   "Nashville, TN, USA"),
        "atlanta":      (33.7490, -84.3880,   "Atlanta, GA, USA"),
        "miami":        (25.7617, -80.1918,   "Miami, FL, USA"),
        "minneapolis":  (44.9778, -93.2650,   "Minneapolis, MN, USA"),
        "kansas city":  (39.0997, -94.5786,   "Kansas City, MO, USA"),
        "las vegas":    (36.1699, -115.1398,  "Las Vegas, NV, USA"),
        "portland":     (45.5051, -122.6750,  "Portland, OR, USA"),
        "oklahoma city":(35.4676, -97.5164,   "Oklahoma City, OK, USA"),
        "albuquerque":  (35.0844, -106.6504,  "Albuquerque, NM, USA"),
        "tucson":       (32.2226, -110.9747,  "Tucson, AZ, USA"),
        "el paso":      (31.7619, -106.4850,  "El Paso, TX, USA"),
    }

    addr_lower = address.lower()
    for city, coords in fallbacks.items():
        if city in addr_lower:
            return coords[0], coords[1], coords[2]

    # Final fallback: geographic center of continental US (Kansas City)
    return 39.0997, -94.5786, f"{address} (Estimated Location)"


def get_route(start_coords, end_coords):
    """Get route distance (m), duration (s), and GeoJSON geometry from OSRM."""
    loc_str = f"{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    url     = f"{OSRM_URL}{loc_str}"
    params  = {"overview": "full", "geometries": "geojson"}

    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                return {
                    "distance_meters":  route["distance"],
                    "duration_seconds": route["duration"],
                    "geometry":         route["geometry"]["coordinates"],  # [[lon, lat], ...]
                }
    except Exception as e:
        print(f"OSRM routing error: {e}")

    # Haversine straight-line fallback when OSRM is unavailable
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    R  = 6_371_000  # Earth radius in metres
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a  = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return {
        "distance_meters":  dist,
        "duration_seconds": dist / 22.35,   # ~50 mph average speed
        "geometry":         [[lon1, lat1], [lon2, lat2]],
    }


def haversine_distance(p1, p2):
    """Distance in miles between two (lat, lon) pairs."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    R  = 3_958.8  # Earth radius in miles
    dl = math.radians(lat2 - lat1)
    dw = math.radians(lon2 - lon1)
    a  = (math.sin(dl / 2) ** 2
          + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
          * math.sin(dw / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def interpolate_coordinate(geometry, fraction):
    """Return (lat, lon) at a given fractional distance along a GeoJSON line."""
    if not geometry:
        return 0.0, 0.0
    if len(geometry) == 1:
        return geometry[0][1], geometry[0][0]
    fraction = max(0.0, min(1.0, fraction))
    if fraction <= 0.0:
        return geometry[0][1], geometry[0][0]
    if fraction >= 1.0:
        return geometry[-1][1], geometry[-1][0]

    segments  = []
    total_dist = 0.0
    for i in range(len(geometry) - 1):
        d = haversine_distance(
            (geometry[i][1], geometry[i][0]),
            (geometry[i + 1][1], geometry[i + 1][0]),
        )
        segments.append(d)
        total_dist += d

    if total_dist == 0:
        return geometry[0][1], geometry[0][0]

    target = total_dist * fraction
    acc    = 0.0
    for i, seg_d in enumerate(segments):
        if acc + seg_d >= target:
            t    = (target - acc) / seg_d if seg_d else 0.0
            lon1, lat1 = geometry[i]
            lon2, lat2 = geometry[i + 1]
            return lat1 + (lat2 - lat1) * t, lon1 + (lon2 - lon1) * t
        acc += seg_d

    return geometry[-1][1], geometry[-1][0]


# ─────────────────────────────────────────────────────────────────────────────
# HOS State Machine
# ─────────────────────────────────────────────────────────────────────────────

class DriverState:
    """
    Tracks all Hours-of-Service counters for a property-carrying driver
    under the FMCSA 70-hour / 8-day ruleset.

    All time values are stored in MINUTES (float) internally.
    """

    def __init__(self, start_time: datetime, initial_cycle_hours: float):
        self.current_time = start_time
        self.status       = "OFF"

        # ── Per-duty-period counters (reset to 0 after a 10-h break) ─────────
        self.driving_today       = 0.0   # limit: 660 min  (11 h)
        self.duty_window_today   = 0.0   # limit: 840 min  (14 h)
        self.is_on_duty_today    = False  # True once driver first comes on duty
        self.driving_since_break = 0.0   # limit: 480 min  (8 h)  → 30-min break

        # ── Rolling 8-day / 70-h cycle ────────────────────────────────────────
        # Index 0 = oldest day (7 days ago), Index 7 = today.
        # Only D and ON time accumulate here.
        self.cycle_history = [initial_cycle_hours / 7.0] * 7 + [0.0]

        # ── Odometer ─────────────────────────────────────────────────────────
        self.odometer           = 0.0   # miles driven so far
        self.last_fuel_odometer = 0.0   # miles at last fuel stop

        # ── Output lists ─────────────────────────────────────────────────────
        self.events  = []   # flat chronological event log
        self.markers = []   # map pin objects

    # ── Helpers ──────────────────────────────────────────────────────────────

    def get_cycle_hours_used(self) -> float:
        return sum(self.cycle_history)

    def log_event(self, start_time, end_time, status, location, remarks, coords):
        """Append or merge into the flat events list."""
        if start_time >= end_time:
            return
        if (self.events
                and self.events[-1]["status"]  == status
                and self.events[-1]["remarks"] == remarks):
            # Extend the previous matching event rather than creating a new one
            self.events[-1]["end_time"] = end_time
        else:
            self.events.append({
                "start_time": start_time,
                "end_time":   end_time,
                "status":     status,
                "location":   location,
                "remarks":    remarks,
                "coords":     coords,
            })

    # ── Core time-advancement method ─────────────────────────────────────────

    def advance_time(self, duration_mins: float, status: str,
                     location: str, remarks: str, coords: tuple):
        """
        Advance simulation time by *duration_mins* with the given status.

        OPTIMISED: splits only at midnight boundaries (O(days) not O(minutes)).
        This is the key change that makes the function run in <1 s on Vercel
        instead of timing out after 10 s.

        Midnight splits are needed so the rolling 8-day cycle_history can be
        updated correctly (each cell represents one calendar day).
        """
        remaining   = float(duration_mins)
        event_start = self.current_time

        while remaining > 0.0:
            mins_in_day       = self.current_time.hour * 60 + self.current_time.minute
            mins_until_midnight = 1440.0 if mins_in_day == 0 else float(1440 - mins_in_day)

            chunk = min(remaining, mins_until_midnight)
            end_t = self.current_time + timedelta(minutes=chunk)

            # ── Update HOS accumulators for this chunk ─────────────────────
            if status in ("D", "ON"):
                self.cycle_history[-1] += chunk / 60.0
                if not self.is_on_duty_today:
                    self.is_on_duty_today  = True
                    self.duty_window_today = 0.0    # window starts fresh
                self.duty_window_today += chunk
                if status == "D":
                    self.driving_today       += chunk
                    self.driving_since_break += chunk

            elif status in ("OFF", "SB"):
                # Off-duty time still counts against the 14-h window
                # once the driver has come on duty that period.
                if self.is_on_duty_today:
                    self.duty_window_today += chunk

            self.current_time  = end_t
            remaining         -= chunk

            # If we landed exactly on midnight and still have time left,
            # roll the 8-day cycle history before the next chunk.
            if (remaining > 0.0
                    and self.current_time.hour   == 0
                    and self.current_time.minute == 0):
                self.cycle_history.pop(0)
                self.cycle_history.append(0.0)

        # Log the full block as one event (group_events_by_day will clip per day)
        self.log_event(event_start, self.current_time, status, location, remarks, coords)


# ─────────────────────────────────────────────────────────────────────────────
# Driving simulation (chunk-based, O(constraint events))
# ─────────────────────────────────────────────────────────────────────────────

def simulate_driving(state: DriverState,
                     total_miles: float,
                     total_duration_mins: float,
                     geometry: list,
                     remarks: str):
    """
    Simulate driving a route segment while enforcing FMCSA HOS rules.

    OPTIMISED: instead of iterating minute-by-minute (original approach,
    O(minutes) ~2 000+ iterations for a cross-country segment), this function
    calculates the *maximum safe driving chunk* before the next constraint
    fires, advances that entire block at once, handles the constraint, and
    repeats.  Typical iteration count: 10-30 per segment regardless of miles.
    """
    if total_duration_mins <= 0 or total_miles <= 0:
        return

    miles_per_min = total_miles / total_duration_mins
    mins_driven   = 0.0
    MAX_ITER      = 1_000   # absolute safety cap (should never be reached)

    for _iteration in range(MAX_ITER):
        if mins_driven >= total_duration_mins:
            break

        frac     = mins_driven / total_duration_mins
        lat, lon = interpolate_coordinate(geometry, frac)
        loc_desc = f"{lat:.4f}, {lon:.4f}"

        # ── Check constraints in FMCSA priority order ─────────────────────

        # 1. Fuel every 1 000 miles (15-min ON stop)
        if state.odometer - state.last_fuel_odometer >= 1_000.0:
            state.advance_time(15, "ON", loc_desc, "Fueling Vehicle", (lat, lon))
            state.last_fuel_odometer = state.odometer
            state.markers.append({
                "type": "fuel", "lat": lat, "lon": lon,
                "time":  state.current_time.isoformat(),
                "label": "Fuel Stop",
                "description": f"Refueled at mile {state.odometer:.1f}",
            })
            continue

        # 2. 70-h / 8-day cycle limit → mandatory 34-h restart
        if state.get_cycle_hours_used() >= 70.0:
            state.advance_time(2040, "OFF", loc_desc,
                               "34-Hour Restart (Cycle Limit)", (lat, lon))
            state.cycle_history      = [0.0] * 8
            state.driving_today      = 0.0
            state.duty_window_today  = 0.0
            state.is_on_duty_today   = False
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "restart", "lat": lat, "lon": lon,
                "time":  state.current_time.isoformat(),
                "label": "34-Hour Restart",
                "description": f"70-hour cycle reset at: {loc_desc}",
            })
            continue

        # 3. 11-h driving limit or 14-h window limit → 10-h sleeper berth
        if state.driving_today >= 660.0 or state.duty_window_today >= 840.0:
            state.advance_time(600, "SB", loc_desc,
                               "10-Hour Reset (Daily Limit)", (lat, lon))
            state.driving_today      = 0.0
            state.duty_window_today  = 0.0
            state.is_on_duty_today   = False
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "rest", "lat": lat, "lon": lon,
                "time":  state.current_time.isoformat(),
                "label": "10-Hour Sleep Break",
                "description": f"HOS Reset at: {loc_desc}",
            })
            continue

        # 4. 8-h continuous driving limit → mandatory 30-min break
        if state.driving_since_break >= 480.0:
            state.advance_time(30, "OFF", loc_desc,
                               "30-Min Rest Break", (lat, lon))
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "break", "lat": lat, "lon": lon,
                "time":  state.current_time.isoformat(),
                "label": "30-Min Break",
                "description": f"Mandatory break at: {loc_desc}",
            })
            continue

        # ── Calculate the largest chunk we can drive before ANY constraint ──
        if miles_per_min > 0:
            mins_to_fuel = max(0.0, (1_000.0 - (state.odometer - state.last_fuel_odometer))
                               / miles_per_min)
        else:
            mins_to_fuel = float("inf")

        mins_to_cycle  = max(0.0, (70.0  - state.get_cycle_hours_used()) * 60.0)
        mins_to_drive  = max(0.0, 660.0  - state.driving_today)
        mins_to_window = max(0.0, 840.0  - state.duty_window_today)
        mins_to_break  = max(0.0, 480.0  - state.driving_since_break)
        mins_remaining = total_duration_mins - mins_driven

        drive_chunk = min(
            mins_to_fuel,
            mins_to_cycle,
            mins_to_drive,
            mins_to_window,
            mins_to_break,
            mins_remaining,
        )

        # Safety: always make forward progress
        if drive_chunk <= 0.0:
            drive_chunk = min(1.0, mins_remaining)
            if drive_chunk <= 0.0:
                break

        state.advance_time(drive_chunk, "D", loc_desc, remarks, (lat, lon))
        state.odometer += miles_per_min * drive_chunk
        mins_driven    += drive_chunk


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def simulate_trip(current_loc: str, pickup_loc: str,
                  dropoff_loc: str, current_cycle_hours: float) -> dict:
    """
    Run a complete HOS-compliant truck driver trip simulation.
    Returns a dict with route_coordinates, markers, daily_logs, and summary info.
    """
    from concurrent.futures import ThreadPoolExecutor

    # ── 1. Geocode all three addresses in parallel ─────────────────────────
    with ThreadPoolExecutor(max_workers=3) as ex:
        fc = ex.submit(geocode_address, current_loc)
        fp = ex.submit(geocode_address, pickup_loc)
        fd = ex.submit(geocode_address, dropoff_loc)
        lat_c, lon_c, desc_c = fc.result()
        lat_p, lon_p, desc_p = fp.result()
        lat_d, lon_d, desc_d = fd.result()

    # ── 2. Fetch both route segments in parallel ───────────────────────────
    with ThreadPoolExecutor(max_workers=2) as ex:
        fr1 = ex.submit(get_route, (lat_c, lon_c), (lat_p, lon_p))
        fr2 = ex.submit(get_route, (lat_p, lon_p), (lat_d, lon_d))
        route_c2p = fr1.result()
        route_p2d = fr2.result()

    # ── 3. Initialise simulation ───────────────────────────────────────────
    start_time = datetime(2026, 6, 18, 0, 0, 0)
    state      = DriverState(start_time, current_cycle_hours)

    state.markers += [
        {"type": "start",   "lat": lat_c, "lon": lon_c,
         "time": state.current_time.isoformat(),
         "label": "Origin",           "description": desc_c},
        {"type": "pickup",  "lat": lat_p, "lon": lon_p,
         "time": None,
         "label": "Pickup Location",  "description": desc_p},
        {"type": "dropoff", "lat": lat_d, "lon": lon_d,
         "time": None,
         "label": "Drop-off Location","description": desc_d},
    ]

    # ── 4. Pre-trip inspection (15 min ON Duty) ────────────────────────────
    state.advance_time(15, "ON", desc_c, "Pre-Trip Inspection", (lat_c, lon_c))

    # ── 5. Drive: Current Location → Pickup ───────────────────────────────
    dist1 = route_c2p["distance_meters"] * 0.000621371
    dur1  = route_c2p["duration_seconds"] / 60.0
    simulate_driving(state, dist1, dur1, route_c2p["geometry"], "En Route to Pickup")

    for m in state.markers:
        if m["type"] == "pickup":
            m["time"] = state.current_time.isoformat()

    # ── 6. Loading at Pickup (1 h ON, with daily-limit guard) ─────────────
    if state.driving_today >= 660.0 or state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_p, "10-Hour Reset (Daily Limit)", (lat_p, lon_p))
        state.driving_today = state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest", "lat": lat_p, "lon": lon_p,
            "time":  state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest at Pickup: {desc_p}",
        })

    state.advance_time(60, "ON", desc_p, "Loading Cargo", (lat_p, lon_p))

    # ── 7. Drive: Pickup → Drop-off ────────────────────────────────────────
    dist2 = route_p2d["distance_meters"] * 0.000621371
    dur2  = route_p2d["duration_seconds"] / 60.0

    if state.driving_today >= 660.0 or state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_p, "10-Hour Reset (Daily Limit)", (lat_p, lon_p))
        state.driving_today = state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest", "lat": lat_p, "lon": lon_p,
            "time":  state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest before Segment 2: {desc_p}",
        })

    simulate_driving(state, dist2, dur2, route_p2d["geometry"], "En Route to Drop-off")

    for m in state.markers:
        if m["type"] == "dropoff":
            m["time"] = state.current_time.isoformat()

    # ── 8. Unloading at Drop-off (1 h ON, with daily-limit guard) ─────────
    if state.driving_today >= 660.0 or state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_d, "10-Hour Reset (Daily Limit)", (lat_d, lon_d))
        state.driving_today = state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest", "lat": lat_d, "lon": lon_d,
            "time":  state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest at Dropoff: {desc_d}",
        })

    state.advance_time(60, "ON", desc_d, "Unloading Cargo", (lat_d, lon_d))

    # ── 9. Pad remainder of final day with Off Duty ────────────────────────
    mins_used = state.current_time.hour * 60 + state.current_time.minute
    remaining = 1440 - mins_used
    if 0 < remaining < 1440:
        state.advance_time(remaining, "OFF", desc_d,
                           "Off Duty (Trip Complete)", (lat_d, lon_d))

    # ── 10. Group flat event list into per-day log objects ─────────────────
    daily_logs = group_events_by_day(state.events, start_time)

    return {
        "start_location":    desc_c,
        "pickup_location":   desc_p,
        "dropoff_location":  desc_d,
        "total_miles":       round(state.odometer, 1),
        "markers":           state.markers,
        "daily_logs":        daily_logs,
        "route_coordinates": route_c2p["geometry"] + route_p2d["geometry"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Daily log sheet grouping
# ─────────────────────────────────────────────────────────────────────────────

def group_events_by_day(flat_events: list, base_start_time: datetime) -> list:
    """
    Clip the continuous flat event list into per-calendar-day segments.
    Events that span midnight are clipped to each day's bounds.
    """
    if not flat_events:
        return []

    start_date = flat_events[0]["start_time"].date()
    end_date   = flat_events[-1]["end_time"].date()

    daily_logs = []
    curr_date  = start_date
    day_num    = 1

    while curr_date <= end_date:
        day_start = datetime(curr_date.year, curr_date.month, curr_date.day,  0,  0,  0)
        day_end   = datetime(curr_date.year, curr_date.month, curr_date.day, 23, 59, 59)

        day_events                         = []
        off_mins = sb_mins = d_mins = on_mins = 0.0

        for e in flat_events:
            ov_start = max(day_start, e["start_time"])
            ov_end   = min(day_end,   e["end_time"])
            if ov_start >= ov_end:
                continue

            dur = (ov_end - ov_start).total_seconds() / 60.0
            s   = e["status"]
            if   s == "OFF": off_mins += dur
            elif s == "SB":  sb_mins  += dur
            elif s == "D":   d_mins   += dur
            elif s == "ON":  on_mins  += dur

            day_events.append({
                "start_time": ov_start.strftime("%H:%M"),
                "end_time":   ov_end.strftime("%H:%M"),
                "status":     s,
                "location":   e["location"],
                "remarks":    e["remarks"],
                "coords":     e["coords"],
            })

        daily_logs.append({
            "day_number": day_num,
            "date":       curr_date.strftime("%Y-%m-%d"),
            "totals": {
                "OFF":   round(off_mins / 60.0, 2),
                "SB":    round(sb_mins  / 60.0, 2),
                "D":     round(d_mins   / 60.0, 2),
                "ON":    round(on_mins  / 60.0, 2),
                "total": round((off_mins + sb_mins + d_mins + on_mins) / 60.0, 2),
            },
            "events": day_events,
        })

        curr_date += timedelta(days=1)
        day_num   += 1

    return daily_logs

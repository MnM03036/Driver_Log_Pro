import os
import math
import requests
from datetime import datetime, timedelta

# Free APIs
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"

def geocode_address(address):
    """
    Geocode address to (lat, lon) using Nominatim.
    """
    if not address:
        return None
    
    headers = {"User-Agent": "LogFillerApp/1.0 (contact@logfiller.com)"}
    params = {"q": address, "format": "json", "limit": 1}
    
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"]), data.get("display_name", address)
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
    
    # Fallback coordinates for common US cities to prevent total failure
    fallbacks = {
        "new york": (40.7128, -74.0060, "New York, NY, USA"),
        "los angeles": (34.0522, -118.2437, "Los Angeles, CA, USA"),
        "chicago": (41.8781, -87.6298, "Chicago, IL, USA"),
        "houston": (29.7604, -95.3698, "Houston, TX, USA"),
        "phoenix": (33.4484, -112.0740, "Phoenix, AZ, USA"),
        "philadelphia": (39.9526, -75.1652, "Philadelphia, PA, USA"),
        "san antonio": (29.4241, -98.4936, "San Antonio, TX, USA"),
        "san diego": (32.7157, -117.1611, "San Diego, CA, USA"),
        "dallas": (32.7767, -96.7970, "Dallas, TX, USA"),
        "san jose": (37.3387, -121.8853, "San Jose, CA, USA"),
        "austin": (30.2672, -97.7431, "Austin, TX, USA"),
        "jacksonville": (30.3322, -81.6557, "Jacksonville, FL, USA"),
        "fort worth": (32.7555, -97.3308, "Fort Worth, TX, USA"),
        "columbus": (39.9612, -82.9988, "Columbus, OH, USA"),
        "charlotte": (35.2271, -80.8431, "Charlotte, NC, USA"),
        "san francisco": (37.7749, -122.4194, "San Francisco, CA, USA"),
        "seattle": (47.6062, -122.3321, "Seattle, WA, USA"),
        "denver": (39.7392, -104.9903, "Denver, CO, USA"),
        "washington": (38.9072, -77.0369, "Washington, DC, USA"),
        "boston": (42.3601, -71.0589, "Boston, MA, USA"),
    }
    
    addr_lower = address.lower()
    for city, coords in fallbacks.items():
        if city in addr_lower:
            return coords[0], coords[1], coords[2]
            
    # Default US center fallback (Kansas City)
    return 39.0997, -94.5786, f"{address} (Estimated)"

def get_route(start_coords, end_coords):
    """
    Get routing distance (meters), duration (seconds), and geometry path (GeoJSON) from OSRM.
    """
    # Coordinates format: lon,lat;lon,lat
    loc_str = f"{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    url = f"{OSRM_URL}{loc_str}"
    params = {"overview": "full", "geometries": "geojson"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                return {
                    "distance_meters": route["distance"],
                    "duration_seconds": route["duration"],
                    "geometry": route["geometry"]["coordinates"] # List of [lon, lat]
                }
    except Exception as e:
        print(f"OSRM routing error: {e}")
        
    # Haversine distance fallback if OSRM is down
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    R = 6371000 # radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = R * c
    
    # Estimate speed at 50 mph (22.35 m/s)
    speed = 22.35
    duration = dist / speed
    
    return {
        "distance_meters": dist,
        "duration_seconds": duration,
        "geometry": [[lon1, lat1], [lon2, lat2]]
    }

def haversine_distance(p1, p2):
    """
    Calculate distance in miles between two (lat, lon) coordinates.
    """
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 3958.8 # Earth radius in miles
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def interpolate_coordinate(geometry, fraction):
    """
    Find coordinate at a given fraction along a GeoJSON line geometry (list of [lon, lat]).
    """
    if not geometry or len(geometry) == 0:
        return 0.0, 0.0
    if len(geometry) == 1:
        return geometry[0][1], geometry[0][0]
    if fraction <= 0.0:
        return geometry[0][1], geometry[0][0]
    if fraction >= 1.0:
        return geometry[-1][1], geometry[-1][0]
        
    # Calculate cumulative distance along segments
    segments = []
    total_dist = 0.0
    for i in range(len(geometry) - 1):
        p1 = (geometry[i][1], geometry[i][0])
        p2 = (geometry[i+1][1], geometry[i+1][0])
        d = haversine_distance(p1, p2)
        segments.append(d)
        total_dist += d
        
    if total_dist == 0:
        return geometry[0][1], geometry[0][0]
        
    target_dist = total_dist * fraction
    curr_dist = 0.0
    
    for i, seg_d in enumerate(segments):
        if curr_dist + seg_d >= target_dist:
            # Target is inside this segment
            seg_fraction = (target_dist - curr_dist) / seg_d
            lon1, lat1 = geometry[i]
            lon2, lat2 = geometry[i+1]
            # Interpolate
            lat = lat1 + (lat2 - lat1) * seg_fraction
            lon = lon1 + (lon2 - lon1) * seg_fraction
            return lat, lon
        curr_dist += seg_d
        
    return geometry[-1][1], geometry[-1][0]

class DriverState:
    def __init__(self, start_time, initial_cycle_hours):
        self.current_time = start_time
        self.status = "OFF" # OFF, SB, D, ON
        
        # HOS Tracking (minutes)
        self.driving_today = 0.0          # Max 11 hours (660 mins)
        self.duty_window_today = 0.0      # Max 14 hours (840 mins)
        self.is_on_duty_today = False     # Toggles true when duty window starts
        self.driving_since_break = 0.0    # Max 8 hours (480 mins)
        
        # Rolling 70-hour/8-day cycle history in hours.
        # cycle_history[7] is today, [0] is 7 days ago.
        self.cycle_history = [initial_cycle_hours / 7.0] * 7 + [0.0]
        
        self.odometer = 0.0
        self.last_fuel_odometer = 0.0
        
        # List of flat events: {start_time, end_time, status, location, remarks, coords}
        self.events = []
        
        # Map markers: {type, lat, lon, time, label, description}
        self.markers = []

    def get_cycle_hours_used(self):
        """
        Total duty hours used in the 8-day rolling window.
        """
        return sum(self.cycle_history)

    def log_event(self, start_time, end_time, status, location, remarks, coords):
        """
        Log an event in the continuous timeline.
        """
        if start_time >= end_time:
            return
        
        # Merge consecutive identical events (ignore location coordinate diffs)
        if self.events and self.events[-1]["status"] == status and self.events[-1]["remarks"] == remarks:
            self.events[-1]["end_time"] = end_time
        else:
            self.events.append({
                "start_time": start_time,
                "end_time": end_time,
                "status": status,
                "location": location,
                "remarks": remarks,
                "coords": coords
            })

    def advance_time(self, duration_mins, status, location, remarks, coords):
        """
        Advance state minute-by-minute, splitting events at midnight and tracking metrics.
        """
        start_t = self.current_time
        
        for _ in range(int(duration_mins)):
            next_t = self.current_time + timedelta(minutes=1)
            
            # Check for midnight boundary crossing
            if self.current_time.date() != next_t.date():
                # End current event at midnight
                self.log_event(start_t, self.current_time, status, location, remarks, coords)
                start_t = next_t
                
                # Roll rolling cycle history
                self.cycle_history.pop(0)
                self.cycle_history.append(0.0)
                
            # Update duty timers
            if status in ["D", "ON"]:
                # Add to rolling cycle history (converted to hours)
                self.cycle_history[-1] += 1.0 / 60.0
                
                if not self.is_on_duty_today:
                    self.is_on_duty_today = True
                    self.duty_window_today = 0.0
                
                self.duty_window_today += 1.0
                
                if status == "D":
                    self.driving_today += 1.0
                    self.driving_since_break += 1.0
            elif status in ["OFF", "SB"]:
                if self.is_on_duty_today:
                    self.duty_window_today += 1.0
                    
            self.current_time = next_t
            
        # Log remaining block
        self.log_event(start_t, self.current_time, status, location, remarks, coords)


def simulate_trip(current_loc, pickup_loc, dropoff_loc, current_cycle_hours):
    """
    Run complete truck driver HOS simulation.
    """
    from concurrent.futures import ThreadPoolExecutor

    # 1. Geocode locations in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_c = executor.submit(geocode_address, current_loc)
        future_p = executor.submit(geocode_address, pickup_loc)
        future_d = executor.submit(geocode_address, dropoff_loc)
        
        lat_c, lon_c, desc_c = future_c.result()
        lat_p, lon_p, desc_p = future_p.result()
        lat_d, lon_d, desc_d = future_d.result()
    
    # 2. Get routes in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_r1 = executor.submit(get_route, (lat_c, lon_c), (lat_p, lon_p))
        future_r2 = executor.submit(get_route, (lat_p, lon_p), (lat_d, lon_d))
        
        route_c_to_p = future_r1.result()
        route_p_to_d = future_r2.result()
    
    # Start on day 1 at 00:00:00
    start_time = datetime(2026, 6, 18, 0, 0, 0)
    state = DriverState(start_time, current_cycle_hours)
    
    # Setup initial markers
    state.markers.append({
        "type": "start",
        "lat": lat_c,
        "lon": lon_c,
        "time": state.current_time.isoformat(),
        "label": "Origin",
        "description": desc_c
    })
    
    state.markers.append({
        "type": "pickup",
        "lat": lat_p,
        "lon": lon_p,
        "time": None, # Filled during simulation
        "label": "Pickup Location",
        "description": desc_p
    })
    
    state.markers.append({
        "type": "dropoff",
        "lat": lat_d,
        "lon": lon_d,
        "time": None, # Filled during simulation
        "label": "Drop-off Location",
        "description": desc_d
    })
    
    # --- Activity 1: Pre-trip Inspection (15 mins ON) ---
    state.advance_time(15, "ON", desc_c, "Pre-Trip Inspection", (lat_c, lon_c))
    
    # --- Activity 2: Segment 1 (Current -> Pickup) ---
    dist1_miles = route_c_to_p["distance_meters"] * 0.000621371
    dur1_mins = int(route_c_to_p["duration_seconds"] / 60)
    simulate_driving(state, dist1_miles, dur1_mins, route_c_to_p["geometry"], "En Route to Pickup")
    
    # Record pickup arrival time
    for m in state.markers:
        if m["type"] == "pickup":
            m["time"] = state.current_time.isoformat()
            
    # --- Activity 3: Loading at Pickup (1 hour ON) ---
    # First check if 14-hour limit has been exceeded. If so, take a 10h break before loading.
    if state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_p, "10-Hour Reset (Daily Limit)", (lat_p, lon_p))
        state.driving_today = 0.0
        state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest",
            "lat": lat_p,
            "lon": lon_p,
            "time": state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest at Pickup: {desc_p}"
        })
        
    state.advance_time(60, "ON", desc_p, "Loading Cargo", (lat_p, lon_p))
    
    # --- Activity 4: Segment 2 (Pickup -> Drop-off) ---
    dist2_miles = route_p_to_d["distance_meters"] * 0.000621371
    dur2_mins = int(route_p_to_d["duration_seconds"] / 60)
    
    # If starting segment 2 will immediately violate 14-hour duty window, insert a 10-hour reset now
    if state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_p, "10-Hour Reset (Daily Limit)", (lat_p, lon_p))
        state.driving_today = 0.0
        state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest",
            "lat": lat_p,
            "lon": lon_p,
            "time": state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest before Segment 2: {desc_p}"
        })
        
    simulate_driving(state, dist2_miles, dur2_mins, route_p_to_d["geometry"], "En Route to Drop-off")
    
    # Record drop-off arrival time
    for m in state.markers:
        if m["type"] == "dropoff":
            m["time"] = state.current_time.isoformat()
            
    # --- Activity 5: Unloading at Drop-off (1 hour ON) ---
    # First check if 14-hour limit has been exceeded. If so, take a 10h break before unloading.
    if state.duty_window_today >= 840.0:
        state.advance_time(600, "SB", desc_d, "10-Hour Reset (Daily Limit)", (lat_d, lon_d))
        state.driving_today = 0.0
        state.duty_window_today = 0.0
        state.is_on_duty_today = False
        state.driving_since_break = 0.0
        state.markers.append({
            "type": "rest",
            "lat": lat_d,
            "lon": lon_d,
            "time": state.current_time.isoformat(),
            "label": "10-Hour Sleep Break",
            "description": f"Rest at Dropoff: {desc_d}"
        })
        
    state.advance_time(60, "ON", desc_d, "Unloading Cargo", (lat_d, lon_d))
    
    # Pad the final day to midnight (24:00) with Off-Duty
    remaining_mins = 1440 - (state.current_time.hour * 60 + state.current_time.minute)
    if remaining_mins > 0 and remaining_mins < 1440:
        state.advance_time(remaining_mins, "OFF", desc_d, "Off Duty (Trip Complete)", (lat_d, lon_d))
        
    # Group the events into daily segments
    daily_logs = group_events_by_day(state.events, start_time)
    
    # Return everything
    return {
        "start_location": desc_c,
        "pickup_location": desc_p,
        "dropoff_location": desc_d,
        "total_miles": round(state.odometer, 1),
        "markers": state.markers,
        "daily_logs": daily_logs,
        "route_coordinates": route_c_to_p["geometry"] + route_p_to_d["geometry"]
    }


def simulate_driving(state, total_miles, total_duration_mins, geometry, remarks):
    """
    Drive a segment step-by-step, checking HOS rules minute-by-minute.
    """
    if total_duration_mins <= 0:
        return
        
    miles_per_min = total_miles / total_duration_mins
    mins_driven = 0
    
    while mins_driven < total_duration_mins:
        # Interpolate coordinates of current location
        frac = mins_driven / total_duration_mins
        lat, lon = interpolate_coordinate(geometry, frac)
        loc_desc = f"{lat:.4f}, {lon:.4f}"
        
        # 1. Check Fueling Limit: every 1,000 miles
        if state.odometer - state.last_fuel_odometer >= 1000.0:
            # Perform a 15-minute ON fueling stop
            state.advance_time(15, "ON", loc_desc, "Fueling Vehicle", (lat, lon))
            state.last_fuel_odometer = state.odometer
            state.markers.append({
                "type": "fuel",
                "lat": lat,
                "lon": lon,
                "time": state.current_time.isoformat(),
                "label": "Fuel Stop",
                "description": f"Refueled at mile {state.odometer:.1f}"
            })
            
        # 2. Check 70-Hour Rolling Limit:
        if state.get_cycle_hours_used() >= 70.0:
            # Must take a 34-hour restart
            state.advance_time(2040, "OFF", loc_desc, "34-Hour Restart (Cycle Limit)", (lat, lon))
            # Reset HOS
            state.cycle_history = [0.0] * 8
            state.driving_today = 0.0
            state.duty_window_today = 0.0
            state.is_on_duty_today = False
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "restart",
                "lat": lat,
                "lon": lon,
                "time": state.current_time.isoformat(),
                "label": "34-Hour Restart",
                "description": f"70-hour cycle reset at: {loc_desc}"
            })
            
        # 3. Check 11-Hour Driving Limit or 14-Hour Duty Window Limit
        # If we are about to violate driving limits, trigger a 10-hour reset
        if state.driving_today >= 660.0 or state.duty_window_today >= 840.0:
            state.advance_time(600, "SB", loc_desc, "10-Hour Reset (Daily Limit)", (lat, lon))
            state.driving_today = 0.0
            state.duty_window_today = 0.0
            state.is_on_duty_today = False
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "rest",
                "lat": lat,
                "lon": lon,
                "time": state.current_time.isoformat(),
                "label": "10-Hour Sleep Break",
                "description": f"HOS Reset at: {loc_desc}"
            })
            
        # 4. Check 8-Hour Continuous Driving Limit
        if state.driving_since_break >= 480.0:
            # Must take a 30-minute break
            state.advance_time(30, "OFF", loc_desc, "30-Min Rest Break", (lat, lon))
            state.driving_since_break = 0.0
            state.markers.append({
                "type": "break",
                "lat": lat,
                "lon": lon,
                "time": state.current_time.isoformat(),
                "label": "30-Min Break",
                "description": f"Mandatory break at: {loc_desc}"
            })
            
        # Drive for 1 minute
        state.advance_time(1, "D", loc_desc, remarks, (lat, lon))
        state.odometer += miles_per_min
        mins_driven += 1


def group_events_by_day(flat_events, base_start_time):
    """
    Split continuous flat events into standard 24-hour daily segments.
    """
    if not flat_events:
        return []
        
    start_date = flat_events[0]["start_time"].date()
    end_date = flat_events[-1]["end_time"].date()
    
    daily_logs = []
    curr_date = start_date
    day_num = 1
    
    while curr_date <= end_date:
        day_start = datetime(curr_date.year, curr_date.month, curr_date.day, 0, 0, 0)
        day_end = datetime(curr_date.year, curr_date.month, curr_date.day, 23, 59, 59)
        
        day_events = []
        off_mins = 0.0
        sb_mins = 0.0
        d_mins = 0.0
        on_mins = 0.0
        
        for e in flat_events:
            # Check overlap
            overlap_start = max(day_start, e["start_time"])
            overlap_end = min(day_end, e["end_time"])
            
            if overlap_start < overlap_end:
                duration_mins = (overlap_end - overlap_start).total_seconds() / 60.0
                status = e["status"]
                
                # Accumulate hours
                if status == "OFF":
                    off_mins += duration_mins
                elif status == "SB":
                    sb_mins += duration_mins
                elif status == "D":
                    d_mins += duration_mins
                elif status == "ON":
                    on_mins += duration_mins
                    
                day_events.append({
                    "start_time": overlap_start.strftime("%H:%M"),
                    "end_time": overlap_end.strftime("%H:%M"),
                    "status": status,
                    "location": e["location"],
                    "remarks": e["remarks"],
                    "coords": e["coords"]
                })
                
        # Total sums in decimal hours
        daily_logs.append({
            "day_number": day_num,
            "date": curr_date.strftime("%Y-%m-%d"),
            "totals": {
                "OFF": round(off_mins / 60.0, 2),
                "SB": round(sb_mins / 60.0, 2),
                "D": round(d_mins / 60.0, 2),
                "ON": round(on_mins / 60.0, 2),
                "total": round((off_mins + sb_mins + d_mins + on_mins) / 60.0, 2)
            },
            "events": day_events
        })
        
        curr_date += timedelta(days=1)
        day_num += 1
        
    return daily_logs

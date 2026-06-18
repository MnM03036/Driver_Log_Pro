Role: You are an elite Full-Stack Software Engineer with expertise in Django, React, and logistics/routing algorithms.

Task: Build a complete, production-ready web application that takes trip parameters as input, calculates a route, simulates a truck driver’s duty cycle according to strict FMCSA Hours of Service (HOS) regulations, and visually generates daily driver log sheets.

Tech Stack & Architecture:

Frontend: React (preferably Vite), Tailwind CSS for a premium, low-friction Apple/Tesla-esque minimalist UI, React-Leaflet (or similar free map library) for route visualization.

Backend: Django with Django REST Framework (DRF) to handle the routing API calls, HOS algorithmic simulation, and log sheet generation logic.

Hosting: Configured for seamless deployment on Vercel (frontend and serverless backend).

Core Inputs (UI Form):

Current Location (String/Address)

Pickup Location (String/Address)

Drop-off Location (String/Address)

Current 70hr/8day cycle hours used (Float)

Core Outputs:

Interactive Map: Displaying the route, driving segments, and precise markers for 30-min breaks, 10-hour sleeper/off-duty breaks, and fuel stops. (Use a free API like Open Source Routing Machine (OSRM) or OpenRouteService for geocoding and routing data).

Generated ELD Log Sheets: Visual replicas of standard daily log sheets (using an uploaded blank template). The app must draw the duty status lines dynamically over a 24-hour grid for however many days the trip takes.

Business Logic & HOS Simulation Engine:
Create a chronological simulation algorithm in Python (Django backend) that calculates the trip minute-by-minute based on the routing API's time/distance estimates.

Rules Engine Assumptions:

Driver Profile: Property-carrying, 70-hour/8-day limit, no adverse driving conditions.

14-Hour Window: A driver cannot drive after 14 hours of coming on duty. Requires 10 consecutive hours off-duty/sleeper berth to reset.

11-Hour Limit: Maximum of 11 hours driving within the 14-hour window.

30-Minute Break: Required after 8 cumulative hours of driving. Logged as Off-Duty or On-Duty Not Driving.

60/70-Hour Limit: Cannot drive after reaching 70 hours on duty in 8 days. (Assume a 34-hour restart is required if this limit is hit during the trip).

Pre-defined Stops: >     * 1 hour of "On-Duty (Not Driving)" time at both the Pickup and Drop-off locations.

15 minutes of "On-Duty (Not Driving)" for fueling at least once every 1,000 miles.

Log Sheet Drawing Logic:

The backend must output the simulation data as an array of daily objects, each containing an array of events (Start Time, End Time, Status, Location, Remarks).

Use HTML5 Canvas (or Python Pillow on the backend) to overlay lines onto the provided log sheet template.

Line 1: Off Duty (breaks, 10-hr resets, 34-hr restarts)

Line 2: Sleeper Berth (can be used interchangeably with Off Duty for the 10-hr reset)

Line 3: Driving (actual movement time)

Line 4: On Duty (loading, unloading, fueling, pre-trip inspections)

Include automatic calculation of total hours at the right of the grid and mileage/header info at the top.

Deliverables Request:

Provide the complete Django backend models, views, and the simulation algorithm script.

Provide the React components, Tailwind styling, and mapping implementation.

Provide the specific logic for rendering the lines onto the log sheet image based on the generated timestamps.

Provide vercel.json and deployment instructions to ensure standard production quality.
<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Deployed%20On-Vercel-black?style=for-the-badge&logo=vercel" alt="Vercel" />
  <img src="https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=for-the-badge&logo=react" alt="React" />
  <img src="https://img.shields.io/badge/Backend-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Styling-Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind" />
</p>

# 🚛 Driver Log Pro

> **An intelligent FMCSA Hours-of-Service (HOS) trip simulator and ELD log sheet generator.**
>
> Enter your trip — origin, pickup, and drop-off — and get a fully compliant driver duty cycle simulation with an interactive route map and downloadable daily log sheets, all generated in seconds.

## 🌐 Live Demo

### **[▶ driver-log-pro-tau.vercel.app](https://driver-log-pro-tau.vercel.app/)**

---

## 📖 What This Project Does

Driver Log Pro is a full-stack web application built for the trucking and logistics industry. It solves a critical operational problem: **planning a multi-day truck route while staying fully compliant with federal FMCSA Hours of Service (HOS) regulations.**

Given three addresses (current location, pickup, drop-off) and a driver's existing cycle usage, the app:

1.  **Geocodes** all locations and **calculates the optimal driving route** via OSRM (Open Source Routing Machine).
2.  **Simulates the entire trip chronologically**, injecting mandatory rest breaks, sleeper berth resets, fueling stops, and loading/unloading time based on FMCSA rules.
3.  **Renders an interactive Leaflet map** with the plotted route, color-coded stop markers (fuel, 30-min break, 10-hr sleep, 34-hr restart), and origin/destination pins.
4.  **Generates visual daily ELD log sheets** — accurate replicas of the standard 24-hour driver log grid — with duty status lines drawn dynamically across the grid, complete with remarks, totals, and header metadata.

---

## ⚙️ How It Works

The application is split into a **React + Vite frontend** and a **Python serverless backend**, both deployed on Vercel as a monorepo.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        VERCEL PLATFORM                          │
│                                                                 │
│  ┌──────────────────────┐     ┌──────────────────────────────┐  │
│  │   React Frontend     │     │   Python Serverless API      │  │
│  │   (Vite + Tailwind)  │────▶│   /api/simulate (POST)       │  │
│  │                      │     │   /api/download-log (GET)     │  │
│  │  • SimulationForm    │◀────│                              │  │
│  │  • Leaflet Map       │     │  ┌────────────────────────┐  │  │
│  │  • Canvas LogGrid    │     │  │  HOS Simulation Engine │  │  │
│  │  • SummaryCards      │     │  │  (hos.py)              │  │  │
│  └──────────────────────┘     │  └────────────────────────┘  │  │
│                               │  ┌────────────────────────┐  │  │
│                               │  │  SVG Log Generator     │  │  │
│                               │  │  (svg_generator.py)    │  │  │
│                               │  └────────────────────────┘  │  │
│                               └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
   ┌─────────────┐              ┌──────────────────┐
   │  Leaflet /  │              │  Nominatim       │
   │  OpenStreet │              │  (Geocoding)     │
   │  Map Tiles  │              │  OSRM (Routing)  │
   └─────────────┘              └──────────────────┘
```

### Backend — HOS Simulation Engine (`api/hos.py`)

The core of the application is a **chronological state-machine** that processes the trip minute-by-minute (optimized into chunk-based iteration for performance). It enforces every major FMCSA rule:

| FMCSA Rule | Implementation |
|---|---|
| **11-Hour Driving Limit** | Max 11 hours driving after 10 consecutive hours off duty. Engine triggers a 10-hr sleeper berth reset when limit is reached. |
| **14-Hour Duty Window** | Cannot drive beyond 14 hours after coming on duty. Tracked separately from driving time; off-duty time still counts against it. |
| **30-Minute Break** | Required after 8 cumulative hours of driving. Logged as a 30-min Off-Duty event. |
| **70-Hour / 8-Day Cycle** | Tracks an 8-day rolling window of on-duty time. Triggers a mandatory 34-hour restart when 70 hours are reached. |
| **Fueling Stops** | 15-minute On-Duty (Not Driving) stop injected every 1,000 miles. |
| **Loading / Unloading** | 1 hour of On-Duty (Not Driving) at both pickup and drop-off locations. |
| **Pre-Trip Inspection** | 15 minutes On-Duty at the origin before driving begins. |

The engine uses the `DriverState` class to track all HOS accumulators (driving time today, duty window, 8-day cycle history, odometer, etc.) and outputs a flat chronological event list that is then clipped into per-calendar-day segments.

### Backend — SVG Log Generator (`api/svg_generator.py`)

Converts each day's event data into a publication-quality SVG image of a standard 24-hour driver log sheet:
- 4-row duty status grid (Off Duty, Sleeper Berth, Driving, On Duty Not Driving)
- Step-function duty lines with transition markers
- Hour/quarter-hour grid lines with Midnight and Noon labels
- Per-row hour totals
- Remarks table with location and event descriptions

### Frontend — React Dashboard

| Component | Purpose |
|---|---|
| **`SimulationForm`** | Trip input form with address fields, cycle hours, driver metadata, and validation |
| **`Map` (RouteMap)** | React-Leaflet interactive map showing the OSRM route polyline and all stop markers with color-coded icons |
| **`LogGrid`** | HTML5 Canvas renderer that draws the daily log sheet grid and duty status lines client-side |
| **`SummaryCards`** | KPI dashboard cards showing total miles, total days, driving hours, and cycle hours used |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 19 + Vite 8 |
| **Styling** | Tailwind CSS 4 |
| **Map** | React-Leaflet 5 + Leaflet (OpenStreetMap tiles) |
| **Icons** | Lucide React |
| **Backend** | Python 3.x (Vercel Serverless Functions) |
| **Geocoding** | Nominatim (OpenStreetMap) — no API key required |
| **Routing** | OSRM (Open Source Routing Machine) — no API key required |
| **Log Sheets** | SVG generation (backend) + HTML5 Canvas (frontend) |
| **Deployment** | Vercel (monorepo: static build + Python serverless) |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.9
- **npm** or **yarn**

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/MnM03036/Driver_Log_Pro.git
cd Driver_Log_Pro

# 2. Install frontend dependencies
cd frontend
npm install

# 3. Start the frontend dev server
npm run dev
# → opens at http://localhost:5173

# 4. (Optional) Install Python API dependencies for local testing
cd ../api
pip install -r requirements.txt
```

> **Note:** The Python API functions (`/api/simulate`, `/api/download-log`) are designed as Vercel Serverless Functions. For full local testing with the backend, use the [Vercel CLI](https://vercel.com/docs/cli):
>
> ```bash
> npm i -g vercel
> vercel dev
> ```

### Deployment (Vercel)

The project is configured for zero-config Vercel deployment via [`vercel.json`](vercel.json):

```bash
# Deploy to Vercel
vercel --prod
```

The `vercel.json` routes:
- `/api/*` → Python serverless functions in `api/`
- `/*` → Static build output from `frontend/dist/`

---

## 📁 Project Structure

```
Driver_Log_Pro/
├── api/                          # Python serverless backend
│   ├── simulate.py               # Vercel handler (POST simulate, GET download-log)
│   ├── hos.py                    # HOS simulation engine & state machine
│   ├── svg_generator.py          # SVG daily log sheet renderer
│   ├── download-log.py           # SVG download endpoint
│   └── requirements.txt          # Python dependencies (requests)
│
├── frontend/                     # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx               # Main app shell, routing, state management
│   │   ├── components/
│   │   │   ├── SimulationForm.jsx # Trip input form
│   │   │   ├── Map.jsx           # React-Leaflet route map
│   │   │   ├── LogGrid.jsx       # Canvas-based log sheet renderer
│   │   │   └── SummaryCards.jsx   # KPI dashboard cards
│   │   ├── index.css             # Global styles
│   │   └── main.jsx              # React entry point
│   ├── package.json
│   └── vite.config.js
│
├── vercel.json                   # Vercel build & routing configuration
├── .gitignore
└── README.md
```

---

## 🧪 Quick Test — Preset Routes

The UI includes built-in test presets to instantly run simulations:

| Preset | Route | Distance | What It Tests |
|---|---|---|---|
| **⚡ Coast to Coast** | New York → Chicago → Los Angeles | 2,800+ mi | 34h restarts, multiple 10h resets, 30m breaks, 1,000-mi fueling |
| **🚛 Midwest Run** | Chicago → St. Louis → Dallas | 950+ mi | 30m driving break, 10h sleeper reset mid-route |
| **🚀 Regional Haul** | Houston → Houston → Dallas | 240 mi | Clean single-day trip within 14h duty window |

---

## 🔮 Future Upgrades

### Near-Term
- **Multi-Stop Routes** — Support for multiple pickup and drop-off waypoints, not just a single pair
- **Editable Log Sheets** — Allow drivers to manually adjust duty status lines on the canvas and export corrected logs
- **PDF Export** — Generate downloadable PDF log books in addition to SVG sheets
- **Weather & Traffic Integration** — Factor in real-time weather and traffic conditions for more accurate ETAs
- **Driver Profiles** — Save and load driver profiles with persistent cycle history

### Mid-Term
- **Team Driving Mode** — Support for two-driver teams with split sleeper berth provisions
- **Split Sleeper Berth** — Implement the 7/3 split sleeper berth exception for more flexible rest scheduling
- **Adverse Driving Conditions** — Add the 2-hour driving extension for adverse conditions per FMCSA §395.1(b)(1)
- **Mobile-First PWA** — Progressive Web App support for tablet/phone use in the cab
- **Geofenced Alerts** — Notify the driver when approaching mandatory break/rest zones

### Long-Term
- **Django Admin Dashboard** — Full Django backend with user authentication, fleet management, and trip history database
- **Real-Time ELD Streaming** — WebSocket-based live duty status tracking for fleet managers
- **AI Route Optimization** — ML-powered route suggestions that minimize total trip time while maximizing HOS compliance
- **DOT Audit Report Generation** — Automated compliance report generation for DOT audits
- **Integration with TMS** — API connectors for popular Transportation Management Systems (TMSoft, McLeod, etc.)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <sub>Built with ❤️ for the trucking industry — compliant with <b>49 CFR Part 395</b></sub>
</p>

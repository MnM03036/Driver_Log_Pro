import json
import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import hos
import svg_generator



class handler(BaseHTTPRequestHandler):
    """
    Vercel Python Serverless Handler.
    Routes:
      POST /api/simulate/       → run HOS simulation, return JSON
      GET  /api/download-log/   → run simulation, return SVG for requested day
    """

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_svg(self, status: int, svg_content: str, filename: str = None):
        body = svg_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        self._send_json(status, {"error": message})

    def _read_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    # ── OPTIONS (CORS pre-flight) ─────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── POST /api/simulate/ ───────────────────────────────────────────────────
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path not in ("/api/simulate", "/api/simulate/"):
            self._send_error(404, "Not found")
            return

        data = self._read_body()

        current_loc  = data.get("current_location", "").strip()
        pickup_loc   = data.get("pickup_location", "").strip()
        dropoff_loc  = data.get("dropoff_location", "").strip()

        try:
            cycle_hours_used = float(data.get("cycle_hours_used", 0.0))
        except (TypeError, ValueError):
            self._send_error(400, "cycle_hours_used must be a valid number.")
            return

        if not current_loc or not pickup_loc or not dropoff_loc:
            self._send_error(
                400,
                "Missing required fields: current_location, pickup_location, dropoff_location."
            )
            return

        try:
            result = hos.simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_hours_used)
            self._send_json(200, result)
        except Exception as exc:
            traceback.print_exc()
            self._send_error(500, f"Simulation error: {str(exc)}")

    # ── GET /api/download-log/ ────────────────────────────────────────────────
    def do_GET(self):
        parsed   = urlparse(self.path)
        path     = parsed.path.rstrip("/")
        qs       = parse_qs(parsed.query)

        def qs_get(key, default=""):
            vals = qs.get(key, [default])
            return vals[0] if vals else default

        if path not in ("/api/download-log", "/api/download-log/"):
            self._send_error(404, "Not found")
            return

        current_loc  = qs_get("current_location")
        pickup_loc   = qs_get("pickup_location")
        dropoff_loc  = qs_get("dropoff_location")
        driver_name  = qs_get("driver_name", "John Doe")
        carrier      = qs_get("carrier_name", "Elite Logistics Inc.")
        vehicle_num  = qs_get("vehicle_num",  "TRK-9821")
        doc_num      = qs_get("doc_num",      "SHP-776102")
        should_dl    = qs_get("download", "false").lower() == "true"

        try:
            cycle_hours_used = float(qs_get("cycle_hours_used", "0.0"))
            day_num          = int(qs_get("day_number", "1"))
        except ValueError:
            self._send_error(400, "Invalid day_number or cycle_hours_used.")
            return

        if not current_loc or not pickup_loc or not dropoff_loc:
            self._send_error(400, "Missing required trip parameters.")
            return

        try:
            sim_data   = hos.simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_hours_used)
            daily_logs = sim_data.get("daily_logs", [])

            target_day = next((l for l in daily_logs if l["day_number"] == day_num), None)
            if not target_day:
                self._send_error(404, f"Day {day_num} not found. Total days: {len(daily_logs)}")
                return

            svg_content = svg_generator.generate_svg_log(target_day, driver_name, carrier, vehicle_num, doc_num)
            filename    = f"driver_log_day{day_num}_{target_day['date']}.svg" if should_dl else None
            self._send_svg(200, svg_content, filename)

        except Exception as exc:
            traceback.print_exc()
            self._send_error(500, f"Error generating log: {str(exc)}")

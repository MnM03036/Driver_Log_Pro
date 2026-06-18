import sys
import os

# Add api to sys.path so it can import hos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'api')))

from api.index import handler
from http.server import HTTPServer
import threading
import requests
import time

def run_server():
    server = HTTPServer(('127.0.0.1', 8081), handler)
    print("Server started on 8081")
    server.handle_request()

t = threading.Thread(target=run_server)
t.start()
time.sleep(1)

# Send request to test the handler
url = "http://127.0.0.1:8081/api/simulate/"
payload = {
    "current_location": "Houston, TX",
    "pickup_location": "Houston, TX",
    "dropoff_location": "Dallas, TX",
    "cycle_hours_used": 0
}

try:
    print(f"Sending POST to {url}")
    resp = requests.post(url, json=payload)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

t.join()

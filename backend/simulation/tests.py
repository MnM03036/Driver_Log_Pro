from django.test import TestCase
from datetime import datetime, timedelta
from .hos import DriverState, simulate_trip, interpolate_coordinate

class HOSTestCase(TestCase):
    def test_coordinate_interpolation(self):
        """
        Test that coordinate interpolation correctly handles fractions.
        """
        geometry = [[-118.2437, 34.0522], [-74.0060, 40.7128]] # LA to NY
        
        # At fraction 0, should be LA
        lat, lon = interpolate_coordinate(geometry, 0.0)
        self.assertAlmostEqual(lat, 34.0522, places=3)
        self.assertAlmostEqual(lon, -118.2437, places=3)
        
        # At fraction 1, should be NY
        lat, lon = interpolate_coordinate(geometry, 1.0)
        self.assertAlmostEqual(lat, 40.7128, places=3)
        self.assertAlmostEqual(lon, -74.0060, places=3)
        
        # At fraction 0.5, should be midpoint
        lat, lon = interpolate_coordinate(geometry, 0.5)
        self.assertAlmostEqual(lat, (34.0522 + 40.7128) / 2.0, places=2)
        self.assertAlmostEqual(lon, (-118.2437 - 74.0060) / 2.0, places=2)

    def test_short_trip_no_breaks(self):
        """
        Test a short trip that does not require any breaks or resets.
        """
        # LA to LA (very short simulated trip)
        result = simulate_trip(
            current_loc="Los Angeles, CA",
            pickup_loc="Los Angeles, CA",
            dropoff_loc="Los Angeles, CA",
            current_cycle_hours=10.0
        )
        
        self.assertIn("daily_logs", result)
        self.assertIn("markers", result)
        self.assertTrue(len(result["daily_logs"]) >= 1)
        
        # Odometer should be 0 because origin, pickup, dropoff are the same
        self.assertEqual(result["total_miles"], 0.0)
        
        # Check that there are no rest/break/restart markers
        marker_types = [m["type"] for m in result["markers"]]
        self.assertNotIn("rest", marker_types)
        self.assertNotIn("break", marker_types)
        self.assertNotIn("restart", marker_types)

    def test_hos_limits_trigger_breaks(self):
        """
        Test that driving > 8 hours triggers a 30-minute break,
        and driving > 11 hours (or duty window > 14 hours) triggers a 10-hour reset.
        """
        start_time = datetime(2026, 6, 18, 8, 0, 0)
        state = DriverState(start_time, initial_cycle_hours=20.0)
        
        # Simulate driving for 12 hours (720 minutes) continuous
        # This should trigger:
        # - A 30-minute break after 8 hours of driving (480 minutes)
        # - A 10-hour reset because 11 hours (660 minutes) of cumulative driving is reached
        
        geometry = [[-118.2437, 34.0522], [-74.0060, 40.7128]]
        
        from .hos import simulate_driving
        # total distance 1000 miles, duration 720 minutes
        simulate_driving(state, total_miles=1000.0, total_duration_mins=720, geometry=geometry, remarks="Driving Test")
        
        # Let's inspect events
        statuses = [e["status"] for e in state.events]
        remarks = [e["remarks"] for e in state.events]
        
        # Should have taken a 30-minute break
        self.assertIn("OFF", statuses)
        self.assertTrue(any("30-Min Rest Break" in r for r in remarks))
        
        # Should have taken a 10-hour reset
        self.assertIn("SB", statuses)
        self.assertTrue(any("10-Hour Reset (Daily Limit)" in r for r in remarks))
        
        # Verify markers
        marker_types = [m["type"] for m in state.markers]
        self.assertIn("break", marker_types)
        self.assertIn("rest", marker_types)

    def test_hos_cycle_restart(self):
        """
        Test that hitting 70 hours in 8 days triggers a 34-hour restart.
        """
        start_time = datetime(2026, 6, 18, 8, 0, 0)
        # Starting with 69.5 hours already used on the cycle
        state = DriverState(start_time, initial_cycle_hours=69.5)
        
        # Check current cycle hours
        self.assertAlmostEqual(state.get_cycle_hours_used(), 69.5)
        
        # Try to drive for 60 minutes
        geometry = [[-118.2437, 34.0522], [-74.0060, 40.7128]]
        from .hos import simulate_driving
        simulate_driving(state, total_miles=50.0, total_duration_mins=60, geometry=geometry, remarks="Driving Test")
        
        # Since we start with 69.5 hours used, driving 30 minutes should hit 70 hours and trigger a 34-hour restart
        statuses = [e["status"] for e in state.events]
        remarks = [e["remarks"] for e in state.events]
        
        self.assertIn("OFF", statuses)
        self.assertTrue(any("34-Hour Restart (Cycle Limit)" in r for r in remarks))
        
        # Verify cycle hours reset to 0 (or almost 0, since we reset history to [0.0]*8 and resume remaining drive)
        # After restart, cycle history is cleared. The remaining driving (after restart) adds a tiny bit to Day-0.
        self.assertTrue(state.get_cycle_hours_used() < 1.0)

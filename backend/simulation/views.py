from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .hos import simulate_trip
from .svg_generator import generate_svg_log

@api_view(["POST"])
def simulate_view(request):
    """
    Simulate the truck driver trip based on HOS rules and OSRM coordinates.
    """
    current_loc = request.data.get("current_location")
    pickup_loc = request.data.get("pickup_location")
    dropoff_loc = request.data.get("dropoff_location")
    
    cycle_hours_str = request.data.get("cycle_hours_used", "0.0")
    try:
        cycle_hours_used = float(cycle_hours_str)
    except ValueError:
        return Response(
            {"error": "cycle_hours_used must be a valid float value representing hours used."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if not current_loc or not pickup_loc or not dropoff_loc:
        return Response(
            {"error": "Missing required fields: current_location, pickup_location, and dropoff_location must be specified."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        result = simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_hours_used)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred during simulation: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET", "POST"])
def download_log_view(request):
    """
    Generate and download a daily driver log sheet as an SVG.
    """
    # Accept params from both GET and POST requests
    data = request.data if request.method == "POST" else request.GET
    
    current_loc = data.get("current_location")
    pickup_loc = data.get("pickup_location")
    dropoff_loc = data.get("dropoff_location")
    day_num_str = data.get("day_number", "1")
    cycle_hours_str = data.get("cycle_hours_used", "0.0")
    
    driver_name = data.get("driver_name", "John Doe")
    carrier = data.get("carrier_name", "Elite Logistics Inc.")
    vehicle_num = data.get("vehicle_num", "TRK-9821")
    doc_num = data.get("doc_num", "SHP-776102")
    
    try:
        cycle_hours_used = float(cycle_hours_str)
        day_num = int(day_num_str)
    except ValueError:
        return HttpResponse("Invalid day_number or cycle_hours_used parameter", status=400)
        
    if not current_loc or not pickup_loc or not dropoff_loc:
        return HttpResponse("Missing required trip parameters: current_location, pickup_location, dropoff_location", status=400)
        
    try:
        # Run simulation to get full logs
        simulation_data = simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_hours_used)
        daily_logs = simulation_data.get("daily_logs", [])
        
        # Find requested day
        target_day = None
        for log in daily_logs:
            if log["day_number"] == day_num:
                target_day = log
                break
                
        if not target_day:
            return HttpResponse(f"Day {day_num} not found in this simulation. Total days: {len(daily_logs)}", status=404)
            
        # Draw SVG log
        svg_content = generate_svg_log(target_day, driver_name, carrier, vehicle_num, doc_num)
        
        # Build Response
        response = HttpResponse(svg_content, content_type="image/svg+xml")
        
        # Set attachment headers if download is requested
        should_download = data.get("download", "false").lower() == "true"
        if should_download:
            filename = f"driver_log_day{day_num}_{target_day['date']}.svg"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            
        return response
    except Exception as e:
        return HttpResponse(f"Error generating log sheet: {str(e)}", status=500)

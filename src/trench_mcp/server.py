import os
import time
import requests
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(name="The Trench MCP Server")

# Configuration
TRENCH_API_URL = os.getenv("TRENCH_API_URL", "http://localhost:8000")
TRENCH_API_KEY = os.getenv("TRENCH_API_KEY", "")

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make authenticated request to Trench API"""
    url = f"{TRENCH_API_URL.rstrip('/')}/api{endpoint}"
    headers = {
        "Authorization": f"Bearer {TRENCH_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}
        
        response.raise_for_status()
        
        # Check if response has content before trying to parse JSON
        if not response.content:
            return {"error": f"Empty response from API endpoint {endpoint}"}
        
        try:
            return response.json()
        except ValueError as json_error:
            return {"error": f"Invalid JSON response from {endpoint}: {str(json_error)}. Response content: {response.text[:200]}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed for {url}: {str(e)}"}

# === SIMULATION STATE TOOLS ===

@mcp.tool()
def test_api_connection() -> str:
    """
    Test the connection to the Trench API server.
    Useful for debugging connectivity issues.
    """
    try:
        # Try a simple GET request to the time endpoint
        result = make_api_request("GET", "/time")
        if "error" in result:
            return f"Connection test failed: {result['error']}\n\nAPI URL: {TRENCH_API_URL}\nAPI Key configured: {'Yes' if TRENCH_API_KEY else 'No'}"
        else:
            return f"Connection test successful!\n\nAPI URL: {TRENCH_API_URL}\nCurrent simulation time: {result.get('sim_time_s', 'unknown')}s\nClock speed: {result.get('clock_speed', 'unknown')}x"
    except Exception as e:
        return f"Connection test failed with exception: {str(e)}\n\nAPI URL: {TRENCH_API_URL}"

@mcp.tool()
def get_current_time() -> str:
    """
    Get the current simulation time and real-world UTC time.
    """
    result = make_api_request("GET", "/time")
    if "error" in result:
        return f"Error: {result['error']}"
    
    return f"""Current Time Information:
- UTC Time: {result.get('current_time', 'Unknown')}
- ISO Time: {result.get('current_time_iso', 'Unknown')}
- Epoch Start: {result.get('epoch_utc', 'Unknown')}
- Clock Speed: {result.get('clock_speed', 1)}x real-time
"""

# === PASS MANAGEMENT TOOLS ===

@mcp.tool()
def get_all_passes() -> str:
    """
    Get information about all passes defined in the scenario.
    Shows complete schedule of satellite passes over the ground station.
    """
    result = make_api_request("GET", "/passes/all")
    if "error" in result:
        return f"Error: {result['error']}"
    
    passes = result.get('passes', [])
    total = result.get('total_count', 0)
    
    if not passes:
        return "No passes defined in scenario"
    
    output = f"All Passes ({total} total):\n"
    for i, p in enumerate(passes, 1):
        output += f"\nPass {i}:"
        output += f"\n  - AOS: {p.get('aos_utc', 'Unknown')}"
        output += f"\n  - LOS: {p.get('los_utc', 'Unknown')}"
        output += f"\n  - Duration: {p.get('duration_s', 0):.0f}s"
        output += f"\n  - Max Elevation: {p.get('max_elev_deg', 0)}°"
        output += f"\n  - Satellite: {p.get('sat_id', 'Unknown')}"
        output += f"\n  - Ground Station: {p.get('gs_id', 'Unknown')}"
    
    return output

@mcp.tool()
def get_next_pass() -> str:
    """
    Get information about the next upcoming satellite pass.
    Returns None if no future passes are scheduled.
    """
    result = make_api_request("GET", "/passes/next")
    if "error" in result:
        return f"Error: {result['error']}"
    
    if result.get('pass') is None:
        return result.get('message', 'No upcoming passes')
    
    p = result.get('pass')
    return f"""Next Pass:
- AOS: {p.get('aos_utc', 'Unknown')}
- LOS: {p.get('los_utc', 'Unknown')}
- Duration: {p.get('duration_s', 0):.0f} seconds
- Max Elevation: {p.get('max_elev_deg', 0)}°
- Satellite: {p.get('sat_id', 'Unknown')}
- Ground Station: {p.get('gs_id', 'Unknown')}
"""

# === TIMING AND WAITING TOOLS ===

@mcp.tool()
def wait_until_time(target_time_iso: str) -> str:
    """
    Wait until the simulation reaches a specific UTC time.
    Polls the simulation every 0.1 seconds until the target time is reached.
    
    Args:
        target_time_iso: Target UTC time in ISO format (e.g., "2025-09-15T17:30:00Z")
    """
    import datetime as dt
    
    try:
        # Parse the target ISO time
        if target_time_iso.endswith('Z'):
            target_time_iso = target_time_iso[:-1] + '+00:00'
        target_dt = dt.datetime.fromisoformat(target_time_iso)
        
        # Convert to UTC if not already
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=dt.timezone.utc)
        else:
            target_dt = target_dt.astimezone(dt.timezone.utc)
            
    except ValueError as e:
        return f"Error parsing target time '{target_time_iso}': {str(e)}"
    
    start_time = time.time()
    max_wait_seconds = 86400  # 1 day timeout
    
    while time.time() - start_time < max_wait_seconds:
        result = make_api_request("GET", "/time")
        if "error" in result:
            return f"Error checking time: {result['error']}"
        
        current_time_iso = result.get('current_time_iso')
        if not current_time_iso:
            return "Error: No current_time_iso in API response"
        
        try:
            # Parse current simulation time
            if current_time_iso.endswith('Z'):
                current_time_iso_fixed = current_time_iso[:-1] + '+00:00'
            else:
                current_time_iso_fixed = current_time_iso
            current_dt = dt.datetime.fromisoformat(current_time_iso_fixed)
            
            # Convert to UTC if not already
            if current_dt.tzinfo is None:
                current_dt = current_dt.replace(tzinfo=dt.timezone.utc)
            else:
                current_dt = current_dt.astimezone(dt.timezone.utc)
            
            # Check if we've reached the target time
            if current_dt >= target_dt:
                return f"Time has been reached"
                
        except ValueError as e:
            return f"Error parsing current time '{current_time_iso}': {str(e)}"
        
        time.sleep(0.1)  # Wait 0.1 seconds before checking again
    
    return f"Timeout waiting for UTC time {target_dt.isoformat()}Z"


# === DOWNLINK CONTROL TOOLS ===

@mcp.tool()
def start_downlink_simple() -> str:
    """
    Start a data downlink session with default parameters (no arguments required).
    Must be called during an active satellite pass.
    """
    result = make_api_request("POST", "/downlink/start")
    if "error" in result:
        return f"Error starting downlink: {result['error']}"
    
    if result.get('status') == 'success':
        bitrate = result.get('bitrate_kbps', 'unknown')
        return f"Downlink started successfully at {bitrate} kbps"
    else:
        return f"Failed to start downlink: {result.get('message', 'Unknown error')}"

@mcp.tool()
def stop_downlink_simple() -> str:
    """
    Stop the current data downlink session (no arguments required).
    Returns complete downlink status including total data downloaded.
    """
    # Get current status before stopping
    status_result = make_api_request("GET", "/downlink/status")
    if "error" in status_result:
        return f"Error getting downlink status: {status_result['error']}"
    
    # Stop the downlink
    stop_result = make_api_request("POST", "/downlink/stop")
    if "error" in stop_result:
        return f"Error stopping downlink: {stop_result['error']}"
    
    # Build comprehensive status report
    status_lines = [
        f"Downlink stopped: {stop_result.get('message', 'Success')}",
        "",
        "Final Downlink Status:",
        f"- Total Data Downloaded: {status_result.get('kb_downloaded_total', 0):.1f} KB",
        f"- Final Bitrate: {status_result.get('current_bitrate_kbps', 0)} kbps",
        f"- Was In Pass: {'Yes' if status_result.get('in_pass') else 'No'}"
    ]
    
    if status_result.get('downlink_start_time_s') is not None:
        duration = status_result.get('current_sim_time_s', 0) - status_result.get('downlink_start_time_s', 0)
        status_lines.extend([
            f"- Downlink Duration: {duration:.1f}s"
        ])
    
    if status_result.get('pass_info'):
        pass_info = status_result['pass_info']
        status_lines.extend([
            "",
            "Pass Information:",
            f"- Satellite: {pass_info.get('sat_id', 'Unknown')}",
            f"- Ground Station: {pass_info.get('gs_id', 'Unknown')}",
            f"- AOS: {pass_info.get('aos_s', 0):.1f}s",
            f"- LOS: {pass_info.get('los_s', 0):.1f}s",
            f"- Time Remaining: {pass_info.get('time_remaining_s', 0):.1f}s"
        ])
    
    return "\n".join(status_lines)

# @mcp.tool()
# def get_downlink_status() -> str:
#     """
#     Get current downlink status including whether we're downlinking and total data downloaded.
#     """
#     result = make_api_request("GET", "/downlink/status")
#     if "error" in result:
#         return f"Error: {result['error']}"
    
#     status_lines = [
#         f"Downlinking: {'Yes' if result.get('downlinking') else 'No'}",
#         f"In Pass: {'Yes' if result.get('in_pass') else 'No'}",
#         f"Total Data Downloaded: {result.get('kb_downloaded_total', 0):.1f} KB",
#         f"Current Bitrate: {result.get('current_bitrate_kbps', 0)} kbps",
#         f"Simulation Time: {result.get('current_sim_time_s', 0):.1f}s"
#     ]
    
#     if result.get('downlink_start_time_s') is not None:
#         status_lines.append(f"Downlink Started At: {result.get('downlink_start_time_s'):.1f}s")
    
#     if result.get('pass_info'):
#         pass_info = result['pass_info']
#         status_lines.extend([
#             f"Current Pass:",
#             f"  - Satellite: {pass_info.get('sat_id', 'Unknown')}",
#             f"  - Ground Station: {pass_info.get('gs_id', 'Unknown')}",
#             f"  - AOS: {pass_info.get('aos_s', 0):.1f}s",
#             f"  - LOS: {pass_info.get('los_s', 0):.1f}s",
#             f"  - Time Remaining: {pass_info.get('time_remaining_s', 0):.1f}s"
#         ])
    
#     return "\n".join(status_lines)

def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    print(f"Starting Trench MCP Server via transport: {transport}")
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()
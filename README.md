# The Trench MCP Server

MCP Server for controlling satellite ground station operations in the Trench simulation.

## Available Tools

### 🛰️ Simulation State Tools
- **`get_simulation_state()`** - Get comprehensive simulation state including satellite position, contact status, and timing
- **`get_current_time()`** - Get current simulation time and real-world UTC time  
- **`restart_simulation()`** - Restart simulation from beginning, resetting all state to epoch time

### 📡 Pass Management Tools  
- **`get_all_passes()`** - Get complete schedule of all satellite passes over ground station
- **`get_next_pass()`** - Get information about next upcoming satellite pass
- **`get_current_pass()`** - Get information about currently active satellite pass (if any)

### ⏰ Timing and Waiting Tools
- **`wait_until_time(target_sim_time)`** - Wait until simulation reaches specific time (seconds since epoch)
- **`wait_for_next_pass()`** - Wait until next satellite pass begins (AOS)

### 📥 Downlink Control Tools
- **`start_downlink(kb_requested, max_minutes=10)`** - Start data downlink session during active pass
- **`stop_downlink()`** - Stop current data downlink session

### 🎯 Ground Station Control Tools  
- **`get_ground_station_state(gs_id="DEMO-GS")`** - Get current antenna position and mode
- **`point_antenna(azimuth, elevation, gs_id="DEMO-GS")`** - Point antenna to specific angles
- **`track_satellite(sat_id="LEO-001", gs_id="DEMO-GS")`** - Start automatic satellite tracking
- **`stop_tracking(gs_id="DEMO-GS")`** - Stop satellite tracking, return to idle
- **`park_antenna(gs_id="DEMO-GS")`** - Park antenna in safe position

### 🏥 Health and Monitoring Tools
- **`get_satellite_health(sat_id="LEO-001")`** - Get satellite health and telemetry information

All tools use authenticated API calls with Bearer token authorization to interact with the Trench simulation API.

## Usage with Claude Desktop

To use this server with the Claude Desktop app, add the following configuration to the "mcpServers" section of your `claude_desktop_config.json`:

### Option 1: Direct installation from GitHub (Recommended)
```json
{
  "mcpServers": {
    "trench-mcp-server": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jasonmeverett/the-trench-mcp@main",
        "run-server"
      ],
      "env": {
        "TRENCH_API_URL": "https://the-trench.ml-2cba638a-03a.eng-ml-i.svbr-nqvp.int.cldr.work/",
        "TRENCH_API_KEY": "<apiv2 key>"
      }
    }
  }
}
```

### Transport

The MCP server's transport protocol is configurable via the `MCP_TRANSPORT` environment variable. Supported values:
- `stdio` **(default)** — communicate over standard input/output. Useful for local tools, command-line scripts, and integrations with clients like Claude Desktop.
- `http` - expose an HTTP server. Useful for web-based deployments, microservices, exposing MCP over a network.
- `sse` — use Server-Sent Events (SSE) transport. Useful for existing web-based deployments that rely on SSE.

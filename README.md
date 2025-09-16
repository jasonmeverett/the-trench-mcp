# The Trench MCP Server

MCP Server used in the Trench demo

(todo: list toools here)

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

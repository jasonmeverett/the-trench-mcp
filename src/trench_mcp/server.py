import os
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(name="Cloudera Iceberg MCP Server via Impala")


# Register functions as MCP tools
@mcp.tool()
def example_tool(query: str) -> str:
    """
    Execute a SQL query on the Impala database and return results as JSON.
    """
    return "example tool"

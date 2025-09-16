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


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    print(f"Starting Iceberg MCP Server via transport: {transport}")
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()
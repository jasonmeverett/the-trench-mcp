import os
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(name="The Trench MCP Server")


# Register functions as MCP tools
@mcp.tool()
def example_tool(query: str) -> str:
    """
    Simple Example Tool
    """
    return "example tool"


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    print(f"Starting Trench MCP Server via transport: {transport}")
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()
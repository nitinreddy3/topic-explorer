"""A thin wrapper around the MCP client so agent.py doesn't need to know
about session/transport plumbing directly — just "list tools" and "call a
tool by name," same as tools.py did in Project 4, except now the tools live
in a separate process (mcp_server.py) speaking a standard protocol.
"""

import sys
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])


@asynccontextmanager
async def mcp_session():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def list_tool_schemas(session: ClientSession, allowed: set[str] | None = None) -> list[dict]:
    """Convert MCP tool definitions into the tool-schema shape Ollama expects."""
    response = await session.list_tools()
    schemas = []
    for tool in response.tools:
        if allowed is not None and tool.name not in allowed:
            continue
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
        )
    return schemas


async def call_tool(session: ClientSession, name: str, arguments: dict) -> str:
    result = await session.call_tool(name, arguments)
    parts = [block.text for block in result.content if hasattr(block, "text")]
    return "\n".join(parts) if parts else ""

"""MCP server for Clash Verge (Mihomo) proxy management."""

import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import MihomoClient, MihomoError


server = Server("mcp-server-clash-verge")


def _client() -> MihomoClient:
    return MihomoClient()


# ═══════════════════════════════════════════════════════════════
# Tools
# ═══════════════════════════════════════════════════════════════

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_proxies",
            description="List all proxy groups and nodes with their types, current selection, and delay/latency. Use this to see available nodes before switching.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="switch_proxy",
            description="Switch a proxy group to a specific node. Use list_proxies first to see available groups and node names.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Proxy group name, e.g. 'Proxy', 'GLOBAL', 'Auto-Select'",
                    },
                    "node": {
                        "type": "string",
                        "description": "Node name to switch to. Must be one of the 'all' entries from list_proxies for that group.",
                    },
                },
                "required": ["group", "node"],
            },
        ),
        Tool(
            name="get_proxy_mode",
            description="Get the current proxy mode (rule, global, or direct).",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="set_proxy_mode",
            description="Set the proxy mode. 'rule' = route by rules, 'global' = all traffic through proxy, 'direct' = all traffic direct (no proxy).",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["rule", "global", "direct"],
                        "description": "Proxy mode to set.",
                    },
                },
                "required": ["mode"],
            },
        ),
        Tool(
            name="test_proxy_delay",
            description="Test the latency/delay of a specific proxy node or group. Returns delay in milliseconds.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Proxy node name or group name to test.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds (default: 3000).",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="reload_config",
            description="Force reload the Mihomo configuration file. Use after updating subscription or editing config manually.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_rules",
            description="List all routing rules (domain, IP, GEOIP, etc.) currently active in Mihomo.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    client = _client()
    try:
        result = await _handle_tool(client, name, arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except MihomoError as e:
        return [TextContent(type="text", text=f"Error: {e}")]
    finally:
        await client.close()


async def _handle_tool(client: MihomoClient, name: str, args: dict[str, Any]) -> Any:
    if name == "list_proxies":
        data = await client.get_proxies()
        # Summarize: show groups with their current node and available nodes + delay
        summary: dict[str, Any] = {}
        for key, val in data.get("proxies", {}).items():
            if val.get("type") in ("Selector", "URLTest", "Fallback", "LoadBalance"):
                nodes = []
                for n in val.get("all", []):
                    delay = data.get("proxies", {}).get(n, {}).get("history", [])
                    latest = delay[-1].get("delay", "N/A") if delay else "N/A"
                    nodes.append({"name": n, "delay_ms": latest})
                summary[key] = {
                    "type": val.get("type"),
                    "now": val.get("now"),
                    "nodes": nodes,
                }
        return {"proxy_groups": summary}

    elif name == "switch_proxy":
        await client.switch_proxy(args["group"], args["node"])
        return {"ok": True, "group": args["group"], "node": args["node"]}

    elif name == "get_proxy_mode":
        configs = await client.get_configs()
        return {"mode": configs.get("mode", "unknown")}

    elif name == "set_proxy_mode":
        await client.patch_configs({"mode": args["mode"]})
        return {"ok": True, "mode": args["mode"]}

    elif name == "test_proxy_delay":
        timeout = args.get("timeout", 3000)
        result = await client.test_delay(args["name"], timeout=timeout)
        return {"name": args["name"], "delay_ms": result.get("delay", "N/A")}

    elif name == "reload_config":
        await client.reload_config()
        return {"ok": True, "message": "Config reloaded"}

    elif name == "list_rules":
        data = await client.get_rules()
        rules = []
        for r in data.get("rules", []):
            rules.append({
                "type": r.get("type"),
                "payload": r.get("payload"),
                "proxy": r.get("proxy"),
            })
        return {"rules": rules[:50], "total": len(rules)}

    else:
        return {"error": f"Unknown tool: {name}"}


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

def main():
    import asyncio
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()

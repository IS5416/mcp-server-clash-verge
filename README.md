# mcp-server-clash-verge

MCP (Model Context Protocol) server for Clash Verge / Mihomo (Clash Meta). Lets Claude Code and other MCP-compatible AI agents control your proxy — switch nodes, change modes, reload config, test latency — directly from conversation.

[中文文档](README_ZH.md)

## Why

When Claude Code hits network errors behind a proxy, you don't want to switch to the Clash Verge GUI, find a faster node, then tell Claude "try again." You want Claude to fix it itself.

This MCP server gives Claude 7 tools to manage your Mihomo proxy autonomously.

## Requirements

- [Clash Verge](https://github.com/clash-verge-rev/clash-verge-rev) (or any Mihomo-based client) with **External Controller** enabled
- Python ≥ 3.10

## Quick Start

### 1. Enable External Controller in Clash Verge

Settings → Clash Field → ☑ External Controller

Default: `http://127.0.0.1:9090` with secret `set-your-secret`.

### 2. Install

```bash
pip install mcp-server-clash-verge
```

Or from source:

```bash
git clone https://github.com/neo/mcp-server-clash-verge.git
cd mcp-server-clash-verge
pip install -e .
```

### 3. Configure Claude Code

Add to your Claude Code `settings.json`:

```json
{
  "mcpServers": {
    "clash-verge": {
      "command": "python",
      "args": ["-m", "mcp_server_clash_verge"],
      "env": {
        "MIHOMO_API_URL": "http://127.0.0.1:9097",
        "MIHOMO_API_SECRET": "set-your-secret"
      }
    }
  }
}
```

After PyPI publication, use the shorter form:

```json
{
  "mcpServers": {
    "clash-verge": {
      "command": "uvx",
      "args": ["mcp-server-clash-verge"],
      "env": {
        "MIHOMO_API_URL": "http://127.0.0.1:9090",
        "MIHOMO_API_SECRET": "your-secret"
      }
    }
  }
}
```

Restart Claude Code.

### 4. Try It

> "List all my proxy nodes."  
> "Switch to HK-01."  
> "I'm getting network errors, find a fast node and switch to it."

## Tools

| Tool | Description |
|------|-------------|
| `list_proxies` | All proxy groups, nodes, current selection, and delay |
| `switch_proxy` | Switch a proxy group to a specific node |
| `get_proxy_mode` | Current mode: rule / global / direct |
| `set_proxy_mode` | Set mode: rule / global / direct |
| `test_proxy_delay` | Test latency of a specific node (milliseconds) |
| `reload_config` | Force reload Mihomo configuration from disk |
| `list_rules` | Show active routing rules |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MIHOMO_API_URL` | `http://127.0.0.1:9090` | Mihomo external controller address |
| `MIHOMO_API_SECRET` | `""` | API secret from Clash Verge settings |

## License

MIT

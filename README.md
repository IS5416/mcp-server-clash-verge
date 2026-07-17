# mcp-server-clash-verge

MCP (Model Context Protocol) server for [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) / Mihomo (Clash Meta). Lets Claude Code and other MCP-compatible AI agents control your proxy — switch nodes, change modes, reload config, test latency — directly from conversation.

[中文文档](README_ZH.md)

## One-Click Install

**Tell Claude Code this one sentence:**

> Help me install https://raw.githubusercontent.com/IS5416/mcp-server-clash-verge/main/SETUP.md

Claude will auto-detect your platform, install the package, configure `~/.claude.json`, and verify everything. **No manual steps. No environment variables.** Restart Claude Code and you're done.

## Why

When Claude Code hits network errors behind a proxy, you don't want to switch to the Clash Verge GUI, find a faster node, then tell Claude "try again." You want Claude to fix it itself.

This MCP server gives Claude 7 tools to manage your Mihomo proxy autonomously.

## Requirements

- [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) (or any Mihomo-based client) with **External Controller** enabled
- Python ≥ 3.10

## Manual Install

### 1. Install the package

```bash
pip install mcp-server-clash-verge
```

Or from source:

```bash
git clone https://github.com/IS5416/mcp-server-clash-verge.git
cd mcp-server-clash-verge
pip install -e .
```

### 2. Configure Claude Code

Edit `~/.claude.json` and add to the `mcpServers` object:

```json
"clash-verge": {
  "command": "python",
  "args": ["-m", "mcp_server_clash_verge"],
  "env": {},
  "type": "stdio"
}
```

If you have `uv` installed:

```json
"clash-verge": {
  "command": "uvx",
  "args": ["mcp-server-clash-verge"],
  "env": {},
  "type": "stdio"
}
```

**No `env` block needed.** The MCP server auto-detects Clash Verge Rev's configuration file on Windows, macOS, and Linux.

Restart Claude Code.

### 3. Try It

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

## Configuration

**Zero config by default.** The server auto-detects Clash Verge Rev on all platforms:

| Platform | Config path |
|----------|------------|
| Windows | `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\config.yaml` |
| macOS | `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml` |
| Linux | `~/.config/io.github.clash-verge-rev.clash-verge-rev/config.yaml` |

### Override (optional)

Set environment variables in `~/.claude.json` if you use a non-standard Clash client:

```json
"clash-verge": {
  "command": "python",
  "args": ["-m", "mcp_server_clash_verge"],
  "env": {
    "MIHOMO_API_URL": "http://127.0.0.1:9097",
    "MIHOMO_API_SECRET": "your-secret"
  },
  "type": "stdio"
}
```

| Variable | Default | Description |
|----------|---------|-------------|
| `MIHOMO_API_URL` | auto-detected | Mihomo external controller address |
| `MIHOMO_API_SECRET` | auto-detected | API secret from Clash Verge settings |

## Use Cases

- Claude Code hits proxy timeout during web scraping/search → automatically switch to a low-latency node and retry
- Need temporary global proxy → `set_proxy_mode global`, switch back to rule mode when done
- After subscription update → `reload_config` to refresh without touching the GUI
- Debug routing issues → `list_rules` to check current rules match expectations

## Security

- The MCP server communicates with Claude Code exclusively via `stdio` — it opens no network ports
- Mihomo API secret is read from your Clash Verge config file, never hardcoded or logged
- All operations are local to your Mihomo instance — no data is sent externally

## License

MIT

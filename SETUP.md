# SETUP: mcp-server-clash-verge

> This file is designed to be executed by Claude Code.  
> A user simply says: "Help me install https://raw.githubusercontent.com/IS5416/mcp-server-clash-verge/main/SETUP.md"  
> and Claude Code handles the rest.

## For Claude Code Agent

Read all instructions below and execute them step by step. Prefer the uvx method if the `uv` tool is installed.

### Step 1: Detect platform and Python

- Check Python version: `python --version` or `python3 --version` (needs ≥ 3.10)
- Check if `uv` is installed: `uv --version`
- Check if Clash Verge is running: verify `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\config.yaml` exists on Windows, `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml` on macOS, or `~/.config/io.github.clash-verge-rev.clash-verge-rev/config.yaml` on Linux.

### Step 2: Install the package

**If uv is available (recommended):**

Skip installation — uvx handles it automatically in Step 3.

**If only pip is available:**

```bash
pip install mcp-server-clash-verge
```

**If not yet on PyPI (git install):**

```bash
pip install git+https://github.com/IS5416/mcp-server-clash-verge.git
```

### Step 3: Configure Claude Code

Create or update `~/.claude/.mcp.json` (user-global MCP config).

**Path:**
- Linux/macOS: `~/.claude/.mcp.json`
- Windows: `%USERPROFILE%\.claude\.mcp.json`

**If uvx is available, write:**
```json
{
  "mcpServers": {
    "clash-verge": {
      "command": "uvx",
      "args": ["mcp-server-clash-verge"]
    }
  }
}
```

**If only python + pip is available, write:**
```json
{
  "mcpServers": {
    "clash-verge": {
      "command": "python",
      "args": ["-m", "mcp_server_clash_verge"]
    }
  }
}
```

If the `.mcp.json` file already has other servers, merge the `clash-verge` entry into `mcpServers` — do NOT overwrite other entries.

### Step 4: Verify

Run the auto-detect check:

```bash
python -c "from mcp_server_clash_verge.client import MihomoClient; import asyncio; asyncio.run(MihomoClient().get_configs()); print('OK')"
```

If this prints `OK`, the setup is working. Clash Verge config was auto-detected.

### Step 5: Tell the user

Say:
> mcp-server-clash-verge is installed and configured.  
> **Restart Claude Code** (quit and reopen) to activate the MCP tools.  
> After restart, try: "列出所有代理节点" or "List all my proxy nodes."

---

## Notes

- **No environment variables needed.** The MCP server auto-detects Clash Verge Rev's config file on all 3 platforms.
- If auto-detection fails (non-standard Clash client), set `MIHOMO_API_URL` and `MIHOMO_API_SECRET` in the `.mcp.json` `env` block.
- The MCP server talks to Mihomo via `stdio` — no network ports opened.

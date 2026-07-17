# mcp-server-clash-verge

MCP (Model Context Protocol) 服务器，用于 [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) / Mihomo (Clash Meta)。让 Claude Code 及其他支持 MCP 的 AI Agent 可以直接控制代理 — 切换节点、修改模式、重载配置、测试延迟 — 全部在对话中完成。

## 一键安装

**对 Claude Code 说一句话：**

> 帮我安装 https://raw.githubusercontent.com/IS5416/mcp-server-clash-verge/main/SETUP.md

Claude 会自动检测你的平台、安装包、创建配置、验证一切。**无需手动操作。无需配置环境变量。** 重启 Claude Code 即可使用。

## 为什么需要

Claude Code 在代理背后遇到网络错误时，你不想切换到 Clash Verge GUI 手动找节点，再告诉 Claude "再试一次"。你希望 Claude 自己修。

这个 MCP 服务器给 Claude 7 个工具，让它自主管理你的 Mihomo 代理。

## 环境要求

- [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev)（或其他基于 Mihomo 的客户端），已启用 **外部控制器**
- Python ≥ 3.10

## 手动安装

### 1. 安装包

```bash
pip install mcp-server-clash-verge
```

或从源码安装：

```bash
git clone https://github.com/IS5416/mcp-server-clash-verge.git
cd mcp-server-clash-verge
pip install -e .
```

### 2. 配置 Claude Code

创建或更新 `~/.claude/.mcp.json`：

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

PyPI 发布后可用更简洁的形式：

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

**无需 `env` 字段。** MCP server 会自动检测 Clash Verge Rev 在 Windows、macOS、Linux 上的配置文件。

重启 Claude Code。

### 3. 试试看

> "列出所有代理节点。"  
> "切换到 HK-01。"  
> "网络又出错了，帮我找一个延迟低的节点切过去。"

## 工具说明

| 工具 | 功能 | 对应 Mihomo API |
|------|------|----------------|
| `list_proxies` | 列出所有代理组、节点、当前选择、延迟 | `GET /proxies` |
| `switch_proxy` | 切换代理组到指定节点 | `PUT /proxies/{group}` |
| `get_proxy_mode` | 查看当前模式 (rule/global/direct) | `GET /configs` |
| `set_proxy_mode` | 设置模式 (rule/global/direct) | `PATCH /configs` |
| `test_proxy_delay` | 测试指定节点延迟 (毫秒) | `GET /proxies/{name}/delay` |
| `reload_config` | 强制重载配置文件 | `PUT /configs?force=true` |
| `list_rules` | 显示当前路由规则 | `GET /rules` |

## 配置方式

**默认零配置。** 服务器自动检测 Clash Verge Rev 的配置文件：

| 平台 | 配置路径 |
|------|---------|
| Windows | `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\config.yaml` |
| macOS | `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml` |
| Linux | `~/.config/io.github.clash-verge-rev.clash-verge-rev/config.yaml` |

### 手动覆盖（可选）

如果你使用非标准 Clash 客户端，可在 `.mcp.json` 中设置环境变量：

```json
{
  "mcpServers": {
    "clash-verge": {
      "command": "python",
      "args": ["-m", "mcp_server_clash_verge"],
      "env": {
        "MIHOMO_API_URL": "http://127.0.0.1:9097",
        "MIHOMO_API_SECRET": "your-secret"
      }
    }
  }
}
```

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `MIHOMO_API_URL` | 自动检测 | Mihomo 外部控制器地址 |
| `MIHOMO_API_SECRET` | 自动检测 | Clash Verge 设置中的 API secret |

## 适用场景

- Claude Code 网页爬取/搜索时代理超时 → 自动切换到低延迟节点重试
- 需要临时全局代理 → `set_proxy_mode global`，用完后切回规则模式
- 更新订阅后 → `reload_config` 刷新配置，无需手动点
- 排查路由问题 → `list_rules` 查看当前规则是否匹配预期

## 安全说明

- 本服务仅通过 stdio 与 Claude Code 通信，不暴露任何网络端口
- Mihomo API secret 自动从 Clash Verge 配置文件读取，不出现在代码或日志中
- 所有操作仅影响本地 Mihomo 实例，不会向外发送数据

## License

MIT

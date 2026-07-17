# mcp-server-clash-verge

MCP (Model Context Protocol) 服务器，用于 Clash Verge / Mihomo (Clash Meta)。让 Claude Code 及其他支持 MCP 的 AI Agent 可以直接控制代理 —— 切换节点、修改模式、重载配置、测试延迟 —— 全部在对话中完成。

## 为什么需要

Claude Code 在代理背后遇到网络错误时，你不想切换到 Clash Verge GUI 手动找节点，再告诉 Claude "再试一次"。你希望 Claude 自己修。

这个 MCP 服务器给 Claude 7 个工具，让它自主管理你的 Mihomo 代理。

## 环境要求

- [Clash Verge](https://github.com/clash-verge-rev/clash-verge-rev)（或其他基于 Mihomo 的客户端），已启用 **外部控制器**
- Python ≥ 3.10

## 快速开始

### 1. 在 Clash Verge 中启用外部控制器

设置 → Clash 字段 → ☑ 外部控制器

默认地址：`http://127.0.0.1:9090`，secret 默认为 `set-your-secret`。

### 2. 安装

```bash
pip install mcp-server-clash-verge
```

或从源码安装：

```bash
git clone https://github.com/neo/mcp-server-clash-verge.git
cd mcp-server-clash-verge
pip install -e .
```

### 3. 配置 Claude Code

在 Claude Code 的 `settings.json` 中添加：

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

PyPI 发布后可用更简洁的形式：

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

重启 Claude Code。

### 4. 试试看

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

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `MIHOMO_API_URL` | `http://127.0.0.1:9090` | Mihomo 外部控制器地址 |
| `MIHOMO_API_SECRET` | `""` | Clash Verge 设置中的 API secret |

## 适用场景

- Claude Code 网页爬取/搜索时代理超时 → 自动切换到低延迟节点重试
- 需要临时全局代理 → `set_proxy_mode global`，用完后切回规则模式
- 更新订阅后 → `reload_config` 刷新配置，无需手动点
- 排查路由问题 → `list_rules` 查看当前规则是否匹配预期

## 安全说明

- 本服务仅通过 stdio 与 Claude Code 通信，不暴露任何网络端口
- Mihomo API secret 通过环境变量传入，不会出现在代码或日志中
- 所有操作仅影响本地 Mihomo 实例，不会向外发送数据

## License

MIT

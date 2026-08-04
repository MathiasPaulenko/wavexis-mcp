<!-- mcp-name: io.github.MathiasPaulenko/wavexis-mcp -->

<p align="center">
  <img src="docs/assets/images/logo-wide.svg" alt="WaveXisMCP" width="480">
</p>

<h3 align="center">面向 LLM 的 MCP 服务器 — 220 个浏览器自动化工具</h3>

<p align="center">
  <strong>Chrome + Firefox · CDP + BiDi · 100% Python · 无需 Node.js · 无需下载 Chromium</strong>
</p>

---

[English](README.md) | **简体中文** | [日本語](README.ja.md)

[![CI](https://github.com/MathiasPaulenko/wavexis-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wavexis-mcp.svg)](https://pypi.org/project/wavexis-mcp/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/wavexis-mcp.svg)](https://pypi.org/project/wavexis-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/wavexis-mcp.svg)](https://pypi.org/project/wavexis-mcp/)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-blue.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/pkgs/container/wavexis-mcp)
[![License](https://img.shields.io/github/license/MathiasPaulenko/wavexis-mcp.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://mathiaspaulenko.github.io/wavexis-mcp/)
[![smithery badge](https://smithery.ai/badge/mathias-paulenko/wavexis-mcp)](https://smithery.ai/servers/mathias-paulenko/wavexis-mcp)

> 将 [wavexis](https://github.com/MathiasPaulenko/wavexis) 浏览器自动化库以 MCP 服务器形式提供给 LLM。共 220 个工具，分属 13 个功能层级。无需 Node.js，无需下载 Chromium — 直接使用本机已安装的 Chrome/Edge。100% Python。

## 快速演示

**30 秒完成第一次截图。** 将以下内容添加到你的 MCP 客户端配置（Claude Desktop、Cursor、Windsurf、VS Code）：

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "all"]
    }
  }
}
```

然后对你的 LLM 说：

> *"请对 https://example.com 截取整页截图"*

LLM 会调用 `wavexis_screenshot(url="https://example.com", full_page=true)` 并返回截图。无需 Node.js，无需下载 Chromium，除上述配置外无需其他设置。

## 为什么选择 WaveXisMCP？

WaveXisMCP 封装了 [wavexis](https://github.com/MathiasPaulenko/wavexis) 浏览器自动化库，并以 [MCP 服务器](https://modelcontextprotocol.io/) 的形式对外暴露。你不需要 Node.js、Playwright，也不需要单独下载 Chromium — WaveXisMCP 会直接启动本机已安装的 Chrome 或 Edge。

### 主要特性

- **220 个工具** — 比 Playwright MCP（21）多 3 倍，比 zendriver-mcp（96）多 2 倍
- **13 个功能层级** — 通过 `--caps` 按需启用。从 `core`（72 个工具）开始，再按需要追加层级
- **Chrome + Firefox** — Chrome/Edge 使用 CDP，Firefox 使用 BiDi。两者都会从 PATH 自动启动对应驱动
- **无需下载 Chromium** — 使用本机浏览器。安装体积约 5MB，而 Playwright MCP 约 400MB
- **隐身模式** — `stealth=true` 可隐藏 `navigator.webdriver`，并伪造 plugins、languages 与 chrome runtime
- **结构化错误** — 每个错误都包含 `suggestion` 字段，便于 LLM 在无人干预下自我纠正
- **多动作 YAML** — 在一次工具调用中串联 navigate → click → fill → screenshot
- **直接 CDP/BiDi 访问（逃生舱）** — 覆盖尚未提供专用工具的浏览器功能
- **Lighthouse 审计、WebAuthn、Bluetooth、Cast** — 其他 MCP 服务器通常不具备的小众能力
- **SSRF 防护、路径沙盒、速率限制** — 从第一天起就内置安全机制
- **593 项测试、强制 90% 覆盖率、真实 Chrome 的 E2E** — 可直接用于生产环境

### 工作原理

```text
你（自然语言）
  → LLM 决定调用哪个工具
    → WaveXisMCP 接收工具调用
      → wavexis 库通过 CDP 或 BiDi 执行
        → Chrome/Edge/Firefox 执行操作
      ← 以 JSON 返回结果（文本、base64、文件路径）
    ← JSON 回传给 LLM
  ← LLM 为你总结结果
```

LLM 不会直接看到浏览器。它只能看到工具定义（名称、描述、参数）以及 JSON 响应。因此，任何兼容 MCP 的 LLM 客户端都能开箱即用，无需定制集成。

### 核心概念

- **工具（Tool）** — 单个浏览器操作（截图、eval、点击等），以 MCP 工具形式暴露，供任意 LLM 客户端调用。
- **会话（Session）** — 持久化的浏览器实例。打开会话后可连续发起多次工具调用，完成后再关闭，避免每次操作都重新启动浏览器。
- **无状态模式（Stateless）** — 调用任意工具时传入 `url` 参数。浏览器会自动启动、执行并关闭。
- **功能层级（Capability tiers）** — 从 `core`（72 个工具）到 `all`（220 个工具）共 13 个层级。通过 `--caps` 按需启用。
- **双后端（Dual backend）** — CDP（基于 Chromium，经由 cdpwave）与 BiDi（W3C 跨浏览器，经由 bidiwave），可按会话选择。
- **结构化错误（Structured errors）** — 每个错误都包含 `suggestion` 字段，告诉 LLM 下一步该做什么，从而实现无人干预的自我纠正。

## 安装

```bash
pip install wavexis-mcp
```

启用 CDP 后端（Chromium）：

```bash
pip install "wavexis-mcp[cdp]"
```

或不安装直接运行（推荐）：

```bash
uvx wavexis-mcp
```

## 环境要求

- **Python**：3.11、3.12 或 3.13
- **浏览器**：Google Chrome、Microsoft Edge，或任意基于 Chromium/Chrome 的浏览器
- **BiDi 后端**（可选）：Chrome 需 ChromeDriver/EdgeDriver，Firefox 需 geckodriver

## 快速开始

添加到你的 MCP 客户端配置（Claude Desktop、Cursor、Windsurf、VS Code）：

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "all"]
    }
  }
}
```

或使用 pip：

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "wavexis-mcp",
      "args": ["--caps", "all"]
    }
  }
}
```

### 无状态模式（一次性）

调用任意工具时传入 `url` 参数 — 浏览器会自动启动、执行并关闭：

```text
wavexis_screenshot(url="https://example.com", full_page=true)
```

### 会话模式（多步骤）

打开会话，串联多个动作，完成后关闭：

```text
wavexis_session_open(backend="cdp", headless=false)
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_click(session_id="abc-123", selector="#login")
wavexis_screenshot(session_id="abc-123")
wavexis_session_close(session_id="abc-123")
```

### 自然语言交互（M1）

使用 `wavexis_act`，通过自然语言与页面交互：

```text
wavexis_session_open(backend="cdp")
wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_act(session_id="abc-123", instruction="click the login button")
→ {"action": "click", "element": {"ref": "el-3", "role": "button", "name": "Login"}, "status": "ok"}
```

`wavexis_act` 工具会获取 a11y 快照，通过关键词打分将指令匹配到元素，并执行检测到的动作（click、type、fill、hover）。不调用外部 LLM — 纯启发式匹配。

## 功能层级

| 层级 | 标志 | 工具数 | 主要功能 |
|------|------|-------|--------------|
| **Core** | 始终启用 | 72 | 会话、导航、截图、PDF、爬取、eval、DOM、输入、cookies、标签页、自然语言交互、iframe、shadow DOM、事件 |
| **Network** | `--caps=network` | 20 | 请求头、UA、拦截、限速、缓存、HAR、intercept、mock、修改请求/响应、请求体、重放 HAR、请求列表 |
| **Storage** | `--caps=storage` | 18 | localStorage、sessionStorage、cache storage、IndexedDB、状态保存/恢复 |
| **Emulation** | `--caps=emulation` | 9 | 设备、视口、地理位置、时区、深色模式、语言区域、CPU、触摸、传感器 |
| **A11y** | `--caps=a11y` | 4 | 无障碍树快照、节点遍历、axe-core 审计 |
| **Interactions** | `--caps=interactions` | 5 | 对话框、下载、权限 |
| **DevTools** | `--caps=devtools` | 31 | 性能、CSS、调试、overlay、控制台、安全、窗口管理、组合 trace、带标注截图 |
| **Vision** | `--caps=vision` | 7 | 基于坐标的鼠标操作（像素级精确） |
| **Video** | `--caps=video` | 4 | 视频录制、章节、动作叠加层 |
| **Testing** | `--caps=testing` | 6 | 断言、定位器生成 |
| **Workflows** | `--caps=workflows` | 6 | 多动作 YAML、直接 CDP/BiDi、浏览器上下文 CRUD |
| **Data** | `--caps=data` | 7 | Codegen、Lighthouse 审计、抽取、WebSocket 拦截、爬取、视觉对比、Core Web Vitals |
| **Experimental** | `--caps=experimental` | 31 | Service workers、动画、WebAuthn、WebAudio、媒体、cast、bluetooth、扩展、偏好设置 |
| **合计** | `--caps=all` | **220** | |

**默认**：`--caps=core`（72 个工具）。启用全部：`--caps=all`。启用指定层级：`--caps=network,storage,emulation`。

> **提示**：建议从 `--caps core` 开始，再按需追加层级。每个层级都会把工具定义加入 LLM 的上下文，从而消耗 token。对大多数任务而言，`core,network,storage`（110 个工具）是较好的平衡点。

## 后端

WaveXisMCP 支持两种后端，并保持完整功能对等：

- **CDP**（cdpwave）— 默认后端，Chrome DevTools Protocol。通过 WebSocket 直连 Chrome/Edge。无需驱动。覆盖 57 个 CDP 域。`pip install "wavexis-mcp[cdp]"`
- **BiDi**（bidiwave）— WebDriver BiDi 协议，W3C 跨浏览器（Firefox、Chrome）。Chrome 需要 chromedriver，Firefox 需要 geckodriver；若尚未运行，两者都会从 PATH 自动启动。`pip install "wavexis-mcp[bidi]"`

按会话选择：

```text
# CDP (default, Chrome/Edge only)
wavexis_session_open(backend="cdp")

# BiDi with Chrome (auto-launches chromedriver)
wavexis_session_open(backend="bidi", browser="chrome")

# BiDi with Firefox (auto-launches geckodriver)
wavexis_session_open(backend="bidi", browser="firefox")
```

### 连接到已有 Chrome

使用 `connect_existing=True`，以 `--remote-debugging-port` 启动 Chrome 并连接到它。适合复用已登录的浏览器配置文件：

```text
# Launch Chrome with debug port and connect via CDP
wavexis_session_open(connect_existing=true)

# Reuse an existing Chrome profile (keeps logins, cookies, extensions)
wavexis_session_open(connect_existing=true, user_data_dir="C:/Users/me/ChromeProfile")
```

Chrome 会以有头模式启动（headless 会被忽略）。会话关闭时，浏览器子进程也会一并终止。

## 多动作 YAML

通过传入 YAML 字符串，在一次工具调用中串联多个动作：

```text
wavexis_multi_action(
    config="""
actions:
  - navigate: https://example.com
  - screenshot:
      full_page: true
  - eval: document.title
  - click: "#login"
  - type:
      selector: "#username"
      text: admin@example.com
  - screenshot: {}
""",
    session_id="abc-123"
)
```

支持的动作类型：`navigate`、`screenshot`、`eval`、`click`、`type`、`fill`。设置 `continue_on_error: true` 可在失败后继续执行。

## MCP 资源与提示词（M3）

**资源（Resources）**（只读浏览器状态）：

- `wavexis://session/{id}/url` — 当前页面 URL
- `wavexis://session/{id}/cookies` — cookies（JSON）
- `wavexis://session/{id}/console` — 控制台消息
- `wavexis://session/{id}/tabs` — 已打开的标签页

**提示词（Prompts）**（工作流模板）：

- `scrape_page(url, selector)` — 爬取并提取内容
- `audit_page(url)` — 完整的 a11y + 性能审计
- `fill_form(url, fields)` — 填写页面表单
- `debug_page(url)` — 调试控制台、网络与性能

## HTTP 传输

将 WaveXisMCP 作为 HTTP 服务器运行，适用于 CI/CD、共享实例或 Docker：

```bash
# HTTP on localhost
wavexis-mcp --transport http --port 8765

# HTTP with all tiers
wavexis-mcp --transport http --port 8765 --caps all

# HTTP with remote access (use behind a reverse proxy!)
wavexis-mcp --transport http --allow-remote --port 8765
```

默认绑定到 `127.0.0.1`。使用 `--allow-remote` 可绑定到 `0.0.0.0`。

## 速率限制（M4）

按会话的令牌桶速率限制：

```bash
# 10 calls/sec, burst of 5
wavexis-mcp --rate-limit 10 --rate-burst 5
```

超限时返回 `{"error": "rate_limited", "retry_after_ms": N}`。

## Docker

```bash
# Pull and run
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp

# Or build locally
docker build -t wavexis-mcp .
docker run -p 8765:8765 wavexis-mcp

# Docker Compose
docker-compose up
```

详见 [Docker 文档](https://mathiaspaulenko.github.io/wavexis-mcp/docker/)。

## 对比

| 功能 | Playwright MCP | **WaveXisMCP** |
|---------|:---:|:---:|
| 语言 | TypeScript | **Python** |
| 是否需要 Node.js | ✗ | **✓（无需 Node.js）** |
| 是否下载 Chromium（约 200MB） | ✓ | **✗（使用本机浏览器）** |
| 安装体积 | ~400MB | **~5MB** |
| 冷启动 | 3.2s | **0.8s** |
| 工具总数 | ~21 | **220** |
| 功能层级（按需启用） | ✗ | **✓（13 个层级）** |
| 双协议（CDP + BiDi） | ✗ | **✓** |
| Firefox 支持 | ✓（基础） | **✓（BiDi + geckodriver 自动启动）** |
| 后端选择（按会话） | ✗ | **✓** |
| 隐身 / 反爬模式 | ✗ | **✓** |
| 直接 CDP/BiDi 访问 | ✗ | **✓（逃生舱）** |
| 多动作 YAML 批处理 | ✗ | **✓** |
| 视频录制 | ✗ | **✓** |
| Lighthouse 审计 | ✗ | **✓** |
| WebAuthn / Bluetooth / Cast | ✗ | **✓** |
| 自然语言交互 | ✗ | **✓（`wavexis_act`）** |
| MCP 资源与提示词 | ✗ | **✓** |
| 速率限制 | ✗ | **✓** |
| SSRF 防护 | ✗ | **✓** |
| 带建议的结构化错误 | ✗ | **✓** |

> **说明**：Playwright MCP 支持 WebKit（Safari）— WaveXisMCP 目前尚不支持。计划功能请参见 [路线图](https://github.com/MathiasPaulenko/wavexis-mcp/issues)。

## 文档

完整文档、API 参考与示例托管于 [mathiaspaulenko.github.io/wavexis-mcp](https://mathiaspaulenko.github.io/wavexis-mcp/)。

主要章节：

- [快速开始](https://mathiaspaulenko.github.io/wavexis-mcp/quickstart/)
- [架构](https://mathiaspaulenko.github.io/wavexis-mcp/architecture/)
- [配置](https://mathiaspaulenko.github.io/wavexis-mcp/configuration/)
- [Docker](https://mathiaspaulenko.github.io/wavexis-mcp/docker/)
- [HTTP 传输](https://mathiaspaulenko.github.io/wavexis-mcp/http-transport/)
- [速率限制](https://mathiaspaulenko.github.io/wavexis-mcp/rate-limiting/)
- [工具参考](https://mathiaspaulenko.github.io/wavexis-mcp/tools/core/)
- [示例](https://mathiaspaulenko.github.io/wavexis-mcp/examples/screenshot/)

## 错误处理

所有工具在失败时都会返回结构化错误 JSON。每个错误都包含 `suggestion` 字段，用于引导 LLM 执行下一步动作：

```json
{
  "error": "Session 'abc-123' not found.",
  "tool": "wavexis_navigate",
  "type": "SessionNotFoundError",
  "message": "Session 'abc-123' not found.",
  "suggestion": "Call wavexis_session_open first to create a browser session."
}
```

这使得 LLM 可以在无人干预下自我纠正 — 它会阅读建议并调用推荐的工具。

## 架构

WaveXisMCP 位于三层生态的最上层：

```text
WaveXisMCP（MCP 服务器，220 个工具）
└─ wraps → wavexis（浏览器自动化库）
               ├─ cdpwave（CDP 后端，Chromium 原生）
               └─ bidiwave（BiDi 后端，W3C 跨浏览器）
```

- **cdpwave** — 面向 Chrome DevTools Protocol 的底层异步 Python 库。通过 WebSocket 直连 Chrome/Edge。无需驱动二进制。
- **bidiwave** — 面向 WebDriver BiDi 协议（W3C 标准）的底层异步 Python 库。可配合 Firefox、Chrome 与 Edge 使用。
- **wavexis** — 高层浏览器自动化库，通过统一的 `AbstractBackend` 接口抽象 cdpwave 与 bidiwave。
- **WaveXisMCP** — 封装 wavexis 的 MCP 服务器。将每个后端方法暴露为 MCP 工具，并提供 Pydantic v2 输入校验、JSON 响应以及功能层级过滤。

完整系统设计、数据流图与 ADR 请参见 [架构文档](https://mathiaspaulenko.github.io/wavexis-mcp/architecture/)。

## 开发

```bash
git clone https://github.com/MathiasPaulenko/wavexis-mcp.git
cd wavexis-mcp
pip install -e ".[dev]"

# 运行质量检查
ruff check wavexis_mcp tests
ruff format --check
mypy wavexis_mcp
python -m bandit -r wavexis_mcp

# 运行测试
pytest tests/unit -v
```

## 贡献

欢迎贡献。开发流程、编码规范与拉取请求流程请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题请参见 [SECURITY.md](SECURITY.md)。

## 致谢

WaveXisMCP 基于 [wavexis](https://github.com/MathiasPaulenko/wavexis) 浏览器自动化库与 [Model Context Protocol](https://modelcontextprotocol.io/) 构建。感谢开源 Python 与 MCP 社区提供的工具与标准，使本项目成为可能。

## 许可证

MIT

<!-- mcp-name: io.github.MathiasPaulenko/wavexis-mcp -->
mcp-name: io.github.MathiasPaulenko/wavexis-mcp

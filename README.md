> [English version](./README.en.md)

# SmallFeishu

一个轻量、可脚本化的飞书自定义机器人通知工具，提供命令行和 Python API。

SmallFeishu 已发布 `v0.1.0` Git 标签。它解决的是一个明确问题：把脚本、定时任务、CI 或本地 Agent 的文本消息发送到一个或多个飞书群，不需要创建完整的飞书应用。

## 适合什么场景

- 脚本或定时任务完成后发送提醒
- 将同一条消息发送到多个飞书群
- 在终端中检查配置和 Webhook 状态
- 在 Python 自动化中直接调用通知器

## 已实现能力

| 能力 | 入口 | 状态 |
|---|---|---|
| 文本通知 | CLI / Python | 可用 |
| 多 Webhook | TOML 配置 | 可用 |
| 配置初始化、查看与路径查询 | CLI | 可用 |
| 状态检查与测试消息 | CLI | 可用 |
| Webhook 脱敏显示 | CLI / Python | 可用 |

## 安装

要求 Python 3.9 或更高版本。可以直接从 GitHub 安装：

```bash
uv tool install git+https://github.com/LAD021/smallfeishu.git
```

也可以克隆后安装：

```bash
git clone https://github.com/LAD021/smallfeishu.git
cd smallfeishu
uv tool install .
```

使用 pip 时：

```bash
python -m pip install "git+https://github.com/LAD021/smallfeishu.git"
```

## 配置

初始化配置文件：

```bash
feishu config init
```

默认配置位置是 `~/.config/smallfeishu/config.toml`：

```toml
[feishu]
enabled = true
webhooks = [
  "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
]
```

配置查找顺序：

1. `FEISHU_CONFIG_PATH` 指定的文件
2. `~/.config/smallfeishu/config.toml`
3. 当前目录下的 `config.toml`

Webhook 是敏感凭证，不要提交到 Git，也不要放进公开日志或截图。

## 命令行

```bash
# 发送文本
feishu send "构建已经完成"

# 查看配置状态（Webhook 会脱敏）
feishu status

# 发送测试消息
feishu test

# 管理配置
feishu config show
feishu config path

# 查看版本
feishu version
```

## Python API

当前公开类是 `Config` 和 `FeishuNotifier`：

```python
from feishu.config import Config
from feishu.notification import FeishuNotifier

config = Config.load()
notifier = FeishuNotifier(config.get_webhooks())
notifier.send_text("自动化任务已经完成")
```

也可以直接传入 Webhook 列表：

```python
from feishu.notification import FeishuNotifier

notifier = FeishuNotifier([
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
])
notifier.send_text("Hello from Python")
```

## 开发与验证

```bash
git clone https://github.com/LAD021/smallfeishu.git
cd smallfeishu
uv sync --extra dev
uv run pytest
```

当前测试覆盖配置、CLI、消息格式化和通知异常路径。部署时仍建议用你自己的飞书机器人完成一次真实发送验证。

## 项目状态

- 当前版本：`v0.1.0`
- 发布形式：Git 标签（仓库当前没有单独的 GitHub Release 页面）
- 许可证：MIT
- 主要实现：Python

## 许可证与反馈

本项目采用 [MIT License](./LICENSE)。问题和改进建议请提交到 [GitHub Issues](https://github.com/LAD021/smallfeishu/issues)。

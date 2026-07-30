> [中文版](./README.md)

# SmallFeishu

A lightweight, scriptable notification tool for Feishu custom bots, with both a command-line interface and a Python API.

SmallFeishu has a tagged `v0.1.0` release. It solves one focused problem: sending text messages from scripts, scheduled jobs, CI, or local agents to one or more Feishu chats without creating a full Feishu application.

## Where It Fits

- Notify a chat when a script or scheduled job finishes
- Send the same message to multiple Feishu chats
- Inspect configuration and webhook status from the terminal
- Call the notifier directly from Python automation

## Implemented Capabilities

| Capability | Interface | Status |
|---|---|---|
| Text notifications | CLI / Python | Available |
| Multiple webhooks | TOML configuration | Available |
| Configuration init, display, and path lookup | CLI | Available |
| Status checks and test messages | CLI | Available |
| Masked webhook display | CLI / Python | Available |

## Installation

Python 3.9 or newer is required. Install directly from GitHub:

```bash
uv tool install git+https://github.com/LAD021/smallfeishu.git
```

Or clone and install locally:

```bash
git clone https://github.com/LAD021/smallfeishu.git
cd smallfeishu
uv tool install .
```

With pip:

```bash
python -m pip install "git+https://github.com/LAD021/smallfeishu.git"
```

## Configuration

Initialize the configuration file:

```bash
feishu config init
```

The default location is `~/.config/smallfeishu/config.toml`:

```toml
[feishu]
enabled = true
webhooks = [
  "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
]
```

Configuration lookup order:

1. The file specified by `FEISHU_CONFIG_PATH`
2. `~/.config/smallfeishu/config.toml`
3. `config.toml` in the current directory

A webhook is a secret credential. Do not commit it to Git or expose it in public logs or screenshots.

## Command Line

```bash
# Send text
feishu send "The build has finished"

# Inspect configuration status (webhooks are masked)
feishu status

# Send a test message
feishu test

# Manage configuration
feishu config show
feishu config path

# Print the version
feishu version
```

## Python API

The current public classes are `Config` and `FeishuNotifier`:

```python
from feishu.config import Config
from feishu.notification import FeishuNotifier

config = Config.load()
notifier = FeishuNotifier(config.get_webhooks())
notifier.send_text("The automation task has finished")
```

You can also pass webhooks directly:

```python
from feishu.notification import FeishuNotifier

notifier = FeishuNotifier([
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
])
notifier.send_text("Hello from Python")
```

## Development and Verification

```bash
git clone https://github.com/LAD021/smallfeishu.git
cd smallfeishu
uv sync --extra dev
uv run pytest
```

The current test suite covers configuration, the CLI, message formatting, and notification error paths. A deployment should still be verified with one real delivery through your own Feishu bot.

## Project Status

- Current version: `v0.1.0`
- Release form: Git tags (the repository currently has no separate GitHub Releases page)
- License: MIT
- Main implementation: Python

## License and Feedback

Released under the [MIT License](./LICENSE). Report problems or propose improvements through [GitHub Issues](https://github.com/LAD021/smallfeishu/issues).

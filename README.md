# SmallFeishu - 飞书通知工具

一个简单易用的飞书机器人消息发送工具，支持命令行和Python API两种使用方式。

## 功能特性

- 🚀 简单易用的命令行界面
- 📝 支持文本、Markdown等多种消息格式
- 🔧 灵活的配置管理
- 🔄 支持多个webhook地址
- 📊 内置状态检查和测试功能
- 🛡️ 完善的错误处理和日志记录

## 安装

```bash
# 使用 uv 安装（推荐）
uv tool install .

# 或者使用 pip 安装
pip install .
```

安装完成后，工具会自动在 `~/.config/smallfeishu/` 目录下创建配置文件 `config.toml`。

## 配置

### 配置文件位置

工具会按以下优先级查找配置文件：

1. 环境变量 `FEISHU_CONFIG_PATH` 指定的路径
2. `~/.config/smallfeishu/config.toml` （推荐）
3. `./config.toml` （当前目录）

### 初始化配置

```bash
# 初始化配置文件
feishu config init

# 查看配置文件路径
feishu config path

# 显示当前配置
feishu config show
```

### 配置文件格式

编辑 `~/.config/smallfeishu/config.toml` 文件：

```toml
# 飞书通知配置文件
[feishu]
# 是否启用飞书通知
enabled = true

# 飞书机器人 webhook 地址列表
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN_HERE"
    # "https://open.feishu.cn/open-apis/bot/v2/hook/ANOTHER_WEBHOOK_TOKEN_HERE"  # 可添加多个webhook
]
```

### 获取飞书机器人Webhook地址

1. 在飞书群聊中点击右上角设置
2. 选择「机器人」→「添加机器人」
3. 选择「自定义机器人」
4. 设置机器人名称和描述
5. 复制生成的 webhook 地址
6. 将地址替换配置文件中的 `YOUR_WEBHOOK_TOKEN_HERE`

## 使用方法

### 命令行使用

```bash
# 发送简单文本消息
feishu send "Hello, World!"

# 发送多行消息
feishu send "第一行\n第二行\n第三行"

# 从文件读取消息内容
feishu send --file message.txt

# 发送Markdown格式消息
feishu send --type markdown "**粗体文本** 和 *斜体文本*"

# 测试配置和连接
feishu test

# 检查工具状态
feishu status

# 查看版本信息
feishu version

# 查看帮助
feishu --help
feishu send --help
```

### Python API使用

```python
from feishu import FeishuBot

# 创建机器人实例
bot = FeishuBot()

# 发送文本消息
bot.send_text("Hello from Python!")

# 发送Markdown消息
bot.send_markdown("**重要通知**\n\n项目部署完成！")

# 发送到指定webhook
bot.send_text("测试消息", webhook_url="your_webhook_url")
```

## 配置管理命令

```bash
# 显示当前配置状态
feishu config show

# 初始化配置文件（会创建示例配置）
feishu config init

# 显示配置文件路径信息
feishu config path
```

## 故障排除

### 常见问题

1. **配置文件不存在**
   ```bash
   feishu config init  # 初始化配置文件
   ```

2. **webhook地址无效**
   - 检查webhook地址是否正确
   - 确认机器人是否已添加到群聊
   - 使用 `feishu test` 测试连接

3. **权限问题**
   - 确保有权限写入配置目录 `~/.config/smallfeishu/`
   - 检查配置文件权限

### 调试模式

设置环境变量启用详细日志：

```bash
export FEISHU_LOG_LEVEL=DEBUG
feishu test
```

## 开发

```bash
# 克隆项目
git clone <repository_url>
cd smallfeishu

# 安装开发依赖
uv sync

# 运行测试
uv run pytest

# 运行代码检查
uv run ruff check
uv run mypy src

# 本地安装开发版本
uv tool install -e .
```

## 许可证

MIT License
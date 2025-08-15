# 飞书命令行工具

一个简单易用的飞书机器人消息发送命令行工具，支持通过webhook向飞书群聊发送消息。

## 功能特性

- 🚀 **简单易用**: 一条命令即可发送消息到飞书群
- 🔧 **配置灵活**: 支持多个webhook，可配置超时时间
- 📝 **日志完善**: 详细的日志记录，支持文件和控制台输出
- 🧪 **测试完整**: 完整的单元测试覆盖
- 🛡️ **错误处理**: 完善的错误处理和重试机制

## 安装

### 使用uv安装（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd smallfeishu

# 安装依赖
uv sync

# 安装为命令行工具
uv pip install -e .
```

### 使用pip安装

```bash
pip install -e .
```

## 配置

### 1. 创建配置文件

复制示例配置文件并填入真实信息：

```bash
cp config.example.toml config.toml
```

### 2. 配置飞书机器人

编辑 `config.toml` 文件：

```toml
[notifications.feishu]
# 是否启用飞书通知
enabled = true

# 飞书机器人 webhook 地址列表
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN_HERE"
]
```

### 3. 获取飞书Webhook地址

1. 在飞书群聊中添加机器人
2. 选择"自定义机器人"
3. 复制生成的webhook地址
4. 将地址填入配置文件

## 使用方法

### 基本命令

```bash
# 查看版本
feishu version

# 查看配置状态
feishu status

# 发送测试消息
feishu test

# 发送文本消息
feishu send "Hello, World!"
```

### 高级用法

```bash
# 使用自定义配置文件
feishu send "测试消息" --config /path/to/config.toml

# 发送多行消息
feishu send "第一行\n第二行\n第三行"

# 查看指定配置文件的状态
feishu status --config /path/to/config.toml
```

## 命令详解

### `feishu send`

发送文本消息到飞书群。

**语法**: `feishu send <message> [--config <config_file>]`

**参数**:
- `message`: 要发送的消息内容（必需）
- `--config`: 配置文件路径（可选，默认为当前目录下的config.toml）

**示例**:
```bash
feishu send "部署完成，请查看"
feishu send "错误报告：数据库连接失败" --config prod.toml
```

### `feishu status`

查看飞书通知配置状态。

**语法**: `feishu status [--config <config_file>]`

**示例**:
```bash
feishu status
feishu status --config prod.toml
```

### `feishu test`

发送测试消息验证配置是否正确。

**语法**: `feishu test [--config <config_file>]`

**示例**:
```bash
feishu test
feishu test --config prod.toml
```

### `feishu version`

显示工具版本信息。

**语法**: `feishu version`

## 配置文件详解

```toml
[notifications.feishu]
# 是否启用飞书通知
# 设置为 true 启用，false 禁用
enabled = true

# 飞书机器人 webhook 地址列表
# 支持配置多个webhook，消息会发送到所有webhook
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN1",
    "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN2"
]

# 可选配置项
# [notifications.feishu.advanced]
# # 消息发送间隔（秒）
# interval = 1
# 
# # 重试次数
# retry_count = 3
# 
# # 超时时间（秒）
# timeout = 10
```

## 开发

### 项目结构

```
smallfeishu/
├── src/feishu/          # 源代码
│   ├── __init__.py      # 包初始化
│   ├── cli.py           # 命令行接口
│   ├── config.py        # 配置管理
│   └── notification.py  # 通知发送
├── tests/               # 测试用例
│   ├── test_cli.py      # CLI测试
│   ├── test_config.py   # 配置测试
│   └── test_notification.py # 通知测试
├── docs/                # 文档
├── config.example.toml  # 配置示例
├── pyproject.toml       # 项目配置
└── README.md           # 项目说明
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_config.py

# 运行测试并显示覆盖率
uv run pytest --cov=feishu

# 详细输出
uv run pytest -v
```

### 代码规范

项目遵循以下开发规范：

- **测试驱动开发**: 先写测试，再写实现
- **类型注解**: 使用Python类型注解
- **文档字符串**: 为所有函数添加详细的文档字符串
- **错误处理**: 完善的异常处理机制
- **日志记录**: 使用loguru进行日志记录

## 故障排除

### 常见问题

1. **配置文件不存在**
   ```
   错误: 配置文件不存在: config.toml
   ```
   解决: 复制 `config.example.toml` 为 `config.toml` 并填入正确配置

2. **webhook URL无效**
   ```
   错误: 无效的webhook URL
   ```
   解决: 检查webhook URL格式，确保是飞书官方格式

3. **网络连接失败**
   ```
   错误: 网络连接失败
   ```
   解决: 检查网络连接，确认webhook地址可访问

4. **飞书API返回错误**
   ```
   错误: 飞书API返回错误，代码: 9999
   ```
   解决: 检查webhook token是否正确，机器人是否被移除

### 调试模式

查看详细日志：

```bash
# 日志文件位置
tail -f feishu.log

# 或者查看控制台输出（INFO级别及以上）
feishu send "测试" 2>&1
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork项目
2. 创建功能分支
3. 编写测试用例
4. 实现功能
5. 运行测试确保通过
6. 提交Pull Request

### 提交规范

- 遵循测试驱动开发
- 确保所有测试通过
- 添加必要的文档
- 保持代码风格一致
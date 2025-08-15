# SmallFeishu 开发文档

## 项目概述

SmallFeishu 是一个简单易用的飞书机器人消息发送工具，提供命令行和Python API两种使用方式。

## 项目结构

```
smallfeishu/
├── src/
│   └── feishu/
│       ├── __init__.py          # 包初始化
│       ├── cli.py               # 命令行界面
│       ├── config.py            # 配置管理
│       ├── bot.py               # 飞书机器人核心功能
│       └── exceptions.py        # 自定义异常
├── tests/                       # 测试文件
├── docs/                        # 文档
├── spikes/                      # 实验性代码
├── config.example.toml          # 配置文件示例
├── install.py                   # 安装后脚本
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 配置系统

### 配置文件查找逻辑

工具按以下优先级查找配置文件：

1. **环境变量** `FEISHU_CONFIG_PATH` 指定的路径
2. **用户配置目录** `~/.config/smallfeishu/config.toml` （推荐）
3. **当前目录** `./config.toml`

### 配置文件格式

支持两种配置格式：

#### 简化格式（推荐）
```toml
[feishu]
enabled = true
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN1",
    "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN2"
]
```

#### 完整格式（兼容）
```toml
[notifications.feishu]
enabled = true
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN1"
]
```

### 配置管理API

```python
from feishu.config import Config

# 加载配置
config = Config.load()

# 获取配置文件路径
path = Config.get_config_path()

# 获取默认配置目录
dir_path = Config.get_default_config_dir()

# 获取配置信息（脱敏）
info = config.get_config_info()
```

## 核心组件

### 1. 配置管理 (config.py)

负责配置文件的加载、验证和管理：

- `Config.load()`: 加载并验证配置文件
- `Config._find_config_file()`: 查找配置文件
- `Config.get_config_info()`: 获取配置信息（脱敏）
- `Config._mask_webhook()`: 遮蔽敏感信息

### 2. 飞书机器人 (bot.py)

核心消息发送功能：

- `FeishuBot.send_text()`: 发送文本消息
- `FeishuBot.send_markdown()`: 发送Markdown消息
- `FeishuBot._send_message()`: 底层消息发送
- `FeishuBot._validate_webhook()`: Webhook验证

### 3. 命令行界面 (cli.py)

提供用户友好的命令行接口：

- `send()`: 发送消息命令
- `test()`: 测试连接命令
- `status()`: 状态检查命令
- `config()`: 配置管理命令
- `version()`: 版本信息命令

### 4. 异常处理 (exceptions.py)

自定义异常类型：

- `FeishuError`: 基础异常类
- `ConfigError`: 配置相关异常
- `NetworkError`: 网络相关异常
- `ValidationError`: 验证相关异常

## 安装系统

### 安装后脚本 (install.py)

在 `uv tool install` 时自动执行：

1. 创建配置目录 `~/.config/smallfeishu/`
2. 生成默认配置文件 `config.toml`
3. 显示安装完成信息和使用指南

### 配置文件初始化

```python
def create_config_file():
    """创建配置文件"""
    config_dir = Path.home() / ".config" / "smallfeishu"
    config_file = config_dir / "config.toml"
    
    # 创建目录
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入示例配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(example_config)
```

## 开发指南

### 环境设置

```bash
# 克隆项目
git clone <repository_url>
cd smallfeishu

# 安装依赖
uv sync

# 安装开发版本
uv tool install -e .
```

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_config.py

# 运行测试并显示覆盖率
uv run pytest --cov=feishu
```

### 代码质量

```bash
# 代码格式化
uv run ruff format

# 代码检查
uv run ruff check

# 类型检查
uv run mypy src
```

### 调试

设置环境变量启用调试模式：

```bash
export FEISHU_LOG_LEVEL=DEBUG
export FEISHU_CONFIG_PATH=/path/to/custom/config.toml
```

## API 参考

### 配置类 (Config)

```python
class Config:
    def __init__(self, enabled: bool, webhooks: List[str]):
        """初始化配置"""
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """加载配置文件"""
    
    @staticmethod
    def get_config_path() -> str:
        """获取配置文件路径"""
    
    @staticmethod
    def get_default_config_dir() -> Path:
        """获取默认配置目录"""
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息（脱敏）"""
```

### 机器人类 (FeishuBot)

```python
class FeishuBot:
    def __init__(self, config: Optional[Config] = None):
        """初始化机器人"""
    
    def send_text(self, message: str, webhook_url: Optional[str] = None) -> bool:
        """发送文本消息"""
    
    def send_markdown(self, message: str, webhook_url: Optional[str] = None) -> bool:
        """发送Markdown消息"""
    
    def test_connection(self) -> bool:
        """测试连接"""
```

## 部署和发布

### 构建包

```bash
# 构建分发包
uv build

# 检查包
twine check dist/*
```

### 发布到PyPI

```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*

# 发布到正式PyPI
twine upload dist/*
```

## 故障排除

### 常见问题

1. **配置文件找不到**
   - 检查配置文件路径
   - 使用 `feishu config path` 查看查找路径
   - 使用 `feishu config init` 初始化配置

2. **Webhook无效**
   - 验证webhook URL格式
   - 检查机器人是否添加到群聊
   - 使用 `feishu test` 测试连接

3. **权限问题**
   - 检查配置目录权限
   - 确保可以写入 `~/.config/smallfeishu/`

### 调试技巧

1. **启用详细日志**
   ```bash
   export FEISHU_LOG_LEVEL=DEBUG
   feishu test
   ```

2. **使用自定义配置路径**
   ```bash
   export FEISHU_CONFIG_PATH=/path/to/debug/config.toml
   feishu status
   ```

3. **检查配置加载**
   ```bash
   feishu config show
   ```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 确保所有测试通过
5. 提交 Pull Request

### 代码规范

- 使用 Type Hints
- 编写函数级注释
- 遵循 PEP 8 规范
- 测试覆盖率 > 80%
- 所有公共API需要文档
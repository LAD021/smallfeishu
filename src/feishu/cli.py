"""命令行接口模块

提供飞书机器人的命令行接口。
主要功能：
- 发送文本消息到飞书群
- 查看配置状态
- 测试连接
- 配置文件管理
- 使用fire库处理命令行参数
"""

import os
import sys
from datetime import datetime
from typing import Optional

import fire
from loguru import logger

from .config import Config, ConfigError
from .notification import FeishuNotifier, NotificationError
from .__init__ import __version__


class FeishuCLI:
    """飞书命令行工具
    
    提供发送消息、查看状态等功能的命令行接口。
    """
    
    def __init__(self):
        """初始化CLI"""
        self._setup_logging()
        logger.info("飞书命令行工具启动")
    
    def _setup_logging(self):
        """设置日志配置"""
        # 移除默认的日志处理器
        logger.remove()
        
        # 添加控制台输出，显示DEBUG及以上级别以便调试
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG"
        )
        
        # 添加文件日志，记录所有级别
        logger.add(
            "feishu.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days"
        )
    
    def send(self, message: str, message_type: str = "text", file: Optional[str] = None) -> bool:
        """发送消息到飞书群
        
        Args:
            message: 要发送的消息内容
            message_type: 消息类型，支持 text, markdown
            file: 从文件读取消息内容
            
        Returns:
            bool: 发送是否成功
            
        Examples:
            feishu send "Hello, World!"
            feishu send "**粗体文本**" --type markdown
            feishu send --file message.txt
        """
        try:
            # 从文件读取消息内容
            if file:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        message = f.read()
                except FileNotFoundError:
                    logger.error(f"文件不存在: {file}")
                    print(f"❌ 文件不存在: {file}")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"读取文件失败: {e}")
                    print(f"❌ 读取文件失败: {e}")
                    sys.exit(1)
            
            # 验证消息内容
            if not message or not message.strip():
                logger.error("消息内容不能为空")
                print("❌ 消息内容不能为空")
                sys.exit(1)
            
            # 加载配置并创建通知器
            app_config = Config.load()
            
            # 检查飞书通知是否启用
            if not app_config.is_enabled():
                logger.error("飞书通知未启用，请检查配置文件")
                print("❌ 飞书通知未启用，请检查配置文件")
                sys.exit(1)
            
            notifier = FeishuNotifier(app_config.get_webhooks())
            
            # 发送消息
            if message_type == "markdown":
                success = notifier.send_markdown(message)
            else:
                success = notifier.send_text(message)
            
            if success:
                logger.info("消息发送成功")
                print("✅ 消息发送成功")
                return True
            else:
                logger.error("消息发送失败")
                print("❌ 消息发送失败")
                sys.exit(1)
                
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            print(f"❌ 配置错误: {e}")
            sys.exit(1)
        except NotificationError as e:
            logger.error(f"发送失败: {e}")
            print(f"❌ 发送失败: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            print(f"❌ 未知错误: {e}")
            sys.exit(1)
    
    def status(self) -> None:
        """查看飞书通知配置状态
            
        Examples:
            feishu status
        """
        try:
            # 加载配置
            app_config = Config.load()
            config_info = app_config.get_config_info()
            
            # 显示状态信息
            print("\n=== 飞书通知配置状态 ===")
            print(f"配置文件: {Config.get_config_path()}")
            print(f"飞书通知: {'✅ 启用' if config_info['enabled'] else '❌ 禁用'}")
            print(f"Webhook数量: {config_info['webhook_count']}")
            
            if config_info['webhooks']:
                print("\nWebhook列表:")
                for i, webhook in enumerate(config_info['webhooks'], 1):
                    print(f"  {i}. {webhook}")
            
            print()
            
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            print(f"❌ 配置错误: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            print(f"❌ 未知错误: {e}")
            sys.exit(1)
    
    def test(self) -> bool:
        """发送测试消息验证配置
            
        Returns:
            bool: 测试是否成功
            
        Examples:
            feishu test
        """
        try:
            # 加载配置并创建通知器
            app_config = Config.load()
            
            # 检查飞书通知是否启用
            if not app_config.is_enabled():
                logger.error("飞书通知未启用，请检查配置文件")
                print("❌ 飞书通知未启用，请检查配置文件")
                sys.exit(1)
            
            notifier = FeishuNotifier(app_config.get_webhooks())
            
            # 创建测试消息
            test_message = f"飞书机器人测试消息\n发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 发送测试消息
            success = notifier.send_text(test_message)
            
            if success:
                logger.info("测试消息发送成功")
                print("✅ 测试成功！飞书机器人配置正常")
                return True
            else:
                logger.error("测试消息发送失败")
                print("❌ 测试失败！请检查配置")
                sys.exit(1)
                
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            print(f"❌ 配置错误: {e}")
            sys.exit(1)
        except NotificationError as e:
            logger.error(f"发送失败: {e}")
            print(f"❌ 发送失败: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            print(f"❌ 未知错误: {e}")
            sys.exit(1)
    
    def version(self) -> None:
        """显示版本信息
        
        Examples:
            feishu version
        """
        print(f"飞书命令行工具 v{__version__}")
        print("一个简单易用的飞书机器人消息发送工具")
    
    def config(self, action: str = "show") -> None:
        """配置文件管理
        
        Args:
            action: 操作类型，支持 show, init, path
            
        Examples:
            feishu config show    # 显示当前配置
            feishu config init    # 初始化配置文件
            feishu config path    # 显示配置文件路径
        """
        if action == "show":
            self._config_show()
        elif action == "init":
            self._config_init()
        elif action == "path":
            self._config_path()
        else:
            print("❌ 不支持的操作")
            print("支持的操作: show, init, path")
            sys.exit(1)
    
    def _config_show(self) -> None:
        """显示当前配置"""
        try:
            config_path = Config.get_config_path()
            print(f"\n📁 配置文件路径: {config_path}")
            
            if not os.path.exists(config_path):
                print("❌ 配置文件不存在")
                print("💡 使用 'feishu config init' 初始化配置文件")
                return
            
            # 加载配置
            app_config = Config.load()
            config_info = app_config.get_config_info()
            
            print(f"\n=== 飞书通知配置 ===")
            print(f"状态: {'✅ 启用' if config_info['enabled'] else '❌ 禁用'}")
            print(f"Webhook数量: {config_info['webhook_count']}")
            
            if config_info['webhooks']:
                print("\nWebhook列表:")
                for i, webhook in enumerate(config_info['webhooks'], 1):
                    print(f"  {i}. {webhook}")
            
            print()
            
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            print(f"❌ 配置错误: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            print(f"❌ 未知错误: {e}")
            sys.exit(1)
    
    def _config_init(self) -> None:
        """初始化配置文件"""
        try:
            config_dir = str(Config.get_default_config_dir())
            config_file = os.path.join(config_dir, "config.toml")
            
            # 创建配置目录
            os.makedirs(config_dir, exist_ok=True)
            
            if os.path.exists(config_file):
                print(f"⚠️  配置文件已存在: {config_file}")
                response = input("是否覆盖现有配置文件? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("取消初始化")
                    return
            
            # 创建示例配置内容
            example_config = """# 飞书通知配置文件
# 请根据实际情况修改以下配置

[feishu]
# 是否启用飞书通知
enabled = true

# 飞书机器人 webhook 地址列表
# 获取方式：
# 1. 在飞书群聊中添加机器人
# 2. 选择"自定义机器人"
# 3. 复制生成的 webhook 地址
# 4. 将地址替换下面的占位符
webhooks = [
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN_HERE"
    # "https://open.feishu.cn/open-apis/bot/v2/hook/ANOTHER_WEBHOOK_TOKEN_HERE"  # 可添加多个webhook
]

# 可选配置项（如果需要的话）
# [feishu.advanced]
# # 消息发送间隔（秒）
# interval = 1
# 
# # 重试次数
# retry_count = 3
# 
# # 超时时间（秒）
# timeout = 10
"""
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(example_config)
            
            print(f"✅ 配置文件已创建: {config_file}")
            print(f"\n🔧 请编辑配置文件，将 YOUR_WEBHOOK_TOKEN_HERE 替换为真实的飞书机器人webhook地址")
            print(f"\n🚀 配置完成后，使用以下命令测试:")
            print(f"   feishu test")
            
        except Exception as e:
            logger.error(f"初始化配置文件失败: {e}")
            print(f"❌ 初始化配置文件失败: {e}")
            sys.exit(1)
    
    def _config_path(self) -> None:
        """显示配置文件路径"""
        try:
            config_path = Config.get_config_path()
            config_dir = str(Config.get_default_config_dir())
            
            print(f"\n📁 当前配置文件路径: {config_path}")
            print(f"📂 默认配置目录: {config_dir}")
            
            if os.path.exists(config_path):
                print("✅ 配置文件存在")
            else:
                print("❌ 配置文件不存在")
                print("💡 使用 'feishu config init' 初始化配置文件")
            
            print(f"\n🔍 配置文件查找顺序:")
            print(f"  1. 环境变量 FEISHU_CONFIG_PATH")
            print(f"  2. {os.path.join(config_dir, 'config.toml')} (推荐)")
            print(f"  3. ./config.toml (当前目录)")
            print()
            
        except Exception as e:
            logger.error(f"获取配置路径失败: {e}")
            print(f"❌ 获取配置路径失败: {e}")
            sys.exit(1)


def main():
    """命令行入口点"""
    try:
        fire.Fire(FeishuCLI)
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        print(f"❌ 程序异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
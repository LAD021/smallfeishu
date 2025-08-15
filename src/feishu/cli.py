"""命令行接口模块

提供飞书机器人的命令行接口。
主要功能：
- 发送文本消息到飞书群
- 查看配置状态
- 测试连接
- 使用fire库处理命令行参数
"""

import sys
from datetime import datetime
from typing import Optional

import fire
from loguru import logger

from feishu.config import Config, ConfigError
from feishu.notification import FeishuNotifier, NotificationError
from feishu import __version__


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
        
        # 添加控制台输出，只显示INFO及以上级别
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # 添加文件日志，记录所有级别
        logger.add(
            "feishu.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days"
        )
    
    def send(self, message: str, config: Optional[str] = None) -> bool:
        """发送文本消息到飞书群
        
        Args:
            message: 要发送的消息内容
            config: 配置文件路径，默认使用当前目录下的config.toml
            
        Returns:
            bool: 发送是否成功
            
        Examples:
            feishu send "Hello, World!"
            feishu send "测试消息" --config /path/to/config.toml
        """
        try:
            # 验证消息内容
            if not message or not message.strip():
                logger.error("消息内容不能为空")
                sys.exit(1)
            
            # 加载配置
            logger.info(f"加载配置文件: {config or 'config.toml'}")
            app_config = Config.load(config)
            
            # 检查飞书通知是否启用
            if not app_config.is_enabled():
                logger.error("飞书通知未启用，请检查配置文件")
                sys.exit(1)
            
            # 创建通知器并发送消息
            webhooks = app_config.get_webhooks()
            logger.info(f"准备发送消息到 {len(webhooks)} 个webhook")
            
            notifier = FeishuNotifier(webhooks)
            success = notifier.send_text(message)
            
            if success:
                logger.info("消息发送成功")
                return True
            else:
                logger.error("消息发送失败")
                sys.exit(1)
                
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            sys.exit(1)
        except NotificationError as e:
            logger.error(f"发送失败: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            sys.exit(1)
    
    def status(self, config: Optional[str] = None) -> None:
        """查看飞书通知配置状态
        
        Args:
            config: 配置文件路径，默认使用当前目录下的config.toml
            
        Examples:
            feishu status
            feishu status --config /path/to/config.toml
        """
        try:
            # 加载配置
            app_config = Config.load(config)
            
            # 显示状态信息
            print("\n=== 飞书通知配置状态 ===")
            print(f"配置文件: {config or 'config.toml'}")
            print(f"飞书通知: {'启用' if app_config.is_enabled() else '禁用'}")
            
            webhooks = app_config.get_webhooks()
            print(f"Webhook数量: {len(webhooks)}")
            
            if webhooks:
                print("\nWebhook列表:")
                for i, webhook in enumerate(webhooks, 1):
                    # 隐藏敏感信息，只显示前缀和后缀
                    masked_webhook = self._mask_webhook(webhook)
                    print(f"  {i}. {masked_webhook}")
            
            print()
            
        except ConfigError as e:
            logger.error(f"配置错误: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            sys.exit(1)
    
    def test(self, config: Optional[str] = None) -> bool:
        """发送测试消息验证配置
        
        Args:
            config: 配置文件路径，默认使用当前目录下的config.toml
            
        Returns:
            bool: 测试是否成功
            
        Examples:
            feishu test
            feishu test --config /path/to/config.toml
        """
        try:
            # 加载配置
            app_config = Config.load(config)
            
            # 检查飞书通知是否启用
            if not app_config.is_enabled():
                logger.error("飞书通知未启用，请检查配置文件")
                sys.exit(1)
            
            # 创建测试消息
            test_message = f"飞书机器人测试消息\n发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 发送测试消息
            webhooks = app_config.get_webhooks()
            logger.info(f"发送测试消息到 {len(webhooks)} 个webhook")
            
            notifier = FeishuNotifier(webhooks)
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
            sys.exit(1)
        except NotificationError as e:
            logger.error(f"发送失败: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"未知错误: {e}")
            sys.exit(1)
    
    def version(self) -> None:
        """显示版本信息
        
        Examples:
            feishu version
        """
        print(f"飞书命令行工具 v{__version__}")
        print("一个简单易用的飞书机器人消息发送工具")
    
    def _mask_webhook(self, webhook: str) -> str:
        """遮蔽webhook中的敏感信息
        
        Args:
            webhook: 原始webhook URL
            
        Returns:
            str: 遮蔽后的URL
        """
        if len(webhook) <= 50:
            # 短URL，显示前10个和后10个字符
            return f"{webhook[:10]}...{webhook[-10:]}"
        else:
            # 长URL，显示前20个和后15个字符
            return f"{webhook[:20]}...{webhook[-15:]}"


def main():
    """主入口函数
    
    用于pyproject.toml中的console_scripts配置。
    """
    try:
        fire.Fire(FeishuCLI)
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
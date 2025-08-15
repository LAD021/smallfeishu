"""CLI模块测试用例

测试cli.py模块的功能，包括：
- 命令行参数解析
- 消息发送命令
- 配置文件处理
- 错误处理
- 日志输出
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from feishu.cli import FeishuCLI
from feishu.config import ConfigError
from feishu.notification import NotificationError


class TestFeishuCLI:
    """飞书CLI测试类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.cli = FeishuCLI()
    
    @patch('feishu.cli.Config.load')
    @patch('feishu.cli.FeishuNotifier')
    def test_send_text_success(self, mock_notifier_class, mock_config_load):
        """测试成功发送文本消息"""
        # 模拟配置
        mock_config = Mock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhooks.return_value = ["https://test.webhook.url"]
        mock_config_load.return_value = mock_config
        
        # 模拟通知器
        mock_notifier = Mock()
        mock_notifier.send_text.return_value = True
        mock_notifier_class.return_value = mock_notifier
        
        # 执行命令
        result = self.cli.send("测试消息")
        
        # 验证结果
        assert result is True
        mock_config_load.assert_called_once_with(None)
        mock_notifier_class.assert_called_once_with(["https://test.webhook.url"])
        mock_notifier.send_text.assert_called_once_with("测试消息")
    
    @patch('feishu.cli.Config.load')
    def test_send_text_feishu_disabled(self, mock_config_load):
        """测试飞书通知被禁用的情况"""
        # 模拟配置
        mock_config = Mock()
        mock_config.is_enabled.return_value = False
        mock_config_load.return_value = mock_config
        
        # 执行命令，应该抛出异常
        with pytest.raises(SystemExit):
            self.cli.send("测试消息")
    
    @patch('feishu.cli.Config.load')
    def test_send_text_config_error(self, mock_config_load):
        """测试配置文件错误"""
        mock_config_load.side_effect = ConfigError("配置文件不存在")
        
        with pytest.raises(SystemExit):
            self.cli.send("测试消息")
    
    @patch('feishu.cli.Config.load')
    @patch('feishu.cli.FeishuNotifier')
    def test_send_text_notification_error(self, mock_notifier_class, mock_config_load):
        """测试通知发送错误"""
        # 模拟配置
        mock_config = Mock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhooks.return_value = ["https://test.webhook.url"]
        mock_config_load.return_value = mock_config
        
        # 模拟通知器错误
        mock_notifier = Mock()
        mock_notifier.send_text.side_effect = NotificationError("发送失败")
        mock_notifier_class.return_value = mock_notifier
        
        with pytest.raises(SystemExit):
            self.cli.send("测试消息")
    
    @patch('feishu.cli.Config.load')
    @patch('feishu.cli.FeishuNotifier')
    def test_send_with_custom_config(self, mock_notifier_class, mock_config_load):
        """测试使用自定义配置文件"""
        # 模拟配置
        mock_config = Mock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhooks.return_value = ["https://test.webhook.url"]
        mock_config_load.return_value = mock_config
        
        # 模拟通知器
        mock_notifier = Mock()
        mock_notifier.send_text.return_value = True
        mock_notifier_class.return_value = mock_notifier
        
        # 执行命令
        result = self.cli.send("测试消息", config="/custom/config.toml")
        
        # 验证配置文件路径
        mock_config_load.assert_called_once_with("/custom/config.toml")
        assert result is True
    
    def test_send_empty_message(self):
        """测试发送空消息"""
        with pytest.raises(SystemExit):
            self.cli.send("")
        
        with pytest.raises(SystemExit):
            self.cli.send(None)
    
    @patch('feishu.cli.Config.load')
    def test_status_command_enabled(self, mock_config_load):
        """测试状态命令 - 启用状态"""
        mock_config = Mock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhooks.return_value = [
            "https://test1.webhook.url",
            "https://test2.webhook.url"
        ]
        mock_config_load.return_value = mock_config
        
        # 这里我们不能直接测试print输出，但可以确保方法执行不报错
        self.cli.status()
        
        mock_config_load.assert_called_once_with(None)
    
    @patch('feishu.cli.Config.load')
    def test_status_command_disabled(self, mock_config_load):
        """测试状态命令 - 禁用状态"""
        mock_config = Mock()
        mock_config.is_enabled.return_value = False
        mock_config.get_webhooks.return_value = []
        mock_config_load.return_value = mock_config
        
        self.cli.status()
        
        mock_config_load.assert_called_once_with(None)
    
    @patch('feishu.cli.Config.load')
    def test_status_command_config_error(self, mock_config_load):
        """测试状态命令配置错误"""
        mock_config_load.side_effect = ConfigError("配置文件不存在")
        
        with pytest.raises(SystemExit):
            self.cli.status()
    
    @patch('feishu.cli.Config.load')
    @patch('feishu.cli.FeishuNotifier')
    def test_test_command_success(self, mock_notifier_class, mock_config_load):
        """测试test命令成功"""
        # 模拟配置
        mock_config = Mock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhooks.return_value = ["https://test.webhook.url"]
        mock_config_load.return_value = mock_config
        
        # 模拟通知器
        mock_notifier = Mock()
        mock_notifier.send_text.return_value = True
        mock_notifier_class.return_value = mock_notifier
        
        result = self.cli.test()
        
        assert result is True
        # 验证发送了测试消息
        mock_notifier.send_text.assert_called_once()
        call_args = mock_notifier.send_text.call_args[0][0]
        assert "测试消息" in call_args
    
    @patch('feishu.cli.Config.load')
    def test_test_command_feishu_disabled(self, mock_config_load):
        """测试test命令 - 飞书禁用"""
        mock_config = Mock()
        mock_config.is_enabled.return_value = False
        mock_config_load.return_value = mock_config
        
        with pytest.raises(SystemExit):
            self.cli.test()
    
    @patch('feishu.cli.logger')
    def test_logging_setup(self, mock_logger):
        """测试日志设置"""
        # 创建新的CLI实例会调用日志设置
        cli = FeishuCLI()
        
        # 验证日志配置被调用
        # 注意：这里的测试可能需要根据实际的日志配置方式调整
        assert mock_logger.remove.called or mock_logger.add.called
    
    def test_version_command(self):
        """测试版本命令"""
        # 版本命令应该不报错
        self.cli.version()
    
    @patch('feishu.cli.sys.exit')
    @patch('feishu.cli.logger')
    def test_error_handling_with_exit(self, mock_logger, mock_exit):
        """测试错误处理和退出"""
        # 这个测试验证错误处理机制
        with patch('feishu.cli.Config.load') as mock_config_load:
            mock_config_load.side_effect = ConfigError("测试错误")
            
            self.cli.send("测试消息")
            
            # 验证错误被记录并退出
            mock_logger.error.assert_called()
            mock_exit.assert_called_with(1)
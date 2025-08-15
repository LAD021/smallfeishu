"""配置模块测试用例

测试config.py模块的功能，包括：
- 配置文件读取
- 配置验证
- 默认值处理
- 错误处理
"""

import os
import tempfile
import pytest
from pathlib import Path

from feishu.config import Config, ConfigError


class TestConfig:
    """配置模块测试类"""
    
    def test_load_valid_config(self):
        """测试加载有效配置文件"""
        config_content = """
[notifications.feishu]
enabled = true
webhooks = ["https://open.feishu.cn/open-apis/bot/v2/hook/test-token"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            config = Config.load(config_path)
            assert config.feishu_enabled is True
            assert len(config.webhooks) == 1
            assert "test-token" in config.webhooks[0]
        finally:
            os.unlink(config_path)
    
    def test_load_config_with_disabled_feishu(self):
        """测试加载禁用飞书的配置"""
        config_content = """
[notifications.feishu]
enabled = false
webhooks = []
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            config = Config.load(config_path)
            assert config.feishu_enabled is False
            assert len(config.webhooks) == 0
        finally:
            os.unlink(config_path)
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        with pytest.raises(ConfigError, match="配置文件不存在"):
            Config.load("/nonexistent/config.toml")
    
    def test_load_invalid_toml(self):
        """测试加载无效的TOML文件"""
        config_content = """
[notifications.feishu
# 缺少闭合括号
enabled = true
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            with pytest.raises(ConfigError, match="配置文件格式错误"):
                Config.load(config_path)
        finally:
            os.unlink(config_path)
    
    def test_load_config_missing_feishu_section(self):
        """测试加载缺少飞书配置段的文件"""
        config_content = """
[other]
value = "test"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            with pytest.raises(ConfigError, match="配置文件中缺少飞书配置"):
                Config.load(config_path)
        finally:
            os.unlink(config_path)
    
    def test_validate_webhooks_empty_when_enabled(self):
        """测试启用飞书但webhook为空的情况"""
        config_content = """
[notifications.feishu]
enabled = true
webhooks = []
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            with pytest.raises(ConfigError, match="启用飞书通知时必须配置至少一个webhook"):
                Config.load(config_path)
        finally:
            os.unlink(config_path)
    
    def test_validate_invalid_webhook_url(self):
        """测试无效的webhook URL"""
        config_content = """
[notifications.feishu]
enabled = true
webhooks = ["invalid-url"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            with pytest.raises(ConfigError, match="无效的webhook URL"):
                Config.load(config_path)
        finally:
            os.unlink(config_path)
    
    def test_load_default_config_path(self):
        """测试加载默认配置文件路径"""
        # 创建临时目录和配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_content = """
[notifications.feishu]
enabled = true
webhooks = ["https://open.feishu.cn/open-apis/bot/v2/hook/test-token"]
            """
            config_path.write_text(config_content)
            
            # 临时改变工作目录
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                config = Config.load()
                assert config.feishu_enabled is True
                assert len(config.webhooks) == 1
            finally:
                os.chdir(original_cwd)
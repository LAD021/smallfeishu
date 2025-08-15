"""配置模块

负责读取和验证config.toml配置文件。
主要功能：
- 读取TOML格式的配置文件
- 验证配置项的有效性
- 提供配置访问接口
"""

import os
import toml
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from loguru import logger


class ConfigError(Exception):
    """配置相关错误"""
    pass


class Config:
    """配置管理类
    
    负责加载和管理飞书机器人的配置信息。
    """
    
    def __init__(self, feishu_enabled: bool, webhooks: List[str]):
        """初始化配置
        
        Args:
            feishu_enabled: 是否启用飞书通知
            webhooks: 飞书webhook地址列表
        """
        self.feishu_enabled = feishu_enabled
        self.webhooks = webhooks
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """加载配置文件
        
        Args:
            config_path: 配置文件路径，默认为当前目录下的config.toml
            
        Returns:
            Config: 配置对象
            
        Raises:
            ConfigError: 配置文件不存在、格式错误或内容无效时抛出
        """
        if config_path is None:
            config_path = "config.toml"
        
        config_file = Path(config_path)
        
        # 检查配置文件是否存在
        if not config_file.exists():
            logger.error(f"配置文件不存在: {config_path}")
            raise ConfigError(f"配置文件不存在: {config_path}")
        
        # 读取配置文件
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = toml.load(f)
            logger.info(f"成功加载配置文件: {config_path}")
        except toml.TomlDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise ConfigError(f"配置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            raise ConfigError(f"读取配置文件失败: {e}")
        
        # 验证配置结构
        if 'notifications' not in config_data or 'feishu' not in config_data['notifications']:
            logger.error("配置文件中缺少飞书配置段")
            raise ConfigError("配置文件中缺少飞书配置段: [notifications.feishu]")
        
        feishu_config = config_data['notifications']['feishu']
        
        # 提取配置项
        feishu_enabled = feishu_config.get('enabled', False)
        webhooks = feishu_config.get('webhooks', [])
        
        # 验证配置
        cls._validate_config(feishu_enabled, webhooks)
        
        return cls(feishu_enabled, webhooks)
    
    @staticmethod
    def _validate_config(feishu_enabled: bool, webhooks: List[str]) -> None:
        """验证配置项
        
        Args:
            feishu_enabled: 是否启用飞书通知
            webhooks: webhook地址列表
            
        Raises:
            ConfigError: 配置无效时抛出
        """
        # 如果启用飞书通知，必须配置webhook
        if feishu_enabled and not webhooks:
            logger.error("启用飞书通知时必须配置至少一个webhook")
            raise ConfigError("启用飞书通知时必须配置至少一个webhook")
        
        # 验证webhook URL格式
        for webhook in webhooks:
            if not Config._is_valid_webhook_url(webhook):
                logger.error(f"无效的webhook URL: {webhook}")
                raise ConfigError(f"无效的webhook URL: {webhook}")
        
        logger.debug(f"配置验证通过: enabled={feishu_enabled}, webhooks={len(webhooks)}个")
    
    @staticmethod
    def _is_valid_webhook_url(url: str) -> bool:
        """验证webhook URL是否有效
        
        Args:
            url: 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            parsed = urlparse(url)
            # 检查是否为HTTPS协议且包含飞书域名
            return (
                parsed.scheme == 'https' and
                'feishu.cn' in parsed.netloc and
                '/open-apis/bot/v2/hook/' in parsed.path
            )
        except Exception:
            return False
    
    def get_webhooks(self) -> List[str]:
        """获取webhook列表
        
        Returns:
            List[str]: webhook地址列表
        """
        return self.webhooks.copy()
    
    def is_enabled(self) -> bool:
        """检查飞书通知是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.feishu_enabled
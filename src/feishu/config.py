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
            config_path: 配置文件路径，如果为None则按优先级查找
            
        Returns:
            Config: 配置对象
            
        Raises:
            ConfigError: 配置文件不存在、格式错误或内容无效时抛出
        """
        if config_path is None:
            config_path = cls._find_config_file()
        
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
            logger.debug(f"配置文件内容: {config_data}")
        except toml.TomlDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise ConfigError(f"配置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            raise ConfigError(f"读取配置文件失败: {e}")
        
        # 验证配置结构 - 支持两种格式：[feishu] 和 [notifications.feishu]
        if 'feishu' in config_data:
            # 简化格式：[feishu]
            feishu_config = config_data['feishu']
            logger.debug("使用简化配置格式: [feishu]")
        elif 'notifications' in config_data and 'feishu' in config_data['notifications']:
            # 完整格式：[notifications.feishu]
            feishu_config = config_data['notifications']['feishu']
            logger.debug("使用完整配置格式: [notifications.feishu]")
        else:
            logger.error("配置文件中缺少飞书配置段")
            raise ConfigError("配置文件中缺少飞书配置段: [feishu] 或 [notifications.feishu]")
        
        logger.debug(f"读取到的飞书配置: {feishu_config}")
        
        # 提取配置项
        feishu_enabled = feishu_config.get('enabled', False)
        webhooks = feishu_config.get('webhooks', [])
        
        # 验证配置
        cls._validate_config(feishu_enabled, webhooks)
        
        return cls(feishu_enabled, webhooks)
    
    @staticmethod
    def _find_config_file() -> str:
        """查找配置文件
        
        按以下优先级查找配置文件：
        1. 环境变量 FEISHU_CONFIG_PATH
        2. ~/.config/smallfeishu/config.toml (XDG标准)
        3. ./config.toml (当前目录)
        
        Returns:
            str: 配置文件路径
            
        Raises:
            ConfigError: 找不到配置文件时抛出
        """
        # 1. 检查环境变量
        env_config = os.getenv('FEISHU_CONFIG_PATH')
        if env_config and Path(env_config).exists():
            logger.debug(f"使用环境变量指定的配置文件: {env_config}")
            return env_config
        
        # 2. 检查XDG标准配置目录
        xdg_config = Path.home() / ".config" / "smallfeishu" / "config.toml"
        if xdg_config.exists():
            logger.debug(f"使用XDG标准配置文件: {xdg_config}")
            return str(xdg_config)
        
        # 3. 检查当前目录
        local_config = Path("config.toml")
        if local_config.exists():
            logger.debug(f"使用当前目录配置文件: {local_config}")
            return str(local_config)
        
        # 如果都不存在，返回XDG标准路径（用于错误提示）
        logger.debug("未找到配置文件，返回默认XDG路径")
        return str(xdg_config)
    
    @staticmethod
    def get_config_path() -> str:
        """获取配置文件路径
        
        Returns:
            str: 配置文件路径
        """
        return Config._find_config_file()
    
    @staticmethod
    def get_default_config_dir() -> Path:
        """获取默认配置目录
        
        Returns:
            Path: 默认配置目录路径
        """
        return Path.home() / ".config" / "smallfeishu"
    
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
    
    def get_config_info(self) -> dict:
        """获取配置信息
        
        Returns:
            dict: 配置信息字典
        """
        return {
            'enabled': self.feishu_enabled,
            'webhook_count': len(self.webhooks),
            'webhooks': [self._mask_webhook(webhook) for webhook in self.webhooks]
        }
    
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
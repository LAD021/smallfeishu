"""通知模块

负责发送消息到飞书群聊。
主要功能：
- 通过webhook发送文本消息
- 发送富文本消息
- 错误处理和重试
- 日志记录
"""

import json
from typing import List, Dict, Any

import requests
from loguru import logger
from requests.exceptions import RequestException, Timeout, ConnectionError


class NotificationError(Exception):
    """通知相关错误"""
    pass


class FeishuNotifier:
    """飞书通知器
    
    负责向飞书群聊发送各种类型的消息。
    """
    
    def __init__(self, webhooks: List[str], timeout: int = 10):
        """初始化飞书通知器
        
        Args:
            webhooks: 飞书webhook地址列表
            timeout: 请求超时时间（秒），默认10秒
            
        Raises:
            ValueError: 参数无效时抛出
        """
        if not webhooks:
            raise ValueError("webhook列表不能为空")
        
        if timeout <= 0:
            raise ValueError("超时时间必须大于0")
        
        self.webhooks = webhooks
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        logger.info(f"初始化飞书通知器，webhook数量: {len(webhooks)}, 超时时间: {timeout}秒")
    
    def _format_message(self, text: str) -> str:
        """格式化消息文本
        
        处理换行符、去除多余空行和空格，优化消息排版。
        
        Args:
            text: 原始文本
            
        Returns:
            str: 格式化后的文本
        """
        if not text:
            return text
        
        # 1. 处理转义的换行符 \n -> 实际换行符
        formatted_text = text.replace('\\n', '\n')
        
        # 2. 处理其他常见的转义字符
        formatted_text = formatted_text.replace('\\t', '\t')
        formatted_text = formatted_text.replace('\\r', '\r')
        
        # 3. 去除行首行尾的空白字符
        lines = formatted_text.split('\n')
        lines = [line.strip() for line in lines]
        
        # 4. 去除多余的连续空行（保留最多一个空行）
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = not line.strip()
            if is_empty:
                if not prev_empty:
                    cleaned_lines.append('')
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        # 5. 去除开头和结尾的空行
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        result = '\n'.join(cleaned_lines)
        
        # 记录格式化过程
        if result != text:
            logger.debug(f"消息格式化前: {repr(text)}")
            logger.debug(f"消息格式化后: {repr(result)}")
        
        return result
    
    def send_text(self, text: str) -> bool:
        """发送文本消息
        
        Args:
            text: 要发送的文本内容
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            ValueError: 消息内容为空时抛出
            NotificationError: 发送失败时抛出
        """
        if not text or not text.strip():
            raise ValueError("消息内容不能为空")
        
        # 格式化消息文本
        formatted_text = self._format_message(text)
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": formatted_text
            }
        }
        
        logger.info(f"准备发送文本消息到 {len(self.webhooks)} 个webhook")
        logger.debug(f"原始消息内容: {text}")
        logger.debug(f"格式化后消息内容: {formatted_text}")
        
        return self._send_to_webhooks(payload)
    
    def send_rich_text(self, content: Dict[str, Any]) -> bool:
        """发送富文本消息
        
        Args:
            content: 富文本内容，格式参考飞书API文档
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            ValueError: 内容为空时抛出
            NotificationError: 发送失败时抛出
        """
        if not content:
            raise ValueError("富文本内容不能为空")
        
        payload = {
            "msg_type": "post",
            "content": {
                "post": content
            }
        }
        
        logger.info(f"准备发送富文本消息到 {len(self.webhooks)} 个webhook")
        logger.debug(f"富文本内容: {json.dumps(content, ensure_ascii=False)}")
        
        return self._send_to_webhooks(payload)
    
    def _send_to_webhooks(self, payload: Dict[str, Any]) -> bool:
        """向所有webhook发送消息
        
        Args:
            payload: 消息载荷
            
        Returns:
            bool: 是否全部发送成功
            
        Raises:
            NotificationError: 发送失败时抛出
        """
        success_count = 0
        errors = []
        
        for i, webhook in enumerate(self.webhooks):
            try:
                self._send_single_webhook(webhook, payload)
                success_count += 1
                logger.debug(f"webhook {i+1}/{len(self.webhooks)} 发送成功")
            except Exception as e:
                error_msg = f"webhook {i+1}/{len(self.webhooks)} 发送失败: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # 检查发送结果
        if success_count == 0:
            # 全部失败
            error_summary = "; ".join(errors)
            raise NotificationError(f"所有webhook发送失败: {error_summary}")
        elif success_count < len(self.webhooks):
            # 部分失败
            error_summary = "; ".join(errors)
            raise NotificationError(f"部分webhook发送失败 ({success_count}/{len(self.webhooks)} 成功): {error_summary}")
        
        # 全部成功
        logger.info(f"消息发送成功，共 {success_count} 个webhook")
        return True
    
    def _send_single_webhook(self, webhook: str, payload: Dict[str, Any]) -> None:
        """向单个webhook发送消息
        
        Args:
            webhook: webhook地址
            payload: 消息载荷
            
        Raises:
            NotificationError: 发送失败时抛出
        """
        try:
            logger.debug(f"向webhook发送请求: {webhook}")
            logger.debug(f"请求头: {self.headers}")
            logger.debug(f"请求载荷: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                webhook,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            logger.debug(f"HTTP响应状态码: {response.status_code}")
            logger.debug(f"HTTP响应头: {dict(response.headers)}")
            logger.debug(f"HTTP响应内容: {response.text}")
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text}"
                logger.error(error_msg)
                raise NotificationError(error_msg)
            
            # 检查飞书API响应
            try:
                result = response.json()
                logger.debug(f"解析的JSON响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                if result.get('code') != 0:
                    error_msg = f"飞书API返回错误，代码: {result.get('code')}, 消息: {result.get('msg')}"
                    logger.error(error_msg)
                    raise NotificationError(error_msg)
                else:
                    logger.info(f"飞书API响应成功: code={result.get('code')}, msg={result.get('msg')}")
            except json.JSONDecodeError as e:
                # 如果响应不是JSON格式，但状态码是200，认为成功
                logger.warning(f"webhook响应不是JSON格式: {e}，但状态码为200，认为发送成功")
                logger.warning(f"原始响应内容: {response.text}")
            
            logger.info(f"webhook发送成功: {webhook}")
            
        except Timeout as e:
            raise NotificationError(f"请求超时: {str(e)}")
        except ConnectionError as e:
            raise NotificationError(f"网络连接失败: {str(e)}")
        except RequestException as e:
            raise NotificationError(f"请求异常: {str(e)}")
        except Exception as e:
            raise NotificationError(f"未知错误: {str(e)}")
    
    def get_webhook_count(self) -> int:
        """获取webhook数量
        
        Returns:
            int: webhook数量
        """
        return len(self.webhooks)
    
    def get_timeout(self) -> int:
        """获取超时时间
        
        Returns:
            int: 超时时间（秒）
        """
        return self.timeout
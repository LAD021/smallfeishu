"""通知模块测试用例

测试notification.py模块的功能，包括：
- 飞书消息发送
- 错误处理
- 重试机制
- 消息格式化
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException, Timeout, ConnectionError

from feishu.notification import FeishuNotifier, NotificationError


class TestFeishuNotifier:
    """飞书通知器测试类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.webhooks = [
            "https://open.feishu.cn/open-apis/bot/v2/hook/test-token-1",
            "https://open.feishu.cn/open-apis/bot/v2/hook/test-token-2"
        ]
        self.notifier = FeishuNotifier(self.webhooks)
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_success(self, mock_post):
        """测试成功发送文本消息"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_post.return_value = mock_response
        
        result = self.notifier.send_text("测试消息")
        
        assert result is True
        assert mock_post.call_count == 2  # 两个webhook都应该被调用
        
        # 验证请求参数
        expected_payload = {
            "msg_type": "text",
            "content": {
                "text": "测试消息"
            }
        }
        
        for call in mock_post.call_args_list:
            args, kwargs = call
            assert kwargs['json'] == expected_payload
            assert kwargs['timeout'] == 10
            assert 'headers' in kwargs
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_with_custom_timeout(self, mock_post):
        """测试使用自定义超时时间发送消息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_post.return_value = mock_response
        
        notifier = FeishuNotifier(self.webhooks, timeout=30)
        result = notifier.send_text("测试消息")
        
        assert result is True
        # 验证超时参数
        for call in mock_post.call_args_list:
            args, kwargs = call
            assert kwargs['timeout'] == 30
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_api_error(self, mock_post):
        """测试API返回错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 9999, "msg": "invalid webhook"}
        mock_post.return_value = mock_response
        
        with pytest.raises(NotificationError, match="飞书API返回错误"):
            self.notifier.send_text("测试消息")
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_http_error(self, mock_post):
        """测试HTTP错误"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with pytest.raises(NotificationError, match="HTTP请求失败"):
            self.notifier.send_text("测试消息")
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_timeout(self, mock_post):
        """测试请求超时"""
        mock_post.side_effect = Timeout("Request timeout")
        
        with pytest.raises(NotificationError, match="请求超时"):
            self.notifier.send_text("测试消息")
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_connection_error(self, mock_post):
        """测试连接错误"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(NotificationError, match="网络连接失败"):
            self.notifier.send_text("测试消息")
    
    @patch('feishu.notification.requests.post')
    def test_send_text_message_partial_failure(self, mock_post):
        """测试部分webhook失败的情况"""
        # 第一个webhook成功，第二个失败
        responses = [
            Mock(status_code=200, json=lambda: {"code": 0, "msg": "success"}),
            Mock(status_code=400, text="Bad Request")
        ]
        mock_post.side_effect = responses
        
        with pytest.raises(NotificationError, match="部分webhook发送失败"):
            self.notifier.send_text("测试消息")
    
    @patch('feishu.notification.requests.post')
    def test_send_rich_text_message(self, mock_post):
        """测试发送富文本消息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_post.return_value = mock_response
        
        content = {
            "zh_cn": {
                "title": "测试标题",
                "content": [
                    [{"tag": "text", "text": "测试内容"}]
                ]
            }
        }
        
        result = self.notifier.send_rich_text(content)
        
        assert result is True
        
        # 验证请求参数
        expected_payload = {
            "msg_type": "post",
            "content": {
                "post": content
            }
        }
        
        for call in mock_post.call_args_list:
            args, kwargs = call
            assert kwargs['json'] == expected_payload
    
    def test_empty_webhooks(self):
        """测试空webhook列表"""
        with pytest.raises(ValueError, match="webhook列表不能为空"):
            FeishuNotifier([])
    
    def test_invalid_timeout(self):
        """测试无效的超时时间"""
        with pytest.raises(ValueError, match="超时时间必须大于0"):
            FeishuNotifier(self.webhooks, timeout=0)
        
        with pytest.raises(ValueError, match="超时时间必须大于0"):
            FeishuNotifier(self.webhooks, timeout=-1)
    
    @patch('feishu.notification.requests.post')
    def test_send_empty_message(self, mock_post):
        """测试发送空消息"""
        with pytest.raises(ValueError, match="消息内容不能为空"):
            self.notifier.send_text("")
        
        with pytest.raises(ValueError, match="消息内容不能为空"):
            self.notifier.send_text(None)
    
    @patch('feishu.notification.logger')
    @patch('feishu.notification.requests.post')
    def test_logging(self, mock_post, mock_logger):
        """测试日志记录"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_post.return_value = mock_response
        
        self.notifier.send_text("测试消息")
        
        # 验证日志调用
        assert mock_logger.info.called
        assert mock_logger.debug.called
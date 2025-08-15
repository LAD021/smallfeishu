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
    
    def test_format_message_newlines(self):
        """测试换行符处理"""
        # 测试转义换行符转换
        result = self.notifier._format_message("第一行\\n第二行\\n第三行")
        expected = "第一行\n第二行\n第三行"
        assert result == expected
        
        # 测试混合换行符（真实回车和转义字符）
        result = self.notifier._format_message("第一行\\n\n第二行")
        expected = "第一行\n\n第二行"
        assert result == expected
        
        # 测试复杂混合场景：既有真实回车又有\n转义字符
        mixed_input = "标题\\n\n内容1\\n内容2\n\\n结尾"
        result = self.notifier._format_message(mixed_input)
        expected = "标题\n\n内容1\n内容2\n\n结尾"
        assert result == expected
    
    def test_format_message_tabs_and_carriage_returns(self):
        """测试制表符和回车符处理"""
        # 测试制表符
        result = self.notifier._format_message("列1\\t列2\\t列3")
        expected = "列1\t列2\t列3"
        assert result == expected
        
        # 测试回车符
        result = self.notifier._format_message("文本\\r换行")
        expected = "文本\r换行"
        assert result == expected
    
    def test_format_message_remove_trailing_spaces(self):
        """测试去除行尾空格"""
        result = self.notifier._format_message("第一行   \\n第二行\t\\n第三行")
        expected = "第一行\n第二行\n第三行"
        assert result == expected
    
    def test_format_message_remove_extra_empty_lines(self):
        """测试去除多余空行"""
        # 测试多个连续空行
        result = self.notifier._format_message("第一行\\n\\n\\n\\n第二行")
        expected = "第一行\n\n第二行"
        assert result == expected
        
        # 测试开头和结尾的空行
        result = self.notifier._format_message("\\n\\n第一行\\n第二行\\n\\n")
        expected = "第一行\n第二行"
        assert result == expected
    
    def test_format_message_complex_case(self):
        """测试复杂格式化场景"""
        input_text = "\\n\\n  标题  \\n\\n\\n内容第一行   \\n\\n内容第二行\\t\\n\\n\\n"
        result = self.notifier._format_message(input_text)
        expected = "标题\n\n内容第一行\n\n内容第二行"
        assert result == expected
    
    def test_format_message_empty_or_none(self):
        """测试空文本或None"""
        assert self.notifier._format_message("") == ""
        assert self.notifier._format_message(None) is None
        assert self.notifier._format_message("   ") == ""
    
    @patch('feishu.notification.requests.post')
    def test_send_text_with_formatting(self, mock_post):
        """测试发送带格式化的文本消息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_post.return_value = mock_response
        
        # 发送包含转义换行符的消息
        original_text = "测试消息\\n第二行\\n\\n第三行"
        result = self.notifier.send_text(original_text)
        
        assert result is True
        
        # 验证格式化后的消息被发送
        expected_formatted = "测试消息\n第二行\n\n第三行"
        expected_payload = {
            "msg_type": "text",
            "content": {
                "text": expected_formatted
            }
        }
        
        for call in mock_post.call_args_list:
            args, kwargs = call
            assert kwargs['json'] == expected_payload
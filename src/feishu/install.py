#!/usr/bin/env python3
"""安装后脚本

在uv tool install时自动创建配置目录和配置文件。
"""

import os
import shutil
from pathlib import Path


def post_install():
    """安装后执行的脚本
    
    创建配置目录并复制示例配置文件。
    """
    # 获取用户配置目录
    config_dir = Path.home() / ".config" / "smallfeishu"
    config_file = config_dir / "config.toml"
    
    # 创建配置目录
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果配置文件不存在，创建示例配置
    if not config_file.exists():
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
        
        print(f"\n✅ 飞书命令行工具安装成功！")
        print(f"\n📁 配置文件已创建: {config_file}")
        print(f"\n🔧 请编辑配置文件，将 YOUR_WEBHOOK_TOKEN_HERE 替换为真实的飞书机器人webhook地址")
        print(f"\n💡 使用以下命令查看配置文件位置:")
        print(f"   feishu config show")
        print(f"\n🚀 配置完成后，使用以下命令测试:")
        print(f"   feishu test")
        print(f"\n📖 更多信息请查看文档: https://github.com/yourusername/smallfeishu")
    else:
        print(f"\n✅ 飞书命令行工具安装成功！")
        print(f"\n📁 配置文件已存在: {config_file}")
        print(f"\n💡 使用 feishu config show 查看当前配置")


if __name__ == "__main__":
    post_install()
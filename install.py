#!/usr/bin/env python3
"""
安装后脚本 - 自动创建配置文件和显示帮助信息

在 uv tool install 时自动执行，创建默认配置文件并显示使用指南。
"""

import sys
from pathlib import Path


def create_config_file():
    """创建默认配置文件"""
    # 获取配置目录路径
    config_dir = Path.home() / ".config" / "smallfeishu"
    config_file = config_dir / "config.toml"
    
    # 创建配置目录
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ 创建配置目录失败: {e}")
        return False
    
    # 如果配置文件已存在，不覆盖
    if config_file.exists():
        print(f"ℹ️  配置文件已存在: {config_file}")
        return True
    
    # 示例配置内容
    config_content = """# 飞书通知配置文件
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
    
    # 写入配置文件
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False
    
    return True


def show_installation_info():
    """显示安装完成信息和使用指南"""
    config_file = Path.home() / ".config" / "smallfeishu" / "config.toml"
    
    print("\n🎉 SmallFeishu 安装完成！")
    print(f"\n📁 配置文件已创建: {config_file}")
    print("\n🔧 接下来的步骤:")
    print("   1. 获取飞书机器人webhook地址:")
    print("      - 在飞书群聊中添加自定义机器人")
    print("      - 复制生成的webhook地址")
    print("   2. 编辑配置文件:")
    print(f"      - 打开文件: {config_file}")
    print("      - 将 YOUR_WEBHOOK_TOKEN_HERE 替换为真实的webhook地址")
    print("   3. 测试配置:")
    print("      feishu test")
    print("   4. 发送第一条消息:")
    print("      feishu send \"Hello World\"")
    print("\n📋 配置管理命令:")
    print("   feishu config show    # 显示当前配置")
    print("   feishu config path    # 显示配置文件路径")
    print("   feishu config init    # 重新初始化配置")
    print("\n📖 更多帮助:")
    print("   feishu --help         # 查看所有命令")
    print("   feishu send --help    # 查看发送命令帮助")
    print("\n📚 文档: https://github.com/your-repo/smallfeishu")
    print("\n✨ 开始使用飞书通知吧！")


def main():
    """主函数 - 安装后脚本入口点"""
    try:
        # 创建配置文件
        if create_config_file():
            # 显示安装信息
            show_installation_info()
        else:
            print("❌ 安装过程中出现错误")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 安装过程中出现未知错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
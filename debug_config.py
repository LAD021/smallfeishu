#!/usr/bin/env python3
"""调试配置读取问题"""

import toml
from pathlib import Path

def debug_config():
    config_file = Path("config.toml")
    
    print(f"配置文件存在: {config_file.exists()}")
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"配置文件原始内容:\n{content}")
            
        config_data = toml.load(config_file)
        print(f"解析后的配置数据: {config_data}")
        
        print(f"是否包含'feishu'键: {'feishu' in config_data}")
        if 'feishu' in config_data:
            print(f"feishu配置: {config_data['feishu']}")
        
        print(f"是否包含'notifications'键: {'notifications' in config_data}")
        if 'notifications' in config_data:
            print(f"notifications配置: {config_data['notifications']}")

if __name__ == "__main__":
    debug_config()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块 - 处理应用程序配置
"""

import os
import json
from pathlib import Path

class Config:
    """配置管理类，处理应用程序配置的加载、保存和访问"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 用户主目录
        self.user_home = str(Path.home())
        # 应用数据目录
        self.app_data_dir = os.path.join(self.user_home, ".enPDF2zhMD")
        # 配置文件路径
        self.config_file = os.path.join(self.app_data_dir, "config.json")
        # 临时文件目录
        self.temp_dir = os.path.join(self.app_data_dir, "temp")
        # 历史记录文件
        self.history_file = os.path.join(self.app_data_dir, "history.json")
        
        # 确保应用数据目录存在
        self._ensure_dirs()
        
        # 默认配置
        self.default_config = {
            "api": {
                "url": "https://api.tu-zi.com",
                "key": "",
                "model": "claude-3-7-sonnet-thinking"
            },
            "ui": {
                "theme": "light",
                "language": "zh_CN"
            },
            "conversion": {
                "output_format": "zip",
                "keep_temp_files": False
            },
            "marker": {
                "force_ocr": False,
                "extract_images": True
            }
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def _ensure_dirs(self):
        """确保必要的目录结构存在"""
        os.makedirs(self.app_data_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 将加载的配置与默认配置合并，确保所有必要的配置项都存在
                return self._merge_configs(self.default_config, config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.default_config
        else:
            # 保存默认配置
            self.save_config(self.default_config)
            return self.default_config
    
    def _merge_configs(self, default, loaded):
        """合并配置，确保所有默认配置项存在"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值，支持点分隔符访问嵌套配置"""
        parts = key.split('.')
        value = self.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置配置值，支持点分隔符访问嵌套配置"""
        parts = key.split('.')
        config = self.config
        for i, part in enumerate(parts[:-1]):
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value
        self.save_config()
        
    def get_session_dir(self, session_id):
        """获取特定会话的临时目录"""
        session_dir = os.path.join(self.temp_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def get_history(self):
        """获取转换历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def add_history_entry(self, entry):
        """添加一条历史记录"""
        history = self.get_history()
        history.insert(0, entry)  # 将新记录添加到列表开头
        # 限制历史记录数量
        if len(history) > 50:
            history = history[:50]
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
            return True
        except:
            return False 
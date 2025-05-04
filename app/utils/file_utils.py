#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件操作工具模块 - 处理文件和目录操作
"""

import os
import shutil
import zipfile
import uuid
import datetime
from pathlib import Path

def create_unique_id():
    """创建唯一会话ID"""
    return str(uuid.uuid4())

def get_file_name(file_path):
    """获取文件名（不含扩展名）"""
    return os.path.splitext(os.path.basename(file_path))[0]

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    os.makedirs(directory, exist_ok=True)
    return directory

def clean_temp_files(directory, max_age_days=7):
    """清理指定目录中的临时文件
    
    Args:
        directory: 目录路径
        max_age_days: 文件最大保留天数
    """
    if not os.path.exists(directory):
        return
    
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=max_age_days)
    
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        # 检查文件/目录的最后修改时间
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
        
        if mtime < cutoff:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"清理文件失败: {item_path}, 错误: {e}")

def create_zip_archive(source_dir, output_path, base_dir=None):
    """将源目录中的文件创建为zip压缩包
    
    Args:
        source_dir: 源目录
        output_path: 输出文件路径
        base_dir: 压缩包内基础目录名，默认为源目录的基本名称
    
    Returns:
        bool: 是否成功创建
    """
    if not os.path.exists(source_dir):
        return False
    
    if base_dir is None:
        base_dir = os.path.basename(source_dir)
    
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(base_dir, os.path.relpath(file_path, source_dir))
                    zipf.write(file_path, arcname)
        return True
    except Exception as e:
        print(f"创建ZIP文件失败: {e}")
        return False

def copy_directory(src, dst):
    """复制目录内容
    
    Args:
        src: 源目录
        dst: 目标目录
    """
    ensure_dir(dst)
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def is_valid_pdf(file_path):
    """检查文件是否为有效的PDF
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为有效PDF
    """
    if not os.path.exists(file_path):
        return False
    
    # 检查文件扩展名
    if not file_path.lower().endswith('.pdf'):
        return False
    
    # 检查文件头部是否包含PDF签名
    try:
        with open(file_path, 'rb') as f:
            header = f.read(1024)
            return header.startswith(b'%PDF-')
    except:
        return False 
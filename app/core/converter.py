#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF转换器模块 - 将PDF转换为Markdown
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path

class PDFConverter:
    """PDF转Markdown转换器类，使用Marker-PDF库"""
    
    def __init__(self, config):
        """初始化转换器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger("PDFConverter")
    
    def convert_pdf_to_markdown(self, pdf_path, output_dir):
        """将PDF转换为Markdown
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录路径
            
        Returns:
            tuple: (bool, str) - (是否成功, Markdown文件路径或错误消息)
        """
        try:
            # 检查marker-pdf已安装，但继续执行即使检查失败
            self._ensure_marker_installed()
            
            # 构建marker命令行参数
            cmd = [
                "marker_single",
                pdf_path,
                "--output_dir", output_dir
            ]
            
            # 添加可选配置参数
            if self.config.get("marker.force_ocr", False):
                cmd.append("--force_ocr")
            
            if not self.config.get("marker.extract_images", True):
                cmd.append("--disable_image_extraction")
            
            # 执行命令
            self.logger.info(f"正在执行命令: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            # 检查是否成功
            if process.returncode != 0:
                self.logger.error(f"转换失败: {stderr}")
                return False, f"PDF转换失败: {stderr}"
            
            # 查找生成的Markdown文件
            markdown_file = self._find_markdown_file(output_dir)
            if not markdown_file:
                return False, "无法找到生成的Markdown文件"
            
            return True, markdown_file
        
        except Exception as e:
            self.logger.exception("PDF转换过程出错")
            return False, f"PDF转换过程出错: {str(e)}"
    
    def _ensure_marker_installed(self):
        """确保marker-pdf已安装"""
        try:
            result = subprocess.run(
                ["marker_single", "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode != 0:
                self.logger.warning("marker-pdf命令行工具检查失败，但将继续尝试使用")
                self.logger.debug(f"错误输出: {result.stderr.decode('utf-8', errors='ignore')}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"检查marker-pdf安装时出错: {str(e)}")
            self.logger.warning("将继续尝试PDF转换过程")
            return False
    
    def _find_markdown_file(self, directory):
        """在给定目录中查找生成的Markdown文件（递归搜索子目录）
        
        Args:
            directory: 目录路径
            
        Returns:
            str: Markdown文件路径，如果未找到则返回None
        """
        # 首先检查当前目录
        for file in os.listdir(directory):
            if file.endswith('.md'):
                return os.path.join(directory, file)
        
        # 然后递归检查子目录
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                # 子目录中有可能包含文件名与目录名相同的markdown文件
                md_file = os.path.join(item_path, f"{item}.md")
                if os.path.exists(md_file) and os.path.isfile(md_file):
                    return md_file
                
                # 递归搜索子目录
                result = self._find_markdown_file(item_path)
                if result:
                    return result
        
        return None
    
    def process_pdf(self, pdf_path, session_dir):
        """处理PDF文件的完整流程
        
        Args:
            pdf_path: PDF文件路径
            session_dir: 会话目录路径
            
        Returns:
            tuple: (bool, dict) - (是否成功, 结果信息)
        """
        # 创建输出目录
        markdown_dir = os.path.join(session_dir, "markdown")
        os.makedirs(markdown_dir, exist_ok=True)
        
        # 转换PDF到Markdown
        success, result = self.convert_pdf_to_markdown(pdf_path, markdown_dir)
        
        if not success:
            return False, {"error": result}
        
        # 提取图片目录
        images_dir = os.path.join(markdown_dir, "images")
        if not os.path.exists(images_dir):
            images_dir = None
        
        return True, {
            "markdown_file": result,
            "images_dir": images_dir,
            "base_dir": markdown_dir
        } 
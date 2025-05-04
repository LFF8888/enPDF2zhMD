#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包模块 - 处理资源打包与导出
"""

import os
import shutil
import logging
from datetime import datetime
from app.utils.file_utils import create_zip_archive, ensure_dir, copy_directory

class OutputPackager:
    """输出打包器类，负责处理转换结果的归档和导出"""
    
    def __init__(self, config):
        """初始化打包器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger("OutputPackager")
    
    def package_results(self, session_dir, translated_file, images_dir, output_path=None, original_pdf=None):
        """打包处理结果
        
        Args:
            session_dir: 会话目录
            translated_file: 翻译后的Markdown文件路径
            images_dir: 图片目录路径，可以为None
            output_path: 指定的输出路径，默认为用户目录下的Documents文件夹
            original_pdf: 原始PDF文件路径
            
        Returns:
            tuple: (bool, str) - (是否成功, 输出文件路径或错误消息)
        """
        try:
            # 准备输出目录
            if not output_path:
                documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                output_path = os.path.join(documents_dir, "enPDF2zhMD_Output")
                ensure_dir(output_path)
            
            # 获取当前时间作为输出文件名后缀
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 获取源文件名（不含扩展名）
            base_name = os.path.splitext(os.path.basename(translated_file))[0]
            if base_name.startswith("zh_"):
                base_name = base_name[3:]  # 移除'zh_'前缀
            
            # 创建最终输出目录
            final_dir = os.path.join(output_path, f"{base_name}_{timestamp}")
            ensure_dir(final_dir)
            
            # 复制翻译后的文件到输出目录，添加_zh后缀
            final_md_path = os.path.join(final_dir, f"{base_name}_zh.md")
            shutil.copy2(translated_file, final_md_path)
            self.logger.info(f"复制翻译后的Markdown文件到: {final_md_path}")
            
            # 查找并复制原始英文Markdown文件
            original_md_name = base_name + ".md" if not base_name.endswith(".md") else base_name
            markdown_dir = os.path.join(session_dir, "markdown")
            original_md_path = os.path.join(markdown_dir, original_md_name)
            
            if os.path.exists(original_md_path):
                final_original_md_path = os.path.join(final_dir, f"{base_name}.md")
                shutil.copy2(original_md_path, final_original_md_path)
                self.logger.info(f"复制原始Markdown文件到: {final_original_md_path}")
            
            # 复制原始PDF文件到输出目录（如果有）
            if original_pdf and os.path.exists(original_pdf):
                pdf_name = os.path.basename(original_pdf)
                pdf_output_path = os.path.join(final_dir, pdf_name)
                shutil.copy2(original_pdf, pdf_output_path)
                self.logger.info(f"复制原始PDF文件到: {pdf_output_path}")
            
            # 找到markdown目录
            markdown_dir = os.path.dirname(os.path.dirname(translated_file))
            if os.path.basename(markdown_dir) != "markdown":
                markdown_dir = os.path.join(session_dir, "markdown")
            
            # 直接复制所有图片文件到输出目录根目录，不创建额外的子目录
            if os.path.exists(markdown_dir):
                self.logger.info(f"复制Markdown目录中的图片文件")
                # 遍历markdown目录中的所有文件
                for root, _, files in os.walk(markdown_dir):
                    for file in files:
                        # 跳过markdown文件和元数据文件
                        if file.endswith('.md') or file.endswith('_meta.json') or file == os.path.basename(translated_file):
                            continue
                        
                        # 复制图片等资源文件到输出目录
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(final_dir, file)
                        shutil.copy2(src_path, dst_path)
                        self.logger.info(f"复制资源文件: {src_path} -> {dst_path}")
            
            # 根据配置决定是否创建zip压缩包
            output_format = self.config.get("conversion.output_format", "zip")
            if output_format == "zip":
                zip_path = f"{final_dir}.zip"
                if create_zip_archive(final_dir, zip_path, base_dir=base_name):
                    # 如果不保留临时文件夹，则删除
                    if not self.config.get("conversion.keep_temp_files", False):
                        shutil.rmtree(final_dir)
                    return True, zip_path
            
            # 如果没有创建zip或创建失败，返回文件夹路径
            return True, final_dir
        
        except Exception as e:
            self.logger.exception("打包过程出错")
            return False, f"打包过程出错: {str(e)}"
    
    def cleanup_session(self, session_dir, keep_temp=False):
        """清理会话目录
        
        Args:
            session_dir: 会话目录路径
            keep_temp: 是否保留临时文件，默认为False
            
        Returns:
            bool: 是否成功清理
        """
        if not keep_temp and os.path.exists(session_dir):
            try:
                shutil.rmtree(session_dir)
                return True
            except Exception as e:
                self.logger.error(f"清理会话目录失败: {e}")
                return False
        return True
    
    def process_packaging(self, conversion_results, output_path=None):
        """处理打包流程
        
        Args:
            conversion_results: 转换结果信息字典
            output_path: 指定的输出路径
            
        Returns:
            tuple: (bool, dict) - (是否成功, 结果信息)
        """
        session_dir = conversion_results.get("session_dir")
        translated_file = conversion_results.get("translated_file")
        images_dir = conversion_results.get("images_dir")
        original_pdf = conversion_results.get("original_file")
        
        # 检查必要信息
        if not session_dir or not translated_file:
            return False, {"error": "缺少必要的转换结果信息"}
        
        # 执行打包
        success, result = self.package_results(
            session_dir, 
            translated_file, 
            images_dir, 
            output_path,
            original_pdf
        )
        
        if not success:
            return False, {"error": result}
        
        # 清理临时文件
        keep_temp = self.config.get("conversion.keep_temp_files", False)
        self.cleanup_session(session_dir, keep_temp)
        
        return True, {
            "output_path": result,
            "type": "zip" if result.endswith(".zip") else "directory"
        } 
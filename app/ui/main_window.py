#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块 - 应用程序主界面
"""

import os
import uuid
import threading
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QProgressBar, QFileDialog,
    QListWidget, QListWidgetItem, QSplitter, QMessageBox,
    QGroupBox, QSpacerItem, QSizePolicy, QDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QIcon

from app.ui.settings import SettingsDialog
from app.core.converter import PDFConverter
from app.core.translator import MarkdownTranslator
from app.core.packager import OutputPackager
from app.utils.file_utils import create_unique_id, is_valid_pdf, get_file_name

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ConversionThread(QThread):
    """转换处理线程"""
    # 信号定义
    update_progress = pyqtSignal(int, str)
    conversion_complete = pyqtSignal(bool, dict)
    
    def __init__(self, config, pdf_path, output_path=None):
        """初始化转换线程
        
        Args:
            config: 配置对象
            pdf_path: PDF文件路径
            output_path: 输出路径，可选
        """
        super().__init__()
        self.config = config
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.session_id = create_unique_id()
        
        # 获取会话目录
        self.session_dir = config.get_session_dir(self.session_id)
        
        # 创建处理器实例
        self.pdf_converter = PDFConverter(config)
        self.translator = MarkdownTranslator(config)
        self.packager = OutputPackager(config)
    
    def run(self):
        """线程运行函数"""
        try:
            # 步骤1: PDF转Markdown
            self.update_progress.emit(10, "正在将PDF转换为Markdown...")
            success, pdf_result = self.pdf_converter.process_pdf(
                self.pdf_path, 
                self.session_dir
            )
            
            if not success:
                self.conversion_complete.emit(False, pdf_result)
                return
            
            # 步骤2: Markdown翻译
            self.update_progress.emit(40, "正在翻译Markdown内容...")
            success, translate_result = self.translator.process_translation(
                pdf_result["markdown_file"],
                self.session_dir
            )
            
            if not success:
                self.conversion_complete.emit(False, translate_result)
                return
            
            # 步骤3: 打包输出
            self.update_progress.emit(80, "正在打包结果...")
            
            # 合并处理结果
            conversion_results = {
                "session_dir": self.session_dir,
                "translated_file": translate_result["translated_file"],
                "images_dir": pdf_result.get("images_dir"),
                "original_file": self.pdf_path
            }
            
            success, package_result = self.packager.process_packaging(
                conversion_results,
                self.output_path
            )
            
            if not success:
                self.conversion_complete.emit(False, package_result)
                return
            
            # 完成
            self.update_progress.emit(100, "转换完成！")
            
            # 添加其他信息到结果
            result = package_result.copy()
            result["original_file"] = self.pdf_path
            result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["file_name"] = get_file_name(self.pdf_path)
            
            self.conversion_complete.emit(True, result)
            
        except Exception as e:
            logging.exception("转换过程中发生错误")
            self.conversion_complete.emit(False, {"error": str(e)})


class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self, config):
        """初始化主窗口
        
        Args:
            config: 配置对象
        """
        super().__init__()
        self.config = config
        self.logger = logging.getLogger("MainWindow")
        
        # 设置窗口属性
        self.setWindowTitle("enPDF2zhMD - 英文PDF转中文Markdown工具")
        self.setMinimumSize(900, 600)
        
        # 设置UI
        self.setup_ui()
        
        # 加载历史记录
        self.load_history()
        
        # 初始状态
        self.conversion_thread = None
        self.set_ready_state()
    
    def setup_ui(self):
        """设置UI组件"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧历史面板
        history_panel = self.create_history_panel()
        splitter.addWidget(history_panel)
        
        # 右侧主面板
        main_panel = self.create_main_panel()
        splitter.addWidget(main_panel)
        
        # 设置分割比例
        splitter.setSizes([200, 700])
    
    def create_history_panel(self):
        """创建历史记录面板
        
        Returns:
            QWidget: 历史记录面板控件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title = QLabel("转换历史")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        layout.addWidget(self.history_list)
        
        # 清理按钮
        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)
        
        return widget
    
    def create_main_panel(self):
        """创建主面板
        
        Returns:
            QWidget: 主面板控件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title = QLabel("enPDF2zhMD - 英文PDF转中文Markdown工具")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 文件选择区域
        file_group = QGroupBox("选择文件")
        file_layout = QVBoxLayout()
        
        file_btn_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        self.file_btn = QPushButton("选择PDF文件")
        self.file_btn.setObjectName("fileButton")
        self.file_btn.clicked.connect(self.select_file)
        file_btn_layout.addWidget(self.file_path_label)
        file_btn_layout.addWidget(self.file_btn)
        
        file_layout.addLayout(file_btn_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 输出设置区域
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout()
        
        output_btn_layout = QHBoxLayout()
        self.output_path_label = QLabel("默认输出目录")
        self.output_btn = QPushButton("选择输出目录")
        self.output_btn.clicked.connect(self.select_output_dir)
        output_btn_layout.addWidget(self.output_path_label)
        output_btn_layout.addWidget(self.output_btn)
        
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 进度区域
        progress_group = QGroupBox("转换进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始转换")
        self.start_btn.clicked.connect(self.start_conversion)
        
        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.show_settings)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.settings_btn)
        
        layout.addLayout(btn_layout)
        
        # 添加弹性空间
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return widget
    
    def select_file(self):
        """选择PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        
        if file_path:
            # 验证是否为有效的PDF
            if not is_valid_pdf(file_path):
                QMessageBox.warning(self, "无效文件", "所选文件不是有效的PDF文件。")
                return
            
            self.file_path_label.setText(file_path)
            self.set_ready_state()
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", ""
        )
        
        if dir_path:
            self.output_path_label.setText(dir_path)
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self)
        result = dialog.exec_()
        
        # 如果用户点击了确定/保存按钮
        if result == QDialog.Accepted:
            # 配置已在对话框中自动保存
            pass
    
    def start_conversion(self):
        """开始转换流程"""
        # 检查是否有选择文件
        pdf_path = self.file_path_label.text()
        if pdf_path == "未选择文件":
            QMessageBox.warning(self, "未选择文件", "请先选择要转换的PDF文件。")
            return
        
        # 检查是否有API密钥
        api_key = self.config.get("api.key")
        if not api_key:
            result = QMessageBox.question(
                self,
                "缺少API密钥",
                "您尚未设置API密钥。要现在设置吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if result == QMessageBox.Yes:
                self.show_settings()
                return
        
        # 获取输出目录
        output_path = self.output_path_label.text()
        if output_path == "默认输出目录":
            output_path = None
        
        # 设置处理状态
        self.set_processing_state()
        
        # 创建并启动转换线程
        self.conversion_thread = ConversionThread(self.config, pdf_path, output_path)
        self.conversion_thread.update_progress.connect(self.update_progress)
        self.conversion_thread.conversion_complete.connect(self.on_conversion_complete)
        self.conversion_thread.start()
    
    def update_progress(self, value, status):
        """更新进度条和状态
        
        Args:
            value: 进度值(0-100)
            status: 状态描述
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def on_conversion_complete(self, success, result):
        """转换完成的回调
        
        Args:
            success: 是否成功
            result: 结果信息
        """
        if success:
            self.set_complete_state()
            
            # 添加到历史记录
            self.add_history_item(result)
            
            # 显示成功信息
            QMessageBox.information(
                self,
                "转换完成",
                f"PDF转换已完成！\n\n输出位置: {result['output_path']}"
            )
            
        else:
            self.set_ready_state()
            
            # 显示错误信息
            error_msg = result.get("error", "未知错误")
            error_title = "转换失败"
            
            # 根据错误消息提供更具体的提示
            if "API" in error_msg and ("密钥" in error_msg or "配额" in error_msg or "key" in error_msg):
                error_title = "API调用错误"
                error_msg += "\n\n请检查API设置，确保密钥正确且有足够的配额。"
            elif "PDF转换" in error_msg:
                error_title = "PDF转换错误"
                error_msg += "\n\n请确保PDF文件有效且格式正确。"
            elif "翻译" in error_msg:
                error_title = "翻译错误"
                error_msg += "\n\n翻译过程中出现问题，请稍后重试。"
            
            QMessageBox.critical(
                self,
                error_title,
                f"转换过程中出现错误：\n{error_msg}"
            )
    
    def set_ready_state(self):
        """设置就绪状态"""
        self.start_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("就绪")
    
    def set_processing_state(self):
        """设置处理中状态"""
        self.start_btn.setEnabled(False)
        self.file_btn.setEnabled(False)
        self.output_btn.setEnabled(False)
        self.settings_btn.setEnabled(False)
        self.progress_bar.setValue(10)
        self.status_label.setText("处理中...")
    
    def set_complete_state(self):
        """设置完成状态"""
        self.start_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_label.setText("转换完成！")
    
    def add_history_item(self, result):
        """添加历史记录项
        
        Args:
            result: 转换结果信息
        """
        # 创建历史记录条目
        file_name = result.get("file_name", "未知文件")
        timestamp = result.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        output_path = result.get("output_path", "")
        
        item_data = {
            "file_name": file_name,
            "timestamp": timestamp,
            "output_path": output_path,
            "output_type": result.get("type", "directory")
        }
        
        # 添加到配置历史记录
        self.config.add_history_entry(item_data)
        
        # 添加到列表控件
        self.add_history_list_item(item_data)
    
    def add_history_list_item(self, item_data):
        """添加项目到历史记录列表
        
        Args:
            item_data: 项目数据
        """
        item = QListWidgetItem(f"{item_data['file_name']} ({item_data['timestamp']})")
        item.setData(Qt.UserRole, item_data)
        self.history_list.insertItem(0, item)
    
    def load_history(self):
        """加载历史记录"""
        history = self.config.get_history()
        
        self.history_list.clear()
        for item_data in history:
            self.add_history_list_item(item_data)
    
    def clear_history(self):
        """清空历史记录"""
        result = QMessageBox.question(
            self,
            "清空历史",
            "确定要清空所有历史记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # 清空列表
            self.history_list.clear()
            
            # 清空配置中的历史记录
            self.config.add_history_entry([])  # 覆盖为空列表
    
    def on_history_item_clicked(self, item):
        """当历史记录项被点击时的处理
        
        Args:
            item: 被点击的列表项
        """
        # 获取项目数据
        item_data = item.data(Qt.UserRole)
        
        # 显示详情
        output_path = item_data.get("output_path", "")
        
        if output_path and os.path.exists(output_path):
            result = QMessageBox.question(
                self,
                "历史记录",
                f"文件: {item_data.get('file_name')}\n"
                f"时间: {item_data.get('timestamp')}\n\n"
                f"输出位置: {output_path}\n\n"
                "是否打开输出位置？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if result == QMessageBox.Yes:
                # 打开输出位置
                self.open_output_location(output_path)
        else:
            QMessageBox.information(
                self,
                "历史记录",
                f"文件: {item_data.get('file_name')}\n"
                f"时间: {item_data.get('timestamp')}\n\n"
                "输出文件已不存在。"
            )
    
    def open_output_location(self, path):
        """打开输出位置
        
        Args:
            path: 文件或目录路径
        """
        try:
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                # Windows系统使用explorer
                subprocess.Popen(["explorer", os.path.dirname(path)])
            elif platform.system() == "Darwin":
                # macOS系统使用open
                subprocess.Popen(["open", os.path.dirname(path)])
            else:
                # Linux系统使用xdg-open
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        except Exception as e:
            logging.exception("打开输出位置时发生错误")
            QMessageBox.critical(
                self,
                "错误",
                f"打开输出位置时发生错误：\n{str(e)}"
            )
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置界面模块 - 提供配置参数设置界面
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QFormLayout, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    """应用程序设置对话框"""
    
    def __init__(self, config, parent=None):
        """初始化设置对话框
        
        Args:
            config: 配置对象
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建选项卡
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # API设置选项卡
        api_tab = QWidget()
        tabs.addTab(api_tab, "API设置")
        self.setup_api_tab(api_tab)
        
        # 转换设置选项卡
        conversion_tab = QWidget()
        tabs.addTab(conversion_tab, "转换设置")
        self.setup_conversion_tab(conversion_tab)
        
        # 界面设置选项卡
        ui_tab = QWidget()
        tabs.addTab(ui_tab, "界面设置")
        self.setup_ui_tab(ui_tab)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def setup_api_tab(self, tab):
        """设置API选项卡
        
        Args:
            tab: 选项卡控件
        """
        layout = QVBoxLayout(tab)
        
        # API 设置组
        api_group = QGroupBox("API 配置")
        form_layout = QFormLayout()
        
        # API URL
        self.api_url = QLineEdit()
        form_layout.addRow("API URL:", self.api_url)
        
        # API 密钥
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        form_layout.addRow("API 密钥:", self.api_key)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "grok-beta",
        ])
        self.model_combo.setEditable(True)
        form_layout.addRow("模型:", self.model_combo)
        
        api_group.setLayout(form_layout)
        layout.addWidget(api_group)
        layout.addStretch()
    
    def setup_conversion_tab(self, tab):
        """设置转换选项卡
        
        Args:
            tab: 选项卡控件
        """
        layout = QVBoxLayout(tab)
        
        # Marker 设置组
        marker_group = QGroupBox("Marker 设置")
        marker_layout = QVBoxLayout()
        
        self.force_ocr = QCheckBox("强制OCR（对扫描PDF更好）")
        marker_layout.addWidget(self.force_ocr)
        
        self.extract_images = QCheckBox("提取图像")
        self.extract_images.setChecked(True)
        marker_layout.addWidget(self.extract_images)
        
        marker_group.setLayout(marker_layout)
        layout.addWidget(marker_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout()
        
        self.output_format = QComboBox()
        self.output_format.addItems(["zip", "directory"])
        output_layout.addWidget(QLabel("输出格式:"))
        output_layout.addWidget(self.output_format)
        
        self.keep_temp = QCheckBox("保留临时文件")
        output_layout.addWidget(self.keep_temp)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
    
    def setup_ui_tab(self, tab):
        """设置界面选项卡
        
        Args:
            tab: 选项卡控件
        """
        layout = QVBoxLayout(tab)
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout()
        
        self.theme = QComboBox()
        self.theme.addItems(["light", "dark"])
        theme_layout.addWidget(QLabel("主题:"))
        theme_layout.addWidget(self.theme)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # 语言设置
        lang_group = QGroupBox("语言设置")
        lang_layout = QVBoxLayout()
        
        self.language = QComboBox()
        self.language.addItems(["zh_CN", "en_US"])
        lang_layout.addWidget(QLabel("界面语言:"))
        lang_layout.addWidget(self.language)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        layout.addStretch()
    
    def load_settings(self):
        """从配置加载设置"""
        # API设置
        self.api_url.setText(self.config.get("api.url", "https://api.tu-zi.com"))
        self.api_key.setText(self.config.get("api.key", ""))
        
        model = self.config.get("api.model", "claude-3-7-sonnet-thinking")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.setCurrentText(model)
        
        # 转换设置
        self.force_ocr.setChecked(self.config.get("marker.force_ocr", False))
        self.extract_images.setChecked(self.config.get("marker.extract_images", True))
        
        output_format = self.config.get("conversion.output_format", "zip")
        self.output_format.setCurrentText(output_format)
        self.keep_temp.setChecked(self.config.get("conversion.keep_temp_files", False))
        
        # UI设置
        theme = self.config.get("ui.theme", "light")
        self.theme.setCurrentText(theme)
        
        language = self.config.get("ui.language", "zh_CN")
        self.language.setCurrentText(language)
    
    def save_settings(self):
        """保存设置到配置"""
        # API设置
        self.config.set("api.url", self.api_url.text())
        self.config.set("api.key", self.api_key.text())
        self.config.set("api.model", self.model_combo.currentText())
        
        # 转换设置
        self.config.set("marker.force_ocr", self.force_ocr.isChecked())
        self.config.set("marker.extract_images", self.extract_images.isChecked())
        
        self.config.set("conversion.output_format", self.output_format.currentText())
        self.config.set("conversion.keep_temp_files", self.keep_temp.isChecked())
        
        # UI设置
        self.config.set("ui.theme", self.theme.currentText())
        self.config.set("ui.language", self.language.currentText())
        
        self.accept() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
enPDF2zhMD - 英文PDF自动转换为中文Markdown工具
"""

import sys
import os
from app.ui.main_window import MainWindow
from app.utils.config import Config

def main():
    """应用程序主入口"""
    # 初始化配置
    config = Config()
    
    # 创建并启动GUI应用
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setApplicationName("enPDF2zhMD")
    
    # 设置样式表
    with open(os.path.join(os.path.dirname(__file__), "resources", "style.css"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    # 创建主窗口
    window = MainWindow(config)
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
# enPDF2zhMD

<div align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Language-English-blue" alt="English"></a>
  <a href="README_zh.md"><img src="https://img.shields.io/badge/语言-中文-red" alt="中文"></a>
</div>

英文PDF自动转换为中文Markdown工具

## 项目介绍

enPDF2zhMD是一个桌面应用程序，可以将英文PDF文档自动转换为中文Markdown文本，同时保留原始文档的格式和图片。

主要功能：
- 自动解析英文PDF文档结构
- 提取并保存图片资源
- 使用AI接口翻译为中文
- 保留原始格式（标题、列表、表格、代码块等）
- 输出为Markdown文档或压缩包

## 安装使用

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/LFF8888/enPDF2zhMD.git
cd enPDF2zhMD
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python main.py
```

### 使用方法

1. 点击"选择PDF文件"按钮，选择要转换的英文PDF文档
2. 可选：点击"设置"按钮，配置API参数和转换选项
3. 点击"开始转换"按钮开始处理
4. 转换完成后，可以在输出位置找到转换结果

## 配置说明

首次运行时，请在"设置"中配置以下参数：

- API URL: 翻译服务的API地址，默认为https://api.tu-zi.com
- API密钥: 从服务提供商获取的密钥（通过网站获得）
- 模型: 使用的AI模型，推荐使用grok-beta

## API邀请链接

这是作者的API邀请链接，邀请好友注册，我可获得 $0.5 额度。好友可获得 $1 额度。
https://api.tu-zi.com/register?aff=HyTx

## 技术架构

本项目使用以下技术：

- 核心功能: PDF解析、AI翻译、资源管理
- 界面: PyQt5构建的现代GUI
- PDF处理: Marker-PDF库
- 翻译: OpenAI兼容API接口

## 贡献代码

欢迎提交Issues和Pull Requests。

## 许可证

MIT License 
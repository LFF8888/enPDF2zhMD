# enPDF2zhMD

<div align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Language-English-blue" alt="English"></a>
  <a href="README_zh.md"><img src="https://img.shields.io/badge/语言-中文-red" alt="中文"></a>
</div>

A tool for converting English PDF documents to Chinese Markdown.

## Introduction

enPDF2zhMD is a desktop application that automatically converts English PDF documents into Chinese Markdown text while preserving the original document's format and images.

Key features:
- Automatic parsing of English PDF document structure
- Extraction and saving of image resources
- Translation to Chinese using AI API
- Preservation of original formatting (headings, lists, tables, code blocks, etc.)
- Output as Markdown document or compressed package

## Installation and Usage

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/LFF8888/enPDF2zhMD.git
cd enPDF2zhMD
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

### Usage Instructions

1. Click the "Select PDF File" button to choose the English PDF document to convert
2. Optional: Click the "Settings" button to configure API parameters and conversion options
3. Click the "Start Conversion" button to begin processing
4. After conversion is complete, you can find the conversion result at the output location

## Configuration 

When running for the first time, please configure the following parameters in "Settings":

- API URL: The API address of the translation service, default is https://api.tu-zi.com
- API Key: The key obtained from the service provider (via website)
- Model: The AI model used, recommended to use grok-beta

## API Invitation Link

This is the author's API invitation link. When you invite friends to register, the author receives $0.5 credit and your friend receives $1 credit.
https://api.tu-zi.com/register?aff=HyTx

## Technical Architecture

This project uses the following technologies:

- Core functionality: PDF parsing, AI translation, resource management
- Interface: Modern GUI built with PyQt5
- PDF processing: Marker-PDF library
- Translation: OpenAI compatible API interface

## Contribution

Issues and Pull Requests are welcome.

## License

MIT License

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译器模块 - 使用AI接口将英文Markdown翻译为中文
"""

import os
import logging
from openai import OpenAI

class MarkdownTranslator:
    """Markdown翻译器类，使用AI API翻译英文为中文"""
    
    def __init__(self, config):
        """初始化翻译器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger("MarkdownTranslator")
        
        # 获取API配置
        self.api_url = self.config.get("api.url", "https://api.tu-zi.com")
        self.api_key = self.config.get("api.key", "sk-qqSS4bq8L0FkypqiofgZbfkfCzG62r19mJ101MfE3GArEfNl")
        self.model = self.config.get("api.model", "claude-3-7-sonnet-thinking")
        
        # 初始化OpenAI客户端
        self.client = None
    
    def translate_markdown(self, markdown_file, output_path):
        """翻译Markdown文件
        
        Args:
            markdown_file: Markdown文件路径
            output_path: 输出文件路径
            
        Returns:
            tuple: (bool, str) - (是否成功, 输出文件路径或错误消息)
        """
        try:
            # 读取Markdown内容
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"读取Markdown文件: {markdown_file}, 内容长度: {len(content)}字符")
            
            # 翻译内容
            translated_content = self._translate(content)
            if not translated_content:
                return False, "翻译失败，API返回为空"
            
            # 保存翻译结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            self.logger.info(f"翻译结果已保存到: {output_path}, 长度: {len(translated_content)}字符")
            return True, output_path
        
        except Exception as e:
            self.logger.exception("翻译过程出错")
            return False, f"翻译过程出错: {str(e)}"
    
    def _translate(self, content):
        """调用API翻译内容
        
        Args:
            content: 要翻译的内容
            
        Returns:
            str: 翻译后的内容，失败返回None
        """
        try:
            # 确保API密钥已设置
            if not self.api_key:
                self.logger.error("API密钥未设置")
                return None
            
            # 初始化客户端
            if not self.client:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=f"{self.api_url}/v1",
                    timeout=600,  # 设置客户端请求超时时间为10分钟
                    max_retries=0  # 限制最大重试次数
                )
            
            # 构建翻译提示词
            system_prompt = "你是一个专业的翻译助手，可以将英文精确翻译为中文。"
            user_prompt = self._build_translation_prompt(content)
            
            # 记录构建的prompt内容
            self.logger.info(f"构建的system prompt: {system_prompt}")
            self.logger.info(f"构建的user prompt开始 ==================")
            self.logger.info(f"{user_prompt}")
            self.logger.info(f"构建的user prompt结束 ==================")
            
            self.logger.info(f"正在调用API：{self.api_url}，模型：{self.model}，内容长度：{len(content)}字符")
            
            # 发送请求
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # 降低温度使输出更确定性
            )
            
            # 提取翻译内容
            if response and response.choices and len(response.choices) > 0:
                translated_content = response.choices[0].message.content
                self.logger.info(f"翻译内容长度: {len(translated_content)}字符")
                
                # 将完整的API返回内容记录到日志
                self.logger.info(f"API返回内容开始 ==================")
                self.logger.info(f"{translated_content}")
                self.logger.info(f"API返回内容结束 ==================")
                
                return translated_content
            else:
                self.logger.error("API响应格式错误")
                return None
            
        except Exception as e:
            error_msg = str(e)
            self.logger.exception(f"API调用失败: {error_msg}")
            
            # 提供友好的错误信息
            if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                self.logger.error("API配额不足，请更新API密钥或充值账户")
            elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                self.logger.error("API认证失败，请检查API密钥是否正确")
            elif "timeout" in error_msg.lower():
                self.logger.error("请求超时，请检查网络连接或稍后重试")
            
            return None
    
    def _build_translation_prompt(self, content):
        """构建翻译提示词
        
        Args:
            content: 原始内容
            
        Returns:
            str: 翻译提示词
        """
        return f"""请将以下英文Markdown文档翻译成中文，必须遵循以下规则：

整理为标准的markdown语法，将内容翻译为流利的中文（好理解的主谓宾顺序，汉语习惯，可适当拆分原文的长句，或变换句式）。
一些惯用术语可保留英语，首次出现的英文缩写需要用括号说明。
图和表格的标题也要翻译（嵌入引用位置附近），表格整理为标准的markdown语法或简洁的html语法。
图表的链接保持原样。所有公式（$行内公式$、$$行间公式$$）使用标准的LaTeX语法。
返回翻译后的完整Markdown内容！不要遗漏！也不要增加原文没有的内容！不要包裹一层```markdown```

待翻译内容：

```markdown
{content}
```"""
    
    def process_translation(self, markdown_file, session_dir):
        """处理翻译的完整流程
        
        Args:
            markdown_file: Markdown文件路径
            session_dir: 会话目录路径
            
        Returns:
            tuple: (bool, dict) - (是否成功, 结果信息)
        """
        # 创建翻译输出目录
        translated_dir = os.path.join(session_dir, "translated")
        os.makedirs(translated_dir, exist_ok=True)
        
        # 生成输出文件路径
        file_name = os.path.basename(markdown_file)
        output_path = os.path.join(translated_dir, f"zh_{file_name}")
        
        # 翻译Markdown
        success, result = self.translate_markdown(markdown_file, output_path)
        
        if not success:
            return False, {"error": result}
        
        return True, {
            "translated_file": result
        } 
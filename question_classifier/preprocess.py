# -*- coding: utf-8 -*-
"""
文本预处理模块
"""
import re


def clean_text(text):
    """
    清洗题目文本
    
    处理内容：
    1. 去除题号（如：1. 、（一）、第3题）
    2. 合并多余空白
    3. 去除不可见字符
    4. 保留公式（LaTeX或Unicode）
    """
    if not isinstance(text, str):
        text = str(text)
    
    # 去除开头的题号
    # 匹配：1. 、1、、（1）、(1)、第1题、一、、（一）等
    text = re.sub(r'^[\s]*[\d一二三四五六七八九十]+[\s]*[\.、．)\）】]\s*', '', text)
    text = re.sub(r'^[\s]*[（\(][\d一二三四五六七八九十]+[）\)]\s*', '', text)
    text = re.sub(r'^[\s]*第[\d一二三四五六七八九十]+[题问]\s*', '', text)
    
    # 去除选项标记前的多余换行，但保留选项内容
    text = re.sub(r'\n+\s*([A-D])[\.、．]\s*', r' \1. ', text)
    
    # 合并多余空白（保留单个空格）
    text = re.sub(r'[\s]+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def prepare_input_text(row):
    """
    准备模型输入文本
    
    将题目各部分拼接为统一输入格式
    """
    text = str(row.get('题目内容', ''))
    return clean_text(text)


if __name__ == '__main__':
    # 测试
    test_cases = [
        "1. 下列关于细胞的说法，正确的是（）A. 选项1 B. 选项2",
        "（一）阅读下面的文章，完成小题。",
        "第3题 计算下列各式的值",
        "  15．已知函数f(x)=x²+1，求f(2)的值。",
    ]
    
    for text in test_cases:
        print(f"原文: {text[:50]}...")
        print(f"清洗: {clean_text(text)[:50]}...")
        print()

# -*- coding: utf-8 -*-
"""
文本预处理模块
"""
import re


CHOICE_OPTION_PATTERN = re.compile(r'(?:^|[\s（(])([A-D])[\.\、．\)）:：]\s*')
CHOICE_KEYWORD_PATTERN = re.compile(r'(选择题|单选|多选|不定项选择)')


def extract_choice_signals(text):
    """
    提取选择题特征信号

    Returns:
        dict: {
            "option_count": 选项数量,
            "has_choice_keyword": 是否包含选择题关键词,
            "has_blank_marks": 是否包含填空标记,
            "has_sub_questions": 是否包含小题序号,
            "is_choice_like": 是否判定为选择题
        }
    """
    if not isinstance(text, str):
        text = str(text)

    option_matches = CHOICE_OPTION_PATTERN.findall(text)
    option_count = len(set(option_matches))
    has_choice_keyword = bool(CHOICE_KEYWORD_PATTERN.search(text))

    # 检测填空标记（3个以上连续下划线）
    has_blank_marks = bool(re.search(r'_{3,}', text))

    # 检测小题序号（1. 2. 3. 等带问号的小题）
    has_sub_questions = bool(re.search(r'[1-5]\.\s*\w+.*[?？]', text))

    # 综合判定逻辑：
    # 1. 有选项（>=2） -> 选择题
    # 2. 有选择题关键词 -> 选择题
    # 3. 填空标记+选项 -> 填空形式的选择题
    # 4. 小题序号+选项 -> 材料+选择题
    is_choice_like = (
        option_count >= 2 or
        has_choice_keyword or
        (has_blank_marks and option_count >= 2) or
        (has_sub_questions and option_count >= 2)
    )

    return {
        "option_count": option_count,
        "has_choice_keyword": has_choice_keyword,
        "has_blank_marks": has_blank_marks,
        "has_sub_questions": has_sub_questions,
        "is_choice_like": is_choice_like,
    }


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

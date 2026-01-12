# -*- coding: utf-8 -*-
"""
题型关键词特征库
用于反向识别各题型的特征，避免误判
"""
import re

# 简答题关键词
JIANDA_KEYWORDS = re.compile(r'(简述|简要说明|简答|阐述|说明.*原因|谈谈|分析.*影响|列举|举例说明|你认为|你的看法)')

# 计算题关键词
JISUAN_KEYWORDS = re.compile(r'(计算|求|解方程|证明|求解|求值|已知.*求|根据.*计算)')

# 材料分析题关键词
CAILIAO_KEYWORDS = re.compile(r'(材料[一二三四五]|根据材料|阅读.*材料|上述材料|结合材料|依据材料)')

# 实验探究题关键词
SHIYAN_KEYWORDS = re.compile(r'(实验|探究|观察.*现象|实验步骤|实验现象|实验结论|实验器材)')

# 写作题关键词
XIEZUO_KEYWORDS = re.compile(r'(作文|写一篇|以.*为题|话题作文|命题作文|续写|不少于.*字)')

# 阅读理解关键词
YUEDU_KEYWORDS = re.compile(r'(阅读.*文章|阅读.*短文|阅读.*完成|阅读理解|阅读下面|Read the (passage|text))')


def extract_type_keywords(text):
    """
    提取题型关键词特征

    Returns:
        dict: {
            "has_jianda": bool,
            "has_jisuan": bool,
            "has_cailiao": bool,
            "has_shiyan": bool,
            "has_xiezuo": bool,
            "has_yuedu": bool,
        }
    """
    if not isinstance(text, str):
        text = str(text)

    return {
        "has_jianda": bool(JIANDA_KEYWORDS.search(text)),
        "has_jisuan": bool(JISUAN_KEYWORDS.search(text)),
        "has_cailiao": bool(CAILIAO_KEYWORDS.search(text)),
        "has_shiyan": bool(SHIYAN_KEYWORDS.search(text)),
        "has_xiezuo": bool(XIEZUO_KEYWORDS.search(text)),
        "has_yuedu": bool(YUEDU_KEYWORDS.search(text)),
    }


def should_suppress_choice_boost(choice_signals, type_keywords):
    """
    判断是否应该抑制选择题增强

    如果题目虽然有选项标记，但更符合其他题型特征，则抑制增强

    Args:
        choice_signals: 选择题信号
        type_keywords: 其他题型关键词

    Returns:
        bool: True表示应该抑制增强
    """
    # 如果有明确的选择题关键词，不抑制
    if choice_signals.get("has_choice_keyword"):
        return False

    # 如果选项数量较少(2个)且有其他题型强特征，抑制
    option_count = choice_signals.get("option_count", 0)
    if option_count <= 2:
        # 简答题、计算题、材料分析题的特征优先级高
        if (type_keywords.get("has_jianda") or
            type_keywords.get("has_jisuan") or
            type_keywords.get("has_cailiao")):
            return True

    # 如果选项数量一般(3个)且有强特征，部分抑制
    if option_count == 3:
        # 只有材料分析题和计算题的特征才抑制（这两个容易误判）
        if (type_keywords.get("has_jisuan") or
            type_keywords.get("has_cailiao")):
            return True

    # 其他情况不抑制
    return False

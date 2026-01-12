# -*- coding: utf-8 -*-
"""
测试V2版本（防御性特征识别）的效果
"""
import sys
sys.path.insert(0, 'question_classifier')

from inference import QuestionClassifier

# 测试案例：涵盖之前的误判问题
test_cases = [
    # 填空形式选择题（应该识别为选择题）✅
    ("填空选择1", "The number of giraffes _______ dropping quickly so a number of people _______ trying their best to save them. A. is; is B. is; are C. are; is", "选择"),
    ("填空选择2", "The Yellow River is _______ to people in Gansu. It gives them water for farming. A. boring B. useful C. difficult D. funny", "选择"),
    ("填空选择3", "Ella lives _______ Harbin _______ her family. A. in; in B. in; with C. with; in", "选择"),

    # 简答题（不应该被误判为选择题）⚠️
    ("简答题1", "简述辛亥革命的历史意义，请从以下三个方面分析：A. 政治方面 B. 经济方面 C. 文化方面", "简答"),
    ("简答题2", "请阐述A国和B国在经济发展模式上的异同点，并谈谈你的看法。", "简答"),
    ("简答题3", "列举A、B、C三种元素的化学性质，并说明其应用。", "简答"),

    # 计算题（不应该被误判为选择题）⚠️
    ("计算题1", "已知A、B、C三点的坐标分别为(1,0)、(0,1)、(1,1)，计算三角形ABC的面积。", "计算"),
    ("计算题2", "计算从A点到B点的距离，已知A(2,3)，B(5,7)。", "计算"),

    # 材料分析题（不应该被误判为选择题）⚠️
    ("材料题1", "根据材料一和材料二，分析A国和B国经济发展的差异。", "材料分析"),
    ("材料题2", "阅读以下材料，分析材料中提到的A项政策和B项政策的影响。", "材料分析"),

    # 纯填空题（不应该被误判为选择题）⚠️
    ("填空题1", "长江是中国第_____大河，黄河是第______大河。", "填空"),
    ("填空题2", "光合作用的场所是_______，原料是_______。", "填空"),

    # 标准选择题（应该识别为选择题）✅
    ("标准选择1", "下列关于细胞的说法，正确的是（）A. 细胞是生命活动的基本单位 B. 病毒有细胞结构 C. 细胞都有细胞壁 D. 细胞都能独立生存", "选择"),
    ("标准选择2", "下列物质中，属于纯净物的是（）A. 空气 B. 矿泉水 C. 冰水混合物 D. 石油", "选择"),
]

def test_classifier():
    """测试分类器"""
    print("=" * 80)
    print("V2版本测试（防御性特征识别）")
    print("=" * 80)

    # 加载模型
    print("\n加载模型...")
    classifier = QuestionClassifier(model_dir='question_classifier/models')

    print("\n开始测试...\n")

    results = {
        "correct": 0,
        "wrong": 0,
        "details": []
    }

    for i, (label, text, expected_type) in enumerate(test_cases, 1):
        result = classifier.predict(text, use_calibration=True)
        pred_type = result['type']
        confidence = result['type_confidence']

        is_correct = (pred_type == expected_type)
        status = "✅" if is_correct else "❌"

        if is_correct:
            results["correct"] += 1
        else:
            results["wrong"] += 1

        print(f"{status} [{i}/{len(test_cases)}] {label}")
        print(f"   题目: {text[:50]}...")
        print(f"   期望: {expected_type}")
        print(f"   预测: {pred_type} (置信度: {confidence:.3f})")

        # 显示选择题信号和关键词特征
        choice_signals = result.get('choice_signals', {})
        type_keywords = result.get('type_keywords', {})

        print(f"   选择题信号: option_count={choice_signals.get('option_count', 0)}, "
              f"has_keyword={choice_signals.get('has_choice_keyword', False)}")

        # 显示检测到的其他题型关键词
        detected_keywords = [k.replace('has_', '') for k, v in type_keywords.items() if v]
        if detected_keywords:
            print(f"   检测到关键词: {', '.join(detected_keywords)}")

        if not is_correct:
            # 显示概率分布
            top_probs = sorted(result['type_probs'].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   概率分布: ", end="")
            for t, p in top_probs:
                print(f"{t}({p:.2f}) ", end="")
            print()

        print()

        results["details"].append({
            "label": label,
            "expected": expected_type,
            "predicted": pred_type,
            "correct": is_correct,
            "confidence": confidence
        })

    # 统计结果
    print("=" * 80)
    print("测试结果统计")
    print("=" * 80)
    print(f"总测试数: {len(test_cases)}")
    print(f"正确数: {results['correct']}")
    print(f"错误数: {results['wrong']}")
    print(f"准确率: {results['correct']/len(test_cases)*100:.1f}%")

    # 分类统计
    print("\n按类别统计:")
    categories = {
        "填空形式选择题": ["填空选择1", "填空选择2", "填空选择3"],
        "简答题": ["简答题1", "简答题2", "简答题3"],
        "计算题": ["计算题1", "计算题2"],
        "材料分析题": ["材料题1", "材料题2"],
        "填空题": ["填空题1", "填空题2"],
        "标准选择题": ["标准选择1", "标准选择2"],
    }

    for category, labels in categories.items():
        cat_correct = sum(1 for d in results["details"] if d["label"] in labels and d["correct"])
        cat_total = len(labels)
        cat_accuracy = cat_correct / cat_total * 100 if cat_total > 0 else 0
        status = "✅" if cat_accuracy == 100 else ("⚠️" if cat_accuracy >= 50 else "❌")
        print(f"  {status} {category}: {cat_correct}/{cat_total} ({cat_accuracy:.0f}%)")

    # 关键问题检查
    print("\n关键改进验证:")

    # 检查1：填空形式选择题改善
    blank_choice_correct = sum(1 for d in results["details"]
                               if d["label"] in ["填空选择1", "填空选择2", "填空选择3"]
                               and d["correct"])
    print(f"  1. 填空形式选择题识别: {blank_choice_correct}/3 ", end="")
    print("✅ 改善有效" if blank_choice_correct >= 2 else "❌ 改善不足")

    # 检查2：简答题保护
    jianda_correct = sum(1 for d in results["details"]
                        if d["label"] in ["简答题1", "简答题2", "简答题3"]
                        and d["correct"])
    print(f"  2. 简答题误判防护: {jianda_correct}/3 ", end="")
    print("✅ 防护有效" if jianda_correct >= 2 else "❌ 防护不足")

    # 检查3：计算题保护
    jisuan_correct = sum(1 for d in results["details"]
                        if d["label"] in ["计算题1", "计算题2"]
                        and d["correct"])
    print(f"  3. 计算题误判防护: {jisuan_correct}/2 ", end="")
    print("✅ 防护有效" if jisuan_correct >= 1 else "❌ 防护不足")

    # 检查4：材料分析题保护
    cailiao_correct = sum(1 for d in results["details"]
                         if d["label"] in ["材料题1", "材料题2"]
                         and d["correct"])
    print(f"  4. 材料分析题误判防护: {cailiao_correct}/2 ", end="")
    print("✅ 防护有效" if cailiao_correct >= 1 else "❌ 防护不足")

    print("\n" + "=" * 80)

    return results


if __name__ == '__main__':
    test_classifier()

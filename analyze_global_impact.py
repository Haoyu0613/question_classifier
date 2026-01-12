# -*- coding: utf-8 -*-
"""
分析选择题优化对全局的影响
"""
import pandas as pd
from collections import defaultdict

def analyze_prediction_results(file_path):
    """分析预测结果的全局影响"""

    # 读取数据
    df = pd.read_excel(file_path)

    # 查找真实题型和预测题型列
    true_col = None
    pred_col = None
    for col in df.columns:
        if '真实' in col or '真值' in col:
            true_col = col
        if '预测' in col and '优化' in col:
            pred_col = col

    if true_col is None or pred_col is None:
        print(f"列名: {df.columns.tolist()}")
        print("请确认Excel中包含真实题型和预测题型列")
        return

    print(f"使用列: 真实题型={true_col}, 预测题型={pred_col}")
    print("=" * 80)

    # 总体统计
    total = len(df)
    correct = (df[true_col] == df[pred_col]).sum()
    accuracy = correct / total

    print(f"\n【整体统计】")
    print(f"总题目数: {total}")
    print(f"正确数: {correct}")
    print(f"整体准确率: {accuracy:.2%}")

    # 选择题专项分析
    print(f"\n{'='*80}")
    print(f"【选择题专项分析】")
    print(f"{'='*80}")

    # 真实的选择题
    real_choice = df[df[true_col] == '选择']
    choice_total = len(real_choice)
    choice_correct = (real_choice[true_col] == real_choice[pred_col]).sum()
    choice_accuracy = choice_correct / choice_total if choice_total > 0 else 0

    print(f"\n1. 真实选择题识别情况:")
    print(f"   - 选择题总数: {choice_total}")
    print(f"   - 正确识别: {choice_correct}")
    print(f"   - 准确率: {choice_accuracy:.2%}")

    # 选择题误判情况
    choice_errors = real_choice[real_choice[true_col] != real_choice[pred_col]]
    if len(choice_errors) > 0:
        print(f"\n   误判分布:")
        error_dist = choice_errors[pred_col].value_counts()
        for pred_type, count in error_dist.items():
            print(f"   - 误判为{pred_type}: {count}个 ({count/choice_total*100:.1f}%)")

    # 其他题型被误判为选择题的情况
    print(f"\n2. 其他题型被误判为选择题的情况:")
    false_positive = df[(df[true_col] != '选择') & (df[pred_col] == '选择')]

    if len(false_positive) > 0:
        print(f"   ⚠️  发现 {len(false_positive)} 个非选择题被误判为选择题")
        fp_dist = false_positive[true_col].value_counts()
        for true_type, count in fp_dist.items():
            ratio = count / len(df[df[true_col] == true_type]) * 100
            print(f"   - {true_type}: {count}个 (占该题型的{ratio:.1f}%)")

        # 显示具体案例
        print(f"\n   具体案例（前5个）:")
        for idx, row in false_positive.head(5).iterrows():
            text = str(row.get('题目内容', ''))[:60]
            print(f"   [{idx}] {text}... → 误判为选择题")
    else:
        print(f"   ✅ 无其他题型被误判为选择题")

    # 各题型准确率对比
    print(f"\n{'='*80}")
    print(f"【各题型准确率统计】")
    print(f"{'='*80}")

    all_types = sorted(df[true_col].unique())

    print(f"\n{'题型':<12} {'总数':<8} {'正确':<8} {'准确率':<10} {'主要误判'}")
    print("-" * 70)

    for qtype in all_types:
        subset = df[df[true_col] == qtype]
        total_count = len(subset)
        correct_count = (subset[true_col] == subset[pred_col]).sum()
        acc = correct_count / total_count if total_count > 0 else 0

        # 找出主要误判类型
        errors = subset[subset[true_col] != subset[pred_col]]
        if len(errors) > 0:
            main_error = errors[pred_col].value_counts().index[0]
            error_count = errors[pred_col].value_counts().values[0]
            main_error_str = f"{main_error}({error_count})"
        else:
            main_error_str = "-"

        print(f"{qtype:<12} {total_count:<8} {correct_count:<8} {acc:<10.2%} {main_error_str}")

    # 混淆矩阵（重点关注选择题）
    print(f"\n{'='*80}")
    print(f"【选择题混淆情况】")
    print(f"{'='*80}")

    # 真实选择题 vs 预测结果
    print(f"\n真实选择题的预测分布:")
    choice_pred_dist = real_choice[pred_col].value_counts()
    for pred_type, count in choice_pred_dist.items():
        ratio = count / choice_total * 100
        marker = "✅" if pred_type == "选择" else "❌"
        print(f"  {marker} 预测为{pred_type}: {count}个 ({ratio:.1f}%)")

    # 预测为选择题的真实分布
    print(f"\n预测为选择题的真实分布:")
    pred_choice = df[df[pred_col] == '选择']
    pred_choice_dist = pred_choice[true_col].value_counts()
    for true_type, count in pred_choice_dist.items():
        ratio = count / len(pred_choice) * 100
        marker = "✅" if true_type == "选择" else "⚠️"
        print(f"  {marker} 真实为{true_type}: {count}个 ({ratio:.1f}%)")

    print(f"\n{'='*80}")

    # 返回关键指标
    return {
        'overall_accuracy': accuracy,
        'choice_accuracy': choice_accuracy,
        'false_positive_count': len(false_positive),
        'choice_total': choice_total,
        'choice_correct': choice_correct
    }


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认文件名
        file_path = '预测结果.xlsx'

    print(f"分析文件: {file_path}\n")
    analyze_prediction_results(file_path)

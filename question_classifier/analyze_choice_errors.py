# -*- coding: utf-8 -*-
"""
分析选择题误判原因
"""
import argparse
import pandas as pd
from preprocess import extract_choice_signals


POSSIBLE_TEXT_COLUMNS = ['题目内容', '题干', '题目', '文本']
POSSIBLE_TRUE_COLUMNS = ['真实题型', '题型', '真值题型', '真实标签']
POSSIBLE_PRED_COLUMNS = ['预测题型', '预测', '预测标签']


def _find_column(df, candidates):
    for name in candidates:
        if name in df.columns:
            return name
    return None


def load_error_table(path):
    if path.endswith('.xlsx') or path.endswith('.xls'):
        return pd.read_excel(path)
    return pd.read_csv(path)


def analyze_choice_errors(df):
    text_col = _find_column(df, POSSIBLE_TEXT_COLUMNS)
    true_col = _find_column(df, POSSIBLE_TRUE_COLUMNS)
    pred_col = _find_column(df, POSSIBLE_PRED_COLUMNS)

    missing_cols = [name for name, col in [('题目内容', text_col), ('真实题型', true_col), ('预测题型', pred_col)] if col is None]
    if missing_cols:
        raise ValueError(f"缺少必要列: {', '.join(missing_cols)}")

    errors = df[(df[true_col] == '选择') & (df[pred_col] != '选择')].copy()
    if errors.empty:
        print("未找到选择题误判记录。")
        return

    signals = errors[text_col].apply(extract_choice_signals)
    errors['选项数量'] = signals.apply(lambda x: x['option_count'])
    errors['包含选择关键词'] = signals.apply(lambda x: x['has_choice_keyword'])
    errors['选择题信号'] = signals.apply(lambda x: x['is_choice_like'])

    total = len(errors)
    print(f"选择题误判总数: {total}")
    print(f"出现选项标记(>=2)占比: {(errors['选项数量'] >= 2).mean():.2%}")
    print(f"包含选择题关键词占比: {errors['包含选择关键词'].mean():.2%}")
    print(f"完全缺少选择信号占比: {(~errors['选择题信号']).mean():.2%}")

    print("\n误判分布（预测题型）:")
    print(errors[pred_col].value_counts())

    print("\n缺少选择信号的示例:")
    print(errors.loc[~errors['选择题信号'], text_col].head(10).to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="分析选择题误判原因")
    parser.add_argument('path', help='分类错误题目表格路径（csv/xlsx）')
    args = parser.parse_args()

    df = load_error_table(args.path)
    analyze_choice_errors(df)


if __name__ == '__main__':
    main()

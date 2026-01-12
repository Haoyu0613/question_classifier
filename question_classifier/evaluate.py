# -*- coding: utf-8 -*-
"""
评估脚本：对比有无先验约束校准的效果
"""
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from inference import QuestionClassifier
from preprocess import clean_text


def evaluate_on_dataset(classifier, df, use_calibration=True):
    """
    在数据集上评估
    
    Returns:
        subject_acc, type_acc, predictions
    """
    texts = df['题目内容'].tolist()
    true_subjects = df['科目'].tolist()
    true_types = df['题型'].tolist()
    
    pred_subjects = []
    pred_types = []
    
    for text in texts:
        result = classifier.predict(text, use_calibration=use_calibration)
        pred_subjects.append(result['subject'])
        pred_types.append(result['type'])
    
    subject_acc = accuracy_score(true_subjects, pred_subjects)
    type_acc = accuracy_score(true_types, pred_types)
    
    return subject_acc, type_acc, pred_subjects, pred_types


def print_comparison_report(classifier, test_df, config):
    """打印对比报告"""
    
    print("\n" + "=" * 70)
    print("模型评估报告")
    print("=" * 70)
    
    # 无校准
    print("\n【无先验约束校准】")
    subj_acc_raw, type_acc_raw, pred_subj_raw, pred_type_raw = evaluate_on_dataset(
        classifier, test_df, use_calibration=False
    )
    print(f"学科准确率: {subj_acc_raw:.4f}")
    print(f"题型准确率: {type_acc_raw:.4f}")
    
    # 有校准
    print("\n【有先验约束校准】")
    subj_acc_cal, type_acc_cal, pred_subj_cal, pred_type_cal = evaluate_on_dataset(
        classifier, test_df, use_calibration=True
    )
    print(f"学科准确率: {subj_acc_cal:.4f}")
    print(f"题型准确率: {type_acc_cal:.4f}")
    
    # 对比
    print("\n【对比】")
    print(f"学科准确率: {subj_acc_raw:.4f} → {subj_acc_cal:.4f} (Δ={subj_acc_cal-subj_acc_raw:+.4f})")
    print(f"题型准确率: {type_acc_raw:.4f} → {type_acc_cal:.4f} (Δ={type_acc_cal-type_acc_raw:+.4f})")
    
    # 详细分类报告（校准后）
    print("\n" + "-" * 70)
    print("学科分类报告（校准后）")
    print("-" * 70)
    print(classification_report(
        test_df['科目'], pred_subj_cal,
        target_names=config['subjects'],
        zero_division=0
    ))
    
    print("\n" + "-" * 70)
    print("题型分类报告（校准后）")
    print("-" * 70)
    print(classification_report(
        test_df['题型'], pred_type_cal,
        target_names=config['types'],
        zero_division=0
    ))
    
    # 分析校准改变了哪些预测
    print("\n" + "-" * 70)
    print("校准效果分析")
    print("-" * 70)
    
    changed_indices = [i for i in range(len(pred_type_raw)) if pred_type_raw[i] != pred_type_cal[i]]
    print(f"校准改变了 {len(changed_indices)} 条预测（共 {len(test_df)} 条）")
    
    if changed_indices:
        # 统计改变后正确/错误的数量
        improved = 0
        worsened = 0
        for i in changed_indices:
            true_type = test_df.iloc[i]['题型']
            if pred_type_cal[i] == true_type and pred_type_raw[i] != true_type:
                improved += 1
            elif pred_type_cal[i] != true_type and pred_type_raw[i] == true_type:
                worsened += 1
        
        print(f"  - 改进（错→对）: {improved} 条")
        print(f"  - 恶化（对→错）: {worsened} 条")
        print(f"  - 净改进: {improved - worsened} 条")


def main():
    """主评估流程"""
    # 加载模型
    classifier = QuestionClassifier(model_dir='models')
    
    # 加载配置
    with open('models/config.pkl', 'rb') as f:
        config = pickle.load(f)
    
    # 加载测试集
    test_df = pd.read_excel(config['test_path'])
    
    # 打印对比报告
    print_comparison_report(classifier, test_df, config)


if __name__ == '__main__':
    main()

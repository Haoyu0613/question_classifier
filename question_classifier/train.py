# -*- coding: utf-8 -*-
"""
训练脚本：学科模型 + 题型模型
"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from preprocess import clean_text


# ==================== 配置 ====================
CONFIG = {
    # 数据路径
    'train_path': 'data/train.xlsx',
    'dev_path': 'data/dev.xlsx',
    'test_path': 'data/test.xlsx',
    
    # 模型保存路径
    'model_dir': 'models',
    
    # TF-IDF 参数
    'tfidf_params': {
        'analyzer': 'char',        # 字符级
        'ngram_range': (2, 5),     # 2-5字符组合
        'max_features': 20000,     # 最大特征数
        'sublinear_tf': True,      # 对词频取对数
        'min_df': 2,               # 最小文档频率
    },
    
    # 分类器参数
    'classifier_params': {
        'C': 1.0,                  # 正则化强度
        'max_iter': 1000,          # 最大迭代次数
        'solver': 'lbfgs',         # 优化算法
        'random_state': 42,
    },
    
    # 标签定义
    'subjects': ['语文', '数学', '英语', '物理', '化学', '生物', '地理', '历史', '道德与法治'],
    'types': ['选择', '填空', '阅读理解', '材料分析', '计算', '实验探究', '简答', '写作'],
}


def load_data(path):
    """加载数据"""
    df = pd.read_excel(path)
    df['clean_text'] = df['题目内容'].apply(clean_text)
    return df


def train_tfidf(texts, params):
    """训练 TF-IDF 向量化器"""
    vectorizer = TfidfVectorizer(**params)
    X = vectorizer.fit_transform(texts)
    print(f"TF-IDF 特征维度: {X.shape[1]}")
    return vectorizer, X


def train_classifier(X_train, y_train, params, class_weight=None):
    """训练分类器"""
    clf = LogisticRegression(
        class_weight=class_weight,
        **params
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate_model(clf, X, y, label_names, model_name="Model"):
    """评估模型"""
    y_pred = clf.predict(X)
    acc = accuracy_score(y, y_pred)
    
    print(f"\n{'='*50}")
    print(f"{model_name} 评估结果")
    print(f"{'='*50}")
    print(f"Accuracy: {acc:.4f}")
    print(f"\n分类报告:")
    print(classification_report(y, y_pred, target_names=label_names, zero_division=0))
    
    return acc, y_pred


def build_prior_matrix(df, subjects, types):
    """
    构建先验矩阵 P(type|subject)
    
    返回: dict, key=学科, value=dict{题型: 概率}
    """
    prior = {}
    
    for subj in subjects:
        subj_df = df[df['科目'] == subj]
        total = len(subj_df)
        
        prior[subj] = {}
        for t in types:
            count = len(subj_df[subj_df['题型'] == t])
            # 拉普拉斯平滑
            prior[subj][t] = (count + 0.5) / (total + 0.5 * len(types))
    
    return prior


def print_prior_matrix(prior, subjects, types):
    """打印先验矩阵"""
    print("\n先验矩阵 P(type|subject):")
    print("-" * 80)
    
    # 表头
    header = f"{'学科':<10}" + "".join([f"{t:<10}" for t in types])
    print(header)
    print("-" * 80)
    
    # 数据行
    for subj in subjects:
        row = f"{subj:<10}"
        for t in types:
            prob = prior[subj].get(t, 0)
            row += f"{prob:<10.3f}"
        print(row)


def save_model(obj, path):
    """保存模型"""
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f"已保存: {path}")


def main():
    """主训练流程"""
    print("=" * 60)
    print("题目学科与题型识别模型训练")
    print("=" * 60)
    
    # 创建模型目录
    os.makedirs(CONFIG['model_dir'], exist_ok=True)
    
    # ==================== 1. 加载数据 ====================
    print("\n[1/6] 加载数据...")
    train_df = load_data(CONFIG['train_path'])
    dev_df = load_data(CONFIG['dev_path'])
    test_df = load_data(CONFIG['test_path'])
    
    print(f"训练集: {len(train_df)} 条")
    print(f"验证集: {len(dev_df)} 条")
    print(f"测试集: {len(test_df)} 条")
    
    # ==================== 2. TF-IDF 向量化 ====================
    print("\n[2/6] 训练 TF-IDF 向量化器...")
    vectorizer, X_train = train_tfidf(train_df['clean_text'], CONFIG['tfidf_params'])
    
    X_dev = vectorizer.transform(dev_df['clean_text'])
    X_test = vectorizer.transform(test_df['clean_text'])
    
    # 保存向量化器
    save_model(vectorizer, f"{CONFIG['model_dir']}/tfidf_vectorizer.pkl")
    
    # ==================== 3. 训练学科模型 ====================
    print("\n[3/6] 训练学科模型...")
    y_train_subject = train_df['科目']
    y_dev_subject = dev_df['科目']
    y_test_subject = test_df['科目']
    
    subject_clf = train_classifier(
        X_train, y_train_subject,
        CONFIG['classifier_params'],
        class_weight=None  # 学科分布均衡，不需要加权
    )
    
    # 评估学科模型
    print("\n--- 学科模型 - 验证集 ---")
    evaluate_model(subject_clf, X_dev, y_dev_subject, CONFIG['subjects'], "学科模型(Dev)")
    
    print("\n--- 学科模型 - 测试集 ---")
    evaluate_model(subject_clf, X_test, y_test_subject, CONFIG['subjects'], "学科模型(Test)")
    
    # 保存学科模型
    save_model(subject_clf, f"{CONFIG['model_dir']}/subject_model.pkl")
    
    # ==================== 4. 训练题型模型 ====================
    print("\n[4/6] 训练题型模型...")
    y_train_type = train_df['题型']
    y_dev_type = dev_df['题型']
    y_test_type = test_df['题型']
    
    type_clf = train_classifier(
        X_train, y_train_type,
        CONFIG['classifier_params'],
        class_weight='balanced'  # 题型分布不均衡，使用自动加权
    )
    
    # 评估题型模型
    print("\n--- 题型模型 - 验证集 ---")
    evaluate_model(type_clf, X_dev, y_dev_type, CONFIG['types'], "题型模型(Dev)")
    
    print("\n--- 题型模型 - 测试集 ---")
    evaluate_model(type_clf, X_test, y_test_type, CONFIG['types'], "题型模型(Test)")
    
    # 保存题型模型
    save_model(type_clf, f"{CONFIG['model_dir']}/type_model.pkl")
    
    # ==================== 5. 构建先验矩阵 ====================
    print("\n[5/6] 构建先验矩阵 P(type|subject)...")
    prior_matrix = build_prior_matrix(train_df, CONFIG['subjects'], CONFIG['types'])
    print_prior_matrix(prior_matrix, CONFIG['subjects'], CONFIG['types'])
    
    # 保存先验矩阵
    save_model(prior_matrix, f"{CONFIG['model_dir']}/prior_matrix.pkl")
    
    # ==================== 6. 保存配置 ====================
    print("\n[6/6] 保存配置...")
    save_model(CONFIG, f"{CONFIG['model_dir']}/config.pkl")
    
    print("\n" + "=" * 60)
    print("训练完成！")
    print("=" * 60)
    print(f"\n模型文件保存在: {CONFIG['model_dir']}/")
    print("  - tfidf_vectorizer.pkl")
    print("  - subject_model.pkl")
    print("  - type_model.pkl")
    print("  - prior_matrix.pkl")
    print("  - config.pkl")


if __name__ == '__main__':
    main()

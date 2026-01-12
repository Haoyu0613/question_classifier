# -*- coding: utf-8 -*-
"""
推理脚本：支持先验约束校准
"""
import pickle
import numpy as np
from preprocess import clean_text, extract_choice_signals


class QuestionClassifier:
    """题目分类器"""
    
    def __init__(self, model_dir='models'):
        """
        初始化分类器
        
        Args:
            model_dir: 模型文件目录
        """
        self.model_dir = model_dir
        self._load_models()
    
    def _load_models(self):
        """加载所有模型文件"""
        # 加载配置
        with open(f"{self.model_dir}/config.pkl", 'rb') as f:
            self.config = pickle.load(f)
        
        # 加载向量化器
        with open(f"{self.model_dir}/tfidf_vectorizer.pkl", 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        # 加载学科模型
        with open(f"{self.model_dir}/subject_model.pkl", 'rb') as f:
            self.subject_model = pickle.load(f)
        
        # 加载题型模型
        with open(f"{self.model_dir}/type_model.pkl", 'rb') as f:
            self.type_model = pickle.load(f)
        
        # 加载先验矩阵
        with open(f"{self.model_dir}/prior_matrix.pkl", 'rb') as f:
            self.prior_matrix = pickle.load(f)
        
        # 使用模型实际的类别顺序（sklearn按字母排序）
        self.subjects = list(self.subject_model.classes_)
        self.types = list(self.type_model.classes_)

        self.enable_choice_heuristic = self.config.get('enable_choice_heuristic', True)
        
        print(f"模型加载完成！")
        print(f"  学科: {self.subjects}")
        print(f"  题型: {self.types}")
    
    def predict(self, text, use_calibration=True, top_k_subjects=3):
        """
        预测单条题目
        
        Args:
            text: 题目文本
            use_calibration: 是否使用先验约束校准
            top_k_subjects: 校准时考虑的Top-K学科数
        
        Returns:
            dict: 包含预测结果和概率
        """
        # 文本清洗
        clean = clean_text(text)
        
        # 向量化
        X = self.vectorizer.transform([clean])
        
        # 学科预测
        subject_probs = self.subject_model.predict_proba(X)[0]
        subject_pred = self.subjects[np.argmax(subject_probs)]
        
        # 题型预测（原始）
        type_probs_raw = self.type_model.predict_proba(X)[0]
        
        if use_calibration:
            # 先验约束校准
            type_probs = self._calibrate_type_probs(
                type_probs_raw, subject_probs, top_k_subjects
            )
        else:
            type_probs = type_probs_raw

        choice_signals = extract_choice_signals(text)
        if self.enable_choice_heuristic and choice_signals["is_choice_like"]:
            type_probs = self._apply_choice_boost(type_probs, choice_signals)
        
        type_pred = self.types[np.argmax(type_probs)]
        
        return {
            'subject': subject_pred,
            'subject_confidence': float(np.max(subject_probs)),
            'subject_probs': {s: float(p) for s, p in zip(self.subjects, subject_probs)},
            'type': type_pred,
            'type_confidence': float(np.max(type_probs)),
            'type_probs': {t: float(p) for t, p in zip(self.types, type_probs)},
            'type_probs_raw': {t: float(p) for t, p in zip(self.types, type_probs_raw)},
            'calibrated': use_calibration,
            'choice_signals': choice_signals,
        }
    
    def _calibrate_type_probs(self, type_probs, subject_probs, top_k=3):
        """
        先验约束校准
        
        P'(type|x) ∝ P(type|x) × Σ_{s∈TopK} P(s|x) · P(type|s)
        """
        # 获取 Top-K 学科
        top_k_indices = np.argsort(subject_probs)[::-1][:top_k]
        
        # 计算先验加权
        prior_weight = np.zeros(len(self.types))
        for idx in top_k_indices:
            subject = self.subjects[idx]
            subject_prob = subject_probs[idx]
            for i, t in enumerate(self.types):
                prior_weight[i] += subject_prob * self.prior_matrix[subject].get(t, 0.01)
        
        # 校准
        calibrated = type_probs * prior_weight
        
        # 归一化
        calibrated = calibrated / (calibrated.sum() + 1e-10)

        return calibrated

    def _apply_choice_boost(self, type_probs, choice_signals):
        """
        对选择题进行启发式概率增强（双向调整策略）

        策略：
        1. 增强选择题概率（根据选项数量和关键词）
        2. 对填空形式的选择题，同时压制填空概率
        3. 归一化
        """
        boosted = np.array(type_probs, dtype=float)
        if '选择' not in self.types:
            return boosted

        choice_index = self.types.index('选择')

        # 1. 分级增强选择题
        if choice_signals["has_choice_keyword"]:
            # 明确的选择题关键词，强增强
            boost_factor = 3.0
        elif choice_signals["option_count"] >= 4:
            # 4个选项，强增强
            boost_factor = 3.5
        elif choice_signals["option_count"] >= 3:
            # 3个选项，中等增强
            boost_factor = 3.0
        elif choice_signals["option_count"] >= 2:
            # 2个选项，温和增强
            boost_factor = 2.5
        else:
            # 无明确信号，不增强
            return boosted

        boosted[choice_index] *= boost_factor

        # 2. 如果是填空形式的选择题，压制填空概率
        if choice_signals.get("is_blank_choice", False):
            if '填空' in self.types:
                blank_index = self.types.index('填空')
                boosted[blank_index] *= 0.4  # 压制到40%

        # 3. 归一化
        boosted = boosted / (boosted.sum() + 1e-10)
        return boosted
    
    def predict_batch(self, texts, use_calibration=True, top_k_subjects=3):
        """
        批量预测
        
        Args:
            texts: 题目文本列表
            use_calibration: 是否使用先验约束校准
            top_k_subjects: 校准时考虑的Top-K学科数
        
        Returns:
            list[dict]: 预测结果列表
        """
        results = []
        for text in texts:
            result = self.predict(text, use_calibration, top_k_subjects)
            results.append(result)
        return results
    
    def predict_simple(self, text, use_calibration=True):
        """
        简化预测，只返回学科和题型
        
        Args:
            text: 题目文本
            use_calibration: 是否使用先验约束校准
        
        Returns:
            tuple: (学科, 题型)
        """
        result = self.predict(text, use_calibration)
        return result['subject'], result['type']


def main():
    """测试推理"""
    # 加载模型
    classifier = QuestionClassifier(model_dir='models')
    
    # 测试样例
    test_cases = [
        "下列关于细胞呼吸的说法，正确的是（）A. 有氧呼吸只在线粒体中进行 B. 无氧呼吸不产生ATP",
        "已知函数f(x)=x²-2x+1，求f(x)的最小值。",
        "阅读下面的文章，完成小题。春天来了，万物复苏...",
        "下列物质中，属于纯净物的是（）A. 空气 B. 矿泉水 C. 冰水混合物",
        "根据材料，分析中国共产党在抗日战争中的作用。",
        "Write a short passage about your favorite season.",
    ]
    
    print("\n" + "=" * 60)
    print("推理测试")
    print("=" * 60)
    
    for i, text in enumerate(test_cases):
        print(f"\n【测试 {i+1}】")
        print(f"题目: {text[:50]}...")
        
        # 不使用校准
        result_raw = classifier.predict(text, use_calibration=False)
        print(f"无校准: 学科={result_raw['subject']}, 题型={result_raw['type']}")
        
        # 使用校准
        result_cal = classifier.predict(text, use_calibration=True)
        print(f"有校准: 学科={result_cal['subject']}, 题型={result_cal['type']}")
        
        # 如果结果不同，显示差异
        if result_raw['type'] != result_cal['type']:
            print(f"  → 校准改变了预测！")
            print(f"     原始题型概率: {result_cal['type_probs_raw']}")
            print(f"     校准后概率:   {result_cal['type_probs']}")


if __name__ == '__main__':
    main()

# 题目学科与题型识别模型

## 项目结构

```
question_classifier/
├── data/                    # 数据目录
│   ├── train.xlsx          # 训练集 (3151条)
│   ├── dev.xlsx            # 验证集 (674条)
│   └── test.xlsx           # 测试集 (675条)
├── models/                  # 模型目录
│   ├── tfidf_vectorizer.pkl    # TF-IDF向量化器
│   ├── subject_model.pkl       # 学科分类模型
│   ├── type_model.pkl          # 题型分类模型
│   ├── prior_matrix.pkl        # 先验矩阵 P(type|subject)
│   └── config.pkl              # 配置文件
├── preprocess.py           # 文本预处理模块
├── train.py                # 训练脚本
├── inference.py            # 推理脚本
└── evaluate.py             # 评估脚本
```

## 模型性能

| 模型 | 测试集准确率 |
|------|-------------|
| 学科模型 | 94.67% |
| 题型模型 | 88.44% |

## 标签定义

**学科（9类）**：语文、数学、英语、物理、化学、生物、地理、历史、道德与法治

**题型（8类）**：选择、填空、阅读理解、材料分析、计算、实验探究、简答、写作

## 使用方法

### 1. 训练模型

```bash
cd question_classifier
python train.py
```

### 2. 推理预测

```python
from inference import QuestionClassifier

# 加载模型
classifier = QuestionClassifier(model_dir='models')

# 单条预测
text = "下列关于细胞呼吸的说法，正确的是（）A. 有氧呼吸只在线粒体中进行"
result = classifier.predict(text)

print(f"学科: {result['subject']} (置信度: {result['subject_confidence']:.2f})")
print(f"题型: {result['type']} (置信度: {result['type_confidence']:.2f})")

# 简化预测
subject, qtype = classifier.predict_simple(text)
print(f"学科: {subject}, 题型: {qtype}")

# 批量预测
texts = ["题目1...", "题目2...", "题目3..."]
results = classifier.predict_batch(texts)
```

### 3. 评估模型

```bash
python evaluate.py
```

## 先验约束校准

推理时可选择是否启用先验约束校准：

```python
# 不使用校准（默认更准确）
result = classifier.predict(text, use_calibration=False)

# 使用校准
result = classifier.predict(text, use_calibration=True)
```

在当前数据集上，校准并未提升准确率，建议默认关闭。

## 依赖

- Python 3.8+
- pandas
- numpy
- scikit-learn
- openpyxl

## 技术方案

1. **特征提取**：TF-IDF (char n-gram 2-5)
2. **分类器**：Logistic Regression
3. **题型不平衡处理**：class_weight='balanced'
4. **先验约束**：P(type|subject) 软约束校准（可选）

## Web应用

### 启动应用

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Web界面
python app.py
```

启动后访问 http://localhost:7860 即可使用。

### 界面功能

- 在文本框中输入题目
- 点击"识别"按钮
- 查看预测的学科、题型及置信度

### 生成公网链接（可选）

修改 `app.py` 最后的 `share=True`，启动后会生成一个可分享的公网链接。

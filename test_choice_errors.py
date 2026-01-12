# -*- coding: utf-8 -*-
"""
测试选择题误判案例
"""
from question_classifier.inference import QuestionClassifier

# 加载模型
classifier = QuestionClassifier(model_dir='models')

# 那7个误判的题目
test_cases = [
    "The number of giraffes _______ dropping quickly so a number of people _______ trying their best to save them. A. is; is B. is; are C. are; is",
    "The Yellow River is _______ to people in Gansu. It gives them water for farming. A. boring B. useful C. difficult D. funny",
    "Ella lives _______ Harbin _______ her family. A. in; in B. in; with C. with; in",
    "A number of boys _______ playing outside and the number of boys in our neighborhood _______ increasing. A. are; are B. is; are C. are; is D. is; is",
    "You _______ be very tired after finishing all those hard jobs. — Yes. I'll take a good rest and make myself comfortable. A. may B. may not C. must D. can",
    "She _______ losing touch with her old friends after moving to a new city. A. worries about B. talks about C. looks for D. takes over",
    "听下面一段对话，回答以下小题。1. Which club does Jim want to join? A. The art club. B. The swimming club. C. The basketball club. 2. Who is Tony? A. A teacher. B. Jim's friend. C. Jim's cousin. 3. When do the club members meet? A. On Friday morning. B. On Friday afternoon. C. On Saturday afternoon. 4. What's the colour of the art building? A. Red. B. Blue. C. Yellow."
]

print("=" * 80)
print("选择题误判案例测试（方案2：双向调整策略）")
print("=" * 80)

correct_count = 0
total_count = len(test_cases)

for i, text in enumerate(test_cases, 1):
    result = classifier.predict(text, use_calibration=True)

    print(f"\n【案例 {i}】")
    print(f"题目: {text[:60]}...")
    print(f"预测题型: {result['type']} (置信度: {result['type_confidence']:.4f})")
    print(f"选择题信号: {result['choice_signals']}")

    if result['type'] == '选择':
        print("✅ 正确识别为选择题")
        correct_count += 1
    else:
        print(f"❌ 误判为 {result['type']}")
        print(f"   题型概率分布: {result['type_probs']}")

print("\n" + "=" * 80)
print(f"测试结果: {correct_count}/{total_count} 正确 ({correct_count/total_count*100:.1f}%)")
print("=" * 80)

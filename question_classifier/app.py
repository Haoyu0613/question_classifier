# -*- coding: utf-8 -*-
"""
题目学科与题型识别 - Web应用
"""
import gradio as gr
from inference import QuestionClassifier

# 加载模型（全局只加载一次）
classifier = QuestionClassifier(model_dir='models')


def predict_question(text):
    """预测题目的学科和题型"""
    if not text or not text.strip():
        return "请输入题目内容", "", "", ""
    
    result = classifier.predict(text, use_calibration=False)
    
    # 格式化输出
    subject = f"{result['subject']}"
    subject_conf = f"{result['subject_confidence']:.1%}"
    qtype = f"{result['type']}"
    type_conf = f"{result['type_confidence']:.1%}"
    
    return subject, subject_conf, qtype, type_conf


# 创建Gradio界面
with gr.Blocks(title="题目分类器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📚 题目学科与题型识别系统
    
    输入一道题目，自动识别其所属学科和题型。
    
    **支持学科**：语文、数学、英语、物理、化学、生物、地理、历史、道德与法治
    
    **支持题型**：选择、填空、阅读理解、材料分析、计算、实验探究、简答、写作
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                label="题目内容",
                placeholder="请在此输入题目...",
                lines=6
            )
            predict_btn = gr.Button("🔍 识别", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### 预测结果")
                subject_output = gr.Textbox(label="学科", interactive=False)
                subject_conf_output = gr.Textbox(label="学科置信度", interactive=False)
                type_output = gr.Textbox(label="题型", interactive=False)
                type_conf_output = gr.Textbox(label="题型置信度", interactive=False)
    
    # 示例题目
    gr.Examples(
        examples=[
            ["下列关于细胞呼吸的说法，正确的是（）\nA. 有氧呼吸只在线粒体中进行\nB. 无氧呼吸不产生ATP\nC. 有氧呼吸的三个阶段都能产生ATP\nD. 无氧呼吸的产物只有酒精"],
            ["已知函数f(x)=x²-2x+1，求函数f(x)的最小值。"],
            ["阅读下面的文章，完成小题。\n春天来了，万物复苏，小草从土里探出头来，柳树抽出了新的枝条..."],
            ["根据材料，分析中国共产党在抗日战争中发挥的作用。"],
            ["Write a short passage about your favorite season. (不少于60词)"],
        ],
        inputs=input_text,
        label="示例题目（点击可快速填入）"
    )
    
    # 绑定按钮事件
    predict_btn.click(
        fn=predict_question,
        inputs=input_text,
        outputs=[subject_output, subject_conf_output, type_output, type_conf_output]
    )
    
    # 回车也可以触发
    input_text.submit(
        fn=predict_question,
        inputs=input_text,
        outputs=[subject_output, subject_conf_output, type_output, type_conf_output]
    )
    
    gr.Markdown("""
    ---
    ⚠️ **提示**：置信度低于60%时，建议人工复核。
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,
        share=False  # 设为True可生成公网链接
    )

"""Gradio Web 界面 —— 流式展示 ReAct 思考过程。

【负责人】C
【完成时间】第 3 周

【核心目标】把 agent.run_stream() 的逐步输出，
用不同颜色/emoji 在 UI 上实时展示，让评分老师看到 Agent
是"会思考的"，而不是黑盒输出答案。

【依赖】pip install gradio
"""

import sys
from pathlib import Path

# 让本文件可以直接 `python ui/gradio_app.py` 运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_llm_client
from agent import Agent
from agent.prompt import build_system_prompt
from tools.registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.wikipedia import WikipediaTool
from tools.file_io import FileReadTool, FileWriteTool
from memory.short_term import ShortTermMemory


# ====================================================================
# 初始化 Agent
# ====================================================================
def make_agent() -> Agent:
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(WikipediaTool())
    tools.register(FileReadTool())
    tools.register(FileWriteTool())

    return Agent(
        llm_client=get_llm_client(),
        tools=tools,
        memory=ShortTermMemory(),
        system_prompt=build_system_prompt(tools),
    )


# ====================================================================
# Gradio 界面
# ====================================================================
def chat_fn(message, history):
    """流式聊天回调。

    TODO(C): 让 ReAct 步骤更美观地呈现
    - 思考用浅灰
    - 工具调用用浅蓝
    - 观察结果用浅黄
    - 最终答案用粗体
    """
    agent = make_agent()  # 每次新建（简单起见；优化时可缓存）
    accumulated = ""
    for step in agent.run_stream(message):
        if step["type"] == "thought":
            accumulated += f"\n🤔 **思考**: {step['content']}\n"
        elif step["type"] == "action":
            accumulated += f"🔧 **调用工具**: `{step['content']}`\n"
        elif step["type"] == "observation":
            accumulated += f"👁️ **观察**: {step['content']}\n"
        elif step["type"] == "final":
            accumulated += f"\n---\n✅ **最终答案**: {step['content']}"
        elif step["type"] == "error":
            accumulated += f"\n⚠️ {step['content']}"
        yield accumulated


def build_ui():
    """构造 Gradio 聊天界面，流式展示 ReAct 思考过程。"""
    import gradio as gr

    demo = gr.ChatInterface(
        fn=chat_fn,
        title="🤖 Mini Agent —— ReAct 智能体",
        description="基于 ReAct 范式的 AI Agent。可以查百科、做计算、读写文件。",
        examples=[
            "(1 + 2) * 3 等于多少？",
            "爱因斯坦活了多少岁？",
            "图灵和爱因斯坦谁活得更久？",
            "把 'Hello Agent' 写入 hello.txt 然后读出来。",
        ],
    )
    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)

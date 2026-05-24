"""命令行入口。

使用：
    python main.py                    # 跑 4 个示例问题
    python main.py "你的问题"          # 跑单个问题
"""

import sys
import argparse

from config import get_llm_client
from agent import Agent
from agent.prompt import build_system_prompt
from tools.registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.wikipedia import WikipediaTool
from tools.file_io import FileReadTool, FileWriteTool
from memory.short_term import ShortTermMemory


def make_agent(version: str = "v1") -> Agent:
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(WikipediaTool())
    tools.register(FileReadTool())
    tools.register(FileWriteTool())

    return Agent(
        llm_client=get_llm_client(),
        tools=tools,
        memory=ShortTermMemory(),
        system_prompt=build_system_prompt(tools, version=version),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="*", help="要问的问题")
    parser.add_argument("--version", default="v1", choices=["v1", "v2"], help="prompt 版本")
    args = parser.parse_args()

    agent = make_agent(args.version)

    if args.question:
        question = " ".join(args.question)
        answer = agent.run(question)
        print(f"\n答案: {answer}")
        return

    # 默认跑 4 个示例
    demo_questions = [
        "(1 + 2) * 3 等于多少？",
        "圆周率前 5 位（3, 1, 4, 1, 5）的和是多少？",
        "爱因斯坦活了多少岁？",
        "图灵和爱因斯坦谁活得更久？多活了几年？",
    ]
    for q in demo_questions:
        print(f"\n{'=' * 70}")
        print(f"❓ {q}")
        print('=' * 70)
        try:
            answer = agent.run(q)
            print(f"\n✅ 答案: {answer}")
        except Exception as e:
            print(f"\n💥 异常: {e}")


if __name__ == "__main__":
    main()

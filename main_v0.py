"""
mini-agent v0 —— ReAct 范式最小可运行 Demo（教学版）
=====================================================
本文件是项目第 1 周的"原理验证"代码。所有逻辑塞在一个文件里，
目的是让 B/C/D 三位同学一眼看懂 ReAct 是怎么运作的。

第 2 周开始我们会把这些代码拆进 agent/、tools/、memory/ 三个模块，
正式分工开发。

------------------------------------------------------------
运行前准备：
    1. pip install openai
    2. 申请 DeepSeek API Key（platform.deepseek.com，新用户送 10 元）
    3. 设置环境变量：
         macOS/Linux: export DEEPSEEK_API_KEY=sk-xxxxx
         Windows    : set DEEPSEEK_API_KEY=sk-xxxxx

运行：
    python main_v0.py
------------------------------------------------------------

ReAct 范式一句话总结：
    Thought (我要做什么)  →  Action (调用什么工具)
        ↑                          ↓
    Observation (工具返回结果)  ←  执行工具
    
    这个循环跑 N 轮，直到 LLM 输出 "Final Answer: xxx"。
"""

import os
import re
import json
import ast
import math
import operator
from openai import OpenAI


# =====================================================================
# 1. 配置
# =====================================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_API_KEY:
    raise RuntimeError(
        "请先设置环境变量 DEEPSEEK_API_KEY。"
        "macOS/Linux: export DEEPSEEK_API_KEY=sk-xxxxx"
    )

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

MODEL = "deepseek-chat"
MAX_ITERATIONS = 8        # 防死循环，最多跑 8 轮
DEBUG = True              # True 时打印中间过程，方便看 ReAct 怎么思考


# =====================================================================
# 2. 工具实现
# ---------------------------------------------------------------------
# 第 2 周由 B 同学改成 Tool 基类 + ToolRegistry 的正式版。
# v0 只用最朴素的函数 + 字典，能跑通就行。
# =====================================================================

# ---- 工具一：计算器 ----
# 用 ast 模块安全求值，不要用 eval（eval 会执行任意代码，极不安全）
_SAFE_OPS = {
    ast.Add: operator.add,   ast.Sub: operator.sub,
    ast.Mult: operator.mul,  ast.Div: operator.truediv,
    ast.Pow: operator.pow,   ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

def _safe_eval(node):
    """递归求值 AST 节点，只允许预设的运算符。"""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")

def tool_calculator(expression: str) -> str:
    """计算数学表达式，支持 + - * / ** %"""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_safe_eval(tree.body))
    except Exception as e:
        return f"Error: 表达式求值失败 - {e}"


# ---- 工具二：名人生卒年查询（mock 版）----
# v0 阶段为了演示多步推理，先用一个查表的假"维基百科"。
# 第 2 周由 B 同学换成真正的 wikipedia-api。
_FAMOUS_PEOPLE = {
    "爱因斯坦":         {"born": 1879, "died": 1955},
    "albert einstein":  {"born": 1879, "died": 1955},
    "图灵":             {"born": 1912, "died": 1954},
    "alan turing":      {"born": 1912, "died": 1954},
    "牛顿":             {"born": 1643, "died": 1727},
    "isaac newton":     {"born": 1643, "died": 1727},
    "居里夫人":         {"born": 1867, "died": 1934},
    "marie curie":      {"born": 1867, "died": 1934},
    "达尔文":           {"born": 1809, "died": 1882},
    "charles darwin":   {"born": 1809, "died": 1882},
}

def tool_get_lifespan(name: str) -> str:
    """查询名人的出生与去世年份。"""
    key = name.lower().strip()
    info = _FAMOUS_PEOPLE.get(key) or _FAMOUS_PEOPLE.get(name.strip())
    if not info:
        available = list(_FAMOUS_PEOPLE.keys())[::2][:5]
        return f"Error: 未找到「{name}」。当前数据库收录: {available} 等"
    return f"{name}: 出生于 {info['born']} 年, 去世于 {info['died']} 年"


# ---- 工具注册表 ----
# v0 用字典存所有工具，第 2 周改成 ToolRegistry 类
TOOLS = {
    "calculator": {
        "fn": tool_calculator,
        "description": "数学计算器。输入数学表达式字符串，返回计算结果。",
        "args": {"expression": "string, 数学表达式，例如 '1+2*3'"},
    },
    "get_lifespan": {
        "fn": tool_get_lifespan,
        "description": "查询一个名人的出生和去世年份。",
        "args": {"name": "string, 名人姓名，例如 '爱因斯坦' 或 'Einstein'"},
    },
}


# =====================================================================
# 3. System Prompt
# ---------------------------------------------------------------------
# 这是整个项目最关键的一段文字。Agent 能不能稳定输出 JSON、
# 能不能正确调用工具，全看这里写得好不好。
# 第 2 周由 A 同学迭代多个版本，做 A/B 对比测试。
# =====================================================================

def _format_tools_for_prompt(tools: dict) -> str:
    """把工具列表格式化成 LLM 容易理解的字符串。"""
    lines = []
    for name, info in tools.items():
        args_str = ", ".join(f"{k}: {v}" for k, v in info["args"].items())
        lines.append(f"- {name}({args_str})\n    功能: {info['description']}")
    return "\n".join(lines)


SYSTEM_PROMPT = f"""你是一个 ReAct 智能体。面对用户问题，你必须严格按以下格式思考与行动：

Thought: <你的推理过程>
Action: {{"tool": "<工具名>", "args": {{...}}}}

之后系统会返回 Observation，你再根据它继续输出 Thought 和 Action，
如此循环，直到你能给出最终答案，此时输出：

Final Answer: <最终答案>

【可用工具】
{_format_tools_for_prompt(TOOLS)}

【铁律】
1. 每轮只输出一个 Thought + 一个 Action，绝对不要自己编造 Observation。
2. Action 必须是合法 JSON，键只能是 "tool" 和 "args"。
3. 任何数字运算都必须调用 calculator，禁止心算。
4. 拿到足够信息后立即输出 Final Answer，不要重复调用工具。
5. 如果工具返回 Error，请理解错误信息并调整策略。

【示例 1：单步任务】
User: (1+2)*3 等于多少？
Thought: 这是一道数学题，调用计算器。
Action: {{"tool": "calculator", "args": {{"expression": "(1+2)*3"}}}}
Observation: 9
Thought: 已经得到结果。
Final Answer: (1+2)*3 = 9

【示例 2：多步任务】
User: 牛顿活了多少岁？
Thought: 先查牛顿的生卒年。
Action: {{"tool": "get_lifespan", "args": {{"name": "牛顿"}}}}
Observation: 牛顿: 出生于 1643 年, 去世于 1727 年
Thought: 用计算器求年龄差。
Action: {{"tool": "calculator", "args": {{"expression": "1727-1643"}}}}
Observation: 84
Thought: 已经得到答案。
Final Answer: 牛顿活了 84 岁。
"""


# =====================================================================
# 4. JSON 解析器
# ---------------------------------------------------------------------
# v0 用最简版本：剥 markdown 围栏 + 中文标点替换 + 正则提取 JSON。
# 第 2 周由 B 同学加强（处理更多边界情况），目标 95% 准确率。
# =====================================================================

def parse_action(text: str) -> dict | None:
    """从 LLM 输出中提取 Action JSON，失败返回 None。"""
    # 1) 剥 markdown 代码围栏
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.replace("```", "")

    # 2) 中文标点替换为英文（LLM 偶尔会输出中文标点）
    text = (text
            .replace("：", ":")
            .replace("，", ",")
            .replace("\u201c", '"').replace("\u201d", '"')   # 中文双引号
            .replace("\u2018", "'").replace("\u2019", "'"))  # 中文单引号

    # 3) 找到 Action: 关键字之后的内容
    m = re.search(r"Action\s*:\s*(\{.*?\})\s*(?:\n|$)", text, re.DOTALL)
    if m:
        candidate = m.group(1)
    else:
        # 兜底：直接找第一个 JSON 对象
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if not m:
            return None
        candidate = m.group(0)

    # 4) 尝试解析
    try:
        result = json.loads(candidate)
        if isinstance(result, dict) and "tool" in result:
            return result
    except json.JSONDecodeError:
        pass
    return None


# =====================================================================
# 5. ReAct 主循环
# ---------------------------------------------------------------------
# 这是整个 Agent 的"心脏"。第 2 周由 A 同学改成 Agent 类。
# =====================================================================

def call_llm(messages: list[dict]) -> str:
    """调用 DeepSeek，返回模型输出。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.0,             # Agent 用 0，输出稳定
        # 关键技巧：让 LLM 输出到 Observation 就停下，
        # 否则它会自己脑补 Observation 内容，整个循环就废了
        stop=["Observation:", "\nObservation"],
    )
    return response.choices[0].message.content


def run_agent(question: str) -> str:
    """跑完整个 ReAct 循环，返回最终答案。"""
    print(f"\n{'=' * 70}")
    print(f"❓ 用户问题: {question}")
    print('=' * 70)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": question},
    ]

    for step in range(1, MAX_ITERATIONS + 1):
        # ---- 5.1 调用 LLM ----
        output = call_llm(messages)
        if DEBUG:
            print(f"\n--- 第 {step} 轮 · LLM 输出 ---\n{output}")

        # ---- 5.2 检查是否给出最终答案 ----
        if "Final Answer:" in output:
            answer = output.split("Final Answer:")[-1].strip()
            print(f"\n{'=' * 70}")
            print(f"✅ 最终答案: {answer}")
            print(f"   (共用了 {step} 轮)")
            print('=' * 70)
            return answer

        # ---- 5.3 解析 Action ----
        action = parse_action(output)
        if not action:
            # 解析失败，把错误反馈给 LLM 让它重试
            if DEBUG:
                print("⚠️ 解析 Action 失败，将错误反馈给 LLM")
            messages.append({"role": "assistant", "content": output})
            messages.append({
                "role": "user",
                "content": "Observation: Error: 你的 Action 不是合法 JSON，"
                           "请按 {\"tool\": \"...\", \"args\": {...}} 格式重试。"
            })
            continue

        # ---- 5.4 执行工具 ----
        tool_name = action.get("tool", "")
        tool_args = action.get("args", {}) or {}

        if tool_name not in TOOLS:
            observation = (f"Error: 工具 '{tool_name}' 不存在。"
                           f"可用工具: {list(TOOLS.keys())}")
        else:
            try:
                observation = TOOLS[tool_name]["fn"](**tool_args)
            except TypeError as e:
                observation = f"Error: 参数不匹配 - {e}"
            except Exception as e:
                observation = f"Error: 工具执行异常 - {e}"

        if DEBUG:
            print(f"🔧 调用 {tool_name}({tool_args})")
            print(f"👁️  Observation: {observation}")

        # ---- 5.5 把本轮结果塞回 messages，进入下一轮 ----
        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    print(f"\n⚠️ 达到最大迭代次数 {MAX_ITERATIONS}，强制退出")
    return "(未能给出答案)"


# =====================================================================
# 6. 测试入口
# =====================================================================
if __name__ == "__main__":
    test_cases = [
        # 简单：单步计算
        "(1 + 2) * 3 等于多少？",

        # 中等：单工具但需要先理解再调用
        "圆周率前 5 位（3, 1, 4, 1, 5）的和是多少？",

        # 进阶：跨工具多步推理（ReAct 的真正威力）
        "爱因斯坦活了多少岁？",

        # 困难：双 wiki + calc，三步以上
        "图灵和爱因斯坦谁活得更久？多活了几年？",
    ]

    for question in test_cases:
        try:
            run_agent(question)
        except Exception as e:
            print(f"\n💥 异常: {e}")
        print()  # 分隔

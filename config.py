"""全局配置 —— 所有人共用。

【负责人】组长 A 维护，改动前在群里同步。
"""

import os

# ===== LLM 配置 =====
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# 备用模型（DeepSeek 不可用时切换）
# 通义千问需要：QWEN_API_KEY，base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"

# ===== Agent 行为 =====
MAX_ITERATIONS = 10        # ReAct 循环最大轮数
TEMPERATURE = 0.0          # Agent 用 0，输出稳定
MAX_CONTEXT_TOKENS = 6000  # 短期记忆 token 上限

# ===== 工具配置 =====
WORKSPACE_DIR = "./workspace"   # 文件工具的工作目录
WIKIPEDIA_LANG = "zh"           # 维基百科默认语言
WIKIPEDIA_TIMEOUT = 10          # 秒

# ===== 调试 =====
DEBUG = True                # True 时打印 ReAct 中间过程


def get_llm_client():
    """获取 LLM 客户端（默认 DeepSeek，可切换为通义千问）。"""
    from openai import OpenAI
    if not DEEPSEEK_API_KEY:
        raise RuntimeError(
            "请先设置 DEEPSEEK_API_KEY 环境变量。"
            "macOS/Linux: export DEEPSEEK_API_KEY=sk-xxxxx"
        )
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

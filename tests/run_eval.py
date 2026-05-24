"""评测脚本 —— 一键跑完所有测试用例，输出 CSV 报告。

【负责人】D
【完成时间】第 2 周末出 v1，第 3 周做实验数据收集

使用方式：
    python tests/run_eval.py
    python tests/run_eval.py --prompt-version v2     # 对比不同 Prompt
    python tests/run_eval.py --cases tests/cases.json
"""

import sys
import json
import csv
import time
import argparse
from pathlib import Path

# 让本文件可以直接运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_llm_client
from agent import Agent
from agent.prompt import build_system_prompt
from tools.registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.wikipedia import WikipediaTool
from tools.file_io import FileReadTool, FileWriteTool
from memory.short_term import ShortTermMemory


def make_agent(prompt_version: str = "v1") -> Agent:
    """初始化一个全功能 Agent"""
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(WikipediaTool())
    tools.register(FileReadTool())
    tools.register(FileWriteTool())

    return Agent(
        llm_client=get_llm_client(),
        tools=tools,
        memory=ShortTermMemory(),
        system_prompt=build_system_prompt(tools, version=prompt_version),
    )


def check_keywords(answer: str, keywords: list[str]) -> bool:
    """检查答案中是否包含至少一个预期关键字"""
    return any(kw in answer for kw in keywords)


def evaluate(cases_path: str, output_path: str, prompt_version: str = "v1"):
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    agent = make_agent(prompt_version)

    print(f"\n{'=' * 70}")
    print(f"开始评测 | Prompt: {prompt_version} | 共 {len(cases)} 个用例")
    print('=' * 70)

    results = []
    for case in cases:
        print(f"\n[{case['id']}] {case['question']}")
        t0 = time.time()
        try:
            answer = agent.run(case["question"])
            elapsed = time.time() - t0
            passed = check_keywords(answer, case["expected_keywords"])
            results.append({
                "id": case["id"],
                "difficulty": case["difficulty"],
                "question": case["question"],
                "answer": answer[:200],   # 截断防止 CSV 太长
                "passed": passed,
                "iterations": agent.last_iteration_count,
                "tokens": agent.last_token_count,
                "elapsed_sec": round(elapsed, 2),
                "expected_tools": ",".join(case.get("expected_tools", [])),
            })
            print(f"  {'✅ PASS' if passed else '❌ FAIL'} | "
                  f"轮数 {agent.last_iteration_count} | "
                  f"tokens {agent.last_token_count} | "
                  f"{elapsed:.1f}s")
            print(f"  答案: {answer[:100]}")
        except Exception as e:
            elapsed = time.time() - t0
            results.append({
                "id": case["id"],
                "difficulty": case["difficulty"],
                "question": case["question"],
                "answer": f"EXCEPTION: {e}",
                "passed": False,
                "iterations": agent.last_iteration_count,
                "tokens": agent.last_token_count,
                "elapsed_sec": round(elapsed, 2),
                "expected_tools": ",".join(case.get("expected_tools", [])),
            })
            print(f"  💥 异常: {e}")

    # 输出 CSV
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    # 输出汇总
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_iter = sum(r["iterations"] for r in results) / total if total else 0
    avg_tokens = sum(r["tokens"] for r in results) / total if total else 0
    avg_time = sum(r["elapsed_sec"] for r in results) / total if total else 0

    print(f"\n{'=' * 70}")
    print(f"📊 汇总  Prompt={prompt_version}")
    print(f"  通过率: {passed}/{total} ({100 * passed / total:.1f}%)")
    print(f"  平均轮数: {avg_iter:.1f}")
    print(f"  平均 tokens: {avg_tokens:.0f}")
    print(f"  平均耗时: {avg_time:.1f}s")
    print(f"  详细结果: {output_path}")
    print('=' * 70)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="tests/cases.json")
    parser.add_argument("--output", default="tests/results/eval_result.csv")
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--all", action="store_true", help="依次运行所有 prompt 版本并对比")
    args = parser.parse_args()

    if args.all:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")

        from tools.registry import ToolRegistry
        from tools.calculator import CalculatorTool
        from tools.wikipedia import WikipediaTool
        from tools.file_io import FileReadTool, FileWriteTool
        from agent.prompt import build_system_prompt
        _tools = ToolRegistry()
        for t in [CalculatorTool(), WikipediaTool(), FileReadTool(), FileWriteTool()]:
            _tools.register(t)

        versions = ["v1", "v2"]
        summaries = []
        for version in versions:
            output = args.output.replace(".csv", f"_{version}.csv")
            results = evaluate(args.cases, output, version)
            total = len(results)
            passed = sum(1 for r in results if r["passed"])
            avg_iter = sum(r["iterations"] for r in results) / total if total else 0
            avg_tokens = sum(r["tokens"] for r in results) / total if total else 0
            avg_time = sum(r["elapsed_sec"] for r in results) / total if total else 0
            sys_prompt = build_system_prompt(_tools, version)
            sys_tokens = len(enc.encode(sys_prompt))
            summaries.append({
                "version": version,
                "passed": passed,
                "total": total,
                "avg_iter": avg_iter,
                "avg_tokens": avg_tokens,
                "avg_time": avg_time,
                "sys_tokens": sys_tokens,
            })

        print(f"\n{'=' * 70}")
        print("📊 版本对比")
        print(f"{'版本':<10} {'通过率':<16} {'平均轮数':<10} {'system prompt':<16} {'平均总tokens':<14} {'平均耗时'}")
        print('-' * 70)
        for s in summaries:
            print(f"{s['version']:<10} "
                  f"{s['passed']}/{s['total']} ({100*s['passed']/s['total']:.1f}%)     "
                  f"{s['avg_iter']:<10.1f} "
                  f"{s['sys_tokens']} tok{'':<8} "
                  f"{s['avg_tokens']:<14.0f} "
                  f"{s['avg_time']:.1f}s")
        print()
        v1_sys = summaries[0]["sys_tokens"]
        for s in summaries[1:]:
            diff = s["sys_tokens"] - v1_sys
            token_diff = s["avg_tokens"] - summaries[0]["avg_tokens"]
            print(f"{s['version']} vs v1: system prompt +{diff} tok，"
                  f"平均总tokens {token_diff:+.0f}，"
                  f"system prompt 贡献约 {diff * summaries[0]['avg_iter']:.0f} tok/题（{diff}×{summaries[0]['avg_iter']:.1f}轮）")
        print('=' * 70)
    else:
        evaluate(args.cases, args.output, args.prompt_version)

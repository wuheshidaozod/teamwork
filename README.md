# mini-agent

基于 ReAct 范式的 AI Agent 框架 —— 浙江大学《大模型与人工智能》大作业（选题一）。

> 从"会说话"到"能做事"——让 LLM 不仅能聊天，还能主动调用工具完成多步推理任务。

## 项目结构

```
mini-agent/
├── agent/              # A（组长）负责：核心 Agent 类与 ReAct 循环
│   ├── core.py         #   Agent 主类
│   ├── prompt.py       #   System Prompt 设计
│   └── parser.py       #   LLM 输出解析（与 B 共同维护）
├── tools/              # B 负责：工具实现
│   ├── base.py         #   Tool 基类
│   ├── registry.py     #   工具注册表
│   ├── calculator.py   #   计算器
│   ├── wikipedia.py    #   维基百科
│   ├── file_io.py      #   文件读写
│   └── python_exec.py  #   (进阶) Python 沙箱
├── memory/             # C 负责：对话历史与记忆
│   ├── base.py         #   Memory 基类
│   ├── short_term.py   #   短期记忆（滑窗 + token 截断）
│   └── long_term.py    #   (进阶) 长期记忆（向量检索）
├── ui/                 # C 负责：Web 界面
│   └── gradio_app.py   #   Gradio 聊天界面
├── tests/              # D 负责：测试与评测
│   ├── cases.json      #   测试用例
│   ├── run_eval.py     #   评测脚本
│   ├── test_tools.py   #   工具单元测试
│   └── test_parser.py  #   解析器单元测试
├── docs/               # 共同维护
│   ├── INTERFACES.md   #   接口约定（任何修改都要同步）
│   └── REPORT.md       #   实验报告草稿（D 主笔）
├── workspace/          # 文件工具的工作目录（运行时生成内容）
├── config.py           # 全局配置（API key、模型选择）
├── main.py             # 命令行入口
├── main_v0.py          # 第 1 周的原型版本（保留作参考）
├── requirements.txt    # 依赖
├── .gitignore
└── README.md
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API key（DeepSeek，新用户送 10 元额度）
export DEEPSEEK_API_KEY=sk-xxxxx     # macOS/Linux
# set DEEPSEEK_API_KEY=sk-xxxxx       # Windows

# 3. 跑命令行版
python main.py

# 4. 跑 Web 版
python ui/gradio_app.py

# 5. 跑评测
python tests/run_eval.py
```

## 分工与里程碑

详见 [docs/INTERFACES.md](docs/INTERFACES.md) 和组员任务说明书。

| 周次 | 关键交付 |
|------|---------|
| 第 1 周 | 开题报告 + main_v0.py 跑通（✅ 已完成） |
| 第 2 周 | 3 工具 + Memory 接入，能完成「爱因斯坦活了多少岁」 |
| 第 3 周 | Gradio UI、流式输出、Prompt 调优，成功率 ≥ 70% |
| 第 4 周 | 实验报告、Demo 视频、答辩 PPT |

## 团队成员

| 代号 | 姓名 | 负责模块 |
|------|------|---------|
| A | XXX（组长） | agent/ |
| B | XXX | tools/ + agent/parser.py |
| C | XXX | memory/ + ui/ |
| D | XXX | tests/ + docs/REPORT.md |

## 约束

- 禁止使用 LangChain / LlamaIndex 等高层框架（课程要求）
- 所有人写代码前先读 `docs/INTERFACES.md`，接口变更必须在群里讨论

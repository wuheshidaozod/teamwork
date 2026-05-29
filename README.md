# mini-agent

基于 ReAct 范式的 AI Agent 框架 —— 浙江大学《大模型与人工智能》大作业（选题一）。

> 从"会说话"到"能做事"——让 LLM 不仅能聊天，还能主动调用工具完成多步推理任务。

## 项目结构

```
mini-agent/
├── agent/              # A（组长）负责：核心 Agent 类与 ReAct 循环
│   ├── core.py         #   Agent 主类
│   ├── prompt.py       #   System Prompt 设计（v1 / v2）
│   └── parser.py       #   LLM 输出解析（与 B 共同维护）
├── tools/              # B 负责：工具实现
│   ├── base.py         #   Tool 基类
│   ├── registry.py     #   工具注册表
│   ├── calculator.py   #   计算器（支持四则运算 / 三角 / 对数等）
│   ├── wikipedia.py    #   维基百科（中文优先，自动回退英文）
│   ├── file_io.py      #   文件读写（限制在 workspace/ 目录内）
│   └── python_exec.py  #   (进阶) Python 沙箱
├── memory/             # C 负责：对话历史与记忆
│   ├── base.py         #   Memory 基类
│   ├── short_term.py   #   短期记忆（滑窗 + token 截断）
│   └── long_term.py    #   (进阶) 长期记忆（向量检索）
├── ui/                 # C 负责：Web 界面
│   └── gradio_app.py   #   Gradio 聊天界面
├── tests/              # D 负责：测试与评测
│   ├── cases.json      #   测试用例（20 题）
│   ├── run_eval.py     #   评测脚本（支持并发、v1/v2 对比）
│   ├── test_tools.py   #   工具单元测试
│   └── test_parser.py  #   解析器单元测试
├── docs/
│   ├── INTERFACES.md   #   接口约定（任何修改都要同步）
│   └── REPORT.md       #   实验报告草稿
├── workspace/          # 文件工具的工作目录（运行时生成内容）
├── config.py           # 全局配置
├── main.py             # 命令行入口
├── main_v0.py          # 第 1 周原型（保留作参考）
├── requirements.txt    # 依赖
├── .env.example        # 环境变量模板（复制为 .env 后填写）
├── run_v1.bat          # 一键评测 v1（Windows）
├── run_v2.bat          # 一键评测 v2（Windows）
├── run_all.bat         # v1 + v2 串行对比（Windows）
├── run_all_fast.bat    # v1 + v2 并发对比，约快 3.5 倍（Windows）
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows
```

打开 `.env`，填入 DeepSeek API Key（前往 [platform.deepseek.com](https://platform.deepseek.com) 注册，新用户赠 10 元额度）：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

> **Wikipedia 代理**：程序会自动读取系统（IE）代理，无需额外配置。
> 如需手动指定，在 `.env` 中设置 `WIKIPEDIA_PROXY=http://127.0.0.1:10808`。

### 3. 运行

**命令行单问题：**

```bash
python -X utf8 main.py "爱因斯坦活了多少岁？"
python -X utf8 main.py --version v2 "图灵和爱因斯坦谁活得更久？"
```

**评测（Windows 双击 bat 文件，或命令行运行）：**

```bash
# 串行评测（保留完整思考过程输出）
python -X utf8 tests/run_eval.py --prompt-version v1
python -X utf8 tests/run_eval.py --prompt-version v2

# v1 vs v2 对比（并发 4 线程，约快 3.5 倍）
python -X utf8 tests/run_eval.py --all --workers 4
```

**Web 界面：**

```bash
python ui/gradio_app.py
```

## 评测结果

| 版本 | 通过率 | 平均轮数 | System Prompt |
|------|--------|---------|--------------|
| v1   | 20/20 (100%) | 2.2 | 约 831 tok |
| v2   | 20/20 (100%) | 2.2 | 约 1022 tok |

v2 相比 v1 新增**工具选择决策树**和**错误处理规则**，对复杂多步任务更稳定。

## 分工与里程碑

| 周次 | 关键交付 |
|------|---------|
| 第 1 周 | 开题报告 + main_v0.py 跑通（✅ 已完成） |
| 第 2 周 | 3 工具 + Memory 接入，能完成「爱因斯坦活了多少岁」（✅ 已完成） |
| 第 3 周 | Gradio UI、流式输出、Prompt 调优，成功率 ≥ 70%（✅ 100%） |
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

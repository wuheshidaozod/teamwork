# 实验报告（草稿）

> 【负责人】D 主笔，A/B/C 提供素材
> 【完成时间】第 3 周末出初稿，第 4 周定稿
> 【字数目标】8-10 页 Word

## 1. 核心原理与算法设计

### 1.1 ReAct 范式介绍
（A 提供素材）TODO：介绍 ReAct = Reasoning + Acting，画出 Thought → Action → Observation 循环图。

### 1.2 Agent 决策闭环流程图
（A 绘制）TODO：用 draw.io / Excalidraw 画一张架构图，覆盖 LLM、Parser、ToolRegistry、Memory 四大模块。

### 1.3 与 OpenAI Function Calling 的对比
（开题报告中已写，搬过来精简）TODO：对比表格。

## 2. 工程实现细节

### 2.1 模块化设计
（A 提供）TODO：四大模块（agent / tools / memory / ui）的职责说明。

### 2.2 核心类说明

#### 2.2.1 Agent 类（agent/core.py）
（A 提供）

#### 2.2.2 ToolRegistry（tools/registry.py）
（B 提供）

#### 2.2.3 ShortTermMemory（memory/short_term.py）
（C 提供）

#### 2.2.4 parse_action（agent/parser.py）
（B 提供）TODO：重点描述对 5 种异常情况的容错处理。

### 2.3 关键工程问题与解决方案
TODO：
- `stop=["Observation:"]` 的妙用（防止 LLM 脑补观察值）
- `max_iterations` 防死循环
- JSON 解析的容错策略
- 工具异常回填给 LLM 而不是抛出

## 3. 实验结果与分析

### 3.1 实验设置
- 模型：DeepSeek-Chat
- 测试用例：8 个，覆盖单步/多步/鲁棒性
- temperature: 0.0
- max_iterations: 10

### 3.2 整体成功率
（D 跑实验填充）TODO：插入柱状图，对比 Prompt v1 vs v2 的成功率。

### 3.3 多步任务能力分析
（D 分析）TODO：T3、T4、T6 的成功率与平均迭代轮数。

### 3.4 失败案例分类
TODO：插入饼图，分类：
- JSON 解析失败（B 负责）
- 工具调用错误（B 负责）
- 推理逻辑错误（A 的 Prompt 问题）
- 最终答案错误

### 3.5 性能指标
TODO：
- 平均 token 消耗
- 平均响应时间
- 迭代轮数分布直方图

### 3.6 进阶功能展示
（C 提供）TODO：
- Gradio UI 截图
- 流式输出效果
- 长期记忆检索演示（如果做了）

## 4. 总结与展望

### 4.1 主要工作
TODO：列出关键成果。

### 4.2 难点突破
TODO：3-4 个最值得讲的工程难题。

### 4.3 不足与改进方向
TODO：诚实地写局限性，反而能加分。

## 5. 团队分工

（参考开题报告分工章节）

## 参考文献

1. Yao S, et al. ReAct: Synergizing Reasoning and Acting in Language Models. arXiv:2210.03629, 2022.
2. OpenAI. Function calling. https://platform.openai.com/docs/guides/function-calling
3. DeepSeek API 文档. https://api-docs.deepseek.com

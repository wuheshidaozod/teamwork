"""Python 代码执行沙箱（进阶工具）。

【负责人】B
【完成时间】第 3 周（进阶项，时间不够可以砍掉）

【安全策略】用 subprocess 隔离 + 资源限制 + 超时

WARNING: 这是有一定风险的工具，仅用于课程演示，不要在生产环境用。
"""

import subprocess
import tempfile
import os

from tools.base import Tool


class PythonExecTool(Tool):
    name = "python_exec"
    description = "执行一段 Python 代码并返回标准输出。代码必须能在 5 秒内完成。"
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "要执行的 Python 代码"
            }
        },
        "required": ["code"],
    }

    def run(self, code: str) -> str:
        """
        TODO(B 第 3 周): 实现 Python 沙箱

        参考实现：

        with tempfile.NamedTemporaryFile(suffix='.py', mode='w',
                                          delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ['python3', tmp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return f"Error: {result.stderr[:500]}"
            output = result.stdout[:2000]  # 限制输出长度
            return output if output else "(代码执行完成，无输出)"
        except subprocess.TimeoutExpired:
            return "Error: 执行超时（>5 秒）"
        except Exception as e:
            return f"Error: {e}"
        finally:
            os.unlink(tmp_path)
        """
        return "[TODO B 第 3 周] 待实现"

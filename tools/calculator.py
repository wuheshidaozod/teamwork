"""计算器工具。

【负责人】B
【完成时间】第 2 周（本文件已给出完整实现，B 直接使用 + 加测试）

【安全要点】用 ast 而不是 eval，避免任意代码执行。
"""

import ast
import math
import operator

from tools.base import Tool


# 允许的二元运算符
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

# 允许的一元运算符
_UNARY_OPS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# 允许的函数调用
_SAFE_FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "sqrt": math.sqrt, "log": math.log, "log2": math.log2,
    "log10": math.log10, "exp": math.exp, "abs": abs,
    "round": round, "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
}


def _safe_eval(node):
    """递归求值 AST 节点，只允许预设的运算符和函数。"""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise ValueError(f"不支持的运算符: {op_type.__name__}")
        return _BIN_OPS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"不支持的一元运算符: {op_type.__name__}")
        return _UNARY_OPS[op_type](_safe_eval(node.operand))
    if isinstance(node, ast.Name):
        if node.id in _SAFE_FUNCTIONS and not callable(_SAFE_FUNCTIONS[node.id]):
            return _SAFE_FUNCTIONS[node.id]  # pi, e
        raise ValueError(f"未定义的变量: {node.id}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_FUNCTIONS:
            raise ValueError(f"不允许的函数调用: {ast.dump(node.func)}")
        fn = _SAFE_FUNCTIONS[node.func.id]
        args = [_safe_eval(a) for a in node.args]
        return fn(*args)
    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")


class CalculatorTool(Tool):
    name = "calculator"
    description = "数学计算器。输入数学表达式字符串，返回计算结果。支持 +-*/% **、sin/cos/sqrt/log 等函数。"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '(1+2)*3' 或 'sqrt(16)+log(e)'"
            }
        },
        "required": ["expression"],
    }

    def run(self, expression: str) -> str:
        try:
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree.body)
            # 整数返回整数形式，浮点保留 6 位有效
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Error: 表达式求值失败 - {e}"

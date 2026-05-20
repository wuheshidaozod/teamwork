"""工具层单元测试。

【负责人】D（用例设计）+ B（实现 wikipedia 后补充）
运行：pytest tests/test_tools.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.calculator import CalculatorTool
from tools.file_io import FileReadTool, FileWriteTool


# ============ 计算器测试 ============
class TestCalculator:
    def setup_method(self):
        self.tool = CalculatorTool()

    def test_basic_arithmetic(self):
        assert self.tool.run(expression="1+2") == "3"
        assert self.tool.run(expression="(1+2)*3") == "9"
        assert self.tool.run(expression="10/2") == "5"

    def test_power_and_mod(self):
        assert self.tool.run(expression="2**10") == "1024"
        assert self.tool.run(expression="10%3") == "1"

    def test_lifespan_calculation(self):
        # T3 测试用例核心
        assert self.tool.run(expression="1955-1879") == "76"

    def test_sum(self):
        # T5 测试用例核心
        assert self.tool.run(expression="3+1+4+1+5") == "14"

    def test_math_functions(self):
        assert self.tool.run(expression="sqrt(16)") == "4"
        assert self.tool.run(expression="abs(-5)") == "5"

    def test_invalid_expression(self):
        result = self.tool.run(expression="1+abc")
        assert result.startswith("Error")

    def test_security_no_eval(self):
        """不允许调用 import、open 等危险函数"""
        result = self.tool.run(expression="__import__('os')")
        assert result.startswith("Error")


# ============ 文件读写测试 ============
class TestFileIO:
    def setup_method(self):
        self.reader = FileReadTool()
        self.writer = FileWriteTool()

    def test_write_then_read(self):
        write_result = self.writer.run(filename="test_pytest.txt",
                                        content="Hello, Agent!")
        assert "已写入" in write_result

        read_result = self.reader.run(filename="test_pytest.txt")
        assert "Hello, Agent!" in read_result

    def test_path_traversal_blocked(self):
        """不允许 ../ 跳出 workspace"""
        result = self.writer.run(filename="../../../etc/passwd",
                                 content="hacked")
        assert "Error" in result and "越界" in result

    def test_read_nonexistent(self):
        result = self.reader.run(filename="does_not_exist_12345.txt")
        assert "Error" in result

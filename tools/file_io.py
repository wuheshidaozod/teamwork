"""文件读写工具。

【负责人】B
【完成时间】第 2 周（本文件已给出完整实现）

【安全要求】
1. 所有路径限制在 WORKSPACE_DIR 内，禁止 ../ 跳出
2. 文件大小限制 1MB
3. 写入时自动创建目录
"""

import os
from pathlib import Path

from tools.base import Tool
from config import WORKSPACE_DIR


_MAX_FILE_SIZE = 1024 * 1024  # 1MB


def _resolve_safe_path(filename: str) -> Path | None:
    """把文件名解析到 workspace 内的安全路径。越界返回 None。"""
    workspace = Path(WORKSPACE_DIR).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    # 清理路径
    target = (workspace / filename).resolve()

    # 安全检查：必须在 workspace 内
    try:
        target.relative_to(workspace)
    except ValueError:
        return None
    return target


class FileReadTool(Tool):
    name = "file_read"
    description = f"读取 {WORKSPACE_DIR}/ 目录下的文本文件。"
    parameters = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "文件名（相对于 workspace/），如 'note.txt'"
            }
        },
        "required": ["filename"],
    }

    def run(self, filename: str) -> str:
        target = _resolve_safe_path(filename)
        if target is None:
            return "Error: 文件路径越界，必须在 workspace/ 目录内"
        if not target.exists():
            return f"Error: 文件 {filename} 不存在"
        if target.stat().st_size > _MAX_FILE_SIZE:
            return f"Error: 文件过大（>1MB）"
        try:
            return target.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error: 读取失败 - {e}"


class FileWriteTool(Tool):
    name = "file_write"
    description = f"向 {WORKSPACE_DIR}/ 目录下的文件写入文本。文件不存在会创建。"
    parameters = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "文件名"},
            "content": {"type": "string", "description": "要写入的内容"},
        },
        "required": ["filename", "content"],
    }

    def run(self, filename: str, content: str) -> str:
        target = _resolve_safe_path(filename)
        if target is None:
            return "Error: 文件路径越界，必须在 workspace/ 目录内"
        if len(content.encode("utf-8")) > _MAX_FILE_SIZE:
            return "Error: 内容过大（>1MB）"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"已写入 {filename}（{len(content)} 字符）"
        except Exception as e:
            return f"Error: 写入失败 - {e}"

"""
detector.py - 检测已装的 AI 编程工具
=====================================

检测:
- Claude Code (claude CLI)
- OpenAI Codex (codex CLI)
- Cursor (IDE 安装)
- OpenClaw (openclaw CLI)
- Hermes (hermes CLI)
- Aider (aider CLI)

每个工具检测 3 个状态:
- 未安装
- 已安装未激活
- 已激活
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# AI 工具定义
AI_TOOLS = [
    {
        "name": "Claude Code",
        "key": "claude_code",
        "cmd": "claude",
        "description": "Anthropic 官方 CLI",
        "config_path": "~/.claude",
        "env_var": "ANTHROPIC_API_KEY",
        "fallback_url": "https://api.skillai.top",
    },
    {
        "name": "OpenAI Codex",
        "key": "codex",
        "cmd": "codex",
        "description": "OpenAI 官方 CLI",
        "config_path": "~/.codex",
        "env_var": "OPENAI_API_KEY",
        "fallback_url": "https://api.skillai.top",
    },
    {
        "name": "Cursor",
        "key": "cursor",
        "cmd": "cursor",
        "description": "AI IDE",
        "config_path": None,  # 通过应用程序检测
        "env_var": None,
        "fallback_url": None,
    },
    {
        "name": "OpenClaw",
        "key": "openclaw",
        "cmd": "openclaw",
        "description": "OpenClaw AI Agent",
        "config_path": "~/.openclaw",
        "env_var": "OPENCLAW_API_KEY",
        "fallback_url": "https://api.skillai.top",
    },
    {
        "name": "Hermes",
        "key": "hermes",
        "cmd": "hermes",
        "description": "Hermes Agent(自学习)",
        "config_path": "~/.hermes",
        "env_var": "HERMES_API_KEY",
        "fallback_url": "https://api.skillai.top",
    },
    {
        "name": "Aider",
        "key": "aider",
        "cmd": "aider",
        "description": "AI 结对编程",
        "config_path": "~/.aider",
        "env_var": "OPENAI_API_KEY",
        "fallback_url": "https://api.skillai.top",
    },
]


def detect_all_tools() -> list:
    """检测所有 AI 工具状态"""
    results = []
    for tool in AI_TOOLS:
        info = detect_tool(tool)
        results.append(info)
    return results


def detect_tool(tool: dict) -> dict:
    """检测单个工具状态"""
    cmd = tool.get("cmd")
    result = {
        "name": tool["name"],
        "key": tool["key"],
        "description": tool["description"],
        "installed": False,
        "version": None,
        "active": False,
        "has_config": False,
        "has_fallback": False,
        "env_var": tool.get("env_var"),
        "fallback_url": tool.get("fallback_url"),
    }

    # 检查命令是否在 PATH
    if cmd and shutil.which(cmd):
        result["installed"] = True
        # 获取版本
        try:
            out = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ver_line = (out.stdout or out.stderr).strip().split("\n")[0]
            result["version"] = ver_line
        except Exception:
            result["version"] = "未知"

    # 检查环境变量
    if tool.get("env_var"):
        env_val = os.getenv(tool["env_var"], "")
        if env_val:
            result["active"] = True

    # 检查配置文件
    if tool.get("config_path"):
        cfg_path = Path(tool["config_path"]).expanduser()
        if cfg_path.exists():
            result["has_config"] = True

    return result


def get_install_instructions(tool_key: str) -> str:
    """获取安装命令"""
    instructions = {
        "claude_code": "npm install -g @anthropic-ai/claude-code",
        "codex": "npm install -g @openai/codex",
        "openclaw": "npm install -g @openclaw/openclaw",
        "hermes": "pip install hermes-agent",
        "aider": "pip install aider-chat",
        "cursor": "从 https://cursor.sh 下载",
    }
    return instructions.get(tool_key, "未知")
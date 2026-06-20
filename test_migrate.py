"""test_migrate.py — migrate_to_free_ai_router.py 单元测试 (4 个)
跑法: python -X utf8 -m unittest test_migrate -v
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# 允许从 cc-switch 目录跑
sys.path.insert(0, str(Path(__file__).parent))
import migrate_to_free_ai_router as mig  # noqa: E402


class TestBuildPlan(unittest.TestCase):

    def test_plan_basic(self):
        """5 个 cc-switch 工具 → 5 个 provider 映射"""
        tools = [
            {"key": "claude_code", "name": "Claude Code", "installed": True, "api_key_set": True, "active": True},
            {"key": "codex",       "name": "OpenAI Codex", "installed": True, "api_key_set": True, "active": False},
            {"key": "openclaw",    "name": "OpenClaw",    "installed": True, "api_key_set": False, "active": False},
            {"key": "hermes",      "name": "Hermes",      "installed": False, "api_key_set": False, "active": False},
            {"key": "aider",       "name": "Aider",       "installed": True, "api_key_set": True, "active": False},
        ]
        active, plan = mig.build_migration_plan("claude_code", tools)
        self.assertEqual(active, "claude_code")
        self.assertEqual(len(plan), 5)
        # claude_code 是 active
        active_entries = [e for e in plan if e["active"]]
        self.assertEqual(len(active_entries), 1)
        self.assertEqual(active_entries[0]["tool_key"], "claude_code")
        # openclaw api_key_set=False → enabled=False
        oc = [e for e in plan if e["tool_key"] == "openclaw"][0]
        self.assertFalse(oc["provider"]["enabled"])
        # hermes installed=False → enabled=False
        hm = [e for e in plan if e["tool_key"] == "hermes"][0]
        self.assertFalse(hm["provider"]["enabled"])

    def test_plan_unknown_tool(self):
        """未知工具跳过 + 不崩"""
        tools = [
            {"key": "claude_code", "name": "Claude Code", "installed": True, "api_key_set": True, "active": True},
            {"key": "unknown_tool", "name": "???", "installed": True, "api_key_set": True, "active": False},
        ]
        active, plan = mig.build_migration_plan("claude_code", tools)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool_key"], "claude_code")

    def test_plan_priority_incremental(self):
        """priority 从 10 开始递增, 不冲突"""
        tools = [
            {"key": "claude_code", "name": "C", "installed": True, "api_key_set": True, "active": True},
            {"key": "codex",       "name": "X", "installed": True, "api_key_set": True, "active": False},
            {"key": "openclaw",    "name": "O", "installed": True, "api_key_set": True, "active": False},
        ]
        _, plan = mig.build_migration_plan("claude_code", tools)
        priorities = [e["provider"]["priority"] for e in plan]
        self.assertEqual(priorities, [10, 11, 12])

    def test_plan_no_tools(self):
        """空 tools → plan=None"""
        active, plan = mig.build_migration_plan(None, [])
        self.assertIsNone(active)
        self.assertEqual(plan, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

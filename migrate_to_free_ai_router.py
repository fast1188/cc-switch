"""migrate_to_free_ai_router.py — cc-switch → free-ai-router 迁移工具 v0.1

用法:
    py migrate_to_free_ai_router.py                  # 干跑, 只看会做什么
    py migrate_to_free_ai_router.py --dry-run        # 同上 (--dry-run 显式)
    py migrate_to_free_ai_router.py --execute        # 真的生成 free-ai-router 配置
    py migrate_to_free_ai_router.py --execute --output <path>  # 自定义输出路径

约束:
- 不读 keys/ 或 env 真实值, 只读 cc-switch 自身的 ~/.cc-switch/state.json
- 备份原 free-ai-router config 到 .bak
- 0 第三方依赖
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Windows GBK stdout
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 路径
CC_SWITCH_STATE = Path.home() / ".cc-switch" / "state.json"
CC_SWITCH_CONFIG = Path.home() / ".cc-switch" / "config.json"
ROUTER_CONFIG = Path(r"D:\Github开源项目\项目源码\free-ai-router\router_config.json")
ROUTER_CONFIG_BAK = Path(str(ROUTER_CONFIG) + f".bak.{datetime.now().strftime('%Y%m%d-%H%M%S')}")

# cc-switch 工具 → free-ai-router provider 映射
TOOL_TO_PROVIDER = {
    "claude_code": {
        "name": "minimax_1",
        "label": "minimax #1 (claude_code 迁移)",
        "base_url": "https://api.minimaxi.com/v1",
        "api_key_env": "MINIMAX_API_KEY_1",
        "models": ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.7-highspeed"],
    },
    "codex": {
        "name": "deepseek_1",
        "label": "deepseek #1 (codex 迁移)",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY_1",
        "models": ["deepseek-chat", "deepseek-reasoner", "deepseek-v4-flash", "deepseek-v4-pro"],
    },
    "openclaw": {
        "name": "minimax_2",
        "label": "minimax #2 (openclaw 迁移)",
        "base_url": "https://api.minimaxi.com/v1",
        "api_key_env": "MINIMAX_API_KEY_2",
        "models": ["MiniMax-M3", "MiniMax-M2.7"],
    },
    "hermes": {
        "name": "minimax_3",
        "label": "minimax #3 (hermes 迁移)",
        "base_url": "https://api.minimaxi.com/v1",
        "api_key_env": "MINIMAX_API_KEY_3",
        "models": ["MiniMax-M3", "MiniMax-M2.7"],
    },
    "aider": {
        "name": "deepseek_2",
        "label": "deepseek #2 (aider 迁移)",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY_2",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
}


def read_cc_switch_state():
    """读 cc-switch state.json, 返回 (active_tool, all_tools)"""
    if not CC_SWITCH_STATE.exists():
        return None, []
    try:
        state = json.loads(CC_SWITCH_STATE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[migrate] 解析 cc-switch state 失败: {e}", file=sys.stderr)
        return None, []
    all_tools = state.get("tools", [])
    active = None
    for t in all_tools:
        if t.get("active"):
            active = t.get("key")
            break
    return active, all_tools


def read_existing_router_config():
    """读现有 router_config.json, 返回 (default_model, providers)"""
    if not ROUTER_CONFIG.exists():
        return "deepseek-chat", []
    try:
        cfg = json.loads(ROUTER_CONFIG.read_text(encoding="utf-8"))
        return cfg.get("default_model", "deepseek-chat"), cfg.get("providers", [])
    except Exception as e:
        print(f"[migrate] 解析 router_config 失败: {e}", file=sys.stderr)
        return "deepseek-chat", []


def build_migration_plan(active_tool, all_tools):
    """构建迁移计划 — 从 cc-switch 状态 → free-ai-router providers"""
    if not all_tools:
        return None, []
    plan = []
    max_priority = 10
    for i, tool in enumerate(all_tools):
        key = tool.get("key")
        if key not in TOOL_TO_PROVIDER:
            print(f"[migrate] 跳过未知工具: {key}", file=sys.stderr)
            continue
        tmpl = TOOL_TO_PROVIDER[key]
        provider = {
            **tmpl,
            "priority": max_priority + i,
            "enabled": bool(tool.get("installed")) and bool(tool.get("api_key_set")),
        }
        plan.append({
            "tool_key": key,
            "tool_name": tool.get("name", key),
            "provider": provider,
            "active": tool.get("key") == active_tool,
        })
    return active_tool, plan


def write_router_config(plan, default_model, existing_providers, output_path, dry_run=False):
    """写新的 router_config.json, 保留现有 providers, 加入迁移的 providers"""
    # 合并: 现有 + 迁移 (去重 by name)
    existing_names = {p["name"] for p in existing_providers}
    new_providers = list(existing_providers)
    added = []
    for entry in plan:
        name = entry["provider"]["name"]
        if name in existing_names:
            print(f"[migrate] 跳过重复: {name}", file=sys.stderr)
            continue
        new_providers.append(entry["provider"])
        added.append(name)

    # 排序 by priority
    new_providers.sort(key=lambda p: p.get("priority", 100))

    new_cfg = {
        "default_model": default_model,
        "cooldown_seconds": 60,
        "providers": new_providers,
        "comment": f"由 migrate_to_free_ai_router.py 自动迁移 ({datetime.now().isoformat()}), 加了 {len(added)} 个 provider",
    }
    output_path = Path(output_path)
    if dry_run:
        print(f"[migrate:DRY-RUN] 会写到: {output_path}")
        return True, added
    # 备份
    if ROUTER_CONFIG.exists() and ROUTER_CONFIG != output_path:
        shutil.copy2(ROUTER_CONFIG, ROUTER_CONFIG_BAK)
        print(f"[migrate] 备份: {ROUTER_CONFIG_BAK}")
    output_path.write_text(
        json.dumps(new_cfg, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    return True, added


def main():
    ap = argparse.ArgumentParser(description="cc-switch → free-ai-router 迁移 v0.1")
    ap.add_argument("--execute", action="store_true",
                    help="真的写 router_config.json (默认是 dry-run)")
    ap.add_argument("--output", type=str,
                    help=f"输出路径 (默认: {ROUTER_CONFIG})")
    args = ap.parse_args()

    dry_run = not args.execute
    output = Path(args.output) if args.output else ROUTER_CONFIG

    print(f"[migrate] mode={'EXECUTE' if args.execute else 'DRY-RUN'}  output={output}")
    print(f"[migrate] cc-switch state: {CC_SWITCH_STATE}  exists={CC_SWITCH_STATE.exists()}")

    active_tool, all_tools = read_cc_switch_state()
    if not all_tools:
        print(f"[migrate] 找不到 cc-switch state ({CC_SWITCH_STATE}), 先跑 cc-switch GUI 检测工具")
        sys.exit(1)

    print(f"\n[migrate] cc-switch 当前状态:")
    print(f"  active: {active_tool or '(无)'}")
    for t in all_tools:
        key = t.get("key", "?")
        installed = "✓" if t.get("installed") else "✗"
        key_set = "key✓" if t.get("api_key_set") else "key✗"
        active_mark = " ← ACTIVE" if t.get("active") else ""
        print(f"  {key:<15} {installed} {key_set}  {t.get('name', '')}{active_mark}")

    default_model, existing_providers = read_existing_router_config()
    print(f"\n[migrate] free-ai-router 当前:")
    print(f"  default_model: {default_model}")
    print(f"  providers: {len(existing_providers)} 个 (将保留)")

    active_tool, plan = build_migration_plan(active_tool, all_tools)
    if not plan:
        print("[migrate] 没有可迁移的工具 (全部是未支持的类型)")
        sys.exit(1)

    print(f"\n[migrate] 迁移计划 ({len(plan)} 个):")
    for entry in plan:
        p = entry["provider"]
        mark = " ★ ACTIVE" if entry["active"] else ""
        print(f"  {p['name']:<14} <- {entry['tool_name']:<15} priority={p['priority']} enabled={p['enabled']}{mark}")

    print(f"\n[migrate] {'会写' if dry_run else '正在写'}: {output}")
    ok, added = write_router_config(plan, default_model, existing_providers, output, dry_run=dry_run)

    if dry_run:
        print(f"\n[migrate] DRY-RUN 完成. 加 {len(added)} 个 provider: {added}")
        print(f"[migrate] 用 --execute 真正写入")
    else:
        print(f"\n[migrate] 写入完成. 加 {len(added)} 个 provider: {added}")
        print(f"[migrate] 测试: py D:\\Github开源项目\\项目源码\\free-ai-router\\smart_router.py --status")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

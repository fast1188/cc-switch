# CC Switch

> 国产化 AI 编程工具切换器(桌面 GUI)
>
> 不是 cc-switch 复刻,做中文用户友好的差异化版本

[![MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/platform-Windows-blue)]()
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)]()
[![Linux](https://img.shields.io/badge/platform-Linux-yellow)]()

> 🌐 **控制台总览:** [fast118.github.io/console](https://fast118.github.io/console/) - 看所有 fast118 开源项目

---

## 这是什么?

CC Switch 是一个桌面 GUI 工具,帮你**一键管理多个 AI 编程助手**。

**vs 国外版 cc-switch (97k stars):**

| 维度 | cc-switch (国外) | CC Switch (我们) |
|------|------------------|------------------|
| 界面 | 英文 | **中文优先** |
| 模型市场 | 静态列表 | **一键试** |
| 国内直连 | ✗ | **内置 api.skillai.top** |
| 团队多账号 | ✗ | **多账号池** |
| Skill 集成 | ✗ | **联动 ai-agent-skills** |
| 中文文档 | ✗ | ✓ |

## 5 分钟上手

**前置:** Python 3.8+ (Windows / macOS / Linux 都有)

**安装:**
```bash
git clone https://github.com/fast118/cc-switch
cd cc-switch
py -m pip install -r requirements.txt
```

**启动:**
```bash
py -m cc_switch
```

**界面:**
- 左侧:已检测的所有 AI 工具(自动)
- 右侧:工具详情 + 操作(设为活跃/复制安装命令/配 API Key)

## 支持的工具

| 工具 | 状态 |
|------|------|
| Claude Code | ✓ 检测 + 设置 |
| OpenAI Codex | ✓ |
| Cursor | ✓ |
| OpenClaw | ✓ |
| Hermes | ✓ |
| Aider | ✓ |

## 核心功能

### 一、检测已装工具

启动自动扫描 PATH,告诉你哪些装了哪些没装:
- ✓ Claude Code 1.0.27 (激活中)
- ✓ OpenAI Codex 0.45.0
- ✗ OpenClaw (未装)
- 点 "复制安装命令" → 粘到终端跑

### 二、设为活跃

选中工具 → 点 "设为活跃" → 按提示设置环境变量(API key)

支持:
- 官方 API key
- 国内中转(api.skillai.top)

### 三、配 API Key(脱敏)

- 输入框是密码框(显示 ●)
- 永久保存提示用 `setx` 命令
- 当下会话用 `os.environ`

## 路线图

| 版本 | 功能 |
|------|------|
| v0.1 | GUI + 检测 + 设活跃 + 配 key |
| v0.2 | 多账号池(团队) |
| v0.3 | 一键试用所有模型对比 |
| v0.4 | Skill 联动(ai-agent-skills)|
| v1.0 | 完整 Tauri 桌面 app |

## 与生态配合

```
CC Switch (桌面 GUI)
  ↓ 选中工具
  ↓ 配 API key
  ↓ 启动
codex-pp (CLI 增强)
  ↓ 加载 skills
ai-agent-skills (skill 库)
  ↓ 撞限速
api.skillai.top (国内中转)
```

**4 个项目互导流,合起来用。**

## 架构

- `cc_switch/__main__.py` - GUI 主入口(tkinter)
- `cc_switch/detector.py` - 工具检测逻辑
- 零外部依赖(只 Python 标准库)

## 不会做的事

- ❌ 不抄 cc-switch
- ❌ 不当"切换器"竞争
- ❌ 不收费
- ❌ 不收集用户数据

## 相关项目

- [codex-pp](https://github.com/fast118/codex-pp) - CLI 增强版
- [ai-agent-skills](https://github.com/fast118/ai-agent-skills) - 11 个 skill
- [free-ai-router](https://github.com/fast118/free-ai-router) - 多 AI 路由器
- [api.skillai.top](https://api.skillai.top) - 国内直连 API

## 许可证

MIT
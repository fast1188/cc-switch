"""
__main__.py - GUI 主入口
=======================
tkinter 实现的桌面 GUI
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

from . import __version__, detector


class CCSwitchApp:
    """主应用窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"CC Switch v{__version__} - 国产化 AI 工具切换器")
        self.root.geometry("900x600")
        self.root.minsize(700, 500)

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        """构建 UI"""
        # 顶部
        header = tk.Frame(self.root, bg="#5865F2", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="CC Switch",
            font=("Microsoft YaHei", 18, "bold"),
            bg="#5865F2",
            fg="white",
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            header,
            text="国产化 AI 编程工具切换器",
            font=("Microsoft YaHei", 11),
            bg="#5865F2",
            fg="white",
        ).pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(
            header,
            text="🔄 刷新",
            font=("Microsoft YaHei", 10),
            command=self._refresh,
        ).pack(side=tk.RIGHT, padx=20, pady=15)

        # 主区域 - 左右分栏
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧:工具列表
        left = tk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            left,
            text="已检测的 AI 工具",
            font=("Microsoft YaHei", 11, "bold"),
        ).pack(anchor=tk.W, pady=(0, 5))

        # Treeview
        columns = ("status", "version", "active", "config")
        self.tree = ttk.Treeview(left, columns=columns, show="tree headings", height=12)
        self.tree.heading("#0", text="工具")
        self.tree.heading("status", text="状态")
        self.tree.heading("version", text="版本")
        self.tree.heading("active", text="激活")
        self.tree.heading("config", text="配置")
        self.tree.column("#0", width=200)
        self.tree.column("status", width=80)
        self.tree.column("version", width=140)
        self.tree.column("active", width=60)
        self.tree.column("config", width=60)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # 右侧:详情 + 操作
        right = tk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(
            right,
            text="工具详情",
            font=("Microsoft YaHei", 11, "bold"),
        ).pack(anchor=tk.W, pady=(0, 5))

        self.detail_text = scrolledtext.ScrolledText(right, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # 操作按钮
        btn_frame = tk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame,
            text="🚀 设为活跃",
            font=("Microsoft YaHei", 10),
            bg="#22C55E",
            fg="white",
            command=self._set_active,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="📋 复制安装命令",
            font=("Microsoft YaHei", 10),
            command=self._copy_install_cmd,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="🔑 配 API Key",
            font=("Microsoft YaHei", 10),
            command=self._set_api_key,
        ).pack(side=tk.LEFT, padx=2)

        # 底部状态栏
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Microsoft YaHei", 9),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _refresh(self):
        """刷新工具列表"""
        # 清空
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 重新检测
        tools = detector.detect_all_tools()
        installed = 0
        for t in tools:
            status = "✓ 已装" if t["installed"] else "✗ 未装"
            active = "✓" if t["active"] else "○"
            config = "✓" if t["has_config"] else "○"
            ver = t["version"] or "-"
            self.tree.insert(
                "", tk.END,
                iid=t["key"],
                text=t["name"],
                values=(status, ver, active, config),
            )
            if t["installed"]:
                installed += 1

        self.status_bar.config(text=f"已检测 {len(tools)} 个工具,装了 {installed} 个")

    def _on_select(self, event):
        """选中时显示详情"""
        sel = self.tree.selection()
        if not sel:
            return
        key = sel[0]
        # 找到对应工具
        for t in detector.detect_all_tools():
            if t["key"] == key:
                self._show_detail(t)
                break

    def _show_detail(self, tool):
        """显示工具详情"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", f"""工具: {tool['name']}
描述: {tool['description']}
状态: {'✓ 已安装' if tool['installed'] else '✗ 未安装'}
版本: {tool['version'] or '-'}
激活: {'✓ 是' if tool['active'] else '○ 否'}
配置目录: {'✓ 存在' if tool['has_config'] else '○ 不存在'}

环境变量: {tool['env_var'] or '-'}
当前值: {self._get_env_value(tool['env_var']) if tool['env_var'] else '-'}

国内直连(api.skillai.top): {tool['fallback_url'] or '-'}

安装命令: {detector.get_install_instructions(tool['key'])}
""")
        self.detail_text.config(state=tk.DISABLED)

    def _get_env_value(self, env_var):
        """获取环境变量值(脱敏)"""
        if not env_var:
            return "-"
        val = __import__("os").getenv(env_var, "")
        if not val:
            return "(未设置)"
        if len(val) < 12:
            return "****"
        return f"{val[:4]}...{val[-4:]}"

    def _set_active(self):
        """设为活跃(导出环境变量)"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个工具")
            return
        key = sel[0]
        for t in detector.detect_all_tools():
            if t["key"] == key:
                env_var = t.get("env_var")
                if not env_var:
                    messagebox.showinfo("提示", f"{t['name']} 没有环境变量配置(可能直接通过配置文件)")
                    return
                messagebox.showinfo(
                    "设为活跃",
                    f"要激活 {t['name']},请设置环境变量:\n\n"
                    f"  {env_var}=<你的API key>\n\n"
                    f"然后重启终端生效。\n\n"
                    f"或者用国内直连:\n"
                    f"  {env_var}=<skillai key>",
                )
                return

    def _copy_install_cmd(self):
        """复制安装命令"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个工具")
            return
        key = sel[0]
        cmd = detector.get_install_instructions(key)
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd)
        messagebox.showinfo("已复制", f"安装命令已复制到剪贴板:\n\n  {cmd}")

    def _set_api_key(self):
        """配置 API Key"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个工具")
            return
        key = sel[0]
        for t in detector.detect_all_tools():
            if t["key"] == key:
                env_var = t.get("env_var")
                if not env_var:
                    messagebox.showinfo("提示", f"{t['name']} 没有 env var 配置")
                    return
                # 弹出输入框
                key_value = self._ask_key(env_var)
                if key_value:
                    import os
                    os.environ[env_var] = key_value
                    messagebox.showinfo("已设置", f"{env_var} 已设置(仅当前会话)\n\n永久保存请用:\n  setx {env_var} \"<key>\"")
                    self._refresh()
                return

    def _ask_key(self, env_var):
        """弹出输入框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"设置 {env_var}")
        dialog.geometry("500x150")
        dialog.transient(self.root)
        dialog.grab_set()

        result = {"value": None}

        tk.Label(
            dialog,
            text=f"输入 {env_var}:",
            font=("Microsoft YaHei", 10),
        ).pack(padx=20, pady=10, anchor=tk.W)

        entry = tk.Entry(dialog, font=("Consolas", 10), show="*")
        entry.pack(fill=tk.X, padx=20, pady=5)
        entry.focus()

        def ok():
            result["value"] = entry.get().strip()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="确定", command=ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT, padx=5)

        dialog.wait_window()
        return result["value"]


def main():
    root = tk.Tk()
    app = CCSwitchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
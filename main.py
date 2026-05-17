#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Py打包工具 v1.0
一键将 Python 源码打包为独立 exe，小白友好
"""

import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import shutil
import threading
import tempfile
import traceback
import re
import ctypes
import glob
import time
import base64

# ============================================================
# 内嵌 Python 图标（base64，已从 python.exe 提取）
# 打包后 exe 移到任何电脑都能用，无需外部图标文件
# ============================================================
DEFAULT_ICON_BASE64 = (
    "AAABAAEAICAQAAAAAADoAgAAFgAAACgAAAAgAAAAQAAAAAEABAAAAAAAgAIAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAACAAACAAAAAgIAAgAAAAIAAgACAgAAAgICAAMDAwAAAAP8AAP8AAAD//wD/"
    "AAAA/wD/AP//AAD///8AAAAAAAAAAAD/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAA//+Auzj/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAP4u7u7uPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAP+7u7v7vwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAD///i7uIiI/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAB3d3d3d/hmiIu7u7u7j/AHd3d3d4hmaIiIu7u7u7/wB3d3d3d3d"
    "mZoiIi7u7u7jwB3d3d3d3d3dniIiLu7u78Ad3d3d/d3doiLu78Ad3d3d3d3d2ZmZmZ4"
    "i7vwB3d3d3d/d3dmZmZmZ4u48Ad3IiIif3d3d2ZmZmf4iP8Ad3d3d3d4iIiIh2Zm//"
    "//AHd3d3d3d3d3d3ZmZvd3AAB3d3d3d3d394h3Zmb3dwAAd3IiIiIiIveId2Zn93cA"
    "AHd3d3d3d3eId3d2f3dwAAd3d3d3d3d4j4iPh3d3AAHd3d3d3d3d3d3d3d3d3AAB3"
    "d3d3d3d3d3d3d3d3dwAAd3d3d3d3d3d3d3d3d3AAHd3d3d3d3d3d3d3d3dwAAd3d3"
    "d3d3d3d3d3d3dwAAd3d3d3d3d3d3d3d3dwAAZmZmZmZmZmZmZmZmZmYAAGZmZmZm"
    "ZmZmZmZmZmZmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//gD///wAf//8AH//+AB///AAf/8AABwAAA"
    "AMAAAAwAAAAMAAAADAAAAAwAAAAMAAAADAAAAAwAAAAMAAAADAAAAAwAAAAPAAA"
    "ADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAfAAA"
    "AP/////////////////////////////////////////////8="
)

# ============================================================
# 配置
# ============================================================
APP_TITLE = "Py打包工具"
APP_VERSION = "1.0"
WINDOW_W = 720
WINDOW_H = 620

# 颜色 - 清爽绿色系，禁止蓝色、紫色
CLR_BG = "#f0f4f0"
CLR_CARD = "#ffffff"
CLR_PRIMARY = "#10b981"
CLR_PRIMARY_HOVER = "#059669"
CLR_PRIMARY_DARK = "#047857"
CLR_TEXT = "#1f2937"
CLR_TEXT_LIGHT = "#6b7280"
CLR_BORDER = "#d1d9d1"
CLR_ERROR = "#ef4444"
CLR_WARN = "#f59e0b"
CLR_SUCCESS = "#10b981"
CLR_LOG_BG = "#1e2a1e"
CLR_LOG_FG = "#d1fae5"
CLR_LOG_WARN = "#fbbf24"
CLR_LOG_ERROR = "#fca5a5"

# 字体
FONT_TITLE = ("Microsoft YaHei UI", 17, "bold")
FONT_LABEL = ("Microsoft YaHei UI", 11)
FONT_ENTRY = ("Microsoft YaHei UI", 11)
FONT_BTN = ("Microsoft YaHei UI", 12, "bold")
FONT_LOG = ("Consolas", 9)
FONT_SMALL = ("Microsoft YaHei UI", 9)

# 危险特殊字符集
BAD_CHARS = set('!@#$%^&*()+=[]{}|\\:;"\'<>,?/`~')

# ============================================================
# 工具函数
# ============================================================

def hide_console_window():
    """隐藏控制台窗口"""
    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        SW_HIDE = 0
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, SW_HIDE)
    except:
        pass


def run_hidden(cmd, timeout=300):
    """静默运行命令，不弹黑窗"""
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def find_python():
    """返回真正的 Python 解释器路径（兼容 PyInstaller 打包后 sys.executable 指向自身的情况）"""
    exe = sys.executable
    # 如果当前是 PyInstaller 打包的 exe（如 PyPackTool.exe），sys.executable 指向的是自身
    # 需要找到真正的 python.exe
    if not exe.lower().endswith("python.exe"):
        # 尝试从 PATH 找 python
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            candidate = os.path.join(path_dir.strip('"'), "python.exe")
            if os.path.exists(candidate):
                return candidate
        # 尝试常见安装路径
        for base in [
            r"C:\Python310",
            r"C:\Python311",
            r"C:\Python312",
            r"C:\Python39",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312",
        ]:
            candidate = os.path.expandvars(os.path.join(base, "python.exe"))
            if os.path.exists(candidate):
                return candidate
        # 尝试 where 命令
        try:
            r = subprocess.run(
                ["where", "python"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                for line in r.stdout.strip().splitlines():
                    line = line.strip()
                    if line.lower().endswith("python.exe") and os.path.exists(line):
                        return line
        except Exception:
            pass
    return exe


def check_python():
    return os.path.exists(find_python())


def check_pip():
    python = find_python()
    if not python:
        return False
    r = run_hidden([python, "-m", "pip", "--version"])
    return r and r.returncode == 0


def check_pyinstaller():
    python = find_python()
    if not python:
        return False
    r = run_hidden([python, "-m", "PyInstaller", "--version"])
    return r and r.returncode == 0


def extract_python_icon():
    """从内嵌 base64 解码图标到临时文件（exe 打包后仍可用）"""
    ico_path = os.path.join(tempfile.gettempdir(), "pypacktool_python_icon.ico")
    # 缓存命中则直接返回
    if os.path.exists(ico_path) and os.path.getsize(ico_path) > 0:
        return ico_path
    try:
        raw = base64.b64decode(DEFAULT_ICON_BASE64)
        with open(ico_path, "wb") as f:
            f.write(raw)
        if os.path.exists(ico_path) and os.path.getsize(ico_path) > 0:
            return ico_path
    except Exception:
        pass
    return ""


def get_disk_freeMB(path):
    try:
        return shutil.disk_usage(path).free / (1024 * 1024)
    except:
        return float("inf")


# ============================================================
# 主应用
# ============================================================

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget, bg="#2d3436", bd=1, relief="solid")
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, font=FONT_SMALL,
                         fg="#dfe6e9", bg="#2d3436", padx=8, pady=4)
        label.pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class PyPackTool:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE}  v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.resizable(False, False)
        self.root.configure(bg=CLR_BG)

        # 图标
        try:
            ico = extract_python_icon()
            if ico:
                self.root.iconbitmap(ico)
        except:
            pass

        self._center_window()

        # 变量
        self.src_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.building = False
        self.default_icon_path = ""

        # 构建界面
        self._build_ui()

        # 延迟检测环境
        self.root.after(300, self._check_env)

    def _center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - WINDOW_W) // 2
        y = (sh - WINDOW_H) // 2
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    # ----------------------------------------------------------------
    # UI 构建
    # ----------------------------------------------------------------
    def _build_ui(self):
        # === 顶部标题区 ===
        hdr = tk.Frame(self.root, bg=CLR_BG)
        hdr.pack(fill="x", padx=28, pady=(18, 0))

        tk.Label(hdr, text="📦  Py打包工具",
                 font=FONT_TITLE, fg=CLR_TEXT, bg=CLR_BG).pack(side="left")

        sub = tk.Label(hdr, text="一键将 Python 源码打包为 exe，小白也能用",
                       font=FONT_SMALL, fg=CLR_TEXT_LIGHT, bg=CLR_BG)
        sub.pack(side="left", padx=12, pady=14)

        # 版本标签
        ver_lbl = tk.Label(hdr, text=f"v{APP_VERSION}", font=FONT_SMALL,
                          fg=CLR_TEXT_LIGHT, bg=CLR_BG)
        ver_lbl.pack(side="right", padx=4)

        # 分隔线
        tk.Frame(self.root, height=1, bg=CLR_BORDER).pack(fill="x", padx=28, pady=(12, 0))

        # === 主内容区 ===
        body = tk.Frame(self.root, bg=CLR_BG)
        body.pack(fill="both", expand=True, padx=28, pady=12)

        # --- 源码行 ---
        self._row(body, "📄  选择 Python 源码（.py 文件）",
                  self.src_var, "浏览...", self._pick_src, 0)

        # --- 输出路径行 ---
        self._row(body, "📁  输出路径（默认与源码同一目录）",
                  self.out_var, "修改", self._pick_out, 1)

        # --- 图标行 ---
        icon_frm = tk.Frame(body, bg=CLR_BG)
        icon_frm.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        body.grid_columnconfigure(0, weight=1)

        tk.Label(icon_frm, text="🎨  程序图标",
                 font=FONT_LABEL, fg=CLR_TEXT, bg=CLR_BG).pack(anchor="w")

        icon_row = tk.Frame(icon_frm, bg=CLR_BG)
        icon_row.pack(fill="x", pady=(5, 0))

        ico_entry = tk.Entry(icon_row, textvariable=self.icon_var,
                             font=FONT_ENTRY, fg=CLR_TEXT, bg=CLR_CARD,
                             relief="solid", bd=1, insertbackground=CLR_TEXT)
        ico_entry.pack(side="left", fill="x", expand=True, ipady=6)

        self._btn(icon_row, "选择图标", self._pick_icon, 80)

        # 默认图标链接
        def_link = tk.Frame(icon_frm, bg=CLR_BG)
        def_link.pack(anchor="w", pady=(5, 0))

        def_lbl = tk.Label(def_link,
                            text="🐍  使用默认 Python 图标",
                            font=FONT_SMALL, fg=CLR_PRIMARY, bg=CLR_BG,
                            cursor="hand2")
        def_lbl.pack(side="left")
        def_lbl.bind("<Button-1>", lambda e: self._use_def_icon())
        ToolTip(def_lbl, "点击使用 Python 官方图标")

        # --- 分隔 ---
        tk.Frame(body, height=1, bg=CLR_BORDER).grid(
            row=3, column=0, sticky="ew", pady=16)

        # --- 开始打包按钮 ---
        self.build_btn = tk.Button(
            body, text="🚀  开始打包",
            font=FONT_BTN, fg="#ffffff", bg=CLR_PRIMARY,
            activebackground=CLR_PRIMARY_HOVER,
            activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            command=self._do_build
        )
        self.build_btn.grid(row=4, column=0, sticky="ew", ipady=10)
        self.build_btn.bind("<Enter>", lambda e: self.build_btn.config(bg=CLR_PRIMARY_HOVER))
        self.build_btn.bind("<Leave>", lambda e: self.build_btn.config(bg=CLR_PRIMARY))

        # --- 日志区 ---
        log_hdr = tk.Frame(body, bg=CLR_BG)
        log_hdr.grid(row=5, column=0, sticky="ew", pady=(16, 3))

        tk.Label(log_hdr, text="📋  打包日志",
                 font=FONT_SMALL, fg=CLR_TEXT_LIGHT, bg=CLR_BG).pack(side="left")

        # 环境状态标签
        self.env_lbl = tk.Label(log_hdr, text="⏳ 检测环境...",
                                 font=FONT_SMALL, fg=CLR_TEXT_LIGHT, bg=CLR_BG)
        self.env_lbl.pack(side="right")

        log_frm = tk.Frame(body, bg=CLR_LOG_BG, bd=1,
                           relief="solid", highlightbackground=CLR_BORDER)
        log_frm.grid(row=6, column=0, sticky="nsew", pady=(0, 4))
        body.grid_rowconfigure(6, weight=1)

        # 日志文本框
        self.log_tk = tk.Text(log_frm, font=FONT_LOG, fg=CLR_LOG_FG,
                              bg=CLR_LOG_BG, relief="flat", wrap="word",
                              state="disabled", padx=12, pady=8,
                              insertbackground=CLR_LOG_FG, spacing1=2)
        self.log_tk.pack(fill="both", expand=True)

        # 标签配置
        self.log_tk.tag_configure("err", foreground=CLR_LOG_ERROR)
        self.log_tk.tag_configure("ok", foreground=CLR_LOG_FG)
        self.log_tk.tag_configure("ok_b", foreground=CLR_SUCCESS)
        self.log_tk.tag_configure("warn", foreground=CLR_LOG_WARN)
        self.log_tk.tag_configure("info", foreground="#93c5fd")

        # 底部状态栏
        foot = tk.Frame(self.root, bg=CLR_CARD, height=32, bd=0, highlightthickness=0)
        foot.pack(fill="x", side="bottom")
        self.status_lbl = tk.Label(foot, text="就绪",
                                    font=FONT_SMALL, fg=CLR_TEXT_LIGHT, bg=CLR_CARD)
        self.status_lbl.pack(side="left", padx=12)

        # 初始日志
        self._log("=" * 36, tag="")
        self._log("📦 Py打包工具已就绪", tag="ok")
        self._log("正在检测环境，请稍候...", tag="info")
        self._log("=" * 36, tag="")

    def _row(self, parent, label, var, btn_text, btn_cmd, row):
        frm = tk.Frame(parent, bg=CLR_BG)
        frm.grid(row=row, column=0, sticky="ew", pady=5)
        parent.grid_columnconfigure(0, weight=1)

        tk.Label(frm, text=label, font=FONT_LABEL,
                 fg=CLR_TEXT, bg=CLR_BG).pack(anchor="w")

        ent_frm = tk.Frame(frm, bg=CLR_BG)
        ent_frm.pack(fill="x", pady=(5, 0))

        ent = tk.Entry(ent_frm, textvariable=var, font=FONT_ENTRY,
                       fg=CLR_TEXT, bg=CLR_CARD, relief="solid", bd=1,
                       insertbackground=CLR_TEXT)
        ent.pack(side="left", fill="x", expand=True, ipady=6)
        self._btn(ent_frm, btn_text, btn_cmd, 80)

    def _btn(self, parent, text, cmd, w=None):
        b = tk.Button(parent, text=text, font=("Microsoft YaHei UI", 10),
                      fg="#ffffff", bg=CLR_PRIMARY,
                      activebackground=CLR_PRIMARY_HOVER,
                      activeforeground="#ffffff",
                      relief="flat", cursor="hand2", command=cmd)
        b.pack(side="right", padx=(8, 0), ipady=4)
        b.bind("<Enter>", lambda e: b.config(bg=CLR_PRIMARY_HOVER))
        b.bind("<Leave>", lambda e: b.config(bg=CLR_PRIMARY))
        return b

    # ----------------------------------------------------------------
    # 环境检测
    # ----------------------------------------------------------------
    def _check_env(self):
        py_ok = check_python()
        pip_ok = check_pip()
        pi_ok = check_pyinstaller()

        py_path = find_python()
        if py_ok:
            self._log("✅ Python 环境正常", tag="ok_b")
            py_ver = sys.version_info[:3]
            self._log(f"   Python {py_ver[0]}.{py_ver[1]}.{py_ver[2]}", tag="info")
            self._log(f"   路径：{py_path}", tag="info")
            self.env_lbl.config(text="✅ 环境就绪", fg=CLR_SUCCESS)
        else:
            self._log("❌ 未检测到 Python，请先安装 Python！", tag="err")
            self.env_lbl.config(text="❌ Python 缺失", fg=CLR_ERROR)
            self.status_lbl.config(text="错误：未安装 Python")

        if pip_ok:
            self._log("✅ pip 包管理器正常", tag="ok_b")
        else:
            self._log("⚠️ pip 未检测到", tag="warn")

        if pi_ok:
            self._log("✅ PyInstaller 已安装，可以直接打包", tag="ok_b")
            self.env_lbl.config(text="✅ 环境就绪 | PyInstaller OK", fg=CLR_SUCCESS)
            self.build_btn.config(state="normal")
        else:
            self._log("⚠️ PyInstaller 未安装，将自动安装...", tag="warn")
            self.build_btn.config(state="disabled")
            self.root.after(200, self._install_pi)

        # 提取默认图标
        self.default_icon_path = extract_python_icon()
        if self.default_icon_path:
            self.icon_var.set(self.default_icon_path)
            self._log("🐍 Python 官方图标已加载", tag="info")

    def _install_pi(self):
        python = find_python()
        if not python:
            self._log("❌ 安装失败：找不到 Python", tag="err")
            self.build_btn.config(state="disabled")
            return

        self._log("正在安装 PyInstaller，请稍候（约 1 分钟）...", tag="warn")
        self.status_lbl.config(text="正在安装 PyInstaller...")

        def install_thread():
            r = run_hidden(
                [python, "-m", "pip", "install", "pyinstaller",
                 "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],
                timeout=180
            )
            self.root.after(0, lambda: self._install_done(r))

        t = threading.Thread(target=install_thread, daemon=True)
        t.start()

    def _install_done(self, result):
        if result and result.returncode == 0:
            self._log("✅ PyInstaller 安装成功！", tag="ok_b")
            self._log("现在可以开始打包了 🎉", tag="ok_b")
            self.env_lbl.config(text="✅ 环境就绪 | PyInstaller OK", fg=CLR_SUCCESS)
            self.status_lbl.config(text="就绪")
            self.build_btn.config(state="normal", bg=CLR_PRIMARY)
        else:
            self._log("❌ PyInstaller 安装失败！", tag="err")
            self._log("请检查网络后手动运行：pip install pyinstaller", tag="warn")
            self.env_lbl.config(text="❌ PyInstaller 安装失败", fg=CLR_ERROR)
            self.status_lbl.config(text="PyInstaller 安装失败")

    # ----------------------------------------------------------------
    # 文件选择
    # ----------------------------------------------------------------
    def _pick_src(self):
        path = filedialog.askopenfilename(
            title="选择 Python 源码文件",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        if path:
            self.src_var.set(path)
            # 自动填充输出目录
            self.out_var.set(os.path.dirname(path))
            self._log(f"已选择：{os.path.basename(path)}", tag="info")
            self.status_lbl.config(text=f"源码：{os.path.basename(path)}")

    def _pick_out(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.out_var.set(path)
            self._log(f"输出目录已修改", tag="info")

    def _pick_icon(self):
        path = filedialog.askopenfilename(
            title="选择程序图标（.ico 文件）",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if path:
            self.icon_var.set(path)
            self._log(f"已选择图标：{os.path.basename(path)}", tag="info")

    def _use_def_icon(self):
        if self.default_icon_path and os.path.exists(self.default_icon_path):
            self.icon_var.set(self.default_icon_path)
            self._log("已切换为 Python 官方图标 🐍", tag="info")
        else:
            self._log("⚠️ 默认图标不可用", tag="warn")

    # ----------------------------------------------------------------
    # 打包
    # ----------------------------------------------------------------
    def _do_build(self):
        if self.building:
            return

        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        ico = self.icon_var.get().strip()

        # ---- 验证源码 ----
        if not src:
            self._log("❌ 请先选择 Python 源码文件！", tag="err")
            return

        if not os.path.exists(src):
            self._log("❌ 打包失败！原因：源码文件不存在、被删除或移动了", tag="err")
            return

        # ---- 基础语法检查 ----
        py_ver = sys.version_info
        try:
            with open(src, "r", encoding="utf-8") as f:
                code = f.read()
        except UnicodeDecodeError:
            try:
                with open(src, "r", encoding="gbk") as f:
                    code = f.read()
            except:
                self._log("❌ 打包失败！原因：源码文件编码有问题，请保存为 UTF-8 格式", tag="err")
                return

        # ---- 文件名特殊字符检查 ----
        basename = os.path.basename(src)
        for ch in basename:
            if ch in BAD_CHARS:
                self._log(f"❌ 打包失败！原因：文件名包含特殊符号（{ch}），请重命名后再试", tag="err")
                return

        # ---- 空格路径警告 ----
        abs_src = os.path.abspath(src)
        if ' ' in abs_src:
            self._log("⚠️ 路径包含空格，可能导致打包失败！", tag="warn")

        # ---- 被占用检查 ----
        try:
            with open(src, "r", encoding="utf-8") as f:
                f.read(1)
        except PermissionError:
            self._log("❌ 打包失败！原因：源码被其他软件占用、打开或编辑中，请先关闭", tag="err")
            return

        # ---- 语法预检查 ----
        try:
            import py_compile
            py_compile.compile(src, doraise=True)
        except py_compile.PyCompileError as e:
            err_str = str(e)
            self._log("❌ 打包失败！原因：源码里有语法错误，请先修复代码中的问题", tag="err")
            return
        except:
            pass

        # ---- 默认输出目录 ----
        if not out:
            out = os.path.dirname(src)
            self.out_var.set(out)

        # ---- 磁盘空间 ----
        free_mb = get_disk_freeMB(out)
        if free_mb < 100:
            self._log("❌ 打包失败！原因：磁盘空间不足，至少需要 100MB 剩余空间", tag="err")
            return

        # ---- PyInstaller 检查 ----
        if not check_pyinstaller():
            self._log("❌ PyInstaller 未安装，请等待自动安装完成后再试", tag="err")
            return

        # ---- 开始打包 ----
        self.building = True
        self.build_btn.config(text="⏳  打包中，请勿关闭...", bg="#9ca3af",
                             state="disabled", relief="flat")
        self.status_lbl.config(text="正在打包...")
        self._log("=" * 36, tag="")
        self._log("🚀 开始打包...", tag="info")

        t = threading.Thread(target=self._build_worker,
                             args=(src, out, ico), daemon=True)
        t.start()

    def _build_worker(self, src, out, ico):
        """打包工作线程（后台运行）"""
        python = find_python()
        src_name = os.path.splitext(os.path.basename(src))[0]
        src_dir = os.path.dirname(os.path.abspath(src))

        # 临时工作目录
        tmp_work = os.path.join(tempfile.gettempdir(),
                                f"pypack_build_{src_name}_{int(time.time())}")
        os.makedirs(tmp_work, exist_ok=True)

        try:
            # ---- 构建命令 ----
            cmd = [
                python, "-m", "PyInstaller",
                "--noconfirm",
                "--onefile",
                "--noconsole",
                "--distpath", out,
                "--workpath", tmp_work,
                "--specpath", tmp_work,
                "--name", src_name,
            ]

            # 图标
            ico_real = ico.strip()
            if ico_real and os.path.exists(ico_real):
                cmd += ["--icon", ico_real]
                self.root.after(0, lambda: self._log(
                    f"🎨 使用图标：{os.path.basename(ico_real)}", tag="info"))

            cmd.append(src)

            self.root.after(0, lambda: self._log(
                f"📄 源码：{os.path.basename(src)}", tag="info"))
            self.root.after(0, lambda: self._log(
                f"📁 输出：{out}", tag="info"))
            self.root.after(0, lambda: self._log(
                "正在编译，这可能需要 1-5 分钟...", tag="warn"))
            self.root.after(0, lambda: self._log(
                f"⚙️ 命令：{' '.join(cmd[:6])} ...", tag="info"))

            # ---- 执行 PyInstaller ----
            r = run_hidden(cmd, timeout=600)

            if r is None:
                self._on_build_fail(
                    "打包超时，可能是代码太复杂或依赖太多，请减少依赖后重试", tmp_work)
                return

            # 记录原始输出（调试用）
            raw_out = (r.stdout or "") + (r.stderr or "")
            self.root.after(0, lambda: self._log(
                f"📋 返回码：{r.returncode}", tag="info"))

            if r.returncode != 0:
                err = self._parse_error(raw_out)
                # 同时输出最后 500 字原始日志
                tail = raw_out[-500:] if len(raw_out) > 500 else raw_out
                self.root.after(0, lambda: self._log(
                    f"📝 原始日志末尾：\n{tail}", tag="err"))
                self._on_build_fail(err, tmp_work)
                return

            # ---- 检查 exe 是否生成 ----
            exe_path = os.path.join(out, f"{src_name}.exe")
            self.root.after(0, lambda: self._log(
                f"🔍 检查路径：{exe_path}", tag="info"))
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                self.root.after(0, lambda: self._log(
                    "=" * 36, tag=""))
                self.root.after(0, lambda: self._log(
                    "🎉 打包成功！", tag="ok_b"))
                self.root.after(0, lambda: self._log(
                    f"📦 生成文件：{exe_path}", tag="ok"))
                self.root.after(0, lambda: self._log(
                    f"📊 文件大小：{size_mb:.1f} MB", tag="ok"))
                self.root.after(0, lambda: self._log(
                    "🧹 正在清理临时文件...", tag="info"))
                self.root.after(0, lambda: self.status_lbl.config(
                    text=f"✅ 打包完成 | {size_mb:.1f} MB"))
            else:
                # 列出输出目录内容帮助排查
                try:
                    files = os.listdir(out) if os.path.isdir(out) else []
                    files_str = ", ".join(files[:10]) if files else "(空目录或目录不存在)"
                except Exception as e:
                    files_str = f"(无法读取目录: {e})"
                self.root.after(0, lambda: self._log(
                    f"📂 输出目录内容：{files_str}", tag="err"))
                self._on_build_fail("未找到生成的 exe 文件", tmp_work)
                return

            # ---- 清理 ----
            self._cleanup(tmp_work, out, src_name)

        except Exception as e:
            err_msg = str(e)
            # 翻译常见错误
            if "PermissionError" in err_msg or "拒绝访问" in err_msg:
                err_msg = "没有管理员权限，请右键以管理员身份运行本工具"
            elif "No module named" in err_msg or "ImportError" in err_msg:
                err_msg = "源码导入了未安装的库"
            self._on_build_fail(err_msg, tmp_work)

    def _on_build_fail(self, reason, tmp_work):
        self.root.after(0, lambda: self._log(
            "=" * 36, tag=""))
        self.root.after(0, lambda: self._log(
            f"❌ 打包失败！原因：{reason}", tag="err"))
        self.root.after(0, lambda: self.status_lbl.config(
            text=f"打包失败：{reason[:30]}"))
        self._cleanup(tmp_work, "", "")
        self.root.after(0, self._reset_build_btn)

    def _reset_build_btn(self):
        self.building = False
        self.build_btn.config(text="🚀  开始打包", bg=CLR_PRIMARY,
                             state="normal", relief="flat")

    def _parse_error(self, stderr_stdout):
        """分析 PyInstaller 错误输出，返回人类可读的原因"""
        txt = stderr_stdout
        # 中文路径
        try:
            txt.encode("ascii")
        except UnicodeEncodeError:
            # 有非ASCII字符（通常是中文路径）
            if any('\u4e00' <= c <= '\u9fff' for c in txt):
                return ("源码文件路径或名称包含中文，"
                        "建议将源码移到不含中文的路径下重试")
        # 找不到模块
        m = re.search(r"ModuleNotFoundError.*?['\"]([^'\"]+)['\"]", txt)
        if m:
            return f"源码导入了未安装的库（{m.group(1)}），请先 pip install 该库"
        # 语法错误
        if "SyntaxError" in txt or "IndentationError" in txt:
            return "源码里有语法错误，请先修复代码"
        # 相对路径
        if "FileNotFoundError" in txt or "No such file" in txt:
            return "源码中使用了相对路径找不到资源文件，请检查代码中的文件路径"
        # 权限
        if "PermissionError" in txt or "拒绝访问" in txt:
            return "没有管理员权限，请右键以管理员身份运行本工具"
        # 磁盘满
        if "No space left" in txt or "disk" in txt.lower() and "full" in txt.lower():
            return "磁盘空间不足，请清理磁盘后重试"
        # 其他
        return ("打包过程出错，可能是依赖库版本不兼容，"
                "或源码中有不支持的特性")

    def _cleanup(self, work_dir, out_dir, exe_name):
        """清理临时文件，只保留源码和 exe"""
        try:
            # 清理工作目录
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)

            # 清理 build 目录（如果还在源码旁边）
            if out_dir and exe_name:
                build_dir = os.path.join(out_dir, "build")
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir, ignore_errors=True)

                # 清理 .spec 文件
                spec_file = os.path.join(out_dir, f"{exe_name}.spec")
                if os.path.exists(spec_file):
                    os.remove(spec_file)

                # 清理 __pycache__
                for root_dir, dirs, _ in os.walk(out_dir):
                    for d in dirs:
                        if d == "__pycache__":
                            try:
                                shutil.rmtree(
                                    os.path.join(root_dir, d),
                                    ignore_errors=True
                                )
                            except:
                                pass
        except Exception:
            pass
        finally:
            self.root.after(0, lambda: self._log(
                "✅ 临时文件已清理完毕", tag="ok_b"))
            self.root.after(0, self._reset_build_btn)

    # ----------------------------------------------------------------
    # 日志
    # ----------------------------------------------------------------
    def _log(self, msg, tag=""):
        self.log_tk.config(state="normal")
        if tag:
            self.log_tk.insert("end", msg + "\n", tag)
        else:
            self.log_tk.insert("end", msg + "\n")
        self.log_tk.see("end")
        self.log_tk.config(state="disabled")


# ============================================================
# 入口
# ============================================================
def main():
    # 打包后隐藏控制台
    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, 0)  # SW_HIDE = 0
    except Exception:
        pass
    root = tk.Tk()
    app = PyPackTool(root)
    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # Windows Mutex：防止打包后多实例（bootloader 重入导致多窗口）
    _MUTEX_NAME = "Global\\PyPackTool_SingleInstance_Mutex_v1"
    _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    _err = ctypes.windll.kernel32.GetLastError()
    if _err == 183:  # ERROR_ALREADY_EXISTS
        # 已有实例在运行，直接退出
        sys.exit(0)

    main()

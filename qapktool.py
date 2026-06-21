import os
import sys
import json
import subprocess
import threading
import ctypes
from ctypes import c_void_p, WINFUNCTYPE, windll
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, "config.json")


def _find_apktool_jar():
    for f in os.listdir(APP_DIR):
        if f.endswith(".jar"):
            return os.path.join(APP_DIR, f)
    return ""


DEFAULT_APKTOOL = _find_apktool_jar()


def _find_java():
    bundled = os.path.join(APP_DIR, "jre", "bin", "java.exe")
    if os.path.isfile(bundled):
        return bundled
    return "java"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"apktool_path": DEFAULT_APKTOOL, "output_dir": ""}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class ApktoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QApkTool - APK 反编译工具")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        icon_path = os.path.join(APP_DIR, "icon.png")
        if os.path.isfile(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)

        self.config = load_config()
        self.process = None

        self._build_ui()
        self._enable_drag_drop()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"), background="#f0f0f0")
        style.configure("Sub.TLabel", font=("Microsoft YaHei UI", 9), background="#f0f0f0")
        style.configure("Action.TButton", font=("Microsoft YaHei UI", 10), padding=6)
        style.configure("TNotebook.Tab", font=("Microsoft YaHei UI", 10), padding=[12, 4])

        # Header
        ttk.Label(self.root, text="QApkTool", style="Title.TLabel").pack(pady=(12, 0))
        ttk.Label(self.root, text="APK 反编译 / 回编译 一键工具（支持拖拽文件）", style="Sub.TLabel").pack(pady=(0, 8))

        # Apktool path row
        path_frame = ttk.LabelFrame(self.root, text="ApkTool 路径", padding=8)
        path_frame.pack(fill="x", padx=12, pady=4)

        self.apktool_var = tk.StringVar(value=self.config["apktool_path"])
        ttk.Entry(path_frame, textvariable=self.apktool_var, font=("Consolas", 9)).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="浏览", command=self._pick_apktool).pack(side="left", padx=(6, 0))

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=8)

        self._build_decompile_tab()
        self._build_recompile_tab()

        # Log area
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=6)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.log_text = tk.Text(log_frame, height=10, font=("Consolas", 9), bg="#1e1e1e", fg="#cccccc",
                                insertbackground="white", state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="就绪 | 可拖拽 APK 或文件夹到窗口")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w",
                  font=("Microsoft YaHei UI", 8)).pack(fill="x", side="bottom")

    def _build_decompile_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  反编译 (d)  ")

        # Input APK
        ttk.Label(tab, text="选择 APK 文件:（可拖拽）").grid(row=0, column=0, sticky="w", pady=4)
        self.decomp_input = tk.StringVar()
        ttk.Entry(tab, textvariable=self.decomp_input, width=50).grid(row=1, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(tab, text="浏览...", command=lambda: self._pick_file(self.decomp_input, [("APK files", "*.apk"), ("All files", "*.*")])).grid(row=1, column=1)

        # Output dir
        ttk.Label(tab, text="输出目录 (可选，留空则自动生成):").grid(row=2, column=0, sticky="w", pady=(10, 4))
        self.decomp_output = tk.StringVar()
        ttk.Entry(tab, textvariable=self.decomp_output, width=50).grid(row=3, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(tab, text="浏览...", command=lambda: self._pick_dir(self.decomp_output)).grid(row=3, column=1)

        # Options
        opt_frame = ttk.Frame(tab)
        opt_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 4))
        self.decomp_force = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="覆盖已有 (-f)", variable=self.decomp_force).pack(side="left")
        self.decomp_no_src = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="不反编译源码 (--no-src)", variable=self.decomp_no_src).pack(side="left", padx=(12, 0))
        self.decomp_no_res = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="不反编译资源 (--no-res)", variable=self.decomp_no_res).pack(side="left", padx=(12, 0))

        # Run button
        ttk.Button(tab, text="开始反编译", style="Action.TButton", command=self._run_decompile).grid(row=5, column=0, columnspan=2, pady=(14, 0))
        tab.columnconfigure(0, weight=1)

    def _build_recompile_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  回编译 (b)  ")

        # Input folder
        ttk.Label(tab, text="选择反编译后的文件夹:（可拖拽）").grid(row=0, column=0, sticky="w", pady=4)
        self.recomp_input = tk.StringVar()
        ttk.Entry(tab, textvariable=self.recomp_input, width=50).grid(row=1, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(tab, text="浏览...", command=lambda: self._pick_dir(self.recomp_input)).grid(row=1, column=1)

        # Output APK
        ttk.Label(tab, text="输出 APK 路径 (可选):").grid(row=2, column=0, sticky="w", pady=(10, 4))
        self.recomp_output = tk.StringVar()
        ttk.Entry(tab, textvariable=self.recomp_output, width=50).grid(row=3, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(tab, text="浏览...", command=lambda: self._pick_save(self.recomp_output)).grid(row=3, column=1)

        # Run button
        ttk.Button(tab, text="开始回编译", style="Action.TButton", command=self._run_recompile).grid(row=4, column=0, columnspan=2, pady=(14, 0))
        tab.columnconfigure(0, weight=1)

    # --- Drag & Drop (Windows API) ---
    def _enable_drag_drop(self):
        hwnd = int(self.root.wm_frame(), 16)
        windll.user32.DragAcceptFiles(hwnd, True)

        WM_DROPFILES = 0x233
        GWL_WNDPROC = -4
        LRESULT = c_void_p
        WPARAM = c_void_p
        LPARAM = c_void_p
        WNDPROC = WINFUNCTYPE(LRESULT, c_void_p, ctypes.c_uint, WPARAM, LPARAM)

        def _wndproc(hwnd, msg, wparam, lparam):
            if msg == WM_DROPFILES:
                hd = wparam
                count = windll.shell32.DragQueryFileW(hd, 0xFFFFFFFF, None, 0)
                files = []
                for i in range(count):
                    size = windll.shell32.DragQueryFileW(hd, i, None, 0) + 1
                    buf = ctypes.create_unicode_buffer(size)
                    windll.shell32.DragQueryFileW(hd, i, buf, size)
                    files.append(buf.value)
                windll.shell32.DragFinish(hd)
                self._handle_drop(files)
                return 0
            return windll.user32.CallWindowProcW(old_wndproc, hwnd, msg, wparam, lparam)

        self._new_wndproc = WNDPROC(_wndproc)
        old_wndproc = windll.user32.GetWindowLongPtrW(hwnd, GWL_WNDPROC)
        windll.user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, self._new_wndproc)

    def _handle_drop(self, files):
        if not files:
            return
        path = files[0]
        if os.path.isfile(path):
            if path.lower().endswith(".apk"):
                self.decomp_input.set(path)
                self.notebook.select(0)
                self._set_status(f"已拖入 APK: {os.path.basename(path)}")
            elif path.lower().endswith(".jar"):
                self.apktool_var.set(path)
                self._set_status(f"已拖入 JAR: {os.path.basename(path)}")
            else:
                self.decomp_input.set(path)
                self.notebook.select(0)
                self._set_status(f"已拖入文件: {os.path.basename(path)}")
        elif os.path.isdir(path):
            self.recomp_input.set(path)
            self.notebook.select(1)
            self._set_status(f"已拖入文件夹: {os.path.basename(path)}")

    # --- File pickers ---
    def _pick_apktool(self):
        path = filedialog.askopenfilename(title="选择 apktool jar", filetypes=[("JAR files", "*.jar")])
        if path:
            self.apktool_var.set(path)

    def _pick_file(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def _pick_dir(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _pick_save(self, var):
        path = filedialog.asksaveasfilename(defaultextension=".apk", filetypes=[("APK files", "*.apk")])
        if path:
            var.set(path)

    # --- Logging ---
    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, msg):
        self.status_var.set(msg)

    # --- Run apktool ---
    def _run_cmd(self, cmd, label):
        self.config["apktool_path"] = self.apktool_var.get()
        save_config(self.config)

        self._log(f">>> {' '.join(cmd)}")
        self._set_status(f"{label} 运行中...")

        def worker():
            try:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                text=True, encoding="utf-8", errors="replace")
                for line in self.process.stdout:
                    self.root.after(0, self._log, line.rstrip("\n"))
                self.process.wait()
                if self.process.returncode == 0:
                    self.root.after(0, self._set_status, f"{label} 完成")
                    self.root.after(0, self._log, f"--- {label} 成功 ---\n")
                    self.root.after(0, lambda: messagebox.showinfo("完成", f"{label}成功!"))
                else:
                    self.root.after(0, self._set_status, f"{label} 失败 (code {self.process.returncode})")
                    self.root.after(0, self._log, f"--- {label} 失败 (exit {self.process.returncode}) ---\n")
            except FileNotFoundError:
                self.root.after(0, self._set_status, "错误: 找不到 Java 或 apktool")
                self.root.after(0, self._log, "错误: 请确认 Java 已安装且 apktool jar 路径正确")
            except Exception as e:
                self.root.after(0, self._set_status, f"错误: {e}")
                self.root.after(0, self._log, f"错误: {e}")
            finally:
                self.process = None

        threading.Thread(target=worker, daemon=True).start()

    def _run_decompile(self):
        apk_path = self.decomp_input.get().strip()
        if not apk_path or not os.path.isfile(apk_path):
            messagebox.showwarning("提示", "请选择有效的 APK 文件")
            return

        jar = self.apktool_var.get().strip()
        cmd = [_find_java(), "-jar", jar, "d", apk_path]

        out = self.decomp_output.get().strip()
        if out:
            cmd += ["-o", out]
        if self.decomp_force.get():
            cmd.append("-f")
        if self.decomp_no_src.get():
            cmd.append("--no-src")
        if self.decomp_no_res.get():
            cmd.append("--no-res")

        self._run_cmd(cmd, "反编译")

    def _run_recompile(self):
        folder = self.recomp_input.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("提示", "请选择反编译后的文件夹")
            return

        jar = self.apktool_var.get().strip()
        cmd = [_find_java(), "-jar", jar, "b", folder]

        out = self.recomp_output.get().strip()
        if out:
            cmd += ["-o", out]

        self._run_cmd(cmd, "回编译")


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("qapktool.app")
    root = tk.Tk()
    app = ApktoolApp(root)
    root.mainloop()

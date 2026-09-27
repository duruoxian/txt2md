"""TXT → MD 便携同步工具：入口、托盘、监听、转换调度。"""
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

import config as cfg_mod
import converter
import icons
import theme
import ui_home
import ui_settings
from tray import Tray
from watcher import Watcher


def _norm(p: str) -> str:
    return os.path.normcase(os.path.abspath(p))


class App:
    def __init__(self):
        self.cfg = cfg_mod.load()
        ctk.set_appearance_mode(self.cfg.get("theme", "System"))
        ctk.set_default_color_theme("green")

        self.system_prompt = converter.load_system_prompt(cfg_mod.base_dir())
        self.event_q = queue.Queue()
        self.manual_q = queue.Queue()
        self.stopping = False
        self.auto = True
        self.last_hash = {}

        self.root = ctk.CTk()
        self.root.title("TXT → MD")
        self._center(520, 540)
        self.root.minsize(440, 460)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self._app_img = ctk.CTkImage(
            light_image=icons.app_icon(128), dark_image=icons.app_icon(128), size=(30, 30)
        )

        self.watcher = Watcher(lambda kind, path: self.event_q.put((kind, path)))
        self.watcher.rebuild(self.cfg.get("watch_list", []))

        self.tray = Tray(self, icons.app_icon(64))
        self.tray.run()

        self._build_ui()
        self._start_manager()

    # ---------- UI ----------
    def _center(self, w: int, h: int):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 3)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.root.configure(fg_color=theme.color("bg"))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(self.root, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text="", image=self._app_img).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkLabel(
            bar, text="TXT → MD", text_color=theme.color("text"),
            font=theme.font(18, "bold"),
        ).grid(row=0, column=1, sticky="w")

        self.theme_btn = ctk.CTkButton(
            bar, text="◐", width=36, height=36, corner_radius=18,
            fg_color="transparent", hover_color=theme.color("hover"),
            text_color=theme.color("text"), font=theme.font(16),
            command=self.toggle_theme,
        )
        self.theme_btn.grid(row=0, column=2, padx=4)
        self.nav_btn = ctk.CTkButton(
            bar, text="⚙", width=36, height=36, corner_radius=18,
            fg_color="transparent", hover_color=theme.color("hover"),
            text_color=theme.color("text"), font=theme.font(16),
            command=self.toggle_view,
        )
        self.nav_btn.grid(row=0, column=3)

        self.content = ctk.CTkFrame(self.root, fg_color=theme.color("bg"))
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.home = ui_home.HomeFrame(self.content, self)
        self.home.grid(row=0, column=0, sticky="nsew")
        self.settings = None
        self.current_view = "home"
        self.nav_btn.configure(text="⚙")
        self.home.tkraise()

    def _rebuild_ui(self):
        for child in self.root.winfo_children():
            child.destroy()
        self._build_ui()

    # ---------- 主题 ----------
    def toggle_theme(self):
        nxt = "Light" if theme.is_dark() else "Dark"
        self.apply_theme(nxt)

    def apply_theme(self, mode: str):
        self.cfg["theme"] = mode
        cfg_mod.save(self.cfg)
        ctk.set_appearance_mode(mode)
        self._rebuild_ui()

    # ---------- 页面 ----------
    def toggle_view(self):
        if getattr(self, "current_view", "home") == "settings":
            self.show_home()
        else:
            self.show_settings()

    def show_home(self):
        self.current_view = "home"
        for child in self.content.winfo_children():
            if child is not self.home:
                child.destroy()
        self.settings = None
        self.nav_btn.configure(text="⚙")
        self.home.tkraise()

    def show_settings(self):
        self.current_view = "settings"
        for child in self.content.winfo_children():
            if child is not self.home:
                child.destroy()
        self.nav_btn.configure(text="←")
        self.settings = ui_settings.SettingsFrame(self.content, self)
        self.settings.grid(row=0, column=0, sticky="nsew")
        self.settings.tkraise()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()

    def hide_window(self):
        self.root.withdraw()

    # ---------- 清单操作 ----------
    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="选择要监视的 txt 文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )
        if not paths:
            return
        for p in paths:
            self._add_entry(str(Path(p)), "file")
        self._after_list_change("已添加文件")

    def add_folders(self):
        d = filedialog.askdirectory(title="选择要监视的文件夹（含子目录）")
        if not d:
            return
        self._add_entry(str(Path(d)), "folder")
        self._after_list_change("已添加文件夹")

    def _add_entry(self, path: str, kind: str):
        watch = self.cfg.setdefault("watch_list", [])
        for ent in watch:
            if _norm(ent["path"]) == _norm(path):
                return
        watch.append({"path": path, "type": kind})

    def remove_entry(self, entry):
        watch = self.cfg.get("watch_list", [])
        self.cfg["watch_list"] = [e for e in watch if e is not entry and _norm(e["path"]) != _norm(entry["path"])]
        self._after_list_change("已移除")

    def _after_list_change(self, msg: str):
        cfg_mod.save(self.cfg)
        self.watcher.rebuild(self.cfg.get("watch_list", []))
        self.home.refresh()
        logging.info("监视清单变更：%s", msg)

    # ---------- 设置 ----------
    def save_settings(self, values: dict):
        self.cfg.update(values)
        cfg_mod.save(self.cfg)
        logging.info("设置已保存")

    def run_test(self, api_base: str, api_key: str, model: str, on_done):
        def work():
            try:
                converter.test_connection(api_base, api_key, model)
                self.post(lambda: on_done(True, "ok"))
            except Exception as e:  # noqa: BLE001
                self.post(lambda: on_done(False, str(e)))

        threading.Thread(target=work, daemon=True).start()

    # ---------- 转换调度 ----------
    def _start_manager(self):
        self._manager = threading.Thread(target=self._manager_loop, daemon=True)
        self._manager.start()

    def _manager_loop(self):
        pending = {}
        while not self.stopping:
            # 手动队列
            while True:
                try:
                    p = self.manual_q.get_nowait()
                except queue.Empty:
                    break
                self._convert_one(p)
            # 事件队列
            try:
                while True:
                    kind, path = self.event_q.get_nowait()
                    path = _norm(path)
                    if kind == "delete":
                        pending.pop(path, None)
                        self.post(lambda p=path: self._on_deleted(p))
                    elif self.auto and self.is_watched(path):
                        pending[path] = time.monotonic()
            except queue.Empty:
                pass
            if self.auto:
                now = time.monotonic()
                debounce = self.cfg.get("debounce_seconds", 2)
                due = [p for p, t in list(pending.items()) if now - t >= debounce]
                for p in due:
                    pending.pop(p, None)
                    self._convert_one(p)
            time.sleep(0.3)

    def _convert_one(self, path: str):
        if not os.path.isfile(path):
            return
        entry = self._entry_for(path)
        key = entry["path"] if entry else path
        try:
            text = converter.read_text(path)
        except Exception as e:  # noqa: BLE001
            self._status(key, f"读取失败", "error")
            logging.exception("读取失败: %s", path)
            return
        h = converter.content_hash(text)
        if self.last_hash.get(path) == h:
            self._status(key, "已是最新", "subtext")
            return
        self._status(key, "转换中…", "warning")
        res = converter.convert_file(path, self.cfg, self.system_prompt)
        if res.get("ok"):
            self.last_hash[path] = h
            ts = time.strftime("%H:%M:%S")
            self._status(key, f"已同步 {ts}", "success")
            usage = res.get("usage") or {}
            logging.info("已转换 %s -> %s | usage=%s", path, res.get("md_path"), usage)
        else:
            self._status(key, f"失败：{res.get('message', '')[:16]}", "error")
            logging.error("转换失败 %s：%s", path, res.get("message"))

    def convert_all(self):
        files = self._collect_watched_files()
        if not files:
            logging.info("没有可转换的文件")
            return
        for p in files:
            self.manual_q.put(_norm(p))
        logging.info("手动转换 %d 个文件", len(files))

    def _collect_watched_files(self):
        out = set()
        for ent in self.cfg.get("watch_list", []):
            p = Path(ent["path"])
            if ent.get("type") == "folder":
                if not p.is_dir():
                    continue
                for f in p.rglob("*.txt"):
                    if self._excluded(f, p):
                        continue
                    out.add(str(f.resolve()))
            elif p.is_file():
                out.add(str(p.resolve()))
        return sorted(out)

    # ---------- 事件处理 ----------
    def _entry_for(self, path: str):
        np = _norm(path)
        for ent in self.cfg.get("watch_list", []):
            ep = Path(ent["path"])
            if ent.get("type") == "file":
                if _norm(ep) == np:
                    return ent
            else:
                try:
                    Path(path).resolve().relative_to(ep.resolve())
                    return ent
                except ValueError:
                    continue
        return None

    def is_watched(self, path: str) -> bool:
        if not path.lower().endswith(".txt"):
            return False
        ent = self._entry_for(path)
        if ent is None:
            return False
        if ent.get("type") == "folder" and self._excluded(Path(path), Path(ent["path"])):
            return False
        return True

    def _excluded(self, file: Path, folder: Path) -> bool:
        exclude = set(self.cfg.get("exclude_dirs", []))
        try:
            rel = file.resolve().relative_to(folder.resolve())
        except ValueError:
            return False
        return any(part in exclude for part in rel.parts[:-1])

    def _status(self, key: str, text: str, color_key: str = "subtext"):
        home = getattr(self, "home", None)
        if home is not None:
            home.set_status(key, text, color_key)

    def _on_deleted(self, path: str):
        md = converter.md_path_for(path)
        try:
            if md.exists():
                md.unlink()
                logging.info("已删除 %s", md)
        except Exception:
            logging.warning("删除 %s 失败", md, exc_info=True)
        np = _norm(path)
        watch = self.cfg.get("watch_list", [])
        new_watch = [
            e for e in watch
            if not (e.get("type") == "file" and _norm(e["path"]) == np)
        ]
        if len(new_watch) != len(watch):
            self.cfg["watch_list"] = new_watch
            cfg_mod.save(self.cfg)
            self.watcher.rebuild(self.cfg.get("watch_list", []))
            self.home.refresh()

    # ---------- 托盘动作 ----------
    def toggle_auto(self):
        self.auto = not self.auto
        self.home.set_auto_state(self.auto)
        logging.info("自动监听：%s", "开启" if self.auto else "暂停")

    def open_recent_folder(self):
        files = self._collect_watched_files()
        target = None
        if files:
            target = Path(files[0]).parent
        elif self.cfg.get("watch_list"):
            p = Path(self.cfg["watch_list"][0]["path"])
            target = p if p.is_dir() else p.parent
        if target and target.exists():
            os.startfile(str(target))  # noqa: S606

    def open_log(self):
        p = cfg_mod.log_path()
        if p.exists():
            os.startfile(str(p))  # noqa: S606

    # ---------- 线程安全 ----------
    def post(self, fn):
        try:
            self.root.after(0, fn)
        except Exception:
            pass

    def quit(self):
        self.stopping = True
        try:
            self.watcher.stop()
        except Exception:
            pass
        try:
            self.tray.stop()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


def setup_logging():
    handlers = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler(cfg_mod.log_path(), encoding="utf-8"))
    except Exception:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def main():
    setup_logging()
    logging.info("TXT → MD 启动，数据目录：%s", cfg_mod.data_dir())
    app = App()
    app.run()


if __name__ == "__main__":
    main()

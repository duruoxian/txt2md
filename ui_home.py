"""主界面：监视清单卡片列表 + 底部操作栏。"""
from pathlib import Path

import customtkinter as ctk

import icons
import theme

_ICON_CACHE = {}


def _tile(kind: str, size: int = 36):
    key = (kind, size)
    if key not in _ICON_CACHE:
        fn = icons.folder_icon if kind == "folder" else icons.file_icon
        _ICON_CACHE[key] = ctk.CTkImage(
            light_image=fn(size, False), dark_image=fn(size, True), size=(size, size)
        )
    return _ICON_CACHE[key]


class WatchRow(ctk.CTkFrame):
    def __init__(self, master, app, entry):
        super().__init__(master, fg_color=theme.color("card"), corner_radius=theme.RADIUS_CARD)
        self.app = app
        self.entry = entry
        self.grid_columnconfigure(1, weight=1)

        path = Path(entry["path"])
        kind = "folder" if entry.get("type") == "folder" else "file"

        icon = ctk.CTkLabel(self, text="", image=_tile(kind))
        icon.grid(row=0, column=0, padx=(14, 10), pady=12)

        name = ctk.CTkLabel(
            self, text=path.name or str(path), text_color=theme.color("text"),
            font=theme.font(15, "bold"), anchor="w",
        )
        name.grid(row=0, column=1, sticky="ew")

        sub = ctk.CTkLabel(
            self, text=str(path.parent), text_color=theme.color("subtext"),
            font=theme.font(11), anchor="w",
        )
        sub.grid(row=1, column=1, sticky="ew", pady=(0, 12))

        self.chip = ctk.CTkLabel(
            self, text="待命", text_color=theme.color("subtext"),
            fg_color=theme.color("chip_bg"), corner_radius=theme.RADIUS_CHIP,
            font=theme.font(12), padx=12, height=26,
        )
        self.chip.grid(row=0, column=2, rowspan=2, padx=(6, 6))

        remove = ctk.CTkButton(
            self, text="✕", width=32, height=32, corner_radius=16,
            fg_color="transparent", hover_color=theme.color("hover"),
            text_color=theme.color("subtext"), font=theme.font(14),
            command=lambda: self.app.remove_entry(self.entry),
        )
        remove.grid(row=0, column=3, rowspan=2, padx=(0, 10))

    def set_status(self, text: str, color_key: str = "subtext"):
        self.chip.configure(text=text, text_color=theme.color(color_key))


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.color("bg"), corner_radius=0)
        self.app = app
        self.rows = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        self.status_chip = ctk.CTkLabel(
            top, text="● 自动监听中", text_color=theme.color("success"),
            fg_color=theme.color("chip_bg"), corner_radius=theme.RADIUS_CHIP,
            font=theme.font(12), padx=12, height=26,
        )
        self.status_chip.pack(side="left")

        self.list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list.grid(row=1, column=0, sticky="nsew", padx=12, pady=4)
        self.list.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", padx=18, pady=(6, 16))
        bar.grid_columnconfigure(0, weight=1)

        self.convert_btn = ctk.CTkButton(
            bar, text="立即转换全部", height=46, corner_radius=theme.RADIUS_BTN,
            fg_color=theme.color("primary"), hover_color=theme.color("primary_hover"),
            text_color=theme.color("on_primary"), font=theme.font(15, "bold"),
            command=self.app.convert_all,
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        add_file = ctk.CTkButton(
            bar, text="＋ 文件", width=96, height=46, corner_radius=theme.RADIUS_BTN,
            fg_color="transparent", border_width=1, border_color=theme.color("outline"),
            text_color=theme.color("text"), hover_color=theme.color("hover"),
            font=theme.font(13), command=self.app.add_files,
        )
        add_file.grid(row=0, column=1, padx=4)

        add_folder = ctk.CTkButton(
            bar, text="＋ 文件夹", width=102, height=46, corner_radius=theme.RADIUS_BTN,
            fg_color="transparent", border_width=1, border_color=theme.color("outline"),
            text_color=theme.color("text"), hover_color=theme.color("hover"),
            font=theme.font(13), command=self.app.add_folders,
        )
        add_folder.grid(row=0, column=2, padx=(4, 0))

        self.empty = ctk.CTkLabel(
            self.list, text="还没有监视的文件\n点击下方「＋ 文件 / ＋ 文件夹」添加",
            text_color=theme.color("muted"), font=theme.font(13), justify="center",
        )

        self.refresh()

    def set_auto_state(self, on: bool):
        if on:
            self.status_chip.configure(text="● 自动监听中", text_color=theme.color("success"))
        else:
            self.status_chip.configure(text="● 已暂停", text_color=theme.color("warning"))

    def refresh(self):
        for row in self.rows.values():
            row.destroy()
        self.rows = {}
        entries = self.app.cfg.get("watch_list", [])
        if not entries:
            self.empty.grid(row=0, column=0, pady=60)
            return
        self.empty.grid_forget()
        for i, entry in enumerate(entries):
            row = WatchRow(self.list, self.app, entry)
            row.grid(row=i, column=0, sticky="ew", padx=6, pady=6)
            self.rows[entry["path"]] = row

    def set_status(self, path: str, text: str, color_key: str = "subtext"):
        row = self.rows.get(path)
        if row is not None:
            row.set_status(text, color_key)

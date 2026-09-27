"""设置页：API Key、接口地址、模型、防抖、主题。"""
import customtkinter as ctk

import theme

THEME_LABELS = {"System": "跟随系统", "Light": "浅色", "Dark": "深色"}
THEME_BACK = {v: k for k, v in THEME_LABELS.items()}


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.color("bg"), corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=theme.color("card"), corner_radius=theme.RADIUS_CARD)
        card.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        card.grid_columnconfigure(1, weight=1)

        r = 0

        def label(text):
            nonlocal r
            ctk.CTkLabel(card, text=text, text_color=theme.color("text"),
                         font=theme.font(13, "bold"), anchor="w").grid(
                row=r, column=0, sticky="w", padx=(18, 12), pady=(16 if r == 0 else 10, 4)
            )

        def label_row(text):
            nonlocal r
            ctk.CTkLabel(card, text=text, text_color=theme.color("subtext"),
                         font=theme.font(12), anchor="w").grid(
                row=r, column=0, sticky="w", padx=(18, 12), pady=(14, 4)
            )

        # API Base
        label_row("接口地址")
        self.api_base = ctk.CTkEntry(
            card, corner_radius=theme.RADIUS_INPUT, height=38,
            fg_color=theme.color("bg"), border_color=theme.color("outline"),
            text_color=theme.color("text"), font=theme.font(13),
        )
        self.api_base.grid(row=r, column=1, sticky="ew", padx=(0, 18), pady=(14, 4))
        self.api_base.insert(0, app.cfg.get("api_base", ""))
        r += 1

        # Model
        label_row("模型")
        self.model = ctk.CTkEntry(
            card, corner_radius=theme.RADIUS_INPUT, height=38,
            fg_color=theme.color("bg"), border_color=theme.color("outline"),
            text_color=theme.color("text"), font=theme.font(13),
        )
        self.model.grid(row=r, column=1, sticky="ew", padx=(0, 18), pady=(14, 4))
        self.model.insert(0, app.cfg.get("model", ""))
        r += 1

        # API Key
        label_row("API Key")
        key_box = ctk.CTkFrame(card, fg_color="transparent")
        key_box.grid(row=r, column=1, sticky="ew", padx=(0, 18), pady=(14, 4))
        key_box.grid_columnconfigure(0, weight=1)
        self.api_key = ctk.CTkEntry(
            key_box, show="•", corner_radius=theme.RADIUS_INPUT, height=38,
            fg_color=theme.color("bg"), border_color=theme.color("outline"),
            text_color=theme.color("text"), font=theme.font(13),
        )
        self.api_key.grid(row=0, column=0, sticky="ew")
        self.api_key.insert(0, app.cfg.get("api_key", ""))
        self._show_key = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            key_box, text="显示", variable=self._show_key, command=self._toggle_key,
            font=theme.font(12), text_color=theme.color("subtext"),
            fg_color=theme.color("primary"), hover_color=theme.color("primary_hover"),
            checkbox_width=18, checkbox_height=18, corner_radius=5,
        ).grid(row=0, column=1, padx=(8, 0))
        r += 1

        # Test
        test_row = ctk.CTkFrame(card, fg_color="transparent")
        test_row.grid(row=r, column=1, sticky="ew", padx=(0, 18), pady=(8, 4))
        self.test_btn = ctk.CTkButton(
            test_row, text="测试连接", width=110, height=34, corner_radius=theme.RADIUS_BTN,
            fg_color=theme.color("primary"), hover_color=theme.color("primary_hover"),
            text_color=theme.color("on_primary"), font=theme.font(13), command=self._test,
        )
        self.test_btn.pack(side="left")
        self.test_result = ctk.CTkLabel(
            test_row, text="", text_color=theme.color("subtext"), font=theme.font(12)
        )
        self.test_result.pack(side="left", padx=12)
        r += 1

        # Debounce
        label_row("保存后延迟（秒）")
        self.debounce = ctk.CTkSlider(
            card, from_=0, to=10, number_of_steps=10,
            progress_color=theme.color("primary"), button_color=theme.color("primary"),
            button_hover_color=theme.color("primary_hover"), command=self._on_debounce,
        )
        self.debounce.grid(row=r, column=1, sticky="ew", padx=(0, 18), pady=(14, 4))
        self.debounce.set(float(app.cfg.get("debounce_seconds", 2)))
        self.debounce_val = ctk.CTkLabel(
            card, text=f"{int(app.cfg.get('debounce_seconds', 2))} 秒",
            text_color=theme.color("subtext"), font=theme.font(12), width=48,
        )
        self.debounce_val.grid(row=r, column=2, padx=(0, 18), pady=(14, 4))
        r += 1

        # Theme
        label_row("主题")
        self.theme_seg = ctk.CTkSegmentedButton(
            card, values=[THEME_LABELS["System"], THEME_LABELS["Light"], THEME_LABELS["Dark"]],
            font=theme.font(12), command=self._on_theme,
            selected_color=theme.color("primary"), selected_hover_color=theme.color("primary_hover"),
            unselected_color=theme.color("chip_bg"), unselected_hover_color=theme.color("hover"),
            text_color=theme.color("text"), corner_radius=theme.RADIUS_INPUT,
        )
        self.theme_seg.grid(row=r, column=1, columnspan=2, sticky="w", padx=(0, 18), pady=(14, 4))
        self.theme_seg.set(THEME_LABELS.get(app.cfg.get("theme", "System"), "跟随系统"))
        r += 1

        # Save
        ctk.CTkButton(
            card, text="保存设置", height=44, corner_radius=theme.RADIUS_BTN,
            fg_color=theme.color("primary"), hover_color=theme.color("primary_hover"),
            text_color=theme.color("on_primary"), font=theme.font(14, "bold"),
            command=self._save,
        ).grid(row=r, column=1, sticky="w", padx=(0, 18), pady=(18, 18))

    def _toggle_key(self):
        self.api_key.configure(show="" if self._show_key.get() else "•")

    def _on_debounce(self, value):
        self.debounce_val.configure(text=f"{int(round(value))} 秒")

    def _on_theme(self, value):
        self.app.apply_theme(THEME_BACK.get(value, "System"))

    def _values(self):
        return {
            "api_base": self.api_base.get().strip(),
            "model": self.model.get().strip(),
            "api_key": self.api_key.get().strip(),
            "debounce_seconds": int(round(self.debounce.get())),
            "theme": THEME_BACK.get(self.theme_seg.get(), "System"),
        }

    def _test(self):
        v = self._values()
        self.test_btn.configure(state="disabled", text="测试中…")
        self.test_result.configure(text="", text_color=theme.color("subtext"))
        self.app.run_test(v["api_base"], v["api_key"], v["model"], self._test_done)

    def _test_done(self, ok, msg):
        self.test_btn.configure(state="normal", text="测试连接")
        if ok:
            self.test_result.configure(text="✓ 连接成功", text_color=theme.color("success"))
        else:
            self.test_result.configure(text=f"✕ {msg}", text_color=theme.color("error"))

    def _save(self):
        self.app.save_settings(self._values())
        self.test_result.configure(text="已保存", text_color=theme.color("success"))

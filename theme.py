"""设计令牌：LocalSend / Material 3 风格的配色与圆角。"""
import customtkinter as ctk

PRIMARY_LIGHT = "#00897B"
PRIMARY_DARK = "#4DB6AC"

PALETTE = {
    "light": {
        "bg": "#F6F7F9",
        "card": "#FFFFFF",
        "text": "#1C1B1F",
        "subtext": "#5F6368",
        "outline": "#E0E0E0",
        "primary": PRIMARY_LIGHT,
        "primary_hover": "#00796B",
        "on_primary": "#FFFFFF",
        "chip_bg": "#ECEFF1",
        "hover": "#F0F2F5",
        "success": "#2E7D32",
        "warning": "#ED6C02",
        "error": "#B3261E",
        "muted": "#8A9099",
    },
    "dark": {
        "bg": "#121212",
        "card": "#1E1E1E",
        "text": "#E6E1E5",
        "subtext": "#9AA0A6",
        "outline": "#2A2A2A",
        "primary": PRIMARY_DARK,
        "primary_hover": "#3FA79B",
        "on_primary": "#00332E",
        "chip_bg": "#2A2A2A",
        "hover": "#262626",
        "success": "#81C784",
        "warning": "#FFB74D",
        "error": "#EF9A9A",
        "muted": "#7C8288",
    },
}

RADIUS_CARD = 16
RADIUS_BTN = 24
RADIUS_INPUT = 12
RADIUS_CHIP = 8

FONT_FAMILY = "Microsoft YaHei UI"


def is_dark() -> bool:
    return ctk.get_appearance_mode() == "Dark"


def color(name: str) -> str:
    return PALETTE["dark" if is_dark() else "light"][name]


def font(size: int = 14, weight: str = "normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)

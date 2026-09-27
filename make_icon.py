"""生成 exe / 窗口使用的 icon.ico（构建前运行一次）。"""
from pathlib import Path

import icons

out = Path(__file__).resolve().parent / "icon.ico"
img = icons.app_icon(256)
img.save(out, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("已生成", out)

"""运行时用 Pillow 绘制图标，无需外部素材文件。"""
from PIL import Image, ImageDraw

PRIMARY = (0, 137, 123, 255)
WHITE = (255, 255, 255, 255)


def app_icon(size: int = 256) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=PRIMARY)
    w, h = size * 0.34, size * 0.44
    x, y = (size - w) / 2, (size - h) / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(size * 0.05), fill=WHITE)
    for i in range(3):
        ly = y + h * 0.28 + i * h * 0.18
        d.line([x + w * 0.18, ly, x + w * 0.82, ly], fill=PRIMARY, width=max(1, int(size * 0.022)))
    return img


def _tile_bg(size: int, dark: bool):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill = (77, 182, 172, 55) if dark else (0, 137, 123, 40)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.28), fill=fill)
    return img, d


def _fg(dark: bool):
    return (77, 182, 172, 255) if dark else (0, 137, 123, 255)


def file_icon(size: int = 40, dark: bool = False) -> Image.Image:
    img, d = _tile_bg(size, dark)
    fg = _fg(dark)
    w, h = size * 0.42, size * 0.52
    x, y = (size - w) / 2, (size - h) / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(size * 0.06), fill=fg)
    for i in range(3):
        ly = y + h * 0.3 + i * h * 0.2
        d.line([x + w * 0.2, ly, x + w * 0.8, ly], fill=(255, 255, 255, 220), width=max(1, int(size * 0.035)))
    return img


def folder_icon(size: int = 40, dark: bool = False) -> Image.Image:
    img, d = _tile_bg(size, dark)
    fg = _fg(dark)
    w, h = size * 0.54, size * 0.42
    x, y = (size - w) / 2, (size - h) / 2 + size * 0.03
    d.rounded_rectangle([x, y - h * 0.18, x + w * 0.45, y + h * 0.25], radius=int(size * 0.05), fill=fg)
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(size * 0.07), fill=fg)
    return img

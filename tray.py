"""系统托盘图标。左键（单击）= 立即转换；双击 = 打开最近文件夹。"""
import threading
import time

import pystray
from pystray import MenuItem as Item


class Tray:
    def __init__(self, app, icon_image):
        self.app = app
        self._last_click = 0.0
        self._timer = None
        self._lock = threading.Lock()
        self.icon = pystray.Icon("txt2md", icon_image, "TXT → MD", menu=self._menu())

    def _menu(self):
        return pystray.Menu(
            Item("立即转换全部", self._on_default, default=True),
            Item("暂停 / 恢复自动监听", lambda i, it: self.app.post(self.app.toggle_auto)),
            Item("打开最近文件夹", lambda i, it: self.app.post(self.app.open_recent_folder)),
            pystray.Menu.SEPARATOR,
            Item("显示主界面", lambda i, it: self.app.post(self.app.show_window)),
            Item("设置", lambda i, it: self.app.post(self.app.show_settings)),
            Item("查看日志", lambda i, it: self.app.post(self.app.open_log)),
            pystray.Menu.SEPARATOR,
            Item("退出", lambda i, it: self.app.post(self.app.quit)),
        )

    def _on_default(self, icon, item):
        now = time.monotonic()
        with self._lock:
            if now - self._last_click < 0.45:
                self._last_click = 0.0
                if self._timer:
                    self._timer.cancel()
                    self._timer = None
                self.app.post(self.app.open_recent_folder)
                return
            self._last_click = now
            self._timer = threading.Timer(0.45, self._single)
            self._timer.start()

    def _single(self):
        with self._lock:
            self._timer = None
        self.app.post(self.app.convert_all)

    def run(self):
        self.icon.run_detached()

    def stop(self):
        try:
            self.icon.stop()
        except Exception:
            pass

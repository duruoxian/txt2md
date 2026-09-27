"""基于 watchdog 的文件夹/文件监听，事件通过回调抛出。"""
import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def _is_txt(p: str) -> bool:
    return str(p).lower().endswith(".txt")


class _Handler(FileSystemEventHandler):
    def __init__(self, emit):
        super().__init__()
        self._emit = emit

    def on_modified(self, event):
        if not event.is_directory and _is_txt(event.src_path):
            self._emit("change", event.src_path)

    def on_created(self, event):
        if not event.is_directory and _is_txt(event.src_path):
            self._emit("change", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and _is_txt(event.src_path):
            self._emit("delete", event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        if _is_txt(event.src_path):
            self._emit("delete", event.src_path)
        if _is_txt(event.dest_path):
            self._emit("change", event.dest_path)


class Watcher:
    def __init__(self, emit):
        self._emit = emit
        self._observer = None

    def rebuild(self, entries):
        self.stop()
        obs = Observer()
        seen = set()
        for ent in entries:
            p = Path(ent.get("path", ""))
            if ent.get("type") == "folder" and p.is_dir():
                key = (str(p.resolve()), True)
                if key in seen:
                    continue
                seen.add(key)
                obs.schedule(_Handler(self._emit), str(p), recursive=True)
            else:
                parent = p.parent
                if not parent.is_dir():
                    continue
                key = (str(parent.resolve()), False)
                if key in seen:
                    continue
                seen.add(key)
                obs.schedule(_Handler(self._emit), str(parent), recursive=False)
        if obs.emitters:
            obs.daemon = True
            obs.start()
            self._observer = obs

    def stop(self):
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=3)
            except Exception:
                logging.warning("停止监听失败", exc_info=True)
            self._observer = None

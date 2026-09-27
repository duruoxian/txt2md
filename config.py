"""配置读写：便携模式，配置与日志默认放在程序（或 exe）同目录。"""
import json
import os
import sys
from pathlib import Path

APP_NAME = "txt2md"

DEFAULTS = {
    "watch_list": [],          # [{"path": "...", "type": "file"|"folder"}]
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "api_key": "",
    "debounce_seconds": 2,
    "theme": "System",         # System | Light | Dark
    "max_file_bytes": 1048576,  # 1MB，超过则跳过
    "exclude_dirs": [".git", "node_modules", ".venv", "venv", "__pycache__", ".idea", ".vscode"],
}


def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    """优先程序同目录（便携）；不可写则回退 %APPDATA%\\txt2md。"""
    d = base_dir()
    try:
        probe = d / ".write_probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return d
    except Exception:
        fallback = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def config_path() -> Path:
    return data_dir() / "config.json"


def log_path() -> Path:
    return data_dir() / "sync.log"


def load() -> dict:
    p = config_path()
    cfg = dict(DEFAULTS)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg


def save(cfg: dict) -> None:
    tmp = config_path().with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, config_path())

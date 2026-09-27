"""调用 DeepSeek，将纯文本重排为 Markdown；原子写入，失败保留旧文件。"""
import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_PROMPT = """你是一个文档排版助手。用户会给你一段随手写的纯文本笔记，你需要把它整理成结构清晰、排版美观的 Markdown。

严格规则：
1. 只做“排版与结构化”，绝对不得新增、删除或修改任何事实性内容：人名、课程名、日期、时间、数字、URL 必须原样保留。
2. 不要改变用户的陈述本意；不要补充用户没有写的信息。
3. 根据内容合理使用：一级标题(#)作为文档总标题、二级/三级标题分节、无序/有序列表、表格、引用块(>)、加粗强调。
4. 如果某些内容无法明确归类，原样保留在文档末尾的“其他”小节，不要丢弃。
5. 保持中文标点与原文用词习惯。
6. 只输出 Markdown 正文本身，不要任何解释性文字，不要用 ``` 代码块包裹整篇内容。"""


def read_text(path: str) -> str:
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_system_prompt(base_dir: Path) -> str:
    p = base_dir / "prompt.md"
    if p.exists():
        try:
            return p.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return DEFAULT_PROMPT


def _post(api_base: str, api_key: str, payload: dict, timeout: int = 90) -> dict:
    url = api_base.rstrip("/") + "/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body[:300]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e


def _strip_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def test_connection(api_base: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "回复两个字：连接"}],
        "max_tokens": 8,
        "stream": False,
    }
    data = _post(api_base, api_key, payload, timeout=30)
    return data["choices"][0]["message"]["content"].strip()


def convert_text(api_base: str, api_key: str, model: str, system_prompt: str, text: str) -> tuple[str, dict]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    data = _post(api_base, api_key, payload)
    md = _strip_fence(data["choices"][0]["message"]["content"])
    return md, data.get("usage", {})


def md_path_for(txt_path: str) -> Path:
    return Path(txt_path).with_suffix(".md")


def write_markdown(txt_path: str, md: str) -> Path:
    target = md_path_for(txt_path)
    if target.exists():
        try:
            backup = target.with_suffix(".md.bak")
            backup.write_bytes(target.read_bytes())
        except Exception:
            logging.warning("备份 %s 失败", target)
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(md, encoding="utf-8")
    os.replace(tmp, target)
    return target


def convert_file(path: str, cfg: dict, system_prompt: str) -> dict:
    """读取 txt -> 调 AI -> 原子写 md。返回 {ok, md_path, message, usage}。"""
    text = read_text(path).strip()
    if not text:
        return {"ok": False, "message": "文件为空，跳过"}
    if not cfg.get("api_key"):
        return {"ok": False, "message": "未配置 API Key"}
    try:
        md, usage = convert_text(
            cfg["api_base"], cfg["api_key"], cfg["model"], system_prompt, text
        )
        target = write_markdown(path, md)
        return {"ok": True, "md_path": str(target), "message": "已更新", "usage": usage}
    except Exception as e:  # noqa: BLE001
        logging.exception("转换失败: %s", path)
        return {"ok": False, "message": str(e)}

# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Optional

Grade = Literal["T", "S", "N"]


@dataclass
class TocEntry:
    id: str
    level: int
    title: str
    print_start: Optional[int] = None
    print_end: Optional[int] = None
    pdf_start: Optional[int] = None
    pdf_end: Optional[int] = None
    source: str = ""


@dataclass
class Capability:
    id: str
    path: str
    pages: int
    encrypted: bool
    grade: Grade
    chars_per_page: float
    has_bookmarks: bool
    has_images: bool = False
    toc_page_hint: list = field(default_factory=list)
    page_size: tuple = (0, 0)


@dataclass
class PageMap:
    id: str
    method: str = "none"
    print2pdf: dict = field(default_factory=dict)  # printed_page -> pdf_page(1-based)
    conflicts: list = field(default_factory=list)


def dumps(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2,
                      default=lambda x: asdict(x) if hasattr(x, "__dict__") else str(x))


def load_json(p: Path) -> dict:
    if not Path(p).exists():
        return {}
    return json.loads(Path(p).read_text(encoding="utf-8"))


def save_json(p: Path, o) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(dumps(o), encoding="utf-8")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def slugify(s: str, n: int = 0) -> str:
    out = "".join(c if (c.isalnum() or c in "-_") else "-" for c in s.lower())
    out = "-".join(x for x in out.split("-") if x)
    return out[:n] if n else out


def default_group(name: str) -> str:
    """按文件名启发式确定卷分组，供首页按 MEGA 分辑归类；可被 config/catalog.json 覆盖。"""
    s = name
    if "Gesamtausgabe" in s:
        low = s.lower()
        if any(k in low for k in ("apparat", "miskewitsch", "z-lib", "1lib")):
            return "辅助文献"
        if any(k in s for k in ("1861-1863", "1861–1863", "Okonomische Manuskripte 1857",
                                "Ökonomische Manuskripte 1857", "Manuskripte 1857-58",
                                "Manuskript 1861-1863")):
            return "MEGA²·II 《资本论》与手稿"
        return "MEGA¹ 第一历史考证版"
    if re.match(r"^[134]\.\d", s):
        return "MEGA¹ 第一历史考证版"
    low = s.lower()
    if "mega¹" in low:
        return "MEGA¹ 第一历史考证版"
    if "mega² i." in low:
        return "MEGA²·I 著作·文章·草稿"
    if "mega² ii." in low:
        return "MEGA²·II 《资本论》与手稿"
    if "mega² iii." in low:
        return "MEGA²·III 书信"
    if "mega² iv." in low:
        return "MEGA²·IV 摘录与笔记"
    if any(k in low for k in ("apparat", "miskewitsch", "z-lib", "1lib")):
        return "辅助文献"
    if "《" in s:
        return "研究专著"
    return "未分组"
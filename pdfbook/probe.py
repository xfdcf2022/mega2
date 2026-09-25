# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from pathlib import Path

import pymupdf as fitz

from .model import Capability, save_json, slugify

SAMPLE = 8
TOC_LIKE_MIN = 4


def _chars(text: str) -> int:
    return len(re.sub(r"\s", "", text or ""))


def _toc_like(text: str) -> bool:
    lines = [l for l in text.splitlines() if l.strip()]
    hits = sum(1 for l in lines
               if re.match(r"^\s*.{4,80}[.·…–]{3,}.*?\d{1,4}\s*$", l))
    return hits >= TOC_LIKE_MIN


def probe(path: str, out_dir: Path) -> Capability:
    pid = slugify(Path(path).stem, 80) or "doc"
    doc = fitz.open(path)
    n = doc.page_count
    enc = bool(doc.needs_pass)

    samples = sorted({max(0, i * n // SAMPLE) for i in range(SAMPLE)} | {n // 2})
    chars = sum(_chars(doc[i].get_text()) for i in samples)
    cpp = chars / max(1, len(samples))
    img_pages = sum(1 for i in samples if doc[i].get_images(full=True))
    grade = "T" if cpp > 1800 else ("S" if cpp > 150 else "N")
    has_img = img_pages >= len(samples) / 2
    has_bm = bool(doc.get_toc(simple=True))
    p0 = doc[0].rect if n else None
    pg = (round(p0.width), round(p0.height)) if p0 else (0, 0)
    hint = [i for i in range(min(40, n)) if _toc_like(doc[i].get_text())]

    cap = Capability(id=pid, path=str(path), pages=n, encrypted=enc, grade=grade,
                     chars_per_page=round(cpp, 1), has_bookmarks=has_bm, has_images=has_img,
                     toc_page_hint=hint, page_size=pg)
    save_json(out_dir / f"probe/{pid}.json", cap)
    doc.close()
    return cap
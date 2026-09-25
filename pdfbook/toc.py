# -*- coding: utf-8 -*-
from __future__ import annotations

import re

import pymupdf as fitz

from .model import TocEntry

TOC_LINE = re.compile(r"^(\s*)(.{2,80}?)\s*[.·…–]{2,}?\s*(\d{1,4})\s*[*†]?\s*$")
PAGE_PAT = re.compile(r"\|\|(\d{1,4})(\d)")
HEAD_KEYS = ("inha", "verzeichnis", "inhalt", "目录", "sommaire")


def walk_root(doc: fitz.Document, cap_id: str, toc_max_level: int = 2):
    """目录获取，5 级回退：印刷目录页 > 书签 > 正文标题 > 固定分块 > 整书一章。"""
    texts = [doc[i].get_text() for i in range(doc.page_count)]
    tpages = _find_toc_pages(texts)
    if tpages:
        entries = _parse_multi_toc(texts, tpages, cap_id)
        kept = [e for e in entries if e.print_start is not None]
        if len(kept) >= 3:
            return _prune_by_level(kept, toc_max_level)

    bm = doc.get_toc(simple=True)
    if bm:
        return _prune_by_level(_from_bookmarks(bm, cap_id), toc_max_level)

    h = _headings(doc, cap_id)
    if h:
        return h

    return [TocEntry(id=f"{cap_id}-ch000", level=0, title="全书",
                     print_start=1, print_end=doc.page_count,
                     pdf_start=1, pdf_end=doc.page_count, source="book")]


def _find_toc_pages(texts: list) -> list:
    cands = []
    for i, t in enumerate(texts):
        lines = [l for l in t.splitlines() if l.strip()]
        rows = [TOC_LINE.match(l) for l in lines]
        rows = [m for m in rows if m]
        if len(rows) < 4:
            continue
        pages = []
        for m in rows:
            try:
                pages.append(int(m.group(3)))
            except ValueError:
                continue
        if not pages:
            continue
        incr = sum(1 for a, b in zip(pages, pages[1:]) if b > a)
        if incr / max(1, len(pages) - 1) >= 0.7:  # 目录页码单调；Register 类按字母序会被剔除
            cands.append(i)
    return cands


def _parse_multi_toc(texts, pages: list, cap_id: str) -> list:
    rows = []
    for p in pages:
        for raw in texts[p].splitlines():
            m = TOC_LINE.match(raw)
            if not m:
                continue
            indent, title, pgn = m.group(1), m.group(2).strip(), int(m.group(3))
            level = min(3, len(indent.replace("　", "  ")) // 2)
            rows.append((level, title, pgn, p))
    # 汇总并按(pdf页,行序)排序后去重
    rows = list(dict.fromkeys(rows))
    # 处理跨行标题：页码相同且紧邻的并入前一条
    merged = []
    for r in rows:
        if merged and r[2] == merged[-1][2] and r[1] != merged[-1][1]:
            merged[-1] = (min(r[0], merged[-1][0]),
                          merged[-1][1] + " " + r[1], r[2], r[3])
        else:
            merged.append(r)
    out = []
    for seq, (level, title, pgn, _p) in enumerate(merged, 1):
        base = slug_keep(cap_id)
        out.append(TocEntry(id=f"{base}-c{seq:03d}", level=level, title=_clean(title),
                            print_start=pgn, source="tocpage"))
    return out


def slug_keep(s: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in s.lower()).strip("-")[:40]


def _from_bookmarks(bm, cap_id: str) -> list:
    out = []
    for seq, (lv, ti, pg) in enumerate(bm):
        out.append(TocEntry(id=f"{cap_id}-bm{seq:04d}", level=lv, title=_clean(ti),
                            pdf_start=pg, source="bookmark"))
    return out


def _clean(s: str) -> str:
    import re as _re
    return _re.sub(r"[\x00-\x1f]", "", s or "").strip()


def _prune_by_level(entries: list, ml: int) -> list:
    """保留 level<=ml 的条目，并按 pdf/print 起始排序。区间吸收在 apply_toc_pages 完成。"""
    kept = [e for e in entries if e.level <= ml]
    key = "pdf_start" if any(e.pdf_start for e in kept) else "print_start"
    kept.sort(key=lambda e: getattr(e, key) or 0)
    return kept


def _fill_sequential(entries: list, key: str) -> None:
    for i, e in enumerate(entries):
        v = getattr(e, key + "_start")
        if v is not None and i + 1 < len(entries):
            nv = getattr(entries[i + 1], key + "_start")
            if nv is not None:
                setattr(e, key + "_end", max(v, nv - 1))


def _apply_max_level(entries: list, ml: int) -> None:
    entries[:] = [e for e in entries if e.level <= ml]


def _headings(doc: fitz.Document, cap_id: str) -> list:
    out, seq = [], 0
    for i in range(min(doc.page_count, 3000)):
        d = doc[i].get_text("dict")
        w = d.get("width", 0)
        for b in d.get("blocks", [])[:14]:
            for l in b.get("lines", []):
                spans = l.get("spans", [])
                if not spans:
                    continue
                s0 = max(spans, key=lambda s: s["size"])
                center = abs(b["bbox"][0] - (w - b["bbox"][2]) / 2) < 80 if w else False
                if s0["size"] >= 13 and center:
                    seq += 1
                    title = re.sub(r"\s+", " ", s0["text"]).strip()
                    if title and len(title) <= 120:
                        out.append(TocEntry(id=f"{cap_id}-hd{seq:04d}", level=0,
                                            title=title, pdf_start=i + 1, source="heading"))
    return out


PAGE_MARKER = r"\|\|(\d{1,4})(\d)"
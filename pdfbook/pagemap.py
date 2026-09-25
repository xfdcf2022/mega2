# -*- coding: utf-8 -*-
from __future__ import annotations

import re

import pymupdf as fitz

from .model import load_json, save_json
from .toc import PAGE_MARKER


def build(doc: fitz.Document, cap_id: str, toc, out_dir) -> None:
    """印刷页⇄PDF页 映射，写入 pagemap/{id}.json。4 级回退+人工覆盖。"""
    ov = load_json(out_dir / f"../config/page-map/{cap_id}.json")
    if ov.get("print2pdf"):
        pm = {"id": cap_id, "method": "override",
              "print2pdf": {int(k): int(v) for k, v in ov["print2pdf"].items()}}
        save_json(out_dir / f"pagemap/{cap_id}.json", pm)
        return

    mapping, method = {}, "none"
    mapping_hf = _by_headers_footers(doc)
    mapping_mk = _by_markers(doc, PAGE_MARKER)
    mapping = dict(mapping_hf)
    for k, v in mapping_mk.items():
        mapping.setdefault(k, v)  # markers 补 headerfooter 空缺
    mapping = _monotonic(mapping)
    if len(mapping) >= 10:
        method = "headerfooter+markers" if mapping_mk and len(mapping_hf) >= 10 else ("markers" if len(mapping_mk) >= 10 else "headerfooter")
    else:
        mapping = _by_offset(doc)
        method = "offset"

    pm = {"id": cap_id, "method": method, "print2pdf": {str(k): v for k, v in mapping.items()}}
    save_json(out_dir / f"pagemap/{cap_id}.json", pm)


def _by_markers(doc, pat):
    m = {}
    for i in range(doc.page_count):
        for pg, _line in re.findall(pat, doc[i].get_text()):
            p = int(pg)
            if 1 <= p <= doc.page_count + 800 and p not in m:
                m[p] = i + 1
    return m


def _by_headers_footers(doc):
    """仅取页脚区(y>86%)的孤立数字作为印刷页码，避免页眉数字污染。"""
    m = {}
    cap = doc.page_count
    for i in range(doc.page_count):
        pg = doc[i]
        h = pg.rect.height or 1
        cands = []
        for b in pg.get_text("blocks"):
            _x0, y0, _x1, _y1, txt = b[0], b[1], b[2], b[3], b[4]
            if y0 > h * 0.86 and txt:
                cands.extend(int(x) for x in re.findall(r"\b\d{1,4}\b", txt or ""))
        cands = [c for c in cands if 1 <= c <= cap]
        if cands:
            m.setdefault(max(set(cands), key=cands.count), i + 1)
    return m


def _monotonic(d):
    """按 pdf 序遍历，印刷页序与 pdf 序双向严格递增，剔除重复/杂值。"""
    out, last_pdf, last_print = {}, -1, -1
    for pr, pdf in sorted(d.items(), key=lambda kv: (kv[1], kv[0])):
        if pdf <= last_pdf:
            continue
        if pr > last_print:
            out[pr] = pdf
            last_pdf, last_print = pdf, pr
    return out


def _by_offset(doc):
    return {1: 1}


def apply_toc_pages(toc, pm_dict, page_count: int) -> None:
    """把印刷页码映射应用到 toc，并按层级吸收规则填充 pdf 区间。"""
    p2p = {int(k): int(v) for k, v in pm_dict.get("print2pdf", {}).items()}
    for e in toc:
        if e.source == "bookmark":
            continue
        if e.print_start and e.print_start in p2p:
            e.pdf_start = p2p[e.print_start]
        else:
            e.pdf_start = None
    # 按 pdf 序排序；无映射的条目剔除（不参与建章）
    ordered = sorted([e for e in toc if e.pdf_start], key=lambda e: (e.pdf_start, e.level))
    # 区间吸收：父/同级条目吸收其下整个子块
    for i, e in enumerate(ordered):
        end = None
        for nxt in ordered[i + 1:]:
            if nxt.level <= e.level:
                end = nxt.pdf_start - 1
                break
        if end is None:
            end = page_count
        e.pdf_end = max(e.pdf_start, min(end, page_count))
    toc[:] = ordered
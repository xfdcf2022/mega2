# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import pymupdf as fitz

from . import extract as ext_m, pagemap as pm_m, probe as probe_m, render as rnd_m
from . import site as site_m, toc as toc_m
from .model import Capability, TocEntry, default_group, load_json, save_json, slugify


def _norm(b: dict, group: str) -> dict:
    b = dict(b)
    b["group"] = group or b.get("group") or "未分组"
    b["cap"] = Capability(**b["cap"]) if isinstance(b.get("cap"), dict) else b.get("cap")
    if isinstance(b.get("toc"), list):
        b["toc"] = [t if isinstance(t, TocEntry) else TocEntry(**t) for t in b["toc"]]
    return b


def _main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 pdfbook/site")
    ap.add_argument("--src", nargs="+", required=True, help="PDF 通配路径，可多值")
    ap.add_argument("--out", default="site")
    ap.add_argument("--config", default="config/catalog.json")
    ap.add_argument("--toc-max-level", type=int, default=2)
    ap.add_argument("--render-images", choices=["all", "by-mode", "none"], default="by-mode")
    ap.add_argument("--img-width", type=int, default=1500, help="原稿页图宽度像素（小=省空间，Pages 部署建议 600~700）")
    ap.add_argument("--footnote-band", type=float, default=0.90)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--only-toc", action="store_true", help="只跑探测定级+目录，不建站")
    a = ap.parse_args(argv)

    work = Path("work")
    work.mkdir(exist_ok=True)
    files = sorted({f for pat in a.src for f in glob.glob(pat, recursive=True) if f.lower().endswith(".pdf")})
    if not files:
        print("!! 没有匹配到 PDF"); return 1

    if a.plan:
        _plan(files); return 0

    catalog = load_json(Path(a.config))
    books = []
    for p in files:
        pid = slugify(Path(p).stem, 80) or "doc"
        bj = work / f"book/{pid}.json"
        if a.resume and bj.exists():
            meta = (catalog or {}).get("books", {}).get(pid, {}) or {}
            grp = meta.get("group") or default_group(Path(p).stem)
            b = _norm(load_json(bj), grp)
            save_json(bj, b)
            books.append(b)
            print(f"[resume] {pid}  group={b['group']}"); continue
        cap = probe_m.probe(p, work)
        doc = fitz.open(p)
        toc = toc_m.walk_root(doc, pid, toc_max_level=a.toc_max_level)
        pm_m.build(doc, pid, toc, work)
        pm = load_json(work / f"pagemap/{pid}.json")
        pm_m.apply_toc_pages(toc, pm, doc.page_count)
        doc.close()
        meta = (catalog or {}).get("books", {}).get(pid, {}) or {}
        b = {"id": pid, "path": p, "cap": cap, "toc": toc, "pm": pm,
             "title_de": meta.get("title_de", pid), "title_zh": meta.get("title_zh", ""),
             "group": meta.get("group") or default_group(Path(p).stem)}
        save_json(bj, b)
        print(f"[ok] {pid}  grade={cap.grade}  pages={cap.pages}  toc={len(toc)}"
              f"  mapped={sum(1 for e in toc if e.pdf_start)}  method={pm.get('method')}")
        books.append(b)
    if a.only_toc:
        return 0
    # 增量合并：把本次批次 + 所有已缓存卷一起建站，避免首页只列当批
    cached = sorted(glob.glob("work/book/*.json"))
    byid = {b["id"]: b for b in books}
    for cj in cached:
        cb = _norm(load_json(cj), "")
        byid.setdefault(cb["id"], cb)
    allbooks = [byid[k] for k in byid.keys()]
    site_m.build_site(allbooks, Path(a.out), a.render_images, a.toc_max_level, a.footnote_band, a.img_width)
    print(f"[site] built -> {Path(a.out)}/index.html  (卷数={len(allbooks)})")
    return 0


def _plan(files: list):
    tot = 0
    for p in files:
        d = fitz.open(p); tot += d.page_count; d.close()
    est_gb = tot * 0.11 / 1024
    print(f"卷数={len(files)}  总页数≈{tot}  全量烘焙≈{est_gb:.1f}GB（约 110KB/页）")
    if est_gb > 18:
        print("!! 磁盘红线：全量烘焙超 18GB，建议 --render-images none/by-mode 或分批")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(_main())
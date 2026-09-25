# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

import pymupdf as fitz

from . import assets as assets_m
from . import extract as ext_m
from . import render as rnd_m
from .model import dumps, slugify

TOC_LIKE = r"^\s*.{4,80}[.·…–]{3,}.*?\d{1,4}\s*$"


def build_site(books: list, out: Path, render_images: str = "by-mode",
               toc_max_level: int = 2, footnote_band: float = 0.72, img_width: int = 1500) -> None:
    out.mkdir(parents=True, exist_ok=True)
    assets_m.install(out / "assets")

    groups = {}
    for b in books:
        groups.setdefault(_group(b), []).append(b)
        _build_book(b, out, render_images, toc_max_level, footnote_band, img_width)

    _write_index(out, books, groups)
    _write_groups(out, groups)
    _write_search(out, books)


def _group(b: dict) -> str:
    return b.get("group") or "未分组"


def _build_book(b: dict, out: Path, render_images: str, ml: int, band: float, img_width: int = 1500) -> None:
    pid = b["cap"].id
    bg = out / "books" / pid
    bg.mkdir(parents=True, exist_ok=True)

    p2p = {}
    for k, v in (b.get("pm") or {}).get("print2pdf", {}).items():
        p2p.setdefault(int(v), int(k))  # pdf页 -> 印刷页（保留首个）

    grade = b["cap"].grade
    doc = fitz.open(b["path"])
    nav = []
    try:
        chapters = [e for e in b["toc"] if e.level <= ml and e.pdf_start]
        for e in chapters:
            mode_text = grade in ("T", "S")
            mode_img = b["cap"].has_images and render_images != "none"
            pages = None
            if mode_text:
                pages = ext_m.chapter_pages(doc, e, band)
            images = []
            if mode_img:
                images = rnd_m.bake_chapter_images(doc, e, bg / "img" / e.id, width=img_width, quality=72)
            slug = slugch(e)
            _write_chapter(b, e, bg / "ch", pages, images, mode_text, mode_img, slug, p2p)
            nav.append({"id": e.id, "level": e.level, "title": e.title, "url": f"{slug}.html"})
    finally:
        doc.close()
    book = {k: b[k] for k in ("id", "title_de", "title_zh", "group", "cap", "toc")}
    book["nav"] = nav
    (bg / "data.js").write_text(f"window.BOOK = {dumps(book)};", encoding="utf-8")
    _write_book_page(b, chapters, bg)


def _nav_html(b: dict, back: str) -> str:
    return (f'<nav class="bar"><a href="../../../index.html">首页</a>'
            f'<a href="../index.html">卷页</a><span style="color:var(--muted)">{escape(b.get("title_de") or b["cap"].id)}</span></nav>')


def _write_chapter(b, ch, ch_dir: Path, pages, images: list, mode_text: bool, mode_img: bool, slug: str, p2p) -> None:
    ch_dir.mkdir(parents=True, exist_ok=True)
    title = escape(ch.title)
    tabs = []
    if mode_text:
        tabs.append('<button data-tab="text" class="on">文本</button>')
    if mode_img:
        tabs.append('<button data-tab="img">原稿</button>')
    if mode_text and mode_img:
        tabs.append('<button data-tab="dual">对照</button>')
    img_html = "".join(f'<img class="leaf" loading="lazy" src="../img/{ch.id}/p{i:05d}.webp" alt="页 {i}">'
                       for i in images)
    imgset = set(images)
    text_html = ""
    dual_html = ""
    if pages:
        for pdf, hdr, body, fn in pages:
            pr = p2p.get(pdf)
            lbl = f"S. {pr}" if pr else f"PDF页 {pdf}"
            label = f'<span class="pg" id="s{pdf}">[{lbl}]</span>'
            hdr_html = f'<aside class="fn hdr" data-pdf="{pdf}">{escape(hdr)}</aside>' if hdr else ""
            fn_html = f'<aside class="fn" data-pdf="{pdf}">{fn}</aside>' if fn else ""
            text_html += label + hdr_html + body + fn_html
            if pdf in imgset:
                dual_html += (f'<div class="dualrow"><div class="dtext">{label}{hdr_html}{body}{fn_html}</div>'
                              f'<div class="dimg"><img loading="lazy" src="../img/{ch.id}/p{pdf:05d}.webp" alt="页 {pdf}"></div></div>')
    text_html = text_html or ('<p style="color:var(--muted)">(本卷无文字层)</p>' if mode_text else "")
    prev_next = ""
    (ch_dir / f"{slug}.html").write_text(
        f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
        f'<title>{title}</title><link rel="stylesheet" href="../../../assets/css/site.css">'
        f'<script src="../data.js"></script></head><body data-ch="{ch.id}">'
        f'<nav class="bar"><a href="../../../index.html">首页</a><a href="../index.html">卷页</a>'
        f'<span style="color:var(--muted)">{escape(b.get("title_de") or "")[:40]}</span></nav>'
        f'<main><h2>{title} <small style="color:var(--muted)">S.{ch.print_start or "–"}</small></h2>'
        f'<div class="tabs">{"".join(tabs)}</div>'
        f'<section class="list tab-text">{text_html}</section>'
        f'<section class="list tab-img hidden">{img_html}</section></main>'
        f'<section class="list tab-dual hidden dual-wide">{dual_html}</section>'
        f'<div class="pgv"><a href="../index.html">← 卷目录</a>'
        f'<span class="pnbar"><a id="pgPrev" href="#">上一章</a><a id="pgNext" href="#">下一章</a></span>'
        f'<span class="pgrange">{ch.pdf_start or ""}-{ch.pdf_end or ""}</span></div>'
        f'<script src="../../../assets/js/app.js"></script>'
        f'<script src="../../../assets/js/search.js"></script></body></html>',
        encoding="utf-8")


def slugch(ch) -> str:
    s = slugify(ch.title, 30) or f"ch{ch.id}"
    return f"{ch.id}-{s}"


def _write_book_page(b: dict, chapters: list, bg: Path) -> None:
    rows = "".join(f'<li><lvl>L{e.level}</lvl><a href="ch/{slugch(e)}.html">{escape(e.title)}</a>'
                   f'<span style="color:var(--muted);margin-left:auto">S.{e.print_start or "-"}</span></li>'
                   for e in chapters)
    cap = b["cap"]
    bg.joinpath("index.html").write_text(
        f'<!doctype html><html lang="zh"><head><meta charset="utf-8">'
        f'<title>{escape(b.get("title_de") or b["id"])}</title>'
        f'<link rel="stylesheet" href="../../assets/css/site.css">'
        f'<script src="data.js"></script></head><body>'
        f'<nav class="bar"><a href="../../index.html">首页</a><a href="../../grp/{slugify(_group(b), 40)}.html">分组</a></nav>'
        f'<main><h2>{escape(b.get("title_de") or "")}</h2>'
        f'<p style="color:var(--muted)">{cap.grade} 级 · {cap.pages} 页 · 约 {round(cap.chars_per_page)} 字符/页'
        f' · 书签 {"有" if cap.has_bookmarks else "无"}</p>'
        f'<h3>章节目录</h3><ul class="toc">{rows}</ul></main>'
        f'<script src="../../assets/js/search.js"></script></body></html>',
        encoding="utf-8")


def _write_index(out: Path, books: list, groups: dict) -> None:
    cards = "".join(
        f'<a class="gcard" href="grp/{slugify(g, 40)}.html"><h3>{escape(g)}</h3><span>{len(vs)} 卷</span></a>'
        for g, vs in groups.items())
    tot_pg = sum(b["cap"].pages for b in books)
    out.joinpath("index.html").write_text(
        f'<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>PDF 静态阅读站</title>'
        f'<link rel="stylesheet" href="assets/css/site.css"></head><body>'
        f'<main><h1>PDF 语料 · 静态章节阅读站</h1>'
        f'<p style="color:var(--muted)">共 {len(books)} 卷 · {tot_pg} 页</p>'
        f'<div class="cards">{cards}</div></main>'
        f'<script src="assets/js/app.js"></script></body></html>',
        encoding="utf-8")


def _write_groups(out: Path, groups: dict) -> None:
    for g, vs in groups.items():
        items = "".join(f'<li><a href="../books/{v["cap"].id}/index.html">{escape(v.get("title_de") or v["cap"].id)}</a>'
                        f'<span style="color:var(--muted)"> {v["cap"].grade} · {v["cap"].pages}p</span></li>'
                        for v in sorted(vs, key=lambda x: x["cap"].id))
        p = out / "grp" / f"{slugify(g, 40)}.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f'<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>{escape(g)}</title>'
            f'<link rel="stylesheet" href="../assets/css/site.css"></head><body>'
            f'<nav class="bar"><a href="../index.html">← 首页</a></nav>'
            f'<main><h1>{escape(g)}</h1><ul class="toc">{items}</ul></main></body></html>',
            encoding="utf-8")


def _write_search(out: Path, books: list) -> None:
    rows = []
    for b in books:
        for e in [x for x in b["toc"] if x.level <= 3]:
            rows.append({"b": b["cap"].id, "c": b.get("title_de") or b["cap"].id, "t": e.title,
                         "id": e.id, "s": e.print_start})
    (out / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "js" / "search-data.js").write_text(
        f"window.SEARCH = {json.dumps(rows, ensure_ascii=False)};", encoding="utf-8")
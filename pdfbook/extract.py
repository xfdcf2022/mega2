# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from html import escape

import pymupdf as fitz

from .model import TocEntry


def page_header(page, band: float = 0.12) -> str:
    """取页眉（顶部 y<12% 的文本块合并成一行），无则返回空串。"""
    h = page.rect.height if page.rect.height else 842
    blocks = [b for b in page.get_text("blocks")
              if (b[4] or "").strip() and b[3] < h * band]
    blocks.sort(key=lambda b: (b[1], b[0]))
    return " ".join(re.sub(r"\s+", " ", b[4]).strip() for b in blocks).strip()


def chapter_pages(doc: fitz.Document, e: TocEntry, footnote_band: float = 0.72) -> list:
    """逐页返回 (pdf页码, 页眉, 正文本体HTML, 脚注HTML)，供文本/对照面板使用。"""
    out = []
    for i in range(e.pdf_start - 1, (e.pdf_end or e.pdf_start)):
        if not 0 <= i < doc.page_count:
            continue
        body, fns, hdr = _split_page(doc[i], footnote_band)
        out.append((i + 1, hdr, body, fns))
    return out


def chapter_html(doc: fitz.Document, e: TocEntry, footnote_band: float = 0.72) -> str:
    parts = []
    for pdf, hdr, body, fns in chapter_pages(doc, e, footnote_band):
        parts.append(f'<span class="pg" id="s{pdf}">[PDF页 {pdf}{" · " + hdr if hdr else ""}]</span>{body}')
        if fns:
            parts.append(f'<aside class="fn" data-pdf="{pdf}">{fns}</aside>')
    return "<article>" + "\n".join(parts) + "</article>"


def pdf_label(i: int) -> int:
    return i + 1


def _split_page(page, band, hband: float = 0.12):
    h = page.rect.height if page.rect.height else 842
    cut = h * hband
    body, fns, hdrs = [], [], []
    for b in sorted(page.get_text("blocks"), key=lambda b: (b[1], b[0])):
        _x0, y0, _x1, y1, txt, *_ = b
        txt = escape((txt or "").strip())
        if not txt:
            continue
        line = re.sub(r"\s*\n\s*", " ", txt)
        if y0 > h * band:
            fns.append(txt.replace("\n", "<br>"))
        elif y1 < cut:
            hdrs.append(line)
        else:
            body.append(line)
    bhtml = "".join(f"<p>{t}</p>" for t in body)
    fhtml = "".join(f"<p>{t}</p>" for t in fns)
    hhtml = " ".join(hdrs)
    return bhtml, fhtml, hhtml
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pymupdf as fitz

from PIL import Image

from .model import TocEntry

WHITE_CUT = 220
MID_LO, MID_HI = 80, 220
BIN_THRESH = 160


def _page_is_printed(im) -> bool:
    h = im.histogram()
    t = sum(h) or 1
    return sum(h[WHITE_CUT:]) / t > 0.60 and sum(h[MID_LO:MID_HI]) / t < 0.30


def bake_chapter_images(doc: fitz.Document, e: TocEntry, img_dir: Path,
                        width: int = 1500, quality: int = 72) -> list:
    """把一章的 PDF 页渲染为 WebP 页图：印刷页→1-bit 无损、灰调页→灰度 q75。已存在则跳过。"""
    pages = list(range(e.pdf_start, (e.pdf_end or e.pdf_start) + 1))
    want = {f"p{i:05d}.webp" for i in pages}
    if img_dir.is_dir():
        have = {f.name for f in img_dir.iterdir() if f.suffix == ".webp"}
        if want <= have:
            return pages
    img_dir.mkdir(parents=True, exist_ok=True)
    for pn in pages:
        i = pn - 1
        if not 0 <= i < doc.page_count:
            continue
        page = doc[i]
        r = page.rect
        z = width / r.width if r.width else 1
        pix = page.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csGRAY)
        im = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        out = img_dir / f"p{i + 1:05d}.webp"
        if _page_is_printed(im):
            im.point(lambda v: 255 if v > BIN_THRESH else 0, "1").save(
                out, "WEBP", lossless=True)
        else:
            im.save(out, "WEBP", quality=75)
    return pages
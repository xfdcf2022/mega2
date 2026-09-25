# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import subprocess
import tempfile

import pymupdf as fitz


def render_png(doc: fitz.Document, page: int, dpi: int = 300) -> str:
    pix = doc[page].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72),
                               colorspace=fitz.csGRAY)
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.write(fd, pix.tobytes("png"))
    os.close(fd)
    return tmp


class TesseractBackend:
    def __init__(self, lang: str = "deu+deu_frak", psm: str = "6"):
        self.lang, self.psm = lang, psm

    def page(self, doc: fitz.Document, page: int) -> str:
        img = render_png(doc, page)
        try:
            r = subprocess.run(
                ["tesseract", img, "-", "-l", self.lang, "--psm", self.psm],
                capture_output=True, text=True)
            return r.stdout or ""
        finally:
            os.unlink(img)


def get_backend(kind: str = "tesseract", **kw):
    if kind == "tesseract":
        return TesseractBackend(**kw)
    if kind == "mineru":
        raise NotImplementedError("MinerU 适配器预留：需磁盘红线 + WER 验证闸门")
    raise ValueError(kind)
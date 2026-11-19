# -*- coding: utf-8 -*-
"""Compose le rapport au format PDF selon la charte graphique de Md_ref.

Le contenu provient exclusivement du DOCUMENT 1
(Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_...).
"""
import json
import os

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

import mdrev_style as S
from mdrev_engine import (register_fonts, Metrics, Layout, header, footer, h1,
                          draw_text, draw_text_right, draw_text_center, rule,
                          col, REG, BOLD)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "livrables",
                   "Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.pdf")

register_fonts()
M = Metrics()
L = Layout(M)

LEADER_END = S.RIGHT_COL - 26.1
TOP_FLOW = 84.0
TOC_TOP = 88.8


# --------------------------------------------------------------------------
class Doc:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(S.PAGE_W, S.PAGE_H))
        self.page = 0

    def blank_page(self):
        self.page += 1

    def page_with_frame(self, label, numbered=True, bookmark=None):
        if self.page:
            self.c.showPage()
        self.page += 1
        header(self.c, label)
        if numbered:
            footer(self.c, self.page)
        if bookmark:
            key = "p%d" % self.page
            self.c.bookmarkPage(key)
            self.c.addOutlineEntry(bookmark, key, level=0, closed=False)


# --------------------------------------------------------------------------
# Couverture
# --------------------------------------------------------------------------
def page_cover(c):
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, S.PAGE_W, S.PAGE_H, stroke=0, fill=1)

    c.setFillColor(col(S.NAVY))
    c.rect(0, S.PAGE_H - 29, S.PAGE_W, 29, stroke=0, fill=1)

    y = S.PAGE_H - 72.6
    draw_text(c, S.MARGIN_L, y, S.ORG, REG, S.S_COVER_ROW, S.NAVY, S.CS_COVER)
    draw_text_right(c, S.RIGHT_COL, y, "FHI 360 — PROJET EpiC RDC", REG, S.S_COVER_ROW,
                    S.NAVY, S.CS_COVER)

    title = DATA["cover_title"]
    size = S.S_COVER_TITLE
    lines = L.wrap(title, REG, size, S.CONTENT_W - 10)
    while len(lines) > 6 and size > 21:
        size -= 0.5
        lines = L.wrap(title, REG, size, S.CONTENT_W - 10)
    leading = size * 1.26
    block_h = leading * (len(lines) - 1)
    top = 372.0 - block_h / 2.0
    base = S.PAGE_H - (top + M.top(size))
    for words in lines:
        draw_text_center(c, S.PAGE_W / 2.0, base, " ".join(words), REG, size, S.BLACK)
        base -= leading

    # bloc institutionnel : logos issus du document source
    items = [("logo_usa_w.png", 21.0), ("logo_epic_w.png", 20.0), ("logo_ichess_w.png", 24.0)]
    dims = []
    for fn, h in items:
        im = Image.open(os.path.join(ROOT, "assets", fn))
        dims.append((fn, h * im.width / im.height, h))
    gap = 30.0
    total_w = sum(w for _, w, _ in dims) + gap * (len(dims) - 1)
    x = (S.PAGE_W - total_w) / 2.0
    ytop = 640.0
    for fn, w, h in dims:
        c.drawImage(os.path.join(ROOT, "assets", fn), x, S.PAGE_H - ytop - h, w, h)
        x += w + gap

    rule(c, 782.0, width=0.75, color=S.NAVY)
    draw_text(c, S.MARGIN_L, S.PAGE_H - 772.2, DATA["cover_place"].upper(), REG,
              S.S_COVER_ROW, S.NAVY, S.CS_COVER)
    draw_text_right(c, S.RIGHT_COL, S.PAGE_H - 772.2, "ICHESS, LLC", REG,
                    S.S_COVER_ROW, S.NAVY, S.CS_COVER)


# --------------------------------------------------------------------------
def page_section(c, block, page_no):
    key = "sec%d" % page_no
    c.bookmarkPage(key)
    c.addOutlineEntry(block["title"], key, level=0, closed=False)
    header(c, block["eyebrow"])
    footer(c, page_no)
    h1(c, block["title"].upper())
    y = S.BODY_TOP
    for p in block["paras"]:
        y = L.draw_justified(c, p, y)
        y += S.PARA_GAP
    y += 31.0
    draw_text(c, 231.8, S.PAGE_H - (y + M.top(10.6)), block["signature"][0], BOLD, 10.6, S.NAVY)
    draw_text(c, 231.8, S.PAGE_H - (y + M.top(10.6) + 15.2), block["signature"][1], REG, 9.4, S.GREY)


# --------------------------------------------------------------------------
# Table des matieres : pagination calculee
# --------------------------------------------------------------------------
TOC_SPEC = {
    0: dict(size=S.S_TOC_L0, font=BOLD, x=S.MARGIN_L, pitch=30.1, before=0.0),
    1: dict(size=S.S_TOC_CH, font=BOLD, x=85.5, pitch=24.6, before=11.6),
    2: dict(size=S.S_TOC_SEC, font=REG, x=97.5, pitch=23.6, before=0.0),
}


def toc_layout():
    rows = []
    y = TOC_TOP
    prev = None
    for level, num, title, page in DATA["toc"]:
        spec = TOC_SPEC[level]
        if prev is not None:
            if level == 1:
                y += spec["before"]
            elif level == 2 and prev == 1:
                y += 1.2
            elif level == 2 and prev == 0:
                y += 9.0
        lines = L.wrap(title, spec["font"], spec["size"], LEADER_END - spec["x"] - 4)
        rows.append(dict(level=level, num=num, title=title, page=page, y=y,
                         lines=len(lines), size=spec["size"], font=spec["font"], x=spec["x"]))
        y += spec["pitch"] + (len(lines) - 1) * (spec["size"] * 1.42)
        prev = level
    return rows


def draw_toc_row(c, row):
    if row["level"] == 0:
        L.draw_entry(c, row["y"], "", row["title"], row["page"], title_x=S.MARGIN_L,
                     title_font=BOLD, title_size=S.S_TOC_L0, page_font=S.S_TOC_L0_PAGE)
    elif row["level"] == 1:
        L.draw_entry(c, row["y"], row["num"], row["title"], row["page"], num_x=S.MARGIN_L,
                     num_font=BOLD, num_size=S.S_TOC_CH, num_color=S.NAVY, title_x=85.5,
                     title_font=BOLD, title_size=S.S_TOC_CH, title_color=S.NAVY,
                     page_font=S.S_TOC_CH_PAGE)
    else:
        L.draw_entry(c, row["y"], row["num"], row["title"], row["page"], num_x=65.5,
                     title_x=97.5, title_font=REG, title_size=S.S_TOC_SEC,
                     page_font=S.S_TOC_SEC_PAGE)


def pages_toc(doc):
    rows = toc_layout()
    pages = [[]]
    limit = 782.0
    for row in rows:
        bottom = row["y"] + (row["lines"] - 1) * (row["size"] * 1.42)
        if bottom > limit:
            pages.append([])
            # recaler relativement au haut de la nouvelle page
            delta = row["y"] - TOC_TOP
            for r in rows[rows.index(row):]:
                r["y"] -= delta
            row["y"] = TOC_TOP
        pages[-1].append(row)
    for i, page_rows in enumerate(pages):
        doc.page_with_frame("TABLE DES MATIÈRES",
                            bookmark="Table des matières" if i == 0 else None)
        for row in page_rows:
            draw_toc_row(doc.c, row)
    return len(pages)


# --------------------------------------------------------------------------
# Listes des figures / tableaux / annexes
# --------------------------------------------------------------------------
LIST_X = S.MARGIN_L + 14.0


LIST_TEXT_W = LEADER_END - LIST_X - 4 - 20.0


def list_entry_h(title, label=""):
    lines = L.wrap(("%s %s" % (label, title)).strip(), REG, S.S_LIST, LIST_TEXT_W)
    return len(lines), (len(lines) - 1) * 13.3


def draw_list_entry(c, y, label, title, page, size=S.S_LIST, page_size=S.S_LIST_PAGE):
    base = S.PAGE_H - (y + M.top(size))
    if page:
        draw_text_right(c, S.RIGHT_COL, S.PAGE_H - (y + M.top(page_size)), page, BOLD,
                        page_size, S.NAVY)
    lines = L.wrap(("%s %s" % (label, title)).strip(), REG, size, LIST_TEXT_W)
    for i, words in enumerate(lines):
        line = " ".join(words)
        yy = base - i * 13.3
        draw_text(c, LIST_X, yy, line, REG, size, S.BLACK)
        if i == len(lines) - 1 and page:
            start = LIST_X + pdfmetrics.stringWidth(line, REG, size) + 4
            if start < LEADER_END:
                c.saveState()
                c.setStrokeColor(col(S.LEADER))
                c.setLineWidth(0.9)
                c.setDash(0.9, 2.0)
                c.line(start, yy + 0.6, LEADER_END, yy + 0.6)
                c.restoreState()
    return (len(lines) - 1) * 13.3


def draw_list_heading(c, y, label):
    draw_text(c, S.MARGIN_L, S.PAGE_H - (y + M.top(S.S_H1)), label, BOLD, S.S_H1, S.NAVY)
    rule(c, y + 18.0, width=0.9, color=S.NAVY)
    return y + 18.0 + 18.2


def pages_lists(doc):
    sections = [
        ("LISTE DES FIGURES", [(("Figure %d:" % i), t, p) for i, (t, p) in
                               enumerate(DATA["figures"], start=1)]),
        ("LISTE DES TABLEAUX", [(("Tableau %d:" % i), t, p) for i, (t, p) in
                                enumerate(DATA["tables"], start=1)]),
        ("TABLEAUX DES ANNEXES", [(("Tableau %s:" % code), t, p) for code, t, p in
                                  DATA["annex_tables"]]),
    ]

    items = []
    for si, (label, rows) in enumerate(sections):
        items.append(dict(kind="head", label=label,
                          h=(36.2 + (16.0 if si else 0.0))))
        for lab, title, pg in rows:
            nlines, extra = list_entry_h(title, lab)
            items.append(dict(kind="entry", label=lab, title=title, page=pg,
                              h=18.4 + extra))

    usable = S.BOTTOM_LIMIT - TOP_FLOW
    pages = []
    cur, acc = [], 0.0
    for it in items:
        need_break = False
        if cur and acc + it["h"] > usable:
            need_break = True
        elif cur and acc > usable - 26 and it["kind"] == "head":
            # eviter un titre de liste seul en bas de page
            need_break = True
        if need_break:
            pages.append(cur)
            cur, acc = [], 0.0
        cur.append(it)
        acc += it["h"]
    if cur:
        pages.append(cur)

    first = True
    for pi, page_items in enumerate(pages):
        doc.page_with_frame("LISTE DES FIGURES ET TABLEAUX",
                            bookmark="Liste des figures et tableaux" if pi == 0 else None)
        y = S.CONTENT_TOP if first else TOP_FLOW
        first = False
        for it in page_items:
            if it["kind"] == "head":
                if y > S.CONTENT_TOP + 1:
                    y += 16.0
                y = draw_list_heading(doc.c, y, it["label"])
            else:
                draw_list_entry(doc.c, y, it["label"], it["title"], it["page"])
                y += 18.4 + list_entry_h(it["title"], it["label"])[1]
    return len(pages)


# --------------------------------------------------------------------------
# Abreviations
# --------------------------------------------------------------------------
def draw_abbrev_header(c, y_top):
    c.setFillColor(col(S.NAVY))
    c.rect(S.MARGIN_L, S.PAGE_H - y_top - S.TBL_HEAD_H, S.CONTENT_W, S.TBL_HEAD_H,
           stroke=0, fill=1)
    base = S.PAGE_H - (y_top + 16.6)
    draw_text(c, S.TBL_COL1_X, base, "SIGLE", BOLD, S.S_TBL_HEAD, S.WHITE, 0.55)
    draw_text(c, S.TBL_COL2_X, base, "SIGNIFICATION", BOLD, S.S_TBL_HEAD, S.WHITE, 0.55)
    return y_top + S.TBL_HEAD_H


def draw_abbrev_rows(c, y_top, rows, start_index):
    y = y_top
    for i, (sigle, definition) in enumerate(rows):
        if (start_index + i) % 2 == 1:
            c.setFillColor(col(S.TINT))
            c.rect(S.MARGIN_L, S.PAGE_H - y - S.TBL_ROW_H, S.CONTENT_W, S.TBL_ROW_H,
                   stroke=0, fill=1)
        base = S.PAGE_H - (y + 14.0)
        draw_text(c, S.TBL_COL1_X, base, sigle, BOLD, S.S_TBL, S.NAVY)
        draw_text(c, S.TBL_COL2_X, base, definition, REG, S.S_TBL, S.BLACK)
        y += S.TBL_ROW_H
    return y


def pages_abbrev(doc):
    rows = DATA["abbrev"]
    per_page = 37
    chunks = [rows[i:i + per_page] for i in range(0, len(rows), per_page)]
    for p, chunk in enumerate(chunks):
        doc.page_with_frame("ABRÉVIATIONS ET ACRONYMES",
                            bookmark="Abréviations et acronymes" if p == 0 else None)
        y = draw_abbrev_header(doc.c, 72.0)
        draw_abbrev_rows(doc.c, y, chunk, p * per_page)
    return len(chunks)


# --------------------------------------------------------------------------
def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = Doc(OUT)
    c = doc.c
    c.setTitle(DATA["cover_title"])
    c.setAuthor("ICHESS, LLC")
    c.setSubject("Diagnostic opérationnel rapide des établissements de santé – RDC")
    c.setCreator("ICHESS, LLC")

    doc.blank_page()
    c.bookmarkPage("cover")
    c.addOutlineEntry("Couverture", "cover", level=0, closed=False)
    page_cover(c)

    c.showPage()
    doc.page = 1
    page_section(c, DATA["preface"], 2)
    doc.page = 2
    c.showPage()
    page_section(c, DATA["remerciements"], 3)
    doc.page = 3

    pages_toc(doc)
    pages_lists(doc)
    pages_abbrev(doc)

    c.save()
    print("PDF :", OUT, "|", doc.page, "pages")


if __name__ == "__main__":
    build()

# -*- coding: utf-8 -*-
"""Rendu de controle du fichier DOCX (aperçu de pagination) avec la police du modele.

LibreOffice n'etant pas disponible dans cet environnement, ce module redessine
le DOCX page par page a partir de sa structure OOXML (styles de paragraphe,
tabulations, tableaux, images) pour permettre un controle visuel.
"""
import json
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import Color, HexColor
from docx.shared import Emu

import mdrev_style as S
from mdrev_engine import register_fonts, Metrics, Layout, REG, BOLD

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TWIP = 1.0 / 20.0      # twips -> points
EMU_PT = 1.0 / 12700.0

register_fonts()
MET = Metrics()


def color_of(rgb):
    if rgb is None:
        return S.BLACK
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def get(el, path, default=None):
    if el is None:
        return default
    v = el.find(qn(path))
    if v is None:
        return default
    return v


class Renderer:
    def __init__(self, docx_path, out_path):
        self.doc = Document(docx_path)
        self.c = canvas.Canvas(out_path, pagesize=(S.PAGE_W, S.PAGE_H))
        self.page_no = 0
        self.y = 0.0
        sec = self.doc.sections[0]
        self.ml = sec.left_margin.pt
        self.mr = sec.right_margin.pt
        self.mt = sec.top_margin.pt
        self.mb = sec.bottom_margin.pt
        self.hdr_dist = sec.header_distance.pt
        self.ftr_dist = sec.footer_distance.pt
        self.cw = S.PAGE_W - self.ml - self.mr
        self.section_label = ""
        self.section_idx = 0
        self.header_on = False
        self.page_start = 1
        self.cover_mode = True
        self.new_page(first=True)

    # ---------------------------------------------------------------
    def new_page(self, first=False):
        if not first:
            if not self.cover_mode:
                self.draw_footer()
            self.c.showPage()
        self.page_no += 1
        self.y = 0.0 if self.cover_mode else self.mt
        if self.header_on and not self.cover_mode:
            self.draw_header()

    def draw_header(self):
        base = S.PAGE_H - 0
        y = S.PAGE_H - (self.hdr_dist + 7.2)
        self.text(self.ml, y, "I C H E S S ,  L L C" if False else "ICHESS, LLC", 7, True,
                  S.NAVY, 1.3)
        label = self.section_label
        w = pdfmetrics.stringWidth(label, REG, 7) + 1.3 * len(label)
        self.text(S.PAGE_W - self.mr - w, y, label, 7, False, S.GREY, 1.3)
        yy = y - 4.5
        self.line(self.ml, yy, S.PAGE_W - self.mr, yy, S.RULE_GREY, 0.5)

    def draw_footer(self):
        label = "%02d" % (self.page_no + self.page_start - 1)
        w = pdfmetrics.stringWidth(label, BOLD, 8) + 2.1 * len(label)
        self.text((S.PAGE_W - w) / 2.0, self.ftr_dist + 4, label, 8, True, S.NAVY, 2.1)

    def text(self, x, baseline, s, size, bold, color, spacing=0.0):
        t = self.c.beginText(x, baseline)
        t.setFont(BOLD if bold else REG, size)
        t.setFillColor(Color(*color))
        t.setCharSpace(spacing)
        t.textOut(s)
        self.c.drawText(t)

    def line(self, x0, y, x1, y2, color, width):
        self.c.saveState()
        self.c.setStrokeColor(Color(*color))
        self.c.setLineWidth(width)
        self.c.line(x0, y, x1, y2)
        self.c.restoreState()

    # ---------------------------------------------------------------
    def run(self):
        body = self.doc.element.body
        for child in body.iterchildren():
            tag = child.tag.split("}")[1]
            if tag == "p":
                self.paragraph(child)
            elif tag == "tbl":
                self.table(child)
        self.draw_footer()
        self.c.save()
        return self.page_no

    # ---------------------------------------------------------------
    def paragraph(self, p_el):
        from docx.text.paragraph import Paragraph
        p = Paragraph(p_el, self.doc)
        pf = p.paragraph_format

        # saut de page explicite
        if pf.page_break_before:
            self.new_page()

        before = pf.space_before.pt if pf.space_before is not None else 0
        after = pf.space_after.pt if pf.space_after is not None else 0
        line = pf.line_spacing
        line = line.pt if hasattr(line, "pt") else None
        left = pf.left_indent.pt if pf.left_indent is not None else 0.0
        right = pf.right_indent.pt if pf.right_indent is not None else 0.0
        first = pf.first_line_indent.pt if pf.first_line_indent is not None else 0.0

        ppr = p_el.find(qn("w:pPr"))
        if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
            # fin de section : la suivante demarre sur une nouvelle page
            if self.cover_mode:
                self.cover_mode = False
                self.header_on = True
                self.section_idx = 1
                self.mt = self.doc.sections[1].top_margin.pt
                self.mb = self.doc.sections[1].bottom_margin.pt
                self.section_label = self.doc.sections[1].header.paragraphs[0].text.split("\t")[-1]
            else:
                self.section_idx += 1
                if self.section_idx < len(self.doc.sections):
                    self.section_label = self.doc.sections[self.section_idx].header.paragraphs[0].text.split("\t")[-1]
            self.new_page()
            return
        bg = None
        if ppr is not None:
            shd = ppr.find(qn("w:shd"))
            if shd is not None:
                bg = shd.get(qn("w:fill"))
        borders = ppr.find(qn("w:pBdr")) if ppr is not None else None
        top_border = borders.find(qn("w:top")) if borders is not None else None
        bottom_border = borders.find(qn("w:bottom")) if borders is not None else None

        # collecte des runs
        fonts = []
        has_break = False
        for r in p.runs:
            if r._r.findall(qn("w:br")):
                has_break = True
            txt = r.text
            size = r.font.size.pt if r.font.size is not None else 10
            bold = bool(r.font.bold)
            col = color_of(r.font.color.rgb if r.font.color and r.font.color.rgb else None)
            rpr = r._r.find(qn("w:rPr"))
            spacing = 0.0
            if rpr is not None:
                sp = rpr.find(qn("w:spacing"))
                if sp is not None:
                    spacing = int(sp.get(qn("w:val"))) * TWIP
            pics = r._r.findall(qn("w:drawing"))
            fonts.append((txt, size, bold, col, spacing, pics))

        if has_break and all(not f[0].strip() for f in fonts):
            if self.y > self.mt + 1:
                self.new_page()
            else:
                self.new_page()
            return

        text = "".join(f[0] for f in fonts)
        if not text.strip() and not any(f[5] for f in fonts):
            if bg:
                # bandeau plein bord
                h = line or 10
                self.c.setFillColor(HexColor("#" + bg))
                self.c.rect(0, S.PAGE_H - self.y - h, S.PAGE_W, h, stroke=0, fill=1)
                self.y += h
            else:
                self.y += before + (line or 10) + after
            return

        size = fonts[0][1]
        bold = fonts[0][2]
        col = fonts[0][3]
        spacing = fonts[0][4]

        if self.y + before + (line or size * 1.4) > S.PAGE_H - self.mb:
            self.new_page()
        self.y += before

        # case de la couverture avec image
        pics = [pp for f in fonts for pp in f[5]]

        x0 = self.ml + left
        width = self.cw - left - right
        align = p.alignment
        rule_h = line or size * 1.35

        if top_border is not None:
            self.line(x0, S.PAGE_H - self.y + 4, x0 + width, S.PAGE_H - self.y + 4,
                      S.NAVY, 0.75)

        if pics:
            total_w = 0.0
            hmax = 0.0
            for pp in pics:
                ext = pp.find(".//" + qn("wp:extent"))
                cx = int(ext.get("cx")) * EMU_PT
                cy = int(ext.get("cy")) * EMU_PT
                total_w += cx
                hmax = max(hmax, cy)
            x = x0 + (width - total_w) / 2.0
            for pp in pics:
                ext = pp.find(".//" + qn("wp:extent"))
                cx = int(ext.get("cx")) * EMU_PT
                cy = int(ext.get("cy")) * EMU_PT
                self.c.setFillColor(HexColor("#EEEEEE"))
                self.c.rect(x, S.PAGE_H - self.y - cy, cx, cy, stroke=0, fill=1)
                x += cx
            self.y += hmax + 5
            return

        # tabulations
        stops = []
        if pf.tab_stops:
            for st in pf.tab_stops:
                stops.append((st.position.pt, st.alignment, st.leader))
        stops = [s for s in stops if s[0] is not None]

        segments = text.split("\t")
        base = S.PAGE_H - (self.y + MET.top(size))
        font = BOLD if bold else REG
        natural = pdfmetrics.stringWidth(text, font, size) + spacing * len(text)
        if natural > width and "\t" not in text:
            lines = Layout(MET).wrap(text, font, size, width)
            for i, words in enumerate(lines):
                line = " ".join(words)
                yy = base - i * rule_h
                if self.y + rule_h * (i + 1) > S.PAGE_H - self.mb:
                    self.new_page()
                    base = S.PAGE_H - (self.y + MET.top(size))
                    yy = base
                ln = line
                if align == WD_ALIGN_PARAGRAPH.JUSTIFY and i < len(lines) - 1:
                    self.justify(ln, yy, x0, width, size, bold, col)
                else:
                    self.text(x0, yy, ln, size, bold, col, spacing)
            self.y += rule_h * len(lines) + after
            return

        if align == WD_ALIGN_PARAGRAPH.CENTER:
            total = pdfmetrics.stringWidth(text, BOLD if bold else REG, size) + spacing * len(text)
            self.text(x0 + (width - total) / 2.0, base, text, size, bold, col, spacing)
        elif align == WD_ALIGN_PARAGRAPH.JUSTIFY:
            self.justify(text, base, x0, width, size, bold, col)
        else:
            font = BOLD if bold else REG
            cursor = x0
            left_tabs = sorted([st[0] for st in stops if st[1] == 0])
            right_tabs = sorted([st[0] for st in stops if st[1] == 2])
            for i, seg in enumerate(segments):
                w = pdfmetrics.stringWidth(seg, font, size) + spacing * len(seg)
                if i == 0:
                    self.text(cursor, base, seg, size, bold, col, spacing)
                    cursor += w
                    continue
                nxt_left = [t for t in left_tabs if x0 + t > cursor + 0.5]
                if nxt_left:
                    pos = x0 + nxt_left[0]
                    self.text(pos, base, seg, size, bold, col, spacing)
                    cursor = pos + w
                    left_tabs.remove(nxt_left[0])
                    continue
                if right_tabs:
                    pos = x0 + right_tabs[-1]
                    self.dotted(cursor + 3, base + 0.8, pos - w - 3)
                    self.text(pos - w, base, seg, size, bold, col, spacing)
                    cursor = pos
                else:
                    self.text(cursor, base, seg, size, bold, col, spacing)
                    cursor += w

        if bg and text.strip() and len(text.strip()) < 3:
            self.c.setFillColor(HexColor("#" + bg))
            self.c.rect(0, S.PAGE_H - self.y - rule_h, S.PAGE_W, rule_h, stroke=0, fill=1)

        self.y += rule_h + after
        if bottom_border is not None:
            self.line(x0, S.PAGE_H - self.y + 2, x0 + width, S.PAGE_H - self.y + 2,
                      S.NAVY, 0.55)

    def justify(self, text, base, x0, width, size, bold, col):
        font = BOLD if bold else REG
        words = text.split(" ")
        if len(words) == 1:
            self.text(x0, base, text, size, bold, col)
            return
        nat = sum(pdfmetrics.stringWidth(w, font, size) for w in words)
        space = pdfmetrics.stringWidth(" ", font, size)
        extra = max(0.0, (width - nat - space * (len(words) - 1)) / (len(words) - 1))
        xx = x0
        for w in words:
            self.text(xx, base, w, size, bold, col)
            xx += pdfmetrics.stringWidth(w, font, size) + space + extra

    def dotted(self, x0, y, x1):
        if x1 <= x0:
            return
        self.c.saveState()
        self.c.setStrokeColor(Color(*S.LEADER))
        self.c.setLineWidth(0.9)
        self.c.setDash(0.9, 2.0)
        self.c.line(x0, y, x1, y)
        self.c.restoreState()

    # ---------------------------------------------------------------
    def table(self, tbl_el):
        from docx.table import Table
        table = Table(tbl_el, self.doc)
        grid = []
        for row in table.rows:
            tr = row._tr
            h_el = tr.find(qn("w:trPr"))
            h = 18.5
            if h_el is not None:
                hh = h_el.find(qn("w:trHeight"))
                if hh is not None:
                    h = int(hh.get(qn("w:val"))) * TWIP
            cells = []
            for cell in row.cells:
                tc_pr = cell._tc.find(qn("w:tcPr"))
                fill = None
                if tc_pr is not None:
                    shd = tc_pr.find(qn("w:shd"))
                    if shd is not None:
                        fill = shd.get(qn("w:fill"))
                txt = cell.text
                bold = any(r.font.bold for p in cell.paragraphs for r in p.runs)
                colr = S.WHITE if bold and fill == "131D44" else (S.NAVY if bold else S.BLACK)
                cells.append((txt, fill, bold, colr))
            grid.append((h, cells))

        xw = [3.4 * 28.3465, 13.3 * 28.3465]
        for h, cells in grid:
            if self.y + h > S.PAGE_H - self.mb:
                self.new_page()
            for i, (txt, fill, bold, colr) in enumerate(cells):
                if fill:
                    self.c.setFillColor(HexColor("#" + fill))
                    self.c.rect(self.ml + sum(xw[:i]), S.PAGE_H - self.y - h, xw[i], h,
                                stroke=0, fill=1)
                base = S.PAGE_H - (self.y + h / 2.0 + 3.0)
                self.text(self.ml + sum(xw[:i]) + 10, base, txt, 8.5 if h < 25 else 8,
                         bold, colr, 0.55 if h >= 25 else 0.0)
            self.y += h


if __name__ == "__main__":
    src = os.path.join(ROOT, "livrables",
                       "Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.docx")
    out = os.path.join(ROOT, "work", "preview_docx.pdf")
    n = Renderer(src, out).run()
    print("apercu DOCX :", out, "|", n, "pages")

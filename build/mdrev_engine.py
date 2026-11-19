# -*- coding: utf-8 -*-
"""Moteur de composition PDF reproduisant la charte de Md_ref."""
import json
import os

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from fontTools.ttLib import TTFont as FTFont

import mdrev_style as S

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(ROOT, "fonts")
ASSET_DIR = os.path.join(ROOT, "assets")

REG, BOLD, ITAL = "GI", "GIB", "GII"


def register_fonts():
    pdfmetrics.registerFont(TTFont(REG, os.path.join(FONT_DIR, "GlacialIndifference-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD, os.path.join(FONT_DIR, "GlacialIndifference-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(ITAL, os.path.join(FONT_DIR, "GlacialIndifference-Italic.ttf")))
    pdfmetrics.registerFontFamily(REG, normal=REG, bold=BOLD, italic=ITAL, boldItalic=BOLD)


def _face(fn):
    return FTFont(os.path.join(FONT_DIR, fn))


class Metrics:
    """Hauteurs de reference (en em) pour l'alignement optique."""

    def __init__(self):
        f = _face("GlacialIndifference-Regular.ttf")
        upm = f["head"].unitsPerEm
        self.ascent = f["hhea"].ascent / upm
        self.descent = f["hhea"].descent / upm
        self.cap = f["OS/2"].sCapHeight / upm

    def top(self, size):
        """Decalage baseline -> haut optique (ascender)."""
        return self.ascent * size

    def captop(self, size):
        return self.cap * size


def col(c):
    return Color(*c)


def sw(text, font, size, cs=0.0):
    """Largeur d'une chaine, interlettrage inclus."""
    if not text:
        return 0.0
    return pdfmetrics.stringWidth(text, font, size) + cs * len(text)


def _out(c, x, baseline, text, font, size, color, cs=0.0):
    t = c.beginText(x, baseline)
    t.setFont(font, size)
    t.setFillColor(col(color))
    t.setCharSpace(cs)
    t.textOut(text)
    c.drawText(t)


def draw_text(c, x, baseline, text, font=REG, size=S.S_BODY, color=S.BLACK, cs=0.0):
    _out(c, x, baseline, text, font, size, color, cs)


def draw_text_right(c, x, baseline, text, font=REG, size=S.S_BODY, color=S.BLACK, cs=0.0):
    draw_text(c, x - sw(text, font, size, cs), baseline, text, font, size, color, cs)


def draw_text_center(c, x, baseline, text, font=REG, size=S.S_BODY, color=S.BLACK, cs=0.0):
    draw_text(c, x - sw(text, font, size, cs) / 2.0, baseline, text, font, size, color, cs)


def rule(c, y_from_top, x0=S.MARGIN_L, x1=S.RIGHT_COL, width=0.7, color=S.RULE_GREY):
    c.saveState()
    c.setStrokeColor(col(color))
    c.setLineWidth(width)
    y = S.PAGE_H - y_from_top
    c.line(x0, y, x1, y)
    c.restoreState()


class Layout:
    """Primitives de composition communes au PDF et au DOCX."""

    def __init__(self, metrics):
        self.m = metrics

    # -- retour a la ligne (sans cesure) ----------------------------------
    def wrap(self, text, font, size, width):
        words = text.split(" ")
        lines, cur = [], []
        for w in words:
            trial = " ".join(cur + [w])
            if cur and pdfmetrics.stringWidth(trial, font, size) > width:
                lines.append(cur)
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(cur)
        return lines

    def draw_justified(self, c, text, y_top, x=S.MARGIN_L, width=S.CONTENT_W,
                       font=REG, size=S.S_BODY, leading=S.LEADING_BODY,
                       color=S.BLACK, justify=True):
        lines = self.wrap(text, font, size, width)
        base = S.PAGE_H - (y_top + self.m.top(size))
        for i, words in enumerate(lines):
            last = (i == len(lines) - 1)
            if justify and not last and len(words) > 1:
                nat = sum(pdfmetrics.stringWidth(w, font, size) for w in words)
                space = pdfmetrics.stringWidth(" ", font, size)
                extra = max(0.0, (width - nat - space * (len(words) - 1)) / (len(words) - 1))
            else:
                extra = 0.0
            xx = x
            for w in words:
                _out(c, xx, base, w, font, size, color)
                xx += pdfmetrics.stringWidth(w, font, size)
                xx += pdfmetrics.stringWidth(" ", font, size) + extra
            base -= leading
        return y_top + leading * len(lines)

    # -- entree de sommaire avec points de conduite -----------------------
    def draw_entry(self, c, y_top, num, title, page,
                   num_x=S.MARGIN_L, title_x=S.MARGIN_L, page_font=S.S_TOC_SEC_PAGE,
                   title_font=REG, title_size=S.S_TOC_SEC, page_x=S.RIGHT_COL,
                   leader_limit=S.RIGHT_COL - 26.1, leader_color=S.LEADER,
                   num_color=S.BLACK, title_color=S.BLACK, num_size=None,
                   page_color=S.NAVY, num_font=None):
        num_size = num_size or title_size
        num_font = num_font or title_font
        if num:
            draw_text(c, num_x, S.PAGE_H - (y_top + self.m.top(num_size)), num,
                      num_font, num_size, num_color)
        base = S.PAGE_H - (y_top + self.m.top(title_size))
        if page:
            draw_text_right(c, page_x, S.PAGE_H - (y_top + self.m.top(page_font)),
                            page, BOLD, page_font, page_color)
        # titre sur une ou plusieurs lignes
        sub = Layout(self.m)
        lines = self.wrap(title, title_font, title_size, leader_limit - title_x - 4)
        for i, words in enumerate(lines):
            line = " ".join(words)
            yy = base - i * (title_size * 1.42)
            _out(c, title_x, yy, line, title_font, title_size, title_color)
            if i == len(lines) - 1 and page:
                start = title_x + pdfmetrics.stringWidth(line, title_font, title_size) + 4
                if start < leader_limit:
                    c.saveState()
                    c.setStrokeColor(col(leader_color))
                    c.setLineWidth(0.9)
                    c.setDash(0.9, 2.0)
                    c.line(start, yy + 0.6, leader_limit, yy + 0.6)
                    c.restoreState()
        return y_top + (len(lines) - 1) * (title_size * 1.42)


def header(c, section_label):
    draw_text(c, S.MARGIN_L, S.PAGE_H - S.HEADER_BASELINE, S.ORG, BOLD, S.S_HEADER, S.NAVY, S.CS_HEADER)
    draw_text_right(c, S.RIGHT_COL, S.PAGE_H - S.HEADER_BASELINE, section_label, REG, S.S_HEADER,
                    S.GREY, S.CS_HEADER)
    rule(c, S.HEADER_RULE_Y, width=0.7, color=S.RULE_GREY)


def footer(c, number):
    label = "0%d" % number if number < 10 else str(number)
    draw_text_center(c, S.PAGE_W / 2.0, S.PAGE_H - S.FOOTER_BASELINE, label, BOLD, 8.2,
                     S.NAVY, S.CS_PAGENUM)


def h1(c, title, y_top=S.CONTENT_TOP, with_rule=True, size=S.S_H1):
    draw_text(c, S.MARGIN_L, S.PAGE_H - (y_top + pdfmetrics.getAscent(REG, size)), title,
              BOLD, size, S.NAVY)
    if with_rule:
        rule(c, y_top + 18.0, width=0.9, color=S.NAVY)
        return y_top + 18.0
    return y_top

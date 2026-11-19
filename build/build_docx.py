# -*- coding: utf-8 -*-
"""Genere le LIVRABLE Word (DOCX) selon la charte graphique de Md_ref.

Contenu : exclusivement celui du DOCUMENT 1.
"""
import copy
import json
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Emu, Inches

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "livrables",
                   "Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.docx")

NAVY = RGBColor(0x13, 0x1D, 0x44)
GREY = RGBColor(0x6B, 0x70, 0x7D)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
NAVY_HEX = "131D44"
TINT_HEX = "FFFBF7"
LEADER_HEX = "CEE1F8"
RULE_HEX = "D9D9D9"

FONT = "Glacial Indifference"

PAGE_W = Cm(21.0)
PAGE_H = Cm(29.7)
MARGIN = Cm(2.1)
TOP_MARGIN = Cm(2.55)

CONTENT_W_PT = 476.2


# --------------------------------------------------------------------------
# Helpers XML
# --------------------------------------------------------------------------
def set_run_font(run, size=None, bold=None, color=None, spacing=None, caps=False,
                 italic=False):
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    font = run.font
    font.name = FONT
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)
    if spacing:
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:val"), str(int(round(spacing * 20))))
        rpr.append(sp)
    if caps:
        c = OxmlElement("w:caps")
        rpr.append(c)
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), "fr-FR")
    rpr.append(lang)


def para_fmt(p, before=0, after=0, line=None, align=None, left=None, right=None,
             first=None, keep_next=False, keep_lines=True, bg=None, page_break_before=False):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line:
        pf.line_spacing = Pt(line)
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    if align is not None:
        p.alignment = align
    if left is not None:
        pf.left_indent = left
    if right is not None:
        pf.right_indent = right
    if first is not None:
        pf.first_line_indent = first
    pf.keep_with_next = keep_next
    pf.keep_together = keep_lines
    pf.page_break_before = page_break_before
    ppr = p._element.get_or_add_pPr()
    if bg:
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), bg)
        ppr.append(shd)
    # cesure desactivee
    hy = OxmlElement("w:suppressAutoHyphens")
    ppr.append(hy)
    return p


def add_bottom_border(p, color=NAVY_HEX, size=6, space=6):
    ppr = p._element.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), str(space))
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.append(borders)


def add_tab_stop(p, pos_pt, align=WD_TAB_ALIGNMENT.RIGHT, leader=WD_TAB_LEADER.DOTS):
    p.paragraph_format.tab_stops.add_tab_stop(Pt(pos_pt), align, leader)


def field_run(paragraph, instr, size=8, bold=True, color=NAVY, spacing=2.1, cached="1"):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = cached
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(txt)
    run._r.append(fld_end)
    set_run_font(run, size=size, bold=bold, color=color, spacing=spacing)


def set_cell_bg(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def set_cell_margins(cell, left=0.0, right=0.0, top=0.0, bottom=0.0):
    tc_pr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for tag, val in (("w:top", top), ("w:start", left), ("w:bottom", bottom),
                     ("w:end", right)):
        el = OxmlElement(tag)
        el.set(qn("w:w"), str(int(val * 20)))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tc_pr.append(mar)


def clear_table_borders(table):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tbl_pr.append(borders)


def fixed_layout(table):
    tbl_pr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)


def set_row_height(row, pt, rule="exact"):
    tr_pr = row._tr.get_or_add_trPr()
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(round(pt * 20))))
    h.set(qn("w:hRule"), rule)
    tr_pr.append(h)


def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    tr_pr.append(el)


def add_page_break(doc):
    p = doc.add_paragraph()
    para_fmt(p, 0, 0)
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


# --------------------------------------------------------------------------
def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = Document()

    # ---- mise en page generale -------------------------------------------
    sec = doc.sections[0]
    sec.page_width = PAGE_W
    sec.page_height = PAGE_H
    sec.left_margin = MARGIN
    sec.right_margin = MARGIN
    sec.top_margin = Cm(0.0)
    sec.bottom_margin = Cm(0.0)
    sec.header_distance = Cm(0.0)
    sec.footer_distance = Cm(0.0)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10)
    normal.font.color.rgb = BLACK
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing = Pt(15.4)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ---- styles de titres (TOC automatique) ------------------------------
    h1 = doc.styles["Heading 1"]
    h1.font.name = FONT
    h1.font.size = Pt(12)
    h1.font.bold = True
    h1.font.color.rgb = NAVY
    h1.font.all_caps = True
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(14)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h1_rpr = h1.element.get_or_add_rPr()
    h1_rfonts = h1_rpr.find(qn("w:rFonts"))
    if h1_rfonts is None:
        h1_rfonts = OxmlElement("w:rFonts")
        h1_rpr.insert(0, h1_rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        h1_rfonts.set(qn(attr), FONT)
    hpdr = h1.element.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "7")
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), NAVY_HEX)
    borders.append(bottom)
    hpdr.append(borders)

    # ---- COUVERTURE (section 1, sans en-tete ni pied) --------------------
    band = doc.add_paragraph()
    para_fmt(band, 0, 0, line=29, left=Cm(-2.1), right=Cm(-2.1), bg=NAVY_HEX)
    r = band.add_run(" ")
    set_run_font(r, size=1, color=WHITE)

    head = doc.add_paragraph()
    para_fmt(head, 38, 0, line=14)
    add_tab_stop(head, CONTENT_W_PT, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
    r = head.add_run("ICHESS, LLC")
    set_run_font(r, size=11.5, color=NAVY, spacing=1.6)
    r = head.add_run("\tFHI 360 — PROJET EpiC RDC")
    set_run_font(r, size=11.5, color=NAVY, spacing=1.6)

    # titre
    spacer = doc.add_paragraph()
    para_fmt(spacer, 0, 0, line=200)
    r = spacer.add_run(" ")
    set_run_font(r, size=1)

    for i, line in enumerate(wrap_title(DATA["cover_title"], 27.0, CONTENT_W_PT - 10)):
        p = doc.add_paragraph()
        para_fmt(p, 0, 0, line=34, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
        r = p.add_run(line)
        set_run_font(r, size=27, color=BLACK)

    spacer = doc.add_paragraph()
    para_fmt(spacer, 0, 0, line=140)
    r = spacer.add_run(" ")
    set_run_font(r, size=1)

    logos = doc.add_paragraph()
    para_fmt(logos, 0, 0, align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, (fn, hpt) in enumerate([("logo_usa_w.png", 21), ("logo_epic_w.png", 20),
                                   ("logo_ichess_w.png", 24)]):
        run = logos.add_run()
        run.add_picture(os.path.join(ROOT, "assets", fn), height=Pt(hpt))
        if i < 2:
            sp = logos.add_run("      ")
            set_run_font(sp, size=11.5)

    spacer = doc.add_paragraph()
    para_fmt(spacer, 0, 0, line=160)
    r = spacer.add_run(" ")
    set_run_font(r, size=1)

    foot = doc.add_paragraph()
    para_fmt(foot, 0, 0, line=14)
    add_tab_stop(foot, CONTENT_W_PT, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
    ppr = foot._element.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single")
    top.set(qn("w:sz"), "6")
    top.set(qn("w:space"), "24")
    top.set(qn("w:color"), NAVY_HEX)
    borders.append(top)
    ppr.append(borders)
    r = foot.add_run(DATA["cover_place"].upper())
    set_run_font(r, size=11.5, color=NAVY, spacing=1.6)
    r = foot.add_run("\tICHESS, LLC")
    set_run_font(r, size=11.5, color=NAVY, spacing=1.6)

    # ---- SECTIONS SUIVANTES : une section par partie, en-tete dedie ------
    first_body = [True]

    def start_section(label):
        sec = doc.add_section(WD_SECTION.NEW_PAGE)
        sec.page_width = PAGE_W
        sec.page_height = PAGE_H
        sec.left_margin = MARGIN
        sec.right_margin = MARGIN
        sec.top_margin = TOP_MARGIN
        sec.bottom_margin = Cm(2.1)
        sec.header_distance = Cm(1.2)
        sec.footer_distance = Cm(0.95)
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        if first_body[0]:
            pg = OxmlElement("w:pgNumType")
            pg.set(qn("w:start"), "2")
            sec._sectPr.append(pg)
            first_body[0] = False
        hp = sec.header.paragraphs[0]
        para_fmt(hp, 0, 0, line=12)
        add_tab_stop(hp, CONTENT_W_PT, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
        r = hp.add_run("ICHESS, LLC")
        set_run_font(r, size=7, bold=True, color=NAVY, spacing=1.3)
        r = hp.add_run("\t" + label)
        set_run_font(r, size=7, color=GREY, spacing=1.3)
        add_bottom_border(hp, color=RULE_HEX, size=4, space=4)
        fp = sec.footer.paragraphs[0]
        para_fmt(fp, 0, 0, line=12, align=WD_ALIGN_PARAGRAPH.CENTER)
        field_run(fp, ' PAGE \\# "00" ', size=8, bold=True, color=NAVY, spacing=2.1,
                  cached="02")
        return sec

    # ---- PREFACE / REMERCIEMENTS ----------------------------------------
    def text_section(block, section_label):
        start_section(section_label)
        p = doc.add_paragraph(style="Heading 1")
        para_fmt(p, 0, 14, line=16, keep_next=True)
        r = p.add_run(block["title"].upper())
        set_run_font(r, size=12, bold=True, color=NAVY)
        for para in block["paras"]:
            p = doc.add_paragraph()
            para_fmt(p, 0, 7.2, line=15.4, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            r = p.add_run(para)
            set_run_font(r, size=10, color=BLACK)
        sig = block["signature"]
        p = doc.add_paragraph()
        para_fmt(p, 31, 0, line=14, left=Pt(172.3))
        r = p.add_run(sig[0])
        set_run_font(r, size=10.5, bold=True, color=NAVY)
        p = doc.add_paragraph()
        para_fmt(p, 3, 0, line=13, left=Pt(172.3))
        r = p.add_run(sig[1])
        set_run_font(r, size=9.5, color=GREY)

    text_section(DATA["preface"], "PRÉFACE")
    text_section(DATA["remerciements"], "REMERCIEMENTS")

    # ---- TABLE DES MATIERES ---------------------------------------------
    start_section("TABLE DES MATIÈRES")
    toc_anchor = doc.add_paragraph()
    para_fmt(toc_anchor, 0, 0, line=1)
    add_toc_field(doc, toc_anchor)

    # ---- LISTES ----------------------------------------------------------
    start_section("LISTE DES FIGURES ET TABLEAUX")
    list_section(doc, "LISTE DES FIGURES",
                 [("Figure %d:" % i, t, p) for i, (t, p) in enumerate(DATA["figures"], 1)])
    list_section(doc, "LISTE DES TABLEAUX",
                 [("Tableau %d:" % i, t, p) for i, (t, p) in enumerate(DATA["tables"], 1)])
    list_section(doc, "TABLEAUX DES ANNEXES",
                 [("Tableau %s:" % c, t, p) for c, t, p in DATA["annex_tables"]])

    # ---- ABREVIATIONS ----------------------------------------------------
    start_section("ABRÉVIATIONS ET ACRONYMES")
    abbreviations(doc)

    add_core_properties(doc)
    doc.save(OUT)
    print("DOCX :", OUT)


# --------------------------------------------------------------------------
def wrap_title(text, size, width_pt):
    """Decoupe le titre de couverture en lignes equilibrees."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
    try:
        pdfmetrics.getFont("GI")
    except Exception:
        pdfmetrics.registerFont(RLTTFont("GI", os.path.join(ROOT, "fonts",
                                                            "GlacialIndifference-Regular.ttf")))
    words = text.split(" ")
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and pdfmetrics.stringWidth(trial, "GI", size) > width_pt:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def set_header_label(doc, label):
    sec = doc.sections[-1]
    hdr = sec.header
    for p in hdr.paragraphs:
        for r in p.runs:
            if "{{SECTION}}" in (r.text or ""):
                r.text = label


TOC_GEOM = {
    0: dict(indent=0.0, tab=0.0, size=10.5, page_size=10, bold=True, color=BLACK),
    1: dict(indent=26.0, tab=26.0, size=10.5, page_size=10, bold=True, color=NAVY),
    2: dict(indent=38.0, tab=38.0, size=9.5, page_size=9, bold=False, color=BLACK),
}


def add_toc_field(doc, anchor):
    """Champ TOC Word dont le resultat mis en cache reprend la table du document source."""
    p = anchor
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(sep)
    run._r.append(OxmlElement("w:t"))

    prev = None
    for level, num, title, page in DATA["toc"]:
        g = TOC_GEOM[level]
        q = doc.add_paragraph()
        if level == 0:
            para_fmt(q, 0, 0, line=30, align=WD_ALIGN_PARAGRAPH.LEFT)
        elif level == 1:
            para_fmt(q, 11.6, 0, line=24.6, align=WD_ALIGN_PARAGRAPH.LEFT,
                     left=Pt(g["indent"]), first=Pt(-g["indent"]))
        else:
            before = 1.2 if prev == 1 else 0.0
            para_fmt(q, before, 0, line=23.6, align=WD_ALIGN_PARAGRAPH.LEFT,
                     left=Pt(g["indent"]), first=Pt(-g["indent"]))
        add_tab_stop(q, CONTENT_W_PT, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        if g["tab"]:
            q.paragraph_format.tab_stops.add_tab_stop(Pt(g["tab"]), WD_TAB_ALIGNMENT.LEFT,
                                                      WD_TAB_LEADER.SPACES)

        if num:
            r = q.add_run(num)
            set_run_font(r, size=g["size"], bold=g["bold"], color=g["color"])
            r = q.add_run("\t")
            set_run_font(r, size=g["size"])
        r = q.add_run(title)
        set_run_font(r, size=g["size"], bold=g["bold"], color=g["color"])
        r = q.add_run("\t" + page)
        set_run_font(r, size=g["page_size"], bold=True, color=NAVY)
        prev = level

    end_run = doc.add_paragraph().add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    end_run._r.append(end)


def Qt(v):
    return Pt(v)


def list_section(doc, label, entries):
    p = doc.add_paragraph(style="Heading 1")
    para_fmt(p, 0, 18, line=16, keep_next=True)
    r = p.add_run(label)
    set_run_font(r, size=12, bold=True, color=NAVY)
    for lab, title, page in entries:
        q = doc.add_paragraph()
        para_fmt(q, 0, 0, line=18.4, left=Pt(14))
        add_tab_stop(q, CONTENT_W_PT - 14, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = q.add_run("%s %s" % (lab, title))
        set_run_font(r, size=9.5, color=BLACK)
        r = q.add_run("\t" + page)
        set_run_font(r, size=9, bold=True, color=NAVY)
    spacer = doc.add_paragraph()
    para_fmt(spacer, 0, 0, line=16)
    r = spacer.add_run(" ")
    set_run_font(r, size=2)


def abbreviations(doc):
    rows = DATA["abbrev"]
    table = doc.add_table(rows=len(rows) + 1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    fixed_layout(table)
    clear_table_borders(table)
    table.autofit = False
    widths = [Cm(3.4), Cm(13.3)]
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = widths[i]

    # entete
    hdr_row = table.rows[0]
    set_row_height(hdr_row, 25)
    set_repeat_header(hdr_row)
    for i, text in enumerate(("SIGLE", "SIGNIFICATION")):
        cell = hdr_row.cells[i]
        set_cell_bg(cell, NAVY_HEX)
        set_cell_margins(cell, left=0.35 if i == 0 else 0.0, right=0.0, top=0.0, bottom=0.0)
        p = cell.paragraphs[0]
        para_fmt(p, 0, 0, line=25, align=WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run(text)
        set_run_font(r, size=8, bold=True, color=WHITE, spacing=0.55)

    for idx, (sigle, definition) in enumerate(rows, start=1):
        row = table.rows[idx]
        set_row_height(row, 18.5)
        for i, text in enumerate((sigle, definition)):
            cell = row.cells[i]
            if idx % 2 == 0:
                set_cell_bg(cell, TINT_HEX)
            set_cell_margins(cell, left=0.35 if i == 0 else 0.0, right=0.0,
                             top=0.0, bottom=0.0)
            p = cell.paragraphs[0]
            para_fmt(p, 0, 0, line=18.5, align=WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(text)
            if i == 0:
                set_run_font(r, size=8.5, bold=True, color=NAVY)
            else:
                set_run_font(r, size=8.5, color=BLACK)


def add_core_properties(doc):
    cp = doc.core_properties
    cp.title = DATA["cover_title"]
    cp.author = "ICHESS, LLC"
    cp.subject = "Diagnostic opérationnel rapide des établissements de santé – RDC"
    cp.category = "Rapport institutionnel"
    cp.comments = "Mise en page conforme à la charte Md_ref. Contenu : document source 05-11-26."


if __name__ == "__main__":
    build()

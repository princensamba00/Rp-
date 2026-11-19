# -*- coding: utf-8 -*-
"""Charte graphique relevee sur Md_ref.pdf (design de reference exclusif)."""

# --- Palette ---------------------------------------------------------------
NAVY = (0x13 / 255, 0x1D / 255, 0x44 / 255)          # #131D44
BLUE = (0x51 / 255, 0x66 / 255, 0xB7 / 255)          # #5166B7
YELLOW = (0xFF / 255, 0xDE / 255, 0x59 / 255)        # #FFDE59
GREY = (0x6B / 255, 0x70 / 255, 0x7D / 255)          # #6B707D
RULE_GREY = (0xD9 / 255, 0xD9 / 255, 0xD9 / 255)     # #D9D9D9
LEADER = (0.8078, 0.8392, 0.9725)                    # #CEE1F8
TINT = (1.0, 0.9843, 0.9690)                         # #FFFBF7
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)

# --- Page & grille ---------------------------------------------------------
PAGE_W = 595.276
PAGE_H = 841.890
MARGIN_L = 59.53
MARGIN_R = 59.53
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R          # 476.22
RIGHT_COL = PAGE_W - MARGIN_R                      # 535.75

HEADER_RULE_Y = 48.5          # depuis le haut de page
HEADER_BASELINE = 42.4
FOOTER_BASELINE = 807.4
CONTENT_TOP = 75.5            # haut optique du titre de section
BODY_TOP = 107.5              # haut optique de la premiere ligne justifiee
BOTTOM_LIMIT = 782.0          # derniere ligne de corps utilisable

# --- Typographie (tailles relevees sur Md_ref) -----------------------------
S_HEADER = 7.2
S_H1 = 12.2
S_BODY = 9.9
LEADING_BODY = 15.4
PARA_GAP = 7.2

S_TOC_L0 = 10.4
S_TOC_L0_PAGE = 10.1
S_TOC_CH = 10.6
S_TOC_CH_PAGE = 10.3
S_TOC_SEC = 9.4
S_TOC_SEC_PAGE = 9.1

S_LIST = 9.4
S_LIST_PAGE = 9.1

S_TBL_HEAD = 7.9
S_TBL = 8.4
TBL_HEAD_H = 25.0
TBL_ROW_H = 18.5
TBL_COL1_X = 70.5
TBL_COL2_X = 158.5
TBL_ALT_FROM = 1              # surlignage des lignes paires

S_COVER_TITLE = 27.0
S_COVER_ROW = 11.5

# --- Interlettrage ---------------------------------------------------------
CS_HEADER = 1.30
CS_PAGENUM = 2.10
CS_COVER = 1.60

# --- Libelles courants -----------------------------------------------------
ORG = "ICHESS, LLC"
ORG_LONG = "International Center for Health Systems Strengthening"

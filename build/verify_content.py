# -*- coding: utf-8 -*-
"""Controle de fidelite : chaque element du DOCUMENT 1 doit se retrouver dans
le livrable, sans ajout de texte redactionnel."""
import json
import os
import re
import unicodedata

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_"
                         "Rapport_final_version_propre_05-11-26.pdf")
OUT_PDF = os.path.join(ROOT, "livrables",
                       "Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.pdf")
DATA = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00ad", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def tokens(s):
    s = norm(s).lower()
    s = re.sub(r"[«»\"“”]", " ", s)
    return [t for t in re.split(r"[^0-9a-zàâçéèêëîïôûùüÿñæœ'’-]+", s) if t]


def pdf_text(path, pages=None):
    d = pymupdf.open(path)
    out = []
    for i, p in enumerate(d):
        if pages and (i + 1) not in pages:
            continue
        out.append(p.get_text())
    return "\n".join(out)


def main():
    source = pdf_text(SRC)
    out = norm(pdf_text(OUT_PDF))
    out_tokens = set(tokens(out))

    print("=" * 72)
    print("1. Textes courants (preface, remerciements)")
    ok = True
    for key in ("preface", "remerciements"):
        for para in DATA[key]["paras"]:
            if norm(para) in out:
                continue
            missing = [w for w in tokens(para) if w not in out_tokens]
            ok = False
            print("   MANQUANT (%s): %s… (%d mots absents)" % (key, para[:60], len(missing)))
    for key in ("preface", "remerciements"):
        for sig in DATA[key]["signature"]:
            if norm(sig) not in out:
                ok = False
                print("   SIGNATURE MANQUANTE :", sig)
    print("   ->", "conforme" if ok else "A CORRIGER")

    print("=" * 72)
    print("2. Table des matieres")
    miss = 0
    for level, num, title, page in DATA["toc"]:
        if norm(title) not in out:
            miss += 1
            print("   MANQUANT :", title)
    print("   %d entrees, %d manquantes" % (len(DATA["toc"]), miss))

    print("=" * 72)
    print("3. Listes des figures et tableaux")
    for label, items in (("Figure", DATA["figures"]), ("Tableau", DATA["tables"]),
                         ("Tableau A", DATA["annex_tables"])):
        miss = 0
        for it in items:
            title = it[0] if label != "Tableau A" else it[1]
            if norm(title) not in out:
                miss += 1
                print("   MANQUANT (%s): %s" % (label, title[:70]))
        print("   %s : %d entrees, %d manquantes" % (label, len(items), miss))

    print("=" * 72)
    print("4. Abreviations")
    miss = 0
    for sigle, definition in DATA["abbrev"]:
        if norm(definition) not in out:
            miss += 1
            print("   MANQUANT :", sigle, "|", definition[:60])
    print("   %d entrees, %d manquantes" % (len(DATA["abbrev"]), miss))

    print("=" * 72)
    print("5. Mots du document source absents du livrable")
    src_tokens = tokens(source)
    # on retire les elements de mise en page propres au document source
    ignore = set()
    missing = {}
    for t in src_tokens:
        if t not in out_tokens:
            missing[t] = missing.get(t, 0) + 1
    # les mots du source non repris (hors pagination, en-tetes du modele initial)
    for t in sorted(missing):
        print("   %-22s x%d" % (t, missing[t]))


if __name__ == "__main__":
    main()

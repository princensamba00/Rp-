# -*- coding: utf-8 -*-
"""Construit le modele de contenu du rapport (source exclusive : DOCUMENT 1).

Les textes courants et le tableau des abreviations sont extraits du PDF source
(work/content_raw.json) ; les listes (table des matieres, figures, tableaux,
annexes) sont relevees a l'identique sur les pages 4 a 8 du document source.
Aucun texte n'est redige ni reformule ici.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
raw = json.load(open(os.path.join(ROOT, "work", "content_raw.json"), encoding="utf-8"))

COVER_TITLE = ("Rapport du diagnostic opérationnel rapide de la préparation des "
               "établissements de santé pour les services de santé maternelle, "
               "néonatale et infantile, paludisme et nutrition")
COVER_PLACE = "Kinshasa, Octobre 2026"

# --- Table des matieres (pages 4-5 du document source) ------------------------
# (niveau, numero, titre, page)
TOC = [
    (0, "", "Préface", "2"),
    (0, "", "Remerciements", "3"),
    (0, "", "Liste des figures et tableaux", "6"),
    (0, "", "Résumé exécutif", "11"),
    (1, "I.", "Introduction", "14"),
    (2, "1.1.", "Contexte et justification", "14"),
    (2, "1.2.", "Objectifs et résultats attendus", "15"),
    (2, "1.3.", "Bénéficiaires et utilisations des résultats", "16"),
    (1, "II.", "Approche méthodologique", "17"),
    (2, "2.1.", "Conception générale de l'étude", "17"),
    (2, "2.2.", "Population, échantillonnage et unités d'analyse", "17"),
    (2, "2.3.", "Instruments de collecte", "18"),
    (2, "2.4.", "Organisation de la collecte", "18"),
    (2, "2.5.", "Assurance qualité des données", "19"),
    (2, "2.6.", "Cadre analytique : fonctions traceuses et classification tricolore", "19"),
    (2, "2.7.", "Analyse qualitative", "24"),
    (2, "2.8.", "Chaîne de traitement des données et reproductibilité", "24"),
    (2, "2.9.", "Considérations éthiques", "25"),
    (2, "2.10.", "Limites méthodologiques", "25"),
    (1, "III.", "Résultats", "26"),
    (2, "3.1.", "Description de l’échantillon et couverture", "26"),
    (2, "3.2.", "Niveau de préparation fonctionnelle des établissements", "27"),
    (2, "3.3.", "Préparation aux urgences", "37"),
    (2, "3.4.", "Intégration opérationnelle des services", "42"),
    (2, "3.5.", "Utilisation des données de routine et de surveillance", "49"),
    (2, "3.6.", "Facteurs associés aux contraintes observées", "50"),
    (2, "3.7.", "Priorités d'investissement", "74"),
    (1, "IV.", "Discussion", "83"),
    (2, "4.1.", "Ce que mesure le diagnostic et comment interpréter les résultats", "83"),
    (2, "4.2.", "Des vulnérabilités déjà documentées et confirmées", "83"),
    (2, "4.3.", "Les goulots dominants à la lumière de la littérature", "85"),
    (2, "4.4.", "Le paradoxe du rétablissement matériel isolé", "86"),
    (2, "4.5.", "De l’offre déclarée à la capacité réelle : les limites du suivi de routine", "86"),
    (2, "4.6.", "Un gradient de capacité insuffisant : l’HGR ne garantit pas toujours la prise en charge des cas référés", "87"),
    (2, "4.7.", "Vulnérabilités provinciales et contraction des appuis extérieurs", "87"),
    (2, "4.8.", "Cohérence avec les orientations nationales vers la CSU", "88"),
    (2, "4.9.", "Forces et limites de l'analyse", "88"),
    (2, "4.10.", "Implications pour l'action et pour la recherche", "88"),
    (1, "V.", "Conclusion et recommandations", "89"),
    (2, "5.1.", "Conclusion", "89"),
    (2, "5.2.", "Recommandations", "89"),
    (0, "", "Bibliographie", "96"),
    (0, "", "Annexes", "100"),
    (2, "", "Annexe 1 : Haut-Katanga", "100"),
    (2, "", "Annexe 2 : Haut-Lomami", "105"),
    (2, "", "Annexe 3 : Kasaï-Central", "109"),
    (2, "", "Annexe 4 : Kasaï-Oriental", "114"),
    (2, "", "Annexe 5 : Lomami", "119"),
    (2, "", "Annexe 6 : Lualaba", "124"),
    (2, "", "Annexe 7 : Sankuru", "129"),
    (2, "", "Annexe 8 : Tanganyika", "133"),
    (2, "", "Annexe 9 : Éléments en cause dans les fonctions d’urgence rouges, par niveau", "138"),
    (2, "", "Annexe 10 : Compléments sur le cumul des blocages, les fragilités et les simulations", "146"),
    (2, "", "Annexe 11 : Analyse de sensibilité : observations rattachées à plusieurs dimensions", "150"),
]

FIGURES = [
    ("Établissements évalués par province et par niveau de soins", "27"),
    ("Classification des 28 fonctions traceuses, ensemble des établissements", "29"),
    ("Préparation opérationnelle des 17 fonctions communes aux trois niveaux de soins", "34"),
    ("Part de fonctions rouges par fonction et par province", "35"),
    ("Préparation opérationnelle par domaine technique et par niveau de soins", "36"),
    ("État opérationnel des fonctions vitales dont le service est déclaré offert, par niveau de soins", "37"),
    ("Préparation aux urgences : ensemble, par niveau de soins et par province", "38"),
    ("Couples de prestations documentés, par niveau de soins", "43"),
    ("Jours de présence des prestataires déclarés sur trois mois, par service et par niveau", "44"),
    ("État de la fonction d’aval lorsque la fonction d’amont est classée verte ou jaune", "48"),
    ("Chaîne surveillance-réponse et chaîne des données : composantes et points de rupture", "49"),
    ("Dimensions bloquantes des fonctions rouges et fragilités des fonctions jaunes", "51"),
    ("Nombre de dimensions bloquantes par fonction rouge, selon le niveau de soins", "52"),
    ("Les douze configurations de blocage les plus fréquentes parmi les fonctions rouges", "53"),
    ("Fonctions jaunes à une seule fragilité du vert", "54"),
    ("Fonctions rouges libérées par le rétablissement d’un seul élément critique", "58"),
    ("Part de fonctions vitales rouges dans les CS selon la présence déclarée d’une catégorie de personnel", "61"),
    ("Composantes de la référence, de l’eau et de l’hygiène, de l’électricité et de la communication", "63"),
    ("Profil des dimensions bloquantes par province", "68"),
    ("Paquets cumulatifs de leviers : fonctions rouges libérées à mesure que les dimensions sont résolues", "77"),
    ("Gain simulé de chaque levier, par province (part des fonctions rouges libérées)", "81"),
]

TABLES = [
    ("Périmètre du diagnostic", "15"),
    ("Base de sondage et échantillon réalisé, par niveau géographique", "17"),
    ("Les 28 fonctions traceuses (71 spécifications selon le niveau)", "20"),
    ("Les huit règles de décision de l'algorithme de classification Vert / Jaune / Rouge", "22"),
    ("Rôle des douze dimensions dans les 71 spécifications", "23"),
    ("Modalités d’application des règles de classification", "24"),
    ("Classification des 28 fonctions traceuses, par ordre de criticité", "29"),
    ("Élément critique le plus souvent en déficit, par fonction", "31"),
    ("Blocages dominants des fonctions d’urgence, par niveau de soins", "39"),
    ("Principaux éléments critiques d’urgence manquants ou en rupture", "40"),
    ("Menaces immédiates et contraintes déclarées d'accès à la référence", "41"),
    ("Correspondance documentaire avec les fonctions signal SONU (référentiel classique)", "42"),
    ("Références au cours des trois derniers mois, par motif", "45"),
    ("Contraintes déclarées au départ lorsque la référence est décidée (centres de santé)", "46"),
    ("Difficultés déclarées à la réception des patients référés (CSR et HGR)", "47"),
    ("État des fonctions vitales d'aval à la destination de référence enquêtée", "47"),
    ("Points de rupture du circuit de surveillance, par niveau et par province", "50"),
    ("Les dimensions de blocage : ce qu'elles bloquent, ce qu'elles fragilisent et ce que leur résolution libère", "52"),
    ("Disponibilité des intrants critiques, tous niveaux", "56"),
    ("Disponibilité des équipements critiques, tous niveaux", "57"),
    ("Effectifs déclarés par catégorie et par niveau (roster du personnel)", "59"),
    ("Formations déclarées au cours des deux dernières années, par thème et par niveau", "60"),
    ("Conditions transversales au niveau des établissements", "62"),
    ("Composantes du mécanisme de référence en cause dans les fonctions rouges de la référence urgente, par niveau", "64"),
    ("Perturbations déclarées au cours des trois derniers mois, par province (% d’établissements)", "65"),
    ("Conjoncturel ou structurel : perturbation déclarée et blocage observé", "66"),
    ("Causes déclarées des interruptions et blocages observés de la fonction correspondante", "67"),
    ("Constance intra-zone de la dimension bloquante dominante", "69"),
    # Document source : renvoi de pagination rompu ("Erreur ! Signet non defini.")
    ("Synthèse des goulots opérationnels, de leurs conséquences et des risques sanitaires associés", ""),
    ("Matrice consolidée d'analyse et de correction des goulots d'étranglement, par contrainte transversale", "71"),
    ("Intrants et équipements prioritaires les plus souvent manquants pour les fonctions vitales (tous niveaux)", "75"),
    ("Gains simulés des paires de leviers et complémentarité", "78"),
    ("Lecture programmatique des priorités d’investissement", "79"),
    ("Profil provincial des blocages et des leviers (ordre alphabétique)", "80"),
    ("Les quinze zones de santé où un seul levier débloque le plus de fonctions rouges, et la meilleure combinaison de deux leviers", "82"),
    ("Rapprochement de quelques indicateurs avec les enquêtes antérieures", "84"),
    ("Plan d'action priorisé : responsables, indicateurs, valeurs de départ et cibles indicatives", "94"),
]

_ZD = [
    ("Haut-Katanga", [("Classification des 28 fonctions traceuses, Haut-Katanga", "101"),
                      ("Dimensions bloquantes des fonctions rouges, par fonction (n), Haut-Katanga", "102"),
                      ("Dimensions bloquantes et fragilités, Haut-Katanga", "103"),
                      ("Conditions transversales et profil d'urgence, Haut-Katanga", "103"),
                      ("Leviers simples et paire optimale, Haut-Katanga", "103"),
                      ("Lecture par zone de santé, Haut-Katanga", "104"),
                      ("Établissements où un seul levier libère le plus de fonctions rouges, Haut-Katanga", "105")]),
    ("Haut-Lomami", [("Classification des 28 fonctions traceuses, Haut-Lomami", "106"),
                     ("Dimensions bloquantes des fonctions rouges, par fonction (n), Haut-Lomami", "107"),
                     ("Dimensions bloquantes et fragilités, Haut-Lomami", "108"),
                     ("Conditions transversales et profil d'urgence, Haut-Lomami", "108"),
                     ("Leviers simples et paire optimale, Haut-Lomami", "108"),
                     ("Lecture par zone de santé, Haut-Lomami", "109"),
                     ("Établissements où un seul levier libère le plus de fonctions rouges, Haut-Lomami", "109")]),
    ("Kasaï-Central", [("Classification des 28 fonctions traceuses, Kasaï-Central", "111"),
                       ("Dimensions bloquantes des fonctions rouges, par fonction (n), Kasaï-Central", "112"),
                       ("Dimensions bloquantes et fragilités, Kasaï-Central", "113"),
                       ("Conditions transversales et profil d'urgence, Kasaï-Central", "113"),
                       ("Leviers simples et paire optimale, Kasaï-Central", "113"),
                       ("Lecture par zone de santé, Kasaï-Central", "114"),
                       ("Établissements où un seul levier libère le plus de fonctions rouges, Kasaï-Central", "114")]),
    ("Kasaï-Oriental", [("Classification des 28 fonctions traceuses, Kasaï-Oriental", "116"),
                        ("Dimensions bloquantes des fonctions rouges, par fonction (n), Kasaï-Oriental", "117"),
                        ("Dimensions bloquantes et fragilités, Kasaï-Oriental", "118"),
                        ("Conditions transversales et profil d'urgence, Kasaï-Oriental", "118"),
                        ("Leviers simples et paire optimale, Kasaï-Oriental", "118"),
                        ("Lecture par zone de santé, Kasaï-Oriental", "119"),
                        ("Établissements où un seul levier libère le plus de fonctions rouges, Kasaï-Oriental", "119")]),
    ("Lomami", [("Classification des 28 fonctions traceuses, Lomami", "120"),
                ("Dimensions bloquantes des fonctions rouges, par fonction (n), Lomami", "121"),
                ("Dimensions bloquantes et fragilités, Lomami", "122"),
                ("Conditions transversales et profil d'urgence, Lomami", "122"),
                ("Leviers simples et paire optimale, Lomami", "122"),
                ("Lecture par zone de santé, Lomami", "123"),
                ("Établissements où un seul levier libère le plus de fonctions rouges, Lomami", "123")]),
    ("Lualaba", [("Classification des 28 fonctions traceuses, Lualaba", "125"),
                 ("Dimensions bloquantes des fonctions rouges, par fonction (n), Lualaba", "126"),
                 ("Dimensions bloquantes et fragilités, Lualaba", "127"),
                 ("Conditions transversales et profil d'urgence, Lualaba", "127"),
                 ("Leviers simples et paire optimale, Lualaba", "127"),
                 ("Lecture par zone de santé, Lualaba", "128"),
                 ("Établissements où un seul levier libère le plus de fonctions rouges, Lualaba", "128")]),
    ("Sankuru", [("Classification des 28 fonctions traceuses, Sankuru", "130"),
                 ("Dimensions bloquantes des fonctions rouges, par fonction (n), Sankuru", "131"),
                 ("Dimensions bloquantes et fragilités, Sankuru", "132"),
                 ("Conditions transversales et profil d'urgence, Sankuru", "132"),
                 ("Leviers simples et paire optimale, Sankuru", "132"),
                 ("Lecture par zone de santé, Sankuru", "133"),
                 ("Établissements où un seul levier libère le plus de fonctions rouges, Sankuru", "133")]),
    ("Tanganyika", [("Classification des 28 fonctions traceuses, Tanganyika", "135"),
                    ("Dimensions bloquantes des fonctions rouges, par fonction (n), Tanganyika", "136"),
                    ("Dimensions bloquantes et fragilités, Tanganyika", "137"),
                    ("Conditions transversales et profil d'urgence, Tanganyika", "137"),
                    ("Leviers simples et paire optimale, Tanganyika", "137"),
                    ("Lecture par zone de santé, Tanganyika", "138"),
                    ("Établissements où un seul levier libère le plus de fonctions rouges, Tanganyika", "138")]),
]

ANNEX_TAIL = [
    ("Éléments et composantes en cause dans les fonctions d’urgence rouges, par fonction et par niveau", "138"),
    ("Nombre de dimensions bloquantes par fonction rouge, par niveau", "146"),
    ("Fonctions jaunes à fragilité unique, par fonction", "147"),
    ("Rétablissement conjoint de tous les éléments critiques en déficit, par niveau", "148"),
    ("Fonctions rouges libérées par le rétablissement d’un seul élément critique, par niveau", "148"),
    ("Fonctions rouges libérées à chaque étape du paquet cumulatif", "149"),
    ("Observations lues dans plusieurs dimensions de la grille", "150"),
    ("Effet du rattachement unique sur les principaux indicateurs", "151"),
]

ANNEX_TABLES = []
n = 0
for _prov, items in _ZD:
    for title, page in items:
        n += 1
        ANNEX_TABLES.append((f"A{n}", title, page))
for title, page in ANNEX_TAIL:
    n += 1
    ANNEX_TABLES.append((f"A{n}", title, page))

assert n == 64, n
assert len(FIGURES) == 21
assert len(TABLES) == 37

data = {
    "cover_title": COVER_TITLE,
    "cover_place": COVER_PLACE,
    "preface": {
        "title": "Préface",
        "eyebrow": "PRÉFACE",
        "paras": [p for p in raw["preface"] if not p.startswith(("Narcisse", "Directeur Technique"))],
        "signature": ["Narcisse Naia Embeke, MD, MPH", "Directeur Technique, Projet EpiC RDC"],
    },
    "remerciements": {
        "title": "Remerciements",
        "eyebrow": "REMERCIEMENTS",
        "paras": [p for p in raw["remerciements"] if not p.startswith(("Ngashi", "Directeur Exécutif"))],
        "signature": ["Ngashi Ngongo, PhD, MD, MPH", "Directeur Exécutif, ICHESS"],
    },
    "toc": TOC,
    "figures": FIGURES,
    "tables": TABLES,
    "annex_tables": ANNEX_TABLES,
    "abbrev": raw["abbrev"],
}

assert len(data["preface"]["paras"]) == 7, len(data["preface"]["paras"])
assert len(data["remerciements"]["paras"]) == 6, len(data["remerciements"]["paras"])
assert len(data["abbrev"]) == 70, len(data["abbrev"])

with open(os.path.join(HERE, "content.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
print("figures", len(FIGURES), "tables", len(TABLES), "annex", len(ANNEX_TABLES), "abbrev", len(data["abbrev"]))

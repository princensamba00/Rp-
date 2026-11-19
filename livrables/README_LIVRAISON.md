# Livraison — Reproduction du rapport source selon le design `Md_ref`

**Projet :** Rapport du diagnostic opérationnel rapide de la préparation des établissements de santé pour les services de santé maternelle, néonatale et infantile, paludisme et nutrition — ICHESS, LLC / FHI 360 – Projet EpiC RDC.

---

## 1. Fichiers livrés

| Livrable | Fichier | Pages |
|---|---|---|
| **1. Word modifiable** | `livrables/Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.docx` | 11 |
| **2. PDF final** | `livrables/Rapport_Diagnostic_Operationnel_Rapide_ESS_EpiC_RDC_FHI360_ICHESS_MdRev.pdf` | 11 |

Les deux fichiers partagent la même structure, la même pagination et la même charte.

---

## 2. Principe de séparation appliqué

| Élément | Source |
|---|---|
| Page de couverture (titre, date), préface, remerciements | **DOCUMENT 1** (texte intégral, mot pour mot) |
| Table des matières (54 entrées + pagination d'origine) | **DOCUMENT 1**, p. 4-5 |
| Liste des figures (21), des tableaux (37), tableaux des annexes (64) | **DOCUMENT 1**, p. 6-8 |
| Abréviations et acronymes (70 entrées) | **DOCUMENT 1**, p. 9-10 |
| Couleurs, polices, tailles, graisses, marges, grilles, en-têtes, pieds de page, tableaux, sommaire, couverture | **Md_ref** (pages 1-21 : pages-types du rapport + planches de style) |

Aucun texte rédactionnel de `Md_ref` (ni les pages de démonstration « Concordia / lorem ipsum ») n'a été repris. Aucune phrase du document source n'a été réécrite, résumée ou complétée.

---

## 3. Charte graphique relevée sur `Md_ref` et appliquée

**Couleurs**
- Bleu nuit institutionnel `#131D44` (titres, filets, numéros de page, colonne « sigle »)
- Bleu pervenche `#5166B7` (accents secondaires)
- Jaune `#FFDE59` (accent)
- Gris texte `#6B707D` (libellés d'en-tête, fonctions)
- Filet gris clair `#D9D9D9` (séparateur d'en-tête)
- Points de conduite `#CEE1F8`, fond de ligne alternée `#FFFBF7`

**Typographie**
- *Glacial Indifference* (Regular / Bold) — police du modèle, embarquée dans le PDF, fournie dans `fonts/`.
- Corps 9,9 pt / interligne 15,4 pt ; titres de section 12,2 pt capitales + filet 0,9 pt ;
  en-tête 7,2 pt interlettré 1,3 pt ; pagination 8,2 pt interlettrée ; lignes de sommaire 10,4 / 10,6 / 9,4 pt ;
  listes 9,4 pt ; tableau des abréviations 8,4 pt.

**Grille**
- A4, marges 2,1 cm à gauche/droite ; zone de texte 476,2 pt ; en-tête à 48,5 pt ; pied de page centré.

**Éléments de présentation**
- Couverture : bandeau plein bord, ligne d'en-tête interlettrée, titre centré, bloc institutionnel (logos du document source), filet et ligne de pied.
- En-tête : « ICHESS, LLC » + libellé de partie, filet gris.
- Pied de page : numéro sur deux chiffres, interlettré, centré.
- Sommaire : points de conduite, trois niveaux hiérarchiques, numéros de page en gras bleu nuit.
- Tableau des abréviations : bandeau bleu nuit, lignes alternées, sans filets, en-tête répété sur la 2ᵉ page.

---

## 4. Exigences techniques respectées

- **Justification** de tous les paragraphes de texte courant.
- **Césure désactivée** : aucun mot, nom, sigle ou organisme n'est coupé (`suppressAutoHyphens` dans le DOCX ; césure non implémentée dans la composition PDF). Contrôle automatique : 0 ligne terminée par un trait d'union.
- **Table des matières** : champ Word `TOC \o "1-2" \h \z \u` (actualisable par F9) dont le résultat mis en cache reproduit la table du document source ; niveaux de titres structurés (`Titre 1` pour les parties présentes).
- **Pagination** sur deux chiffres (02, 03, 04…).
- **Aucun débordement** : contrôle automatique des boîtes de texte (0 dépassement de marge).
- **Polices intégrées** dans le PDF (sous-ensembles TrueType).
- **Signets PDF** : Couverture, Préface, Remerciements, Table des matières, Liste des figures et tableaux, Abréviations et acronymes.

---

## 5. Contrôles qualité effectués

| Contrôle | Méthode | Résultat |
|---|---|---|
| Intégralité du texte de la préface et des remerciements | comparaison automatique avec le texte source | conforme (7 + 6 paragraphes, signatures incluses) |
| Table des matières | 54 entrées vérifiées une à une | 54/54 |
| Liste des figures | 21 entrées | 21/21 |
| Liste des tableaux | 37 entrées | 37/37 |
| Tableaux des annexes | 64 entrées | 64/64 |
| Abréviations | 70 entrées (sigle + signification) | 70/70 |
| Mots du document source absents du livrable | analyse lexicale | aucun mot de contenu manquant |
| Débordements / troncatures | contrôle des boîtes de texte et rendu page à page | 0 |
| Césure | contrôle des fins de ligne | 0 |
| Comparaison visuelle avec `Md_ref` | superposition page à page (préface, sommaire, listes, abréviations) | conforme |

Le rendu du fichier Word a été contrôlé page par page au moyen d'un moteur d'aperçu reconstituant sa pagination (LibreOffice/Word n'étant pas disponibles dans l'environnement de production).

---

## 6. Points à connaître

1. **Périmètre du document source.** Le PDF fourni (`…05-11-26.pdf`) ne contient que **10 pages** : couverture, préface, remerciements, table des matières, liste des figures et tableaux, abréviations. Le corps annoncé par la table des matières (Résumé exécutif p. 11 → Tableau A64 p. 151) **ne figure pas** dans le fichier transmis ; il n'a donc pas pu être composé. La reproduction est intégrale pour tout le contenu disponible. Transmettre le corps du rapport permettra de l'ajouter dans la même charte et de renuméroter la table.
2. **Renvoi rompu du document source.** Le « Tableau 29 » porte dans le document d'origine la mention Word « Erreur ! Signet non défini. » à la place du numéro de page. Cette mention technique n'a pas été reproduite ; l'entrée est conservée sans numéro de page, aucun numéro n'ayant été inventé.
3. **Police du modèle.** Pour que le DOCX s'ouvre exactement comme le PDF sur un autre poste, installer les deux fichiers de `fonts/` (Glacial Indifference Regular et Bold, licence SIL OFL — `fonts/OFL.txt`) avant ouverture. À défaut, Word substituera une police voisine.
4. **Actualisation du sommaire.** Le champ de table des matières est actualisable (F9). Son cache reprend la table du document source (qui décrit l'ensemble du rapport sur 151 pages) ; une actualisation le recalculera à partir des titres réellement présents dans ce fichier.

---

## 7. Chaîne de production (reproductible)

```
fonts/                     police du modèle (SIL OFL)
assets/                    logos institutionnels extraits du document source
build/make_content.py      modèle de contenu (textes, listes, abréviations)
build/content.json         contenu consolidé (aucune réécriture)
build/mdrev_style.py       charte relevée sur Md_ref (couleurs, tailles, grille)
build/mdrev_engine.py      primitives de composition (justification sans césure, points de conduite)
build/build_pdf.py         composition du PDF
build/build_docx.py        génération du DOCX (styles, en-têtes, tableaux, champ TOC)
build/preview_docx.py      aperçu de pagination du DOCX
build/verify_content.py    contrôle de fidélité du contenu
```

Régénération : `python build/make_content.py && python build/build_pdf.py && python build/build_docx.py`.

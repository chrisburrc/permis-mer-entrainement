#!/usr/bin/env python3
"""Génère glossaire.js à partir de « 06 - Fiches de révision/glossaire-voile.md ».

Seules les sections ★★★ (Essentiel), ★★ (Utile) et « Compléments » (traités comme
Essentiel) sont reprises. La section ★ Culture est ignorée.

Usage : python3 generer-glossaire.py   (à relancer après chaque modification du glossaire)
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCE = ICI.parent / "06 - Fiches de révision" / "glossaire-voile.md"
CIBLE = ICI / "glossaire.js"

# Sous-titres du Markdown → thème de l'application
THEMES = {
    "Le bateau": "bateau",
    "Bateau, stabilité et gros temps": "bateau",
    "Types de voiliers": "bateau",
    "Le vent et les allures": "vent",
    "Voiles": "voiles",
    "Voiles et réglages": "voiles",
    "Gréement et cordages": "greement",
    "Gréement et accastillage": "greement",
    "Mouvements, incidents et gros temps": "gros_temps",
    "Mouillage": "mouillage",
    "Marée": "maree",
}

# Termes de la section « Compléments » → thème
COMPLEMENTS = {
    "guindant": "voiles",
    "mouiller": "mouillage",
    "amarre": "mouillage",
}


def slug(texte):
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def md_vers_html(texte):
    t = html.escape(texte, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t


def main():
    niveau = None
    theme_md = None
    entrees = []
    for ligne in SOURCE.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("## "):
            titre = ligne[3:]
            if titre.startswith("★★★"):
                niveau = 3
            elif titre.startswith("★★"):
                niveau = 2
            elif titre.startswith("★"):
                niveau = None  # Culture : ignorée
            elif titre.startswith("Compléments"):
                niveau = 3
                theme_md = "Compléments"
            else:
                niveau = None
            continue
        if ligne.startswith("### "):
            theme_md = ligne[4:].strip()
            continue
        if niveau is None or not ligne.startswith("| **"):
            continue

        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if len(cellules) < 2:
            continue
        cellule_terme, definition = cellules[0], " | ".join(cellules[1:])
        mots = re.findall(r"\*\*(.+?)\*\*", cellule_terme)
        terme = re.sub(r"\*\*(.+?)\*\*", r"\1", cellule_terme)

        if theme_md == "Compléments":
            theme = COMPLEMENTS.get(slug(mots[0]).split("-")[0], "vent")
        else:
            theme = THEMES.get(theme_md)
            if theme is None:
                raise SystemExit(f"Thème inconnu : {theme_md!r} (ajouter à THEMES)")

        # Mots à masquer dans la définition (question « définition → mot »)
        masques = set()
        for m in mots:
            for partie in re.split(r"\s*/\s*", m):
                masques.add(partie)
        masques |= set(re.findall(r"\(ou (\w+)\)", terme))

        entrees.append({
            "id": slug(terme.split("(")[0]),
            "terme": terme,
            "masques": sorted(masques, key=len, reverse=True),
            "definition": md_vers_html(definition),
            "niveau": niveau,
            "theme": theme,
        })

    ids = [e["id"] for e in entrees]
    doublons = {i for i in ids if ids.count(i) > 1}
    if doublons:
        raise SystemExit(f"Identifiants en double : {sorted(doublons)}")

    CIBLE.write_text(
        "// Fichier généré par generer-glossaire.py à partir de\n"
        "// « 06 - Fiches de révision/glossaire-voile.md ». Ne pas modifier à la main.\n"
        "const GLOSSAIRE = "
        + json.dumps(entrees, ensure_ascii=False, indent=1)
        + ";\n",
        encoding="utf-8",
    )
    n3 = sum(e["niveau"] == 3 for e in entrees)
    n2 = len(entrees) - n3
    print(f"{len(entrees)} termes ({n3} essentiels, {n2} utiles) → {n3 * 2 + n2} questions")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Télécharge les images d'illustration du glossaire et génère images.js.

Source : images-sources.json, liste de {"id": <id du terme>, "fichier": "File:… sur
Wikimedia Commons", "raison": <ce que montre l'image>}. Plusieurs termes peuvent
partager le même fichier.

Pour chaque fichier : miniature de 800 px max téléchargée depuis Commons, convertie
en JPEG dans images/, et crédit (auteur, licence) noté dans images.js.

Usage : python3 generer-images.py   (à relancer après chaque modification de images-sources.json)
Nécessite ImageMagick (commande `magick`).
"""
import html
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCE = ICI / "images-sources.json"
DOSSIER = ICI / "images"
CIBLE = ICI / "images.js"
API = "https://commons.wikimedia.org/w/api.php"
AGENT = "glossaire-voile/1.0 (outil de révision)"


def lire(url, essais=6):
    """Télécharge une URL, en attendant puis réessayant si Commons limite le débit (429)."""
    for i in range(essais):
        req = urllib.request.Request(url, headers={"User-Agent": AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == essais - 1:
                raise
            time.sleep(5 * (i + 1))


def appel(params):
    return json.loads(lire(API + "?" + urllib.parse.urlencode({**params, "format": "json"})))


def texte(valeur):
    """Retire le HTML des métadonnées Commons (auteur souvent sous forme de lien)."""
    t = re.sub(r"<[^>]+>", "", valeur or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def nom_local(fichier):
    base = fichier.split(":", 1)[1].rsplit(".", 1)[0]
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base[:60] + ".jpg"


def main():
    sources = json.loads(SOURCE.read_text(encoding="utf-8"))
    DOSSIER.mkdir(exist_ok=True)
    infos = {}
    erreurs = []
    for fichier in sorted({s["fichier"] for s in sources}):
        try:
            rep = appel({
                "action": "query", "titles": fichier, "prop": "imageinfo",
                "iiprop": "url|extmetadata", "iiurlwidth": 800,
            })
            page = next(iter(rep["query"]["pages"].values()))
            ii = page["imageinfo"][0]
        except Exception as e:  # fichier introuvable, réseau…
            erreurs.append(f"{fichier} : {e}")
            continue
        meta = ii.get("extmetadata", {})
        licence = texte(meta.get("LicenseShortName", {}).get("value"))
        local = DOSSIER / nom_local(fichier)
        if not local.exists():
            brut = local.with_suffix(".tmp")
            brut.write_bytes(lire(ii.get("thumburl") or ii["url"]))
            subprocess.run([
                "magick", str(brut), "-background", "white", "-flatten",
                "-resize", "800x600>", "-strip", "-quality", "80", str(local),
            ], check=True)
            brut.unlink()
            time.sleep(0.5)  # rester poli avec l'API
        infos[fichier] = {
            "src": f"images/{local.name}",
            "auteur": texte(meta.get("Artist", {}).get("value")) or "auteur inconnu",
            "licence": licence or "licence inconnue",
            "licenceUrl": texte(meta.get("LicenseUrl", {}).get("value")),
            "page": ii["descriptionurl"],
        }

    images = {}
    for s in sources:
        if s["fichier"] in infos:
            images[s["id"]] = infos[s["fichier"]]

    # Supprime les images qui ne servent plus
    utilises = {Path(i["src"]).name for i in infos.values()}
    for f in DOSSIER.glob("*.jpg"):
        if f.name not in utilises:
            f.unlink()

    CIBLE.write_text(
        "// Fichier généré par generer-images.py à partir de images-sources.json.\n"
        "// Ne pas modifier à la main. Images : Wikimedia Commons, licences libres.\n"
        "const IMAGES = " + json.dumps(images, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"{len(images)} termes illustrés, {len(infos)} images → {CIBLE.name}")
    for e in erreurs:
        print("⚠️ ", e, file=sys.stderr)


if __name__ == "__main__":
    main()

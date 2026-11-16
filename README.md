# Entraînement permis mer (voile)

Cartes de révision pour l'examen théorique du permis mer suisse (OSNM), catégorie voile.

- `index.html` : l'application (ouvrir dans un navigateur, fonctionne aussi sur smartphone).
- `glossaire.js` : glossaire de la voile, généré par `generer-glossaire.py`. Ne pas modifier à la main.
- `questions.js` : questions d'examen, ajoutées au fil des cours.
- `images.js` et `images/` : illustrations des réponses « mot → définition » (Wikimedia Commons, auteur et licence affichés sous l'image), générées par `generer-images.py` à partir de `images-sources.json`. Pour ajouter ou changer une image : modifier `images-sources.json`, puis lancer `python3 generer-images.py`.

La progression (À revoir / Hésitant / Maîtrisé) est enregistrée dans le navigateur, sur chaque appareil séparément.

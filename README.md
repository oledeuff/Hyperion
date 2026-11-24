# HyperION

Chaire IUF 2025–2030 d’Olivier Le Deuff, Université Bordeaux Montaigne, laboratoire MICA.

Le site public articule épistémologie, pratiques et ingénierie de l’hyperinvestigation. Son entrée par un tesseract WebGL est un choix de recherche et de représentation. Les rubriques restent accessibles indépendamment du contexte graphique.

## Deux étapes de publication

- **GitHub Pages — test** : https://oledeuff.github.io/Hyperion/ ; publication de `main/docs`, version identifiée dans `docs/version.json`, pages principales marquées `noindex`.
- **Huma-Num — version validée** : https://hyperion.huma-num.fr/ ; export statique après vérification de la version de test.

Le dépôt reste la source commune. Les identifiants de connexion, le pilotage privé, les budgets et les notes internes n’y ont pas leur place.

## Travailler sur le site

Aucune dépendance npm n’est nécessaire. Python 3 et Node servent les pages et vérifient le JavaScript.

```sh
npm run dev
npm run check
```

Les pages sont servies depuis `docs/`. Les styles et les interactions partagés se trouvent dans `docs/assets/`. Le WebGL de l’accueil est autonome ; il ne charge aucune bibliothèque distante.

La vue claire est proposée par défaut. Un choix explicite de thème est ensuite conservé. Le tesseract montre deux cubes emboîtés, avec six points qui ouvrent directement des rubriques. Sa géométrie et ses zones de clic sont communes au WebGL et à l’alternative SVG ; les accès textuels restent visibles sous la figure.

L’atelier présente les fiches des strates et la boîte à billes de Rouletabille. Les autres essais restent conservés dans le dépôt. Les deux vues retenues disposent de surfaces de lecture claires et d’une commande de pause.

`scripts/build_site.py` produit les pages éditoriales et `docs/data/publications.json`. Il conserve les textes français et anglais des pages historiques à partir du commit de référence, en modifiant leur présentation. Pour actualiser les contenus, modifier le générateur puis lancer :

```sh
python3 scripts/build_site.py
npm run check
```

La source de chaque référence récente figure dans le fichier public de données. MatrioscIA et les travaux antérieurs restent identifiés comme des appuis du programme ; les projets annoncés ne sont pas présentés comme des logiciels achevés.

## Préparer Huma-Num

Après avoir validé et enregistré la version sur GitHub :

```sh
npm run export:humanum
```

Le script produit `dist/humanum/` et un ZIP. Il retire les mentions de test, adapte l’indexation et inscrit le commit source dans `version.json`. Il n’effectue aucune connexion ni aucun transfert.

Dans FileZilla, transférer **le contenu de l’export** dans le répertoire web indiqué par Huma-Num. Déterminer ce répertoire à partir des instructions du service avant le transfert. Vérifier ensuite l’accueil, `version.json`, les liens, le WebGL et les ressources. Conserver l’ancienne version pour pouvoir revenir en arrière.

## Vérifications et limites

Les contrôles automatiques portent sur les liens internes, les fragments, les fichiers locaux, les références publiques, la structure et la syntaxe JavaScript. Les tests Node contrôlent également la géométrie du tesseract, son cadrage, l’épaisseur des arêtes et la sélection de ses points. Vérifier aussi le rendu à petite largeur, le clavier, les thèmes, les langues, la pause et la préférence de réduction des animations dans un navigateur.

Les explorations historiques gardent leur caractère de prototypes et peuvent présenter des limites d’accessibilité. Les pages de lecture et les fiches constituent des accès complémentaires. Aucune conformité RGAA n’est revendiquée.

## Bibliothèques des prototypes historiques

Deux prototypes utilisent Three.js r161 et OrbitControls, conservés dans `docs/assets/vendor/` avec leur licence MIT. L’import de Three.js dans OrbitControls est adapté à ce chemin local. L’accueil utilise directement WebGL et ne dépend pas de ces fichiers.

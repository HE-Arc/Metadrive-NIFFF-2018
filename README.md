# Metadrive-NIFFF-2018

Expérience (jeu) dont le but est de parcourir des trajets de films fantastiques connus à travers des enchaînements de panoramas StreetView à l'aide d'un tapis de danse. [TB]

---

# Utilisation
**Important :** 

Le clonage seul de ce projet ne fournit pas tous les fichiers (ressources) nécessaires au bon fonctionnement de l'application.

Seules les images constituant les parcours ne sont pas sur le dépot, vous pouvez fournir vos propres images à l'application ou télécharger celle proposées plus bas.

## Prérequis

### Python
Python 3.6 est nécessaire pour l'exécution des scripts.

Les commandes `python` et `pip` doivent être disponibles dans la console.

### Envs

L'idéal est de créer un environnement pour la partie Jeu et un second pour la partie Récupération d'images. Ci-dessous, la procédure de mise en place si vous n'êtes pas familier avec Python.

#### Création de l'environnement

Dans le cas de ce projet, le chemin doit correspondre au répertoire *MetadriveGame* ou *StreetviewScrapper* (à effectuer une fois pour chacun).

 `env_nom_du_projet` sera le nom de votre environnement.

```console
python -m venv /chemin/vers/projet/env_nom_du_projet
```
#### Activation de l'environnement

Vous pouvez ensuite activer votre nouvel environnement en vous rendant dans le dossier le contenant (*MetadriveGame* ou *StreetviewScrapper*) (si vous n'y étiez pas déjà) et en lançant la commande suivante :
```console
env_nom_du_projet\Scripts\activate.bat
```
### Dépendances
Il suffit de vous rendre dans le dossier de votre choix (*MetadriveGame* ou *StreetviewScrapper*) après y avoir créé un environnement et l'avoir activé, puis de lancer la commande suivante :

```console
pip install -r requirements.txt
```

Normalement toutes les dépendances liées à cette partie du projet devraient maintenant s'installer dans votre environnement.


## MetadriveGame (Jeu)

### Ressources

Avant d'exécuter le script, il est nécessaire d'alimenter le dossier d'images des niveaux. Le jeu attend les images dans le dossier *maps* respectivement dans les répertoires indiqués dans les fichier XML *levels_en.xml* et *levels_fr.xml*. Les noms des dossiers (`path`) et nombres d'images (`distance`) doivent être respectés.

La version de base fournie ne contient pas d'images et le dossier *maps* est vide. Libre à vous d'ajuster les fichiers XML et mettre vos propre images ou de télécharger l'archive suivante contenant les 3600 images (~ 10 Go) du projet.

[Télécharger l'archive contenant les 3600 images (~10 Go)](https://drive.google.com/file/d/1a8FztGNd4WexBjrNIX84hnoZ0cWFca2S/view?usp=sharing)

### Exécution
Depuis le répertoire *MetadriveGame* avec l'enrivonnement activé :


```console
python metadrive.py
```

Les commandes au clavier sont les touches "O", "K", "L" et "M".

**Important :** L'application est faite pour être affichée en plein écran sur un moniteur vertical en 1080x1920.

### Constantes et paramètres

Un grand nombre de paramètres propres à l'application peuvent être modifiés directement à partir du fichier *const.py*. Il est ainsi très simple de personnaliser l'expérience proposée par le jeu.

## StreeviewScrapper (Récupération d'images)

### scrapper.py
Ceci est la première version de la récupération des images. Elle travaille avec l'API Google et nécessite donc une clé API. Après avoir récupéré votre clé depuis la [Gestion des API Google](https://console.developers.google.com/apis), il faut simplement coller cette dernière dans un fichier texte nommé *api_key.txt* à la racine de *StreetviewScrapper*.

Le script prend en entrée un fichier GPX avec un formatage particulier. C'est pourquoi des exemples sont disponibles dans le dossier *gpx_data*. Ce sont les deux fichiers servant à récupérer les parcours utilisés dans le cadre du projet (le troisième n'étant pas assez dense en image et utilise *scrapper_selenium_straight.py*).

Pour exécuter le script, lancer la commande suivante en remplaçant `gpx_file.gpx` par le nom du fichier GPX de votre choix :

```console
python scrapper.py -i ./gpx_data/gpx_file.gpx -o ./maps/
```

L'option `-i` permet d'indiquer l'emplacement du fichier GPX à traiter.

L'option `-o` permet d'indiquer l'emplacement de sortie des images.

Un dossier *output* contiendra les images brutes telles qu'elles sont récupérées et un second dossier nommé *output_2* contiendra les images redimensionnées et découpées.

### scrapper_selenium.py

Ceci est la seconde version de la récupération des images. Elle fonctionne avec l'outil Selenium et le navigateur Chrome.

Le fonctionnement de ce script est exactement le même que celui indiqué pour *scrapper.py* à l'exception qu'il ne nécessite pas de clé API et ne fournit qu'une seule sortie image dans le dossier *output_2*

```console
python scrapper_selenium.py -i ./gpx_data/gpx_file.gpx -o ./maps/
```

**Remarque :** Il est normal que ce script soit beaucoup plus lent que le précédent. Il se peut également que certaines erreurs non fatales se glissent au début de l'exécution du programme.

### scrapper_selenium_straight.py

Cette version est destinée à la récupération spécifique de la route du troisième niveau puisque ce dernier dispose d'une densité d'image très faible. Cependant, il est possible d'en récupérer d'avantage en se déplaçant directement avec les flèches dans Street View.

C'est pourquoi cette version ne requiert qu'un seul point de départ (inscrit directement dans le script) sous forme de longitude et latitude. Ce script fonctionne uniquement sur les lignes droites puisque l'orientation de la caméra reste fixe sur toute la durée de la capture.

```console
python scrapper_selenium_straight.py -o ./maps/
```

# VTK-labo2

## But du labo

Le but de ce laboratoire est de générer une carte topographique en couleur et en relief à partir des données altimétriques brutes. Ces données sont fournies en annexe sous la forme d'un fichier texte contenant 3001 x 3001 altitudes (en mètres) échantillonnant de manière régulière la zone comprise entre 45 et 47.5 degrés de latitude nord, et 5 et 7.5 degrés de longitude est. 

A vous de concevoir le pipeline de visualisation permettant d'obtenir une image similaire à celle ci contre (qui ne couvre qu'une partie de la zone). 

Vous devez fournir comme résultats

- le code python de votre pipeline complet qui permet de générer une carte similaire à la mienne. Incluez-y des commentaires justifiant vos choix de structures de données, de traitement des données, de lookup table, ... Ce programme doit permettre d'interagir avec la carte créée avec le style Trackball de VTK et par exemple de générer l'image du bas
- Une carte alternative au format PNG en supposant que le niveau de la mer est monté à 370 mètres. La mer doit comme les lacs être représentée en bleu.

Conseils

- Réfléchissez bien au meilleur type de dataset à utiliser pour stocker la structure de la carte 3d. Un bon choix simplifie le travail et minimise la mémoire utilisée. 
- Idéalement, vous devriez centrer votre système de coordonnées sur le centre de la terre. Vous pouvez utiliser l'approximation sphérique pour la forme de la terre. Son rayon moyen est de 6371009 mètres. Réfléchissez à ce que représentent des latitudes et longitudes et utiliser une/des vtkTransform pour calculer vos coordonnées 3D. 
- La position initiale de la caméra et de son point focal doit être fixée par vos soins.

## Choix

### Structure choisie

Afin de minimiser le nombre de point à stocker (les points sont déjà continus), il faut choisir entre :
 - Image data
 - Rectilinear Grid
 - Structured Grid

Hors, la seule qui a une géometrie complétement irrégulière, est la Structured Grid.


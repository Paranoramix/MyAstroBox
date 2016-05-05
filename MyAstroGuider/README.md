# MyAstroGuider

MyAstroGuider est une solution d'autoguidage à faible coût développé dans le cadre du projet MyAstroBox.

Celui-ci propulse un serveur TCP (adressable par socket) de contrôle de l'autoguidage. Il utilise différentes sources d'entrée pour l'autoguidage : 
  - la RaspiCam 
  - une webcam USB

La correction se fait sur le port ST4 de la monture automatiquement.

# Dépendances

MyAstroGuider dépend de plusieurs composants logiciels tierces :

    OpenCV pour la gestion du flux vidéo de la webcam et pour le traitement d'images.
    imutils pour du traitement d'images.

# Licences

MyAstroGuider est un projet OpenSource sous licence MIT. Chaque composant tierce est sous sa propre licence d'utilisation.

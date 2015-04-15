# Introduction

MyAstrobox est un système complet de contrôle d'un observatoire astronomique à bas coût.

L'objectif principal est de maîtriser les coûts de fabrication de l'observatoire, et de fournir un moyen efficace pour piloter celui-ci, à distance. Le pilotage se fait directement à traver un site web local, déployé sur un mini-PC dans l'observatoire. Comme la communauté OpenSource est active pour concevoir et développer des composants permettant de contrôler les différents éléments d'un observatoire, MyAstroBox reprend les différentes briques logicielles pour y intégrer une interface unifiée.


# Dépendances

MyAstrobox dépend de plusieurs composants logiciels tierces :

    NodeJS propule le serveur web pour la consultation et le pilotage de l'observatoire.
    MongoDB est la base de données utilisée pour le stockage des données persistantes.
    AdminLTE est le template utilisé pour le rendu des pages HTML. Il est développé par Almsaeed Studio
    MJPG-Streamer permet le retour vidéo de la caméra intégrée à l'observatoire.
    iAstroHub permet le contrôle de la monture, le pointage, l'autoguidage et la prise de photographies. 


# L'observatoire

L'observatoire est prinicpalement en bois et se pose autour du télescope et de la monture. Il peut être construit de différentes tailles, en fonction de l'instrument que l'on souhaite abriter.

Le toit ouvrant est télescopique. Il se compose de 3 parties s'emboîtant lors de l'ouverture. Le déplacement des parties mobiles est basé sur de simples glissières disponibles dans le commerce. L'étanchéité est assurée par des joints.

Le toît est motorisé avec un moteur pas à pas entrainant une vis déplaçant un chariot. Le chariot mobile est fixé au toit coulissant.

La station météo intègre des éléments classiques :

    un capteur de température et d'humidité (DHT22),
    un anémomètre LaCrosse Technology TX20U,
    un capteur de températoure infrarouge (MLX90614).

L'interface entre ces capteurs et le mini-PC est assurée par une carte Arduino Nano.

En plus de ces capteurs météorologiques, d'autres capteurs sont présents dans l'abri :

    un ampèremetre pour mesurer la consommation globale de l'observatoire,
    un capteur de niveau de charge de la batterie,
    des capteurs de fin de course pour l'ouverture et la fermeture du toît ouvrant.


# Licences

MyAstrobox est un projet OpenSource sous licence MIT. Chaque composant tierce est sous sa propre licence d'utilisation.

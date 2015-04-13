# MyAstroBox Project

L'objectif est de fournir un système de contrôle automatisé d'un abri de télescope ("home made") à coût réduit.

Pour cela, on s'appuiera sur différents composants "low cost" : 

une carte Arduino Nano pour la lecture des données fournies par les différents capteurs

un (ou deux) Raspberry PI (2) / B+ pour fournir l'interface de communication avec l'électronique de l'abri.
  
  
L'abri de télescope est fabriqué en bois et possède un toit coulissant télescopique (construction prévue en mai / juin).

Le toit coulisse avec un entrainement par vis. Ce système a déjà été réalisé pour faire des timelapses avec translation de l'appareil photo.

L'abri possède sa propre station météo :
  capteur de température et d'humidité,
  anémomètre,
  capteur de température IR pour mesurer la couverture nuageuse.

L'abri propose également un retour vidéo basé sur une RaspiCam No IR (sans filtre IR).
La caméra démarre automatique à chaque détection de mouvement.


Pour contrôler les différents organes du télescope (monture, guidage, APN, etc.), on se basera sur la librairie indilib (www.indilib.org).


Naturellement, comme on parle de "low cost", le budget total ne doit pas dépasser les 500 €.


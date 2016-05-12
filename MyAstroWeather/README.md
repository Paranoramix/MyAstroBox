# MyAstroWeather

MyAstroWeather est une station météo simple développée dans le cadre du projet MyAstroBox.

Celui-ci propulse un serveur TCP (adressable par socket) de interroger les différents capteurs météo. Les capteurs disponibles sont :
  - un anémomètre + girouette La Crosse Technology TX20,
  - un capteur de température et d'humidité relative DHT22,
  - un capteur de température infrarouge MLX90614.

# Dépendances

MyAstroWeather dépend de plusieurs composants logiciels tierces :

    Wiring Pi pour permettre la communication avec les ports GPIO d'un Raspberry PI,
    le driver BCM2835 pour permettre la communication sur le port I²C.

# Installation
    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo rpi-update
    $ sudo reboot
    $ sudo apt-get install git-core
    $ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
    $ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    $ sudo apt-get install libxvidcore-dev libx264-dev
    $ sudo apt-get install libgtk2.0-dev
    $ sudo apt-get install libatlas-base-dev gfortran
    $ sudo apt-get install python2.7-dev python3-dev
    
    $ cd ~
    $ git clone git://git.drogon.net/wiringPi
    $ cd wiringPi
    $ git pull origin
    $ ./build
    
    $ cd ~
    $ wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
    $ tar zxvf bcm2835-1.50.tar.gz
    $ cd bcm2835-1.50
    $ ./configure
    $ make
    $ sudo make check
    $ sudo make install
    
    $ sudo raspi-config
         **under Advanced Options - enable Device Tree
    $ sudo reboot
    
    $ cd ~
    $ git clone git@github.com:Paranoramix/MyAstroBox.git
    $ cd MyAstroBox/MyAstroWeather
    $ gcc tcp_server.c -o ../MyAstroWeather -lm -lbcm2835 -lpthread -lwiringPi
    
# Licences

MyAstroWeather est un projet OpenSource sous licence MIT. Chaque composant tierce est sous sa propre licence d'utilisation.

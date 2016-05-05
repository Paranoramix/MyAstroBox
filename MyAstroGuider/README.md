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

# Installation

    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo rpi-update
    $ sudo reboot
    $ sudo apt-get install build-essential git cmake pkg-config
    $ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
    $ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    $ sudo apt-get install libxvidcore-dev libx264-dev
    $ sudo apt-get install libgtk2.0-dev
    $ sudo apt-get install libatlas-base-dev gfortran
    $ sudo apt-get install python2.7-dev python3-dev
    
    $ cd ~
    $ wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.0.0.zip
    $ unzip opencv.zip
    $ wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.0.0.zip
    $ unzip opencv_contrib.zip
    
    $ wget https://bootstrap.pypa.io/get-pip.py
    $ sudo python get-pip.py
    
    $ pip install numpy
    
    $ cd ~/opencv-3.0.0/
    $ mkdir build
    $ cd build
    $ cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D INSTALL_C_EXAMPLES=ON \
        -D INSTALL_PYTHON_EXAMPLES=ON \
        -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.0.0/modules \
        -D BUILD_EXAMPLES=ON ..
    
    $ make -j4
    $ sudo make install
    $ sudo ldconfig
    
    $ ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
    
    $ cd /usr/local/lib/python3.4/site-packages/
    $ sudo mv cv2.cpython-34m.so cv2.so
    
    $ ln -s /usr/local/lib/python3.4/site-packages/cv2.so cv2.so
    
# Licences

MyAstroGuider est un projet OpenSource sous licence MIT. Chaque composant tierce est sous sa propre licence d'utilisation.

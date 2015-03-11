Open Meteo Data PI plotter
=========

Plotting utility for Open Meteo Data ( www.openmeteodata.org ) data

Dependencies
=========
sudo apt-get install libfreetype6-dev

sudo apt-get install freetype*

sudo apt-get install libfreetype6-dev libxft-dev

sudo apt-get install  python-dev

sudo apt-get install g++

sudo apt-get install git

git clone git://github.com/matplotlib/matplotlib.git

cd matplotlib

sudo python setup.py install

sudo apt-get install python-pip

sudo pip install Pydap

cd ..
wget -O basemap-1.0.7.tar.gz http://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz?r=&ts=1382557269&use_mirror=netcologne

tar xvf basemap-1.0.7.tar.gz

cd basemap-1.0.7

cd geos-3.3.3

export GEOS_DIR=/usr/local

./configure --prefix=$GEOS_DIR

make 

sudo make install

cd ..

sudo python setup.py install

sudo apt-get install  python-gdal


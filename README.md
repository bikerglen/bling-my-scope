# bling-my-scope

## Installing

sudo apt update

sudo apt upgrade

sudo apt install libopencv-dev python3-opencv

python3 -c "import cv2; print(cv2.__version__)"

sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel

sudo python3 -m pip install --force-reinstall adafruit-blinka

## Connecting

Connect a strip of neopixels to GPIO D18 on the Raspberry Pi.

## Configuring

Adjust the gamma variable to get the desired effect. 1.25 works well for a scope waveform window, 2.8 works well for normal video.

Set the number of pixels along each of the scope using the n???Pixels variables. Pixels start in the top left corner when facing the front of the scope and continue in a clockwise direction around the scope.

## Running

sudo python3 bling_800x600.py

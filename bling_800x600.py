import numpy as np
import cv2 as cv
import socket
import math
import board
import neopixel

# gamma correction value
# try values from 0.75 to 0.5 depending on desired effect
# 1.25 works well for scope video, 2.8 works well for normal video
gamma = 2.8

# pixel configuration
# number of pixels on each side running clockwise starting at top left
nTopPixels    = 56
nRightPixels  = 40
nBottomPixels = 56
nLeftPixels   = 40

# use output image
# set to true to enable a debug image on the screen
useOutputImage = True

# calculate gamma lookup table
gamma8 = bytearray (256)
for i in range (0,256):
    gamma8[i] = round (255.0*pow(i/255.0,gamma))

# calculate total number of pixels
nTotalPixels  = nTopPixels + nRightPixels + nBottomPixels + nLeftPixels

# initialize pixel control on D18 GPIO pin
pixels = neopixel.NeoPixel(board.D18, nTotalPixels, auto_write=False)

# open video capture device
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# set resolution to native resolution of scope, 800 x 600
cap.set(cv.CAP_PROP_FRAME_WIDTH,  800)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 600)

# main loop
while True:
    # capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    if useOutputImage:
        # erase output image
        outimage = np.zeros((360,440,3), np.uint8)

    # crop to waveform area of scope display
    frame = frame[61:61+478,25:25+640]

    # make smaller to speed things up a bit
    frame = cv.resize(frame, (400, 320))

    # copy input frame to center of output frame
    if useOutputImage:
        outimage[20:340,20:420] = frame[0:320,0:400]

    # pick 60px tall/wide strips along each edge of the waveform area
    topStrip = frame[  0: 60,  0:400]
    botStrip = frame[260:320  ,0:400]
    lefStrip = frame[  0:320,  0: 60]
    rigStrip = frame[  0:320,340:400]

    # resize those strips to number of pixels
    # scaling hints from github / Andrew Mohawk / aurora
    topPix = cv.resize (topStrip, (nTopPixels, 1),    interpolation=cv.INTER_AREA)
    botPix = cv.resize (botStrip, (nBottomPixels, 1), interpolation=cv.INTER_AREA)
    lefPix = cv.resize (lefStrip, (1, nLeftPixels),   interpolation=cv.INTER_AREA)
    rigPix = cv.resize (rigStrip, (1, nRightPixels),  interpolation=cv.INTER_AREA)

    # add pixel colors to output image
    if useOutputImage:

        # draw top outputs in output window
        x0 = 20                                                     # left edge
        for x in range (0, nTopPixels):
            x1 = round (20 + (x+1) * 400.0/nTopPixels)              # right edge
            color = (int(topPix[0][x][0]), int(topPix[0][x][1]), int(topPix[0][x][2]))
            cv.rectangle (outimage, (x0, 0), (x1, 19), color, -1)
            x0 = x1                                                 # next left edge

        # draw right outputs in output window
        y0 = 20                                                     # top edge
        for y in range (0, nRightPixels):
            y1 = round (20 + (y+1) * 320.0/nRightPixels)            # bottom edge
            color = (int(rigPix[y][0][0]), int(rigPix[y][0][1]), int(rigPix[y][0][2]))
            cv.rectangle (outimage, (420, y0), (439, y1), color, -1)
            y0 = y1                                                 # next top edge

        # draw bottom outputs in output window
        x0 = 20                                                     # left edge
        for x in range (0, nBottomPixels):
            x1 = round (20 + (x+1) * 400.0/nBottomPixels)           # right edge
            color = (int(botPix[0][x][0]), int(botPix[0][x][1]), int(botPix[0][x][2]))
            cv.rectangle (outimage, (x0, 340), (x1, 359), color, -1)
            x0 = x1                                                 # next left edge

        # draw left outputs in output window
        y0 = 20                                                     # top edge
        for y in range (0, nLeftPixels):
            y1 = round (20 + (y+1) * 320.0/nLeftPixels)             # bottom edge
            color = (int(lefPix[y][0][0]), int(lefPix[y][0][1]), int(lefPix[y][0][2]))
            cv.rectangle (outimage, (0, y0), (19, y1), color, -1)
            y0 = y1                                                 # next top edge

    # map top pixels into neopixels
    firstPixel = 0
    for pixel in range (0, nTopPixels):
        pixels[firstPixel+pixel] = ( gamma8[topPix[0][pixel][2]], \
                                     gamma8[topPix[0][pixel][1]], \
                                     gamma8[topPix[0][pixel][0]] )

    # map right pixels into neopixels
    firstPixel = nTopPixels
    for pixel in range (0, nRightPixels):
        pixels[firstPixel+pixel] = ( gamma8[rigPix[pixel][0][2]], \
                                     gamma8[rigPix[pixel][0][1]], \
                                     gamma8[rigPix[pixel][0][0]] )

    # map bottom pixels into neopixels
    firstPixel = nTopPixels + nRightPixels
    for pixel in range (0, nBottomPixels):
        pixels[firstPixel+pixel] = ( gamma8[botPix[0][nBottomPixels-pixel-1][2]], \
                                     gamma8[botPix[0][nBottomPixels-pixel-1][1]], \
                                     gamma8[botPix[0][nBottomPixels-pixel-1][0]] )

    # map left pixels into neopixels
    firstPixel = nTopPixels + nRightPixels + nBottomPixels
    for pixel in range (0, nLeftPixels):
        pixels[firstPixel+pixel] = ( gamma8[lefPix[nLeftPixels-pixel-1][0][2]], \
                                     gamma8[lefPix[nLeftPixels-pixel-1][0][1]], \
                                     gamma8[lefPix[nLeftPixels-pixel-1][0][0]] )

    # send neopixels on rpi gpio
    pixels.show ()
    
    # display the output frame
    if useOutputImage:
        cv.imshow('output', outimage)
        if cv.waitKey(1) == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()


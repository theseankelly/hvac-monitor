#!/usr/bin/env python

import cv2
import numpy as np

def find_leds(im):
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 0
    params.maxThreshold = 400
    params.minDistBetweenBlobs = 1
    params.filterByArea = True
    params.minArea = 0
    params.maxArea = 25
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    params.filterByColor = False

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect((im.astype(np.uint8)))

    pts = np.asarray([[p.pt[1], p.pt[0]] for p in keypoints])
    np.sort(pts, axis=0)
    return pts

def parse_image_hardcoded_positions(im):
    """
    Parses image based on hardcoded position information.

    Temporary workaround so I can still collect data until I sort out
    exposure/whitebalance issues on the raspicam.

    Do not change any offsets/sizes unless the camera moves!
    """

    #
    # Crop a fixed ROI and convert to grayscale
    #
    im_roi = im[246:296,675:705]
    im_roi_gray = cv2.cvtColor(im_roi, cv2.COLOR_BGR2GRAY)

    #
    # Fixed centroid/offsets for each LED.
    # row 0: green/power
    # row 1: zone 1 call
    # row 2: zone 1 valve
    # row 3: zone 2 call
    # etc
    #
    led_centroids = \
        np.array(
            [[7,12],
             [14,12],
             [14,19],
             [20,12],
             [20,19],
             [28,12],
             [28,19],
             [35,12],
             [35,19]])

    status = np.zeros((4,2))
    t = 10
    w = 1

    c = led_centroids[0]
    if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
        c = led_centroids[1]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[0,0] = 1

        c = led_centroids[2]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[0,1] = 1

        c = led_centroids[3]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[1,0] = 1

        c = led_centroids[4]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[1,1] = 1

        c = led_centroids[5]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[2,0] = 1

        c = led_centroids[6]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[2,1] = 1

        c = led_centroids[7]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[3,0] = 1

        c = led_centroids[8]
        if (np.mean(im_roi_gray[c[0]-w:c[0]+w+1,c[1]-w:c[1]+w+1]) > t):
            status[3,1] = 1
    else:
        raise RuntimeError('Unable to parse power/status LED!')

    return status

def parse_image(im):
    """
    Parses an input image for LEDs
    """

    # TODO - potentially need to crop an ROI
    im = im[60:130,310:340]

    #
    # Convert to HSV space for filtering -- the input image
    # should be a standard OpenCV 'BGR' image. Intentionally
    # converting using 'RGB2HSV' as a 'trick' to make the filtering
    # code a little easier to read.
    #
    # (The colors of interest become green, cyan, and purple
    # instead of green, red and yellow. This way, we don't need to
    # handle red wrapping around from 0 to 255.)
    #
    im_hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)

    #
    # Create color masks
    #
    lower_green = np.array([30,15,150])
    upper_green = np.array([80,255,255])
    mask_green = cv2.inRange(im_hsv, lower_green, upper_green)
    green_leds = find_leds(mask_green)

    lower_cyan = np.array([85,20,150])
    upper_cyan = np.array([120,255,255])
    mask_cyan = cv2.inRange(im_hsv, lower_cyan, upper_cyan)
    cyan_leds = find_leds(mask_cyan)

    lower_purple = np.array([120,100,150])
    upper_purple = np.array([160,255,255])
    mask_purple = cv2.inRange(im_hsv, lower_purple, upper_purple)
    purple_leds = find_leds(mask_purple)

    status = np.zeros((4,2))

    # Total hack
    zone1 = green_leds[0,0] + 5.5
    zone2 = green_leds[0,0] + 11
    zone3 = green_leds[0,0] + 16.5
    zone4 = green_leds[0,0] + 22

    for row in cyan_leds:
        if np.abs(row[0] - zone1) <= 2:
            status[0,0] = 1
        elif np.abs(row[0] - zone2) <= 2:
            status[1,0] = 1
        elif np.abs(row[0] - zone3) <= 2:
            status[2,0] = 1
        elif np.abs(row[0] - zone4) <= 2:
            status[3,0] = 1

    for row in purple_leds:
        if np.abs(row[0] - zone1) <= 2:
            status[0,1] = 1
        elif np.abs(row[0] - zone2) <= 2:
            status[1,1] = 1
        elif np.abs(row[0] - zone3) <= 2:
            status[2,1] = 1
        elif np.abs(row[0] - zone4) <= 2:
            status[3,1] = 1

    return status


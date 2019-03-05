#!/usr/bin/env python

import numpy as np
import cv2

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
    t = 20
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

    # Crop a fairly liberal ROI
    im = im[170:330,630:755]

    #
    # Convert to HSV space for filtering
    #
    im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    #
    # Threshold on the 'value' channel of HSV because it seems to give a more
    # even response
    # TODO: This should probably be a grayscale image. Need to learn about
    # gamma and adjusting for intensities.
    #
    mask = (im_hsv[:,:,2] > 75).astype(np.uint8)*255
    leds = find_leds(mask)

    if (len(leds) < 1):
        raise RuntimeError('No LEDs segmented')

    #
    # Find and strip out the green power LED (assume it's the lowest row count)
    #
    power_led_idx = np.argmin(leds[:,0])
    power_led = leds[power_led_idx, :]
    leds = np.delete(leds, power_led_idx, axis=0)

    #
    # Sanity test - see if a 3x3 patch of pixels around the 'power led'
    # does in fact fall within the green color space.
    #
    lower_green = np.array([20,0,10])
    upper_green = np.array([110,255,255])
    mask_green = cv2.inRange(im_hsv, lower_green, upper_green)
    patch = mask_green[
        int(power_led[0])-2:int(power_led[0])+3,
        int(power_led[1])-2:int(power_led[1])+3]
    if (len(patch[patch > 0].flatten()) < 1):
        raise RuntimeError('Power LED failed color check.')

    #
    # Synthesize the ideal LED offsets from the power LED
    # Spacing is hardcoded and depends on resolution and distance.
    #
    led_spacing = (7,7)
    zone_rows_approx = np.linspace(
        power_led[0] + led_spacing[0],
        power_led[0] + led_spacing[0]*4,
        4)

    zone_cols_approx = np.linspace(
        power_led[1],
        power_led[1] + led_spacing[1],
        2)

    #
    # Validate that the original ROI is big enough
    # and that we're not potentially dropping LEDs
    #
    if ((zone_rows_approx > im.shape[0]).any() or
        (zone_cols_approx > im.shape[1]).any()):
        raise RuntimeError('Expected LED offsets exceed image limits.')

    status = np.zeros((4,2), dtype=np.uint8)

    #
    # For each 'found' LED figure out which approximated LED it's
    # 'closest' to and mark the value in the status array
    #
    for led in leds:
        row = (np.abs(led[0] - zone_rows_approx)).argmin()
        col = (np.abs(led[1] - zone_cols_approx)).argmin()

        #
        # Ensure the closest match we found is within half of the expected
        # LED spacing. If not, we can't really guarantee the match is valid.
        #
        if ((np.abs(led[0] - zone_rows_approx[row]) > (led_spacing[0]/2)) or
            (np.abs(led[1] - zone_cols_approx[col]) > (led_spacing[1]/2))):
            raise RuntimeError('Closest match for LED exceeds tolerance.')
        status[row, col] = 1

    return status

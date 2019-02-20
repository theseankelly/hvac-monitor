#!/usr/bin/env python

import cv2
import datetime
import time
import schedule

import hvacmon.camera
import hvacmon.imgproc
import hvacmon.db

def capture_state():
    print("Capturing State...")

    #
    # Capture a frame
    #
    with hvacmon.camera.Camera(rotation=180) as cam:
        im, timestamp = cam.get_frame()

    #
    # Parse the status from the image
    #
    status = hvacmon.imgproc.parse_image(im)

    #
    # Temporary -- log all 'raw' data from the camera until
    # some confidence has been gained.
    #
    cv2.imwrite('/home/pi/data/hvac/%s.jpg' % timestamp, im)

    #
    # Insert the data into the database
    #
    hvacmon.db.append_zone_data(timestamp, status)

def main():
    schedule.every(15).seconds.do(capture_state)
    while 1:
        schedule.run_pending()
        time.sleep(1)

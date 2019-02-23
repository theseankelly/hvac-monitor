#!/usr/bin/env python

import cv2
import datetime
import time
import dateutil.parser

import hvacmon.camera
import hvacmon.imgproc
import hvacmon.db

def main():

    with hvacmon.camera.Camera(rotation=180) as cam:

        # Get the original snapshot of the system
        im, prev_timestamp = cam.get_frame()
        prev_status = hvacmon.imgproc.parse_image_hardcoded_positions(im)

        print("(%s) Initial system state:" % prev_timestamp)
        print(prev_status)

        while 1:
            time.sleep(5)
            im, timestamp = cam.get_frame()

            try:
                status = hvacmon.imgproc.parse_image_hardcoded_positions(im)
            except:
                print("(%s) Error processing image!" % timestamp)
                cv2.imwrite('/home/pi/data/hvac/failures/%s.jpg' % filename, im)
                continue

            dt = (dateutil.parser.parse(timestamp) -
                  dateutil.parser.parse(prev_timestamp)).total_seconds()

            filename  = dateutil.parser.parse(timestamp).strftime(
                "%Y-%m-%d_%H-%M-%S")

            if (~(status == prev_status).all()):
                print("(%s) Status change detected!" % timestamp)
                print(status)
                cv2.imwrite('/home/pi/data/hvac/statechange/%s.jpg' % filename, im)

                hvacmon.db.append_zone_data(prev_timestamp, timestamp, prev_status)
                prev_status = status
                prev_timestamp = timestamp

            elif (dt > 60):
                print("(%s) No status change after 1 min, logging..." % timestamp)
                ts = dateutil.parser.parse(timestamp).strftime(
                    "%Y-%m-%d_%H-%M-%S.jpg")
                cv2.imwrite('/home/pi/data/hvac/timeouts/%s.jpg' % filename, im)

                hvacmon.db.append_zone_data(
                    prev_timestamp, timestamp, prev_status)
                prev_status = status
                prev_timestamp = timestamp

            else:
                #print("(%s) No status change..." % timestamp)
                pass


#!/usr/bin/env python
import sys
import argparse
import time
import dateutil
import dateutil.parser
import schedule
import numpy as np
import cv2

import hvacmon.camera
import hvacmon.imgproc
import hvacmon.db
import hvacmon.weather

class HvacMgr():
    def __init__(self, cam):
        self.cam_ = cam
        im, self.prev_timestamp_ = self.cam_.get_frame()
        try:
            self.prev_status_ = hvacmon.imgproc.parse_image(im)
        except:
            self.prev_status_ = np.zeros((4,2))
        print("(%s) Initial state: %s" % (self.prev_timestamp_,
                                          self.prev_status_.flatten())

    def run(self):
        im, timestamp = self.cam_.get_frame()

        t1_str = dateutil.parser.parse(self.prev_timestamp_).strftime(
            "%Y-%m-%d_%H-%M-%S")
        t2_str = dateutil.parser.parse(timestamp).strftime(
            "%Y-%m-%d_%H-%M-%S")

        filename = t1_str + "_" + t2_str

        dt = (dateutil.parser.parse(timestamp) -
              dateutil.parser.parse(self.prev_timestamp_)).total_seconds()

        try:
            status = hvacmon.imgproc.parse_image(im)
        except:
            print("(%s) Error processing image!" % timestamp)
            cv2.imwrite('/home/pi/data/hvac/failures/%s.png' % filename, im)
            self.prev_status_ = np.zeros((4,2))
            self.prev_timestamp_ = timestamp
            return

        if (~(status == self.prev_status_).all()):
            print("(%s) Status change detected: %s" % (timestamp,
                                                       status.flatten()))
            cv2.imwrite('/home/pi/data/hvac/statechange/%s.png' % filename, im)

            hvacmon.db.append_zone_data(
                self.prev_timestamp_, timestamp, self.prev_status_)
            self.prev_status_ = status
            self.prev_timestamp_ = timestamp

        elif (dt > 60):
            print("(%s) No status change after 1 min, logging..." % timestamp)
            cv2.imwrite('/home/pi/data/hvac/timeouts/%s.png' % filename, im)

            hvacmon.db.append_zone_data(
                self.prev_timestamp_, timestamp, self.prev_status_)
            self.prev_status_ = status
            self.prev_timestamp_ = timestamp

def temperature():
    timestamp, temperature = hvacmon.weather.get_temperature()
    print("(%s) Got temperature reading: %f" % (timestamp, temperature))
    hvacmon.db.append_temperature_data(timestamp, temperature)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rotation", nargs='?', default=0, type=int,
        help="Camera rotation in degrees", required=False)
    args = parser.parse_args()
    return args

def run():
    args = parse_args()

    with hvacmon.camera.Camera(rotation=args.rotation) as cam:
        hvac_mgr = HvacMgr(cam)
        schedule.every(5).seconds.do(hvac_mgr.run)
        schedule.every(15).minutes.do(temperature)
        while 1:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    sys.exit(run())

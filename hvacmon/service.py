#!/usr/bin/env python
import sys
import argparse
import time
import os
import dateutil
import dateutil.parser
import schedule
import numpy as np
import cv2

import hvacmon.camera
import hvacmon.imgproc
import hvacmon.db
import hvacmon.weather
import hvacmon.util

class Service:
    """
    Service wrapper for running HVAC monitor continuously.

    Methods
    -------
    __init__(outdir, darksky_api_key, lat, lon, camera_rotation=0, debug=False)
        Initializes the system for use. Creates output directories if needed.
    run()
        Main entry point to the service - blocks indefinitely.
    sample_hvac_status()
        Gets current state of HVAC system and logs information to database.
    sample_temperature()
        Gets current temperature from DarkSky and logs information to database.
    """

    def __init__(self, outdir, darksky_api_key, lat, lon,
                 camera_rotation=0, debug=False):
        """
        Initializes the system for use. Creates output directories if needed.

        Parameters
        ----------
        outdir : str
            Output directory to log information/images.

        darksky_api_key : str
            Developer key for the DarkSky API.

        lat : float
            Latitude of location to sample weather information.

        lon : float
            Longitude of location to sample weather information.

        camera_rotation : int
            Mounting rotation of camera (one of 90, 180, 270).

        debug : boolean
            Whether to run in 'debug' mode, which logs pngs of captured images
            to output for future analysis/debug. This can consume large amounts
            of disk over time.
        """
        self._outdir = os.path.basename(outdir)
        if not os.path.exists(self._outdir):
            print("Creating outdir: %s" % self._outdir)
            os.makedirs(self._outdir)
        if (self._debug):
            self._failpath = os.path.join(self._outdir, 'failures')
            self._changepath = os.path.join(self._outdir, 'statechange')
            self._timeoutpath = os.path.join(self._outdir, 'timeouts')
            if not os.path.exists(self._failpath):
                print("Creating outdir: %s" % self._failpath)
                os.makedirs(self._failpath)
            if not os.path.exists(self._changepath):
                print("Creating outdir: %s" % self._changepath)
                os.makedirs(self._changepath)
            if not os.path.exists(self._timeoutpath):
                print("Creating outdir: %s" % self._timeoutpath)
                os.makedirs(self._timeoutpath)

        self._camera = hvacmon.camera.Camera(camera_rotation)
        self._db = hvacmon.db.Database(filepath=self._outdir)
        self._weather = hvacmon.weather.Weather(darksky_api_key, lat, lon)
        self._debug = debug

        self._prev_timestamp = hvacmon.util.get_timestamp()
        self._prev_status = np.zeros((4,2))

    def run(self):
        """
        Main entry point to the service - blocks indefinitely.

        HVAC status is sampled every 5 seconds.
        Temperature is sampled every 15 minutes.
        """
        self._prev_timestamp, im = self._camera.get_frame()
        try:
            self._prev_status = hvacmon.imgproc.parse_image(im)
        except RuntimeError as e:
            print("(%s) Error capturing initial state: %s"
                % (self._prev_timestamp, e))

        print("(%s) Initial state: %s" % (self._prev_timestamp,
                                          self._prev_status.flatten()))

        schedule.every(5).seconds.do(self.sample_hvac_status)
        schedule.every(15).minutes.do(self.sample_temperature)
        while 1:
            schedule.run_pending()
            time.sleep(1)

    def sample_hvac_status(self):
        """
        Gets current state of HVAC system and logs information to database.

        Previous state information is logged to the database when:
            - A change in state is detected.
            - There was an error processing the image (prev state is captured).
            - No state change was observed after a fixed period of time.

        If the debug flag was set on the object, images are saved as pngs.
        """
        timestamp, im = self._camera.get_frame()
        if (self._debug):
            t1_str = dateutil.parser.parse(self._prev_timestamp).strftime(
                "%Y-%m-%d_%H-%M-%S")
            t2_str = dateutil.parser.parse(timestamp).strftime(
                "%Y-%m-%d_%H-%M-%S")
            filename = t1_str + "_" + t2_str

        dt = (dateutil.parser.parse(timestamp) -
              dateutil.parser.parse(self._prev_timestamp)).total_seconds()

        try:
            status = hvacmon.imgproc.parse_image(im)
        except RuntimeError as e:
            print("(%s) Error processing image: %s" % (timestamp, e))
            if (self._debug):
                cv2.imwrite(
                    os.path.join(self._failpath, '%s.png' % filename), im)
            self._prev_status = np.zeros((4,2))
            self._prev_timestamp = timestamp
            return

        if (~(status == self._prev_status).all()):
            print("(%s) Status change detected: %s" % (timestamp,
                                                       status.flatten()))
            if (self._debug):
                cv2.imwrite(
                    os.path.join(self._changepath, '%s.png' % filename), im)

            self._db.append_zone_data(
                self.prev_timestamp_, timestamp, self.prev_status_)
            self.prev_status_ = status
            self.prev_timestamp_ = timestamp

        elif (dt > 60):
            print("(%s) No status change after 1 min, logging..." % timestamp)
            if (self._debug):
                cv2.imwrite(
                    os.path.join(self._timeoutpath, '%s.png' % filename), im)

            self._db.append_zone_data(
                self.prev_timestamp_, timestamp, self.prev_status_)
            self.prev_status_ = status
            self.prev_timestamp_ = timestamp


    def sample_temperature(self):
        """
        Gets current temperature from DarkSky and logs information to database.
        """
        try:
            timestamp, temperature = self._weather.get_temperature()
            print("(%s) Got temperature reading: %f" % (timestamp, temperature))
            self._db.append_temperature_data(timestamp, temperature)
        except:
            e = sys.exc_info()[0]
            print("Unable to reach DarkSky Service: %s" % e)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rotation", nargs='?', default=0, type=int,
        help="Camera rotation in degrees", required=False)
    parser.add_argument("-d", "--debug", action='store_true',
        help="Run in debug mode (saves raw images to disk)")
    parser.add_argument("-o", "--outdir", type=str, default='/var/lib/hvacmon',
        help="Output directory to store database and debug images")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    #
    # Weather parameters stored as env vars.
    #
    if 'DARKSKY_API_KEY' not in os.environ:
        raise RuntimeError('Environment variable DARKSKY_API_KEY not set.')
    else:
        darksky_api_key = os.environ['DARKSKY_API_KEY']

    if 'HVACMON_LAT' not in os.environ:
        raise RuntimeError('Environment variable HVACMON_LAT not set.')
    else:
        latitude = float(os.environ['HVACMON_LAT'])

    if 'HVACMON_LON' not in os.environ:
        raise RuntimeError('Environment variable HVACMON_LON not set.')
    else:
        longitude = float(os.environ['HVACMON_LON'])

    #
    # Create and run the service.
    #
    srv = Service(
        args.outdir, darksky_api_key, latitude, longitude,
        args.rotation, args.debug)
    srv.run()

if __name__ == '__main__':
    sys.exit(main())

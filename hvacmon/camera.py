#!/usr/bin/env python
import cv2
import datetime
import io
import picamera
import picamera.array
import time

class Camera:
    def __init__(self, resolution=(640, 480), rotation=0, framerate=24,
                 exposure_mode='sports'):
        self._resolution = resolution
        self._rotation = rotation
        self._framerate = framerate
        self._exposure_mode = exposure_mode

    def __enter__(self):
        self._camera = picamera.PiCamera()
        self._camera.resolution = self._resolution
        self._camera.rotation = self._rotation
        self._camera.framerate = self._framerate
        self._camera.exposure_mode = self._exposure_mode
        # Camera warmup time
        time.sleep(2)

    def __exit__(self, type, value, traceback):
        self._camera.close()

    def get_frame(self):
        """
        Returns an OpenCV image captured from the camera
        """

        #
        # Generate local ISO 8601 timestamp with timezone info
        # Courtesy of https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
        #
        utc_offset_sec = \
            time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        timestamp = datetime.datetime.now().replace(
            tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

        stream = io.BytesIO()
        with picamera.array.PiRGBArray(self._camera) as stream:
            self._camera.capture(stream, format='bgr')
            image = stream.array

        return image, timestamp
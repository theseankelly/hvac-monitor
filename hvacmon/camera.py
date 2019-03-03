#!/usr/bin/env python
import cv2
import datetime
import io
import picamera
import picamera.array
import time
import numpy as np
import hvacmon.util

class Camera:
    def __init__(self, resolution=(640, 480), rotation=0):
        self._resolution = resolution
        self._rotation = rotation

    def __enter__(self):
        self._camera = picamera.PiCamera()
        self._camera.rotation = self._rotation
        self._camera.exposure_mode = 'off'
        self._camera.shutter_speed = 16000
        time.sleep(2)
        return self

    def __exit__(self, type, value, traceback):
        self._camera.close()

    def get_frame(self):
        """
        Returns an OpenCV image captured from the camera
        """
        timestamp = hvacmon.util.get_timestamp()
        stream = io.BytesIO()
        with picamera.array.PiRGBArray(self._camera) as stream:
            self._camera.capture(stream, format='bgr')
            image = stream.array

        return image, timestamp


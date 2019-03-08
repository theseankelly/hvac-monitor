#!/usr/bin/env python
import io
import time
import picamera
import picamera.array
import hvacmon.util

class Camera:
    """
    Helper for configuring and obtaining images off raspberry pi camera.

    Wraps the picamera module with specific settings.

    Methods
    -------
    __init__(rotation=0)
        Initializes the camera object and configures imager settings.
    get_frame()
        Reads frame into an openCV compatible buffer.
    """

    def __init__(self, rotation=0):
        """
        Initializes the object and configures the imager

        Parameters
        ----------
        rotation : int
            Camera rotation to apply. Must be one of 0, 90, 180, or 270.
        """
        self._resolution = (1280, 720)
        self._exposure_mode = 'off'
        self._shutter_speed = 16000
        self._rotation = rotation
        with picamera.PiCamera() as camera:
            camera.resolution = self._resolution
            camera.rotation = self._rotation
            camera.exposure_mode = self._exposure_mode
            camera.shutter_speed = self._shutter_speed
        time.sleep(2)

    def get_frame(self):
        """
        Reads frame into an openCV compatible buffer.

        Returns
        -------
        timestamp : str
            Approximate timestamp associated with the frame capture.

        image : 3 dimensional ndarray
            NumPy array containing image data. Rows and Cols match configured
            imager size. Channels are in 'bgr' order for use with OpenCV.
        """
        timestamp = hvacmon.util.get_timestamp()
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.capture(stream, format='bgr')
                image = stream.array

        return timestamp, image

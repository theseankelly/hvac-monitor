import cv2
import h5py
import numpy as np
from os import listdir
import pytest
from hvacmon import imgproc

def test_eval(test_dset):
    with h5py.File('data/hvacmon_data.h5', 'r') as f:
        g = f['annotated']
        im = g[test_dset][:]
        annotated_status = g[test_dset].attrs['status']

    status = imgproc.parse_image(im)
    assert (status == annotated_status).all()

def pytest_generate_tests(metafunc):
    with h5py.File('data/hvacmon_data.h5', 'r') as f:
        g = f['annotated']
        dsets = list(g.keys())
    metafunc.parametrize("test_dset", dsets)
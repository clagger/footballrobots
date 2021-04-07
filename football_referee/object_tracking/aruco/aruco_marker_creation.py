import os

import numpy as np
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


## Aruco Marker Creation (5 Marker, 1 Calibration Tag, 4 Car Tags)

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
os.getcwd()

for i in range(1 , 10):
    img = aruco.drawMarker(aruco_dict,i,700)
    plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
    plt.axis("off")
    plt.savefig("football_referee/object_tracking/aruco/aruco_marker/tag_"+str(i)+".png", bbox_inches='tight')

import json
import logging
import os

import cv2
from cv2 import aruco
import numpy as np

from football_robots.object_tracking.hsv_object_tracker import HSVObjectTracker
# from football_referee.object_tracking.camera.aruco_camera_calibration import CameraCalibration
from football_referee.object_tracking.camera.threaded_video_stream import ThreadedVideoStream
from football_referee.object_tracking.aruco.aruco_tracker import ArucoTracker
from football_robots.player.player import *


def get_hsv_values_from_file(path, color):
    """
    Reads the hsv values from a json
    :param path: path to json
    :param color: color of the object to track
    :return:
    """
    with open(path, "r") as read_file:
        hsv_values = json.load(read_file)
        lower = []
        upper = []
        for i in hsv_values["{0}_lower_bound".format(color)]:
            lower.append(hsv_values["{0}_lower_bound".format(color)][i])
        for i in hsv_values["{0}_upper_bound".format(color)]:
            upper.append(hsv_values["{0}_upper_bound".format(color)][i])
    return [tuple(lower), tuple(upper)]


def load_coefficients(path):
    """
    Loads camera matrix and distortion coefficients.
    :param path: path to file
    :return:
    """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode("K").mat()
    dist_matrix = cv_file.getNode("D").mat()

    cv_file.release()
    return [camera_matrix, dist_matrix]


class Tracker:
    def start_tracking(self, game_data: GameData, color):
        """
        Init ball tracking and aruco marker tracking
        :param game_data: game_data object
        :param color: color of the ball to track
        """
        hsv_mask_path = "object_tracking/data/ball_hsv.json"
        # Reading and setting hsv values
        lower_bound, upper_bound = get_hsv_values_from_file(hsv_mask_path, color)
        # Init ball detection
        ball_tracker = HSVObjectTracker(hsv_lower_bound=lower_bound, hsv_upper_bound=upper_bound, draw_circle=True,
                                        ball_width=5, show_coords=False)
        # Load camera calibration matrices
        path_to_calibration_matrice_file = "object_tracking/data/aruco_camera_calibration"
        # path_to_image_folder = "data/images/calibration_images"
        a_tracker = ArucoTracker(path_to_calibration_matrice_file, game_data)

        ### Start Tracking Frame by Frame and update position data

        vs = ThreadedVideoStream(src=1).start()
        initialized = False
        print('TRACKER: Initializing Field')
        while True:
            # grab the current frame
            # If the src is a video capture vs.read() returns (true,image)
            frame = vs.read()

            if frame is None:
                print('no frame found')
                break

            # ARUCO tracking
            if not initialized:
                initialized = a_tracker.init_field(frame)
                cv2.imshow("Frame", frame)
            else:
                a_tracker.find_markers(frame)
                # Ball Tracking
                frame = ball_tracker.draw_object_mask_to_frame(frame)
                # map ball coordinates to origin aruco marker's coordinate system and set them in the gameobject
                ball_x, ball_y = np.round(np.fabs(ball_tracker.get_ball_position() - a_tracker.origin_corners[0][0]), 2)
                game_data.ball_coordinates.pos_x, game_data.ball_coordinates.pos_y = float(ball_x), float(ball_y)
                cv2.imshow("Frame", frame)

            # press q to quit :)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                vs.stop()
                cv2.destroyAllWindows()
                break

        print("Quitting app.")

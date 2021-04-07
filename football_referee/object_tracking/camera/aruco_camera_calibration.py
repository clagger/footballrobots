# This class was used to initially calibrate the camera. Afterwards the results were saved to a file.
# The saved configuration gets loaded everytime the project is restarted.

import os
import cv2
import numpy as np


class CameraCalibration:
    critera = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    def __init__(self, square_size, path_to_images, width, height):
        """
        :param square_size: size of the printed calibration test image
        :param path_to_images: path to the necessary calibration images
        :param width:
        :param height:
        """
        self.square_size = square_size
        self.path_to_images = path_to_images
        self.width = width
        self.height = height

    def calibrate(self, criteria=critera):
        """
         Apply camera calibration operation for images in the given directory path.
        :param criteria: criteria for camera calibration
        :return:
        """
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
        objp = np.zeros((self.height * self.width, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.width, 0:self.height].T.reshape(-1, 2)

        objp = objp * self.square_size

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        for fname in os.listdir(self.path_to_images):
            img_path = self.path_to_images + fname
            img = cv2.imread(img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (self.width, self.height), None)

            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, (self.width, self.height), corners2, ret)

        if len(imgpoints) == 0:
            return print("No objects have been detected")

        self.ret, self.mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        return [self.ret, self.mtx, dist, rvecs, tvecs]


def save_coefficients(mtx_m, dist_m, path):
    """
    Save the camera matrix and the distortion coefficients to given path/file.
    :param mtx_m:   positioning matrix
    :param dist_m: distance
    :param path: path where the file should be saved
    :return:
    """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    cv_file.write("K", mtx_m)
    cv_file.write("D", dist_m)
    # note you *release* you don't close() a FileStorage object
    cv_file.release()


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
    return camera_matrix, dist_matrix



## ONLY FOR TESTING   ##
#path_to_image_folder = "../data/images/c_images_logitech/"
#cc = CameraCalibration(0.035, path_to_image_folder, 9, 6)
#print(os.getcwd())
#[ret, mtx, dist, rvecs, tvecs] = cc.calibrate()
#save_coefficients(mtx, dist, "../data/aruco_camera_calibration")
#print("Done. RMS: " + str(ret))

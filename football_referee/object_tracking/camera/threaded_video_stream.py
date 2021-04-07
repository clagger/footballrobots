from threading import Thread

import cv2


class ThreadedVideoStream:
    def __init__(self, src=0):
        """
        init the threaded video stream class
        :param src: src is the number of the input device   it can vary if
        multiple cameras are connected to the same pc (e.g. integrated webcam + usb webcam)
        """
        # if src is a string it should be a path to the input video
        # if src is a number it should be the correct video input device
        print('VIDEO: Initializing Video Stream')
        self.stream = cv2.VideoCapture(src)
        print('VIDEO: Finished initializing Video Stream')
        print('VIDEO: Setting Video width to 1400')
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1400)
        print('VIDEO: Setting Video height to 700')
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)
        print('VIDEO: Disabling Camera Autofocus')
        self.stream.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        print('VIDEO: Starting video stream')
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        """
        starts the video stream threaded by calling the update method.
        :return:
        """
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """
         Starts the video stream and runs till stopped. Is called in start().
        :return:
        """
        print('VIDEO: Video Stream started')
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """
        reads the next frame
        :return:
        """
        return self.frame

    def stop(self):
        """
        stops the video stream
        :return:
        """
        self.stopped = True

    def release(self):
        """
        Releases the capturing device.
        :return:
        """
        self.stream.release()

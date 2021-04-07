import cv2
import time
import datetime
import imutils
import numpy as np


class VIDEO:
    """ class that represents video capture of the robot

    """
    def __init__(self, record_video=True, video_name='video.avi', lower_color=(20, 80, 20), upper_color=(30, 255, 255)):
        """ constructor of the class

        :param record_video: boolean; if video should be recorded
        :param video_name: string; name of the saved file
        :param lower_color: (int, int, int); HSV value of the lower border of captured object
        :param upper_color: (int, int, int); HSV value of the upper border of captured object
        """
        self.video = cv2.VideoCapture(0)

        # We need to check if camera 
        # is opened previously or not 
        if not self.video.isOpened():
            print("Error reading video file")

            # We need to set resolutions.
        # so, convert them from float to integer. 
        self.frame_width = int(self.video.get(3))
        self.frame_height = int(self.video.get(4))
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.size = (self.frame_width, self.frame_height)
        # Below VideoWriter object will create 
        # a frame of above defined The output  
        # is stored in file with the name stored in self.video_name.
        self.record_video = record_video
        if self.record_video:
            self.video_result = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'MJPG'), self.fps, self.size)

        # define the lower and upper boundaries of the colored
        # ball in the HSV color space
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.x = 0
        self.y = 0
        self.is_ball_visible = False
        self.radius = 10

    def find_ball(self):
        """ looks for ball in video frame and marks it

        """
        ret, frame = self.video.read()

        if ret:

            # ------- detect object --------
            # resize the frame, blur it, and convert it to the HSV
            # color space
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            center = None
            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((self.x, self.y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # only proceed if the radius meets a minimum size
                if radius > self.radius:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(self.x), int(self.y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

            self.is_ball_visible = len(cnts) > 0 and radius > self.radius
            # ------------------------------      

            # add timestamp
            ts = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            cv2.putText(frame, "x: {}, y: {}, object: {}".format(round(self.x, 2), round(self.y, 2),
                                                                 len(cnts) > 0 and radius > 10),
                        (10, frame.shape[0] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            # Write the frame into the 
            # file 'filename.avi'
            cv2.imwrite("test.jpg", frame)
            if self.record_video:
                self.video_result.write(frame)

        else:
            print('no frame found')

    def save_video(self):
        """ saves the video that was captured

        """
        # Release the video capture and 
        # video write objects 
        self.video.release()
        if self.record_video:
            self.video_result.release()
        print("The video was successfully saved")

    def get_ball_position_and_state(self):
        """ returns position of ball and if ball is visible

        :return: (int, int, boolean); position of ball and if ball is visible
        """
        return (self.x, self.y, self.is_ball_visible)

    def set_boundaries(self, lower_boundary, upper_boundary):
        """ sets lower and upper hsv boundary

        :param lower_boundary: (int, int, int) hsv value of lower boundary
        :param upper_boundary: (int, int, int) hsv value of upper boundary
        """
        self.lower_color = lower_boundary
        self.upper_color = upper_boundary

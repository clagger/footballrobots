import cv2
import imutils


class HSVObjectTracker:
    """ class that represents an HSV object tracker

    all colors that are between lower_bound and upper_bound in the HSV spectrum are tracked

    """
    def __init__(self, hsv_lower_bound, hsv_upper_bound, draw_circle, ball_width, show_coords=False):
        """ constructor of the class

        :param hsv_lower_bound: [int, int, int]; HSV values of the lower bound color
        :param hsv_upper_bound: [int, int, int]; HSV values of the upper bound color
        :param draw_circle: boolean; if a circle should be drawn around the tracked object
        :param ball_width: int; width of the ball
        :param show_coords: boolean; if the coordinates of the tracked object should be shown
        """
        self.hsv_lower_bound = hsv_lower_bound
        self.hsv_upper_bound = hsv_upper_bound
        self.draw_circle = draw_circle
        self.ball_width = ball_width
        self.show_coords = show_coords
        self.center = None
        self.radius = 0
        self.x = 0
        self.y = 0
        self.m = None
        self.mask = None

    def detect_object(self, frame):
        """
        find contours in the mask and initialize the current
        (x, y) center of the ball

        :param frame: ?; video frame that is used to detect object
        :return: modified frame
        """
        contours = cv2.findContours(self.mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        self.center = None
        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            ((self.x, self.y), self.radius) = cv2.minEnclosingCircle(c)
            self.m = cv2.moments(c)
            self.center = (int(self.m["m10"] / self.m["m00"]), int(self.m["m01"] / self.m["m00"]))
            # c an only detect 1 ball at all times
            # only proceed if the radius meets a minimum size
            # print(self.radius)
            if self.radius > self.ball_width and self.draw_circle:
                frame = self.draw_circle_on_frame(frame)
            if self.show_coords:
                frame = self.show_coordinates(frame)
        return frame

    def show_coordinates(self, frame):
        """ draws object coordinates on the frame

        :param frame: ?; video frame that is used to detect object
        :return: modified frame
        """
        coords = "X: " + str(self.x) + " Y: " + str(self.y)
        org = (50, 50)
        colors = (255, 0, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, coords, org, font, 1, colors, 2, cv2.LINE_AA)
        return frame

    def draw_circle_on_frame(self, frame):
        """ draws circle around found object on frame

        :param frame: ?; video frame that is used to detect object
        :return: modified frame
        """
        cv2.circle(frame, (int(self.x), int(self.y)), int(self.radius),
                   (0, 255, 255), 2)
        cv2.circle(frame, self.center, 5, (0, 0, 255), -1)
        return frame

    def create_mask(self, hsv):
        """ creates an HSV mask to find object

        :param hsv: ?;
        :return:
        """
        # Creating the mask
        self.mask = cv2.inRange(hsv, self.hsv_lower_bound, self.hsv_upper_bound)
        self.mask = cv2.erode(self.mask, None, iterations=2)
        self.mask = cv2.dilate(self.mask, None, iterations=2)

    def draw_object_mask_to_frame(self, frame):
        """ draws HSV mask to find object

        :param frame: ?; video frame that is used to detect object
        :return: frame
        """
        # frame = imutils.resize(frame)
        if frame is None:
            print("Frame is None")
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        # Change color space from RGB to HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        self.create_mask(hsv)

        frame = self.detect_object(frame)
        return frame

    def get_ball_position(self):
        """ getter function that returns coordinates of found object

        :return: float, float; coordinates of found object
        """
        return self.x, self.y

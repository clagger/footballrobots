import Adafruit_PCA9685 # Import the library used to communicate with PCA9685
import time
import sys


class SERVO:
    """ class that represents servor of the camera

    original code (found in Adeept AWR 4WD Documentation) was adapted to be used in a class
    """
    def __init__(self):
        """ constructor of the class

        """
        self.pwm = Adafruit_PCA9685.PCA9685()  # Instantiate the object used to control the PWM
        self.pwm.set_pwm_freq(50)  # Set the frequency of the PWM signa

    def set_angle(self, percent):
        """ sets angle of camera servo

        :param percent: int; percentage of camera angle
        """
        angle = int(round(percent * 1.2 + 100, 0))
        if angle < 100:
            angle = 100
        if angle > 220:
            angle = 220
        self.pwm.set_pwm(0, 0, angle)

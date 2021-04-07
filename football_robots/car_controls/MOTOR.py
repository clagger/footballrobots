import time
import RPi.GPIO as GPIO # Import the library used to control GPIO

class MOTOR:
    """ class that represents the motor of the robot

    original code (found in Adeept AWR 4WD Documentation) was adapted to be used in a class
    """
    def __init__(self):
        """ constructor of the MOTOR class

        """
        GPIO.setwarnings(False)
        GPIO.cleanup() # Reset the high and low levels of the GPIO port
        #The following code defines the GPIO used to control the L298N chip. This definition is different for different Raspberry Pi driver boards.
        self.Motor_A_EN = 17
        self.Motor_B_EN = 4
        self.Motor_A_Pin1 = 27
        self.Motor_A_Pin2 = 18
        self.Motor_B_Pin1 = 21
        self.Motor_B_Pin2 = 26
        self.setup()

    def motorStop(self):
        """ stops all motors

        """
        GPIO.output(self.Motor_A_Pin1, GPIO.LOW)
        GPIO.output(self.Motor_A_Pin2, GPIO.LOW)
        GPIO.output(self.Motor_B_Pin1, GPIO.LOW)
        GPIO.output(self.Motor_B_Pin2, GPIO.LOW)
        GPIO.output(self.Motor_A_EN, GPIO.LOW)
        GPIO.output(self.Motor_B_EN, GPIO.LOW)


    def setup(self):
        """ GPIO initialization, GPIO motor cannot be controlled without initialization

        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Motor_A_EN, GPIO.OUT)
        GPIO.setup(self.Motor_B_EN, GPIO.OUT)
        GPIO.setup(self.Motor_A_Pin1, GPIO.OUT)
        GPIO.setup(self.Motor_A_Pin2, GPIO.OUT)
        GPIO.setup(self.Motor_B_Pin1, GPIO.OUT)
        GPIO.setup(self.Motor_B_Pin2, GPIO.OUT)
        self.motorStop()  # Avoids automatic motor rotation after initialization
        try:  # Try is used here to avoid errors due to repeated setting of PWM
            self.pwm_A = GPIO.PWM(self.Motor_A_EN, 1000)
            self.pwm_B = GPIO.PWM(self.Motor_B_EN, 1000)
        except:
            pass

    def motor_A(self, direction, speed):
        """ controls motor of port A (left motor pair)

        :param direction: int; 1 -> forward. -1 -> backward
        :param speed: int; speed of motor rotation
        """
        if direction == -1:
            GPIO.output(self.Motor_A_Pin1, GPIO.HIGH)
            GPIO.output(self.Motor_A_Pin2, GPIO.LOW)
            self.pwm_A.start(100)
            self.pwm_A.ChangeDutyCycle(speed)
        if direction == 1:
            GPIO.output(self.Motor_A_Pin1, GPIO.LOW)
            GPIO.output(self.Motor_A_Pin2, GPIO.HIGH)
            self.pwm_A.start(100)
            self.pwm_A.ChangeDutyCycle(speed)

    def motor_B(self, direction, speed):
        """ controls motor of port B (right motor pair)

        :param direction: int; 1 -> forward. -1 -> backward
        :param speed: int; speed of motor rotation
        """
        if direction == 1:
            GPIO.output(self.Motor_B_Pin1, GPIO.HIGH)
            GPIO.output(self.Motor_B_Pin2, GPIO.LOW)
            self.pwm_B.start(100)
            self.pwm_B.ChangeDutyCycle(speed)
        if direction == -1:
            GPIO.output(self.Motor_B_Pin1, GPIO.LOW)
            GPIO.output(self.Motor_B_Pin2, GPIO.HIGH)
            self.pwm_B.start(100)
            self.pwm_B.ChangeDutyCycle(speed)

    def move(self, direction, speed):
        """ moves robot forward or backward

        :param direction: int; 1 -> forward. -1 -> backward
        :param speed: int; speed of motor rotation
        """
        self.motor_A(direction, speed)
        self.motor_B(direction, speed)

    def rotate(self, direction, speed):
        """ moves robot left or right

        :param direction: int; 1 -> left. -1 -> right
        :param speed: int; speed of motor rotation
        """
        self.motor_A(direction, speed)
        self.motor_B(direction * (-1), speed)

    def __del__(self):
        """ destructor function of MOTOR class

        stops motor if class gets destroyed
        """
        self.motorStop()
        GPIO.cleanup()


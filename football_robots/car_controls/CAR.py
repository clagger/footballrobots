from football_robots.car_controls.MOTOR import MOTOR
from football_robots.car_controls.LED import LED
from football_robots.car_controls.SERVO import SERVO
from football_robots.car_controls.ULTRASONIC import ULTRASONIC
from football_robots.car_controls.VIDEO import VIDEO
from queue import Queue
from threading import Thread
import time


class CAR:
    """
    A class that represents the robot car
    """

    def __init__(self, light=(0, 20, 0), start_video=False):
        """ constructor for the CAR class

        :param light: list; represents RGB values of the LED
        :param start_video: boolean; if video should be started or not
        """
        self.initiate_classes(start_video)
        self.camera_angle = 100  # range is from 0% (top) to 100% (bottom)
        self.speed = 100  # range is from 0% to 100%
        self.red_light = light[0]  # range is from 0 to 255
        self.green_light = light[1]  # range is from 0 to 255
        self.blue_light = light[2]  # range is from 0 to 255
        self.set_camera_angle(self.camera_angle)
        self.set_light_color(self.red_light, self.green_light, self.blue_light)

    def initiate_classes(self, start_video):
        """ initiates the classes that control different parts of the robot

        :param start_video: boolean; if video should be started or not
        """
        self.LED = LED()  # responsible for LED control
        self.MOTOR = MOTOR()  # responsible for robot movement
        self.SERVO = SERVO()  # responsible for camera servo
        self.ULTRASONIC = ULTRASONIC()  # responsible for ultrasonic measurement
        self.ultrasonic_queue = Queue()  # queue that stores measured distances
        if start_video:
            self.VIDEO = VIDEO()  # controls videostream
            self.video_queue = Queue()
            self.stop_video_queue = Queue()

    # MOTOR wrapper functions

    def move(self, direction):
        """ lets car move forward or backward

        :param direction: int; 1 -> car moves forward. -1 -> car moves backwards
        """
        self.MOTOR.move(direction, self.speed)

    def rotate(self, direction):
        """ lets car rotate left or right

        :param direction: int; 1 -> car rotates left. -1 -> car rotates right
        """
        self.MOTOR.rotate(direction, self.speed)

    def stop(self):
        """ stops movement of the car

        IMPORTANT!
        This is the only command that stops the movement of the car.

        Example:
            car.rotate(-1)
            time.sleep(1)
            car.stop()

        This example lets car rotate to the right for one second and then stops it
        """
        self.MOTOR.motorStop()

    def set_speed(self, speed):
        """ sets the default speed of the car

        :param speed: int; sets speed. Min: 0, Max: 100

        TIPP: Speed of 100 with full battery is faster as Speed of 100 with not full battery
        """
        if 100 >= speed >= 0:
            self.speed = speed

    def increase_speed(self):
        """ increases speed by 10

        """
        if self.speed >= 90:
            self.speed = 100
        else:
            self.speed += 10

    def decrease_speed(self):
        """ decreases speed by 10

        """
        if self.speed <= 10:
            self.speed = 0
        else:
            self.speed -= 10

    def get_speed(self):
        """ returns current speed of the car

        :return: speed of car
        """
        return self.speed

    #  LED wrapper funtions
    def set_light_color(self, red, green, blue):
        """ sets the color of the LED of the car

        :param red: int; red color value. Min: 0, Max: 255
        :param green: int; green color value. Min: 0, Max: 255
        :param blue: int; blue color value. Min: 0, Max: 255
        """
        self.red_light = red
        self.green_light = green
        self.blue_light = blue
        self.LED.set_color(red, green, blue)

    def get_light_color(self):
        """ returns current color of LED

        :return: int, int, int; RGB
        """
        return self.red_light, self.green_light, self.blue_light

    # SERVO wrapper functions
    def set_camera_angle(self, angle):
        """ sets angle of camera servo

        :param angle: int; angle of camera servo
        """
        self.camera_angle = angle
        self.SERVO.set_angle(angle)

    def get_camera_angle(self):
        """ returns camera angle

        :return: int; angle of camera
        """
        return self.camera_angle

    def camera_down(self):
        """ moves camera down

        """
        if self.camera_angle >= 90:
            self.camera_angle = 100
        else:
            self.camera_angle += 10
        self.SERVO.set_angle(self.camera_angle)

    def camera_up(self):
        """ moves camera up

        """
        if self.camera_angle <= 10:
            self.camera_angle = 0
        else:
            self.camera_angle -= 10
        self.SERVO.set_angle(self.camera_angle)

    # ULTRASONIC wrapper functions
    def get_object_distance(self):
        """ returns distance to closest object

        :return: float; distance to object in metre
        """
        return self.ultrasonic_queue.get()

    def measure_distance(self):
        """ measures distance to nearest object and puts it in ultrasonic queue

        """
        while 1:
            time.sleep(0.1)
            distance = self.ULTRASONIC.get_distance()
            self.ultrasonic_queue.put(distance)

    def start_ultrasonic(self):
        """ starts ultrasonic measurement

        """
        ulsonic_thread = Thread(target=self.measure_distance, daemon=True)
        ulsonic_thread.start()

    # VIDEO wrapper functions
    def get_object_coordinates(self):
        """ returns object coordinates according to video frame and if ball is visible

        :return: (int, int, boolean)
        """
        return self.video_queue.get()

    def find_object(self):
        """ looks for object

        """
        while 1:
            self.VIDEO.find_ball()
            coordinates_and_state = self.VIDEO.get_ball_position_and_state()
            self.video_queue.put(coordinates_and_state)
            if self.stop_video_queue.get():
                break
        print("")
        print("saving video")
        self.VIDEO.save_video()

    def start_video(self):
        """ starts video thread

        """
        video_thread = Thread(target=self.find_object, daemon=True)
        video_thread.start()

    def should_stop_video(self, stop):
        """ defines if video should be stopped

        :param stop: boolean; if video should be stopped
        """
        self.stop_video_queue.put(stop)

    def set_video_boundaries(self, lower_boundary, upper_boundary):
        """ sets color boundaries of object

        :param lower_boundary: (int, int, int); lower hsv color boundary
        :param upper_boundary: (int, int, int); upper hsv color boundary
        """
        self.VIDEO.set_boundaries(lower_boundary, upper_boundary)

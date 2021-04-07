import logging
import CAR
import time

"""
tests functionality of ultrasonic.
Robot drives to object if distance is bigger than 20 cm and drives away if distance is smaller than 10 cm

IMPORTANT!
script only works on robot
"""
if __name__ == "__main__":
    car = CAR.CAR()
    car.start_ultrasonic()
    while 1:
        time.sleep(0.1)
        while car.get_object_distance() <= 0.1:
            car.move(-1)
        while car.get_object_distance() >= 0.2:
            car.move(1)
        car.stop()

import CAR
import time

""" script that tests the functionalities of the robot

IMPORTANT!
Only usable on robot
"""

CAR = CAR.CAR()

# check if LED works

print("LED is now red")
CAR.set_light_color(20, 0, 0)
time.sleep(1)

print("LED is now green")
CAR.set_light_color(0, 20, 0)
time.sleep(1)

print("LED is now blue")
CAR.set_light_color(0, 0, 20)
time.sleep(1)

# check if SERVO works

print("SERVO at top")
CAR.set_camera_angle(0)
time.sleep(1)

print("SERVO at bottom")
CAR.set_camera_angle(100)
time.sleep(1)

print("SERVO in the middle")
CAR.set_camera_angle(50)
time.sleep(1)

# check if MOTOR works

print("drive forward")
CAR.move(1)
time.sleep(1)
CAR.stop()

print("drive backward")
CAR.move(-1)
time.sleep(1)
CAR.stop()

print("rotate left")
CAR.rotate(1)
time.sleep(1)
CAR.stop()

print("rotate right")
CAR.rotate(-1)
time.sleep(1)
CAR.stop()

# check if ULTRASONIC works
print('')
print('place an object in front of the ultrasonic sensor')
time.sleep(1)
print(3)
time.sleep(1)
print(2)
time.sleep(1)
print(1)
time.sleep(1)
CAR.start_ultrasonic()
print('move object')
print('')
end_time = time.time() + 5
while time.time() < end_time:
    print(CAR.get_object_distance())
    time.sleep(0.1)

print('')
print("Test finished")




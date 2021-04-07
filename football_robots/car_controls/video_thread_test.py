import CAR
import time

"""
Tests functionality of video stream and robot ball detection
"""
if __name__ == "__main__":
    car = CAR.CAR(light=(0, 0, 0))
    car.set_video_boundaries((32, 106, 42), (90, 255, 255))
    car.start_ultrasonic()
    car.start_video()
    start = time.time()
    try:
        while 1:
            car.should_stop_video(False)
            ball_position = car.get_object_coordinates()
            if ball_position[0] <= 300 and not ball_position[2]:
                car.set_speed(80)
                car.rotate(1)
            elif ball_position[0] >= 340 and not ball_position[2]:
                car.set_speed(80)
                car.rotate(-1)
            elif 0 < car.get_object_distance() < 3:
                car.set_speed(100)
                car.move(1)
            else:
                car.stop()

    except KeyboardInterrupt:
        car.stop()
        car.should_stop_video(True)
        time.sleep(1)

# created a *threaded* video stream, allow the camera sensor to warmup,
# this class wes purly for testing different settings
from __future__ import print_function

import cv2
import imutils

from football_referee.object_tracking.camera.fps import FPS
from football_referee.object_tracking.camera.threaded_video_stream import ThreadedVideoStream


def test_fps(video_stream):
    fps = FPS().start()
    # loops till 1000 frames passed can be lowered but results in less accurate fps
    if isinstance(video_stream, ThreadedVideoStream):
        print("\n[INFO] Testing threaded video stream")
    else:
        print("\n[INFO] Testing non-threaded video stream")
    # loops till 500 frames have been renderd
    while fps._numFrames < 500:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        # if also impacts performance but impact is not relevant in this case
        if isinstance(video_stream, ThreadedVideoStream):
            frame = video_stream.read()
        else:
            _, frame = video_stream.read()

        frame = imutils.resize(frame, width=400)
           # check to see if the frame should be displayed to our screen
        if show_video:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
        # update the FPS counter
        fps.update()
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    # do a bit of cleanup
    cv2.destroyAllWindows()
    if isinstance(video_stream, ThreadedVideoStream):
        video_stream.stop()
    else:
        video_stream.release()


# and start the FPS counter
# HUGE impact on FPS
show_video = False

threaded_vs = ThreadedVideoStream(src=0).start()
test_fps(threaded_vs)

non_threaded_vs = cv2.VideoCapture(0)
test_fps(non_threaded_vs)

import datetime


class FPS:
    def __init__(self):
        """
        Initializes the FPS classed. This class was used to benchmark different video device settings.
        """
        self._start = None
        self._end = None
        self._numFrames = 0
        self._currentFPS = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()


    #should be used in loops
    def get_fps(self):
        # always iterate over the last 10 fps and calculate how much time it took
        if self._numFrames == 0:
            #set initial start time
            self.start()

        self.update()
        if self._numFrames == 30:
            self.stop()
            self._currentFPS = self.fps()
            self._numFrames = 0
            return self._currentFPS
        return self._currentFPS



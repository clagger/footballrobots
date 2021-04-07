from rpi_ws281x import *

class LED:
    """ class that represents LED of the robot

    """
    def __init__(self):
        """ constructor of LED class

        original code can be found in Adeept AWR 4WD Documentation.
        Refactored to be used in a class.
        """
        self.LED_COUNT = 6  # total number of LEDs
        self.LED_PIN = 12  # Set to the input pin number of the LED group
        self.LED_FREQ_HZ = 800000
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 255
        self.LED_INVERT = False
        self.LED_CHANNEL = 0
        # Use the configuration item above to create a strip
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT,
                                       self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()

    def set_color(self, R, G, B):
        """  sets the color of all LEDs

        :param R: int; Red color value. Min: 0, Max: 255
        :param G: int; Green color value. Min: 0, Max: 255
        :param B: int; Blue color value. Min: 0, Max: 255
        """
        color = Color(R, G, B)

        # Only one LED light color can be set at a time, so we need to do a loop
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()

    def set_single_pixel(self, pixel, R, G, B):
        """ sets the color of a single LED pixel

        :param pixel: int; index of chosen pixel. Min:0, Max: 11
        :param R: int; Red color value. Min: 0, Max: 255
        :param G: int; Green color value. Min: 0, Max: 255
        :param B: int; Blue color value. Min: 0, Max: 255
        """
        color = Color(R, G, B)
        self.strip.setPixelColor(pixel, color)
        self.strip.show()

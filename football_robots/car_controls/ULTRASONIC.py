import football_robots.car_controls.ultra as ultra


class ULTRASONIC:
    """ class that represents ultrasonic

    """
    def __init__(self):
        """ constructor of the class

        """
        self.Tr = 11  # Pin number of input terminal of ultrasonic module
        self.Ec = 8  # Pin number of output terminal of ultrasonic module

    def get_distance(self):
        return ultra.checkdist(self.Tr, self.Ec)

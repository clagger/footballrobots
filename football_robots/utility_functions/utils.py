import json
import cv2
import numpy as np


def calculate_angle(vector1_x, vector1_y, vector2_x, vector2_y):
    """ calculates the angle between two vectors

    :param vector1_x: float; x part of first vector
    :param vector1_y: float; y part of second vector
    :param vector2_x: float; x part of first vector
    :param vector2_y: float; y part of second vector
    :return: float; angle between two vectors in degree
    """
    return np.round(np.degrees(np.arccos((vector1_x * vector2_x + vector1_y * vector2_y) /
                                  (np.sqrt(vector1_x ** 2 + vector1_y ** 2) *
                                   np.sqrt(vector2_x ** 2 + vector2_y ** 2)))), 2)
                                   

def get_init_values(path):
    """ loads data from json file in given path

    :param path: string; path to json file
    :return: dictionary; data from json file
    """
    with open(path, "r") as read_file:
        init = json.load(read_file)
    return init


def get_distance(point_1, point_2):
    """ calculates distance between two BasicCoordinates

    :param point_1: BasicCoordinate; coordinate 1
    :param point_2: BasicCoordinate; coordinate 2
    :return: float; distance
    """
    dist = np.sqrt((point_1.pos_x - point_2.pos_x) ** 2 + (
            point_1.pos_y - point_2.pos_y) ** 2)
    return dist


def load_coefficients(path):
    """ Loads camera matrix and distortion coefficients. """
    # FILE_STORAGE_READ
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode("K").mat()
    dist_matrix = cv_file.getNode("D").mat()

    cv_file.release()
    return camera_matrix, dist_matrix


def calc_init_position_ball(game_data):
    """ calculates position of the ball at the start using intersection of two lines

    :param game_data: GameData; data of the game
    :return: float, float; coordinates of the position
    """
    line1 = [[game_data.goal_1.post_1.pos_x, game_data.goal_1.post_1.pos_y],
             [game_data.goal_2.post_2.pos_x, game_data.goal_2.post_2.pos_y]]

    line2 = [[game_data.goal_1.post_2.pos_x, game_data.goal_1.post_2.pos_y],
             [game_data.goal_2.post_1.pos_x, game_data.goal_2.post_1.pos_y]]
    return line_intersection(line1, line2)


def line_intersection(line1, line2):
    """ calculates the intersection of two lines

    :param line1: [[float, float],[float, float]]; start and end point of first line
    :param line2: [[float, float],[float, float]]; start and end point of second line
    :return: float, float; coordinates of the intersection
    """
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return float(x), float(y)


def get_distance_of_point_to_line(point, line_point1, line_point2):
    """ calculates the distance of a given point to a line given its start and end point

    :param point: [float, float]; coordinates of the point
    :param line_point1: [float, float]; coordinates of the start point of the line
    :param line_point2: [float, float]; coordinates of the end point of the line
    :return: float; distance of point to line
    """
    return np.linalg.norm(np.cross(line_point2-line_point1, line_point1-point))/np.linalg.norm(line_point2-line_point1)


def is_out_of_bounds(player, destination):
    """ calculates if a given bound is outside of the valid field

    :param player: Player; player that 'knows' the game field
    :param destination: [float, float]; coordinates of the point
    :return: boolean; if point is not valid
    """
    x_boundary_width = (player.game_data.goal_1.post_2.pos_x - player.game_data.goal_2.post_2.pos_x) / 10
    x_boundary_lower = x_boundary_width + (
                player.game_data.goal_2.post_2.pos_x + player.game_data.goal_2.post_1.pos_x) / 2
    x_boundary_higher = - x_boundary_width + (
                player.game_data.goal_1.post_2.pos_x + player.game_data.goal_1.post_1.pos_x) / 2

    post_distance = player.game_data.goal_1.post_2.pos_y - player.game_data.goal_1.post_1.pos_y
    y_boundary_lower = player.game_data.goal_1.post_1.pos_y - 0.5 * post_distance
    y_boundary_higher = player.game_data.goal_1.post_2.pos_y + 0.5 * post_distance

    return destination[0] < x_boundary_lower or destination[0] > x_boundary_higher or destination[1] < y_boundary_lower or destination[1] > y_boundary_higher

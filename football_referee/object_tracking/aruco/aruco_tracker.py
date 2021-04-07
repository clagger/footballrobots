import cv2
import cv2
import cv2.aruco as aruco

from football_robots.player.player import *
from football_robots.utility_functions.utils import calculate_angle, load_coefficients, calc_init_position_ball, \
    get_distance


def translate_to_custom_origin(new_origin_corners, point_corners):
    return np.fabs(point_corners - new_origin_corners[0])


# Calculates Init positions for robots and ball
def calc_init_position(goal, angle, side):
    # calculate vector of first edge
    vector_x = goal.post_1.pos_x - goal.post_2.pos_x
    vector_y = goal.post_1.pos_y - goal.post_2.pos_y
    distance_posts = np.sqrt(vector_x ** 2 + vector_y ** 2)

    dist_to_point = (distance_posts * np.sin(np.deg2rad(angle))) / np.sin(np.deg2rad(180 - 2 * angle))

    init_x = goal.post_1.pos_x + dist_to_point * np.sin(np.deg2rad(angle)) * side
    init_y = goal.post_1.pos_y + dist_to_point * np.cos(np.deg2rad(angle))

    return float(np.round(init_x, 2)), float(np.round(init_y, 2))


# Only returns true if all crucial init values are set!
# Sets init positions for players and ball
def check_init(game_data: GameData, origin_x, origin_y):
    """ checks if field ArUco-Markers were detected and calculates init positions of ball and players

    :param game_data: GameData; Object that contains all information of the game
    :param origin_x: float; X-Coordinate of origin point
    :param origin_y: float; Y-Coordinate of origin point
    :return: boolean; if field was correctly initialized
    """
    if game_data.goal_1.post_1.pos_x == 0:
        return False
    if game_data.goal_1.post_1.pos_y == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_1.post_2.pos_x == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_1.post_2.pos_y == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_2.post_1.pos_x == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_2.post_1.pos_y == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_2.post_2.pos_x == 0:
        print('ERROR: Goal Post not detected')
        return False
    if game_data.goal_2.post_2.pos_y == 0:
        print('ERROR: Goal Post not detected')
        return False
    if origin_x == 0:
        print('ERROR: Origin Point not detected')
        return False
    if origin_y == 0:
        print('ERROR: Origin Point not detected')
        return False

    goal_1_init_x, goal_1_init_y = calc_init_position(game_data.goal_1, 60, -1)
    game_data.init_1.pos_x, game_data.init_1.pos_y = goal_1_init_x, goal_1_init_y + 100
    game_data.init_2.pos_x, game_data.init_2.pos_y = goal_1_init_x, goal_1_init_y - 100

    goal_2_init_x, goal_2_init_y = calc_init_position(game_data.goal_2, 60, 1)
    game_data.init_3.pos_x, game_data.init_3.pos_y = goal_2_init_x, goal_2_init_y + 100
    game_data.init_4.pos_x, game_data.init_4.pos_y = goal_2_init_x, goal_2_init_y - 100

    game_data.init_1 = validate_init_position(1, BasicCoordinate(game_data.init_1.pos_x, game_data.init_1.pos_y))
    game_data.init_2 = validate_init_position(2, BasicCoordinate(game_data.init_2.pos_x, game_data.init_2.pos_y))
    game_data.init_3 = validate_init_position(3, BasicCoordinate(game_data.init_3.pos_x, game_data.init_3.pos_y))
    game_data.init_4 = validate_init_position(4, BasicCoordinate(game_data.init_4.pos_x, game_data.init_4.pos_y))

    game_data.center.pos_x, game_data.center.pos_y = calc_init_position_ball(game_data)

    print("TRACKER: Initialization finished")
    return True


def validate_init_position(init_pos_num, calculated_init_pos):
    """ validates if the calculated init positions are correct

    if the distance between the calculated init position and a hardcoded position is too big, something went wrong
    during init position calculation and the hardcoded fallback coordinate is used instead
    :param init_pos_num: int; id of position
    :param calculated_init_pos: BasicCoordinate; calculated init position
    :return: BasicCoordinate; valid init position
    """
    dist = 0
    init_pos = BasicCoordinate(0, 0)
    if init_pos_num == 1:
        # x = 996 y=436
        init_pos = BasicCoordinate(996, 436)
        dist = get_distance(calculated_init_pos, init_pos)
    elif init_pos_num == 2:
        # x=996 y=236
        init_pos = BasicCoordinate(996, 236)
        dist = get_distance(calculated_init_pos, init_pos)
    elif init_pos_num == 3:
        # x=322 y=447
        init_pos = BasicCoordinate(322, 447)
        dist = get_distance(calculated_init_pos, init_pos)
    elif init_pos_num == 4:
        # x=322 y=247
        init_pos = BasicCoordinate(322, 247)
        dist = get_distance(calculated_init_pos, init_pos)
    else:
        print("Something went wrong during validation of init positions")

    if dist > 150:
        print(f"Set hardcoded init position for Init{init_pos_num}")
        return init_pos
    return calculated_init_pos


class ArucoTracker:
    """ class that represents the ArUco Tracker

    """
    def __init__(self, path_to_calibration_matrice_file, game_data: GameData, aruco_dict=aruco.DICT_6X6_250,
                 font=cv2.FONT_HERSHEY_SIMPLEX):
        """ constructor of the class

        :param path_to_calibration_matrice_file: string; path to file that contains the calibration details
        :param game_data: GameData; Object that contains all information of the game
        :param aruco_dict: which aruco dictionary should be used
        :param font: which font should be used
        """
        self.mtx, self.dist = load_coefficients(path_to_calibration_matrice_file)
        self.origin_x = 1
        self.origin_y = 0
        self.origin_corners = np.asarray([[[0, 0], [0, 30], [30, 30], [30, 0]]])
        self.aruco_dict = aruco.Dictionary_get(aruco_dict)
        self.parameters = aruco.DetectorParameters_create()
        self.parameters.adaptiveThreshConstant = 10
        self.font = font
        self.game_data = game_data
        self.goal_posts = [(1, 1), (1, 1), (1, 1), (1, 1)]

    def find_markers(self, frame):
        """ searches for ArUco markers, detects if they belong to a robot, translates the coordinates of found robot to
        custom coordinate system, writes them into the gameData object and marks them in the frame

        :param frame: current video frame of the camera
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected_image_points = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        if np.all(ids is not None):
            # estimate pose of each marker and return the values
            # rvec and tvec-different from camera coefficients
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, self.mtx, self.dist)

            # string that shows aruco ids
            id_text = ''
            for i in range(ids.size):
                id_text += str(ids[i][0]) + ', '
                # check if current id is calibration marker
                if ids[i] in [2, 3, 4, 5]:
                    # set corners relative to custom origin
                    point_corners = translate_to_custom_origin(self.origin_corners, corners[i])

                    # Calculate X Y coordinates of marker center
                    x, y = np.sum(point_corners[0], axis=0) / 4

                    # calculate vector of first edge
                    vector_x, vector_y = np.diff(corners[i][0][:2], axis=0)[0]

                    # calculate angle of marker rotation. alpha = 0 means first edge and x-Axis are parallel
                    alpha = calculate_angle(self.origin_x, self.origin_y, vector_x, vector_y)

                    if point_corners[0][0][1] < point_corners[0][1][1]:
                        alpha = 360 - alpha

                    self.game_data.player_coordinates[int(ids[i] - 2)] = PlayerCoordinate(int(ids[i] - 1), alpha, x, y)
                    self.draw_corners(frame, corners[i], ids[i])
                    if self.game_data.game_status == GameStatus.INIT:
                        center = (int(self.origin_corners[0][0][0] - self.game_data.center.pos_x),
                                  int(self.origin_corners[0][0][1] - self.game_data.center.pos_y))
                        cv2.circle(frame, center, 20, (0, 255, 255), thickness=4, lineType=8)
                        cv2.putText(frame, "Place Ball Here", center, self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            self.draw_goals(frame)

    def draw_goals(self, frame):
        """ marks the goal lines in the given frame

        :param frame: current video frame of the camera
        """
        cv2.line(frame, self.goal_posts[0], self.goal_posts[1], (0, 255, 0), 4)
        cv2.line(frame, self.goal_posts[2], self.goal_posts[3], (0, 0, 255), 4)

    def init_field(self, frame):
        """ checks if all field ArUco Markers are visible and saves field ArUco Marker position in the GameData Object

        :param frame: current video frame of the camera
        :return: boolean; if field is initialized correctly
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected_image_points = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        if np.all(ids is not None):
            # estimate pose of each marker and return the values
            # rvec and tvec-different from camera coefficients
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, self.mtx, self.dist)

            for i in range(ids.size):
                # check if current id is calibration marker
                if ids[i] == 1:
                    self.origin_x, self.origin_y = np.diff(corners[i][0][:2], axis=0)[0]
                    self.origin_corners = corners[i]

                # if aruco id 6 - 9 --> set x, y of goal posts
                # 6, 7 -> Goal 1 Post 1/2
                # 8, 9 -> Goal 2 Post 1/2
                elif ids[i] in [6, 7, 8, 9]:
                    # set corners relative to custom origin
                    point_corners = translate_to_custom_origin(self.origin_corners, corners[i])

                    # Set X/Y to 0 corner for goal posts
                    x, y = point_corners[0][0]

                    if ids[i] == 6:
                        self.game_data.goal_1.post_1.pos_x = float(x) + 10
                        self.game_data.goal_1.post_1.pos_y = float(y)
                        self.goal_posts[0] = (corners[i][0][0][0], corners[i][0][0][1])
                    elif ids[i] == 7:
                        self.game_data.goal_1.post_2.pos_x = float(x) + 10
                        self.game_data.goal_1.post_2.pos_y = float(y)
                        self.goal_posts[1] = (corners[i][0][0][0], corners[i][0][0][1])
                    elif ids[i] == 8:
                        self.game_data.goal_2.post_1.pos_x = float(x) - 10
                        self.game_data.goal_2.post_1.pos_y = float(y)
                        self.goal_posts[2] = (corners[i][0][0][0], corners[i][0][0][1])
                    elif ids[i] == 9:
                        self.game_data.goal_2.post_2.pos_x = float(x) - 10
                        self.game_data.goal_2.post_2.pos_y = float(y)
                        self.goal_posts[3] = (corners[i][0][0][0], corners[i][0][0][1])
            return check_init(self.game_data, self.origin_x, self.origin_y)

    def draw_corners(self, frame, corners, aruco_id):
        """ marks the corners of the found player ArUco markers

        :param frame: current video frame of the camera
        :param corners: Array; Array that has all the found corners in it
        :param aruco_id: int; ID of the marker to mark
        """
        color = (0, 255, 0) if aruco_id < 4 else (0, 0, 255)
        for j in range(4):
            cv2.putText(frame, "{0}".format(j), (corners[0][j][0], corners[0][j][1]), self.font, 0.5,
                        color, 2, cv2.LINE_AA)
            cv2.circle(frame, (corners[0][j][0], corners[0][j][1]), 2, (255, 0, 0), thickness=1,
                       lineType=8)

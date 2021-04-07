import platform
import traceback

import numpy as np
import time
import threading
from enum import Enum
from football_robots.networking.socketClient import Client
from football_robots.utility_functions.utils import get_init_values, get_distance_of_point_to_line, is_out_of_bounds, get_distance

# to prevent import issues on server
if "Linux" in platform.platform():
    from football_robots.car_controls.CAR import CAR
    import mariadb
else:
    from football_robots.car_controls.DUMMY_CAR import CAR


class GameStatus(Enum):
    """ class that represents the current game status

    """
    NO_STATE = -1
    INIT = 0
    START = 1
    PAUSE = 2
    STOP = 3


class BasicCoordinate:
    """ class that represents basic coordinates

    """
    def __init__(self, pos_x, pos_y):
        """ constructor for the class

        :param pos_x: float; x-Coordinate
        :param pos_y: float; y-Coordinate
        """
        self.pos_x = pos_x
        self.pos_y = pos_y

    def get_pos(self):
        """ getter function

        :return: float, float; x and y-Coordinate
        """
        return self.pos_x, self.pos_y

    def __str__(self):
        """ defines string representation of the class

        :return: string;
        """
        return 'X: {0}, Y: {1}'.format(self.pos_x, self.pos_y)


class PlayerCoordinate(BasicCoordinate):
    """ class that represents the coordinates of a player

    """
    def __init__(self, player_id, alpha, pos_x, pos_y):
        """ class constructor

        :param player_id: int; id of the player
        :param alpha: float; rotation of the player. 0 -> player looks in x direction
        :param pos_x: float; x-Coordinate of player
        :param pos_y: float; y-Coordinate of player
        """
        self.player_id = player_id
        self.alpha = alpha
        BasicCoordinate.__init__(self, pos_x, pos_y)

    def __str__(self):
        return 'ID: {0}, X: {1}, Y: {2}, Alpha: {3}'.format(self.player_id, self.pos_x, self.pos_y, self.alpha)


class Goal:
    """ class that represents a goal

    """
    def __init__(self, post1_x, post1_y, post2_x, post2_y):
        """ constructor of the class

        :param post1_x: float; x-Coordinate of first goal post
        :param post1_y: float; y-Coordinate of first goal post
        :param post2_x: float; x-Coordinate of second goal post
        :param post2_y: float; y-Coordinate of second goal post
        """
        self.post_1 = BasicCoordinate(post1_x, post1_y)
        self.post_2 = BasicCoordinate(post2_x, post2_y)

    def get_coords(self):
        """ getter function of post coordinates

        :return: float, float, float, float;
        """
        return self.post_1.pos_x, self.post_1.pos_y, self.post_2.pos_x, self.post_2.pos_y


class GameData:
    """ class that represents important data of the game

    """
    def __init__(self, player_coordinates: [PlayerCoordinate], ball_coordinates: BasicCoordinate, goal_1: Goal,
                 goal_2: Goal, game_status: GameStatus, init_1: BasicCoordinate, init_2: BasicCoordinate,
                 init_3: BasicCoordinate, init_4: BasicCoordinate, center: BasicCoordinate, goals_team1, goals_team2,
                 game_time):
        """ constructor of the class

        :param player_coordinates: [PlayerCoordinate]; list of all the player coordinates
        :param ball_coordinates: BasicCoordinate; position of the ball
        :param goal_1: Goal; goal of team 1
        :param goal_2: Goal; goal of team 2
        :param game_status: GameStatus; current status of the game
        :param init_1: BasicCoordinate; Position of a player during kick off
        :param init_2: BasicCoordinate; Position of a player during kick off
        :param init_3: BasicCoordinate; Position of a player during kick off
        :param init_4: BasicCoordinate; Position of a player during kick off
        :param center: BasicCoordinate; Position of the center of the field
        :param goals_team1: int; number of scored goals of team 1
        :param goals_team2: int; number of scored goals of team 2
        :param game_time: float; game time that passed since first kick off. Pauses when game is paused
        """
        self.player_coordinates = player_coordinates
        self.ball_coordinates = ball_coordinates
        self.goal_1 = goal_1
        self.goal_2 = goal_2
        self.game_status = game_status
        self.init_1 = init_1
        self.init_2 = init_2
        self.init_3 = init_3
        self.init_4 = init_4
        self.center = center
        self.goals_team1 = goals_team1
        self.goals_team2 = goals_team2
        self.game_time = game_time
        self.should_log = True


class Player:
    """ class that represents a single player

    :attr init: dictionary; contains the data from player_init_local.json
    :attr player_id: int; id of the player
    :attr mate_id: int; id of the mate
    :attr side: int; defines which side of the field the player needs to defend
    :attr use_ml: boolean; if player uses ML Algorithm for decisions or man made decision tree
    :attr ml_type: string; defines which ML Algorithm should be used
    :attr game_data: GameData; contains all the data of the game
    :attr car: CAR; used to control the robot
    :attr x: float; x-Coordinate of the player
    :attr y: float; y-Coordinate of the player
    :attr rot: float; rotation of the player
    :attr conn: ?; connector to mariadb database
    :attr current_decision: string; current decision of the robot
    :attr avoidance_radius: int; defines how much pixel a player drives around an obstacle
    :attr game_status: GameStatus; current status of the game
    :attr decision_count: int; counts how much decisions were made during one game
    :attr ml_model: ?; ML model that is used for decisions if use_ml == True

    """
    def __init__(self):
        """ constructor of the class

        """
        self.init = get_init_values("football_robots/player_init_local.json")
        if not self.init:
            print("Error when reading from player init json file ")
            return
        self.player_id = self.init["player_id"]
        self.mate_id = self.init["mate_id"]
        self.side = self.init["side"]
        self.use_ml = self.init["use_ml"]
        self.ml_type = self.init["ml_type"]
        self.game_data = create_empty_game_data()
        self.car = CAR() if self.side == 1 else CAR(light=(20, 0, 0))
        self.x, self.y, self.rot = 0, 0, 0
        self.conn = None
        self.update_own_coordinates()
        self.current_decision = None
        self.avoidance_radius = 100
        self.game_status = self.game_data.game_status
        self.decision_count = 0
        self.ml_model = None

    def __str__(self):
        """

        :return: string; string representation of the class
        """
        return str(self.__class__) + ": " + str(self.__dict__)

    def move_to_xy(self, destination_x, destination_y, avoid_ball=False, destination_is_ball=False):
        """ lets robot move to specific destination in the grid

        Robot automatically avoids obstacles that are between it and its destination
        (needs improvement, currently only first obstacle is avoided)

        :param destination_x: float; x-coordinate of the destination
        :param destination_y: float; x-coordinate of the destination
        :param avoid_ball: boolean; if robot should avoid ball
        :param destination_is_ball: if destination is ball
        :return:
        """
        self.update_own_coordinates()
        epsilon_distance = 40  # pixel; robot reaches destination if distance < epsilon_distance
        epsilon_rotation = 25  # pixel; robot looks at destination if angle to destination < epsilon_rotation
        distance_to_destination = self.get_distance_to_point(destination_x, destination_y)
        while distance_to_destination > epsilon_distance:
            # robot should stop moving if game status changes
            if self.game_status != self.game_data.game_status:
                self.game_status = self.game_data.game_status
                break
            if destination_is_ball and get_distance(self.game_data.ball_coordinates, BasicCoordinate(destination_x, destination_y)) > 50:
                break
            self.update_own_coordinates()
            blocking_player = self.get_blocking_player(destination_x, destination_y, avoid_ball)
            if not blocking_player:
                # contains angle to destination, direction of rotation (1 == left, -1 == right) and direction of
                # movement (1 == forward, -1 == backward)
                angle_and_directions = self.get_angle_to_xy(destination_x - self.x, destination_y - self.y)
                distance_to_destination = self.get_distance_to_point(destination_x, destination_y)
            else:
                new_destination = self.get_avoidance_point(blocking_player, destination_x, destination_y)
                angle_and_directions = self.get_angle_to_xy(new_destination.pos_x - self.x,
                                                            new_destination.pos_y - self.y)
                distance_to_destination = self.get_distance_to_point(new_destination.pos_x, new_destination.pos_y)
            if angle_and_directions[0] > epsilon_rotation:
                self.car.rotate(int(angle_and_directions[1]))
            else:
                self.car.move(int(angle_and_directions[2]))
            # artificially slows down car. Needed, because otherwise car is too fast for object detection
            time.sleep(0.01)
            self.car.stop()
            time.sleep(0.01)
        self.car.stop()

    def get_distance_to_point(self, destination_x, destination_y):
        """ distance in pixel to a given point is calculated

        for calculation Pythagoras' theorem is used

        :param destination_x: float; x-Coordinate of the destination
        :param destination_y: float; y-Coordinate of the destination
        :return: float; distance to destination in pixel
        """
        return np.sqrt((destination_x - self.x) ** 2 + (destination_y - self.y) ** 2)

    def get_blocking_player(self, destination_x, destination_y, avoid_ball):
        """ returns one object that blocks path to destination

        HINT: to return all blocking objects just adapt the return statement.
        IMPORTANT: if all object are returned get_avoidance_point needs to ba refactored as well

        :param destination_x: float; x-Coordinate of the destination
        :param destination_y: float; y-Coordinate of the destination
        :param avoid_ball: boolean; if ball should be avoided too
        :return: BasicCoordinate: object that blocks path to destination
        """
        other_players = [player for player in self.game_data.player_coordinates if player.player_id != self.player_id]
        if avoid_ball:
            other_players.append(self.game_data.ball_coordinates)
        blocking_players = [player for player in other_players if
                            self.is_player_blocking_path(player, destination_x, destination_y)]
        return blocking_players[0] if len(blocking_players) > 0 else None

    def is_player_blocking_path(self, player: BasicCoordinate, destination_x, destination_y):
        """ returns if given object is blocking the path to the destination or not

        an object blocks the path if the distance  from its center to the direct line between the player and its
        destination is smaller than the self.avoidance_radius and object is between player and destination

        :param player: BasicCoordinate; Coordinates of given object
        :param destination_x: float; x-Coordinate of the destination
        :param destination_y: float; y-Coordinate of the destination
        :return: boolean; if object is blocking path or not
        """
        myself = np.array([self.x, self.y])
        destination = np.array([destination_x, destination_y])
        obstacle_player = np.array([player.pos_x, player.pos_y])
        max_x = max(myself[0], destination[0])
        min_x = min(myself[0], destination[0])
        max_y = max(myself[1], destination[1])
        min_y = min(myself[1], destination[1])
        is_obstacle_blocking = get_distance_of_point_to_line(obstacle_player, myself, destination) < self.avoidance_radius
        is_obstacle_between_player_and_destination_x = min_x <= obstacle_player[0] <= max_x
        is_obstacle_between_player_and_destination_y = min_y <= obstacle_player[1] <= max_y
        return is_obstacle_blocking and (is_obstacle_between_player_and_destination_x or is_obstacle_between_player_and_destination_y)

    def get_angle_to_xy(self, x_diff, y_diff):
        """ calculates the angle and the direction a player needs to rotate to look at its destination

        :param x_diff: float; destination_x - self.x
        :param y_diff: float; destination_y - self.y
        :return: [float, int]; angle and rotation direction (1 == left, -1 == right)
        """
        # angle between robot and destination point to x-Axis
        dest_angle = np.degrees(np.arcsin(y_diff / np.sqrt(x_diff ** 2 + y_diff ** 2)))
        if x_diff >= 0:
            dest_angle = (360 - dest_angle) % 360
        else:
            dest_angle = 180 + dest_angle
        # shortest angle from robot front to destination point plus rotation direction
        angle = dest_angle - self.rot
        angle_with_dir1 = np.array([np.abs(angle), np.sign(angle)])
        angle_with_dir2 = np.array([360 - np.abs(angle), angle_with_dir1[1] * (-1)])
        angle_to_dest = angle_with_dir1 if np.abs(angle_with_dir1[0]) <= angle_with_dir2[0] else angle_with_dir2

        # get minimum rotation angle. Car rotates backside to destination point if it is quicker
        alpha_front = np.append(angle_to_dest, 1)
        alpha_back = np.array([(180 - alpha_front[0]), alpha_front[1] * (-1), -1])
        alpha = alpha_front if alpha_front[0] < alpha_back[0] else alpha_back
        return alpha

    def get_avoidance_point(self, blocking_player: BasicCoordinate, destination_x, destination_y):
        """ calculates the coordinates of the point that avoids the obstacle

        :param blocking_player: BasicCoordinate; coordinates of the blocking object
        :param destination_x: float; x-Coordinate of the destination
        :param destination_y: float; y-Coordinate of the destination
        :return: BasicCoordinate; Coordinates of the avoidance point
        """
        myself = np.array([self.x, self.y])
        blocker = np.array([blocking_player.pos_x, blocking_player.pos_y])
        destination = np.array([destination_x, destination_y])
        distance_to_line = get_distance_of_point_to_line(blocker, myself, destination)
        distance_to_obstacle = np.linalg.norm(myself - blocker)
        distance_to_line_intersection = np.sqrt(distance_to_obstacle ** 2 - distance_to_line ** 2)
        line_vector = destination - myself
        intersection_point = myself + (line_vector / np.linalg.norm(line_vector)) * distance_to_line_intersection
        obstacle_to_intersection_vector = intersection_point - blocker
        avoidance_point = intersection_point + (
                    obstacle_to_intersection_vector / np.linalg.norm(obstacle_to_intersection_vector)) * (
                                      2 * self.avoidance_radius - distance_to_line)

        if is_out_of_bounds(self, avoidance_point):
            intersection_to_obstacle_vector = blocker - intersection_point
            avoidance_point = blocker + (
                    intersection_to_obstacle_vector / np.linalg.norm(intersection_to_obstacle_vector)) * (
                                      2 * self.avoidance_radius)

        return BasicCoordinate(avoidance_point[0], avoidance_point[1])

    def update_own_coordinates(self):
        """ function that updates own coordinates and rotation from game data

        """
        coord = self.game_data.player_coordinates[self.player_id - 1]
        self.x, self.y, self.rot = coord.pos_x, coord.pos_y, coord.alpha

    def move_to_init(self):
        """ moves player to one of the init positions

        """
        self.current_decision = None
        if self.side == 1:
            destination_x = self.game_data.init_1.pos_x if self.player_id > self.mate_id else self.game_data.init_2.pos_x
            destination_y = self.game_data.init_1.pos_y if self.player_id > self.mate_id else self.game_data.init_2.pos_y
        else:
            destination_x = self.game_data.init_3.pos_x if self.player_id > self.mate_id else self.game_data.init_4.pos_x
            destination_y = self.game_data.init_3.pos_y if self.player_id > self.mate_id else self.game_data.init_4.pos_y
        self.move_to_xy(destination_x, destination_y)

    def get_insert_string(self):
        """ creates string that is needed to insert data into the database

        IMPORTANT: Number of question marks need to be equal to number of variables

        :return: string; insert string
        """
        return "INSERT INTO game_data (time, player_id, mate_id, team_id, decision, goal_team_1, " \
               "goal_team_2, goal_1_post_1_x, goal_1_post_1_y, goal_1_post_2_x, goal_1_post_2_y, goal_2_post_1_x, " \
               "goal_2_post_1_y, goal_2_post_2_x, goal_2_post_2_y, " \
               " player_1_x, player_1_y, player_1_alpha, player_2_x, player_2_y, player_2_alpha," \
               " player_3_x, player_3_y, player_3_alpha, player_4_x, player_4_y, player_4_alpha," \
               "ball_x, ball_y, decision_count) VALUES(?, ? ,?, ? ,? ,? ,? ,? ,? ,? , ?, ?, ? ,?, ? ,? ,? ,? ,? ,? ," \
               "? ,?, ?, ?, ?, ?, ?, ?, ?, ?) "

    def connect_to_server(self):
        """ starts a connection to the referee in a separate thread

        """
        # Function for player to connect to server
        client = Client()
        threading.Thread(target=client.startClient, args=(self, self.init["server_ip"],), daemon=True).start()

    def log_to_database(self):
        """ logs data from the player to the DB

        """
        self.connect_to_db()

        while 1:

            time.sleep(0.5)
            # check if conn lost and reconnect
            if not self.conn:
                print("Lost connection to DB, trying to reconnect!")
                self.connect_to_db()

            # As long as the game is not started, do not log anything

            if self.game_data.game_status != GameStatus.START or not self.game_data.should_log:
                print("no logging to db")
                continue
            # Get Cursor
            cur = self.conn.cursor()
            try:
                # IMPORTANT: order and number of variables must be the same as in the insert string
                cur.execute(self.get_insert_string(),
                            (self.game_data.game_time,
                             self.player_id,
                             self.mate_id,
                             self.side,
                             self.current_decision,
                             self.game_data.goals_team1,
                             self.game_data.goals_team2,
                             float(self.game_data.goal_1.post_1.pos_x),
                             float(self.game_data.goal_1.post_1.pos_y),
                             float(self.game_data.goal_1.post_2.pos_x),
                             float(self.game_data.goal_1.post_2.pos_y),
                             float(self.game_data.goal_2.post_1.pos_x),
                             float(self.game_data.goal_2.post_1.pos_y),
                             float(self.game_data.goal_2.post_2.pos_x),
                             float(self.game_data.goal_2.post_2.pos_y),
                             float(self.game_data.player_coordinates[0].pos_x),
                             float(self.game_data.player_coordinates[0].pos_y),
                             float(self.game_data.player_coordinates[0].alpha),
                             float(self.game_data.player_coordinates[1].pos_x),
                             float(self.game_data.player_coordinates[1].pos_y),
                             float(self.game_data.player_coordinates[1].alpha),
                             float(self.game_data.player_coordinates[2].pos_x),
                             float(self.game_data.player_coordinates[2].pos_y),
                             float(self.game_data.player_coordinates[2].alpha),
                             float(self.game_data.player_coordinates[3].pos_x),
                             float(self.game_data.player_coordinates[3].pos_y),
                             float(self.game_data.player_coordinates[3].alpha),
                             float(self.game_data.ball_coordinates.pos_x),
                             float(self.game_data.ball_coordinates.pos_y),
                             int(self.decision_count)))

            except mariadb.Error as e:
                print(f"Error: {e}")
                traceback.print_exc()
                break

            self.conn.commit()
            cur.close()

    def connect_to_db(self):
        """ connects to MariaDB Platform

        """
        try:
            conn = mariadb.connect(
                user=self.init["db_username"],
                password=self.init["db_password"],
                host=self.init["db_ip"],
                port=3306,
                database="football"

            )
            print(f"Successfully connected to DB at IP {self.init['db_ip']}")
            self.conn = conn
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")


def create_empty_game_data():
    """ function that creates an empty game data

    is needed to proper start up the system

    :return: GameData; empty game data
    """
    # Creates 4 Coordinate-objects; for each player one objects
    # Their content will be updated
    coordinates_1 = PlayerCoordinate(player_id=1, pos_x=0, pos_y=0, alpha=0)
    coordinates_2 = PlayerCoordinate(player_id=2, pos_x=0, pos_y=0, alpha=0)
    coordinates_3 = PlayerCoordinate(player_id=3, pos_x=0, pos_y=0, alpha=0)
    coordinates_4 = PlayerCoordinate(player_id=4, pos_x=0, pos_y=0, alpha=0)
    coordinates = [coordinates_1, coordinates_2, coordinates_3, coordinates_4]

    ball_coordinate = BasicCoordinate(pos_x=0, pos_y=0)
    init_1 = BasicCoordinate(pos_x=0, pos_y=0)
    init_2 = BasicCoordinate(pos_x=0, pos_y=0)
    init_3 = BasicCoordinate(pos_x=0, pos_y=0)
    init_4 = BasicCoordinate(pos_x=0, pos_y=0)
    goal_1 = Goal(post1_x=0, post1_y=0, post2_x=0, post2_y=0)
    goal_2 = Goal(post1_x=0, post1_y=0, post2_x=0, post2_y=0)
    center = BasicCoordinate(pos_x=0, pos_y=0)
    return GameData(coordinates, ball_coordinate, goal_1, goal_2, GameStatus.NO_STATE, init_1, init_2, init_3, init_4,
                    center, 0, 0, 0)

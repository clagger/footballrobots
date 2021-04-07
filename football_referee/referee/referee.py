import time
from football_referee.networking.multiClientServer import Server
from football_robots.player.player import GameData, GameStatus
from football_robots.utility_functions.utils import get_distance


def check_init_occupied(pos_1, pos_2):
    """ checks two positions are nearly the same

    :param pos_1: BasicCoordinate; Position 1
    :param pos_2: BasicCoordinate; Position 1
    :return: boolean; if positions are nearly the same
    """
    dist = get_distance(pos_1, pos_2)
    return dist < 50


def check_init_player(init_pos, game_data):
    """ checks if given init position is occupied

    :param init_pos: BasicCoordinate; init position
    :param game_data: GameData; Object that contains all information of the game
    :return: boolean; if given init position is occupied
    """
    for player_coordinate in game_data.player_coordinates:
        if check_init_occupied(init_pos, player_coordinate):
            return True
    return False


class Referee:
    """ class that represents the referee

    """
    def __init__(self, server: Server, game_duration):
        """ constructor of the class

        :param server: Server; the communication server which the referee belongs to
        :param game_duration: float; duration of the game in seconds
        """
        self.team1 = "Team 1"
        self.team2 = "Team 2"
        self.server = server
        self.game_duration = game_duration
        self.score = {self.team1: 0,
                      self.team2: 0}

        self.game_timer = GameTimer(self.game_duration)
        self.currently_playing = False

    def manage_game(self, game_data: GameData):
        """ manages the game according to the current status of the game

        :param game_data: GameData; Object that contains all information of the game
        """
        if game_data.game_status == GameStatus.INIT and all(self.ready_for_kickoff(game_data)) and not self.currently_playing:
            self.start_game(game_data)
        if game_data.game_status == GameStatus.INIT and all(self.ready_for_kickoff(game_data)) and self.currently_playing:
            self.resume_game(game_data)
        if game_data.game_status == GameStatus.START:
            self.check_goal(game_data)
        if game_data.game_status == GameStatus.STOP or self.game_timer.get_time_passed() > self.game_duration:
            self.stop_game(game_data)
        if game_data.game_status == GameStatus.PAUSE:
            self.pause_game(game_data)

    def ready_for_kickoff(self, game_data: GameData):
        """ checks if everything is in order to start the game

        :param game_data: GameData; Object that contains all information of the game
        :return: [boolean]; if ball and players are in position and if all players are connected to the server
        """
        # check if all init positions are occupied
        init_1_ready = check_init_player(game_data.init_1, game_data)
        init_2_ready = check_init_player(game_data.init_2, game_data)
        init_3_ready = check_init_player(game_data.init_3, game_data)
        init_4_ready = check_init_player(game_data.init_4, game_data)
        # check if ball is on starting pos
        ball_ready = check_init_occupied(game_data.center, game_data.ball_coordinates)
        return [ball_ready, init_1_ready, init_2_ready,  init_3_ready, init_4_ready, self.all_players_connected()]

    def check_goal(self, game_data: GameData):
        """ checks if a goal is scored and afterwards pauses the game and adds a point to a team when they scored a goal

        :param game_data: GameData; Object that contains all information of the game
        """
        ball_x, ball_y = game_data.ball_coordinates.pos_x, game_data.ball_coordinates.pos_y

        # Goal of team 1 --> if its in its a goal for team2
        goal1_1_x, goal1_1_y, goal1_2_x, goal1_2_y = game_data.goal_1.get_coords()
        goal2_1_x, goal2_1_y, goal2_2_x, goal2_2_y = game_data.goal_2.get_coords()

        scoring_team = None
        if (goal1_1_x - ball_x < 0) and (goal1_2_x - ball_x < 0):
            scoring_team = self.team2

        if (goal2_1_x - ball_x > 0) and (goal2_2_x - ball_x > 0):
            scoring_team = self.team1

        if scoring_team:
            game_data.game_status = GameStatus.INIT
            self.game_timer.pause()
            self.update_score(scoring_team, game_data)

    def all_players_connected(self):
        """ checks if all players are connected to the server

        :return: boolean; if all players are connected to the server
        """
        num_clients = len(self.server.CLIENTS)
        return num_clients == 4

    def pause_game(self, game_data: GameData):
        """ pauses the game and the game timer

        :param game_data: GameData; Object that contains all information of the game
        """
        game_data.game_status = GameStatus.PAUSE
        self.game_timer.pause()

    def resume_game(self, game_data: GameData):
        """ resumes the game and the game timer

        :param game_data: GameData; Object that contains all information of the game
        """
        game_data.game_status = GameStatus.START
        self.game_timer.resume()

    def stop_game(self, game_data: GameData):
        """ ends the game and resets the referee object

        :param game_data: GameData; Object that contains all information of the game
        """
        game_data.game_status = GameStatus.STOP
        if self.currently_playing:
            print('Game ended')
            print(f"Team Green {self.score['Team 1']}:{self.score['Team 2']} Team Red")
        self.currently_playing = False
        self.reset_game()

    def update_score(self, team, game_data: GameData):
        """ adds a point to the given team and saves it in the game data object

        :param team: string; team that gets the point
        :param game_data: GameData; Object that contains all information of the game
        """
        self.score[team] += 1
        if team == self.team1:
            game_data.goals_team1 = self.score[team]
        else:
            game_data.goals_team2 = self.score[team]

    def get_score(self):
        """ getter function for current score

        :return: dictionary; current team scores
        """
        return self.score

    def reset_score(self):
        """ resets the scores to 0
        """
        self.score = {self.team1: 0,
                      self.team2: 0}

    def reset_game(self):
        """ reinitiates the referee object
        """
        self.__init__(self.server, self.game_duration)

    def start_game(self, game_data):
        """ starts the game timer and the game

        :param game_data: GameData; Object that contains all information of the game
        """
        game_data.game_status = GameStatus.START
        self.currently_playing = True
        self.game_timer.start()

    def still_playing(self):
        """ checks if the game is not paused or stopped

        :return: boolean; if game is not stopped or paused
        """
        return self.game_timer.still_playing()

    def get_time_passed(self, game_data: GameData):
        """ returns how much game time passed and saves it in the game data object

        :param game_data: GameData; Object that contains all information of the game
        :return: float; how much game time has passed
        """
        game_time = self.game_timer.get_time_passed()
        game_data.game_time = round(game_time, 2)
        return game_time


class GameTimer:
    """ represents the time measurement of the game

    """
    def __init__(self, game_duration):
        """ constructor of the class

        :param game_duration: float; how long the game should be in seconds
        """
        self.time_started = None
        self.time_paused = None
        self.paused = False
        self.game_duration = game_duration

    def start(self):
        """ starts timer
        """
        self.time_started = time.time()

    def pause(self):
        """ pauses timer
        """
        if self.time_started is None:
            raise ValueError("Timer not started")
        if not self.paused:
            self.time_paused = time.time()
            self.paused = True

    def resume(self):
        """ resumes timer
        """
        if self.time_started is None:
            raise ValueError("Timer not started")
        if not self.paused:
            raise ValueError("Timer is not paused")
        pause_time = time.time() - self.time_paused
        self.time_started = self.time_started + pause_time
        self.paused = False

    def reset(self):
        """ resets timer
        """
        self.__init__(self.game_duration)

    def get_time_passed(self):
        """ returns how much time the game was played

        :return: float; how much time has passed in-game
        """
        if self.time_started and not self.paused:
            return time.time() - self.time_started
        elif self.time_started and self.paused:
            return self.time_paused - self.time_started
        else:
            return 0

    def still_playing(self):
        """ returns if the game is not stopped or paused

        :return: boolean; if game is not stopped or paused
        """
        if self.get_time_passed() > self.game_duration and not self.paused:
            return False
        return True

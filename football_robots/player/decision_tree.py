from football_robots.player.player import *
from football_robots.utility_functions.utils import calc_init_position_ball


def decide_action(player: Player):
    """ man made decision tree to decide which action to take

    for a better picture please read the technical documentation

    :param player: Player; player that decides
    """
    player.decision_count += 1
    # Ball is in own side
    if is_ball_in_own_side(player):
        # player is closest to ball
        if is_closest_to_ball(player, player.player_id):
            # Ball is closer to own goal than player
            if is_ball_closer_to_goal_than_player(player, player.player_id):
                # Ball is closer to own goal than mate
                if is_ball_closer_to_goal_than_player(player, player.mate_id):
                    print('recover (OC1)')
                    player.current_decision = 'recover'
                    recover(player)
                # Mate is closer to own goal than ball
                else:
                    print('guard (OB1)')
                    player.current_decision = 'guard'
                    guard(player)
            # Player is closer to own goal than ball
            else:
                print('shoot (OA1)')
                player.current_decision = 'shoot'
                shoot(player)
        # mate is closest to ball
        elif is_closest_to_ball(player, player.mate_id):
            # Ball is closer to own goal than mate
            if is_ball_closer_to_goal_than_player(player, player.mate_id):
                # Ball is closer to own goal than player
                if is_ball_closer_to_goal_than_player(player, player.player_id):
                    print('guard (OC2)')
                    player.current_decision = 'guard'
                    guard(player)
                # Player is closer to own goal than ball
                else:
                    print('intercept (OB2)')
                    player.current_decision = 'intercept'
                    intercept(player)
            # Mate is closer to own goal than ball
            else:
                print('guard (OA2)')
                player.current_decision = 'guard'
                guard(player)
        # opponent is closest to ball
        else:
            # player is closest to ball
            if is_closest_of_team_to_ball(player, player.player_id):
                # Ball is closer to own goal than player
                if is_ball_closer_to_goal_than_player(player, player.player_id):
                    # Ball is closer to own goal than mate
                    if is_ball_closer_to_goal_than_player(player, player.mate_id):
                        print('recover (OC1)')
                        player.current_decision = 'recover'
                        recover(player)
                    # Mate is closer to own goal than ball
                    else:
                        print('guard (OB1)')
                        player.current_decision = 'guard'
                        guard(player)
                # Player is closer to own goal than ball
                else:
                    print('shoot (OA1)')
                    player.current_decision = 'shoot'
                    shoot(player)
            # mate is closest to ball
            else:
                # Ball is closer to own goal than mate
                if is_ball_closer_to_goal_than_player(player, player.mate_id):
                    # Ball is closer to own goal than player
                    if is_ball_closer_to_goal_than_player(player, player.player_id):
                        print('guard (OC2)')
                        player.current_decision = 'guard'
                        guard(player)
                    # Player is closer to own goal than ball
                    else:
                        print('intercept (OB2)')
                        player.current_decision = 'intercept'
                        intercept(player)
                # Mate is closer to own goal than ball
                else:
                    print('guard (OA2)')
                    player.current_decision = 'guard'
                    guard(player)
    # Ball is in opponent side
    else:
        # player is closest to ball
        if is_closest_to_ball(player, player.player_id):
            # Player is closer to opponent goal than ball
            if not is_ball_closer_to_goal_than_player(player, player.player_id, is_own_goal=False):
                # Mate is closer to opponent goal than ball
                if not is_ball_closer_to_goal_than_player(player, player.mate_id, is_own_goal=False):
                    print('recover (EC1)')
                    player.current_decision = 'recover'
                    recover(player)
                # Ball is closer to opponent goal than mate
                else:
                    print('center (EB1)')
                    player.current_decision = 'center'
                    center(player)
            # Ball is closer to opponent goal than player
            else:
                print('shoot (EA1)')
                player.current_decision = 'shoot'
                shoot(player)
        # mate is closest to ball
        elif is_closest_to_ball(player, player.mate_id):
            # Mate is closer to opponent goal than ball
            if not is_ball_closer_to_goal_than_player(player, player.mate_id, is_own_goal=False):
                # Player is closer to opponent goal than ball
                if not is_ball_closer_to_goal_than_player(player, player.player_id, is_own_goal=False):
                    print('center (EC2)')
                    player.current_decision = 'center'
                    center(player)
                # Ball is closer to opponent goal than player
                else:
                    print('shoot (EB2)')
                    player.current_decision = 'shoot'
                    shoot(player)
            # Ball is closer to opponent goal than mate
            else:
                print('center (EA2)')
                player.current_decision = 'center'
                center(player)
        # opponent is closest to ball
        else:
            # player is closest to ball
            if is_closest_of_team_to_ball(player, player.player_id):
                # Player is closer to opponent goal than ball
                if not is_ball_closer_to_goal_than_player(player, player.player_id, is_own_goal=False):
                    # Mate is closer to opponent goal than ball
                    if not is_ball_closer_to_goal_than_player(player, player.mate_id, is_own_goal=False):
                        print('recover (EC1)')
                        player.current_decision = 'recover'
                        recover(player)
                    # Ball is closer to opponent goal than mate
                    else:
                        print('center (EB1)')
                        player.current_decision = 'center'
                        center(player)
                # Ball is closer to opponent goal than player
                else:
                    print('shoot (EA1)')
                    player.current_decision = 'shoot'
                    shoot(player)
            # mate is closest to ball
            else:
                # Mate is closer to opponent goal than ball
                if not is_ball_closer_to_goal_than_player(player, player.mate_id, is_own_goal=False):
                    # Player is closer to opponent goal than ball
                    if not is_ball_closer_to_goal_than_player(player, player.player_id, is_own_goal=False):
                        print('center (EC2)')
                        player.current_decision = 'center'
                        center(player)
                    # Ball is closer to opponent goal than player
                    else:
                        print('shoot (EB2)')
                        player.current_decision = 'shoot'
                        shoot(player)
                # Ball is closer to opponent goal than mate
                else:
                    print('center (EA2)')
                    player.current_decision = 'center'
                    center(player)


def is_ball_in_own_side(player: Player):
    """ if ball is in own side

    :param player: Player; player that decides its action
    :return: boolean; if ball is in own side
    """
    ball_x = player.game_data.ball_coordinates.pos_x
    center_x, _ = calc_init_position_ball(player.game_data)
    is_in_own_side = ball_x - center_x > 0 if player.side == 1 else ball_x - center_x <= 0
    return is_in_own_side


def is_closest_to_ball(player, player_id):
    """ if given player is closest to ball

    :param player: Player; player that decides its action
    :param player_id: int; id of the given player
    :return: boolean; if given player is closest to ball
    """
    return get_closest_player_coordinate(player).player_id == player_id


def is_closest_of_team_to_ball(player, player_id):
    """ if given player is closer to the ball than their teammate

    :param player: Player; player that decides its action
    :param player_id: int; id of the given player
    :return: boolean; if given player is closer to ball
    """
    return get_closest_team_player_coordinate(player).player_id == player_id


def get_closest_player_coordinate(player: Player):
    """ finds player who is closest to the ball

    :param player: Player; player that decides its action
    :return: PlayerCoordinate; coordinate of the player who is the closest to the ball
    """
    my_coordinates = get_coordinates(player.game_data.player_coordinates, player.player_id)
    my_distance_and_id = (get_distance(player.game_data.ball_coordinates, my_coordinates), player.player_id)

    mate_coordinates = get_coordinates(player.game_data.player_coordinates, player.mate_id)
    mate_distance_and_id = (get_distance(player.game_data.ball_coordinates, mate_coordinates), player.mate_id)

    opp_ids = [number for number in [1, 2, 3, 4] if number not in [player.player_id, player.mate_id]]
    opp1_coordinates = get_coordinates(player.game_data.player_coordinates, opp_ids[0])
    opp1_distance_and_id = (get_distance(player.game_data.ball_coordinates, opp1_coordinates), opp_ids[0])

    opp2_coordinates = get_coordinates(player.game_data.player_coordinates, opp_ids[1])
    opp2_distance_and_id = (get_distance(player.game_data.ball_coordinates, opp2_coordinates), opp_ids[1])

    distances_and_ids = [my_distance_and_id, mate_distance_and_id, opp1_distance_and_id, opp2_distance_and_id]
    distances = list(zip(*distances_and_ids))[0]

    _, closest_player_id = distances_and_ids[distances.index(min(distances))]

    closest_player: PlayerCoordinate = player.game_data.player_coordinates[closest_player_id-1]
    return closest_player


def get_closest_team_player_coordinate(player: Player):
    """ finds player of the team who is closer to the ball

    :param player: Player; player that decides its action
    :return: PlayerCoordinate; Coordinates of the teammate that is closer to the ball
    """
    my_coordinates = get_coordinates(player.game_data.player_coordinates, player.player_id)
    my_distance_and_id = (get_distance(player.game_data.ball_coordinates, my_coordinates), player.player_id)

    mate_coordinates = get_coordinates(player.game_data.player_coordinates, player.mate_id)
    mate_distance_and_id = (get_distance(player.game_data.ball_coordinates, mate_coordinates), player.mate_id)

    distances_and_ids = [my_distance_and_id, mate_distance_and_id]
    distances = list(zip(*distances_and_ids))[0]
    _, closest_player_id = distances_and_ids[distances.index(min(distances))]

    closest_player: PlayerCoordinate = player.game_data.player_coordinates[closest_player_id - 1]
    return closest_player


def get_coordinates(coordinates, player_id):
    """ returns coordinates of given player

    :param coordinates: [PlayerCoordinates]; list of all the player coordinates
    :param player_id: int; id of given player
    :return: PlayerCoordinates; coordinates of given player
    """
    return coordinates[player_id - 1]


def is_ball_closer_to_goal_than_player(player: Player, player_id, is_own_goal=True):
    """ if ball is closer to given goal than given player

    :param player: Player; player that decides its action
    :param player_id: int; id of given player
    :param is_own_goal: boolean; if given goal is the goal that the given player defends
    :return: boolean; if ball is closer to given goal than given player
    """
    ball_x = player.game_data.ball_coordinates.pos_x
    player_x = get_coordinates(player.game_data.player_coordinates, player_id).pos_x
    goal1_x = (player.game_data.goal_1.post_1.pos_x + player.game_data.goal_1.post_2.pos_x) / 2
    goal2_x = (player.game_data.goal_2.post_1.pos_x + player.game_data.goal_2.post_2.pos_x) / 2
    if is_own_goal:
        goal_x = goal1_x if player.side == 1 else goal2_x
    else:
        goal_x = goal2_x if player.side == 1 else goal1_x
    return np.abs(ball_x - goal_x) < np.abs(player_x - goal_x)


def get_distance(coord1, coord2):
    """ calculates distance in pixel between two BasicCoordinates

    For calculation Pythagoras' theorem is used

    :param coord1: BasicCoordinate; coordinate 1
    :param coord2: BasicCoordinate; coordinate 2
    :return: float; distance in pixel
    """
    return np.sqrt((coord1.pos_x - coord2.pos_x) ** 2 + (coord1.pos_y - coord2.pos_y) ** 2)


# PLAYER ACTIONS
def intercept(player: Player):
    """ deciding player moves directly to the ball

    :param player: Player; player that decides its action
    """
    player.move_to_xy(player.game_data.ball_coordinates.pos_x,
                      player.game_data.ball_coordinates.pos_y,
                      destination_is_ball=True)


def guard(player: Player):
    """ deciding player moves to their own goal to defend it

    :param player: Player; player that decides its action
    """
    if player.side == 1:
        goal_coord_x = (player.game_data.goal_1.post_1.pos_x + player.game_data.goal_1.post_2.pos_x) / 2
        goal_coord_y = (player.game_data.goal_1.post_1.pos_y + player.game_data.goal_1.post_2.pos_y) / 2
    else:
        goal_coord_x = (player.game_data.goal_2.post_1.pos_x + player.game_data.goal_2.post_2.pos_x) / 2
        goal_coord_y = (player.game_data.goal_2.post_1.pos_y + player.game_data.goal_2.post_2.pos_y) / 2
    player.move_to_xy(goal_coord_x, goal_coord_y, avoid_ball=True)


def center(player: Player):
    """ deciding player moves to the center of the field

    :param player: Player; player that decides its action
    """
    goal1_coord_x = (player.game_data.goal_1.post_1.pos_x + player.game_data.goal_1.post_2.pos_x) / 2
    goal1_coord_y = (player.game_data.goal_1.post_1.pos_y + player.game_data.goal_1.post_2.pos_y) / 2
    goal2_coord_x = (player.game_data.goal_2.post_1.pos_x + player.game_data.goal_2.post_2.pos_x) / 2
    goal2_coord_y = (player.game_data.goal_2.post_1.pos_y + player.game_data.goal_2.post_2.pos_y) / 2

    center_coord_x = (goal1_coord_x + goal2_coord_x) / 2
    center_coord_y = (goal1_coord_y + goal2_coord_y) / 2

    player.move_to_xy(center_coord_x, center_coord_y, avoid_ball=True)


def recover(player: Player):
    """ deciding player recovers the ball and moves it away from their own goal

    :param player: Player; player that decides its action
    """
    player.update_own_coordinates()
    recover_y = player.y
    y_difference = 50
    if np.abs(recover_y - player.game_data.ball_coordinates.pos_y) < y_difference:
        recover_y += np.sign(recover_y - player.game_data.ball_coordinates.pos_y) * y_difference

    x_difference = 50
    recover_x = player.game_data.ball_coordinates.pos_x + np.sign(1.5 - player.side) * x_difference
    recover_x, recover_y = transform_to_boundary(player, recover_x, recover_y)
    player.move_to_xy(recover_x, recover_y)
    intercept(player)


def shoot(player: Player):
    """ deciding player shoots the ball to the enemy goal

    :param player: Player; player that decides its action
    """
    if player.side == 1:
        opp_goal_coord_x = (player.game_data.goal_2.post_1.pos_x + player.game_data.goal_2.post_2.pos_x) / 2
        opp_goal_coord_y = (player.game_data.goal_2.post_1.pos_y + player.game_data.goal_2.post_2.pos_y) / 2
        upper_boundary = player.game_data.goal_2.post_2.pos_y
        lower_boundary = player.game_data.goal_2.post_1.pos_y
    else:
        opp_goal_coord_x = (player.game_data.goal_1.post_1.pos_x + player.game_data.goal_1.post_2.pos_x) / 2
        opp_goal_coord_y = (player.game_data.goal_1.post_1.pos_y + player.game_data.goal_1.post_2.pos_y) / 2
        upper_boundary = player.game_data.goal_1.post_2.pos_y
        lower_boundary = player.game_data.goal_1.post_1.pos_y

    opp_goal_to_ball_x = player.game_data.ball_coordinates.pos_x - opp_goal_coord_x
    opp_goal_to_ball_y = player.game_data.ball_coordinates.pos_y - opp_goal_coord_y

    opp_goal_to_me_x = player.game_data.player_coordinates[player.player_id - 1].pos_x - opp_goal_coord_x

    # if the ball is close enough to the enemy goal, this step is ignored
    if not (np.abs(opp_goal_to_ball_x) < 50 and lower_boundary < player.game_data.ball_coordinates.pos_y < upper_boundary) or np.abs(opp_goal_to_ball_x) > np.abs(opp_goal_to_me_x):
        # calculates and moves to position that allows player to shoot to the center of the enemy goal
        distance_to_ball = 100
        direction_vector = np.array([opp_goal_to_ball_x, opp_goal_to_ball_y])
        ball_coordinate = np.array([player.game_data.ball_coordinates.pos_x, player.game_data.ball_coordinates.pos_y])
        shoot_x, shoot_y = ball_coordinate + (direction_vector / np.linalg.norm(direction_vector)) * distance_to_ball

        shoot_x, shoot_y = transform_to_boundary(player, shoot_x, shoot_y)
        player.move_to_xy(shoot_x, shoot_y)
    intercept(player)


def transform_to_boundary(player: Player, x_coord, y_coord):
    """ if x and y-coordinates are to close to the boundaries, they are relocated to the nearest point inside the valid
    field

    :param player: Player; player that decides its action
    :param x_coord: float; x-coordinate that gets checked
    :param y_coord: float; y-coordinate that gets checked
    :return: float, float; checked and (if needed) changed coordinates
    """
    x_boundary_width = (player.game_data.goal_1.post_2.pos_x - player.game_data.goal_2.post_2.pos_x) / 10
    x_boundary_lower = x_boundary_width + (player.game_data.goal_2.post_2.pos_x + player.game_data.goal_2.post_1.pos_x) / 2
    x_boundary_higher = - x_boundary_width + (player.game_data.goal_1.post_2.pos_x + player.game_data.goal_1.post_1.pos_x) / 2

    x_coord = x_coord if x_coord > x_boundary_lower else x_boundary_lower
    x_coord = x_coord if x_coord < x_boundary_higher else x_boundary_higher

    post_distance = player.game_data.goal_1.post_2.pos_y - player.game_data.goal_1.post_1.pos_y
    y_boundary_lower = player.game_data.goal_1.post_1.pos_y - 0.5 * post_distance
    y_boundary_higher = player.game_data.goal_1.post_2.pos_y + 0.5 * post_distance

    y_coord = y_coord if y_coord > y_boundary_lower else y_boundary_lower
    y_coord = y_coord if y_coord < y_boundary_higher else y_boundary_higher

    return x_coord, y_coord


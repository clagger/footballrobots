import time
import threading
from football_robots.player.player import Player, GameStatus
from football_robots.player.decision_tree import decide_action
from football_robots.player.ml_decision import ml_decide_action, load_ml_model


def main():
    """ main function of the robots

    """
    player = Player()
    player.connect_to_server()
    threading.Thread(target=player.log_to_database, daemon=True).start()
    if player.use_ml:
        load_ml_model(player)
    # let robot connect properly
    time.sleep(1)
    while 1:
        if player.game_data.game_status == GameStatus.START and not player.use_ml:
            decide_action(player)
        if player.game_data.game_status == GameStatus.START and player.use_ml:
            ml_decide_action(player)
        if player.game_data.game_status == GameStatus.INIT:
            player.move_to_init()


if __name__ == '__main__':
    main()

import sys
import threading
import time
import jsonpickle
import PySimpleGUI as sg
from football_referee.networking.multiClientServer import Server
from football_referee.object_tracking.object_tracker import Tracker
from football_referee.referee.referee import Referee
from football_robots.player.player import create_empty_game_data, GameStatus, BasicCoordinate


def createGUI():
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Button('Start', key='start'), sg.Button('Pause', key='pause', disabled=True),
               sg.Button('Stop', key='stop', disabled=True), sg.Text(key='time', size=(20, 1)),
               sg.Text(key='score', size=(20, 1))],
              [sg.Text(key='player_1', size=(100, 1))],
              [sg.Text(key='player_2', size=(100, 1))],
              [sg.Text(key='player_3', size=(100, 1))],
              [sg.Text(key='player_4', size=(100, 1))],
              [sg.Text(key='ball', size=(100, 1))],
              [sg.Text(key='status', size=(33, 1)), sg.Checkbox('log data', key='should_log', default=True)]
              ]

    # Create the Window in background thread
    window = sg.Window('Football Commander 3.2', layout)
    # guiThread = threading.Thread(target=, daemon=True).start()
    return window


def init_game(game_data):
    game_data.game_status = GameStatus.INIT


def update_gui(window, game_data, referee):
    # Read the Window Commands
    event, value = window.Read(timeout=100)

    for player_coord in game_data.player_coordinates:
        player = "player_" + str(player_coord.player_id)
        window.Element(player).update(
            "Player ID: {0} X: {1} Y: {2} Alpha: {3}".format(player_coord.player_id, player_coord.pos_x,
                                                             player_coord.pos_y, player_coord.alpha))

    window.Element('ball').update("Ball: X: {0} Y: {1}".format(game_data.ball_coordinates.pos_x,
                                                               game_data.ball_coordinates.pos_y))
    window.Element('status').update("Game Status: {0}".format(game_data.game_status))
    window.Element('time').update("Time left: {0}".format(round(referee.game_duration - referee.get_time_passed(game_data),2)))
    window['score'].update(f"Team Green {referee.score['Team 1']}:{referee.score['Team 2']} Team Red")
    if event in (sg.WIN_CLOSED, 'Quit'):  # if user closed the window using X or clicked Quit button
        return True
    elif event == "start":
        if referee.currently_playing:
            referee.resume_game(game_data)
        else:
            game_data.game_status = GameStatus.INIT
    elif event == "pause":
        referee.pause_game(game_data)
    elif event == 'stop':
        referee.stop_game(game_data)
    if game_data.game_status == GameStatus.START:
        window['start'].update(disabled=True)
        window['pause'].update(disabled=False)
        window['stop'].update(disabled=False)
    if game_data.game_status == GameStatus.STOP:
        window['start'].update(disabled=False)
        window['pause'].update(disabled=True)
        window['stop'].update(disabled=True)
    if game_data.game_status == GameStatus.PAUSE:
        window['start'].update(disabled=False)
        window['pause'].update(disabled=True)
        window['stop'].update(disabled=False)
    if game_data.game_status == GameStatus.INIT:
        window['start'].update(disabled=True)
        window['pause'].update(disabled=True)
        window['stop'].update(disabled=False)

    game_data.should_log = value['should_log']


def print_data(game_data, center):
    for coordinate in game_data.player_coordinates:
        print("Player ID: {0} X: {1} Y: {2} Alpha: {3}".format(coordinate.player_id, coordinate.pos_x,
                                                               coordinate.pos_y, coordinate.alpha))

    print("Ball: X: {0} Y: {1}".format(game_data.ball_coordinates.pos_x,
                                       game_data.ball_coordinates.pos_y))

    print("Goal 1: Post 1 X: {0} Y: {1} , Post 2 X: {2} Y: {3}".format(game_data.goal_1.post_1.pos_x,
                                                                       game_data.goal_1.post_1.pos_y,
                                                                       game_data.goal_1.post_2.pos_x,
                                                                       game_data.goal_1.post_2.pos_y))

    print("Goal 2: Post 1 X: {0} Y: {1} , Post 2 X: {2} Y: {3}".format(game_data.goal_2.post_1.pos_x,
                                                                       game_data.goal_2.post_1.pos_y,
                                                                       game_data.goal_2.post_2.pos_x,
                                                                       game_data.goal_2.post_2.pos_y))
    print("Game Status: {0}".format(game_data.game_status))
    print("Init 1: X {0} Y {1}".format(game_data.init_1.pos_x, game_data.init_1.pos_y))
    print("Init 2: X {0} Y {1}".format(game_data.init_2.pos_x, game_data.init_2.pos_y))
    print("Init 3: X {0} Y {1}".format(game_data.init_3.pos_x, game_data.init_3.pos_y))
    print("Init 4: X {0} Y {1}".format(game_data.init_4.pos_x, game_data.init_4.pos_y))
    print("Center X {0} Y {1}".format(center.pos_x, center.pos_y))


def main():
    game_data = create_empty_game_data()

    # Init Multiclient Server
    # create new server listening for connections
    s = Server()
    threading.Thread(target=s.startServer, daemon=True).start()

    # Init Player/Ball Tracking
    t = Tracker()
    threading.Thread(target=t.start_tracking, args=(game_data, 'blue',), daemon=True).start()

    referee = Referee(server=s, game_duration=300)
    # create GUI
    window = createGUI()

    while True:
        if update_gui(window, game_data, referee):
            sys.exit()
        referee.manage_game(game_data)
        data = jsonpickle.dumps(game_data)
        s.broadcast(data)
        time.sleep(0.2)


if __name__ == '__main__':
    main()

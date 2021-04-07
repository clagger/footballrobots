import xgboost
from sklearn.preprocessing import LabelEncoder

from football_robots.player.player import *
from football_robots.player.decision_tree import shoot, intercept, recover, center, guard
import pandas as pd


def load_ml_model(player: Player):
    if player.ml_type is None:
        print("Error: No ML Type set in player config json file")
        return

    if player.ml_type == "xgboost":
        xgb_model_latest = xgboost.XGBRegressor()
        xgb_model_latest.load_model("football_robots/ml_models/xgb.model")
        player.ml_model = xgb_model_latest

    print(f"Using ML: {player.ml_type}, Loaded model: {player.ml_model}")

    return


def ml_decide_action(player: Player):
    # build data frame for prediction!

    columns = ['time',
               'player_id',
               'mate_id',
               'team_id',
               'decision',
               'goals_team_1',
               'goals_team_2',
               'goal_1_post_1_x',
               'goal_1_post_1_y',
               'goal_1_post_2_x',
               'goal_1_post_2_y',
               'goal_2_post_1_x',
               'goal_2_post_1_y',
               'goal_2_post_2_x',
               'goal_2_post_2_y',
               'player_1_x',
               'player_1_y',
               'player_1_alpha',
               'player_2_x',
               'player_2_y',
               'player_2_alpha',
               'player_3_x',
               'player_3_y',
               'player_3_alpha',
               'player_4_x',
               'player_4_y',
               'player_4_alpha',
               'ball_x',
               'ball_y']

    df_predict = pd.DataFrame(columns=columns)

    data = [float(player.game_data.game_time),
            int(player.player_id),
            int(player.mate_id),
            int(player.side),
            None,
            int(player.game_data.goals_team1),
            int(player.game_data.goals_team2),
            float(player.game_data.goal_1.post_1.pos_x),
            float(player.game_data.goal_1.post_1.pos_y),
            float(player.game_data.goal_1.post_2.pos_x),
            float(player.game_data.goal_1.post_2.pos_y),
            float(player.game_data.goal_2.post_1.pos_x),
            float(player.game_data.goal_2.post_1.pos_y),
            float(player.game_data.goal_2.post_2.pos_x),
            float(player.game_data.goal_2.post_2.pos_y),
            float(player.game_data.player_coordinates[0].pos_x),
            float(player.game_data.player_coordinates[0].pos_y),
            float(player.game_data.player_coordinates[0].alpha),
            float(player.game_data.player_coordinates[1].pos_x),
            float(player.game_data.player_coordinates[1].pos_y),
            float(player.game_data.player_coordinates[1].alpha),
            float(player.game_data.player_coordinates[2].pos_x),
            float(player.game_data.player_coordinates[2].pos_y),
            float(player.game_data.player_coordinates[2].alpha),
            float(player.game_data.player_coordinates[3].pos_x),
            float(player.game_data.player_coordinates[3].pos_y),
            float(player.game_data.player_coordinates[3].alpha),
            float(player.game_data.ball_coordinates.pos_x),
            float(player.game_data.ball_coordinates.pos_y)]

    actions = {'shoot': 0, 'recover': 0, 'guard': 0, 'center': 0, 'intercept': 0}

    for action in actions:
        # fill first row of dataframe with data and replaced None value with action
        df_predict.loc[0] = [action if v is None else v for v in data]

    le_decision = LabelEncoder()
    le_decision.fit(["center", "guard", "intercept", "recover", "shoot"])
    df_predict['decision'] = le_decision.transform(df_predict['decision'])

    df_predict['player_id'] = df_predict['player_id'].astype('float64')
    df_predict['mate_id'] = df_predict['mate_id'].astype('float64')
    df_predict['team_id'] = df_predict['team_id'].astype('float64')
    df_predict['goals_team_1'] = df_predict['goals_team_1'].astype('float64')
    df_predict['goals_team_2'] = df_predict['goals_team_2'].astype('float64')

    for action in actions:
        # predict score and save it to action value
        actions[action] = player.ml_model.predict(df_predict)[0]

    # get action with highest score and execute action
    player.current_decision = max(actions, key=actions.get)
    print(f"Action: {player.current_decision} predicted highest score {actions[player.current_decision]}")

    if player.current_decision == "shoot":
        shoot(player)
    if player.current_decision == "recover":
        recover(player)
    if player.current_decision == "guard":
        guard(player)
    if player.current_decision == "center":
        center(player)
    if player.current_decision == "intercept":
        intercept(player)

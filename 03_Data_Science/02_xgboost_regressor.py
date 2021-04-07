#################
# Approach 1: Regression Model for score
# XGBoost Regression Model for predicting score for players actions
# Made with love
#################

import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.metrics import mean_squared_error, roc_curve, auc, roc_auc_score, recall_score, precision_score, f1_score, \
    accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV
from dfply import *
from sklearn.preprocessing import label_binarize, LabelEncoder, MinMaxScaler

import os

# Load Training Data
training_data = pd.read_csv('06_Data_Science/labeled_data.csv')

# Convert categorical columns to numeric encoding
training_data.dtypes
training_data['decision'] = training_data['decision'].astype('category')
training_data['player_id'] = training_data['player_id'].astype('category')
training_data['mate_id'] = training_data['mate_id'].astype('category')
training_data['team_id'] = training_data['team_id'].astype('category')

training_data.dtypes
le = LabelEncoder()
le.fit(training_data['decision'])
training_data['decision'] = le.transform(training_data['decision'])

le.fit(training_data['player_id'])
training_data['player_id'] = le.transform(training_data['player_id'])

le.fit(training_data['mate_id'])
training_data['mate_id'] = le.transform(training_data['mate_id'])

le.fit(training_data['team_id'])
training_data['team_id'] = le.transform(training_data['team_id'])

# separate label from rest of features
features_training, labels_training = training_data.iloc[:, 0:-1], training_data.iloc[:, -1:]

# scale scores to 0 - 1 using minmax scaler
min_max_scaler = MinMaxScaler()
labels_training = min_max_scaler.fit_transform(labels_training)

# create DMatrix
data_dmatrix = xgb.DMatrix(data=features_training, label=labels_training)

# split up training data into 80% training and 20% validation data
features_train, features_val, labels_train, labels_val = train_test_split(features_training, labels_training,
                                                                          test_size=0.2, random_state=123)

# setup objective and hyperparameters
# TODO Hyperparameter Optimization with GridSearch
xg_reg = xgb.XGBRegressor(objective='reg:squarederror', colsample_bytree=0.3, learning_rate=0.1, max_depth=5, alpha=10,
                          n_estimators=50)

# fit the model with training data
xg_reg.fit(features_train, labels_train)

# predict score of validation data
pred_val_scores = xg_reg.predict(features_val)

# compare predicted weights to real validation weights
rmse = np.sqrt(mean_squared_error(labels_val, pred_val_scores))
print("RMSE: %f" % (rmse))

# save model
xg_reg.save_model("football_robots/ml_models/xgb.model")


## Test to build dataframe with one row (for usage in game)

columns = ['time',
           'player_id',
           'mate_id',
           'team_id',
           'decision',
           'goal_team_1',
           'goal_team_2',
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

xg_reg.predict(features_val[:1])



first_row = list(features_val.iloc[0])
test = pd.DataFrame(columns=columns)
test.loc[0] = first_row

xg_reg.predict(test)[0]


# get highest score from key value map
actions = {'shoot': 0.2, 'cover': 0, 'guard': 0.6, 'center': 0, 'intercept': 0}

max(actions, key=actions.get)
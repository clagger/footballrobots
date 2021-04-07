### Random Forest Regression


# Import needed libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import label_binarize, LabelEncoder, MinMaxScaler

# Importing the dataset
path = '06_Data_Science/labeled_data.csv'
training_data = pd.read_csv(path)

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


# split up training data into 80% training and 20% validation data
from sklearn.model_selection import train_test_split
features_train, features_val, labels_train, labels_val = train_test_split(features_training, labels_training,
                                                                          test_size=0.2, random_state=123)

# Training the Random Forest Regression model on the whole dataset
from sklearn.ensemble import RandomForestRegressor
regressor = RandomForestRegressor(n_estimators=5, random_state=0)
regressor.fit(features_train, labels_train.ravel())

# predict score of validation data
pred_val_scores = regressor.predict(features_val)

# compare predicted weights to real validation weights
from sklearn.metrics import mean_squared_error
rmse = np.sqrt(mean_squared_error(labels_val, pred_val_scores))
print("RMSE: %f" % (rmse))


# save model
rf_reg.save_model("football_robots/ml_models/rf_reg.model")
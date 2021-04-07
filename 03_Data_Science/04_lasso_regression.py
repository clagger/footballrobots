import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import label_binarize, LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split

import pickle
from numpy import arange
import os
# create 5 models
# 1 for each action
# feed data data to all models and take action with highest score

training_data = pd.read_csv(r'/home/tmo/Projects/dat19_footballrobots/06_Data_Science/labeled_data.csv')

# this func replaces the categorical variables with 0 & 1 depending on the passed decision param
training_data['decision'] = training_data['decision'].astype('category')
training_data['player_id'] = training_data['player_id'].astype('category')
training_data['mate_id'] = training_data['mate_id'].astype('category')
training_data['team_id'] = training_data['team_id'].astype('category')


le = LabelEncoder()
le.fit(training_data['decision'])
training_data['decision'] = le.transform(training_data['decision'])

le.fit(training_data['player_id'])
training_data['player_id'] = le.transform(training_data['player_id'])

le.fit(training_data['mate_id'])
training_data['mate_id'] = le.transform(training_data['mate_id'])

le.fit(training_data['team_id'])
training_data['team_id'] = le.transform(training_data['team_id'])


#split up data & label
features_training, labels_training = training_data.iloc[:, 0:-1], training_data.iloc[:, -1:]


# scale scores to 0 - 1 using minmax scaler
min_max_scaler = MinMaxScaler()
labels_training = min_max_scaler.fit_transform(labels_training)





#Creating the LASSO model
#Without alhpa   using GridSearch to find optimal alpha
model = Lasso()

#Grid Search for finding the best hyperparams
#Creating Validation method
#Setting the RMSE as Scoring Param
grid = dict()
grid['alpha'] = arange(0, 1, 0.01)
grid['tol']=arange(0.0001,0.1,0.001)
cross_val = RepeatedKFold(n_splits=10, n_repeats=10, random_state=5)
search = GridSearchCV(model, grid, scoring='neg_root_mean_squared_error', cv=cross_val, n_jobs=-1)



# split up training data into 80% training and 20% validation data
# 80% train 20% validation data
features_train, features_val, labels_train, labels_val = train_test_split(features_training, labels_training,
                                                                          test_size=0.2, random_state=123)

#training and validating 
#also finding 

# perform the search
results = search.fit(features_train, labels_train.ravel())


#Printing the result
print('RMSE: %.3f' % results.best_score_)
print('Best Alpha: %s' % results.best_params_)
# -*- coding: utf-8 -*-
"""
Stacked regressor to combine multiple models

@author: a.stratigakos
"""

import gurobipy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor

cd = os.path.dirname(__file__)  #Current directory
sys.path.append(cd)
project_dir=Path(cd).parent.__str__()   #project_directory

#%%

predictor_1 = pd.read_csv(project_dir+'\\data\\submission\\akylas\\Predictor1.csv', 
                          index_col = 0, parse_dates =True)

predictor_2 = pd.read_csv(project_dir+'\\data\\submission\\akylas\\Predictor2.csv', 
                          index_col = 0, parse_dates =True)

data_path = project_dir + '\\data\\processed_data'

hhour_df = pd.read_csv(data_path+'\\half_hourly_power_staplegrove.csv', 
                       index_col = 0, parse_dates =True, dayfirst=True)

#%%

# The predictions from the individual models are used as features in a stacked regression
# This implies an additional training set for the stacked regressor
# Example:
train_start = '2021-07-01'
train_stop = '2021-07-31'
valid_start = '2021-08-01'


train_vmax = hhour_df['value_max'][train_start:train_stop].values
train_vmin = hhour_df['value_min'][train_start:train_stop].values

trainX_max = np.column_stack((predictor_1['value_max'][:train_stop].values, predictor_2['value_max'][:train_stop].values))
trainX_min = np.column_stack((predictor_1['value_max'][:train_stop].values, predictor_2['value_max'][:train_stop].values))

testX_max = np.column_stack((predictor_1['value_max'][valid_start:].values, predictor_2['value_max'][:train_stop].values))
testX_min = np.column_stack((predictor_1['value_max'][valid_start:].values, predictor_2['value_max'][:train_stop].values))

final_Pred_ub = np.zeros(len(predictor_1['value_max'][valid_start:]))
final_Pred_lb = np.zeros(len(predictor_1['value_max'][valid_start:]))

#%%
#!!!!! this implies all days are full length, might have an issue in the final data set
periods = 48    # number of timesteps per day
ndays = int(len(train_vmax)/periods)
num_models = trainX_max.shape[1]
plot = False
for i in range(periods):
    
    # Separate model per each timestep
    # Constrained regression (convex combination of predictors)
    m = gp.Model()

    # Coef is >=0, this could be relaxed
    coef = m.addMVar(num_models, vtype = gp.GRB.CONTINUOUS, lb = 0)
    error = m.addMVar(ndays, vtype = gp.GRB.CONTINUOUS, lb = -gp.GRB.INFINITY)
                
    # Constraints
    m.addConstr( sum(coef) == 1)
    m.addConstr( error == train_vmax[i::periods] - trainX_max[i::periods]@coef)
    m.setObjective( error@error, gp.GRB.MINIMIZE)
    m.optimize()

    final_Pred_ub[i::periods] = testX_max[i::periods]@coef.X

    # Examine weight of each learner
    if plot:
        plt.bar(0, coef.X[0])
        plt.bar(1, coef.X[1])
        plt.xticks([0,1], ['Model 1', 'Model 2'])        
        plt.show()

    # Same model for v_min
    m = gp.Model()

    # Coef is >=0, this could be relaxed
    coef = m.addMVar(num_models, vtype = gp.GRB.CONTINUOUS, lb = 0)
    error = m.addMVar(ndays, vtype = gp.GRB.CONTINUOUS, lb = -gp.GRB.INFINITY)
                
    # Constraints
    m.addConstr( sum(coef) == 1)
    m.addConstr( error == train_vmin[i::periods] - trainX_min[i::periods]@coef)
    m.setObjective( error@error, gp.GRB.MINIMIZE)
    m.optimize()

    final_Pred_lb[i::periods] = testX_min[i::periods]@coef.X
#%%
final_Pred = pd.DataFrame(data = np.column_stack((final_Pred_ub, final_Pred_lb)), 
                          columns = ['value_max', 'value_min'], index = predictor_1[valid_start:].index)
#%%
ax = predictor_1[valid_start:]['value_max'].plot(label='Model 1')
predictor_1[valid_start:]['value_max'].plot(label='Model 2', ax=ax)
final_Pred[valid_start:]['value_max'].plot(label='Stacked Regressor', ax=ax)





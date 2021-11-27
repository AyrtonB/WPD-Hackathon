# -*- coding: utf-8 -*-
"""
Base forecasting model:
    Random forest to predict both directions
    Weather data from all the stations
    Power measurement data from Staplegrove
@author: akylas.stratigakos@mines-paristech.fr
"""

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
plt.rcParams['figure.dpi'] = 600

#from Utility_functions import *

#%% Load processed data
data_path = project_dir + '\\data\\processed_data'

spg_weather_df = pd.read_csv(data_path+'\\weather_staplegrove.csv', 
                         index_col=0, parse_dates = True, dayfirst=True)

msh_weather_df = pd.read_csv(data_path+'\\weather_mousehole.csv', 
                         index_col=0, parse_dates = True, dayfirst=True)

hhour_df = pd.read_csv(data_path+'\\half_hourly_power_staplegrove.csv', 
                       index_col = 0, parse_dates =True, dayfirst=True)

#minute_df = pd.read_csv(data_path+'\\minute_power_staplegrove.csv', index_col = 0, parse_dates =True, dayfirst=True)

#%% Process weather data from stations

# Keep only the following variables
weather_variables = ['temperature', 'solar_irradiance', 'pressure',
                     'spec_humidity', 'speed', 'direction']
weather_feat = [ f+'_'+str(i) for i in range(1,6) for f in weather_variables]

header = pd.MultiIndex.from_product([['staplegrove', 'mousehole'], 
                                     weather_feat], names=['Area','Variable'])
# merge w multiheader
weather_df = pd.DataFrame(data=np.column_stack((spg_weather_df[weather_feat].values, msh_weather_df[weather_feat].values)), 
                          columns = header, index = spg_weather_df.index)

# Create max/min/mean/range
for area in ['staplegrove', 'mousehole']:
    
    weather_df[area, 'solar_max'] = weather_df[area][['solar_irradiance_' + str(i) for i in range(1,6)]].max(axis=1)
    weather_df[area, 'solar_min'] = weather_df[area][['solar_irradiance_' + str(i) for i in range(1,6)]].min(axis=1)
    weather_df[area, 'solar_mean'] = weather_df[area][['solar_irradiance_' + str(i) for i in range(1,6)]].mean(axis=1)
    weather_df[area, 'solar_range'] = weather_df[area,'solar_max'] - weather_df[area,'solar_min']

    weather_df[area, 'solar_max_grad'] = weather_df[area, 'solar_max'].diff()
    weather_df[area, 'solar_mean_grad'] = weather_df[area, 'solar_mean'].diff()
        
    weather_df[area, 'solar_max_roll'] = weather_df[area, 'solar_max'].ewm(alpha=0.9).mean()
    weather_df[area, 'solar_mean_roll'] = weather_df[area, 'solar_mean'].ewm(alpha=0.9).mean()
    
    for i in range(1,6):
        weather_df[area, 'direction_'+str(i)] = np.sin(np.deg2rad(weather_df[area, 'direction_'+str(i)]))

#%%

target_df = hhour_df.copy()
target_df['range'] = target_df['value_max']-target_df['value_min']
target_df['ub'] = target_df['value_max']-target_df['value']
target_df['lb'] = target_df['value']-target_df['value_min']

## Create features
Predictors = hhour_df['value'].to_frame()
Predictors = Predictors.join(weather_df.resample('30 Min').interpolate(), how='left')

Predictors['Month'] = Predictors.index.month
Predictors['Day'] = Predictors.index.weekday
Predictors['Hour'] = Predictors.index.hour
Predictors['Minute'] = Predictors.index.minute
Predictors['Day_year'] = Predictors.index.day_of_year

##### Temporal features of measured power

# Eigendecomposition in trajectory matrix
trajectory_mat = Predictors['value'].to_frame()

for lag in range(1, 7*48+1):
    trajectory_mat['value-'+str(lag)] = trajectory_mat['value'].shift(lag)

trajectory_mat = trajectory_mat.dropna()


pca = PCA(n_components = 20)
pca.fit(trajectory_mat)

plt.plot(pca.explained_variance_ratio_.cumsum())
plt.hlines(.90, 0, pca.n_components, linestyle='--', color='black')
plt.title('Percentage Variance Explained')
plt.show()

PCs = pca.fit_transform(trajectory_mat)
PCs = pd.DataFrame(data=PCs, columns = ['PC'+str(i+1) for i in range(pca.n_components)], index = trajectory_mat.index)

# Left join on predictors
Predictors = Predictors.join(PCs, how='left')

# Rate of change
Predictors['val_grad'] = Predictors['value'].diff()
Predictors['val_grad_2'] = Predictors['val_grad'].diff()
Predictors['val_grad_3'] = Predictors['val_grad_2'].diff()

# Historical lags
lags = list(np.arange(1, 7)) + [48, 2*48, 7*48]
for lag in lags:
    Predictors['val_lag_'+str(lag)] = Predictors['value'].shift(lag)

#### Temporal features of weather variables
# Lags on irradiance and wind speed
for c in Predictors.columns:
    if len(c)>1:
        if ('solar_irradiance' in c[1])or(('temperature' in c[1])):        
            print(c)    
            for lag in np.arange(1, 3):
                Predictors[c[0], c[1]+'_lag_'+str(lag)] = Predictors[c].shift(lag)
            
# Rolling averages for power
Predictors['value_roll_std'] = Predictors['value'].ewm(alpha=0.9).std()
Predictors['value_roll_mean_fast'] = Predictors['value'].ewm(alpha=0.9).mean()
Predictors['value_roll_mean_slow'] = Predictors['value'].ewm(alpha=0.01).mean()

Predictors['value_roll_min'] = Predictors['value'].rolling(12).min()
Predictors['value_roll_max'] = Predictors['value'].rolling(12).max()

Predictors = Predictors.dropna()
#%%
train_stop = '2021-07-31'

valid_start = '2021-08-01'
valid_stop = '2021-08-31'

train_Pred = Predictors[:train_stop]
valid_Pred = Predictors[valid_start:valid_stop]

train_vmax = hhour_df['value_max'][train_Pred.index]
valid_vmax = hhour_df['value_max'][valid_Pred.index]

train_ub_diff = (hhour_df['value_max']-hhour_df['value'])[train_Pred.index]
valid_ub_diff = (hhour_df['value_max']-hhour_df['value'])[valid_Pred.index]

train_lb_diff = (hhour_df['value']-hhour_df['value_min'])[train_Pred.index]
valid_lb_diff = (hhour_df['value']-hhour_df['value_min'])[valid_Pred.index]

train_vmin = (hhour_df['value_min'])[train_Pred.index]
valid_vmin = (hhour_df['value_min'])[valid_Pred.index]

################ Forecasting 

# store results
Pred_ub = pd.DataFrame(data=[], index = valid_Pred.index)
Pred_lb = pd.DataFrame(data=[], index = valid_Pred.index)

#%% Train forecasting model (single model for both directions)

rf_single = ExtraTreesRegressor(n_estimators = 1000, n_jobs = -1)
rf_single.fit(train_Pred, np.column_stack((train_ub_diff, train_lb_diff)))

rf_joint_predictions = rf_single.predict(valid_Pred)

Pred_ub['RF'] = rf_joint_predictions[:,0] + valid_Pred['value'].values
Pred_lb['RF'] = valid_Pred['value'].values - rf_joint_predictions[:,1]

t = 2*48
plt.plot(valid_Pred['value'].values[t:t+96])
plt.plot(Pred_ub['RF'].values[t:t+96], '--')
plt.plot(Pred_lb['RF'].values[t:t+96], '--')
plt.show()

p = 20
importances = rf_single.feature_importances_
std = np.std([tree.feature_importances_ for tree in rf_single.estimators_], axis=0)
indices = np.argsort(importances)[::-1]

plt.barh(range(p), importances[indices[:p]], yerr = std[indices[:p]])
plt.yticks(range(p), train_Pred.columns[indices[:p]])
plt.show()

#print('Single model: ')
#print(eval_point_pred(Pred_ub['RF'], valid_ub.values, digits=3))
#print(eval_point_pred(Pred_lb['RF'], valid_lb.values, digits=3))

#%%
selected = 'RF'
output = pd.DataFrame(data = np.column_stack((Pred_ub[selected].values, Pred_lb[selected].values)),
                      index = valid_Pred['2021-08-01':].index, columns = ['value_max', 'value_min'])

output.to_csv(project_dir+'\\data\\submission\\akylas\\predictions.csv')
from torch import nn, Tensor
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import Adam
from wpdhack import data, feature
from wpdhack.suite import construct_prediction_df
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
device = torch.device('cuda:0')

def weights_init(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight)
        torch.nn.init.zeros_(m.bias)

# Load Data

data_dir: str='data'
model_1_kwargs: dict={}
model_2_kwargs: dict={}
data_kwargs: dict={
    'real_power_sub_dir': 'real_power',
    'weather_sub_dir': 'weather',
    'real_power_time_period': '_pre_august',
    'real_power_site': 'Staplegrove_CB905',
    'weather_grid_point': 'staplegrove_1',
    'weather_interpolate_method': 'interpolate',
    'use_target_delta': False
}
features_kwargs: dict={
        'features': ['temporal', 'dir_speed', 'hcdh', 'lagged']
    }
cols_subset: list=['value', 'temperature', 'solar_irradiance', 'pressure',
                       'spec_humidity', 'hour', 'windspeed_north', 'windspeed_east', 
                       'doy', 'speed', 'direction', 'weekend', 'hcdh']
y1_col: str='value_max'
y2_col: str='value_min'
df_features, df_target = data.construct_baseline_features_target_dfs(data_dir, **data_kwargs)
df_features = feature.create_additional_features(df_features, df_target, **features_kwargs)
df_features = feature.process_features(df_features, cols_subset=cols_subset)

print('FEATURES: ', type(df_features))
print('TARGET: ', type(df_target))

df_features = np.asanyarray(df_features).astype('float32')
df_target = np.asanyarray(df_target).astype('float32')
x_mean = np.mean(df_features, axis = 0)
x_std = np.std(df_features, axis = 0)
X = (df_features - x_mean)/x_std
y_mean = np.mean(df_target, axis = 0)
y_std = np.std(df_target, axis = 0)
Y = (df_target - y_mean)/y_std
print(Y.shape, ' ', X.shape)
X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.3)
# Transform to Tensors. 
x_tensor = torch.from_numpy(X_train)
y_tensor = torch.from_numpy(Y_train)
xv_tensor = torch.from_numpy(X_val)
yv_tensor = torch.from_numpy(Y_val)
train_ds = TensorDataset(x_tensor, y_tensor)
val_ds = TensorDataset(xv_tensor, yv_tensor)

# model definition
model = nn.Sequential(
    nn.Linear(X.shape[1],150), 
    nn.ReLU(), 
    nn.Linear(150, 150), 
    nn.ReLU(), 
    nn.Linear(150, 2)
)

model.to(device)
model.apply(weights_init)

optimizer = Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()
trainloader = DataLoader(train_ds, batch_size=1024, shuffle=True)
testloader = DataLoader(val_ds, batch_size=128, shuffle=False)

# training process

for epoch in range(50):
    model.train()
    running_loss = 0
    train_pred = []
    train_out = []
    for i, tdata in enumerate(trainloader):
        optimizer.zero_grad()
        x, y = tdata
        x, y = x.to(device), y.to(device)
        y_hat = model(x)
        loss = loss_fn(y_hat, y)
        loss.backward()
        optimizer.step()
        running_loss+=loss.item()
        train_pred.append(y_hat.to('cpu').data.numpy())
        train_out.append(y.to('cpu').data.numpy())
    train_pred = np.concatenate(train_pred, axis=0)
    train_out = np.concatenate(train_out, axis=0)
    print(epoch, ' MSE: ', mean_squared_error(train_pred, train_out))
    if epoch%10==0 or epoch==49:
        model.eval()
        val_out = []
        val_pred = []
        for i, tdata in enumerate(testloader):
            x, y = tdata
            x, y = x.to(device), y.to(device)
            y_hat = model(x)
            val_pred.append(y_hat.to('cpu').data.numpy())
            val_out.append(y.to('cpu').data.numpy())
        val_out = np.concatenate(val_out, axis=0)
        val_pred = np.concatenate(val_pred, axis=0)

        print('Validation: ', epoch, ' ', mean_squared_error(val_out, val_pred))



# Submission
params = {
    'data_dir': 'data',
    'data_kwargs': {
        'real_power_sub_dir': 'real_power',
        'weather_sub_dir': 'weather',
        'real_power_time_period': '_pre_august',
        'real_power_site': 'Staplegrove_CB905',
        'weather_grid_point': 'staplegrove_1',
        'weather_interpolate_method': 'interpolate',
        'use_target_delta': False
    },
    'y1_col': 'value_max',
    'y2_col': 'value_min',
    'split_kwargs': {
        'n_splits': 5, 
        'shuffle': False
    },
    'cols_subset': ['value', 'temperature', 'solar_irradiance', 'pressure',
                     'spec_humidity', 'hour', 'windspeed_north', 'windspeed_east',
                     'doy', 'speed', 'direction', 'weekend', 'hcdh'],
    'features_kwargs': {
        'features': ['temporal', 'dir_speed', 'hcdh', 'lagged']
    }
}
data_dir = params['data_dir']
df_observation_submission = data.load_real_power_dataset(f'{data_dir}/real_power', site='Staplegrove_CB905', real_power_variable='observation_variable_half_hourly', time_period='_august')
df_weather = data.load_weather_df(f'{data_dir}/weather', 'staplegrove_1')

common_idxs = df_observation_submission.index.intersection(df_weather.index)

df_submission_features = df_observation_submission.loc[common_idxs].copy()
df_submission_features[df_weather.columns] = df_weather.loc[common_idxs].copy()
df_submission_features = feature.create_additional_features(df_submission_features, **params['features_kwargs'])
df_submission_features = feature.process_features(df_submission_features, cols_subset=params['cols_subset'])
submission_index = df_submission_features.index
X_submission = df_submission_features.values

print(X_submission.shape)
X_sub = (X_submission-x_mean)/x_std
X_sub = np.asanyarray(X_sub).astype('float32')

y_sub = np.empty_like(X_sub)
X_sub = torch.from_numpy(X_sub)
y_sub = torch.from_numpy(y_sub)
sub_ds = TensorDataset(X_sub, y_sub)
sub_loader = DataLoader(sub_ds, batch_size=128, shuffle=False)

model.eval()
pred = []
for i, tdata in enumerate(sub_loader):
    x, y = tdata
    x = x.to(device)
    pred.append(model(x).to('cpu').data.numpy())

pred = np.concatenate(pred, axis=0)
pred = pred*y_std+y_mean
submissions_dir: str='data/submission'


df_pred = construct_prediction_df(pred[:,0], pred[:,1], submission_index, df_submission_features)
df_pred.to_csv(f'{submissions_dir}/archive/predictions_{pd.Timestamp.now().strftime("%Y-%m-%d %H-%M-%S")}.csv')

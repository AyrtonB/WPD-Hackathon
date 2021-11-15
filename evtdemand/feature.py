# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03a-feature-generation.ipynb (unless otherwise specified).

__all__ = ['dt_rng_to_SPs', 'create_temporal_features', 'create_dir_speed_features', 'calc_hcdh_factor',
           'create_hcdh_features', 'create_prev_month_stats_df', 'create_additional_features', 'process_features']

# Cell
import numpy as np
import pandas as pd

from evtdemand import data

# Cell
def dt_rng_to_SPs(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    freq: str='30T',
    tz: str='Europe/London'
):
    dt_rng = pd.date_range(start_date, end_date, freq=freq, tz=tz)

    SPs = list((2*(dt_rng.hour + dt_rng.minute/60) + 1).astype(int))
    dt_strs = list(dt_rng.strftime('%Y-%m-%d'))

    df_dates_SPs = pd.DataFrame({'date':dt_strs, 'SP':SPs}, index=dt_rng).astype(str)

    # Accounting for clock changes
    clock_change_dt_idxs_dir = pd.Series(dt_rng).apply(lambda dt: dt.utcoffset().total_seconds()).diff().replace(0, np.nan).dropna()

    for dt_idx, dir_ in clock_change_dt_idxs_dir.items():
        dt = dt_rng[dt_idx].date()
        SPs = (1 + 2*(dt_rng[dt_rng.date==dt] - pd.to_datetime(dt).tz_localize('Europe/London')).total_seconds()/(60*60)).astype(int)

        df_dates_SPs.loc[df_dates_SPs.index.date==dt, 'SP'] = SPs

    return df_dates_SPs

def create_temporal_features(df_features: pd.DataFrame):
    df_dates_SPs = dt_rng_to_SPs(
        df_features.index.min().strftime('%Y-%m-%d %H:%M'),
        df_features.index.max().strftime('%Y-%m-%d %H:%M')
    )

    df_dates_SPs.index = df_dates_SPs.index.tz_convert('UTC')

    df_temporal = pd.DataFrame({
        # 'SP': df_dates_SPs['SP'].values,
        'hour': df_features.index.hour + df_features.index.minute/60,
        'doy': df_features.index.dayofyear,
        'weekend': df_features.index.dayofweek.isin([5, 6])
    }, index=df_features.index)

    return df_temporal

# Cell
def create_dir_speed_features(s_U: pd.Series, s_V: pd.Series):
    df_speed_dir = pd.DataFrame({
        'direction': np.mod(180 + np.rad2deg(np.arctan2(s_U, s_V)), 360),
        'speed': np.sqrt(s_U**2 + s_V**2)
    })

    return df_speed_dir

# Cell
def calc_hcdh_factor(
    t: float,
    hbt: float=10,
    cbt: float=20,
    beta_0: float=0,
    beta_1: float=1,
    beta_2: float=2
):
    if isinstance(t, pd.Series):
        hdh = (hbt-t).to_frame().assign(ref=0).max(axis=1)
        cdh = (t-cbt).to_frame().assign(ref=0).max(axis=1)

    else:
        hdh = max(0, hbt-t)
        cdh = max(0, t-cbt)

    hcdh_factor = beta_0 + beta_1*hdh + beta_2*cdh

    return hcdh_factor

def create_hcdh_features(df_features: pd.DataFrame):
    df_hcdh_factor = calc_hcdh_factor(df_features['temperature']).to_frame()
    df_hcdh_factor = df_hcdh_factor.rename(columns={0: 'hcdh'})

    return df_hcdh_factor

# Cell
def create_prev_month_stats_df(df_features: pd.DataFrame, df_target: pd.DataFrame):
    s_avg_to_max = df_target['value_max'] - df_features['value']
    s_avg_to_min = df_target['value_min'] - df_features['value']

    df_prev_month_stats = pd.DataFrame({
        'prev_month_max_avg': s_avg_to_max.resample('MS').mean().shift().reindex(s_avg_to_max.index).ffill().dropna(),
        'prev_month_max_max': s_avg_to_max.resample('MS').max().shift().reindex(s_avg_to_max.index).ffill().dropna(),
        'prev_month_min_avg': s_avg_to_min.resample('MS').mean().shift().reindex(s_avg_to_min.index).ffill().dropna(),
        'prev_month_min_min': s_avg_to_min.resample('MS').min().shift().reindex(s_avg_to_min.index).ffill().dropna()
    })

    return df_prev_month_stats

# Cell
def create_additional_features(
    df_features: pd.DataFrame,
    df_target: pd.DataFrame,
    features: list=['temporal', 'dir_speed', 'hcdh', 'prev_month_stats']
):
    if 'temporal' in features:
        df_features = df_features.merge(create_temporal_features(df_features), left_index=True, right_index=True)

    if 'dir_speed' in features:
        df_features = df_features.merge(create_dir_speed_features(df_features['windspeed_east'], df_features['windspeed_north']), left_index=True, right_index=True)

    if 'hcdh' in features:
        df_features = df_features.merge(create_hcdh_features(df_features), left_index=True, right_index=True)

    if 'prev_month_stats' in features:
        df_features = df_features.merge(create_prev_month_stats_df(df_features, df_target), left_index=True, right_index=True)

    df_features = df_features.dropna()

    return df_features

# Cell
def process_features(
    df_features: pd.DataFrame,
    cols_subset = ['value', 'temperature', 'solar_irradiance', 'windspeed_north',
                   'windspeed_east', 'pressure', 'spec_humidity', 'hour', 'doy',
                   'weekend', 'direction', 'speed', 'hcdh'],
):
    df_features_processed = df_features.copy()

    common_cols_subset = df_features_processed.columns.intersection(pd.Index(cols_subset))
    df_features_processed = df_features_processed[common_cols_subset]

    return df_features_processed
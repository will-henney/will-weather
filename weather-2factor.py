import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_color_codes('dark')

df_inside = pd.read_csv("netatmo_station.csv", sep=';', index_col=1, parse_dates=True)
df_outside = pd.read_csv("netatmo_module.csv", sep=';', index_col=1, parse_dates=True)
df_rain =  pd.read_csv("netatmo_rain.csv", sep=';', index_col=1, parse_dates=True)

# Correct the pressures from before 2019-07
lowmask = df_inside.Pressure < 1000.0
df_inside.Pressure[lowmask] += 212.0


figfile = "weather-pairplot.png"

# Resample by day and by hour
dfi_max_day = df_inside.resample('1D').max()
dfi_min_day = df_inside.resample('1D').min()
dfi_med_hr = df_inside.resample('1H').mean()

dfo_med_hr = df_outside.resample('1H').mean()
dfr_sum_hr = df_rain.resample("1H").sum()

# Restrict to afternoons, 12am to 5pm
# pm_indices = dfi_med_hr.index.indexer_between_time('12:00', '17:00')

# Restrict to daytime: 
day_indices = dfi_med_hr.index.indexer_between_time('07:00', '19:00')

df = dfi_med_hr.join(dfo_med_hr, rsuffix=" out").join(dfr_sum_hr, rsuffix=" rain")
df = df.iloc[day_indices]
df = df.fillna(method='bfill')


# df = dfi_min_day
variables = ['Temperature', 'Temperature out', 'CO2', 'Humidity', 'Humidity out', 'Noise', 'Pressure', 'Rain']
minmax = {
    'Temperature': [0, 35],
    'Temperature out': [0, 35],
    'CO2': [300, 1000],
    'Humidity': [0, 100],
    'Humidity out': [0, 100],
    'Noise': [30, 70],
    'Pressure': [1010, 1030],
    'Rain': [0.1, 25],
}
variables = list(minmax)
g = sns.PairGrid(df, vars=variables, height=1.5)
g = g.map_upper(plt.scatter, marker='.', alpha=0.03, facecolor='r', edgecolor='none')
g = g.map_lower(sns.kdeplot, cmap="Purples_d", n_levels=15)
g = g.map_diag(plt.hist)
# Make sure graph limits are always consistent
for j, k in enumerate(variables):
    g.axes[j, j].set(xlim=minmax[k], ylim=minmax[k])
g.fig.suptitle("Hourly means, daytime only (7AM-7PM)")
g.savefig(figfile)


# Repeat for night time
night_indices = dfi_med_hr.index.indexer_between_time('19:00', '07:00')
df = dfi_med_hr.join(dfo_med_hr, rsuffix=" out").join(dfr_sum_hr, rsuffix=" rain")
df = df.iloc[night_indices]
df = df.fillna(method='bfill')
g = sns.PairGrid(df, vars=variables, size=1.5)
g = g.map_upper(plt.scatter, marker='.', alpha=0.03, facecolor='r', edgecolor='none')
g = g.map_lower(sns.kdeplot, cmap="Purples_d", n_levels=15)
g = g.map_diag(plt.hist)
# Make sure graph limits are same for night and day
for j, k in enumerate(variables):
    g.axes[j, j].set(xlim=minmax[k], ylim=minmax[k])
g.fig.suptitle("Hourly means, nighttime only (7PM-7AM)")
g.savefig(figfile.replace(".png", "-night.png"))

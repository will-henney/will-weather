# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Historic Morelia weather records from NOAA

# These records are from https://www.ncdc.noaa.gov/cdo-web/orders?id=2079422&email=will@henney.org

# In theory they cover the mean/min/max temperature, plus rainfall for the Morelia weather station from 1977 to 2020.  They do not cover humidity unfortunately.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_color_codes()

df = pd.read_csv("../2079422.csv", index_col=2, parse_dates=True)
df

df.describe()

df.plot("DATE", ["TMIN", "TAVG", "TMAX"], figsize=(20,3), lw=0.2, alpha=0.8)

df.plot("DATE", "PRCP", figsize=(20,2), lw=0.2, logy=True)



df.index.day

df["DAY"] = df.index.dayofyear

df.plot("DAY", "TAVG", figsize=(20,10), lw=0.2)

df.plot("DAY", "PRCP", figsize=(20,10), lw=0.2, logy=True)

df_outside = pd.read_csv("../netatmo_module.csv", sep=';', index_col=1, parse_dates=True)

df_outside.describe()

df_outside

df_outside["DAY"] = df_outside.index.dayofyear

df_outside.plot("DAY", "Temperature", figsize=(20,10), lw=0.2)

df_mean = df_outside.resample("1D").mean()

df_mean

df_mean.plot("DAY", "Temperature", figsize=(20,10), lw=1)

fig, ax = plt.subplots(figsize=(16,8))
ax.plot("DAY", "TAVG", data=df, lw=0.3, label="NOAA")
ax.plot("DAY", "Temperature", data=df_mean, label="63-E", lw=2)
ax.legend()
ax.set(
    xlabel="Day of year",
    ylabel="Mean temperature",
)
sns.despine()

# So this shows the mean outside daily temperature in orange for 2018-20, superimposed on the NOAA data from 1977-2020.  The agreement is very good. 

df_mean.plot("DAY", "Humidity", figsize=(20,10), lw=1)



# From the paper https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=3551767 the relation between humidity, temperature and COVID-19 $R$ value is
# $$
# R = 3.968 − 0.0383 T − 0.0224 H
# $$
#

df_mean["R"] = 3.968 - 0.0383*df_mean["Temperature"] - 0.0224*df_mean["Humidity"]

df_mean.plot("DAY", "R", figsize=(20,10), lw=1)

# Fraction of population that needs to be immune in order to achieve herd immunity: $f = 1 - 1/R$

df_mean["f"] = 1.0 - 1.0/df_mean["R"]

df_mean.plot("DAY", "f", figsize=(20,10), lw=1, c="r")

# With social distancing, the reproduction number could be further reduced.  Try out 0, 20, 50% reductions

# +
fig, ax = plt.subplots(figsize=(16,8))

day = df_mean["DAY"]
R = df_mean["R"]
for reduction in 0, 20, 40, 60:
    f = 1.0 - 1.0/((1 - reduction/100)*R)
    ax.plot(day, f, label=f"Reduction: {reduction}%")
ax.legend()
ax.set(
    xlabel="Day of year",
    ylabel="Equilibrium infected fraction of population",
    ylim=[0, None],
)
sns.despine()
# -

# ### Conclusion

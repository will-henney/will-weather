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

df.plot(y=["TMIN", "TAVG", "TMAX"], use_index=True, figsize=(20,3), lw=0.2, alpha=0.8)

df.plot(y="PRCP", use_index=True, figsize=(20,2), lw=0.2, logy=True)

df.index.day

df["DAY"] = df.index.dayofyear

df.plot("DAY", "TAVG", "scatter", figsize=(20,10), alpha=0.2)

df.plot("DAY", "PRCP", figsize=(20,10), lw=0.2, logy=True)

df_outside = pd.read_csv("../netatmo_module.csv", sep=';', index_col=1, parse_dates=True)

df_outside.describe()

df_outside

df_outside["DAY"] = df_outside.index.dayofyear

df_outside.plot("DAY", "Temperature", "scatter", figsize=(20,10), lw=0.2, alpha=0.01)

df_mean = df_outside.resample("1D").mean()

df_mean

df_mean.plot("DAY", "Temperature", "scatter", figsize=(20,10), lw=1)

fig, ax = plt.subplots(figsize=(16,8))
ax.plot("DAY", "TAVG", ".", data=df, lw=0.2, color="b", alpha=0.2, label="NOAA 1980-2020")
ax.plot("DAY", "Temperature", "s", data=df_mean, label="63-E 2018-2020", lw=4, color="r", alpha=1.0)
ax.legend()
ax.set(
    xlabel="Day of year",
    ylabel="Mean temperature",
)
sns.despine()

# So this shows the mean outside daily temperature in orange for 2018-20, superimposed on the NOAA data from 1977-2020.  The agreement is very good. 

df_mean.plot("DAY", "Humidity", "scatter", figsize=(20,10), lw=1)



# From the paper https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=3551767 the relation between humidity, temperature and COVID-19 $R$ value is
# $$
# R = 3.968 − 0.0383 T − 0.0224 H
# $$
#

df_mean["R"] = 3.968 - 0.0383*df_mean["Temperature"] - 0.0224*df_mean["Humidity"]

df_mean.plot("DAY", "R", "scatter", figsize=(20,10), lw=1)

# Fraction of population that needs to be immune in order to achieve herd immunity: $f = 1 - 1/R$

df_mean["f"] = 1.0 - 1.0/df_mean["R"]

df_mean.plot("DAY", "f", "scatter", figsize=(20,10), lw=1, c="r")

# With social distancing, the reproduction number could be further reduced.  Try out 0, 20, 50% reductions

# +
fig, ax = plt.subplots(figsize=(16,8))

day = df_mean["DAY"]
R = df_mean["R"]
for reduction in 0, 20, 40, 60:
    f = 1.0 - 1.0/((1 - reduction/100)*R)
    ax.plot(day, 100*f, "o", label=f"Reduction: {reduction}%")
ax.legend()
ax.set(
    xlabel="Day of year",
    ylabel="Equilibrium infected percentage of population for herd immunity",
    ylim=[0, 100],
)
sns.despine()
# -

# ### Conclusion
#
# In the rainy season, with no additional measures, we need 40% of population infected (or vaccinated) in order for herd immunity to stop outbreaks.  This rises to 60% in dry season.  This assumes that people cannot be re-infected once they have caught the disease once 
#
# A 40% reduction in reproduction rate (from hygiene measures and social distancing) would be enough to reduce that to almost zero in rainy season.  And that would need to be a 60% reduction during the dry season.  Note that the reduction measures need to be permanent in order to be effective in the long term. 

# ### Update 2020-03-29
#
# There have been several more recent papers that suggest that it is the absolute humidity that matters.  For instance, [Qasim Bukhari and Yusuf Jameel. Will coronavirus pandemic diminish by summer? SSRN, March 2020.](https://ssrn.com/abstract=3556998)
#

# The absolute humidity follows from the Clausius–Clapeyron equation:
# $$
# \mathrm{AH} = 
# \frac{
# 13.247\, H \, e^{17.6 T / (T + 243.5)} 
# }{
# 273.15 + T
# } \ \mathrm{g\,m^{-3}} \ ,
# $$
# where $T$ is temperature in celsius and $H$ is relative humidity in per-cent.

import numpy as np

sns.set_context('poster')

T = df_mean["Temperature"]
df_mean["AH"] = 13.247*df_mean["Humidity"]*np.exp(17.6*T/(T + 243.5))/(273.15 + T)

fig, ax = plt.subplots(figsize=(16,6))
scat = ax.scatter("DAY", "AH", data=df_mean, c=df_mean.index.year, 
                  edgecolors="k", linewidths=0.5,
                  marker=".", vmin=2017.5, vmax=2020.5, cmap="viridis_r")
cb = fig.colorbar(scat, ax=ax, ticks=[2018, 2019, 2020], format="%d")
ax.axhspan(4.0, 10.0, color="r", alpha=0.1, zorder=-10)
for i, s in zip([0, 91, 182, 273], ["winter\nsolstice", "spring\nequinox", "summer\nsolstice", "autumn\nequinox"]): 
    # Try and hit equinoxes and solstices
    iday = (i - 10) % 365
    ax.axvline(iday, color="k", ls="--", zorder=-10, alpha=0.3, ymax=0.85)
    ax.text(iday, 18.0, s, ha="center")
ax.set(
    ylim=[0, 20],
    ylabel='Absolute humidity, g/m$^3$',
    xlabel='Day of year',
)
sns.despine()
fig.tight_layout()
fig.savefig("morelia-absolute-humidity-2018-to-2020.")



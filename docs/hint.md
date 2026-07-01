You find Sea-ice area data from CMIP6 models here and SIA data from observations here. With the latter data we have worked before, you can also use the data you used back then in .csv format.

In today's exercise, we will work with the historical (1850-2014) data from one of the CMIP6 models:

Download the data file for one of the models. In the following example, I use MPI-ESM1-2-LR, but you can use any model.
Load the NetCDF file into an xarray dataframe and print its contents to examine which simulations are contained in the file. We will focus on the data from the first ensemble member of the historical simulations, typically called modelname_hist_r1i1p1f1
You can use code such as the following to plot the modelled September sea-ice area, the sea-ice evolution after 2000, or the mean seasonal cycle for the period 2000 to 2010
file = 'MPI-ESM1-2-LR_nh_all_fv0.03.nc'
sia = xr.open_dataset(file)
septsia = sia["MPI_ESM1_2_LR_hist_r1i1p1f1"].where(sia["time_historical"].dt.month == 9, drop=True)
sia2000 = sia["MPI_ESM1_2_LR_hist_r1i1p1f1"].where(sia["time_historical"].dt.year >= 2000, drop=True)
sia2000_2010 = sia["MPI_ESM1_2_LR_hist_r1i1p1f1"].where((sia["time_historical"].dt.year >= 2000) & (sia["time_historical"].dt.year <= 2010), drop=True).groupby("time_historical.month").mean("time_historical")
septsia.plot()
plt.show()
sia2000.plot()
plt.show()
sia2000_2010.plot()
plt.show()
Based on this, you can now evaluate this first ensemble member of the historical record against the observational record that we examined some weeks ago. Choose three different metrics that you think could be useful, and examine how well this model does in reproducing these metrics. Repeat this exercise for 2 other models. Which of these three models is the best?

dirk.notz
11:17 AM
The two additional slides for the exercise

Exercise_notes.pdf
PDF884KB
June 16
System
4:46 PM
@amelielinha joined the channel.
June 17

dirk.notz
11:15 AM
Pick a climate model as described above and download its sea-ice area simulations
Estimate internal variability of one of the metrics you examined last week (for example September sea ice area) by calculating the standard deviation of September sea-ice area across all ensemble members of the model. Does the internal variability change over time?
Estimate internal variability of the same metric from calculating the standard deviation of the pre-industrial control simulation. How does this compare to the internal variability estimated in step 2?
Repeat the model evaluation from last week: Is the model further away from the observations than the internal variability?
June 24

dirk.notz
10:44 AM
Exercise for today:
Download 1° by 1° Climate model output
You find CMIP6 sea-ice concentration and thickness data interpolated to 1° by 1° grids here 
Download a sea-ice concentration field and a sea-ice thickness field 

Look at the data
Plot the sea-ice concentration for the Arctic using Panoply if you have it installed
Load the data into an xarray in python
Plot the sea-ice concentration for the Arctic using xarrays like we did for the observations
Calculate sea-ice area
Try to calculate northern-hemisphere sea-ice area
Play around with the data
Maybe also download temperature data for the atmosphere and look at the co-variability of sea-ice fields and temperature fields
Compare different models
Examine the seasonal cycle of sea-ice thickness in a specific grid cell, For the energy budget calculation, I suggest to set Tsurf to 0 C whenever it gets above 0 C, because sea ice cannot be warmer than 0 C. In summer, the outgoing longwave radiation is therefore given by sea ice with a surface temperature of 0 C. The energy budget is closed because the additional energy is used for melting at the sea-ice surface,  so you can calculate the energy for surface melting as the residual of the energy budget given in the exercise. We'll discuss this briefly next week. 


dirk.notz
12:51 PM
Here is my solution for 2.2, so you can use this as a starting point for 2.3:

import matplotlib.pyplot as plt
import numpy as np


def shortwave(day):
    return 314. * np.exp(-(day-164)**2/4608.)

def otherfluxes(day):
    return 118. * np.exp(-0.5 * (day-206.)**2 / (53**2)) + 179.

def albedo():
    alb_i       = 0.64   # bare ice albedo
    return alb_i

# First, set the array of 365 days and load the measured data
days  = np.arange(365)
Tsurf = np.zeros(365)

###
# First, define some parameters that might be changed to examine the 
# behaviour of the model
###
Kelvin      = 273.15       # Difference between Kelvin and C
Tbot        = -1.8+Kelvin  # Bottom temperature [K}
h_ice       = 0.5          # initial ice thickness [m]

###
# Second, set physical constants
###
k_ice       = 2.2          # heat conductivity of ice [W/(m K)]
eps_sigma   = 0.95*5.67e-8 # Constant in Boltzman-law

for day in days:
    # Set coefficients for polynomyal as described in exercise
    a = eps_sigma
    b = 0
    c = 0
    d = k_ice/h_ice
    e = - (1-albedo())*shortwave(day) - otherfluxes(day) - Tbot*k_ice/h_ice
  
    # Calculate surface temperature
    Ttemporary = np.roots([a,b,c,d,e])
    Tsurf[day] = max(Ttemporary[np.isreal(Ttemporary)] )

# plot surface temperature
plt.plot(Tsurf-Kelvin)
plt.axis([0, 365, -20, 20])
plt.xlabel('day')
plt.ylabel('Temperature')
plt.show()
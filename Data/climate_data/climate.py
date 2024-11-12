


import xarray as xr
import pandas as pd
import numpy as np

# Load the downloaded NetCDF file
ds = xr.open_dataset('/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/bc_climate_data.nc')

# Convert temperature and dewpoint from Kelvin to Celsius
ds['t2m'] = ds['t2m'] - 273.15
ds['d2m'] = ds['d2m'] - 273.15

# Calculate relative humidity using temperature and dewpoint
ds['humidity'] = 100 * (np.exp((17.625 * ds['d2m']) / (243.04 + ds['d2m'])) /
                        np.exp((17.625 * ds['t2m']) / (243.04 + ds['t2m'])))

# Calculate wind speed from U and V components
ds['wind_speed'] = (ds['u10']**2 + ds['v10']**2) ** 0.5

# Resample to daily averages
daily_avg = ds.resample(valid_time='1D').mean()

# Select and rename variables for the final dataset
df = daily_avg[['t2m', 'tp', 'wind_speed', 'humidity', 'ssrd', 'swvl1']].to_dataframe().reset_index()
df.columns = ['Date', 'Time', 'Latitude', 'Longitude', 'Temperature_C', 'Precipitation_mm', 'WindSpeed_m/s', 'Humidity_%', 'SolarRadiation_W/m2', 'SoilMoisture_m3/m3']

# Save to CSV
df.to_csv('daily_climate_data_bc.csv', index=False)

print("Daily climate data for British Columbia has been saved to 'daily_climate_data_bc.csv'")

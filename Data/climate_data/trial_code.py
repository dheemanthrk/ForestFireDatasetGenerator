import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Point

# Load climate data from NetCDF file
print("Loading climate data NetCDF file...")
ds = xr.open_dataset('/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/climate_data/bc_climate_data_2021_02.nc')

# Convert temperature and dewpoint from Kelvin to Celsius
ds['t2m'] = ds['t2m'] - 273.15
ds['d2m'] = ds['d2m'] - 273.15

# Calculate relative humidity using temperature and dewpoint
ds['humidity'] = 100 * (np.exp((17.625 * ds['d2m']) / (243.04 + ds['d2m'])) /
                        np.exp((17.625 * ds['t2m']) / (243.04 + ds['t2m'])))

# Calculate wind speed from U and V components
ds['wind_speed'] = (ds['u10']**2 + ds['v10']**2) ** 0.5

# Resample to daily averages using 'valid_time'
daily_avg = ds.resample(valid_time='1D').mean()

# Convert to DataFrame and rename columns
print("Converting climate data to DataFrame...")
climate_df = daily_avg[['t2m', 'tp', 'wind_speed', 'humidity', 'ssrd', 'swvl1']].to_dataframe().reset_index()

# Adjust column renaming based on actual column count
expected_columns = ['Date', 'Latitude', 'Longitude', 'Temperature_C', 'Precipitation_mm', 'WindSpeed_m/s', 'Humidity_%', 'SolarRadiation_W/m2', 'SoilMoisture_m3/m3']
if len(climate_df.columns) == len(expected_columns) + 1:
    climate_df.drop(columns=['number'], inplace=True, errors='ignore')

climate_df.columns = expected_columns[:len(climate_df.columns)]  # Adjust based on actual length

print("Climate data after renaming:")
print(climate_df.head())

# Load BC boundary shapefile and create 10x10 km grid
print("Loading BC boundary shapefile...")
bc_boundary = gpd.read_file("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp").to_crs("EPSG:3005")

# Generate 10 km x 10 km grid cells within BC boundary
minx, miny, maxx, maxy = bc_boundary.total_bounds
grid_size = 10000  # 10 km
grid_cells = [box(x, y, x + grid_size, y + grid_size)
              for x in np.arange(minx, maxx, grid_size)
              for y in np.arange(miny, maxy, grid_size)]
grid_gdf = gpd.GeoDataFrame(grid_cells, columns=["geometry"], crs="EPSG:3005")
grid_gdf = grid_gdf[grid_gdf.within(bc_boundary.unary_union)]
grid_gdf["grid_id"] = range(1, len(grid_gdf) + 1)

# Calculate centroids and convert them to latitude and longitude
grid_gdf["centroid"] = grid_gdf.centroid
grid_gdf = grid_gdf.set_geometry("centroid")
grid_gdf = grid_gdf.to_crs("EPSG:4326")
grid_gdf["latitude"] = grid_gdf.geometry.y
grid_gdf["longitude"] = grid_gdf.geometry.x
grid_gdf = grid_gdf.set_geometry("geometry")

# Reproject climate data to match the grid CRS and assign grid IDs via spatial join
print("Assigning grid IDs to climate data...")
climate_gdf = gpd.GeoDataFrame(climate_df, geometry=gpd.points_from_xy(climate_df.Longitude, climate_df.Latitude), crs="EPSG:4326")
climate_gdf = climate_gdf.to_crs(grid_gdf.crs)
climate_with_grid = gpd.sjoin(climate_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")

# Aggregate climate data by grid cell and date
print("Aggregating climate data by grid cell and date...")
climate_summary = climate_with_grid.groupby(['grid_id', 'Date']).agg(
    avg_temperature=('Temperature_C', 'mean'),
    total_precipitation=('Precipitation_mm', 'sum'),
    avg_wind_speed=('WindSpeed_m/s', 'mean'),
    avg_humidity=('Humidity_%', 'mean'),
    avg_solar_radiation=('SolarRadiation_W/m2', 'mean'),
    avg_soil_moisture=('SoilMoisture_m3/m3', 'mean')
).reset_index()

# Add latitude and longitude of grid cell centroids to the climate summary
climate_summary = climate_summary.merge(grid_gdf[['grid_id', 'latitude', 'longitude']], on="grid_id", how="left")

# Load fire history data
print("Loading fire history data...")
fire_data = pd.read_csv("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/cwfis/NFDB_point_txt/NFDB_point_20240613.txt", parse_dates=['REP_DATE'])
fire_gdf = gpd.GeoDataFrame(fire_data, geometry=gpd.points_from_xy(fire_data.LONGITUDE, fire_data.LATITUDE), crs="EPSG:4326")
fire_gdf = fire_gdf.to_crs(grid_gdf.crs)
fire_with_grid = gpd.sjoin(fire_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")

# Add a 'fire_occurred' flag and prepare for merging
fire_with_grid['fire_occurred'] = 1
fire_summary = fire_with_grid[['grid_id', 'REP_DATE', 'fire_occurred']].rename(columns={'REP_DATE': 'Date'})

# Merge climate and fire data by grid cell and date
print("Combining climate and fire data...")
combined_data = pd.merge(climate_summary, fire_summary, on=['grid_id', 'Date'], how='left')
combined_data['fire_occurred'] = combined_data['fire_occurred'].fillna(0).astype(int)

# Save combined data
output_path = 'combined_climate_fire_data_02.csv'
combined_data.to_csv(output_path, index=False)
print(f"Combined data saved to {output_path}")

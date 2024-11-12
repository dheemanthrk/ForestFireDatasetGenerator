import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Point

# Load and inspect the NetCDF file
print("Loading climate data NetCDF file...")
ds = xr.open_dataset('/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/bc_climate_data.nc')

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

# Convert to DataFrame for further processing, dropping the 'number' column if not needed
print("Converting to DataFrame...")
df = daily_avg[['t2m', 'tp', 'wind_speed', 'humidity', 'ssrd', 'swvl1']].to_dataframe().reset_index()
df = df.drop(columns=['number'], errors='ignore')  # Drop the 'number' column if present

# Renaming columns for clarity
df.columns = ['Date', 'Latitude', 'Longitude', 'Temperature_C', 'Precipitation_mm', 
              'WindSpeed_m/s', 'Humidity_%', 'SolarRadiation_W/m2', 'SoilMoisture_m3/m3']

print("Initial data preview after renaming:")
print(df.head())  # Display the first few rows to confirm data presence

# Check for empty DataFrame
if df.empty:
    print("Error: DataFrame is empty after conversion.")
else:
    print(f"Data loaded successfully with {len(df)} records.")

# Load BC boundary and create 10x10 km grid within it
print("Loading BC boundary shapefile...")
bc_boundary = gpd.read_file("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp").to_crs("EPSG:3005")
print("BC boundary loaded and reprojected.")

print("Generating 10 km x 10 km grid...")
minx, miny, maxx, maxy = bc_boundary.total_bounds
grid_size = 10000  # 10 km

# Generate the grid cells
grid_cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        grid_cells.append(box(x, y, x + grid_size, y + grid_size))
        y += grid_size
    x += grid_size

grid_gdf = gpd.GeoDataFrame(grid_cells, columns=["geometry"], crs="EPSG:3005")
grid_gdf = grid_gdf[grid_gdf.within(bc_boundary.unary_union)]
grid_gdf["grid_id"] = range(1, len(grid_gdf) + 1)
print("Grid created with total cells:", len(grid_gdf))

# Assign latitude and longitude to each grid cell's centroid
grid_gdf["latitude"] = grid_gdf.centroid.y
grid_gdf["longitude"] = grid_gdf.centroid.x

# Reproject climate data to match the grid CRS
print("Reprojecting climate data to match grid CRS...")
climate_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326")
climate_gdf = climate_gdf.to_crs(grid_gdf.crs)

# Spatial join between climate points and grid cells to assign grid IDs
print("Performing spatial join...")
climate_with_grid = gpd.sjoin(climate_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")
print("Spatial join completed. Sample data with grid IDs:")
print(climate_with_grid.head())

# Group by grid_id and Date, aggregating daily values
print("Aggregating data by grid cell and date...")
climate_summary = climate_with_grid.groupby(['grid_id', 'Date']).agg(
    avg_temperature=('Temperature_C', 'mean'),
    total_precipitation=('Precipitation_mm', 'sum'),
    avg_wind_speed=('WindSpeed_m/s', 'mean'),
    avg_humidity=('Humidity_%', 'mean'),
    avg_solar_radiation=('SolarRadiation_W/m2', 'mean'),
    avg_soil_moisture=('SoilMoisture_m3/m3', 'mean')
).reset_index()

# Merge centroid lat/lon to summary
climate_summary = climate_summary.merge(grid_gdf[['grid_id', 'latitude', 'longitude']], on="grid_id", how="left")

# Save to CSV
output_path = 'daily_climate_data_with_grid.csv'
climate_summary.to_csv(output_path, index=False)
print(f"Aggregated climate data saved to {output_path}")

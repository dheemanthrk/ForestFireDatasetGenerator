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

# Convert to DataFrame for further processing
print("Converting to DataFrame...")
df = daily_avg[['t2m', 'tp', 'wind_speed', 'humidity', 'ssrd', 'swvl1']].to_dataframe().reset_index()

# Drop 'number' column if it exists to avoid renaming issues
df = df.drop(columns=['number'], errors='ignore')  # Drop 'number' column if present

# Renaming columns
df.columns = ['Date', 'Latitude', 'Longitude', 'Temperature_C', 'Precipitation_mm', 
              'WindSpeed_m/s', 'Humidity_%', 'SolarRadiation_W/m2', 'SoilMoisture_m3/m3']

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

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

# Load fire history data and convert it to a GeoDataFrame
print("Loading fire history data...")
fire_data = pd.read_csv("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/cwfis/NFDB_point_txt/NFDB_point_20240613.txt")
fire_data['geometry'] = fire_data.apply(lambda row: Point(row['LONGITUDE'], row['LATITUDE']), axis=1)
fire_gdf = gpd.GeoDataFrame(fire_data, geometry='geometry', crs="EPSG:4326").to_crs("EPSG:3005")

# Convert fire data Date column to datetime format for consistency
fire_gdf['REP_DATE'] = pd.to_datetime(fire_gdf['REP_DATE'])

# Spatial join to assign grid IDs to fire points
fire_with_grid = gpd.sjoin(fire_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")
fire_with_grid = fire_with_grid[['grid_id', 'REP_DATE']]
fire_with_grid = fire_with_grid.rename(columns={'REP_DATE': 'Date'})
fire_with_grid['fire_occurred'] = 1  # Flag fire occurrences

# Merge fire occurrences with climate data, filling missing fire_occurred with 0
combined_data = climate_summary.merge(fire_with_grid, on=['grid_id', 'Date'], how='left')
combined_data['fire_occurred'] = combined_data['fire_occurred'].fillna(0).astype(int)

# Convert latitude and longitude to WGS84 for final output
combined_data_gdf = gpd.GeoDataFrame(combined_data, geometry=gpd.points_from_xy(combined_data.longitude, combined_data.latitude), crs="EPSG:3005")
combined_data_gdf = combined_data_gdf.to_crs("EPSG:4326")
combined_data_gdf['latitude'] = combined_data_gdf.geometry.y
combined_data_gdf['longitude'] = combined_data_gdf.geometry.x
combined_data_gdf = combined_data_gdf.drop(columns='geometry')

# Save to CSV
output_path = 'combined_climate_fire_data_with_grid.csv'
combined_data_gdf.to_csv(output_path, index=False)
print(f"Combined climate and fire data with grid saved to {output_path}")

import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box
import requests
import time

# Google Maps Elevation API Key
API_KEY = 'AIzaSyAOylG5Aqt_KYG2_wUH9oc2ed7Nh40kqzs'

# Function to get elevations for multiple points in a batch
def get_elevations_batch(coords):
    locations = "|".join([f"{lat},{lon}" for lat, lon in coords])
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={locations}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('results'):
        return [result['elevation'] for result in response.json()['results']]
    print("Error with Google Elevation API response:", response.json())
    return [None] * len(coords)

# Function to calculate slope and aspect for each grid cell
def calculate_slope_aspect(grid_df):
    grid_df['elevation'] = np.nan
    grid_df['slope'] = np.nan
    grid_df['aspect'] = np.nan

    coords = []
    index_map = {}

    # Prepare all required points (center and neighbors)
    for index, row in grid_df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        index_map[index] = [
            (lat, lon),         # Center
            (lat + 0.1, lon),   # North
            (lat - 0.1, lon),   # South
            (lat, lon + 0.1),   # East
            (lat, lon - 0.1)    # West
        ]
        coords.extend(index_map[index])

    # Process in batches of 512 (Google's batch limit)
    for i in range(0, len(coords), 512):
        batch_coords = coords[i:i + 512]
        elevations = get_elevations_batch(batch_coords)

        # Debug output to check if elevations were retrieved
        if not any(elevations):
            print("No elevations retrieved for batch starting with coords:", batch_coords[:5])

        # Map the elevations back to the grid cells and calculate slope/aspect
        for idx, (index, points) in enumerate(index_map.items()):
            if i + idx * 5 + 4 >= len(elevations): break  # Ensure batch limit

            # Retrieve elevation values for center and neighbors
            center_elev, north_elev, south_elev, east_elev, west_elev = elevations[idx*5:idx*5+5]
            if None in [center_elev, north_elev, south_elev, east_elev, west_elev]:
                print(f"Missing elevation data at grid index {index}. Skipping this point.")
                continue  # Skip if any elevation data is missing

            # Calculate slope
            dx = (east_elev - west_elev) / 2
            dy = (north_elev - south_elev) / 2
            slope = np.sqrt(dx**2 + dy**2) / 111139  # Approximate distance (degrees to meters)
            
            # Calculate aspect
            aspect = np.degrees(np.arctan2(dy, dx))
            if aspect < 0:
                aspect += 360
            
            # Assign values to the DataFrame
            grid_df.at[index, 'elevation'] = center_elev
            grid_df.at[index, 'slope'] = slope
            grid_df.at[index, 'aspect'] = aspect

        time.sleep(1)  # Avoid hitting rate limits
    return grid_df
# Load climate data from NetCDF file
print("Loading climate data NetCDF file...")
ds = xr.open_dataset('/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/climate_data/bc_climate_data_2023_08.nc')

ds['t2m'] = ds['t2m'] - 273.15
ds['d2m'] = ds['d2m'] - 273.15

ds['humidity'] = 100 * (np.exp((17.625 * ds['d2m']) / (243.04 + ds['d2m'])) /
                        np.exp((17.625 * ds['t2m']) / (243.04 + ds['t2m'])))

ds['wind_speed'] = (ds['u10']**2 + ds['v10']**2) ** 0.5
daily_avg = ds.resample(valid_time='1D').mean()

print("Converting climate data to DataFrame...")
climate_df = daily_avg[['t2m', 'tp', 'wind_speed', 'humidity', 'ssrd', 'swvl1']].to_dataframe().reset_index()

# Drop the 'number' column if it exists to avoid the length mismatch issue
if 'number' in climate_df.columns:
    climate_df = climate_df.drop(columns=['number'])

# Rename columns for clarity
climate_df.columns = ['Date', 'Latitude', 'Longitude', 'Temperature_C', 'Precipitation_mm', 
                      'WindSpeed_m/s', 'Humidity_%', 'SolarRadiation_W/m2', 'SoilMoisture_m3/m3']

print("Loading BC boundary shapefile...")
bc_boundary = gpd.read_file("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp").to_crs("EPSG:3005")
minx, miny, maxx, maxy = bc_boundary.total_bounds
grid_size = 10000
grid_cells = [box(x, y, x + grid_size, y + grid_size)
              for x in np.arange(minx, maxx, grid_size)
              for y in np.arange(miny, maxy, grid_size)]
grid_gdf = gpd.GeoDataFrame(grid_cells, columns=["geometry"], crs="EPSG:3005")
grid_gdf = grid_gdf[grid_gdf.within(bc_boundary.unary_union)]
grid_gdf["grid_id"] = range(1, len(grid_gdf) + 1)

grid_gdf["centroid"] = grid_gdf.centroid
grid_gdf = grid_gdf.set_geometry("centroid")
grid_gdf = grid_gdf.to_crs("EPSG:4326")
grid_gdf["latitude"] = grid_gdf.geometry.y
grid_gdf["longitude"] = grid_gdf.geometry.x
grid_gdf = grid_gdf.set_geometry("geometry")

print("Calculating elevation, slope, and aspect for each grid cell...")
grid_gdf = calculate_slope_aspect(grid_gdf)

print("Assigning grid IDs to climate data...")
climate_gdf = gpd.GeoDataFrame(climate_df, geometry=gpd.points_from_xy(climate_df.Longitude, climate_df.Latitude), crs="EPSG:4326")
climate_gdf = climate_gdf.to_crs(grid_gdf.crs)
climate_with_grid = gpd.sjoin(climate_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")

print("Aggregating climate data by grid cell and date...")
climate_summary = climate_with_grid.groupby(['grid_id', 'Date']).agg(
    avg_temperature=('Temperature_C', 'mean'),
    total_precipitation=('Precipitation_mm', 'sum'),
    avg_wind_speed=('WindSpeed_m/s', 'mean'),
    avg_humidity=('Humidity_%', 'mean'),
    avg_solar_radiation=('SolarRadiation_W/m2', 'mean'),
    avg_soil_moisture=('SoilMoisture_m3/m3', 'mean')
).reset_index()

climate_summary = climate_summary.merge(grid_gdf[['grid_id', 'latitude', 'longitude', 'elevation', 'slope', 'aspect']], on="grid_id", how="left")

print("Loading fire history data...")
fire_data = pd.read_csv("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/cwfis/NFDB_point_txt/NFDB_point_20240613.txt")
fire_data['REP_DATE'] = pd.to_datetime(fire_data['REP_DATE'], errors='coerce')
fire_gdf = gpd.GeoDataFrame(fire_data, geometry=gpd.points_from_xy(fire_data['LONGITUDE'], fire_data['LATITUDE']), crs="EPSG:4326")
fire_gdf = fire_gdf.to_crs(grid_gdf.crs)
fire_with_grid = gpd.sjoin(fire_gdf, grid_gdf[['grid_id', 'geometry']], how="inner", predicate="within")

fire_with_grid['fire_occurred'] = 1
fire_summary = fire_with_grid[['grid_id', 'REP_DATE', 'fire_occurred']].rename(columns={'REP_DATE': 'Date'})

print("Combining climate, fire, and topography data...")
combined_data = pd.merge(climate_summary, fire_summary, on=['grid_id', 'Date'], how='left')
combined_data['fire_occurred'] = combined_data['fire_occurred'].fillna(0).astype(int)

output_path = 'combined_climate_fire_data_with_topography.csv'
combined_data.to_csv(output_path, index=False)
print(f"Combined data with elevation, slope, and aspect saved to {output_path}")

import ee
import geemap
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from datetime import datetime, timedelta

# Initialize Earth Engine
ee.Initialize()

# Load and convert the BC boundary shapefile
print("Loading BC boundary shapefile...")
bc_boundary = gpd.read_file("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp")
bc_boundary = bc_boundary.to_crs("EPSG:4326")  # Convert to match Earth Engine's CRS
print("BC boundary loaded and converted.")

# Define the date range for NDVI data
start_date = '2022-01-01'
end_date = '2022-01-31'  # Change as needed for longer periods
scale = 10000  # 10 km grid size for NDVI sampling

# Initialize DataFrame to accumulate results
all_ndvi_data = pd.DataFrame()

# Function to tile the boundary into smaller areas (50 km by 50 km)
def create_tiles(bc_boundary, tile_size_km=50):
    minx, miny, maxx, maxy = bc_boundary.total_bounds
    tile_size = tile_size_km * 1000  # Convert to meters
    tiles = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            tile = box(x, y, x + tile_size, y + tile_size)
            tiles.append(tile)
            y += tile_size
        x += tile_size
    return gpd.GeoDataFrame(tiles, columns=["geometry"], crs="EPSG:4326")

# Create tiles
tiles_gdf = create_tiles(bc_boundary, tile_size_km=50)
tiles_gdf = gpd.overlay(tiles_gdf, bc_boundary, how="intersection")  # Clip tiles to BC boundary

# Divide the date range into weekly intervals
start_dt = datetime.strptime(start_date, '%Y-%m-%d')
end_dt = datetime.strptime(end_date, '%Y-%m-%d')

# Function to process NDVI data within a single tile and date range
def process_ndvi_for_tile(aoi, current_start_str, current_end_str):
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterDate(current_start_str, current_end_str) \
        .filterBounds(aoi) \
        .map(lambda image: image.normalizedDifference(['B8', 'B4']).rename('NDVI'))
    ndvi_image = collection.median()
    
    # Sample NDVI values across 10 km grid within the tile
    sample_points = ndvi_image.sample(region=aoi, scale=scale, projection='EPSG:4326', geometries=True)
    return sample_points.getInfo()

# Iterate over weekly date batches and each tile
current_start = start_dt
while current_start < end_dt:
    current_end = current_start + timedelta(days=6)
    if current_end > end_dt:
        current_end = end_dt

    # Format dates for Earth Engine
    current_start_str = current_start.strftime('%Y-%m-%d')
    current_end_str = current_end.strftime('%Y-%m-%d')
    print(f"Processing from {current_start_str} to {current_end_str}")

    for _, tile in tiles_gdf.iterrows():
        # Convert each tile geometry to an Earth Engine object
        aoi = ee.Geometry.Polygon(tile['geometry'].exterior.coords[:])
        
        try:
            sampled_ndvi = process_ndvi_for_tile(aoi, current_start_str, current_end_str)

            # Collect sampled NDVI data for this batch
            batch_data = []
            for feature in sampled_ndvi['features']:
                coord = feature['geometry']['coordinates']
                ndvi_value = feature['properties']['NDVI']
                batch_data.append({
                    'latitude': coord[1],
                    'longitude': coord[0],
                    'NDVI': ndvi_value,
                    'date': current_start_str
                })

            # Append to the main DataFrame
            all_ndvi_data = pd.concat([all_ndvi_data, pd.DataFrame(batch_data)], ignore_index=True)

        except ee.ee_exception.EEException as e:
            print(f"Error processing tile: {e}")
    
    current_start = current_end + timedelta(days=1)

# Save the final NDVI data to a CSV file
output_path = 'sampled_ndvi_data_with_10km.csv'
all_ndvi_data.to_csv(output_path, index=False)
print(f"Sampled NDVI data saved to {output_path}")

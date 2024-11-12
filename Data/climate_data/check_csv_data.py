import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the climate data CSV
df = pd.read_csv('/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/climate_data/daily_climate_data_with_grid.csv')

# Convert grid coordinates to geometry points in the EPSG:3005 projection
geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:3005")

# Reproject to EPSG:4326 to get latitude/longitude in degrees
gdf = gdf.to_crs("EPSG:4326")

# Update the latitude and longitude columns with the reprojected coordinates
gdf['latitude'] = gdf.geometry.y
gdf['longitude'] = gdf.geometry.x

# Drop the geometry column if no longer needed and save the updated CSV
gdf.drop(columns='geometry', inplace=True)
gdf.to_csv('daily_climate_data_bc_corrected.csv', index=False)

print("Latitude and longitude values converted to degrees and saved.")

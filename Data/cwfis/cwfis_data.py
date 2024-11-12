import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box

# Load the fire history data and check columns
print("Loading fire history data...")
file_path = "/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/cwfis/NFDB_point_txt/NFDB_point_20240613.txt"
fire_data = pd.read_csv(file_path, low_memory=False)  # Set low_memory to False to avoid dtype warning
print("Column names in the fire history data:", fire_data.columns)
print("First few rows of the fire history data:")
print(fire_data.head())

# Use the appropriate column names based on the dataset inspection
latitude_col = 'LATITUDE'
longitude_col = 'LONGITUDE'
date_col = 'REP_DATE'  # Assuming this is the relevant date column

# Convert the fire data to a GeoDataFrame
print("Converting fire history data to GeoDataFrame...")
fire_data['geometry'] = fire_data.apply(lambda row: Point(row[longitude_col], row[latitude_col]), axis=1)
fire_gdf = gpd.GeoDataFrame(fire_data, geometry='geometry', crs="EPSG:4326")
print("Fire history GeoDataFrame created.")
print(fire_gdf.head())

# Load the British Columbia boundary shapefile
print("Loading BC boundary shapefile...")
bc_boundary = gpd.read_file("/Users/dheemanth/Downloads/BCGW_7113060B_1730778599498_16464/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp")  # Replace with actual file path
bc_boundary = bc_boundary.to_crs("EPSG:3005")  # Using EPSG:3005 (BC Albers) for projection consistency
print("BC boundary shapefile loaded.")
print(bc_boundary.head())

# Generate a 10 km x 10 km grid within the bounding box of BC
print("Generating 10 km x 10 km grid...")
minx, miny, maxx, maxy = bc_boundary.total_bounds
grid_size = 10000  # 10 km in meters

# Create grid cells within the bounding box
grid_cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        cell = box(x, y, x + grid_size, y + grid_size)
        grid_cells.append(cell)
        y += grid_size
    x += grid_size

# Convert grid cells to a GeoDataFrame and clip to BC boundary
grid_gdf = gpd.GeoDataFrame(grid_cells, columns=["geometry"], crs="EPSG:3005")
grid_gdf = gpd.overlay(grid_gdf, bc_boundary, how="intersection")
grid_gdf["grid_id"] = range(1, len(grid_gdf) + 1)
print("Grid created with total cells:", len(grid_gdf))
print(grid_gdf.head())

# Reproject fire data to match grid CRS
print("Reprojecting fire history data to match grid CRS...")
fire_gdf = fire_gdf.to_crs(grid_gdf.crs)
print("Reprojection complete.")

# Perform spatial join to map fire history points to grid cells
print("Performing spatial join to map fire history points to grid cells...")
fire_with_grid = gpd.sjoin(fire_gdf, grid_gdf, how="inner", predicate="within")

# Filter relevant columns and rename them
fire_with_grid = fire_with_grid[['grid_id', date_col, latitude_col, longitude_col]]
fire_with_grid = fire_with_grid.rename(columns={latitude_col: 'latitude', longitude_col: 'longitude', date_col: 'date'})

# Set fire occurrence flag
fire_with_grid['fire_occurred'] = 1

# Check results
print("Fire history data with grid mapping:")
print(fire_with_grid.head())

# Save the results to CSV
output_path = "fire_history_with_grid.csv"
fire_with_grid.to_csv(output_path, index=False)
print(f"Fire history data with grid saved to {output_path}")

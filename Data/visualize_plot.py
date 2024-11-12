import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt

# Load the shapefile for British Columbia
bc_shapefile_path = '/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/ABMS_PROVINCE_SP/ABMS_PROV_polygon.shp'  # Update with your path
try:
    bc_gdf = gpd.read_file(bc_shapefile_path)
    print("Shapefile loaded successfully.")
except FileNotFoundError:
    print("Error: Shapefile not found. Check the file path.")
    exit()

# Get the bounding box coordinates of British Columbia
minx, miny, maxx, maxy = bc_gdf.total_bounds
print(f"Bounding box: {minx}, {miny}, {maxx}, {maxy}")

# Define grid size in meters for projected CRS (10 km grid cells)
grid_size = 10000  # 10 km

# Generate the grid cells within the bounding box
grid_cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        # Create a box for each grid cell
        cell = box(x, y, x + grid_size, y + grid_size)
        grid_cells.append(cell)
        y += grid_size
    x += grid_size

# Convert grid cells to a GeoDataFrame
grid_gdf = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=bc_gdf.crs)
print(f"Generated grid with {len(grid_gdf)} cells.")

# Clip the grid to the shape of British Columbia
grid_gdf = gpd.clip(grid_gdf, bc_gdf)
print(f"Grid clipped to British Columbia shape. Remaining cells: {len(grid_gdf)}")

# Plot the results
fig, ax = plt.subplots(figsize=(10, 10))
bc_gdf.plot(ax=ax, edgecolor='black', color='lightgrey', linewidth=0.5)  # Plot BC shape
grid_gdf.plot(ax=ax, edgecolor='blue', alpha=0.3, linewidth=0.2)  # Plot grid over BC shape

ax.set_title("10km x 10km Grid over British Columbia")
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

plt.show()

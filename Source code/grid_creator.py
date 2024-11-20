import geopandas as gpd
import numpy as np
from shapely.geometry import box
from pathlib import Path
import re

def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    return re.sub(r'[^\w\-_\.]', '_', name)

def create_grid(province_shapefile, grid_size, output_folder):
    """
    Creates a grid over a province, clips it to the province boundary,
    and adds latitude and longitude for grid centroids.

    Parameters:
    - province_shapefile (str): Path to the province shapefile.
    - grid_size (int): Size of the grid cell (in meters).
    - output_folder (Path): Directory to save the grid shapefile.

    Returns:
    - Path to the saved grid shapefile.
    """
    print(f"Loading province shapefile from {province_shapefile}...")
    province_gdf = gpd.read_file(province_shapefile)

    # Reproject to EPSG:3005 (BC Albers)
    print("Reprojecting province shapefile to EPSG:3005...")
    province_gdf = province_gdf.to_crs("EPSG:3005")

    # Generate grid
    print("Creating grid...")
    minx, miny, maxx, maxy = province_gdf.total_bounds
    x_coords = np.arange(minx, maxx, grid_size)
    y_coords = np.arange(miny, maxy, grid_size)
    grid_cells = [box(x, y, x + grid_size, y + grid_size) for x in x_coords for y in y_coords]
    grid_gdf = gpd.GeoDataFrame({"geometry": grid_cells}, crs="EPSG:3005")

    # Clip grid to province boundary
    print("Clipping grid to province boundary...")
    grid_gdf = gpd.overlay(grid_gdf, province_gdf, how="intersection")

    # Add grid_id column
    print("Adding grid_id column...")
    grid_gdf["grid_id"] = range(1, len(grid_gdf) + 1)

    # Reproject grid to EPSG:4326 for lat/lon
    print("Reprojecting grid to EPSG:4326...")
    grid_gdf = grid_gdf.to_crs("EPSG:4326")

    # Add latitude and longitude columns from centroids
    print("Adding latitude and longitude columns from centroids...")
    grid_gdf["latitude"] = grid_gdf.geometry.centroid.y
    grid_gdf["longitude"] = grid_gdf.geometry.centroid.x

    # Save grid to file
    province_name = province_gdf["PRNAME"].iloc[0]
    province_safe_name = sanitize_filename(province_name)
    output_file = Path(output_folder) / f"{province_safe_name}_grid.shp"
    print(f"Saving grid shapefile to {output_file}...")
    grid_gdf.to_file(output_file)

    print("Grid creation complete!")
    return str(output_file)

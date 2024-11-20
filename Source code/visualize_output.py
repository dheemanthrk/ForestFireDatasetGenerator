import geopandas as gpd

def validate_grid_coverage(nova_scotia_shapefile, grid_shapefile):
    """
    Validates if the generated grid fully covers the Nova Scotia shapefile.

    Parameters:
    - nova_scotia_shapefile (str): Path to the Nova Scotia shapefile.
    - grid_shapefile (str): Path to the grid shapefile.

    Returns:
    - None: Prints the validation result.
    """
    # Load Nova Scotia shapefile
    print(f"Loading Nova Scotia shapefile from {nova_scotia_shapefile}...")
    nova_scotia_gdf = gpd.read_file(nova_scotia_shapefile)
    if nova_scotia_gdf.empty:
        print("Error: Nova Scotia shapefile is empty or not loaded properly.")
        return

    # Load grid shapefile
    print(f"Loading grid shapefile from {grid_shapefile}...")
    grid_gdf = gpd.read_file(grid_shapefile)
    if grid_gdf.empty:
        print("Error: Grid shapefile is empty or not loaded properly.")
        return

    # Ensure CRS alignment
    if nova_scotia_gdf.crs != grid_gdf.crs:
        print("CRS mismatch detected. Reprojecting grid to match Nova Scotia CRS...")
        grid_gdf = grid_gdf.to_crs(nova_scotia_gdf.crs)

    # Validate spatial coverage using total bounds
    print("Calculating total bounds...")
    nova_scotia_bounds = nova_scotia_gdf.total_bounds  # [minx, miny, maxx, maxy]
    grid_bounds = grid_gdf.total_bounds  # [minx, miny, maxx, maxy]

    # Allow for minor floating-point discrepancies
    tolerance = 1e-6
    if (abs(nova_scotia_bounds[0] - grid_bounds[0]) <= tolerance and
        abs(nova_scotia_bounds[1] - grid_bounds[1]) <= tolerance and
        abs(nova_scotia_bounds[2] - grid_bounds[2]) <= tolerance and
        abs(nova_scotia_bounds[3] - grid_bounds[3]) <= tolerance):
        print("✅ The grid fully covers Nova Scotia.")
    else:
        print("❌ The grid does not fully cover Nova Scotia. Consider adjusting the grid size or alignment.")

    # Optional: Print the bounds for further analysis
    print("\nNova Scotia Bounds:", nova_scotia_bounds)
    print("Grid Bounds:", grid_bounds)

# Example Usage
if __name__ == "__main__":
    nova_scotia_shapefile = "/Users/dheemanth/Desktop/Project/Source code/project_data/shapefiles/Nova_Scotia_shapefile/nova_scotia_boundary.shp"
    grid_shapefile = "/Users/dheemanth/Desktop/Project/Source code/project_data/grids/Nova_Scotia___Nouvelle-Écosse_grid.shp"
    
    validate_grid_coverage(nova_scotia_shapefile, grid_shapefile)

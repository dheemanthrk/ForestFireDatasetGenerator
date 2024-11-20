import matplotlib.pyplot as plt
import geopandas as gpd
import os

def visualize_grid_and_boundary(province_shapefile, grid_shapefile):
    """
    Visualize the grid and the province boundary on a map.

    Parameters:
    - province_shapefile (str): Path to the province boundary shapefile.
    - grid_shapefile (str): Path to the grid shapefile.
    """
    # Load the province shapefile
    print(f"Loading province shapefile from {province_shapefile}...")
    province_gdf = gpd.read_file(province_shapefile)
    if province_gdf.empty:
        print(f"Error: The province shapefile '{province_shapefile}' is empty or not loaded properly.")
        return

    # Load the grid shapefile
    print(f"Loading grid shapefile from {grid_shapefile}...")
    grid_gdf = gpd.read_file(grid_shapefile)
    if grid_gdf.empty:
        print(f"Error: The grid shapefile '{grid_shapefile}' is empty or not loaded properly.")
        return

    # Check and match CRS
    if province_gdf.crs != grid_gdf.crs:
        print(f"CRS mismatch: Reprojecting grid to match province CRS.")
        grid_gdf = grid_gdf.to_crs(province_gdf.crs)

    # Plot the boundary and grid
    print("Visualizing the grid and boundary...")
    _, ax = plt.subplots(figsize=(10, 10))

    # Plot province boundary
    province_gdf.plot(ax=ax, edgecolor="blue", facecolor="none", linewidth=1, label="Province Boundary")

    # Plot grid
    grid_gdf.plot(ax=ax, edgecolor="green", facecolor="none", linewidth=0.5, label="Grid")

    # Add legend and titles
    ax.set_title("Grid and Province Boundary Visualization", fontsize=16)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Dynamically resolve paths relative to the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    province_shapefile = os.path.join(base_dir, "shapefiles", "British_Columbia_shapefile", "british_columbia_boundary.shp")
    grid_shapefile = os.path.join(base_dir, "grids", "british_columbia_boundary_grid", "province_grid.shp")
    
    visualize_grid_and_boundary(province_shapefile, grid_shapefile)

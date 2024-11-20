import geopandas as gpd
import rasterio
import pandas as pd
import numpy as np

def map_values_to_grid(grid_file, dem_file, slope_file, aspect_file, output_csv):
    grid_gdf = gpd.read_file(grid_file)

    with rasterio.open(dem_file) as dem_src, \
         rasterio.open(slope_file) as slope_src, \
         rasterio.open(aspect_file) as aspect_src:

        dem_data = dem_src.read(1)
        slope_data = slope_src.read(1)
        aspect_data = aspect_src.read(1)

        transform = dem_src.transform

        grid_gdf["elevation"] = np.nan
        grid_gdf["slope"] = np.nan
        grid_gdf["aspect"] = np.nan

        for index, row in grid_gdf.iterrows():
            x, y = row["geometry"].centroid.x, row["geometry"].centroid.y
            row_idx, col_idx = ~transform * (x, y)
            row_idx, col_idx = int(row_idx), int(col_idx)

            if 0 <= row_idx < dem_data.shape[0] and 0 <= col_idx < dem_data.shape[1]:
                grid_gdf.at[index, "elevation"] = dem_data[row_idx, col_idx]
                grid_gdf.at[index, "slope"] = slope_data[row_idx, col_idx]
                grid_gdf.at[index, "aspect"] = aspect_data[row_idx, col_idx]

    grid_gdf.to_csv(output_csv, index=False)
    print(f"Values mapped to grid and saved to '{output_csv}'.")

if __name__ == "__main__":
    grid_file = "project_data/grids/Nova_Scotia___Nouvelle-Écosse_grid.shp"
    dem_file = "project_data/dem_data.tif"
    slope_file = "project_data/slope.tif"
    aspect_file = "project_data/aspect.tif"
    output_csv = "project_data/output/grid_with_dem_data.csv"
    map_values_to_grid(grid_file, dem_file, slope_file, aspect_file, output_csv)

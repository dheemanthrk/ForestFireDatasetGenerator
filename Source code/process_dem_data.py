import rasterio
import numpy as np

def calculate_slope_aspect(dem_file, slope_file="project_data/slope.tif", aspect_file="project_data/aspect.tif"):
    with rasterio.open(dem_file) as src:
        elevation = src.read(1).astype(float)
        elevation[elevation == src.nodata] = np.nan
        
        transform = src.transform
        res_x, res_y = transform[0], -transform[4]

        x, y = np.gradient(elevation, res_x, res_y)

        slope = np.sqrt(x**2 + y**2)
        slope = np.arctan(slope) * (180 / np.pi)

        aspect = np.arctan2(-x, y) * (180 / np.pi)
        aspect[aspect < 0] += 360

        profile = src.profile
        profile.update(dtype=rasterio.float32, nodata=-9999)

        with rasterio.open(slope_file, "w", **profile) as dst:
            dst.write(slope.astype(rasterio.float32), 1)
        with rasterio.open(aspect_file, "w", **profile) as dst:
            dst.write(aspect.astype(rasterio.float32), 1)

    print(f"Slope saved to '{slope_file}', Aspect saved to '{aspect_file}'.")

if __name__ == "__main__":
    dem_file = "project_data/dem_data.tif"  # DEM file path
    calculate_slope_aspect(dem_file)

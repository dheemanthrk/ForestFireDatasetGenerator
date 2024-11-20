import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def process_climate_csv(grid_shapefile, climate_csv, output_csv):
    """
    Process climate data CSV and map it to grid cells.

    Parameters:
    - grid_shapefile (str): Path to the shapefile containing grid cells.
    - climate_csv (str): Path to the climate data CSV.
    - output_csv (str): Path to save the processed CSV file.
    """
    print(f"Loading grid shapefile from {grid_shapefile}...")
    grid_gdf = gpd.read_file(grid_shapefile)

    print(f"Loading climate data from {climate_csv}...")
    climate_df = pd.read_csv(climate_csv)

    # Ensure required columns exist
    required_columns = {"valid_time", "latitude", "longitude", "t2m", "tp", "u10", "v10", "d2m"}
    if not required_columns.issubset(climate_df.columns):
        missing_columns = required_columns - set(climate_df.columns)
        raise ValueError(f"Climate data is missing required columns: {missing_columns}")

    print("Converting temperature from Kelvin to Celsius...")
    climate_df["Temperature_C"] = climate_df["t2m"] - 273.15

    print("Calculating wind speed...")
    climate_df["WindSpeed_m/s"] = (climate_df["u10"]**2 + climate_df["v10"]**2)**0.5

    print("Calculating relative humidity...")
    climate_df["Humidity_%"] = 100 * (2.718**((17.625 * climate_df["d2m"]) / (243.04 + climate_df["d2m"])) /
                                      2.718**((17.625 * climate_df["t2m"]) / (243.04 + climate_df["t2m"])))

    print("Renaming precipitation column...")
    climate_df.rename(columns={"tp": "Precipitation_mm"}, inplace=True)

    print("Converting time column...")
    climate_df.rename(columns={"valid_time": "time"}, inplace=True)
    climate_df["time"] = pd.to_datetime(climate_df["time"])

    print("Converting climate data to GeoDataFrame...")
    climate_gdf = gpd.GeoDataFrame(
        climate_df,
        geometry=gpd.points_from_xy(climate_df["longitude"], climate_df["latitude"]),
        crs="EPSG:4326"
    )

    print("Mapping climate data to grid cells...")
    climate_with_grid = gpd.sjoin(climate_gdf, grid_gdf, how="inner", predicate="within")

    # Ensure latitude and longitude columns are retained
    climate_with_grid["latitude"] = climate_with_grid.geometry.y
    climate_with_grid["longitude"] = climate_with_grid.geometry.x

    print("Aggregating climate data by grid cells...")
    aggregated_data = climate_with_grid.groupby(["grid_id", "time"]).agg(
        avg_temperature=("Temperature_C", "mean"),
        total_precipitation=("Precipitation_mm", "sum"),
        avg_wind_speed=("WindSpeed_m/s", "mean"),
        avg_humidity=("Humidity_%", "mean"),
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean")
    ).reset_index()

    print(f"Saving processed climate data to {output_csv}...")
    aggregated_data.to_csv(output_csv, index=False)
    print("Processing complete!")

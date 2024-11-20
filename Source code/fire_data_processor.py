import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def process_fire_data(fire_file, grid_shapefile, climate_csv, output_csv):
    """
    Process fire history data, map it to grid cells, and integrate with climate data.

    Parameters:
    - fire_file (str): Path to the fire history data file (e.g., CSV or TXT).
    - grid_shapefile (str): Path to the shapefile containing grid cells.
    - climate_csv (str): Path to the processed climate data CSV.
    - output_csv (str): Path to save the combined data.
    """
    print(f"Loading fire history data from {fire_file}...")
    fire_df = pd.read_csv(fire_file, delimiter=",")  # Adjust delimiter as needed

    # Rename columns to match expected format
    column_mapping = {
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "REP_DATE": "fire_date",  # Using 'REP_DATE' as the fire occurrence date
        "SIZE_HA": "fire_size",
        "CAUSE": "fire_cause"
    }
    fire_df.rename(columns=column_mapping, inplace=True)

    # Ensure required columns
    required_columns = {"latitude", "longitude", "fire_date", "fire_size", "fire_cause"}
    if not required_columns.issubset(fire_df.columns):
        missing_columns = required_columns - set(fire_df.columns)
        raise ValueError(f"Fire data is missing required columns: {missing_columns}")

    print("Converting fire data to GeoDataFrame...")
    fire_gdf = gpd.GeoDataFrame(
        fire_df,
        geometry=gpd.points_from_xy(fire_df["longitude"], fire_df["latitude"]),
        crs="EPSG:4326"
    )

    print(f"Loading grid shapefile from {grid_shapefile}...")
    grid_gdf = gpd.read_file(grid_shapefile)

    print("Mapping fire data to grid cells...")
    fire_with_grid = gpd.sjoin(fire_gdf, grid_gdf, how="inner", predicate="within")

    print("Aggregating fire data by grid cells and dates...")
    fire_with_grid["fire_date"] = pd.to_datetime(fire_with_grid["fire_date"]).dt.date
    fire_summary = fire_with_grid.groupby(["grid_id", "fire_date"]).agg(
        fire_count=("geometry", "count"),  # Count the number of fires
        total_fire_size=("fire_size", "sum"),  # Sum fire sizes
        fire_cause=("fire_cause", lambda x: ', '.join(x.dropna().unique())),  # Concatenate unique causes
    ).reset_index()

    print(f"Loading processed climate data from {climate_csv}...")
    climate_df = pd.read_csv(climate_csv)

    print("Merging fire data with climate data...")
    climate_df["fire_date"] = pd.to_datetime(climate_df["time"]).dt.date  # Convert time to date for merging
    combined_data = pd.merge(climate_df, fire_summary, how="left", left_on=["grid_id", "fire_date"],
                             right_on=["grid_id", "fire_date"])

    # Fill NaN values for fire-related columns
    combined_data["fire_count"] = combined_data["fire_count"].fillna(0).astype(int)
    combined_data["total_fire_size"] = combined_data["total_fire_size"].fillna(0)
    combined_data["fire_cause"] = combined_data["fire_cause"].fillna("None")

    print(f"Saving combined data to {output_csv}...")
    combined_data.to_csv(output_csv, index=False)
    print("Fire data integration complete!")

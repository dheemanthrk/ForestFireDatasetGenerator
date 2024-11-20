# from pathlib import Path
# import os

# # Importing required functions from separate modules
# from province_shapefile_extractor import extract_province_shapefile
# from grid_creator import create_grid
# from climate_data_fetcher import fetch_climate_data
# from climate_data_processor import process_climate_data

# # Constants (Base paths)
# BASE_FOLDER = Path(__file__).resolve().parent / "project_data"  # Main folder to store all outputs
# SHAPEFILE_FOLDER = BASE_FOLDER / "shapefiles"
# LPR_SHAPEFILE_FOLDER = SHAPEFILE_FOLDER / "lpr_000a21a_e"
# GRID_FOLDER = BASE_FOLDER / "grids"
# CLIMATE_DATA_FOLDER = BASE_FOLDER / "climate_data"
# OUTPUT_FOLDER = BASE_FOLDER / "output"

# # Ensure directories exist
# for folder in [SHAPEFILE_FOLDER, GRID_FOLDER, CLIMATE_DATA_FOLDER, OUTPUT_FOLDER]:
#     folder.mkdir(parents=True, exist_ok=True)

# def main():
#     print("Starting the workflow...")

#     # Step 1: User inputs for province and dates
#     province_name = input("Enter the province name: ").strip()
#     year = int(input("Enter the year for climate data (e.g., 2023): "))
#     months = input("Enter months (comma-separated, e.g., 1,2,3 for Jan, Feb, Mar): ")
#     months = [int(m.strip()) for m in months.split(",")]

#     # Step 2: Extract province shapefile
#     print("\nExtracting province shapefile...")
#     province_shapefile = extract_province_shapefile(
#         province_name=province_name,
#         shapefile_folder=str(LPR_SHAPEFILE_FOLDER),
#         parent_output_folder=str(SHAPEFILE_FOLDER)
#     )

#     if "Error" in province_shapefile:
#         print(province_shapefile)
#         return
#     print(f"Extracted shapefile: {province_shapefile}")

#     # Step 3: Create grids for the province
#     print("\nCreating grids...")
#     grid_shapefile = create_grid(
#         province_shapefile=province_shapefile,
#         grid_size=10000,  # Grid size: 10km x 10km
#         output_folder=GRID_FOLDER
#     )
#     print(f"Grid created: {grid_shapefile}")

#     # Step 4: Fetch or skip climate data
#     print("\nChecking for existing climate data...")
#     for month in months:
#         climate_file = CLIMATE_DATA_FOLDER / f"climate_data_{year}_{month:02d}.nc"
#         if not climate_file.exists():
#             print(f"Fetching climate data for {year}-{month:02d}...")
#             fetch_climate_data(
#                 bounding_box=gpd.read_file(province_shapefile).total_bounds,
#                 year=year,
#                 months=[month],
#                 output_folder=CLIMATE_DATA_FOLDER
#             )
#         else:
#             print(f"Climate data for {year}-{month:02d} already exists. Skipping download.")
#     print(f"Climate data available in: {CLIMATE_DATA_FOLDER}")

#     # Step 5: Process climate data and map to grids
#     print("\nProcessing climate data and mapping to grids...")
#     processed_climate_data = process_climate_data(
#         grid_shapefile=grid_shapefile,
#         climate_files=list(CLIMATE_DATA_FOLDER.glob("*.nc")),  # Use all .nc files in the folder
#         output_csv=OUTPUT_FOLDER / f"{province_name.lower().replace(' ', '_')}_climate_data.csv"
#     )
#     print(f"Processed climate data saved to: {OUTPUT_FOLDER}")

#     print("\nWorkflow completed successfully!")

# if __name__ == "__main__":
#     main()
# from pathlib import Path
# from grid_creator import create_grid
# from climate_data_processor import process_climate_csv
# from fire_data_processor import process_fire_data

# # Paths
# BASE_FOLDER = Path(__file__).resolve().parent / "project_data"
# SHAPEFILE_FOLDER = BASE_FOLDER / "shapefiles"
# GRID_FOLDER = BASE_FOLDER / "grids"
# CLIMATE_DATA_FOLDER = BASE_FOLDER / "climate_data"
# FIRE_DATA_FOLDER = BASE_FOLDER / "fire_data"
# OUTPUT_FOLDER = BASE_FOLDER / "output"

# # Input Files
# PROVINCE_SHAPEFILE = SHAPEFILE_FOLDER / "Nova_Scotia_shapefile/nova_scotia_boundary.shp"
# CLIMATE_CSV_FILE = CLIMATE_DATA_FOLDER / "climate_data.csv"
# FIRE_FILE = FIRE_DATA_FOLDER / "NFDB_point_20240613.txt"  # Replace with actual fire history file

# # Output Files
# GRID_SHAPEFILE = GRID_FOLDER / "Nova_Scotia___Nouvelle-Écosse_grid.shp"
# PROCESSED_CLIMATE_CSV = OUTPUT_FOLDER / "Nova_Scotia_processed_climate_data.csv"
# COMBINED_CSV = OUTPUT_FOLDER / "Nova_Scotia_combined_data.csv"


# def main():
#     print("Starting the workflow...\n")

#     # Step 1: Create Grid
#     print("Creating grid for the province...")
#     create_grid(
#         province_shapefile=str(PROVINCE_SHAPEFILE),
#         grid_size=10000,  # Grid size: 10 km x 10 km
#         output_folder=str(GRID_FOLDER)
#     )
#     print(f"Grid created: {GRID_SHAPEFILE}\n")

#     # Step 2: Process Climate Data
#     print("Processing climate data and mapping it to grid cells...")
#     process_climate_csv(
#         grid_shapefile=str(GRID_SHAPEFILE),
#         climate_csv=str(CLIMATE_CSV_FILE),
#         output_csv=str(PROCESSED_CLIMATE_CSV)
#     )
#     print(f"Processed climate data saved to: {PROCESSED_CLIMATE_CSV}\n")

#     # Step 3: Process Fire History Data
#     print("Processing fire history data and integrating with climate data...")
#     process_fire_data(
#         fire_file=str(FIRE_FILE),
#         grid_shapefile=str(GRID_SHAPEFILE),
#         climate_csv=str(PROCESSED_CLIMATE_CSV),
#         output_csv=str(COMBINED_CSV)
#     )
#     print(f"Combined data saved to: {COMBINED_CSV}\n")

#     print("Workflow completed successfully!")


# if __name__ == "__main__":
#     main()
from pathlib import Path
from grid_creator import create_grid
from climate_data_processor import process_climate_csv
from fire_data_processor import process_fire_data
from fetch_dem_data import fetch_dem_data
from process_dem_data import calculate_slope_aspect
from map_slope_elevation_aspect import map_values_to_grid
import pandas as pd

# Base folders
BASE_FOLDER = Path(__file__).resolve().parent / "project_data"
SHAPEFILE_FOLDER = BASE_FOLDER / "shapefiles"
GRID_FOLDER = BASE_FOLDER / "grids"
CLIMATE_DATA_FOLDER = BASE_FOLDER / "climate_data"
FIRE_DATA_FOLDER = BASE_FOLDER / "fire_data"
DEM_DATA_FOLDER = BASE_FOLDER / "dem_data"
OUTPUT_FOLDER = BASE_FOLDER / "output"

# Input files
PROVINCE_SHAPEFILE = SHAPEFILE_FOLDER / "Nova_Scotia_shapefile/nova_scotia_boundary.shp"
CLIMATE_CSV_FILE = CLIMATE_DATA_FOLDER / "climate_data.csv"
FIRE_FILE = FIRE_DATA_FOLDER / "NFDB_point_20240613.txt"

# Output files
GRID_SHAPEFILE = GRID_FOLDER / "Nova_Scotia___Nouvelle-Écosse_grid.shp"
PROCESSED_CLIMATE_CSV = OUTPUT_FOLDER / "Nova_Scotia_processed_climate_data.csv"
DEM_FILE = DEM_DATA_FOLDER / "dem_data.tif"
SLOPE_FILE = DEM_DATA_FOLDER / "slope.tif"
ASPECT_FILE = DEM_DATA_FOLDER / "aspect.tif"
GRID_WITH_DEM_CSV = OUTPUT_FOLDER / "Nova_Scotia_grid_with_dem_data.csv"
COMBINED_CSV = OUTPUT_FOLDER / "Nova_Scotia_combined_data.csv"
FINAL_CSV = OUTPUT_FOLDER / "Nova_Scotia_final_combined_data.csv"

# Bounding box for Nova Scotia (adjust as needed)
NOVA_SCOTIA_BBOX = [-66.45, 43.26, -59.66, 47.24]  # (min_lon, min_lat, max_lon, max_lat)


def main():
    print("Starting the workflow...\n")

    # Step 1: Create Grid (if not already created)
    if not GRID_SHAPEFILE.exists():
        print("Creating grid for the province...")
        create_grid(
            province_shapefile=str(PROVINCE_SHAPEFILE),
            grid_size=10000,  # Grid size: 10 km x 10 km
            output_folder=str(GRID_FOLDER)
        )
        print(f"Grid created: {GRID_SHAPEFILE}\n")
    else:
        print(f"Grid already exists: {GRID_SHAPEFILE}\n")

    # Step 2: Process Climate Data
    if not PROCESSED_CLIMATE_CSV.exists():
        print("Processing climate data and mapping it to grid cells...")
        process_climate_csv(
            grid_shapefile=str(GRID_SHAPEFILE),
            climate_csv=str(CLIMATE_CSV_FILE),
            output_csv=str(PROCESSED_CLIMATE_CSV)
        )
        print(f"Processed climate data saved to: {PROCESSED_CLIMATE_CSV}\n")
    else:
        print(f"Processed climate data already exists: {PROCESSED_CLIMATE_CSV}\n")

    # Step 3: Fetch DEM Data
    if not DEM_FILE.exists():
        print("Fetching DEM data...")
        fetch_dem_data(bbox=NOVA_SCOTIA_BBOX, output_file=str(DEM_FILE))
        print(f"DEM data saved to: {DEM_FILE}\n")
    else:
        print(f"DEM data already exists: {DEM_FILE}\n")

    # Step 4: Process DEM Data (Calculate Slope and Aspect)
    if not (SLOPE_FILE.exists() and ASPECT_FILE.exists()):
        print("Processing DEM data...")
        calculate_slope_aspect(dem_file=str(DEM_FILE), slope_file=str(SLOPE_FILE), aspect_file=str(ASPECT_FILE))
        print(f"Slope and aspect data saved to: {SLOPE_FILE}, {ASPECT_FILE}\n")
    else:
        print(f"Slope and aspect data already exist: {SLOPE_FILE}, {ASPECT_FILE}\n")

    # Step 5: Map DEM Data to Grid
    if not GRID_WITH_DEM_CSV.exists():
        print("Mapping DEM, slope, and aspect data to grid cells...")
        map_values_to_grid(
            grid_file=str(GRID_SHAPEFILE),
            dem_file=str(DEM_FILE),
            slope_file=str(SLOPE_FILE),
            aspect_file=str(ASPECT_FILE),
            output_csv=str(GRID_WITH_DEM_CSV)
        )
        print(f"DEM data mapped to grid and saved to: {GRID_WITH_DEM_CSV}\n")
    else:
        print(f"Mapped DEM data already exists: {GRID_WITH_DEM_CSV}\n")

    # Step 6: Process Fire History Data
    if not COMBINED_CSV.exists():
        print("Processing fire history data and integrating with climate data...")
        process_fire_data(
            fire_file=str(FIRE_FILE),
            grid_shapefile=str(GRID_SHAPEFILE),
            climate_csv=str(PROCESSED_CLIMATE_CSV),
            output_csv=str(COMBINED_CSV)
        )
        print(f"Combined data saved to: {COMBINED_CSV}\n")
    else:
        print(f"Combined data already exists: {COMBINED_CSV}\n")

    # Step 7: Merge DEM Data with Combined Data
    if not FINAL_CSV.exists():
        print("Merging DEM data with combined data...")
        combined_df = pd.read_csv(COMBINED_CSV)
        dem_df = pd.read_csv(GRID_WITH_DEM_CSV)

        # Merge DEM data using grid_id
        final_df = combined_df.merge(
            dem_df[['grid_id', 'elevation', 'slope', 'aspect']], on='grid_id', how='left'
        )

        # Save the final combined CSV
        final_df.to_csv(FINAL_CSV, index=False)
        print(f"Final combined data saved to: {FINAL_CSV}\n")
    else:
        print(f"Final combined data already exists: {FINAL_CSV}\n")

    print("Workflow completed successfully!")


if __name__ == "__main__":
    main()

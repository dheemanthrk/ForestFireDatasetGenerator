import xarray as xr
import pandas as pd
from pathlib import Path

def convert_nc_to_csv(nc_file, output_csv):
    """
    Converts a NetCDF file to a CSV file.

    Parameters:
    - nc_file (str): Path to the NetCDF file.
    - output_csv (str): Path to save the converted CSV file.
    """
    print(f"Loading NetCDF file: {nc_file}...")
    try:
        ds = xr.open_dataset(nc_file)

        # Flatten the data into a DataFrame
        print("Converting NetCDF data to a DataFrame...")
        df = ds.to_dataframe().reset_index()

        # Save to CSV
        print(f"Saving DataFrame to CSV: {output_csv}...")
        df.to_csv(output_csv, index=False)
        print("Conversion complete!")
    except Exception as e:
        print(f"Error during conversion: {e}")

# Example usage
if __name__ == "__main__":
    # Path to your .nc file
    nc_file = "/Users/dheemanth/Desktop/Project/Source code/project_data/climate_data/climate_data_2023_01.nc"

    # Path to save the converted CSV
    output_csv = "/Users/dheemanth/Desktop/Project/Source code/project_data/climate_data/climate_data.csv"

    # Convert .nc to .csv
    convert_nc_to_csv(nc_file, output_csv)

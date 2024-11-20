import xarray as xr
import pandas as pd

def netcdf_to_csv(nc_file, output_csv):
    """
    Convert NetCDF file to CSV.
    
    Parameters:
    - nc_file (str): Path to the NetCDF file.
    - output_csv (str): Path to save the CSV file.
    """
    print(f"Converting NetCDF file {nc_file} to CSV...")
    ds = xr.open_dataset(nc_file)

    # Flatten the NetCDF data
    data = ds.to_dataframe().reset_index()

    # Save to CSV
    data.to_csv(output_csv, index=False)
    print(f"NetCDF data saved to {output_csv}.")

import cdsapi
import time

# Initialize CDS API client
c = cdsapi.Client()

# Function to retrieve data for a specific month with status updates
def download_monthly_data(year, month):
    month_str = f"{month:02d}"  # Format month as two digits
    filename = f'bc_climate_data_{year}_{month_str}.nc'  # Save each month separately
    
    # Submit the request and wait for it to finish
    print(f"Starting download for {year}-{month_str}...")
    result = c.retrieve(
        'reanalysis-era5-land',
        {
            'variable': [
                '2m_temperature', 'total_precipitation', '10m_u_component_of_wind', 
                '10m_v_component_of_wind', '2m_dewpoint_temperature', 
                'surface_solar_radiation_downwards', 'volumetric_soil_water_layer_1'
            ],
            'year': str(year),
            'month': month_str,
            'day': [f"{d:02d}" for d in range(1, 32)],  # All days in the month
            'time': [f"{h:02d}:00" for h in range(0, 24, 3)],  # 3-hour intervals
            'area': [59.5, -139.0, 48.3, -114.0],  # Bounding box for British Columbia
            'format': 'netcdf'
        }
    )
    result.download(filename)
    print(f"Data for {year}-{month_str} saved as '{filename}'")

# Download data for August 2023
download_monthly_data(2023, 8)
print("Data download for August 2023 complete.")

import cdsapi
import os
from pathlib import Path

def fetch_climate_data(bounding_box, year, months, output_folder):
    """
    Fetch climate data for the given bounding box, year, and months.

    Parameters:
    - bounding_box (list): [minx, miny, maxx, maxy] for the area.
    - year (int): Year for the climate data.
    - months (list): List of months (integers) to fetch.
    - output_folder (str): Folder to save the climate data.
    """
    c = cdsapi.Client()

    # Ensure output folder exists
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for month in months:
        filename = output_folder / f"climate_data_{year}_{month:02d}.nc"
        print(f"Fetching data for {year}-{month:02d}...")

        c.retrieve(
            'reanalysis-era5-land',
            {
                'variable': [
                    '2m_temperature', 'total_precipitation', '10m_u_component_of_wind',
                    '10m_v_component_of_wind', '2m_dewpoint_temperature',
                    'surface_solar_radiation_downwards', 'volumetric_soil_water_layer_1'
                ],
                'year': str(year),
                'month': f"{month:02d}",
                'day': [f"{d:02d}" for d in range(1, 32)],
                'time': [f"{h:02d}:00" for h in range(0, 24, 3)],
                'area': [
                    bounding_box[3], bounding_box[0],  # North, West
                    bounding_box[1], bounding_box[2]   # South, East
                ],
                'format': 'netcdf'
            },
            str(filename)
        )
        print(f"Saved: {filename}")


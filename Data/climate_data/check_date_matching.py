import pandas as pd

# Load fire history data
fire_data = pd.read_csv("/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/cwfis/NFDB_point_txt/NFDB_point_20240613.txt")

# Convert REP_DATE to datetime format
fire_data['REP_DATE'] = pd.to_datetime(fire_data['REP_DATE'], errors='coerce')

# Filter fire data for the date 2023-08-09
matching_fires = fire_data[fire_data['REP_DATE'] == '2023-08-09']

# Select and display relevant columns including latitude and longitude
print("Fires matching the date 2023-08-09 with latitude and longitude:")
print(matching_fires[['NFDBFIREID', 'REP_DATE', 'LATITUDE', 'LONGITUDE']])

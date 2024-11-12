import pandas as pd

# Load the combined climate and fire data
file_path = '/Users/dheemanth/Desktop/Project/ForestFireDatasetGenerator/App/Data/climate_data/combined_climate_fire_data_with_latlong.csv'
df = pd.read_csv(file_path)

# Check if any row has fire_occurred set to 1
if df['fire_occurred'].any():
    print("There are rows where fire_occurred is 1 (fire events recorded).")
    # Display a few rows where fire_occurred is 1
    print(df[df['fire_occurred'] == 1].head())
else:
    print("No rows have fire_occurred as 1. No fire events were recorded in this data.")

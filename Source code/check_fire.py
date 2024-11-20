import pandas as pd

def filter_fire_data(input_csv, output_csv):
    """
    Filters the CSV to only include rows where fire_count is not 0.

    Parameters:
    - input_csv (str): Path to the input CSV file.
    - output_csv (str): Path to save the filtered output CSV file.
    """
    print(f"Loading data from {input_csv}...")
    df = pd.read_csv(input_csv)

    print("Filtering rows where fire_count is not 0...")
    filtered_df = df[df['fire_count'] > 0]

    print(f"Saving filtered data to {output_csv}...")
    filtered_df.to_csv(output_csv, index=False)
    print("Filtering complete!")

# Example usage
input_csv = "/Users/dheemanth/Desktop/Project/Source code copy/project_data/output/Nova_Scotia_combined_data.csv"  # Replace with your actual file path
output_csv = "/Users/dheemanth/Desktop/Project/Source code copy/project_data/output/fire_check.csv"  # Replace with your desired output path
filter_fire_data(input_csv, output_csv)

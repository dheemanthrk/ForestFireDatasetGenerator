import pandas as pd
import matplotlib.pyplot as plt

# File path
FINAL_CSV = "/Users/dheemanth/Desktop/Project/Source code copy/project_data/output/Nova_Scotia_final_combined_data.csv"

# Load the data
print("Loading final CSV...")
df = pd.read_csv(FINAL_CSV)

# Check for missing values in slope, elevation, and aspect
df['missing_data'] = df[['elevation', 'slope', 'aspect']].isna().any(axis=1)

# Plot the data
plt.figure(figsize=(12, 8))

# Plot points with data
plt.scatter(
    df.loc[~df['missing_data'], 'longitude'],
    df.loc[~df['missing_data'], 'latitude'],
    c='green', label='Data Available', alpha=0.6, edgecolor='k', s=50
)

# Plot points without data
plt.scatter(
    df.loc[df['missing_data'], 'longitude'],
    df.loc[df['missing_data'], 'latitude'],
    c='red', label='Missing Data', alpha=0.6, edgecolor='k', s=50
)

# Add plot details
plt.title("Grid Cells with Slope, Elevation, and Aspect Data", fontsize=14)
plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)
plt.legend()
plt.grid(True)

# Save the plot
plt.savefig("/Users/dheemanth/Desktop/Project/Source code copy/project_data/output/grid_data_visualization.png")
plt.show()

print("Visualization saved as grid_data_visualization.png")

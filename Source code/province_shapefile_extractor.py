import os
import geopandas as gpd

def extract_province_shapefile(province_name, shapefile_folder="shapefiles/lpr_000a21a_e", parent_output_folder="shapefiles"):
    """
    Extracts the shapefile for a given province and saves it to a dedicated folder within the parent output folder.

    Parameters:
    - province_name (str): The name of the province to extract (e.g., "British Columbia").
    - shapefile_folder (str): The folder containing the source shapefile.
    - parent_output_folder (str): The parent folder where province-specific folders will be created.

    Returns:
    - str: The path to the saved shapefile or an error message if the province is not found.
    """
    # Construct paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shapefile_path = os.path.join(script_dir, shapefile_folder, "lpr_000a21a_e.shp")
    province_output_folder = os.path.join(script_dir, parent_output_folder, f"{province_name.replace(' ', '_')}_shapefile")
  
    # Ensure province-specific output directory exists
    os.makedirs(province_output_folder, exist_ok=True)

    # Load the shapefile
    print(f"Loading shapefile from {shapefile_path}...")
    gdf = gpd.read_file(shapefile_path)

    # Filter province by user input
    print(f"Filtering for province: {province_name}...")
    filtered_gdf = gdf[gdf["PRNAME"].str.contains(province_name, case=False, na=False)]

    if filtered_gdf.empty:
        return f"Error: Province '{province_name}' not found in the shapefile."

    # Reproject to EPSG:4326
    print("Reprojecting to EPSG:4326...")
    filtered_gdf = filtered_gdf.to_crs("EPSG:4326")

    # Save the filtered shapefile
    output_file = os.path.join(province_output_folder, f"{province_name.replace(' ', '_').lower()}_boundary.shp")
    print(f"Saving filtered shapefile to {output_file}...")
    filtered_gdf.to_file(output_file)

    return output_file

# Example Usage
if __name__ == "__main__":
    # User inputs province name
    user_input = input("Enter the name of the province/territory (e.g., 'British Columbia'): ").strip()
    
    # Call the function
    result = extract_province_shapefile(user_input)
    print(result)

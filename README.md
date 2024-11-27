# Forest Fire Prediction Dataset Generation and Analysis

## Overview
This project is aimed at creating a comprehensive, automated workflow for generating a geospatial dataset to predict forest fires. The workflow integrates data from multiple sources, processes and enriches it with derived features, addresses class imbalance, and produces a final dataset ready for machine learning applications.

---

## Data Sources and Features

### 1. **Climate Data (ERA5-Land via Copernicus)**
- **Variables Extracted:**
  - Temperature
  - Precipitation
  - Wind Speed
  - Humidity
- **Processing Steps:**
  - Interpolation for missing data (data available every 5 days).
  - Mapping variables to 10 km x 10 km grid cells.

### 2. **NDVI Data (Copernicus Sentinel-2)**
- **Variable Extracted:**
  - NDVI (Normalized Difference Vegetation Index)
- **Processing Steps:**
  - Fetch NDVI TIFF files for specified dates.
  - Map NDVI values to grid cells.

### 3. **Topographical Data (Copernicus DEM)**
- **Variable Extracted:**
  - Elevation
- **Features Calculated:**
  - Slope
  - Aspect
- **Processing Steps:**
  - Fetch DEM data.
  - Calculate slope and aspect using DEM values.
  - Map all topographical features to grid cells.

### 4. **Fire History Data (CWFIS)**
- **Variables Extracted:**
  - Fire Count
  - Fire Size
  - Fire Cause
- **Processing Steps:**
  - Map fire occurrences to grid cells.
  - Aggregate fire data by grid and date.

---

## Workflow Steps

### Step 1: Extracting Province Shapefile
- Extract shapefile for the target province from a national shapefile.
- Create a boundary shapefile in EPSG:4326.

### Step 2: Creating Grids
- Generate 10 km x 10 km grids for the extracted province shapefile.
- Compute centroids for each grid cell.

### Step 3: Fetching and Processing Climate Data
- Download climate data for the specified bounding box and date range.
- Convert NetCDF files to CSV and map climate data to grid cells.
- Interpolate missing data for seamless analysis.

### Step 4: Fetching and Processing NDVI Data
- Fetch NDVI TIFF files for the given date range using Sentinel-2 data.
- Map NDVI values to grid cells.

### Step 5: Fetching and Calculating Topographical Features
- Fetch DEM data for the region.
- Calculate slope and aspect from DEM.
- Map elevation, slope, and aspect to grid cells.

### Step 6: Integrating Fire History Data
- Process fire history data from CWFIS.
- Map fire occurrences to grid cells and aggregate by date.

### Step 7: Merging All Data
- Merge climate, NDVI, topographical, and fire data into a single dataset.
- Ensure alignment by grid ID and date.

### Step 8: Addressing Class Imbalance
- Handle class imbalance using techniques such as SMOTE, NearMiss, or hybrid methods.
- Ensure balanced datasets for machine learning applications.

---

## Final Dataset
- **Features Included:**
  - Climate Variables: Temperature, Precipitation, Wind Speed, Humidity
  - NDVI
  - Topographical Features: Elevation, Slope, Aspect
  - Fire Data: Fire Count, Fire Size, Fire Cause
- **Output Format:** CSV file with grid-level features aligned by date.

---

## Tools and Libraries
- **Data Processing:**
  - `geopandas` for shapefile manipulation.
  - `rasterio` for DEM and NDVI processing.
  - `xarray` and `pandas` for handling climate data.
  - `shapely` for geometry operations.
- **Data Fetching:**
  - Copernicus API for climate, NDVI, and DEM data.
  - CWFIS for fire history data.

---

## How to Run

### Prerequisites
1. Install required Python libraries:
   ```bash
   pip install geopandas rasterio pandas xarray shapely requests
   ```
2. Ensure Copernicus credentials are available in `credentials.json`.

### Steps
1. Clone the repository and navigate to the project directory.
2. Run the main script:
   ```bash
   python main.py
   ```
3. Provide input parameters such as date range and province.
4. Access the final dataset in the output folder.

---

## Future Enhancements
- Expand to include more features such as vegetation indices or anthropogenic factors.
- Implement advanced data balancing techniques.
- Automate deployment as a web app or Python library for wider usability.

---

## Contact
For questions or feedback, please reach out to [your email/contact information].

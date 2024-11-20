import requests
import json

def load_access_token():
    try:
        with open("project_data/access_token.json", "r") as f:
            data = json.load(f)
            return data["access_token"]
    except FileNotFoundError:
        print("Access token file not found. Please generate it first.")
        return None

def fetch_dem_data(bbox, output_file="dem_data.tif"):
    access_token = load_access_token()
    if not access_token:
        print("Access token is missing or invalid.")
        return False

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["DEM"],
        output: {
          id: "default",
          bands: 1,
          sampleType: SampleType.UINT16,
        }
      };
    }

    function evaluatePixel(sample) {
      return [sample.DEM];
    }
    """

    payload = {
        "input": {
            "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
                "bbox": bbox,
            },
            "data": [
                {
                    "type": "dem",
                    "dataFilter": {"demInstance": "COPERNICUS_30"},
                }
            ],
        },
        "output": {
            "width": 2500,
            "height": 2500,
            "responses": [
                {"identifier": "default", "format": {"type": "image/tiff"}},
            ],
        },
        "evalscript": evalscript,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"DEM data saved as '{output_file}'")
        return True
    else:
        print(f"Failed to fetch DEM data: {response.status_code} - {response.content}")
        return False

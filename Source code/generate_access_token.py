import requests
import json

def generate_access_token(username, password):
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    payload = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        with open("project_data/access_token.json", "w") as f:
            json.dump({"access_token": access_token}, f)
        print("Access Token generated and saved to 'project_data/access_token.json'.")
    else:
        print(f"Failed to generate access token. Error: {response.status_code}")
        print(response.json())

# Replace with your Copernicus login credentials
if __name__ == "__main__":
    username = "dh243394@dal.ca"
    password = "gRu3DKG.?7P$e/j"
    generate_access_token(username, password)

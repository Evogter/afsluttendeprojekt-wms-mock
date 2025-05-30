import requests
import json
from tabulate import tabulate

BASE_URL = "https://7c7d0cff-5448-4fb5-ab3c-d61af987163f.mock.pstmn.io/api/v1"

def login():
    url = f"{BASE_URL}/Auth/login"
    payload = {"username": "admin", "password": "ApiMock2025"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

def get_devices(token):
    url = f"{BASE_URL}/Devices/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch devices", "status_code": response.status_code}
    
def get_device(device_id, token):
        url = f"{BASE_URL}/Devices/{device_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch device", "status_code": response.status_code}
    
def get_updates():
    url = f"{BASE_URL}/Updates"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch updates", "status_code": response.status_code}
    
if __name__ == "__main__":
    token = login()
    
    print("Login:")
    print(token)

    print("\nAll Devices:")
    devices = get_devices(token)
    print(json.dumps(devices, indent=2))

    print("\nAll Devices (Tableview):")
    devices = get_devices(token)
 
    headers = ["ID", "Navn", "Status", "Firmware", "Seneste Check-in"]
    rows = [[d["id"], d["name"], d["status"], d["firmware"], d["lastCheckIn"]] for d in devices]

    print(tabulate(rows, headers=headers, tablefmt="grid"))

    print("\nUpdate Status:")
    updates = get_updates()
    print(json.dumps(devices, indent=2))
    
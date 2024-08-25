import requests
import msal
from dotenv import load_dotenv
import os

load_dotenv()

# Constants for authentication and API endpoints
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def get_access_token():
    """Authenticate and get an access token from Azure AD."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    token = app.acquire_token_for_client(SCOPE)

    if "access_token" in token:
        # print(token["access_token"])
        return token["access_token"]
    else:
        raise Exception("Failed to acquire access token.")


def get_devices(access_token):
    # Endpoint documentation: https://learn.microsoft.com/en-us/graph/api/device-get?view=graph-rest-1.0&tabs=http
    """Fetch all devices from Entra ID (Azure AD)."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    endpoint = f"{GRAPH_API_ENDPOINT}/devices"
    devices = []
    response = requests.get(endpoint, headers=headers)
    # print(response.status_code)
    if response.status_code == 200:
        devices = response.json().get("value", [])
    # print(devices)
    return devices


def get_intune_devices(access_token):
    # Endpoint documentation: https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list?view=graph-rest-1.0
    """Fetch all devices from Intune."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    endpoint = f"{GRAPH_API_ENDPOINT}/deviceManagement/managedDevices"
    devices = []
    response = requests.get(endpoint, headers=headers)
    # print(response.status_code)
    if response.status_code == 200:
        devices = response.json().get("value", [])
    # print(devices)
    return devices


def find_duplicates(devices):
    """Find duplicate devices based on the device name."""
    device_dict = {}
    for device in devices:
        name = device.get("displayName")
        if name in device_dict:
            device_dict[name].append(device)
        else:
            device_dict[name] = [device]

    duplicates = {name: devs for name, devs in device_dict.items() if len(devs) > 1}
    return duplicates


def delete_device(device_id, access_token):
    # Endpoint documentation: https://learn.microsoft.com/en-us/graph/api/device-delete?view=graph-rest-1.0&tabs=http
    """Delete a device by its ID."""
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = f"{GRAPH_API_ENDPOINT}/devices/{device_id}"
    response = requests.delete(endpoint, headers=headers)
    return response.status_code == 204


def cleanup_duplicates(duplicates, access_token):
    """Keep the most recent device and delete the duplicates."""
    deleted_count = 0
    for name, devices in duplicates.items():
        # Sort devices by last contacted date, descending
        devices.sort(
            key=lambda x: x.get("approximateLastSignInDateTime", ""), reverse=True
        )
        # Keep the first one and delete the rest
        for device in devices[1:]:
            if delete_device(device["id"], access_token):
                deleted_count += 1
    return deleted_count


if __name__ == "__main__":
    try:
        access_token = get_access_token()

        # Fetch devices from Entra ID
        ad_devices = get_devices(access_token)
        # print(ad_devices)

        # Fetch devices from Intune
        intune_devices = get_intune_devices(access_token)
        # print(intune_devices)

        # Combine both sets of devices
        all_devices = ad_devices + intune_devices
        # print(all_devices)

        # Find duplicates
        duplicates = find_duplicates(all_devices)

        # Clean up duplicates
        deleted_count = cleanup_duplicates(duplicates, access_token)

        print(f"Cleanup complete. {deleted_count} duplicate devices were deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")

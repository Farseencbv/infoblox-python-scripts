"""
This script downloads all networks from an Infoblox Grid Manager as a CSV file. 
It connects to the Grid Manager using the provided URL, username, and password, initiates a CSV export of all networks from the "On-Prem" network view, and downloads the resulting export file. 
The script then renames the csv file with a timestamp and saves it in the same directory as the script. 
Finally, the script triggers a call to indicate that the download is complete using the token received from the CSV export initiation request.

"""


import requests
import json
import time
import os

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Grid Variables
gm_url = "https://192.168.1.100/wapi/v2.7"
gm_user = "farseencbv"
gm_pwd = "infoblox"
now = time.strftime("%Y-%m-%d")
outputfile = f"Infoblox_Networks_{now}.csv"


def networks_export_csv():
    """Function to download all networks from Infoblox as CSV"""

    try:
        # Initiate a session to CSV Export of all Networks from On-Prem network view
        networks = {"_object": "network", "network_view": "On-Prem"}
        headers = {"content-type": "application/json"}
        response = requests.post(f"{gm_url}/fileop?_function=csv_export",
                                 verify=False, auth=(gm_user, gm_pwd),
                                 headers=headers, data=json.dumps(networks))

        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"CSV export initiation failed: {e}")
        return

    try:
        # Extract token and URL from the response
        d = response.json()
        token = d["token"]
        url = d["url"]

        # Download CSV  file using the URL
        headers = {"content-type": "application/force-download"}
        download_file = requests.get(url, verify=False, stream=True,
                                      auth=(gm_user, gm_pwd), headers=headers)
        download_file.raise_for_status()

        # Write CSV file to output file
        with open(outputfile, "wb") as file:
            file.write(download_file.content)

        print(f"The Network export has been downloaded as '{outputfile}'")
    except requests.exceptions.RequestException as e:
        print(f"CSV export failed: {e}")
        return

    try:
        # Post a call to trigger download complete using the received token
        headers = {"content-type": "application/json"}
        payload = dict(token=token)
        export_complete = requests.post(f"{gm_url}/fileop?_function=downloadcomplete",
                                         verify=False, auth=(gm_user, gm_pwd),
                                         headers=headers, data=json.dumps(payload))

        export_complete.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"CSV export didn't complete as expected: {e}")
        return


if __name__ == "__main__":
    networks_export_csv()

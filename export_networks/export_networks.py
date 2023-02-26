"""
This script downloads all networks from an Infoblox Grid Manager as a CSV file. 
It connects to the Grid Manager using the provided URL, username, and password, initiates a CSV export of all networks from the "On-Prem" network view, and downloads the resulting export file. 
The script then renames the csv file with a timestamp and saves it in the same directory as the script. 
Finally, the script triggers a call to indicate that the download is complete using the token received from the CSV export initiation request.

"""


import requests
import json
import time


# Disable SSL warnings
requests.packages.urllib3.disable_warnings()


# Grid Variables
gm_url = "https://1.1.1.1/wapi/v2.7"
gm_user = "fars"
gm_pwd = "infoblox"
now = time.strftime("%Y-%m-%d")
outputfile = f"Infoblox_Networks_{now}.csv"


# Setting up a session with the Infoblox GM
s = requests.Session()
s.auth = (gm_user, gm_pwd)
s.verify = False
headers = {"content-type": "application/json"}


def networks_export_csv():
    """Function to download all networks from Infoblox as CSV"""

    # Initiate a session to CSV Export of all Networks from On-Prem network view
    networks = {"_object": "network", "network_view": "On-Prem"}
    response = s.post(f"{gm_url}/fileop?_function=csv_export",headers=headers, data=json.dumps(networks))
    
    if not response.ok:
        raise requests.exceptions.RequestException(f"CSV export initiation failed with HTTP error code {response.status_code}")


    # Extract token and URL from the response
    d = response.json()
    token = d["token"]
    url = d["url"]


    # Download CSV  file using the URL
    headers_force = {"content-type": "application/force-download"}
    download_file = s.get(url, stream=True, headers=headers_force)
    
    if not download_file.ok:
        raise requests.exceptions.RequestException(f"CSV download failed with HTTP error code {download_file.status_code}")


    # Write CSV file to output file
    with open(outputfile, "wb") as file:
        file.write(download_file.content)

    print(f"The Network export has been downloaded as '{outputfile}'")


    # Post a call to trigger download complete using the received token
    payload = dict(token=token)
    export_complete = s.post(f"{gm_url}/fileop?_function=downloadcomplete",headers=headers, data=json.dumps(payload))
    
    if not export_complete.ok:
        raise requests.exceptions.RequestException(f"CSV export didn't complete as expected with HTTP error code {export_complete.status_code}")



if __name__ == "__main__":
    networks_export_csv()

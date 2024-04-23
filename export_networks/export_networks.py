#!/usr/bin/python3.8

"""
This script downloads all networks from an Infoblox Grid Manager as a CSV file. 
It connects to the Grid Manager using the provided URL, username, and password, initiates a CSV export of all networks from the "On-Prem" network view, and downloads the resulting export file. 
The script then renames the csv file with a timestamp and saves it in the same directory as the script. 

"""

import requests
import json
import time
import urllib3
import os
from dotenv import load_dotenv

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Grid Credentials
load_dotenv('/filepath/.env')
gm_user = os.getenv('INFOBLOX_USERNAME')
gm_pwd  = os.getenv('INFOBLOX_PASSWORD')

# Grid Variables
gm_url = "https://gridmaster/wapi/v2.12.2"
now = time.strftime('%Y-%m-%d')
outputfile = f'Infoblox_Networks_{now}.csv'

# Setting up a session with the Infoblox GM
s = requests.Session()
s.auth = (gm_user, gm_pwd)
s.verify = False
s.headers = {"content-type": "application/json"}

# Function to get Networks CSV export

def networks_export_csv():
    """
    Function to download all Networks from Infoblox from on prem view as csv
    Raises:
        requests.exceptions.RequestException: If any step (initiating export, downloading file, or completing export) fails.
    
    """

    # Step 1: Initiate CSV Export Session
    initial_url = f'{gm_url}/fileop?_function=csv_export'
    networks = {"_object": "network", "network_view":"On-Prem"}
    response = s.post(initial_url, data=json.dumps(networks))

    if not response.ok:
        raise requests.exceptions.RequestException(f'CSV export initiation failed with HTTP error code {response.status_code}')

    # Extract token and url from the response
    output = response.json()
    url = output['url']
    token = output['token']

    # Step 2: Download  CSV file using the url
    download_headers = {"content-type": "application/force-download"}
    download_file = s.get(url, headers=download_headers, stream=True)

    if not download_file.ok:
        raise requests.exceptions.RequestException(f'CSV file download failed with HTTP error code {download_file.status_code}')

    # Write exports to an output file
    with open (outputfile, 'wb') as file:
        file.write(download_file.content)

    print(f"The network exports has been downloaded as {outputfile}")

    # Step 4: Post a call to trigger download complete using the received token from the above steps
    final_url = f'{gm_url}/fileop?_function=downloadcomplete'
    export_token = {"token" : token}
    export_complete = s.post(final_url,data=json.dumps(export_token))

    if not export_complete.ok:
        raise requests.exceptions.RequestException(f"CSV export didn't complete as expected with HTTP error code {export_complete.status_code}")

if __name__ == '__main__':
    networks_export_csv()

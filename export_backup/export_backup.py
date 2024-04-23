#!/usr/bin/python3.8
"""
This script downloads an Infoblox database backup and saves it to the local file system. 
It connects to an Infoblox Grid Manager using the RESTfulAPI and authenticates using the provided credentials. 
The backup file is downloaded using the URL received from the response of initiating the backup session. 

"""

import time
import json
import requests
import urllib3
from dotenv import load_dotenv
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Grid Creds
load_dotenv('.env')
gm_user = os.getenv('INFOBLOX_USERNAME')
gm_pwd  = os.getenv('INFOBLOX_PASSWORD')


# Grid Variables
gm_url = "https://gridmaster/wapi/v2.12.2"
now = time.strftime('%Y-%m-%d_%I-%M_%p')
outputfile = f'FNF_Infoblox_Backup_{now}.bak'

# Setting up a session with the Infoblox GM
s = requests.Session()
s.auth = (gm_user, gm_pwd)
s.headers = {"content-type" : "application/json"}
s.verify = False

# Function to get Backup

def infoblox_backup():
    """
    Function to download Infoblox database backup 
    Raises:
        requests.exceptions.RequestException: If any step (initiating backup, downloading file, or completing backup) fails.
    
    """

    # Step 1: Initiate Grid Backup Session
    initial_url = f"{gm_url}/fileop?_function=getgriddata"
    backup = {'type': 'BACKUP', 'discovery_data': False}
    response = s.post(base_url, data=json.dumps(backup))

    if not response.ok:
        raise requests.exceptions.RequestException(f"Grid backup initiation failed with HTTP error code {response.status_code}")

    # Extract token and url from the response
    output = response.json()
    token = output['token']
    url =  output['url']

     # Step 2: Download backup file using the url
    download_headers = {"content-type": "application/force-download"}
    download_file = s.get(url, headers=download_headers, stream=True)

    if not download_file.ok:
        raise requests.exceptions.RequestException(f"Downloading backup file failed with HTTP error code {download_file.status_code}")

    # Write backup file to output file
    with open(outputfile, 'wb') as file:
        file.write(download_file.content)

    print(f"The backup has been downloaded as {outputfile}")

     # Step 4: Post a call to trigger download complete using the received token from the above steps
    final_url = f"{gm_url}/fileop?_function=downloadcomplete"
    backup_token = {"token": token}
    backup_complete = s.post(final_url, data=json.dumps(backup_token))
    
    if not backup_complete.ok:
        raise requests.exceptions.RequestException(f"Infoblox backup didn't complete as expected with HTTP error code {backup_complete.status_code}")



if __name__ == '__main__':
    infoblox_backup()
   

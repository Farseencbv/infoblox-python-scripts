#!/usr/bin/python3.8
"""
This scripts used to restore Infoblox Grid using an existing backupfile

"""

import requests
import urllib3
import os
import json
from dotenv import load_dotenv

# Disable SSl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Grid Creds
load_dotenv('/filepath/.env')
gm_user = os.getenv('INFOBLOX_USERNAME')
gm_pwd  = os.getenv('INFOBLOX_PASSWORD')


# Grid Variables
gm_url = 'https://gridmaster/wapi/v2.12.2'
upload_file_name = 'database.bak'

# Setting up a session with the Infoblox GM
s = requests.Session()
s.auth = (gm_user, gm_pwd)
s.verify = False
s.headers = {"content-type" : "application/json"}

# Function to Restore the lab 

def infoblox_restore():
    """
    Function to restore infoblox database backup
    Raises:
        requests.exceptions.RequestException: If any step fails.

    """

    # STEP 1 - Initiate Grid restore Session
    response = s.post(f"{gm_url}/fileop?_function=uploadinit")

    if not response.ok:
        raise requests.exceptions.RequestException(f"Grid restore Initiation is failed with HTTP error code {response.status_code}")
    
    #  STEP 2 Extract token and URL from the response
    output = response.json()
    token = output["token"]
    url = output["url"]
    
    # STEP 3 - upload backup file using the url
    with open(upload_file_name, "rb") as f:
        files = {"file": f}
        auth  = (gm_user,gm_pwd)
        upload_backup = requests.post(url, files=files, auth=auth, verify=False, stream=True) # no headers for this request 
    
    # STEP 4 - Restore the grid
    restore_url = f'{gm_url}/fileop?_function=restoredatabase'
    payload = {"token": token, "mode" : "FORCED", "keep_grid_ip" : True, "discovery_data": False}
    restore_grid = s.post(restore_url, data=json.dumps(payload))
    
    if not restore_grid.ok:
        raise requests.exceptions.RequestException(f"Infoblox Restore didn't complete as expected with HTTP error code {restore_grid.status_code}")
    
    else:
     print("Restore completed!")



    

if __name__ == '__main__':
    infoblox_restore()

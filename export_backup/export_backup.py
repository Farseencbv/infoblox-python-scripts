"""

This script downloads an Infoblox database backup and saves it to the local file system. 
It connects to an Infoblox Grid Manager using the RESTfulAPI and authenticates using the provided credentials. 
The backup file is downloaded using the URL received from the response of initiating the backup session. 
The file is then saved locally with a timestamped filename. 
Finally, a POST request is sent to trigger download complete using the received token.

"""

import requests
import json
import time


requests.packages.urllib3.disable_warnings()

# Grid variables
gm_url = "https://192.168.1.100/wapi/v2.7"
gm_user = 'farseencbv'
gm_pwd = 'infoblox'
now = time.strftime('%Y-%m-%d')
outputfile = f'infoblox_backup_{now}.bak'

def infoblox_backup():
    """Function to download Infoblox database backup"""
    try:
        # Step 1: Initiate Grid Backup Session
        backup = {"type": "BACKUP"}
        headers = {"content-type": "application/json"}
        response = requests.post(f'{gm_url}/fileop?_function=getgriddata', verify=False, auth=(gm_user, gm_pwd), headers=headers, data=json.dumps(backup))
        response.raise_for_status()
        d = response.json()
        token = d['token']
        url = d['url']

        # Step 2: Download backup file using the url
        headers = {"content-type": "application/force-download"}
        download_file = requests.get(url, auth=(gm_user, gm_pwd), verify=False, stream=True, headers=headers)
        download_file.raise_for_status()

        # Write backup file to output file
        with open(outputfile, 'wb') as file:
            file.write(download_file.content)

        print(f"The backup has been downloaded as '{outputfile}'")

        # Step 4: Post a call to trigger download complete using the received token from the above steps
        headers = {"content-type": "application/json"}
        payload = dict(token=token)
        backup_complete = requests.post(f'{gm_url}/fileop?_function=downloadcomplete', auth=(gm_user, gm_pwd), verify=False, headers=headers, data=json.dumps(payload))
        backup_complete.raise_for_status()
        print("Backup completed!")
    except Exception as e:
        print(f"Backup failed due to error: {e}")

if __name__ == '__main__':
    infoblox_backup()

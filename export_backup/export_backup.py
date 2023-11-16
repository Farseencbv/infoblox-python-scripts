"""
This script downloads an Infoblox database backup and saves it to the local file system. 
It connects to an Infoblox Grid Manager using the RESTfulAPI and authenticates using the provided credentials. 
The backup file is downloaded using the URL received from the response of initiating the backup session. 
The file is then saved locally with a timestamped filename. 
Finally, a POST request is sent to trigger the download complete using the received token.

"""


import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Grid variables
gm_url = "https://1.1.1.1/wapi/v2.12.2"
gm_user = 'fars'
gm_pwd = 'infoblox'
now = time.strftime('%Y-%m-%d')
outputfile = f'infoblox_backup_{now}.bak'


# Setting up a session with the Infoblox GM
s = requests.Session()
s.auth = (gm_user, gm_pwd)
s.headers = {"content-type": "application/json"}
s.verify = False

def infoblox_backup():
    """Function to download Infoblox database backup"""


    # Step 1: Initiate Grid Backup Session
    backup = {"type": "BACKUP"}
    response = s.post(f'{gm_url}/fileop?_function=getgriddata', data=json.dumps(backup))
    
    if not response.ok:
        raise Exception(f"Grid backup initiation failed with HTTP error code {response.status_code}")
    
    response_data = response.json()
    token = response_data['token']
    url = response_data['url']


    # Step 2: Download backup file using the url
    download_headers = {"content-type": "application/force-download"}
    download_file = s.get(url, stream=True, headers=download_headers)
    
    if not download_file.ok:
        raise Exception(f"Downloading backup file failed with HTTP error code {download_file.status_code}")

    # Write backup file to output file
    with open(outputfile, 'wb') as file:
        file.write(download_file.content)

    print(f"The backup has been downloaded as '{outputfile}'")


    # Step 4: Post a call to trigger download complete using the received token from the above steps
    backup_token = {"token": token}
    backup_complete = s.post(f'{gm_url}/fileop?_function=downloadcomplete', data=json.dumps(backup_token))
    
    if not backup_complete.ok:
        raise Exception(f"Download token deletion failed with HTTP error code {backup_complete.status_code}")
    


if __name__ == '__main__':
    infoblox_backup()

    

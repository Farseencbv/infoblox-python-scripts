import requests
import json
import time


requests.packages.urllib3.disable_warnings()

# Grid variables
gm_url = "https://1.1.1.1/wapi/v2.7"
gm_user = 'fars'
gm_pwd = 'infoblox'
now = time.strftime('%Y-%m-%d')
outputfile = f'infoblox_backup_{now}.bak'


def infoblox_backup():
    """Function to download Infoblox database backup"""


    # Step 1: Initiate Grid Backup Session
    backup = {"type": "BACKUP"}
    headers = {"content-type": "application/json"}
    response = requests.post(f'{gm_url}/fileop?_function=getgriddata', verify=False, auth=(gm_user, gm_pwd), headers=headers, data=json.dumps(backup))
    
    if not response.ok:
        raise Exception(f"Grid backup initiation failed with HTTP error code {response.status_code}")
    
    d = response.json()
    token = d['token']
    url = d['url']


    # Step 2: Download backup file using the url
    headers = {"content-type": "application/force-download"}
    download_file = requests.get(url, auth=(gm_user, gm_pwd), verify=False, stream=True, headers=headers)
    
    if not download_file.ok:
        raise Exception(f"Downloading backup file failed with HTTP error code {download_file.status_code}")

    # Write backup file to output file
    with open(outputfile, 'wb') as file:
        file.write(download_file.content)

    print(f"The backup has been downloaded as '{outputfile}'")


    # Step 4: Post a call to trigger download complete using the received token from the above steps
    headers = {"content-type": "application/json"}
    payload = dict(token=token)
    backup_complete = requests.post(f'{gm_url}/fileop?_function=downloadcomplete', auth=(gm_user, gm_pwd), verify=False, headers=headers, data=json.dumps(payload))
    
    if not backup_complete.ok:
        raise Exception(f"Triggering download complete failed with HTTP error code {backup_complete.status_code}")
    print("Backup completed!")


if __name__ == '__main__':
    infoblox_backup()

    

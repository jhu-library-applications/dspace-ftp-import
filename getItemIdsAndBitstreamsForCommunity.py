import json
import requests
import secrets
import time
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

handle = input('Enter handle: ')

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')

endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityName = community['name'].replace(' ', '')
communityID = community['uuid']

itemList = []

collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
for j in range(0, len(collections)):
    collectionID = collections[j]['uuid']
    print(collectionID)
    if collectionID not in skippedCollections:
        offset = 0
        items = ''
        while items != []:
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
            items = items.json()
            for k in range(0, len(items)):
                itemID = items[k]['uuid']
                itemID = '/rest/items/'+itemID
                itemList.append(itemID)
            offset = offset + 200
            print(offset)

handle = handle.replace('/', '-')
f = csv.writer(open(filePath+handle+'handlesAndBitstreams.csv', 'w', encoding='utf-8'))
f.writerow(['itemID']+['bitstream']+['title'])

len(itemList)
for itemID in itemList:
    metadata = requests.get(baseURL+itemID+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    title = ''
    for i in range(0, len(metadata)):
        if metadata[i]['key'] == 'dc.title':
            title = metadata[i]['value']

    bitstreams = requests.get(baseURL+itemID+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies, verify=verify).json()
    print(len(bitstreams))
    for bitstream in bitstreams:
        fileName = bitstream['name']
        f.writerow([itemID]+[fileName]+[title])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))

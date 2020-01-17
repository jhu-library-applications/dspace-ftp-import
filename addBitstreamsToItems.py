 import json
import requests
import secrets
from datetime import datetime
import time
import csv
import urllib3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='collectionHandle of the collection to retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

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

f = csv.writer(open('ingestedBitstreams'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))

with open(filename) as bitstreamsCSV:
    bitstreamsCSV = csv.DictReader(bitstreamsCSV)
    for row in bitstreamsCSV:
        fileName = row['newfile']
        itemID = row['itemID']
        bitstream = row['localFileLocation']
        data = open(bitstream, 'rb')

        bitstreams = requests.get(baseURL+itemID+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies, verify=verify).json()
        initialBitstreams = len(bitstreams)
        print('{} initial bitstreams'.format(initialBitstreams))

        post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerFileUpload, cookies=cookies, verify=verify, data=data).json()
        print(post)
        link = post['link']
        print('Added {} for item'.format(link))

        bitstreams = requests.get(baseURL+itemID+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies, verify=verify).json()
        totalBitstreams = len(bitstreams)
        addedBitstreams = totalBitstreams - initialBitstreams
        print('{} total bitstreams, {} added'.format(totalBitstreams, addedBitstreams))

        # Create provenance notes
        itemMetadataProcessed = []
        metadata = requests.get(baseURL+str(itemID)+'/metadata?&limit=500', headers=header, cookies=cookies, verify=verify).json()

        for l in range(0, len(metadata)):
            metadata[l].pop('schema', None)
            metadata[l].pop('element', None)
            metadata[l].pop('qualifier', None)
            itemMetadataProcessed.append(metadata[l])

        bitstream = requests.get(baseURL+link, headers=header, cookies=cookies, verify=verify).json()
        uploadedFileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream['checkSum']['checkSumAlgorithm']
        if uploadedFileName == fileName:
            provNote = {}
            provNote['key'] = 'dc.description.provenance'
            provNote['language'] = 'en_US'
            utc = datetime.utcnow()
            utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
            provNoteValue = 'Bitstream '+uploadedFileName+' added by '+userFullName+' ('+email+') on '+utcTime+' (GMT). '+size+' bytes, checkSum: '+checksum+' ('+algorithm+')'
            provNote['value'] = provNoteValue
            itemMetadataProcessed.append(provNote)
            itemMetadataProcessed = json.dumps(itemMetadataProcessed)
            print('updated metadata for', itemID)
            delete = requests.delete(baseURL+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
            print(delete)
            post = requests.put(baseURL+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
            print(post)
            f.writerow([itemID]+[link]+[uploadedFileName]+[delete]+[post])
            print('')
        else:
            pass

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))

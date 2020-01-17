from ftplib import FTP
import csv
import argparse
import os
import time
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-i', '--importation', help='Do you need to import the files? Enter yes to import.')
parser.add_argument('-d', '--directory')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.importation:
    importation = args.importation
else:
    importation = input('Do you need to import the files? Enter yes to import.')
if args.directory:
    directory = args.directory
else:
    directory = input("Enter the local directory that is currently storing or will store the files.Format like '(C:/Test/):'")

startTime = time.time()

ftp = FTP()

f = csv.writer(open('FTPlisting'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w', encoding='utf-8'))
f.writerow(['file']+['filematch'])

f2 = csv.writer(open('filematching'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w', encoding='utf-8'))
f2.writerow(['newfile']+['localFileLocation']+['itemID']+['matchingfile']+['title'])

# Complete server details below.
server = 'serverName'
port = 21
ftp.connect(server, port)
username = 'username'
password = 'password'
ftp.login(username, password)
ftp.cwd('folderName')

fileCount = 0

dirlist = ftp.nlst()
for file in dirlist:
    file = file.strip()
    filematch = file[:-8]
    filematch = filematch.replace('-', '_').replace(' ', '_')
    f.writerow([file]+[filematch])
    if importation == 'yes':
        local_filename = os.path.join(directory, file)
        lf = open(local_filename, 'wb')
        ftp.retrbinary("RETR "+file, lf.write)
    else:
        local_filename = directory+file
    with open(filename) as otherMetadata:
        otherMetadata = csv.DictReader(otherMetadata)
        for row in otherMetadata:
            other_identifier = row['bitstream'].strip()
            filematch2 = other_identifier[:-4]
            filematch2 = filematch2.replace('-', '_').replace('&', '_').replace(' ', '_')
            title = row['title']
            itemID = row['itemID']
            if filematch == filematch2:
                f2.writerow([file]+[local_filename]+[itemID]+[other_identifier]+[title])
                print("found: "+file)
                fileCount = fileCount + 1
                print('{} files matched'.format(fileCount))
                break
        else:
            f2.writerow([file]+[local_filename]+['no matching file found'])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))

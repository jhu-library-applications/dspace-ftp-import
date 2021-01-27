import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

f = csv.writer(open('newfilematching.csv', 'w'))
f.writerow(['newfile']+['itemID']+['localFileLocation'])

with open(filename) as bitstreamsCSV:
    bitstreamsCSV = csv.DictReader(bitstreamsCSV)
    for row in bitstreamsCSV:
        fileName = row['newfile']
        itemID = row['itemID']
        bitstream = row['localFileLocation']
        bitstream = bitstream.replace('', '')
        f.writerow([fileName]+[itemID]+[bitstream])

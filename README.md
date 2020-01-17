# dspace-ftp-import

## downloadAndMatchFTPFiles.py

This script accesses a FTP directory and creates a CSV with all the filenames from that directory. Then it uses the CSV produced by *getItemIdsAndBitstreamsForCommunity.py* to match the filenames from the FTP directory to very similar filenames from the Dspace community. There is also an option to allow you to download the FTP files to a local directory on your device.

## getItemIdsAndBitstreamsForCommunity.py

This script loops through a community in DSpace to produce a CSV with all of the bitstream filenames within that community listed with the link to their associated item.

## addBitstreamsToItems.py

This script uses a CSV to add bitstreams to a previously existing item in DSpace through the API. The CSV contains three columns: newfile, itemID, and localFileLocation.

| Column Name       | Description                                                      |
|-------------------|------------------------------------------------------------------|
| newfile           |The filename, with extension, of the bitstream to add to the item |
| itemID            |The link to the item where you would like to add the bitstream    |
| localFileLocation |The full path to the bitstream's location on your device          |   

After reading the CSV with DictReader, the script request the current bitstreams of the Dspace item. The script then prints the number of initial bitstreams associated with that item. Then, the script posts the new bitstream to that Dspace item, naming it with the string indicated in the newfile column. Then the script again requests the current bitstreams, to help verify that the new bitstream has been added.

Then, the script adds a dc.description.provenance note to the item's metadata to provide a record of adding a bitstream. Because the DSpace API cannot simply add additional elements (key/value pairs) to an item's metadata, the script first requests all of the item's metadata and adds each individual metadata element to a list called itemMetadataProcessed. Then a newly created provenance note is added to that list. After that, the script uses the requests module to delete the item's original metadata and to "put" the new metadata from itemMetadataProcessed (containing all the old elements and the new provenance note) as the item's updated metadata. Finally, a csv log of these changes is produced, listing the itemID, the bitstream link, the new filename, the response from the metadata deletion, and the response from the metadata "put" command.

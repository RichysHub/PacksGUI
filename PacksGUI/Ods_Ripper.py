#!/usr/bin/env python
""""Script to rip card data from existing ods file into tinydb format"""

from pyexcel_ods3 import get_data
from tinydb import TinyDB

__author__ = "Richard J Spencer"

ODS_FILE = "E:\\Users\\Richard\\Desktop\\Desktop Records.ods"
CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'

db = TinyDB(CARD_DATA_FILE)
card_table = db.table('card_data')

data = get_data(ODS_FILE)
for entry in data['Pack Data'][1:]:
    if entry and entry[0] != '':
        # had to do some funky business to zero pad
        year = entry[0].year
        month = entry[0].month
        day = entry[0].day
        if month < 10:
            month = '0' +str(month)
        if day < 10:
            day = '0' +str(day)
        card_table.insert({
            'date': '{}/{}/{}'.format(year, month, day),
            'commons': entry[1], 'rares': entry[2], 'epics': entry[3], 'legendaries': entry[4],
            'g_commons': entry[5], 'g_rares': entry[6], 'g_epics': entry[7], 'g_legendaries': entry[8],
            'notes':entry[10], 'set': entry[11]
        })

        # Todo: modify this code, while searching through the ods, follow along with files
        # we know majority of entries are 1 to 1 with images
        # we know data in the ods is ordered, as are the images
        # only issues come with the dupe images, but we can report those dates and fix later

        # if we're using glob to find images for date:
        # if find one, match it (this matches 246 images of 849)
        # if finds mutliple, keep hold of that array and go through the lines of ods
        # pair off data & image one by one
        # if we have an ods line but no image, report that date (missing image :O !)
        # if we come to a new date in the ods, report the old date (dupe image / missing data)

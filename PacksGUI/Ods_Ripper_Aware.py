#!/usr/bin/env python
""""Script to rip card data from existing ods file into tinydb format aware of the images"""

from pyexcel_ods3 import get_data
from tinydb import TinyDB
import glob
import os

__author__ = "Richard J Spencer"

ODS_FILE = "E:\\Users\\Richard\\Desktop\\Desktop Records.ods"
CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'
IMAGE_DIRECTORY = 'E:\\Users\\Richard\\Desktop\\Hearthstone Screenshots\\Packs'

db = TinyDB(CARD_DATA_FILE)
card_table = db.table('card_data')

def get_sort_key(match):
    """Takes a single glob match, spits out the date & time, returning a sort_key"""
    match = match.split('\\')[-1]
    if match.startswith("Hearthstone Screenshot"):
        # eg. Hearthstone Screenshot 01-15-17 17.27.24.png
        # date is zero padded, which is helpful
        date_list = match[23:31].split('-')
        # american->english date
        date_list[0], date_list[1] = date_list[1], date_list[0]
        date_list[2] = '20' + date_list[2]
        date = '/'.join(date_list)
        # time format hh.mm.ss
        time = match[-12:-4]
    else:  # underscored version pre mid 2015
        # eg. Hearthstone_Screenshot_1.3.2014.20.16.36.png
        # date is NOT zero padded, ie 1.1.2015
        date_list = match[23:-13].split('.')
        if len(date_list[0]) == 1:
            date_list[0] = '0' + date_list[0]
        if len(date_list[1]) == 1:
            date_list[1] = '0' + date_list[1]
        date_list[0], date_list[1] = date_list[1], date_list[0]
        date = '/'.join(date_list)
        # time is still zero padded
        time = match[-12:-4]
    datetime = '{}/{}/{}_{}'.format(year, month, day, time)
    return datetime

data = get_data(ODS_FILE)
current_date = None
image_index = 0
matches = []

# In order to keep the photos in place, we just note any that don't have a correspoding record
# These are mainly doubles of other images, highlighting gold shine, or photo of pack count
bad_images = ['Hearthstone_Screenshot_12.19.2013.07.44.44.png',
              'Hearthstone_Screenshot_12.19.2013.07.44.52.png',
              'Hearthstone_Screenshot_12.27.2013.10.26.45.png',
              'Hearthstone_Screenshot_12.28.2013.08.09.32.png',
              'Hearthstone_Screenshot_1.3.2014.20.16.10.png',
              'Hearthstone_Screenshot_1.5.2014.23.06.03.png',
              'Hearthstone_Screenshot_1.14.2014.20.39.32.png',
              'Hearthstone_Screenshot_1.20.2014.12.42.50.png',
              'Hearthstone_Screenshot_3.23.2014.16.23.10.png',
              'Hearthstone_Screenshot_3.23.2014.16.23.16.png',
              'Hearthstone_Screenshot_5.26.2014.13.11.18.png',
              'Hearthstone_Screenshot_6.15.2014.15.28.10.png',
              'Hearthstone_Screenshot_8.30.2014.23.33.36.png',
              'Hearthstone_Screenshot_9.5.2014.04.39.19.png',
              'Hearthstone_Screenshot_12.10.2014.00.19.05.png',
              'Hearthstone_Screenshot_12.15.2014.00.23.20.png',
              'Hearthstone_Screenshot_12.17.2014.19.38.10.png',
              'Hearthstone Screenshot 05-12-15 00.04.58.png',
              'Hearthstone Screenshot 06-09-15 00.23.29.png',
              'Hearthstone_Screenshot_8.21.2014.06.05.08.png',
              'Hearthstone_Screenshot_9.1.2014.19.17.48.png',
              ]

error_counts = {'2013': 0, '2014': 0, '2015': 0, '2016': 0, '2017': 0}
# Just for giving counts of matching errors per year

# ignore first row, headers
# iterate over the records in the ods file
for entry in data['Pack Data'][1:]:
    if entry and entry[0] != '':
        # if the record is from a new date
        if current_date != entry[0]:
            # had to do some funky business to zero pad
            year = entry[0].year
            month = entry[0].month
            day = entry[0].day
            if month < 10:
                month = '0' +str(month)
            if day < 10:
                day = '0' +str(day)

            if (int(year) < 2015) | ((int(year) == 2015) & (int(month) < 4)):
                # old format, using str(int()) to strip leading zero
                glob_term = 'Hearthstone_Screenshot_{}.{}.{}.*.png'.format(str(int(month)), str(int(day)), year)
            else:
                glob_term = 'Hearthstone Screenshot {}-{}-{} *.png'.format(month, day, str(year)[2:])

            # some of the images weren't used from the previous date
            if image_index != len(matches):
                problem = False
                # we have more images than records, but maybe they're just all bad images?
                for match in matches[image_index:]:
                    if match.split('\\')[-1] not in bad_images:
                        problem = True
                if problem:
                    # if we still have images, without records, something will need manual fixing
                    print('Additional image in {}'.format(current_date))
                    error_counts[str(current_date.year)] += 1

            # current date moves forward to that of the new record
            current_date = entry[0]
            image_index = 0
            # can use the modified time to order, as glob is potentially arbitrary order
            # would probably be more correct to use filename, but mtime is known to be a good proxy
            matches = sorted(glob.glob(os.path.join(IMAGE_DIRECTORY, str(year), glob_term)),key=os.path.getmtime)

        # if the image is in the bad images array, we just skip it
        # use while in case of multiple bad images in a row
        while matches[image_index].split('\\')[-1] in bad_images:
            # by increasing image index, we go on to just use the next one
            image_index += 1

        # if we aren't left with any more images for this record, we print the error and move on
        if image_index >= len(matches):
            print('Additional record in {}'.format(current_date))
            image_index += 1
            continue

        # if all has gone well, we can push the data to the tinydb file
        # date is now the sort key
        card_table.insert({
            'date':get_sort_key(matches[image_index]),
            'commons': entry[1], 'rares': entry[2], 'epics': entry[3], 'legendaries': entry[4],
            'g_commons': entry[5], 'g_rares': entry[6], 'g_epics': entry[7], 'g_legendaries': entry[8],
            'notes': entry[10], 'set': entry[11]
        })
        image_index += 1

for year in error_counts:
    print('{} errors found in {}'.format(error_counts[year],year))
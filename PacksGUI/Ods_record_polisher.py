#!/usr/bin/env python

from tinydb import TinyDB, where, Query
import os
import glob

__author__ = "Richard J Spencer"

CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'
IMAGE_DIRECTORY = 'E:\\Users\\Richard\\Desktop\\Hearthstone Screenshots\\Packs'

# date format changeover occured between 3.28.2015 and 04-01-15

def refine_data():
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    for entry in card_data.all():
        year = entry['date'][:4]
        month = entry['date'][5:7]
        day = entry['date'][8:10]
        if (int(year) < 2015) | ((int(year) == 2015) & (int(month)<4)):
            glob_term = 'Hearthstone_Screenshot_{}.{}.{}.*.png'.format(str(int(month)), str(int(day)), year)
        else:
            glob_term = 'Hearthstone Screenshot {}-{}-{} *.png'.format(month, day, year[2:])

        matches = glob.glob(os.path.join(IMAGE_DIRECTORY, year, glob_term))

        if len(matches) == 1:
            match = matches[0].split('\\')[-1]
            print(match)

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







    # for file in os.listdir(os.path.join(IMAGE_DIRECTORY)):
    #     if file.endswith(".png") and file.startswith("Hearthstone"):
    #         self.packs.append(CardPack(file))

            print('{} matched with {} -- {}'.format(entry['date'], date, time))

            datetime = '{}/{}/{}_{}'.format(year,month,day,time)



            print(datetime)
            card_data.update({'sort_key':datetime},where('date') == entry['date'])

refine_data()
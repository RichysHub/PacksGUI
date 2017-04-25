#!/usr/bin/env python
""""Script to rip card data from existing ods file into tinydb format"""

from tinydb import TinyDB, where, Query

__author__ = "Richard J Spencer"

CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'


def average_result(set):
    """given the set code, calculates average contents"""
    db=TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    set_results = card_data.search(where('set') == set)
    print(set_results)
    c = r = e = l = g_c = g_r = g_e = g_l = total = 0
    for entry in set_results:
        total += 1
        c += entry['commons']
        r += entry['rares']
        e += entry['epics']
        l += entry['legendaries']
        g_c += entry['g_commons']
        g_r += entry['g_rares']
        g_e += entry['g_epics']
        g_l += entry['g_legendaries']

    print('Average of: {} commons, {} rares, {} epics, {} legendaries \n'
          ' {} golden commons, {} golden rares, {} golden epics, {} '
          'golden legendaries'.format(c/total, r/total, e/total, l/total, g_c/total, g_r/total, g_e/total, g_l/total))

    pass


def number_packs(set):
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    total = card_data.count(where('set') == set)
    return total


def percentage_40(set):
    """"calculates the %ge of the given set that are 40 dust packs (4c1r)"""
    db=TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    total = card_data.count(where('set') == set)
    q = Query()
    num_forties = card_data.count((q.set == set) & (q.commons == 4) & (q.rares == 1))

    print(num_forties/total)


def value_DE(content):
    """"given the contens of a pack in the form of a dict, returns disenchant value in dust"""
    c = content['commons']
    r = content['rares']
    e = content['epics']
    l = content['legendaries']
    g_c = content['g_commons']
    g_r = content['g_rares']
    g_e = content['g_epics']
    g_l = content['g_legendaries']
    return 5*c + 20*r + 100*e + 400*l + 50*g_c + 100*g_r + 400*g_e * 1600*g_l


def value_craft(content):
    """"given the contens of a pack in the form of a dict, returns craft cost in dust"""
    c = content['commons']
    r = content['rares']
    e = content['epics']
    l = content['legendaries']
    g_c = content['g_commons']
    g_r = content['g_rares']
    g_e = content['g_epics']
    g_l = content['g_legendaries']
    return 40*c + 100*r + 400*e + 1600*l + 400*g_c + 800*g_r + 1600*g_e * 3200*g_l


def total_packs():
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    return len(card_data)


# Todo: verify actually works
def pity_timer(set, rarity):
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    set_packs = card_data.search(where('set') == set)
    # put into reverse date order
    set_packs.sort(key=lambda entry: entry['date'], reverse=True)

    timer = 0
    for pack in set_packs:
        if pack[rarity] > 0:
            break
        timer += 1
    return timer


def number_with_key(key):
    """counts how many packs currently have an associated key"""
    # good for checking profileration of sort_key etc
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    packs = card_data.all()
    total = 0
    with_key = 0
    for pack in packs:
        total += 1
        if key in pack:
            with_key += 1
    print('{} out of {} have sort keys'.format(with_key, total))


def filename_from_date(date):
    pass


def date_from_filename(filename):
    """
    Takes filename of screenshot and returns string date

    :param filename: string filename for Hearthstone Screenshot
    :return: date string of form yyyy/mm/dd/hh/mm/ss
    """

    if filename.startswith("Hearthstone Screenshot"):
        # eg. Hearthstone Screenshot 01-15-17 17.27.24.png
        date_list = filename[23:31].split('-')
        date_list[2] = '20' + date_list[2] # 15->2015
    else: # underscored version pre mid 2015
        # eg. Hearthstone_Screenshot_1.3.2014.20.16.36.png
        date_list = filename[23:-13].split('.')
        if len(date_list[0]) == 1:
            date_list[0] = '0' + date_list[0]
        if len(date_list[1]) == 1:
            date_list[1] = '0' + date_list[1]

    time_list = filename[-12:-4].split('.')
    date_list[0], date_list[1] = date_list[1], date_list[0] # american->english date
    date_list.reverse()
    datetime = '/'.join([*date_list, *time_list])
    return datetime


if __name__ == "__main__":
    average_result('MSoG')
    percentage_40('MSoG')

    for set in ['Classic', 'GVG', 'TGT', 'WotOG', 'MSoG']:
        print('{} packs from {}'.format(number_packs(set), set))

    for rarity in ['epics', 'legendaries', 'g_commons', 'g_rares', 'g_epics', 'g_legendaries']:
        print('Timer for {}: {}'.format(rarity, pity_timer('MSoG',rarity)))

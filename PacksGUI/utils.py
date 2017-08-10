#!/usr/bin/env python
""""Script to rip card data from existing ods file into tinydb format"""

from tinydb import TinyDB, where, Query
from collections import Counter
from Hearthstone import Hearthstone

__author__ = "Richard J Spencer"

# TODO: cleanup! Use config file and also actually USE these functions in layout_test
CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'

# TODO: so much WETness in these functions! so many of them reimplement loading in the data from file

# TODO: move other things that belong here, here

# TODO: better use of config properties for validation and simplification

# TODO: test
# verify averages are calculated correctly
# --> effectively combining a test that it loads the data alright, I suppose


# TODO: this is just printing at the moment, we will need one for actual analysis later
def average_result(set_):
    """given the set code, calculates average contents"""
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    set_results = card_data.search(where('set') == set_)
    print(set_results)
    c = r = e = l = g_c = g_r = g_e = g_l = total = 0
    # TODO: can revamp with some collections.counter usage, probably
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


# TODO: test
# mock data file can be generated, and passed in
# ensure ignores malformed entries present
# gets count of packs correct for random sets
def number_packs(set_):
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    total = card_data.count(where('set') == set_)
    return total


# TODO: can probably be broken down as a combination of two smaller functions
# --> total number of packs, as by number_packs, and then number of given dust value
# TODO: looks like could be clearer using the where logic from tinydb
def percentage_40(set_):
    """"calculates the %ge of the given set that are 40 dust packs (4c1r)"""
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    total = card_data.count(where('set') == set_)
    q = Query()
    num_forties = card_data.count((q.set == set_) & (q.commons == 4) & (q.rares == 1))

    print(num_forties/total)


# TODO: test
# passed an assortment of cards, does it return the correct value?
# could random test it, but at that point you're trusting the random-gen solver more for no reason
def value_disenchant(content):
    """"given the contents of a pack in the form of a dict, returns disenchant value in dust"""
    total = 0
    for rarity in Hearthstone.rarities:
        total += Hearthstone.disenchant_values[rarity] * content[rarity]
    return total


# TODO: test
# As with the value_DE
# TODO: logic once condensed as per suggestions would only differ from value_DE by the value dict
# --> This could be passed in, or be a Hearthstone constant, and DRY things up that way
def value_enchant(content):
    """"given the contents of a pack in the form of a dict, returns craft cost in dust"""
    total = 0
    for rarity in Hearthstone.rarities:
        total += Hearthstone.enchant_values[rarity] * content[rarity]
    return total


# TODO: test
# do we get the right number of packs from a test tinyDB file?
def total_packs():
    # TODO: can be extended to take an argument that defaults to None, so can search for total for set
    # ie, merge with number_packs
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    return len(card_data)


# TODO: test
# test TinyDB file with known timer values, verify they are returned
# Could random test for this, counting when adding to the file is easy, calculating the timer is less easy
# Todo: verify actually works
# Todo: Sets from KFT on will have an initial Leg timer set to non-zero. Need to account for that
def pity_timer(set, rarity):
    db = TinyDB(CARD_DATA_FILE)
    card_data = db.table('card_data')
    set_packs = card_data.search(where('set') == set)
    # put into reverse date order
    set_packs.sort(key=lambda entry: entry['date'], reverse=True)

    # We're counting lines till we hit the rarity
    # Might be better off using a tinydb query to find first occurrence
    # Can we then get some form of index from that, and ensure things have been sorted by correct key?
    timer = 0
    for pack in set_packs:
        if pack[rarity] > 0:
            break
        timer += 1
    return timer


# TODO: this was really built as a utility when fleshing out the system, is it going to have use?
def number_with_key(key):
    """counts how many packs currently have an associated key"""
    # good for checking proliferation of sort_key etc
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


# TODO: test
# pass in some file names, then peel out the data from the returned datetime and compare
# Ensure works for both types of filename
# TODO: handle malformed file names?
# TODO: use of slice is clunky, could use regex, or a less painful to understand split
def date_from_filename(filename):
    """
    Takes filename of screenshot and returns string date

    :param filename: string filename for Hearthstone Screenshot
    :return: date string of form yyyy/mm/dd/hh/mm/ss
    """

    if filename.startswith("Hearthstone Screenshot"):
        # eg. Hearthstone Screenshot 01-15-17 17.27.24.png
        date_list = filename[23:31].split('-')
        date_list[2] = '20' + date_list[2]  # 15->2015
    else: # underscored version pre mid 2015
        # eg. Hearthstone_Screenshot_1.3.2014.20.16.36.png
        date_list = filename[23:-13].split('.')
        if len(date_list[0]) == 1:
            date_list[0] = '0' + date_list[0]
        if len(date_list[1]) == 1:
            date_list[1] = '0' + date_list[1]

    time_list = filename[-12:-4].split('.')
    date_list[0], date_list[1] = date_list[1], date_list[0]  # american->english date
    date_list.reverse()
    datetime = '/'.join([*date_list, *time_list])
    return datetime


if __name__ == "__main__":
    # TODO: remove, was just for testing
    average_result('MSoG')
    percentage_40('MSoG')

    for set in ['Classic', 'GVG', 'TGT', 'WotOG', 'MSoG']:
        print('{} packs from {}'.format(number_packs(set), set))

    for rarity in ['epics', 'legendaries', 'g_commons', 'g_rares', 'g_epics', 'g_legendaries']:
        print('Timer for {}: {}'.format(rarity, pity_timer('MSoG',rarity)))

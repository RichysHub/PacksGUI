#!/usr/bin/env python

"""GUI for storing statistics of pack openings from screenshots"""

# from tkinter import Tk, Menu, PhotoImage, Label, Spinbox, Frame
from tkinter import *
from tkinter.ttk import *
from tkinter import font
from PIL import Image, ImageTk
import os
from utils import date_from_filename as d_from_f

from tinydb import TinyDB, where

__author__ = "Richard J Spencer"

# Todo: split into config file for path to images
# path to un-stored screenshots
TO_PROCESS = 'E:\\Users\\Richard\\Desktop'


# path to stored screenshots root folder
# auto-splits to correct year folder
# PROCESSED =

CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'

# Todo:remove this garbage of process-mapping
# With screenshots on the desktop
# open up the GUI, which searches the desktop for images
# on load, gets the full list of possible screenshots
# can display count of screenshots found
# possible progress bar
# cycles through until end of list then self closes
# skip button for non-packs will leave shots, hence not looping

# reads image file in and displays as part of GUI
# needs to scale image, so it's not 1920x1080. Need to use PIL for this
# pre-processing here, ie Peter's NN for guessing the settings to submit
# read in date, time etc and display in better format
# presents buttons for selecting 40dust/55dust etc
# really it'll be a 4c1r, 3c2r etc
# buttons will have nice custom graphics to be easy to use
# notes text field for entering Legendary names etc
# could extend to pull card list data, for autocomplete
# up to 6 notes may be needed on a single card
# ( 5 of legendary, golden epic, golden legendary) + First of set
# selection box for card set
# Drop down selection box from known sets
# should likely be sorted with wild sets pushed down
# ie chronological, except for classic

# On hit submit:
# verifies 5 cards specified
# ensures all needed data given, else prompts for that data
# adds data to the data-store
# currently .ods spreadsheet, could move to csv, database, whatever
# moves the image to the output folder
# use date to determine which year folder to store image in

# Todo: add resizing handling of image
# configure event can be bound to, allowing PIL to rescale image

# Pack object?
# image_name - name of image
# image_path - full path to image
# date - date string of format dd/mm/yyyy
# time - only used to sort screenshots from the same day
# distribution of cards - perhaps a dict, {c:4, r:1, e:0, ...}
# value? - would mainly be for part of UI, spreadsheet already does this
# sort_key - yyyy/mm/dd_hh.mm.ss for sorting screenshots

class CardPack:
    def __init__(self, file):
        self.image_name = file
        self.image_path = os.path.join(TO_PROCESS, file)
        self.parse_name()
        self.date = ""
        self.time = ""
        self.sort_key = ""
        self.contents = {'commons':0, 'rares':0, 'epics':0, 'legendaries':0,
                         'g_commons':0, 'g_rares':0, 'g_epics':0, 'g_legenaries':0}
        self.card_set = ""
        self.notes = ""

    def output(self):
        return {'date':self.sort_key, 'set':self.card_set, 'notes':self.notes, **self.contents}

    def parse_name(self):
        # from filename, extract the date and time of the screenshot

        # spaced version is new version
        if self.image_name.startswith("Hearthstone Screenshot"):
            # eg. Hearthstone Screenshot 01-15-17 17.27.24.png
            # date is zero padded, which is helpful
            date_list = self.image_name[23:31].split('-')
            # american->english date
            date_list[0], date_list[1] = date_list[1], date_list[0]
            date_list[2] = '20' + date_list[2]
            self.date = '/'.join(date_list)
            # time format hh.mm.ss
            self.time = self.image_name[-12:-4]

        else:  # underscored version pre mid 2015
            # eg. Hearthstone_Screenshot_1.3.2014.20.16.36.png
            # date is NOT zero padded, ie 1.1.2015
            date_list = self.image_name[23:-13].split('.')
            if len(date_list[0]) == 1:
                date_list[0] = '0' + date_list[0]
            if len(date_list[1]) == 1:
                date_list[1] = '0' + date_list[1]
            date_list[0], date_list[1] = date_list[1], date_list[0]
            self.date = '/'.join(date_list)
            # time is still zero padded
            self.time = self.image_name[-12:-4]
        self.sort_key = '/'.join(reversed(date_list)) + '_' + self.time[6:] + self.time[2:6] + self.time[:2]
        print('Date: {} | Time: {}'.format(self.date, self.time))


class PacksGUI:
    def __init__(self, master):

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10, family="Belwe-Bold")
        root.option_add("*Font", default_font)


        self.master = master
        master.title("Hearthstone Pack Recorder")
        self.packs = []

        self.layout()

        self.find_packs()
        # Todo: would be nice to use with open format, else remember to close image
        image = Image.open(self.packs[0].image_path)
        # open image with PIL, resize and convert for Tk
        # image = Image.open('E:\\Users\\Richard\\Desktop\\m.png')
        image = image.resize((960, 540), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        # photo is placed on a label for display
        label = Label(self.imageFrame, image=photo)
        label.image = photo
        label.pack()

    def layout(self):
        self.imageFrame = Frame(self.master)
        valuesFrame = Frame(self.master)
        setFrame = Frame(self.master)
        noteFrame = Frame(self.master)
        buttonsFrame = Frame(self.master)

        self.imageFrame.grid()
        valuesFrame.grid(row = 1)
        setFrame.grid(row = 2)
        noteFrame.grid(row = 3)
        buttonsFrame.grid(row = 4)

        Grid.columnconfigure(self.master, 0, weight=1)

        common_variable = StringVar()
        common_variable.set("0")
        rare_variable = StringVar()
        rare_variable.set("0")
        epic_variable = StringVar()
        epic_variable.set("0")
        legendary_variable = StringVar()
        legendary_variable.set("0")

        golden_common_variable = StringVar()
        golden_common_variable.set("0")
        golden_rare_variable = StringVar()
        golden_rare_variable.set("0")
        golden_epic_variable = StringVar()
        golden_epic_variable.set("0")
        golden_legendary_variable = StringVar()
        golden_legendary_variable.set("0")

        self.counter_variables = {"common":common_variable, "rare":rare_variable,
                                  "epic":epic_variable, "legendary": legendary_variable,
                                  "golden_common": golden_common_variable, "golden_rare": golden_rare_variable,
                                  "golden_epic": golden_epic_variable, "golden_legendary": golden_legendary_variable
                                  }

        # nicer way to generate the spinners, though the grid requirement makes it a little funky
        # Todo: far more pythonic, investigate
        # spinners = {}
        # for key in self.counter_variables:
        #     counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=self.counter_variables[key], width=3, justify=CENTER)
        #     spinners.update({key:counter})

        common_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=common_variable, width=3, justify=CENTER)
        rare_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=rare_variable, width=3, justify=CENTER)
        epic_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=epic_variable, width=3, justify=CENTER)
        legendary_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=legendary_variable, width=3, justify=CENTER)
        golden_common_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=golden_common_variable, width=3, justify=CENTER)
        golden_rare_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=golden_rare_variable, width=3, justify=CENTER)
        golden_epic_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=golden_epic_variable, width=3, justify=CENTER)
        golden_legendary_counter = Spinbox(valuesFrame, from_=0, to=5, textvariable=golden_legendary_variable, width=3, justify=CENTER)

        forty_dust_button = Button(valuesFrame, text="40 dust", command=self.forty_duster)

        common_counter.grid(column=0, row=0)
        rare_counter.grid(column=1, row=0)
        epic_counter.grid(column=3, row=0)
        legendary_counter.grid(column=4, row=0)

        forty_dust_button.grid(column=2, rowspan=2, row=0)

        golden_common_counter.grid(column=0, row=1)
        golden_rare_counter.grid(column=1, row=1)
        golden_epic_counter.grid(column=3, row=1)
        golden_legendary_counter.grid(column=4, row=1)

        self.set_variable = StringVar()

        set_choices = ["Classic", "Whispers of the Old Gods",
                       "Mean Streets of Gadgetzan",  "Journey to Un'Goro", "Goblins vs. Gnomes",
                      "The Grand Tournament"]

        self.set_variable.set("Classic")
        # tkinter version
        # set_selector = OptionMenu(setFrame, self.set_variable, *set_choices)
        # ttk doesn't add the default to the options (allows a message)
        set_selector = OptionMenu(setFrame, self.set_variable, "Card Set", *set_choices)
        # mildly hacky way to add a seperator into the dropdown menu after standard packs
        set_selector.__getitem__('menu').insert_separator(4)

        # print(set_selector.__getitem__('menu').configure(activebackground="green"))

        # attempt to add images to options
        # logo = Image.open("../Logo_TGT.png")
        # logo_photo = ImageTk.PhotoImage(logo)
        # set_menu.insert_command(1, label="The Grand Tournament", image=logo_photo, compound = LEFT, command = lambda :self.set_variable.set("The Grand Tournament"))
        # set_menu.logos = logo_photo # keep reference

        set_selector.pack()

        self.note_box = Entry(noteFrame, justify=CENTER, width=60)
        self.note_box.pack()

        submit_button = Button(buttonsFrame, text="    Submit    ", command=self.submit)

        # Todo: not pack button can either skip the image, or bring up a dialog showing folders available
        # ie, can choose 'Deck', even prompt for name of deck (check for name, if not same date, refuse)
        # 'Deck' also doesn't use year folders, so just goes into folder
        # if chose 'Arena Related', file will go in correct year folder
        not_pack_button = Button(buttonsFrame, text="Not Pack")

        submit_button.pack(side=LEFT)
        not_pack_button.pack(side=LEFT)

    def find_packs(self):
        for file in os.listdir(TO_PROCESS):
            if file.endswith(".png") and file.startswith("Hearthstone"):
                self.packs.append(CardPack(file))
        # sort can be done here with a key, eg., yyyy/mm/dd/hh/mm/ss
        # reverse so pop can be used to get in order
        # could otherwise do a for pack in packs dealio
        self.packs.reverse()
        print(self.packs)

    def submit(self):
        # takes the values currently set, validates
        # checks no additional info needed, else prompts for that
        # if all is in order, adds data to the spreadsheet
        # verifies add was successful?
        # moves the image to the correct file
        # continues onto the next image in the list

        total_cards = 0
        for variable_key in self.counter_variables:
            total_cards += int(self.counter_variables[variable_key].get())

        if total_cards != 5:
            self.alert("Number of cards selected =/= 5")
            return

        print('{} commons | {} rares | {} epics | {} legendarys'
              .format(self.counter_variables["common"].get(), self.counter_variables["rare"].get(),
                      self.counter_variables["epic"].get(), self.counter_variables["legendary"].get()))
        print('{} golden commons | {} golden rares | {} golden epics | {} golden legendarys'
              .format(self.counter_variables["golden_common"].get(), self.counter_variables["golden_rare"].get(),
                      self.counter_variables["golden_epic"].get(), self.counter_variables["golden_legendary"].get()))
        print('From the set: {}'.format(self.set_variable.get()))
        print('Notes: {}'.format(self.note_box.get()))

        pass

    def skip(self):
        # image is not a pack; screenshots are all alike, so this can only be user done
        # just moves on to next pack
        pass

    def forty_duster(self):
        # called if current pack is a 4 common, 1 rare pack, ie 40 duster
        for key in self.counter_variables:
            if key == "common":
                self.counter_variables[key].set("4")
            elif key == "rare":
                self.counter_variables[key].set("1")
            else:
                self.counter_variables[key].set("0")

    def alert(self, message):
        top = Toplevel()
        top.title("Alert")
        msg = Message(top, text=message)
        msg.pack()
        button = Button(top, text="OK", command=top.destroy)
        button.pack()

    def save_to_tinydb(self):
        # takes the current card pack, and save the data to the ods file that is specified elsewhere
        pass

root = Tk()
my_gui = PacksGUI(root)

print(d_from_f("Hearthstone Screenshot 01-15-17 17.27.24.png"))

db = TinyDB(CARD_DATA_FILE)
card_table = db.table('card_data')

# what do we want to save?
# date / time can be seperate, perhaps sortkey in there too? (having both is ~redundant)
# number or c,r,e,l,gc,gr,ge,gl
# card set
# Notes

root.mainloop()

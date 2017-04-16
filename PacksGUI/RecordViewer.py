#!/usr/bin/env python

"""GUI for storing statistics of pack openings from screenshots"""

# from tkinter import Tk, Menu, PhotoImage, Label, Spinbox, Frame
from tkinter import *
from tkinter.ttk import *
from tkinter import font
from PIL import Image, ImageTk
import os

from tinydb import TinyDB, where

__author__ = "Richard J Spencer"

CARD_DATA_FILE = 'E:\\Users\\Richard\\Desktop\\card_db.json'
IMAGE_DIRECTORY = 'E:\\Users\\Richard\\Desktop\\Hearthstone Screenshots\\Packs'

class Viewer:
    def __init__(self, master):
        self.master = master
        master.title("Hearthstone Pack Viewer")

        db = TinyDB(CARD_DATA_FILE)
        card_table = db.table('card_data')
        self.entries = card_table.all()
        self.entries.sort(key=lambda entry: entry['date'])
        self.dates = [entry['date'] for entry in self.entries]
        self.datesVar = StringVar(value=self.dates)
        print(self.dates)
        self.layout()


    def layout(self):

        self.image_label = Label(self.master)


        self.image_label.grid(column = 0, row=0)
        self.l = Listbox(self.master, height=30, listvariable=self.datesVar)
        self.l.grid(column=0, row=1, sticky=(N, W, E, S))
        s = Scrollbar(root, orient=VERTICAL, command=self.l.yview)
        s.grid(column=1, row=1, sticky=(N, S))
        self.l['yscrollcommand'] = s.set
        Sizegrip().grid(column=1, row=1, sticky=(S, E))
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        self.l.bind('<<ListboxSelect>>', self.showImage)

    def showImage(self, *args):
        idxs = self.l.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            date = self.dates[idx]

            year = date[:4]
            month = date[5:7]
            day = date[8:10]
            time = date[-8:]
            if (int(year) < 2015) | ((int(year) == 2015) & (int(month)<4)):
                file_name = 'Hearthstone_Screenshot_{}.{}.{}.{}.png'.format(str(int(month)), str(int(day)), year, time)
            else:
                file_name = 'Hearthstone Screenshot {}-{}-{} {}.png'.format(month, day, year[2:], time)

        image = Image.open(os.path.join(IMAGE_DIRECTORY, year, file_name))
        image = image.resize((960, 540), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

root = Tk()
my_gui = Viewer(root)
root.mainloop()
#!/usr/bin/env python

# from tkinter import Tk, Menu, PhotoImage, Label, Spinbox, Frame
from tkinter import *
from tkinter.ttk import *
from tkinter import font
from PIL import Image, ImageTk
import os


class IntScroller(Frame):

    def __init__(self, master, **kwargs):
        Frame.__init__(self, master)

        # Todo: add some fancy backdrop graphics with a holding label
        # self.backdrop = Label(self)



        self.min = kwargs.pop('from_', 0)
        self.max = kwargs.pop('to', 5)
        self.increment = kwargs.pop('increment',1)
        self.var = kwargs.pop('textvariable', IntVar())

        # Todo: ensure we pop out any kwargs that can't be passed down

        self.up_button = Button(self, text='\u25b2', command=self.inc, **kwargs)
        self.text = Entry(self, textvariable = self.var, justify=CENTER, **kwargs)
        self.down_button = Button(self, text='\u25bc', command=self.dec, **kwargs)

        self.up_button.pack(side=TOP)
        self.text.pack(side=TOP)
        self.down_button.pack(side=TOP)


        # from_: int to count from
        # to: into to count to
        # textvariable: variable holding value (should replace with intVar?)
        # justify:
        # width:
        #
        #
        # STANDARD OPTIONS
        #
        #     activebackground, background, borderwidth,
        #     cursor, exportselection, font, foreground,
        #     highlightbackground, highlightcolor,
        #     highlightthickness, insertbackground,
        #     insertborderwidth, insertofftime,
        #     insertontime, insertwidth, justify, relief,
        #     repeatdelay, repeatinterval,
        #     selectbackground, selectborderwidth
        #     selectforeground, takefocus, textvariable
        #     xscrollcommand.
        #
        # WIDGET-SPECIFIC OPTIONS
        #
        #     buttonbackground, buttoncursor,
        #     buttondownrelief, buttonuprelief,
        #     command, disabledbackground,
        #     disabledforeground, format, from_,
        #     invalidcommand, increment,
        #     readonlybackground, state, to,
        #     validate, validatecommand values,
        #     width, wrap,

    def inc(self):
        old_val = self.var.get()
        if old_val <= (self.max - self.increment):
            self.var.set(old_val + self.increment)

    def dec(self):
        old_val = self.var.get()
        if old_val >= (self.min + self.increment):
            self.var.set(old_val - self.increment)

    pass


class GUI:
    def __init__(self, master):

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=16, family="Belwe-Bold")
        root.option_add("*Font", default_font)

        self.master = master
        self.layout()
        pass

    def layout(self):

        self.main_frame = Frame(self.master)
        self.main_frame.pack(padx=20, pady=20)

        self.tab_frame = Frame(self.main_frame, height=100)
        self.tab_frame.grid(row=0, column=0, columnspan=5)

        image = Image.open("E:\\Users\\Richard\\Desktop\\Hearthstone Screenshot FF-FF-FF AA.EE.II.png")
        image = image.resize((700, 394), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        image_frame = Label(self.main_frame, image=photo)
        image_frame.image = photo

        image_frame.grid(row=1, column=0, columnspan=5, pady=20)

        small_font = font.Font()
        small_font.configure(size=10, family="Belwe-Bold")
        s = Style()
        s.configure('my.TButton', font=("Belwe-Bold", 8))


        self.c_var = IntVar()
        self.r_var = IntVar()
        self.e_var = IntVar()
        self.l_var = IntVar()
        self.g_c_var = IntVar()
        self.g_r_var = IntVar()
        self.g_e_var = IntVar()
        self.g_l_var = IntVar()

        self.c_scoll = IntScroller(self.main_frame, textvariable=self.c_var, width=2)
        self.r_scoll = IntScroller(self.main_frame, textvariable=self.r_var, width=2)
        self.e_scoll = IntScroller(self.main_frame, textvariable=self.e_var, width=2)
        self.l_scoll = IntScroller(self.main_frame, textvariable=self.l_var, width=2)
        self.g_c_scoll = IntScroller(self.main_frame, textvariable=self.g_c_var, width=2)
        self.g_r_scoll = IntScroller(self.main_frame, textvariable=self.g_r_var, width=2)
        self.g_e_scoll = IntScroller(self.main_frame, textvariable=self.g_e_var, width=2)
        self.g_l_scoll = IntScroller(self.main_frame, textvariable=self.g_l_var, width=2)

        self.g_c_scoll.text.config(font=small_font)
        self.g_c_scoll.up_button.config(style='my.TButton')
        self.g_c_scoll.down_button.config(style='my.TButton')
        self.g_r_scoll.text.config(font=small_font)
        self.g_r_scoll.up_button.config(style='my.TButton')
        self.g_r_scoll.down_button.config(style='my.TButton')
        self.g_e_scoll.text.config(font=small_font)
        self.g_e_scoll.up_button.config(style='my.TButton')
        self.g_e_scoll.down_button.config(style='my.TButton')
        self.g_l_scoll.text.config(font=small_font)
        self.g_l_scoll.up_button.config(style='my.TButton')
        self.g_l_scoll.down_button.config(style='my.TButton')

        self.c_scoll.grid(row=2, column=0)
        self.r_scoll.grid(row=2, column=1)
        self.e_scoll.grid(row=2, column=3)
        self.l_scoll.grid(row=2, column=4)
        self.g_c_scoll.grid(row=3, column=0, pady=20)
        self.g_r_scoll.grid(row=3, column=1, pady=20)
        self.g_e_scoll.grid(row=3, column=3, pady=20)
        self.g_l_scoll.grid(row=3, column=4, pady=20)

        self.forty_button = Button(self.main_frame, text="40 Dust")
        self.forty_button.grid(row=2, column=2)


        self.set_variable = StringVar()

        set_choices = ["Classic", "Whispers of the Old Gods",
                       "Mean Streets of Gadgetzan",  "Journey to Un'Goro", "Goblins vs. Gnomes",
                      "The Grand Tournament"]

        self.set_variable.set("Classic")
        set_selector = OptionMenu(self.main_frame, self.set_variable, "Card Set", *set_choices)
        set_selector['menu'].insert_separator(4)
        set_selector['menu'].config(font=small_font)
        set_selector.grid(row=4, column=1, columnspan=3, pady=20)

        # Todo: fix up the fonts. Default font will be determined by the option menu, due to inability to modify easily

        self.notes_label = Label(self.main_frame, text="Notes:", font=small_font)
        self.notes_label.grid(row=5, column=0, columnspan=5)
        self.note_box = Entry(self.main_frame, justify=CENTER, width=60)
        self.note_box.grid(row=6, column=0, columnspan=5)

        self.submit_button = Button(self.main_frame, text="Submit")
        self.submit_button.grid(row=7, column=0, columnspan=3, sticky=NSEW, pady=20, padx=10)
        self.not_pack_button = Button(self.main_frame, text="Not Pack")
        self.not_pack_button.grid(row=7, column=3, columnspan=2, sticky=NSEW, pady=20, padx=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.columnconfigure(4, weight=1)

root = Tk()
my_gui = GUI(root)
root.mainloop()

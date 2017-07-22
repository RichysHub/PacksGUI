#!/usr/bin/env python

# Todo: remove the import * bad habits

# from tkinter import Tk, Menu, PhotoImage, Label, Spinbox, Frame
from tkinter import *
from tkinter.ttk import *
from tkinter import font
from PIL import Image, ImageTk
import configparser
import os
import shutil
from collections import Counter
from utils import date_from_filename
from datetime import datetime
from tinydb import TinyDB, Query


class IntScroller(Frame):

    def __init__(self, master, **kwargs):
        Frame.__init__(self, master)

        # Todo: add some fancy backdrop graphics with a holding label
        # self.backdrop = Label(self)

        self.min = kwargs.pop('from_', 0)
        self.max = kwargs.pop('to', 5)
        self.increment = kwargs.pop('increment', 1)
        self.var = kwargs.pop('textvariable', IntVar())

        # Todo: ensure we pop out any kwargs that can't be passed down

        self.up_button = Button(self, text='\u25b2', command=self.inc, **kwargs)
        self.text = Entry(self, textvariable = self.var, justify=CENTER, **kwargs)
        self.down_button = Button(self, text='\u25bc', command=self.dec, **kwargs)

        self.up_button.pack(side=TOP)
        self.text.pack(side=TOP)
        self.down_button.pack(side=TOP)


        # Copied from spindown, hoping to implement similar options for compatibility
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

# Todo: perhaps a view base class if enough methods are shared


class CardPack:
    def __init__(self, file_path, folder_path):
        self.image_name = file_path

        self.folder_path = folder_path
        self.full_path = os.path.join(folder_path, file_path)
        # Todo: datetime module wants ints, not strings, so is a bit of a pain
        # --> May want to reevaluate implementation of the sortkey
        self.sortkey = date_from_filename(file_path)

        self.date_time = datetime(*[int(val) for val in self.sortkey.split('/')])
        self.date = self.date_time.date()
        self.time = self.date_time.time()


# Displays pity timers
# Should be on a per set basis, with dropdown
# Should also have some form of suggestion for pack to buy
# Perhaps even a top3 list of exciting timers that are nearly up
# --> Obvs prioritising legendary over epic, but would rank Leg in 2 > Epic in 1 eg.
class PityView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Pity'


# A basic statistics page, perhaps later will include some pretty graphs
class StatsView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Stats'

        self.rarities = ['common', 'rare', 'epic', 'legendary',
                         'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']

        self.set_selector = None
        total_packs_label = Label(self, text='Total packs opened:')
        total_packs_label.grid(row=1, column=0, columnspan=2, sticky=E)
        self.total_packs_number = Label(self, text='Not set')
        self.total_packs_number.grid(row=1, column=2, columnspan=2, sticky=W)

        self.total_numbers = {}
        self.mean_numbers = {}

        for idx, rarity in enumerate(self.rarities):
            boundary = Frame(self)
            rarity_label = Label(boundary, text=rarity)
            rarity_label.pack()
            total_number = Label(boundary, text='#')
            total_number.pack(pady=10)
            mean_number = Label(boundary, text='#')
            mean_number.pack()
            boundary.grid(row=2+int(idx/4), column=idx%4, padx=20, pady=30)

            self.total_numbers.update({rarity: total_number})
            self.mean_numbers.update({rarity: mean_number})

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def add_set_selector(self, model_variable, standard, wild):
        # Adding in some space padding to avoid an issue with tkinter
        # AS 2 OptionMenus would have some of the same items, highlight tick cross-updates
        set_selector = OptionMenu(self, model_variable, " Card Set ", ' All Sets ',
                                 *[' '+item+' ' for item in standard], *[' '+item+' ' for item in wild])
        set_selector['menu'].insert_separator(1)
        set_selector['menu'].insert_separator(len(standard)+2)
        set_selector.grid(row=0, column=0, columnspan=5, pady=20)
        self.set_selector = set_selector
        pass

    def bind_pack_number(self, variable):
        # binds the variable as the value for the pack number display
        self.total_packs_number.config(textvariable=variable)

    def bind_total_cards_numbers(self, variable_dict):
        for rarity in self.rarities:
            self.total_numbers[rarity].config(textvariable=variable_dict[rarity])

    def bind_mean_cards_numbers(self, variable_dict):
        for rarity in self.rarities:
            self.mean_numbers[rarity].config(textvariable=variable_dict[rarity])


# A view will sit within the app, bordered by padding, with navigation above
class PackView(Frame):
    """Singleton class for main pack detail entry view"""
    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master
        self.name = 'Pack'

        image = Image.open("E:\\Users\\Richard\\Desktop\\GUI_Sandbox\\Placeholder.png")
        image = image.resize((700, 394), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.image_frame = Label(self, image=photo)
        self.image_frame.image = photo
        self.image_frame.grid(row=0, column=0, columnspan=4, pady=20)

        self.rarity_values = {}
        self.rarity_scrollers = {}
        self.rarities = ['common', 'rare', 'epic', 'legendary',
                         'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']

        self.notes_label = Label(self, text="Notes:")
        self.notes_label.grid(row=4, column=0, columnspan=4)
        self.note_box = Entry(self, justify=CENTER, width=60)
        self.note_box.grid(row=5, column=0, columnspan=4)

        self.submit_button = Button(self, text="Submit")
        self.submit_button.grid(row=6, column=0, columnspan=3, sticky=NSEW, pady=20, padx=10)
        self.not_pack_button = Button(self, text="Not Pack")
        self.not_pack_button.grid(row=6, column=3, columnspan=2, sticky=NSEW, pady=20, padx=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def add_scrollers(self, scrollvars):
        for rarity in self.rarities:
            self.rarity_scrollers.update({rarity: IntScroller(self, textvariable=scrollvars[rarity], width=2)})

        self.rarity_scrollers['common'].grid(row=1, column=0, pady=10)
        self.rarity_scrollers['rare'].grid(row=1, column=1, pady=10)
        self.rarity_scrollers['epic'].grid(row=1, column=2, pady=10)
        self.rarity_scrollers['legendary'].grid(row=1, column=3, pady=10)

        self.rarity_scrollers['golden_common'].grid(row=2, column=0, pady=10)
        self.rarity_scrollers['golden_rare'].grid(row=2, column=1, pady=10)
        self.rarity_scrollers['golden_epic'].grid(row=2, column=2, pady=10)
        self.rarity_scrollers['golden_legendary'].grid(row=2, column=3, pady=10)
        pass

    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", *standard, *wild)
        set_selector['menu'].insert_separator(len(standard))
        set_selector.grid(row = 3, column=1, columnspan=2, pady=20)

    def set_image(self, image):
        # takes the result of Image.open, and pushes result to the image frame
        sized_image = image.resize((700, 394), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(sized_image)
        self.image_frame.config(image=photo)
        self.image_frame.image = photo


class PackMiniView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Packs'
    pass


class ArenaMiniView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Arena Rewards'
    pass


class SeasonMiniView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Season End'
    pass


class OtherMiniView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.name = 'Other'
    pass


# This view is special, it occupies the entire GUI and contains other views within it
class MainView(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.views = {}

        self.tab_frame = Frame(self, height=100)
        self.tab_frame.grid(row=0, column=0)
        self.tab_buttons = []

    # passed a factory method, sets up a view from that factory, and adds it to its view list
    # Also sets up the buttons here. These buttons just switch which view is on top, so are OK to be view-bound
    def add_view(self, factory):
        view = factory(self)
        self.views[view.name] = view
        view.grid(row=1, column=0, sticky=NSEW)
        # adds button to nav bar that will raise that view
        button = Button(self.tab_frame, text=view.name, command=lambda: self.raise_view(view.name))
        btn_idx = len(self.tab_buttons)
        button.grid(row=0, column=btn_idx, padx=20, sticky=NSEW)
        self.tab_buttons.append(button)
        self.columnconfigure(btn_idx, weight=1)
        return view

    def raise_view(self, view_name):
        frame = self.views[view_name]
        frame.tkraise()


# designed to hold the back-bone logic of the whole shebang

# Controller passes a config, from which the model extracts a lot of info
# model will then go and grab the files it needs to hold
class Model:

    def __init__(self, config):
        self.config = config

        db_file = self.config['filepaths']['tinydb']
        db = TinyDB(db_file)
        self.card_table = db.table('card_data')

        self.packs = []
        self.current_pack = None
        self.rarities = ['common', 'rare', 'epic', 'legendary',
                         'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']
        self.standard_sets = config['sets_standard']
        self.wild_sets = config['sets_wild']

        self.acronyms = dict(config['sets_wild'].items())
        self.acronyms.update(config['sets_standard'].items())

        self.default_pack = {'common': 4, 'rare': 1}

        self.image = None

        # IDEA: split out golden quantities
        # --> easy enough to work around
        # --> some validation easier
        # --> allows for controller to send the view the two sets separately?

        self.quantities = {}
        self.notes = StringVar()  # defaults to empty string
        self.card_set = StringVar()
        self.viewed_total_quantities = {} # quantites for each rarity, for stats view
        self.viewed_mean_quantities = {}
        self.view_card_set = StringVar() # card set, as deemed by stats view
        self.viewed_total_packs = IntVar() # packs for stats view card set

        for rarity in self.rarities:
            # rarities are stored in IntVars so view can auto-update
            self.quantities.update({rarity: IntVar()})
            # viewed quantities are linked to being the # of that rarity in DB, for view_card_set
            self.viewed_total_quantities.update({rarity: IntVar()})
            self.viewed_mean_quantities.update({rarity: StringVar()})

        self.view_card_set.trace_variable('w', self.extract_data)

        self.find_images()
        self.next_pack()

        pass

    def find_images(self):
        """Finds all the screenshots on the desktop that might be packs, and stores them"""
        desktop_path = self.config['filepaths']['desktop']
        for file in os.listdir(desktop_path):
            if file.endswith(".png") and file.startswith("Hearthstone"):
                # Todo: signature of CardPack might change
                self.packs.append(CardPack(file, desktop_path))
        # reverse so pop can be used to get in order
        self.packs.sort(key=lambda pack: pack.sortkey, reverse=True)
        print(self.packs)

        pass

    def next_pack(self):
        # moves onto the next pack in the list, updating image as well
        try:
            self.current_pack = self.packs.pop()
            self.image = Image.open(self.current_pack.full_path)
        except IndexError:
            # no more packs to process
            self.current_pack = None

        # Todo: handle the no-more pack case more deftly
        # could use a BooleanVar flag for 'model has finished'

        self.reset_variables()

    def reset_variables(self):
        # Resetting some variables back to default values
        for rarity in self.rarities:
            # get default contents of pack, assumes 0 of any not specified
            default = self.default_pack.get(rarity, 0)
            self.quantities[rarity].set(default)
        self.notes.set('')
        # Note: self.card_set is not reset, assumes multiple packs of same set most likely

    def is_valid_pack(self):

        if (self.card_set.get() not in self.standard_sets) and \
                (self.card_set.get() not in self.wild_sets):
            # CARD SET NOT SELECTED
            return False

        total_cards = sum([val.get() for val in self.quantities.values()])
        if total_cards != 5:
            #  NOT ENOUGH CARDS
            return False

        if (self.quantities['legendary'].get() + self.quantities['golden_epic'].get() +
                self.quantities['golden_legendary'].get() > 0) and (self.notes.get() == ''):
            # NOTEWORTHY CARD NOT NOTED
            return False

        return True

    def submit(self):
        # commits pack data to tinydb file
        # makes no attempt to validate, assumes you have sorted this

        self.card_table.insert({
            'date': self.current_pack.sortkey,
            **{rarity: self.quantities[rarity].get() for rarity in self.rarities},
            'notes': self.notes.get(), 'set': self.acronyms[self.card_set.get()]
        })

        pack_folder = self.config['output']['packs']
        dest_folder = os.path.join(pack_folder, str(self.current_pack.date.year))

        #check year folder exists
        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)

        destination = os.path.join(dest_folder, self.current_pack.image_name)
        shutil.move(self.current_pack.full_path, destination)

        #TODO: check this is needed
        self.extract_data()

        self.next_pack()

    def not_pack(self):

        # Todo: REMOVE
        # Temporarily will just skip the pack entirely
        self.next_pack()

        # user has selected that the image is not a pack
        # has to work out where else the file might be intended to go (from ini)
        # Should then cause the view to change for the user to select the destination

        # Destination being picked will evoke some other method of the model, not here
        # --> Issue with that would be that it's not so clear what method to call?
        # --> ini file allows arbitrary folders to be added simply by declaring them & giving the rules for that file
        # --> perhaps a method that takes the internal name as an arg and uses that to enact behaviour?
        pass

    # on the not_pack selection, user has decided that this is not to be moved from desktop
    # --> Currently just using an alias to the next_pack method to skip the current pack
    skip_image = next_pack

    def process_not_pack(self, out_folder):
        # from the not_pack selection, user has decided this should be under out_folder
        # should look to config as to any subfolders based on date of image
        # should move image to desired location
        pass

    def extract_data(self, *callback):
        # called when the view_card_set variable changes
        # looks at the new value, and determines if it is a set, or 'All Sets'
        # performs requires queries on the tinyDB, and updates any variables to these value
        # -->view will then change, as variables are updated

        set_name = self.view_card_set.get()
        # Janky, reverses the padding we had to do earlier
        set_name = set_name[1:-1]

        if set_name == 'Card Set':
            return
        elif set_name == 'All Sets':  # case looking for all packs handled separately
            results = self.card_table.all()
        else:
            acronym = self.acronyms[set_name]
            pack = Query()
            results = self.card_table.search(pack['set'] == acronym)

        total_packs = len(results)
        count = Counter()
        for pack_line in results:
            count.update({k:pack_line[k] for k in self.rarities})

        self.viewed_total_packs.set(total_packs)
        for rarity in self.rarities:
            self.viewed_total_quantities[rarity].set(count[rarity])
            if total_packs == 0:
                self.viewed_mean_quantities[rarity].set('###')
            else:
                self.viewed_mean_quantities[rarity].set('{:.3f}'.format(float(count[rarity])/total_packs))


# GUI class acts as the controller, reacting to changes in the view, and updating the model accordingly
class GUI:
    def __init__(self, master):

        # using configparser, can load in the .ini file
        config = configparser.ConfigParser(allow_no_value=True)
        # Override the default behaviour, which is to strip case
        config.optionxform = str
        config.read('../PacksGUI_conf.ini')
        # can then read in data with things like config['filepaths']['desktop']
        # DEFAULT is a magic-section for ini, which acts as info for any section

        self.model = Model(config)
        self.master = master

        self.main_view = MainView(master)
        self.main_view.pack(padx=20, pady=20)

        self.pack_view = self.main_view.add_view(PackView)
        self.configure_pack_view()

        self.stats_view = self.main_view.add_view(StatsView)
        self.configure_stats_view()

        self.pity_view = self.main_view.add_view(PityView)
        self.layout()

        self.main_view.raise_view(self.pack_view.name)

    # TODO: remove menu bar if not being used
    def layout(self):

        menubar = Menu(self.master)
        menu_file = Menu(menubar, tearoff=0)
        menu_edit = Menu(menubar, tearoff=0)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menu_file.add_command(label="Hey There!", command=lambda:print('hello'))
        root['menu'] = menubar

    def configure_pack_view(self):

        self.pack_view.submit_button.config(command=self.submit)
        self.pack_view.add_scrollers(self.model.quantities)
        self.pack_view.add_set_selector(self.model.card_set, self.model.standard_sets, self.model.wild_sets)
        self.pack_view.note_box.config(textvariable=self.model.notes)
        self.pack_view.not_pack_button.config(command=self.not_pack)
        self.update_image()

    def configure_stats_view(self):
        self.stats_view.add_set_selector(self.model.view_card_set, self.model.standard_sets, self.model.wild_sets)
        self.stats_view.bind_pack_number(self.model.viewed_total_packs)
        self.stats_view.bind_total_cards_numbers(self.model.viewed_total_quantities)
        self.stats_view.bind_mean_cards_numbers(self.model.viewed_mean_quantities)
        pass

    def configure_pity_view(self):
        pass

    def update_image(self):
        #Todo: handle no images found
        self.pack_view.set_image(self.model.image)

    def not_pack(self):
        self.model.next_pack()
        self.update_image()

    def submit(self):
        # evoked by the submit button.
        # The controller has this method such that if the model were to fail, view can be changed
        valid = self.model.is_valid_pack()
        if valid:
            self.model.submit()
            self.update_image()
        else:
            print("Invalid pack")
        pass


# create a root window, set up the GUI in that window, and run
root = Tk()
my_gui = GUI(root)
root.mainloop()

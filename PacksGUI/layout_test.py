#!/usr/bin/env python

# Todo: remove the import * bad habits

# from tkinter import Tk, Menu, PhotoImage, Label, Spinbox, Frame
import configparser
import os
from collections import Counter
from datetime import datetime
from tkinter import *
from tkinter.ttk import *

from PIL import Image, ImageTk
from tinydb import TinyDB, Query

from utils import date_from_filename


class IntScroller(Frame):
    # TODO: test
    # Some simple test to ensure that the textvariable is suitable updated
    # check works for non-default delta, negative delta etc
    # Check bounds are upheld
    def __init__(self, master, **kwargs):
        super().__init__(master)
        # Todo: add some fancy backdrop graphics with a holding label
        # self.backdrop = Label(self)

        # define from_ < to, even for negative increment
        self.min = kwargs.pop('from_', 0)
        self.max = kwargs.pop('to', 5)
        self.increment = kwargs.pop('increment', 1)
        self.var = kwargs.pop('textvariable', IntVar())

        # Defaulting to min, may want to do something funky for negative increment?
        value = kwargs.pop('value', self.min)
        # Clamp value to range
        value = min(self.max, max(value, self.min))
        # TODO: this feels a little funky, having the IntScroller set the value in the model?
        self.var.set(value)

        self.up_button = Button(self, text='\u25b2', command=self.inc, **kwargs)
        self.text = Entry(self, textvariable=self.var, justify=CENTER, **kwargs)
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
        value = self.var.get() + self.increment
        value = min(self.max, max(value, self.min))
        self.var.set(value)

    def dec(self):
        value = self.var.get() - self.increment
        value = min(self.max, max(value, self.min))
        self.var.set(value)


class Hearthstone:

    # Abstract class intended to contain hearthstone properties that many classes need access to
    # Basically working as a container for constants about the game itself
    # --> rarities is a great example of this, now accessable through Hearthstone.rarities
    rarities = ['common', 'rare', 'epic', 'legendary',
                'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']
    default_pack = {'common': 4, 'rare': 1, 'epic': 0, 'legendary': 0,
                    'golden_common': 0, 'golden_rare': 0, 'golden_epic': 0, 'golden_legendary': 0}
    disenchant_values = {'common': 5, 'rare': 20, 'epic': 100, 'legendary': 400,
                         'golden_common': 50, 'golden_rare': 100, 'golden_epic':400, 'golden_legendary':1600}
    enchant_values = {'common': 40, 'rare': 100, 'epic': 400, 'legendary': 1600,
                      'golden_common': 400, 'golden_rare': 800, 'golden_epic': 1600, 'golden_legendary': 3200}
    # TODO: perhaps card_sets belongs in here too, something like Hearthstone.standard_sets / wild_set / all_sets


# Todo: Probably want a rename, given we aren't assuming it's a pack any more
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


class View(Frame):
    """ Abstract View class from which other views inherit """

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = None
        self.subpages = {}
        self.subpage_buttons = []

        # Must be set by subclasses
        self.subpage_frame = None
        self.subpage_button_frame = None
        self.active_subpage = None

    # TODO: test
    # Do we test on the base class, or on a derivative of it?
    # Subpage is returned
    # Ensure button does things?

    # TODO: from trying to envisage tests, this seems to do a LOT for one method
    # --> is this a problem?
    def add_subpage(self, constructor):
        if not self.active_subpage:
            # subpage variable is needed, if none, supply one
            self.active_subpage = StringVar()
        # We assume these have been set by now
        subpage = constructor(self.subpage_frame)
        self.subpages[subpage.name] = subpage
        subpage.grid(row=0, column=0, sticky=NSEW)
        self.subpage_frame.columnconfigure(0, weight=1)
        # adds button to nav bar that will raise that view
        button = Button(self.subpage_button_frame, text=subpage.name, command=lambda: self.raise_view(subpage.name))
        btn_idx = len(self.subpage_buttons)
        button.grid(row=0, column=btn_idx, padx=20, sticky=NSEW)
        self.subpage_buttons.append(button)
        self.columnconfigure(btn_idx, weight=1)

        self.active_subpage.set(subpage.name)
        return subpage

    # TODO: test?
    # hard to test that the page is actually raised, unless we can get some height info somehow
    # can definitely test the variable is updated correctly
    def raise_view(self, subpage_name):
        frame = self.subpages[subpage_name]
        self.active_subpage.set(subpage_name)
        frame.tkraise()

    # TODO: test
    # Will be tested in the background of testing the raise funcitons & things
    def bind_subpage_variable(self, subpage_var):
        self.active_subpage = subpage_var


# Displays pity timers
# Should be on a per set basis, with dropdown
# Should also have some form of suggestion for pack to buy
# Perhaps even a top3 list of exciting timers that are nearly up
# --> Obvs prioritising legendary over epic, but would rank Leg in 2 > Epic in 1 eg.
# --> Simple heuristic would be #left/#timer, so if time is 25, and this'd be pack 20, 20/25
# --> Compare heuristics and show info about the highest scoring
# -----> Which set, what you can expect, how many 'til guarantee
class PityView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Pity'


# A basic statistics page, perhaps later will include some pretty graphs
class StatsView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Stats'

        self.set_selector = None
        total_packs_label = Label(self, text='Total packs opened:')
        total_packs_label.grid(row=1, column=0, columnspan=2, sticky=E)
        self.total_packs_number = Label(self, text='Not set')
        self.total_packs_number.grid(row=1, column=2, columnspan=2, sticky=W)

        self.total_numbers = {}
        self.mean_numbers = {}

        for idx, rarity in enumerate(Hearthstone.rarities):
            boundary = Frame(self)
            rarity_label = Label(boundary, text=rarity)
            rarity_label.pack()
            total_number = Label(boundary, text='#')
            total_number.pack(pady=10)
            mean_number = Label(boundary, text='#')
            mean_number.pack()
            # Grid into a 4 wide array
            boundary.grid(row=2+int(idx/4), column=idx % 4, padx=20, pady=30)

            self.total_numbers.update({rarity: total_number})
            self.mean_numbers.update({rarity: mean_number})

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    # TODO: test
    # Ensure the set selector is present (children of View list ?)
    # Verify the selector options are correct
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

    # TODO: test
    # set the variable, change it, and then see if the label is updated?
    # Should be able to pull the text from the Label, presumably
    def bind_pack_number(self, variable):
        # binds the variable as the value for the pack number display
        self.total_packs_number.config(textvariable=variable)

    # TODO: test
    # same as pack_number
    def bind_total_cards_numbers(self, variable_dict):
        for rarity in Hearthstone.rarities:
            self.total_numbers[rarity].config(textvariable=variable_dict[rarity])

    # TODO: test
    # again, same as above 2
    def bind_mean_cards_numbers(self, variable_dict):
        for rarity in Hearthstone.rarities:
            self.mean_numbers[rarity].config(textvariable=variable_dict[rarity])


# Todo: rename to something like 'Image storing', given does more than packs now
# A view will sit within the app, bordered by padding, with navigation above
class PackView(View):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.name = 'Pack'
        self.subpages = {}
        self.subpage_buttons = []
        self.active_subpage = None
        self.image = None

        self.image_frame = Label(self)
        image = Image.new('RGB', (1920, 1080))
        self.set_image(image)
        self.image_frame.grid(row=0, column=0, columnspan=4, pady=20)

        self.subpage_button_frame = Frame(self)
        self.subpage_button_frame.grid(row=1, column=0, columnspan=4)
        self.subpage_frame = Frame(self)
        self.subpage_frame.grid(row=2, column=0, columnspan=4, sticky=NSEW)

        self.submit_button = Button(self, text="Submit")
        self.submit_button.grid(row=6, column=0, columnspan=3, sticky=NSEW, pady=20, padx=10)
        self.not_pack_button = Button(self, text="Not Pack")
        self.not_pack_button.grid(row=6, column=3, columnspan=1, sticky=NSEW, pady=20, padx=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    # Todo: test?
    # check is sized correctly?
    def set_image(self, image):
        # takes the result of Image.open, and pushes result to the image frame
        sized_image = image.resize((700, 394), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(sized_image)
        self.image_frame.config(image=photo)
        self.image_frame.image = photo


class PackMiniView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        # Todo: perhaps split 'name' into internal moniker, to match .ini, and display name, for buttons
        self.name = 'Packs'

        self.rarity_values = {}
        self.rarity_scrollers = {}

        self.notes_label = Label(self, text="Notes:")
        self.notes_label.grid(row=3, column=0, columnspan=4)
        self.note_box = Entry(self, justify=CENTER, width=60)
        self.note_box.grid(row=4, column=0, columnspan=4)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    # TODO: test
    # verify scrollvars are unpacked correctly
    def add_scrollers(self, scrollvars):
        for rarity in Hearthstone.rarities:
            self.rarity_scrollers.update({rarity: IntScroller(self, textvariable=scrollvars[rarity], width=2)})

        self.rarity_scrollers['common'].grid(row=0, column=0, pady=10)
        self.rarity_scrollers['rare'].grid(row=0, column=1, pady=10)
        self.rarity_scrollers['epic'].grid(row=0, column=2, pady=10)
        self.rarity_scrollers['legendary'].grid(row=0, column=3, pady=10)

        self.rarity_scrollers['golden_common'].grid(row=1, column=0, pady=10)
        self.rarity_scrollers['golden_rare'].grid(row=1, column=1, pady=10)
        self.rarity_scrollers['golden_epic'].grid(row=1, column=2, pady=10)
        self.rarity_scrollers['golden_legendary'].grid(row=1, column=3, pady=10)

    # TODO: test
    # Set selector added, options correct, bound to variable right
    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", *standard, *wild)
        set_selector['menu'].insert_separator(len(standard))
        set_selector.grid(row=2, column=1, columnspan=2, pady=20)
        self.set_selector = set_selector


# Note: arena rewards got a rework Aug 11
# For presentation, will need separate logic before + after

class ArenaMiniView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Arena Rewards'

        self.rarity_values = {}
        self.rarity_scrollers = {}


class SeasonMiniView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Season End'

        self.max_rank_Label = Label(self, text='Highest Rank Achieved:')
        self.end_rank_Label = Label(self, text='End of Season Rank:')
        # Todo: Are we using IntScrollers for this, or some other solution?
        # End of season Mini view is unique in its submit functionality:
        # --> As max/end information is not both known for every image, the submission only
        # --> 'updates' the database, not overriding what is already set
        # --> As such it is paramount that the two variables be set to None or some other
        # --> Sentinel value, once the submit button is pressed and processed

        # Todo: Add a month dropdown, which defaults to the month guessed by the filename
        # --> Should never have to use it, but it's a nice option to have in case of failure

        self.max_rank_entry = None
        self.end_rank_entry = None

        self.max_rank_Label.grid(row=0, column=0, sticky=E)
        self.end_rank_Label.grid(row=1, column=0, sticky=E)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


class OtherMiniView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Other'
        self.folder_selection = None
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    # TODO: set selector is a little bit WET, may want a very minor refactor
    def add_selector(self, variable, *options):
        # Folder selection is a dropdown of any output folder not in ['packs', 'arena', 'rewards']
        # Selection of a folder, and hitting save just auto-routes the image to the correct folder
        # Config is used by the model to determine any sub-folders by year/month
        self.folder_selection = OptionMenu(self, variable, "Folder", *options)
        self.folder_selection.grid()


# Main GUI view, mainly as a container so the subpage methods can be used for the separate views
class MainView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.views = {}

        self.subpage_button_frame = Frame(self, height=100)
        self.subpage_button_frame.grid(row=0, column=0)
        self.subpage_frame = Frame(self)
        self.subpage_frame.grid(row=1, column=0)


# TODO: opening of TinyDB is done manually in the 3 places it occurs
# Investigate if this can be made DRY

# TODO: Model is currently a big blob, could really be split up a little
# designed to hold the back-bone logic of the whole shebang

# Controller passes a config, from which the model extracts a lot of info
# model will then go and grab the files it needs to hold
class Model:

    # TODO: test
    # config parsed and things are extracted
    # Tinydb data is extracted correctly
    # Verify all the 'Var's are present and correct?
    # Check trace_variable is bound correctly - could overload the self.extract_data with a testing function
    def __init__(self, config):
        self.config = config

        self.db_file = self.config['filepaths']['tinydb']

        self.packs = []
        self.current_pack = None

        self.standard_sets = config['sets_standard']
        self.wild_sets = config['sets_wild']

        self.acronyms = dict(config['sets_wild'].items())
        self.acronyms.update(config['sets_standard'].items())

        self.image = None

        # ~~ Image saving view ~~
        # StringVar will hold the name of the current subpage
        self.current_subpage = StringVar()

        # ~~ Card pack subpage ~~
        self.quantities = {}
        self.notes = StringVar()  # defaults to empty string
        self.card_set = StringVar()

        # ~~ Arena subpage ~~
        # Todo: may want to group rewards up so call call model.rewards.gold for example
        self.reward_quantities = {}
        self.reward_dust = IntVar()
        self.reward_gold = IntVar()
        self.reward_packs = IntVar()
        self.arena_wins = IntVar()
        self.arena_losses = IntVar()

        # ~~ End of Season subpage ~~
        self.end_rank =  IntVar()
        self.max_rank = IntVar()

        # ~~ Stats view ~~
        self.viewed_total_quantities = {}  # quantities for each rarity, for stats view
        self.viewed_mean_quantities = {}
        self.view_card_set = StringVar()  # card set, as deemed by stats view
        self.viewed_total_packs = IntVar()  # packs for stats view card set

        for rarity in Hearthstone.rarities:
            # rarities are stored in IntVars so view can auto-update
            self.quantities.update({rarity: IntVar()})
            # viewed quantities are linked to being the # of that rarity in DB, for view_card_set
            self.viewed_total_quantities.update({rarity: IntVar()})
            self.viewed_mean_quantities.update({rarity: StringVar()})

        # Any time you change which card set you're viewing, reloads data
        self.view_card_set.trace_variable('w', self.extract_data)

        self.find_images()
        self.next_pack()

        pass

    # TODO: test
    # Ensure functions correctly - doesn't false-match, gets 'em all
    # Verify the list is sorted correctly
    def find_images(self):
        """Finds all the screenshots on the desktop that might be packs, and stores them"""
        desktop_path = self.config['filepaths']['desktop']
        for file in os.listdir(desktop_path):
            if file.endswith(".png") and file.startswith("Hearthstone"):
                # Todo: signature of CardPack might change
                self.packs.append(CardPack(file, desktop_path))
        # reverse so pop can be used to get in order
        self.packs.sort(key=lambda pack: pack.sortkey, reverse=True)

    # TODO: test
    # moves to next pack
    # handles the no-more-packs situation correctly
    def next_pack(self):
        # closing images once we're done with them
        if self.current_pack:
            self.image.close()
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

    # TODO: test
    # ensure that after this is run, any contents are wiped
    # Ensure defaults are in correct boxes
    def reset_variables(self):
        # Resetting some variables back to default values
        for rarity in Hearthstone.rarities:
            # Todo: default pack, move to Hearthstone class?
            # get default contents of pack, assumes 0 of any not specified
            default = Hearthstone.default_pack[rarity]
            self.quantities[rarity].set(default)
        self.notes.set('')
        # Note: self.card_set is not reset, assumes multiple packs of same set most likely

    # TODO: this model-level validation is the last bastion
    # --> need not be the only one, if the Controller can do it, might be worth
    def is_valid_pack(self):
        # Todo: ideally we'd throw the user some information as to why it fails
        # --> Not core requirement, I will know what's up

        if (self.card_set.get() not in self.standard_sets) and \
                (self.card_set.get() not in self.wild_sets):
            # CARD SET NOT SELECTED
            return False

        total_cards = sum([val.get() for val in self.quantities.values()])
        if total_cards != 5:
            #  NOT ENOUGH CARDS
            return False

        if self.quantities['common'].get() == 5:
            # ALL COMMONS NOT VALID
            return False

        if (self.quantities['legendary'].get() + self.quantities['golden_epic'].get() +
                self.quantities['golden_legendary'].get() > 0) and (self.notes.get() == ''):
            # NOTEWORTHY CARD NOT NOTED
            return False

        return True

    # TODO: test
    # TinyDB file should be updated with the pack data
    # TinyDB should be using the correct table for the data
    # image should be moved to the correct folder, according to the word of the config
    # directories should be made if not present

    # TODO: storing the data to the database, and moving the file
    # should be separate both from each other and from the main 'submit' method
    # imagine we were moving both into web-based databasing

    # Should the correct submission process be the responsibility of Model or Controller?
    def submit(self):
        # commits pack data to tinydb file
        # makes no attempt to validate, assumes you have sorted this

        # Todo: somehow check the current subpage, and modify behaviour accordingly

        with TinyDB(self.db_file) as db:
            card_table = db.table('card_data')
            card_table.insert({
                'date': self.current_pack.sortkey,
                **{rarity: self.quantities[rarity].get() for rarity in Hearthstone.rarities},
                'notes': self.notes.get(), 'set': self.acronyms[self.card_set.get()]
            })

        pack_folder = self.config['output']['packs']
        dest_folder = os.path.join(pack_folder, str(self.current_pack.date.year))

        # check year folder exists
        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)

        destination = os.path.join(dest_folder, self.current_pack.image_name)
        # Todo: for testing, file movement is disabled
        # shutil.move(self.current_pack.full_path, destination)

        # TODO: check this is needed
        self.extract_data()

        self.next_pack()

    # TODO: test
    # pack is not moved, and the next image is loaded in
    # Really weak test, but especially if this gets more complex, would be nice to be sure
    def not_pack(self):
        # "Not pack" will likely be removed and made into "skip".
        # Images for things other than packs will have a sub page of the storage screen
        self.next_pack()

    # Another alias. Can be cleaned up when refactoring if needed
    skip_image = next_pack

    # TODO: test
    # When passed a set name, ensure it pulls back only for that set
    # Handles no data being found for the given set sensibly
    # Handles case for no option selected, 'Card Set'
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
            with TinyDB(self.db_file) as db:
                card_table = db.table('card_data')
                results = card_table.all()
        else:
            acronym = self.acronyms[set_name]
            pack = Query()
            with TinyDB(self.db_file) as db:
                card_table = db.table('card_data')
                results = card_table.search(pack['set'] == acronym)

        total_packs = len(results)
        count = Counter()
        for pack_line in results:
            count.update({k: pack_line[k] for k in Hearthstone.rarities})

        self.viewed_total_packs.set(total_packs)
        for rarity in Hearthstone.rarities:
            self.viewed_total_quantities[rarity].set(count[rarity])
            if total_packs == 0:
                self.viewed_mean_quantities[rarity].set('###')
            else:
                self.viewed_mean_quantities[rarity].set('{:.3f}'.format(float(count[rarity])/total_packs))


# GUI class acts as the controller, reacting to changes in the view, and updating the model accordingly
class GUI:
    def __init__(self, master, config):

        self.model = Model(config)
        self.master = master

        self.main_view = MainView(master)
        self.main_view.pack(padx=20, pady=20)

        self.pack_view = self.main_view.add_subpage(PackView)
        self.configure_pack_view()

        self.stats_view = self.main_view.add_subpage(StatsView)
        self.configure_stats_view()

        self.pity_view = self.main_view.add_subpage(PityView)
        self.layout()

        self.main_view.raise_view(self.pack_view.name)

    # TODO: remove menu bar if not being used
    def layout(self):

        menubar = Menu(self.master)
        menu_file = Menu(menubar, tearoff=0)
        menu_edit = Menu(menubar, tearoff=0)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menu_file.add_command(label="Hey There!", command=lambda: print('hello'))
        self.master['menu'] = menubar

    def configure_pack_view(self):
        # ~~ Main pack view ~~
        self.pack_view.submit_button.config(command=self.submit)
        # Self methods, rather than model so we can hook in to update image
        # Todo: should we hook the image update in as a variable binging?
        self.pack_view.not_pack_button.config(command=self.not_pack)
        self.update_image()
        self.pack_view.bind_subpage_variable(self.model.current_subpage)

        # ~~ Pack subpage ~~
        pack_subpage = self.pack_view.add_subpage(PackMiniView)
        pack_subpage.add_scrollers(self.model.quantities)
        pack_subpage.add_set_selector(self.model.card_set, self.model.standard_sets, self.model.wild_sets)
        pack_subpage.note_box.config(textvariable=self.model.notes)

        # ~~ Arena subpage ~~
        self.pack_view.add_subpage(ArenaMiniView)

        # ~~ End of Season subpage ~~
        season_subpage = self.pack_view.add_subpage(SeasonMiniView)

        other_subpage = self.pack_view.add_subpage(OtherMiniView)
        # Todo: work out where folders are read from config and passed here
        # other_subpage.add_selector()

        self.pack_view.raise_view(pack_subpage.name)

    def configure_stats_view(self):
        self.stats_view.add_set_selector(self.model.view_card_set, self.model.standard_sets, self.model.wild_sets)
        self.stats_view.bind_pack_number(self.model.viewed_total_packs)
        self.stats_view.bind_total_cards_numbers(self.model.viewed_total_quantities)
        self.stats_view.bind_mean_cards_numbers(self.model.viewed_mean_quantities)
        pass

    def configure_pity_view(self):
        pass

    def update_image(self):
        try:
            self.pack_view.set_image(self.model.image)
        except AttributeError: # Handling no image found, generating a black image for now
            self.pack_view.set_image(Image.new('RGB', (1920, 1080)))

    # TODO: probably want a rename for this, given it's now going to be not pack, not arena, not EoS etc
    def not_pack(self):
        self.model.next_pack()
        self.update_image()

    def submit(self):

        # Todo: this needs to be revamped
        # --> Validation is only needed in this form for a pack submission
        # --> Can use model variable to determine which subpage we are on
        # --> Can process subpage validation separately

        # Todo: is the logic for this being in the controller still valid, or should it move?

        # evoked by the submit button.
        # The controller has this method such that if the model were to fail, view can be changed
        valid = self.model.is_valid_pack()
        if valid:
            self.model.submit()
            self.update_image()
        else:
            print("Invalid pack")
        pass


# TODO: before changing things that start actually interacting with the filesystem, need some tests
# Tests SHOULD be able to load in just the model, and effectively simulate a user
# Button presses on the interface should only ever be effecting the model
# --> not_pack does call a GUI method, for updating image, not a huge sticking point
# Tests should be able to see that the program moves files as expected, and then move 'em back
# Probably just a single image
# Random tests can make up the filename, and meta data, and watch as the system stores it
# Test different config options all work
# Test that the database is correctly updated for the submissions
# Check data verification works

# Todo: one test per source file seems like a standard practice
# One file per source file, with a test set per source class
# --> Some other nest another test class inside, for each method, probs overkill here, but maybe
# --> If tests need setup or 2 types, 2 classes works better
# Shouldn't be too hard to mirror refactoring that way, just got to check top level class contents of the two files
# Majority of tests will be for model, presumably

# https://github.com/sloria/TextBlob/tree/dev/textblob
# random repo to see some style, uses Nose, but close enough
if __name__ == '__main__':
    # create a root window, set up the GUI in that window, and run
    root = Tk()

    # Todo: when packaged up, have a method that sets the config file
    # --> all things that use config would have to be made after this, or updated :/


    # using configparser, can load in the .ini file
    configuration = configparser.ConfigParser(allow_no_value=True)
    # Override the default behaviour, which is to strip case
    configuration.optionxform = str
    configuration.read('../PacksGUI_conf.ini')
    # can then read in data with things like config['filepaths']['desktop']
    # DEFAULT is a magic-section for ini, which acts as info for any section
    my_gui = GUI(root, configuration)
    root.mainloop()

from tkinter import Label, Entry, CENTER, E
from tkinter.ttk import OptionMenu

from Hearthstone import Hearthstone
from IntScroller import IntScroller
from FullViews import View


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

    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", *standard, *wild)
        set_selector['menu'].insert_separator(len(standard))
        set_selector.grid(row=2, column=1, columnspan=2, pady=20)
        self.set_selector = set_selector


class ArenaMiniView(View):
    # Note: arena rewards got a rework Aug 11
    # For presentation, will need separate logic before + after
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



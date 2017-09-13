from tkinter import Label, Entry, CENTER, E, Frame, NSEW, LabelFrame, Tk, StringVar, RIDGE
from tkinter.ttk import OptionMenu

from Hearthstone import Hearthstone
from IntScroller import IntScroller
from FullViews import View
from utils import optionmenu_patch


class PackMiniView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        # Todo: perhaps split 'name' into internal moniker, to match .ini, and display name, for buttons
        self.name = 'Packs'

        self.rarity_values = {}
        self.rarity_scrollers = {}
        self.set_selector = None
        self.virtual_cursor = 0  # Virtual cursor, for entering values into scrollers with keyboard

        self.notes_label = Label(self, text="Notes:")
        self.notes_label.grid(row=3, column=0, columnspan=4)
        self.note_box = Entry(self, justify=CENTER, width=60)
        self.note_box.grid(row=4, column=0, columnspan=4)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        # Adding a 5th column, for push scrollers left, little janky but looks acceptable
        # self.columnconfigure(4, weight=1)

    def add_scrollers(self, scrollvars):
        rarity_names = {'common': 'Common', 'rare': 'Rare', 'epic': 'Epic', 'legendary': 'Legendary',
                        'golden_common': 'Golden\nCommon', 'golden_rare': 'Golden\nRare',
                        'golden_epic': 'Golden\nEpic', 'golden_legendary': 'Golden\nLegendary'}
        for rarity in Hearthstone.rarities:
            self.rarity_scrollers.update({rarity: IntScroller(self, textvariable=scrollvars[rarity],
                                                              label=rarity_names[rarity], width=2)})

        self.rarity_scrollers['common'].grid(row=0, column=0, pady=10)
        self.rarity_scrollers['rare'].grid(row=0, column=1, pady=10)
        self.rarity_scrollers['epic'].grid(row=0, column=2, pady=10)
        self.rarity_scrollers['legendary'].grid(row=0, column=3, pady=10)

        self.rarity_scrollers['golden_common'].grid(row=1, column=0, pady=10)
        self.rarity_scrollers['golden_rare'].grid(row=1, column=1, pady=10)
        self.rarity_scrollers['golden_epic'].grid(row=1, column=2, pady=10)
        self.rarity_scrollers['golden_legendary'].grid(row=1, column=3, pady=10)

        # activate the first scroller
        self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].activate()

    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", *standard, *wild)
        # Fix for multi-menu bug
        optionmenu_patch(set_selector, model_variable)
        set_selector['menu'].insert_separator(len(standard))
        set_selector.grid(row=2, column=1, columnspan=2, pady=20)
        self.set_selector = set_selector

    def key_pressed(self, event):

        valid_digits = ('0', '1', '2', '3', '4', '5')

        enter = '\r'
        backspace = '\x08'
        escape = '\x1b'

        key = event.char

        if key in valid_digits:  # Valid values get passed to current intscroller
            current_scroller = self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]]
            current_scroller.set(int(key))
            current_scroller.deactivate()
            self.virtual_cursor = (self.virtual_cursor + 1) % len(Hearthstone.rarities)
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].activate()
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].text.focus_set()
        elif key is escape:  # Esc returns to default pack
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].deactivate()
            for rarity in Hearthstone.rarities:
                self.rarity_scrollers[rarity].set(Hearthstone.default_pack[rarity])
            self.virtual_cursor = 0
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].activate()
        elif key is backspace:  # Backspace moves back, and removes value
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].deactivate()
            self.virtual_cursor = (self.virtual_cursor - 1) % len(Hearthstone.rarities)
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].set(0)
            self.rarity_scrollers[Hearthstone.rarities[self.virtual_cursor]].activate()


class ArenaMiniView(View):
    # Note: arena rewards got a rework Aug 11
    # For presentation, will need separate logic before + after
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Arena Rewards'

        self.subpage_frame = Frame(self)
        self.subpage_frame.grid(row=0, column=0, sticky=NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.page_one = self.add_subpage(ArenaPageOne, make_button=False)
        self.page_two = self.add_subpage(ArenaPageTwo, make_button=False)

        self.raise_view(self.page_one.name)


class ArenaPageOne(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Arena1'

    def add_win_selector(self, model_variable):
        pass

    def add_loss_selector(self, model_variable):
        pass

    def add_class_selector(self, model_variable):
        pass


class ArenaPageTwo(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Arena2'


        # self.reward_boxes = [RewardBox(self) for i in range(5)]
        # pack reward is reward_boxes[0], kept at start
        box1 = RewardBox(self)
        box1.grid(row=0, column=0, sticky=NSEW)
        box2 = RewardBox(self)
        box2.grid(row=0, column=1, sticky=NSEW)
        box2.add_reward_dropdown(StringVar(), '2', ['1', '2', '3', '4', '5'])
        box3 = RewardBox(self)
        box3.grid(row=0, column=2, sticky=NSEW)
        box4 = RewardBox(self)
        box4.grid(row=1, column=0, sticky=NSEW)

        filler_box = RewardBox(self)
        filler_box.grid(row=1, column=1, sticky=NSEW)

        box5 = RewardBox(self)
        box5.grid(row=1, column=2, sticky=NSEW)
        box5.add_reward_dropdown(StringVar(), '5', ['1', '2', '3', '4', '5'])

        for i in range(0, 3):
            self.columnconfigure(i, weight=1)
        for i in range(0, 2):
            self.rowconfigure(i, weight=1)


    def set_number_wins(self, wins):
        # Do something with the interface, depending on the number of wins
        # Could remove the extra boxes, could just disable them

        number_boxes = Hearthstone.num_arena_rewards[wins]


        pass


class RewardBox(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Reward Box'

        self.reward_dropdown = None
        edge_color = '#2d2d89'
        self.config(highlightbackground=edge_color, highlightthickness=1)

        self.reward_entry_frame = Frame(self)
        self.reward_entry_frame.grid(row=1, column=0)
        label = Label(self.reward_entry_frame, text='Hello')
        label.pack()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def add_reward_dropdown(self, model_variable, default, options):
        self.reward_dropdown = OptionMenu(self, model_variable, default, *options)
        # Using patch to fix bug with multiple menus
        optionmenu_patch(self.reward_dropdown, model_variable)
        self.reward_dropdown.grid(row=0, column=0)


class CardRewardEntry(View):
    pass


class DustRewardEntry(View):
    pass


class GoldRewardEntry(View):
    pass


class PackRewardEntry(View):
    pass


        # Arena MiniView has 2 stages, corresponding to the 2 images each arena run gives
        # Each stage will likely be a further subpage, but without control buttons
        # First image:
        # End screen, #wins, #loses, class
        # Win spinbox / IntScroller, 0-12
        # Loses spinbox / IntScroller, 0-3 - verification, no 12-3 allow eg 0-2, for retires


        # Second image:
        # Rewards, predetermined number of boxes, some rewards predetermined
        # Gold: spinbox / IntScroller between known min-max
        # --> How do we handle the 12 wins double guaranteed gold? Will just be clear from default value?
        # Dust: spinbox / IntScroller between known min-max
        # Card: dropdown box between rarities
        # Pack: Selector for set (defaults to most recent expansion, last in standard)

        # Each of these box content selectors will slot into the second image, perhaps separate View objects
        # Need selector for type, for the Random rewards (dropdown contents known)
        # Could have all the possible box content views stacked, with dropdown raising one of them


        # Do we want to lockout the Packs, EoS, Other mini views until we have both images stored?
        # How would we even do this?
        # --> need a ref to PacksView, which controls those buttons
        # --> something like master.disable_buttons(), master.enable_buttons()
        # Also useful for the EoS minipage, which is many images


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

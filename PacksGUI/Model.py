import os
from collections import Counter
from tkinter import StringVar, IntVar

from PIL import Image
from tinydb import TinyDB, Query

from CardPack import CardPack
from Hearthstone import Hearthstone


# TODO: opening of TinyDB is done manually in the 3 places it occurs
# Investigate if this can be made DRY

# TODO: Model is currently a big blob, could really be split up a little
# designed to hold the back-bone logic of the whole shebang
class Model:

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

    def find_images(self):
        """Finds all the screenshots on the desktop that might be packs, and stores them"""
        desktop_path = self.config['filepaths']['desktop']
        for file in os.listdir(desktop_path):
            if file.endswith(".png") and file.startswith("Hearthstone"):
                # Todo: signature of CardPack might change
                self.packs.append(CardPack(file, desktop_path))
        # reverse so pop can be used to get in order
        self.packs.sort(key=lambda pack: pack.sortkey, reverse=True)

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

    def reset_variables(self):
        # Resetting some variables back to default values
        for rarity in Hearthstone.rarities:
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

        # Todo: check the current subpage, and modify behaviour accordingly

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

    def not_pack(self):
        # "Not pack" will likely be removed and made into "skip".
        # Images for things other than packs will have a sub page of the storage screen
        self.next_pack()

    # Another alias. Can be cleaned up when refactoring if needed
    skip_image = next_pack

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



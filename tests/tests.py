import os
import tempfile
import tkinter
import tkinter.ttk
import unittest
from configparser import ConfigParser
from datetime import datetime

from PIL import Image
from tinydb import TinyDB

import CardPack
from IntScroller import IntScroller
import MiniViews
import Model
import FullViews
import layout_test
from Hearthstone import Hearthstone


# ~~ IMPORTANT ~~
# This is a large file for tests, prior to the refactoring
# Tests should be placed into files that match source files

# Make sure you aren't pitching test code vs real code for no reason
# tests where it's easy to construct, but hard for the real code to deconstruct are great though

class TestIntScroller(unittest.TestCase):

    def setUp(self):
        self.root = tkinter.Tk()

    def test_allotted_integer_variable_type(self):
        scroller = IntScroller(self.root)
        variable = scroller.var
        self.assertIsInstance(variable, tkinter.IntVar)

    def test_default_value(self):
        expected_value = 3
        scroller = IntScroller(self.root, value=expected_value, from_=0, to=5)
        value = scroller.var.get()
        self.assertEqual(value, expected_value)

    def test_default_above_range(self):
        # Value should be clamped to the range, regardless of erroneous default
        to_value = 5
        scroller = IntScroller(self.root, value=to_value + 1, from_=0, to=to_value, increment=1)
        value = scroller.var.get()
        self.assertEqual(value, to_value)

    def test_default_below_range(self):
        from_value = 0
        scroller = IntScroller(self.root, value=from_value - 1, from_=from_value, to=5, increment=1)
        value = scroller.var.get()
        self.assertEqual(value, from_value)

    def test_increment(self):
        increment = 1
        scroller = IntScroller(self.root, from_=0, increment=1, to=5, value=3)
        initial_value = scroller.var.get()
        scroller.inc()
        result_value = scroller.var.get()
        self.assertEqual(result_value, initial_value + increment)

    def test_decrement(self):
        increment = 1
        scroller = IntScroller(self.root, from_=0, increment=1, to=5, value=3)
        initial_value = scroller.var.get()
        scroller.dec()
        result_value = scroller.var.get()
        self.assertEqual(result_value, initial_value - increment)

    def test_increment_above_bounds(self):
        to_value = 5
        scroller = IntScroller(self.root, from_=0, to=to_value, value=to_value, increment=1)
        scroller.inc()
        self.assertEqual(scroller.var.get(), to_value)

    def test_decrement_below_bounds(self):
        from_value = 0
        scroller = IntScroller(self.root, from_=from_value, to=5, value=from_value, increment=1)
        scroller.dec()
        self.assertEqual(scroller.var.get(), from_value)

    def test_negative_step_increment(self):
        # In use cases where Up arrow should decrease the number on the IntScroller
        # Example case would be for end of season rank, Rank 1 'higher' than Rank 25
        increment = -1
        scroller = IntScroller(self.root, from_=0, increment=increment, to=5, value=3)
        initial_value = scroller.var.get()
        scroller.inc()
        result_value = scroller.var.get()
        self.assertEqual(result_value, initial_value + increment)

    def test_negative_step_decrement(self):
        increment = -1
        scroller = IntScroller(self.root, from_=0, increment=increment, to=5, value=3)
        initial_value = scroller.var.get()
        scroller.dec()
        result_value = scroller.var.get()
        self.assertEqual(result_value, initial_value - increment)

    def test_negative_increment_below_bounds(self):
        from_value = 0
        scroller = IntScroller(self.root, from_=from_value, to=5, value=from_value, increment=-1)
        scroller.inc()
        self.assertEqual(scroller.var.get(), from_value)

    def test_negative_decrement_above_bounds(self):
        to_value = 5
        scroller = IntScroller(self.root, from_=0, to=to_value, value=to_value, increment=-1)
        scroller.dec()
        self.assertEqual(scroller.var.get(), to_value)

    def test_creates_label(self):
        scroller = IntScroller(self.root, label='Label')
        self.assertIsInstance(scroller.label, tkinter.Label)

    def test_ignore_no_label(self):
        scroller = IntScroller(self.root)
        self.assertIsNone(scroller.label)


class TestCardPack(unittest.TestCase):

    def test_extracts_time_and_date(self):
        image_name = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'
        folder_path = 'C:/'

        card_pack = CardPack.CardPack(image_name, folder_path)

        self.assertEqual(card_pack.image_name, image_name)
        self.assertEqual(card_pack.full_path, 'C:/Hearthstone_Screenshot_1.2.2014.03.04.05.png')
        self.assertEqual(card_pack.sortkey, '2014/01/02/03/04/05')
        self.assertEqual(card_pack.date_time, datetime(2014, 1, 2, 3, 4, 5))


class TestView(unittest.TestCase):

    def named_generator(self, name):
        class NamedSubpage(tkinter.Frame):
            def __init__(self, master):
                super().__init__(master)
                self.name = name
        return NamedSubpage

    def setUp(self):
        root = tkinter.Tk()
        self.view = FullViews.View(root)

        # Having to add in the two frames, which would be done by child class
        self.subpage_frame = tkinter.Frame(root)
        self.view.subpage_frame = self.subpage_frame
        subpage_button_frame = tkinter.Frame(root)
        self.view.subpage_button_frame = subpage_button_frame

        # We will often need only 1 subpage, generating it here
        self.TestSubpage = self.named_generator('TEST')

    def test_provided_subpage_variable(self):
        # Adding a subpage should require variable
        self.view.add_subpage(self.TestSubpage)
        self.assertIsInstance(self.view.active_subpage, tkinter.StringVar)

    def test_binds_subpage_variable(self):
        subpage_variable = tkinter.StringVar()
        self.view.bind_subpage_variable(subpage_variable)
        self.assertIs(self.view.active_subpage, subpage_variable)

    def test_preserves_set_variable(self):
        subpage_variable = tkinter.StringVar()
        self.view.bind_subpage_variable(subpage_variable)
        self.view.add_subpage(self.TestSubpage)
        self.assertIs(self.view.active_subpage, subpage_variable)

    def test_current_subpage_variable_set(self):
        subpage_variable = tkinter.StringVar()
        self.view.bind_subpage_variable(subpage_variable)
        subpage_name = 'TestName'
        self.view.add_subpage(self.named_generator(subpage_name))
        self.assertEqual(self.view.active_subpage.get(), subpage_name)

    def test_returns_subpage_from_constructor(self):
        self.assertIsInstance(self.view.add_subpage(self.TestSubpage), self.TestSubpage)

    def test_stores_subpage_to_dict(self):
        subpage = self.view.add_subpage(self.TestSubpage)
        self.assertIs(self.view.subpages[subpage.name], subpage)

    def test_raise_button_bound(self):

        self.given_name = None

        # Creating a mock raise function, which just sets given_name to the called subpage
        def mock_raise(subpage_name):
            self.given_name = subpage_name
        # Inject new mock raise
        self.view.raise_view = mock_raise
        # Create subpage and add to view
        subpage_name = 'TestName'
        self.view.add_subpage(self.named_generator(subpage_name))
        # Invoke the newly added subpage button
        self.view.subpage_buttons[0].invoke()
        # Test whether our mock raise has been called
        self.assertEqual(self.given_name, subpage_name)

    def test_stores_raise_button(self):
        self.view.add_subpage(self.TestSubpage)
        # using ttk buttons for style, test uses correct class
        self.assertIsInstance(self.view.subpage_buttons[-1], tkinter.ttk.Button)

    def test_new_views_placed_highest(self):
        # Using a custom named subpage, to demonstrate different objects
        self.view.add_subpage(self.TestSubpage)
        newest_subpage = self.view.add_subpage(self.named_generator('Newest'))
        # order returned is bottom to top
        frame_children = self.subpage_frame.winfo_children()
        self.assertIs(frame_children[-1], newest_subpage)

    def test_oldest_view_remains_lowest(self):
        oldest_subpage = self.view.add_subpage(self.named_generator('Oldest'))
        self.view.add_subpage(self.TestSubpage)
        frame_children = self.subpage_frame.winfo_children()
        self.assertIs(frame_children[0], oldest_subpage)

    def test_view_is_raised(self):
        subpage_name = 'Oldest'
        oldest_subpage = self.view.add_subpage(self.named_generator(subpage_name))
        self.view.add_subpage(self.TestSubpage)
        # Now we know the oldest one is currently lowest in GUI, try to raise it
        self.view.raise_view(subpage_name)
        # Check oldest subpage is now highest in GUI
        frame_children = self.subpage_frame.winfo_children()
        self.assertIs(frame_children[-1], oldest_subpage)

    def test_current_subpage_variable_updated_on_raise(self):
        subpage_variable = tkinter.StringVar()
        self.view.bind_subpage_variable(subpage_variable)
        subpage_name = 'TestName'
        self.view.add_subpage(self.named_generator(subpage_name))
        self.view.add_subpage(self.TestSubpage)
        self.view.raise_view(subpage_name)
        self.assertEqual(self.view.active_subpage.get(), subpage_name)


class TestPityView(unittest.TestCase):
    pass


class TestStatsView(unittest.TestCase):

    def setUp(self):
        root = tkinter.Tk()
        self.view = FullViews.StatsView(root)

    def test_set_selector_created(self):
        variable = tkinter.StringVar()
        standard = ['ONE', 'TWO', 'THREE']
        wild = ['FOUR', 'FIVE', 'SIX']
        self.view.add_set_selector(variable, standard, wild)
        self.assertIsInstance(self.view.set_selector, tkinter.ttk.OptionMenu)

    def test_pack_number_variable_bound(self):
        self.view.bind_pack_number(tkinter.StringVar())
        self.assertIsNotNone(self.view.total_packs_number.cget('textvariable'))

    def test_total_cards_variable_bound(self):

        rarity_variables = {rarity: tkinter.IntVar() for rarity in Hearthstone.rarities}
        self.view.bind_total_cards_numbers(rarity_variables)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertIsNotNone(self.view.total_numbers[rarity].cget("textvariable"), rarity)

    def test_mean_cards_variable_bound(self):
        rarity_variables = {rarity: tkinter.StringVar() for rarity in Hearthstone.rarities}
        self.view.bind_mean_cards_numbers(rarity_variables)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertIsNotNone(self.view.mean_numbers[rarity].cget("textvariable"), rarity)


class TestPackView(unittest.TestCase):
    pass


class TestPackMiniView(unittest.TestCase):

    def setUp(self):
        root = tkinter.Tk()
        # Wouldn't normally instantiate as top level, but can do
        self.view = MiniViews.PackMiniView(root)

    def test_scrollers_created(self):
        scrollvars = {rarity: tkinter.StringVar() for rarity in Hearthstone.rarities}
        self.view.add_scrollers(scrollvars)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertIsInstance(self.view.rarity_scrollers[rarity], IntScroller, rarity)

    def test_scroll_variables_unpacked(self):
        scrollvars = {rarity: tkinter.StringVar() for rarity in Hearthstone.rarities}
        self.view.add_scrollers(scrollvars)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertIs(self.view.rarity_scrollers[rarity].var, scrollvars[rarity], rarity)

    def test_set_selector_created(self):
        variable = tkinter.StringVar()
        standard = ['ONE', 'TWO', 'THREE']
        wild = ['FOUR', 'FIVE', 'SIX']
        self.view.add_set_selector(variable, standard, wild)
        self.assertIsInstance(self.view.set_selector, tkinter.ttk.OptionMenu)


class TestArenaMiniView(unittest.TestCase):

    pass


class TestSeasonMiniView(unittest.TestCase):

    pass


class TestOtherMiniView(unittest.TestCase):

    def setUp(self):
        root = tkinter.Tk()
        self.view = MiniViews.OtherMiniView(root)

    def test_folder_selector_created(self):
        options = ['ONE', 'TWO', 'THREE']
        variable = tkinter.StringVar()
        self.view.add_selector(variable, options)
        self.assertIsInstance(self.view.folder_selection, tkinter.ttk.OptionMenu)


class TestMainView(unittest.TestCase):
    pass


class TestModel(unittest.TestCase):

    def make_image(self, filepath):
        # Full HD res images
        # Test could use smaller , but no reason not to test properly
        image = Image.new('RGB', (1920,1080))
        image.save(filepath,format="PNG")
        image.close()

    def setUp(self):

        # create a temp file, save it's path and close it
        database_file = tempfile.NamedTemporaryFile(delete=False)
        self.teardown_files = []
        self.teardown_dirs = []
        self.database_path = database_file.name
        self.teardown_files.append(self.database_path)
        database_file.close()

        # Config for testing is fully defined here, so we can control every aspect
        config = ConfigParser(allow_no_value=True)
        # Override the default behaviour, which is to strip case
        config.optionxform = str
        config.add_section('filepaths')
        config.set('filepaths', 'tinydb', self.database_path)
        config.set('filepaths', 'desktop', 'C:')  # Tests should be overriding this, if used

        config.add_section('sets_standard')
        config.set('sets_standard', 'Classic', 'Classic')
        config.add_section('sets_wild')
        config.set('sets_wild', 'Goblins vs Gnomes', 'GvG')

        self.config = config

    def tearDown(self):
        # Remove temp constructs
        # All files must be torn down, so that directories are left empty
        # Clear up temporary files we created
        for path in self.teardown_files:
            os.unlink(path)
            assert not os.path.exists(path)
        # Clear up temporary directories
        # Will error on any non-empty directories
        for dir_ in self.teardown_dirs:
            os.rmdir(dir_)

    # ~~ Test init ~~

    def test_assigns_tkinter_variables(self):
        md = Model.Model(self.config)
        string_variables = [md.current_subpage, md.notes,
                            md.card_set, md.view_card_set]

        integer_variables = [md.reward_dust, md.reward_gold,
                             md.reward_packs, md.arena_wins,
                             md.arena_losses, md.end_rank,
                             md.max_rank, md.viewed_total_packs]

        for variable in string_variables:
            with self.subTest(variable=variable):
                self.assertIsInstance(variable, tkinter.StringVar, variable)

        for variable in integer_variables:
            with self.subTest(variable=variable):
                self.assertIsInstance(variable, tkinter.IntVar, variable)

        for rarity in Hearthstone.rarities:

            with self.subTest(rarity=rarity):
                self.assertIsInstance(md.viewed_mean_quantities[rarity], tkinter.StringVar, variable)

            with self.subTest(rarity=rarity):
                self.assertIsInstance(md.viewed_total_quantities[rarity], tkinter.IntVar, variable)

    def test_extracts_acronyms(self):
        pass

    # ~~ Test find_image ~~

    def test_parses_all_images(self):
        # Test that the model finds all screenshots in the desktop folder

        # the 'desktop', avoids issues with images that might be in the temp folder
        desktop_folder = tempfile.mkdtemp(prefix='HS_')

        self.config.set('filepaths', 'desktop', desktop_folder)

        # Todo: push this filename generating to the utils file.
        # Format of screenshots could also be pushed to Hearthstone class
        old_name = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'  # 03:04:05 on 2/1/2014
        new_1_name = 'Hearthstone Screenshot 06-07-17 08.09.10.png'  # 08:09:10 on 7/6/2017
        new_2_name = 'Hearthstone Screenshot 11-12-17 13.14.15.png'  # 13:14:15 on 12/11/2017

        old_path = os.path.join(desktop_folder, old_name)
        new_1_path = os.path.join(desktop_folder, new_1_name)
        new_2_path = os.path.join(desktop_folder, new_2_name)

        # Weird order, but ensures sorting is not using creation time, but filename only
        self.make_image(new_2_path)
        self.make_image(old_path)
        self.make_image(new_1_path)

        # Set all the generated images, and the folder they are in, to be torn down
        self.teardown_files.append(old_path)
        self.teardown_files.append(new_1_path)
        self.teardown_files.append(new_2_path)
        self.teardown_dirs.append(desktop_folder)

        model = Model.Model(self.config)

        # Pack will have already been popped, so will only have 2 left
        self.assertEqual(len(model.packs), 2)
        self.assertIsInstance(model.packs[0], CardPack.CardPack)

        # The exact details of the sorting and date extraction will be tested elsewhere
        # Here we simply test we have them sorted correctly
        # packs list should be newest->oldest, so that pop gets the oldest
        self.assertEqual(model.packs[0].image_name, new_2_name)
        self.assertEqual(model.packs[1].image_name, new_1_name)
        # Oldest pack will have been popped off the list already
        self.assertIsInstance(model.current_pack, CardPack.CardPack)
        self.assertEqual(model.current_pack.image_name, old_name)

        # Before teardown, we need to close the image
        model.image.close()

    def test_ignores_malformed_image_names(self):

        desktop_folder = tempfile.mkdtemp(prefix='HS_')
        self.config.set('filepaths', 'desktop', desktop_folder)

        valid_name = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'  # 03:04:05 on 2/1/2014
        # Using a similar naming format, to get the 'worst-case' possibility
        invalid_name = 'Other_games_Screenshot_1.2.2014.03.04.05.png'
        valid_path = os.path.join(desktop_folder, valid_name)
        invalid_path = os.path.join(desktop_folder, invalid_name)

        self.make_image(valid_path)
        self.make_image(invalid_path)

        # Set all the generated images, and the folder they are in, to be torn down
        self.teardown_files.append(valid_path)
        self.teardown_files.append(invalid_path)
        self.teardown_dirs.append(desktop_folder)

        model = Model.Model(self.config)

        # Should not have any packs, as the valid one has been popped
        self.assertEqual(len(model.packs), 0)
        self.assertEqual(model.current_pack.image_name, valid_name)

        # Before teardown, we need to close the image
        model.image.close()

    # ~~ Test next_pack ~~

    def test_next_pack(self):
        # Could really be incorporated with an earlier test

        desktop_folder = tempfile.mkdtemp(prefix='HS_')
        self.config.set('filepaths', 'desktop', desktop_folder)

        file_1 = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'  # 03:04:05 on 2/1/2014
        file_2 = 'Hearthstone Screenshot 06-07-17 08.09.10.png'  # 08:09:10 on 7/6/2017
        file_1_path = os.path.join(desktop_folder, file_1)
        file_2_path = os.path.join(desktop_folder, file_2)

        self.make_image(file_1_path)
        self.make_image(file_2_path)

        # Set all the generated images, and the folder they are in, to be torn down
        self.teardown_files.append(file_1_path)
        self.teardown_files.append(file_2_path)
        self.teardown_dirs.append(desktop_folder)

        model = Model.Model(self.config)

        # Model auto-pulls file_1 into current_pack
        self.assertEqual(len(model.packs), 1)
        self.assertEqual(model.current_pack.image_name, file_1)

        model.next_pack()  # move file_2 to curernt_pack
        self.assertEqual(len(model.packs), 0)
        self.assertEqual(model.current_pack.image_name, file_2)

        model.next_pack()  # no more files, current_pack set to None
        self.assertEqual(len(model.packs), 0)
        self.assertIsNone(model.current_pack)

    # ~~ Test reset_variables ~~

    def test_variables_are_reset(self):
        desktop_folder = tempfile.mkdtemp(prefix='HS_')
        self.config.set('filepaths', 'desktop', desktop_folder)

        file_1 = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'  # 03:04:05 on 2/1/2014
        file_1_path = os.path.join(desktop_folder, file_1)

        self.make_image(file_1_path)

        # Set all the generated images, and the folder they are in, to be torn down
        self.teardown_files.append(file_1_path)
        self.teardown_dirs.append(desktop_folder)

        model = Model.Model(self.config)

        for rarity in Hearthstone.rarities:
            model.quantities[rarity].set(1)

        note_string = 'Some Interesting Notes'
        model.notes.set(note_string)
        set_string = "Journey to Un'Goro"
        model.card_set.set(set_string)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertEqual(model.quantities[rarity].get(), 1)

        self.assertEqual(model.notes.get(), note_string)
        self.assertEqual(model.card_set.get(), set_string)

        model.reset_variables()

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertEqual(model.quantities[rarity].get(), Hearthstone.default_pack[rarity])

        self.assertEqual(model.notes.get(), '')
        # card set is intentionally left
        self.assertEqual(model.card_set.get(), set_string)

        model.image.close()

    # ~~ Test is_valid_pack ~~
    # Note, only the values of the model are tested, no image need be loaded

    def test_valid_pack(self):
        model = Model.Model(self.config)

        for rarity in Hearthstone.rarities:
            model.quantities[rarity].set(Hearthstone.default_pack[rarity])

        model.card_set.set('Classic')
        self.assertTrue(model.is_valid_pack())

    def test_valid_pack_defaults(self):
        model = Model.Model(self.config)
        model.card_set.set('Classic')
        self.assertTrue(model.is_valid_pack())

    def test_valid_pack_noteworthy(self):
        model = Model.Model(self.config)
        model.quantities['common'].set(3)
        model.quantities['golden_epic'].set(1)
        model.card_set.set('Classic')

        notes_string = 'This has a golden epic'
        model.notes.set(notes_string)
        self.assertEqual(model.notes.get(), notes_string)
        self.assertTrue(model.is_valid_pack())

    def test_too_many_cards(self):
        model = Model.Model(self.config)

        for rarity in Hearthstone.rarities:
            model.quantities[rarity].set(0)
        # Not adding anything that might trigger the need for notes
        model.quantities['common'].set(100)
        model.quantities['rare'].set(100)

        model.card_set.set('Classic')
        self.assertFalse(model.is_valid_pack())

    def test_too_few_cards(self):
        model = Model.Model(self.config)

        for rarity in Hearthstone.rarities:
            model.quantities[rarity].set(0)

        model.card_set.set('Classic')
        self.assertFalse(model.is_valid_pack())

    def test_all_common_cards(self):
        model = Model.Model(self.config)

        for rarity in Hearthstone.rarities:
            model.quantities[rarity].set(0)

        model.quantities['common'].set(5)
        model.card_set.set('Classic')
        self.assertFalse(model.is_valid_pack())

    def test_no_set_selected(self):
        model = Model.Model(self.config)
        # defaults is valid, sans the card_set
        self.assertFalse(model.is_valid_pack())
        pass

    def test_no_required_notes(self):
        model = Model.Model(self.config)
        model.quantities['common'].set(3)
        model.quantities['golden_epic'].set(1)
        model.card_set.set('Classic')

        self.assertFalse(model.is_valid_pack())

    # ~~ Test submit ~~

    def test_tinydb_updated_pack(self):
        pass

    def test_tinydb_updated_arena(self):
        pass

    def test_tinydb_updated_end_of_season(self):
        pass

    def test_image_correctly_moved(self):
        # Test for each output folder

        # # not really needed, but allows easier cleanup
        # hearthstone_screenshot_folder = tempfile.mkdtemp()
        # # self.teardown_list.append(hearthstone_screenshot_folder)
        # pack_folder = os.path.join(hearthstone_screenshot_folder, 'Packs')
        # os.mkdir(pack_folder)
        pass

    def test_handles_missing_directory(self):
        pass

    def test_year_separated_directory(self):
        pass

    def test_month_separated_directory(self):
        pass

    # ~~ Test not_pack

    def test_image_is_not_moved(self):
        # Could really be incorporated with an earlier test

        desktop_folder = tempfile.mkdtemp(prefix='HS_')
        self.config.set('filepaths', 'desktop', desktop_folder)

        file_1 = 'Hearthstone_Screenshot_1.2.2014.03.04.05.png'  # 03:04:05 on 2/1/2014
        file_1_path = os.path.join(desktop_folder, file_1)

        self.make_image(file_1_path)

        # Set all the generated images, and the folder they are in, to be torn down
        self.teardown_files.append(file_1_path)
        self.teardown_dirs.append(desktop_folder)

        model = Model.Model(self.config)

        self.assertEqual(model.current_pack.image_name, file_1)
        model.not_pack()
        self.assertIsNone(model.current_pack)
        self.assertTrue(os.path.exists(file_1_path))

    # ~~ Test extract_data ~~
    # Todo: Currently just tests for pack data extraction, will need to add Arena and EOS
    # when their relavent viewing pages have been created

    def test_extract_data(self):
        # TODO: needs to update with the changes to the save format and sortkey
        note_string_1 = 'Some Interesting Notes'
        sortkey_1 = '2017/01/02/03/04/05/06'
        note_string_2 = 'Some More Interesting Notes'
        sortkey_2 = '2017/07/08/09/10/11/12'
        note_string_3 = 'Even More Interesting Notes'
        sortkey_3 = '2017/01/13/14/15/16/17'

        pack_1 = {'date': sortkey_1, 'common': 4, 'rare': 1, 'epic': 0, 'legendary': 0,
                  'golden_common': 0, 'golden_rare': 0, 'golden_epic': 0, 'golden_legendary': 0,
                  'notes': note_string_1, 'set': 'KFT'}
        pack_2 = {'date': sortkey_2, 'common': 2, 'rare': 1, 'epic': 1, 'legendary': 0,
                  'golden_common': 0, 'golden_rare': 1, 'golden_epic': 0, 'golden_legendary': 0,
                  'notes': note_string_2, 'set': 'KFT'}
        pack_3 = {'date': sortkey_3, 'common': 2, 'rare': 1, 'epic': 0, 'legendary': 1,
                  'golden_common': 0, 'golden_rare': 1, 'golden_epic': 0, 'golden_legendary': 0,
                  'notes': note_string_3, 'set': 'Classic'}

        db = TinyDB(self.database_path)
        card_table = db.table('card_data')
        card_table.insert(pack_1)
        card_table.insert(pack_2)
        card_table.insert(pack_3)
        db.close()

        self.config.set('sets_standard', 'Knights of the Frozen Throne', 'KFT')
        self.config.set('sets_standard', 'Whispers of the Old Gods', 'WotOG')

        model = Model.Model(self.config)

        # Have to disable the trace the vew_card_set variable, so we can override value
        model.view_card_set.trace_vdelete(*model.view_card_set.trace_vinfo()[0])

        model.view_card_set.set('Knights of the Frozen Throne')
        model.extract_data()

        self.assertEqual(model.viewed_total_packs.get(), 2)

        self.assertEqual(model.viewed_mean_quantities['common'].get(), '3.000')
        self.assertEqual(model.viewed_mean_quantities['rare'].get(), '1.000')
        self.assertEqual(model.viewed_mean_quantities['epic'].get(), '0.500')
        self.assertEqual(model.viewed_mean_quantities['legendary'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_common'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_rare'].get(), '0.500')
        self.assertEqual(model.viewed_mean_quantities['golden_epic'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_legendary'].get(), '0.000')

        self.assertEqual(model.viewed_total_quantities['common'].get(), 6)
        self.assertEqual(model.viewed_total_quantities['rare'].get(), 2)
        self.assertEqual(model.viewed_total_quantities['epic'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['legendary'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_common'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_rare'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['golden_epic'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_legendary'].get(), 0)

        model.view_card_set.set('Classic')
        model.extract_data()

        self.assertEqual(model.viewed_total_packs.get(), 1)

        self.assertEqual(model.viewed_mean_quantities['common'].get(), '2.000')
        self.assertEqual(model.viewed_mean_quantities['rare'].get(), '1.000')
        self.assertEqual(model.viewed_mean_quantities['epic'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['legendary'].get(), '1.000')
        self.assertEqual(model.viewed_mean_quantities['golden_common'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_rare'].get(), '1.000')
        self.assertEqual(model.viewed_mean_quantities['golden_epic'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_legendary'].get(), '0.000')

        self.assertEqual(model.viewed_total_quantities['common'].get(), 2)
        self.assertEqual(model.viewed_total_quantities['rare'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['epic'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['legendary'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['golden_common'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_rare'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['golden_epic'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_legendary'].get(), 0)

        model.view_card_set.set('All Sets')
        model.extract_data()

        self.assertEqual(model.viewed_total_packs.get(), 3)

        self.assertEqual(model.viewed_mean_quantities['common'].get(), '2.667')
        self.assertEqual(model.viewed_mean_quantities['rare'].get(), '1.000')
        self.assertEqual(model.viewed_mean_quantities['epic'].get(), '0.333')
        self.assertEqual(model.viewed_mean_quantities['legendary'].get(), '0.333')
        self.assertEqual(model.viewed_mean_quantities['golden_common'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_rare'].get(), '0.667')
        self.assertEqual(model.viewed_mean_quantities['golden_epic'].get(), '0.000')
        self.assertEqual(model.viewed_mean_quantities['golden_legendary'].get(), '0.000')

        self.assertEqual(model.viewed_total_quantities['common'].get(), 8)
        self.assertEqual(model.viewed_total_quantities['rare'].get(), 3)
        self.assertEqual(model.viewed_total_quantities['epic'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['legendary'].get(), 1)
        self.assertEqual(model.viewed_total_quantities['golden_common'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_rare'].get(), 2)
        self.assertEqual(model.viewed_total_quantities['golden_epic'].get(), 0)
        self.assertEqual(model.viewed_total_quantities['golden_legendary'].get(), 0)

        model.view_card_set.set('Whispers of the Old Gods')
        model.extract_data()

        self.assertEqual(model.viewed_total_packs.get(), 0)

        for rarity in Hearthstone.rarities:
            with self.subTest(rarity=rarity):
                self.assertEqual(model.viewed_mean_quantities[rarity].get(), '###')
                self.assertEqual(model.viewed_total_quantities[rarity].get(), 0)

    def test_card_set_not_selected(self):
        # Function simply returns without doing anything
        # really hard to test this...
        pass


class TestGUI(unittest.TestCase):

    def setUp(self):
        # create a temp file, save it's path and close it
        database_file = tempfile.NamedTemporaryFile(delete=False)
        self.teardown_files = []
        self.teardown_dirs = []
        self.database_path = database_file.name
        self.teardown_files.append(self.database_path)
        database_file.close()

        # Config for testing is fully defined here, so we can control every aspect
        config = ConfigParser(allow_no_value=True)
        # Override the default behaviour, which is to strip case
        config.optionxform = str
        config.add_section('filepaths')
        config.set('filepaths', 'tinydb', self.database_path)
        config.set('filepaths', 'desktop', 'C:')  # Tests should be overriding this, if used

        config.add_section('sets_standard')
        config.set('sets_standard', 'Classic', 'Classic')
        config.add_section('sets_wild')
        config.set('sets_wild', 'Goblins vs Gnomes', 'GvG')

        self.config = config

    def tearDown(self):
        for path in self.teardown_files:
            os.unlink(path)
            assert not os.path.exists(path)

    def test_init(self):
        root = tkinter.Tk()
        gui = layout_test.GUI(root, self.config)

        self.assertIsInstance(gui.model, Model.Model)
        self.assertIsInstance(gui.main_view, FullViews.MainView)
        self.assertIsInstance(gui.pack_view, FullViews.PackView)
        self.assertIsInstance(gui.stats_view, FullViews.StatsView)
        self.assertIsInstance(gui.pity_view, FullViews.PityView)


if __name__ == '__main__':
    unittest.main()
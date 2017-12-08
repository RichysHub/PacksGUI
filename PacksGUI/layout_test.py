#!/usr/bin/env python

import configparser
from tkinter import Tk, Menu

from PIL import Image


from MiniViews import PackMiniView, ArenaMiniView, SeasonMiniView, OtherMiniView
from Model import Model
from FullViews import PityView, StatsView, PackView, MainView
import Hearthstone


# Controller passes a config, from which the model extracts a lot of info
# model will then go and grab the files it needs to hold
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
        self.old_set = None

        self.model.bind_graph_update_function(self.update_graphs)

        self.pity_view = self.main_view.add_subpage(PityView)
        self.configure_pity_view()

        self.master.wm_title('Hearthstone screenshot cataloger')

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
        # Todo: should we hook the image update in as a variable binding?
        self.pack_view.not_pack_button.config(command=self.not_pack)
        self.update_image()
        self.pack_view.bind_subpage_variable(self.model.current_subpage)

        # ~~ Pack subpage ~~
        pack_subpage = self.pack_view.add_subpage(PackMiniView)
        pack_subpage.add_scrollers(self.model.quantities)
        pack_subpage.add_set_selector(self.model.card_set, self.model.standard_sets, self.model.wild_sets)
        pack_subpage.note_box.config(textvariable=self.model.notes)

        # ~~ Arena subpage ~~
        arena_subpage = self.pack_view.add_subpage(ArenaMiniView)

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
        self.stats_view.bind_enchant_values(self.model.disenchant_value, self.model.enchant_value)
        pass

    def configure_pity_view(self):
        self.pity_view.add_set_selector(self.model.pity_card_set, self.model.standard_sets, self.model.wild_sets)
        self.pity_view.bind_current_timers(self.model.pity_current_timers)
        self.pity_view.bind_pack_number(self.model.pity_total_packs)
        self.pity_view.bind_advice_text(self.model.pity_advice)

    def update_image(self):
        try:
            self.pack_view.set_image(self.model.image)
        except (AttributeError, ValueError):
            # Handling no image found, or last image closed, generating a black image for now
            self.pack_view.set_image(Image.new('RGB', (1920, 1080)))

    # TODO: probably want a rename for this, given it's now going to be not pack, not arena, not EoS etc
    def not_pack(self):
        self.model.next_pack()
        self.update_image()

    def submit(self):

        # --> Can use model variable to determine which subpage we are on
        # --> Can process subpage validation separately

        # Todo: is the logic for this being in the controller still valid, or should it move?
        # evoked by the submit button.
        # The controller has this method such that if the model were to fail, view can be changed

        # We lucked out here. We can use this submit hook to perform all the arena related things we need.
        # On arena submit, we can extract the # of wins from the model's variable, and set up the next arena page
        # Can also lock all our top level buttons, so that the user can't switch off between images

        active_page = self.pack_view.active_subpage.get()

        # Todo: Could do with something cleaner than an if else ladder
        # Todo: using names here is a little off, consider changing this
        if active_page == 'Packs':  # Actual pack submission page
            valid = self.model.is_valid_pack()
            if valid:
                self.model.submit()
                self.update_image()
            else:
                print("Invalid pack")
            pass
        elif active_page == 'Arena Rewards':  # Arena rewards page
            page = self.pack_view.subpages['Arena Rewards'].active_subpage.get()
            print(page)
            if page == 'Arena1':
                # This will end up a little WET when we add the Season end set
                # Both want the buttons to stay disabled for a set # of images, and enable at end
                # Both will want the first in set to be raised at the end too
                # Could be done cleaner than case by case
                self.main_view.disable_buttons()
                self.pack_view.disable_buttons()
                # logic to prepare second arena page will go here, extracting win# from the first page

                wins = 3

                # self.pack_view.subpages['Arena Rewards'].set_number_wins(wins)

                reward_obj = Hearthstone.Hearthstone.rewards[wins]

                for reward in reward_obj.guaranteed:
                    if not isinstance(reward, Hearthstone.Random):  # Not a pool reward
                        # Todo: Not sure how we're handling the boxes
                        # Could be using grid_remove method on the reward boxes
                        # Adjust remaining boxes based on the pools
                        # so that all the subpages are there but hidden?
                        # We know we always have a pack box, so this one makes no sence to have the others hiding in
                        # self.pack_view.subpages['Arena Rewards'].add_box(reward)
                        pass
                    else:
                        # Sending the whole pool, let the view work it out?
                        # self.pack_view.subpages['Arena Rewards'].add_box(reward_obj.pool)
                        pass

                self.pack_view.subpages['Arena Rewards'].raise_view('Arena2')
            elif page == 'Arena2':
                self.main_view.enable_buttons()
                self.pack_view.enable_buttons()

                # Some method to reset the boxes, either here or perhaps when bringing up the page 2
                # self.pack_view.subpages['Arena Rewards'].clear_boxes()

                self.pack_view.subpages['Arena Rewards'].raise_view('Arena1')

                # TODO model submit in here

        elif active_page == 'Season End':  # End of season rewards page
            pass
        elif active_page == 'Other':  # Other image page
            pass
        else:
            pass

    def update_graphs(self, *callback):
        new_set = self.model.view_card_set.get()
        if new_set == self.old_set:
            # callbacks from optionmenus fire twice, check it actually changed
            return
        # We bind this function so that it is called every time stats view dropdown is changed
        self.old_set = new_set
        graph_data = self.model.extract_data()
        if graph_data:
            x, y = graph_data
            self.stats_view.clear()
            self.stats_view.plot(x, y)


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

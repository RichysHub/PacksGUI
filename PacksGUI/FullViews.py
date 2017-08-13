from tkinter import StringVar, NSEW, Label, E, W, Frame
from tkinter.ttk import Button, OptionMenu

from PIL import Image, ImageTk

from Hearthstone import Hearthstone


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

        self.bind('<FocusIn>', self.on_focus)  # Bind on_focus method
        self.bind('<Key>', self.key_pressed)  # Bind key_pressed method

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

    def raise_view(self, subpage_name):
        frame = self.subpages[subpage_name]
        self.active_subpage.set(subpage_name)
        frame.tkraise()
        frame.focus_set()

    def bind_subpage_variable(self, subpage_var):
        self.active_subpage = subpage_var

    def key_pressed(self, event):
        # Override this method to handle key presses
        pass

    def on_focus(self, *args):
        # Called when focus is set to this widget
        print('{}: I just got focus :3'.format(self.name))
        pass

# Displays pity timers
# Should be on a per set basis, with dropdown
# Should also have some form of suggestion for pack to buy
# Perhaps even a top3 list of exciting timers that are nearly up
# --> Obvs prioritising legendary over epic, but would rank Leg in 2 > Epic in 1 eg.
# --> Simple heuristic would be #left/#timer, so if time is 25, and this'd be pack 20, 20/25
# --> Compare heuristics and show info about the highest scoring
# -----> Which set, what you can expect, how many 'til guarantee
# A basic statistics page, perhaps later will include some pretty graphs
class PityView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Pity'


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
        for rarity in Hearthstone.rarities:
            self.total_numbers[rarity].config(textvariable=variable_dict[rarity])

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

    def set_image(self, image):
        # takes the result of Image.open, and pushes result to the image frame
        sized_image = image.resize((700, 394), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(sized_image)
        self.image_frame.config(image=photo)
        self.image_frame.image = photo

    def on_focus(self, *args):
        # Push focus to currently active subpage
        self.subpages[self.active_subpage.get()].focus_set()


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



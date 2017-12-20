from tkinter import StringVar, NSEW, Label, Frame, DISABLED, NORMAL, CENTER, BOTH, LabelFrame
from tkinter.ttk import Button, OptionMenu

from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import datetime

from Hearthstone import Hearthstone
from utils import optionmenu_patch

# matching default Windows grey
matplotlib.rcParams['figure.facecolor'] = '0.95'


years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')


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

    def size_grid(self, rows, columns):
        self.size_rows(rows)
        self.size_columns(columns)

    def size_rows(self, rows):
        for i in range(rows):
            self.rowconfigure(i, weight=1)

    def size_columns(self, columns):
        for i in range(columns):
            self.columnconfigure(i, weight=1)

    # TODO: from trying to envisage tests, this seems to do a LOT for one method
    # --> is this a problem?
    def add_subpage(self, constructor, make_button=True):
        # can pass buttons=False, to not bother making them
        if not self.active_subpage:
            # subpage variable is needed, if none, supply one
            self.active_subpage = StringVar()
        # We assume these have been set by now
        subpage = constructor(self.subpage_frame)
        self.subpages[subpage.name] = subpage
        subpage.grid(row=0, column=0, sticky=NSEW)
        self.subpage_frame.columnconfigure(0, weight=1)
        self.subpage_frame.rowconfigure(0, weight=1)
        if make_button:
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
        print('{}: I just got focus'.format(self.name))
        pass

    def disable_buttons(self):
        for button in self.subpage_buttons:
            button.config(state=DISABLED)

    def enable_buttons(self):
        for button in self.subpage_buttons:
            button.config(state=NORMAL)


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

        # Suggestion block
        # --> Legendary in 2 > Golden common in 1
        # --> Weight by max timer, not value, but use value to break ties?
        # --> Need a heuristic that gives reasonable sorting

        # Do we want 2 suggestion blocks? 1 overall, 1 set specific?

        # Idea: Just current/Max, highest wins
        # weights epic in 1 = legendary in 4 = Golden rare in 3 = g.epic in 15 = g.leg in 35
        # The g.leg is of course nice, but if it's hiding a legendary in 5 from a different set :/
        # Perhaps a max cap of say things that are 10 off max?

        self.set_selector = None
        self.current_timers = {}

        self.total_packs = Label(self, text='# Packs', justify=CENTER)
        self.total_packs.grid(row=0, column=0, columnspan=3, sticky=NSEW)

        for idx, rarity in enumerate(Hearthstone.rarities[2:]):
            boundary = Frame(self)
            rarity_label = Label(boundary, text=Hearthstone.rarity_display_names[rarity])
            rarity_label.pack()
            current_timer = Label(boundary, text='#/#')
            current_timer.pack(pady=10)
            # Grid into a 3 wide array
            boundary.grid(row=1+(idx//3), column=idx % 3, padx=20, pady=30, sticky=NSEW)

            self.current_timers.update({rarity: current_timer})

        self.advice_text = Label(self, text='I have no advice for you', justify=CENTER)
        self.advice_text.grid(row=3, column=0, columnspan=3, sticky=NSEW)

        self.size_columns(3)

    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", *standard, *wild)
        # Using patch to fix bug with multiple menus
        optionmenu_patch(set_selector, model_variable)
        set_selector['menu'].insert_separator(len(standard))
        set_selector.grid(row=0, column=0, columnspan=5, pady=20)
        self.set_selector = set_selector

    def bind_current_timers(self, variable_dict):
        for rarity in Hearthstone.rarities[2:]:
            self.current_timers[rarity].config(textvariable=variable_dict[rarity])

    def bind_pack_number(self, variable):
        # Using the combined label & val in a string var here
        # Inconsistent, but it makes it much easier here
        self.total_packs.config(textvariable=variable)

    def bind_advice_text(self, string_var):
        self.advice_text.config(textvariable=string_var)


class StatsView(View):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = 'Stats'

        self.set_selector = None
        self.total_packs = Label(self, text='# Packs')
        self.total_packs.grid(row=1, column=1, columnspan=2, sticky=NSEW)

        self.total_numbers = {}
        self.mean_numbers = {}

        # TODO: color mean values green/red depending how they compare to average?
        for idx, rarity in enumerate(Hearthstone.rarities):
            boundary = Frame(self)
            rarity_label = Label(boundary, text=Hearthstone.rarity_display_names[rarity])
            rarity_label.pack()
            total_number = Label(boundary, text='#')
            total_number.pack(pady=10)
            mean_number = Label(boundary, text='#')
            mean_number.pack()
            # Grid into a 4 wide array
            boundary.grid(row=3+(idx//4), column=idx % 4, padx=20, pady=30, sticky=NSEW)

            self.total_numbers.update({rarity: total_number})
            self.mean_numbers.update({rarity: mean_number})

        # Average dust disenchant per pack
        # Average dust enchant per pack

        self.disenchant_value = Label(self, text='Average Disenchant\n100')
        self.disenchant_value.grid(row=2, column=1, pady=20)
        self.enchant_value = Label(self, text='Average Enchant\n180')
        self.enchant_value.grid(row=2, column=2, pady=20)

        # Graphs in a buttoned subpage area?
        # Graphs for:
        # --> packs over time
        # --> packs of set vs total packs
        # ----> This one is a little redundant?
        # --> disenchant values

        self.stats_figure = Figure(figsize=(5, 4), dpi=100)
        self.stats_plot = self.stats_figure.add_subplot(111)

        self.fig_frame = Frame(self)
        self.fig_frame.grid(row=6, column=0, columnspan=4, sticky=NSEW)

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(self.stats_figure, master=self.fig_frame)
        canvas.show()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

        self.size_columns(4)

    def add_set_selector(self, model_variable, standard, wild):
        set_selector = OptionMenu(self, model_variable, "Card Set", 'All Sets', *standard, *wild)
        # Using patch to fix bug with multiple menus
        optionmenu_patch(set_selector, model_variable)
        set_selector['menu'].insert_separator(1)
        set_selector['menu'].insert_separator(len(standard)+2)
        set_selector.grid(row=0, column=0, columnspan=5, pady=20)
        self.set_selector = set_selector
        pass

    def bind_pack_number(self, variable):
        # binds the variable as the value for the pack number display
        self.total_packs.config(textvariable=variable)

    def bind_total_cards_numbers(self, variable_dict):
        for rarity in Hearthstone.rarities:
            self.total_numbers[rarity].config(textvariable=variable_dict[rarity])

    def bind_mean_cards_numbers(self, variable_dict):
        for rarity in Hearthstone.rarities:
            self.mean_numbers[rarity].config(textvariable=variable_dict[rarity])

    def bind_enchant_values(self, disenchant_variable, enchant_variable):
        self.disenchant_value.config(textvariable=disenchant_variable)
        self.enchant_value.config(textvariable=enchant_variable)

    def plot(self, x, y):
        self.stats_plot.plot(x, y)
        self.stats_plot.xaxis.set_major_locator(years)
        self.stats_plot.xaxis.set_major_formatter(yearsFmt)
        self.stats_plot.xaxis.set_minor_locator(months)

        datemin = datetime.date(2013, 12, 14)
        datemax = datetime.date(datetime.date.today().year + 1, 1, 1)
        self.stats_plot.set_xlim(datemin, datemax)
        self.stats_plot.xaxis_date()
        self.stats_figure.canvas.draw()

    def clear(self):
        self.stats_plot.clear()
        self.stats_figure.canvas.draw()


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

        self.size_columns(4)

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

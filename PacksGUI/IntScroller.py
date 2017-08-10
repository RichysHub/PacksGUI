from tkinter import IntVar, Entry, CENTER, TOP, Frame
from tkinter.ttk import Button


class IntScroller(Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master)

        # define from_ < to, even for negative increment
        self.min = kwargs.pop('from_', 0)
        self.max = kwargs.pop('to', 5)
        self.increment = kwargs.pop('increment', 1)
        self.var = kwargs.pop('textvariable', IntVar())

        # Defaulting to min if no starting value given
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

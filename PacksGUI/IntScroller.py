from tkinter import IntVar, Entry, CENTER, RIGHT, LEFT, Frame, Tk, Label, LabelFrame
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
        label_text = kwargs.pop('label', None)

        # Clamp value to range
        value = min(self.max, max(value, self.min))

        # TODO: this feels a little funky, having the IntScroller set the value in the model?
        self.var.set(value)

        right_frame = Frame(self)

        if label_text:
            left_frame = Frame(self)
            self.label = Label(left_frame, text=label_text, justify=RIGHT)
            self.label.pack()
            left_frame.grid(row=0, column=0)
            scroller_column = 1
        else:
            self.label = None
            scroller_column = 0

        self.up_button = Button(right_frame, text='\u25b2', command=self.inc, **kwargs)
        self.text = Entry(right_frame, textvariable=self.var, justify=CENTER, state='readonly', **kwargs)
        self.down_button = Button(right_frame, text='\u25bc', command=self.dec, **kwargs)

        self.up_button.grid(row=0)
        self.text.grid(row=1)
        self.down_button.grid(row=2)
        right_frame.grid(row=0, column=scroller_column)

        # Using a third column, same width as text column, to help keep scroller central in widget
        self.columnconfigure(0, weight=1, uniform='foo')
        if label_text:
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1, uniform='foo')



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

if __name__ == '__main__':
    # Simple testbed, for quick viewing of changes
    root = Tk()
    frame = Frame(root)
    frame.pack(padx=100, pady=100)

    textless = IntScroller(frame, from_=0, to=5, value=10, width=2)
    text = IntScroller(frame, from_=0, to=5, value=10, width=2, label='Epicdsfhgkusdfjygdsfjgdfhjgsdfghgfsdfug')
    negative_increment = IntScroller(frame, from_=0, to=25, value=25, width=3, increment=-1, label='Rank')
    multiple_increment = IntScroller(frame, from_=0, to=30, value=10, width=2, increment=2)

    textless.pack()
    text.pack()
    negative_increment.pack()
    multiple_increment.pack()

    root.mainloop()

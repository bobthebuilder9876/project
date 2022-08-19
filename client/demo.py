import tkinter as tk
from tkinter import ttk
from datetime import datetime

# constants for use as font definitions to ensure a consistent design
LARGEFONT = ("Verdana", 20)
SMALLFONT = ("Verdana", 14)
VSMALLFONT = ("Verdana", 10)


class tkinterApp(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, Results, SingleDay, MultiDay):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# first window frame startpage

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # label of frame Layout 2
        label = ttk.Label(self, text="Retrieve Medical Data", font=LARGEFONT)

        # putting the grid in its place by using
        # grid
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Search for data from a single day",
                             command=lambda: controller.show_frame(SingleDay))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        button2 = ttk.Button(self, text="Search for data from a range of dates",
                             command=lambda: controller.show_frame(MultiDay))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)


# second window frame to display retrieved medical data
class Results(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page 1", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

    # this method validates whether the data is in the correct format
    def checkValInput(self, date):
        format = "%d-%m-%Y"
        # checking if format matches the date
        res = True

        # using try-except to check for truth value
        try:
            res = bool(datetime.strptime(date, format))
        except ValueError:
            res = False
        return res

    # when the user searches for a single day, the value of the date is passed to this method
    def searchSingle(self, date, cont):
        if not self.checkValInput(self, date):
            cont.show_frame(SingleDay)

        format = "%d-%m-%Y"
        dateF = datetime.strptime(date, format)

    def searchMulti(self, dateFrom, dateTo, cont):
        # first check the data is of the right format
        if not (self.checkValInput(self, dateFrom) and self.checkValInput(self, dateTo)):
            cont.show_frame(MultiDay)

        # convert the dates to the date format
        format = "%d-%m-%Y"
        dateFromF = datetime.strptime(dateFrom, format)
        dateToF = datetime.strptime(dateTo, format)

        # compare the dates to check that the from date isn't after the to
        if dateFromF > dateToF:
            cont.show_frame(MultiDay)


class SingleDay(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Search for single day", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)
        label2 = ttk.Label(self, text="Date", font=SMALLFONT)
        label2.grid(row=1, column=1, padx=10, pady=10)
        dateEntry = ttk.Entry(self)
        dateEntry.grid(row=1, column=2, padx=10, pady=10)
        searchBtn = ttk.Button(self, text="Search",
                               command=lambda: [controller.show_frame(Results),
                                                Results.searchSingle(Results, dateEntry.get(), controller)])
        searchBtn.grid(row=1, column=3, padx=10, pady=10)
        inputDscr = ttk.Label(self, text="Enter date in format %d-%m-%Y", font=VSMALLFONT)
        inputDscr.grid(row=1, column=4, padx=10, pady=10)

class MultiDay(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Search for data in a range", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)
        label2 = ttk.Label(self, text="Date from", font=SMALLFONT)
        label2.grid(row=1, column=1, padx=10, pady=10)
        dateFrom = ttk.Entry(self)
        dateFrom.grid(row=1, column=2, padx=10, pady=10)
        label3 = ttk.Label(self, text="Date to", font=SMALLFONT)
        label3.grid(row=2, column=1, padx=10, pady=10)
        dateTo = ttk.Entry(self)
        dateTo.grid(row=2, column=2, padx=10, pady=10)
        searchBtn = ttk.Button(self, text="Search",
                               command=lambda: [controller.show_frame(Results),
                                                Results.searchMulti(Results, dateFrom.get(), dateTo.get(), controller)])
        searchBtn.grid(row=2, column=3, padx=10, pady=10)
        inputDscr = ttk.Label(self, text="Enter date in format %d-%m-%Y", font=VSMALLFONT)
        inputDscr.grid(row=1, column=4, padx=10, pady=10)


# Driver Code
app = tkinterApp()
app.mainloop()


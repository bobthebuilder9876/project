# TKinter-based Graphic User Interface

from ftplib import FTP
from tkinter import *
import tkinter.font as font
from tkinter.ttk import *
from tkcalendar import Calendar

# FTP Connection details

host = "127.0.0.1" # PLACEHOLDER - Server hostname
port = 21 # PLACEHOLDER - Server port
user = "devuser" # PLACEHOLDER - Server username
pswd = "verysecurepassword1234" # PLACEHOLDER - Server password


def ftp_connect():
    ftp = FTP(host, user, pswd)
    ftp.login()


def search_multi_day():
    date_to_frame.tkraise(root)


def search_just_day():
    return None


# Initialisation of form and declaration of size and key properties
root = Tk()
root.title("Medical data retrieval")
root.resizable(width=FALSE, height=FALSE)
root.geometry("900x600")


# Heading
heading = Label(root, text="Retrieve medical data")
heading['font'] = font.Font(size=18)
heading.place(x=30, y=20)


# Input boxes for range of dates, data is required from
date_from = Label(root, text="From: ")
date_from['font'] = font.Font(size=12)
date_from.place(x=30, y=80)

#from_input = Entry(root)
#from_input.place(x=100, y=80)

#to_input = Entry(root)
#to_input.place(x=100, y=120)

date_to = Label(root, text="To: ")
date_to['font'] = font.Font(size=12)
date_to.place(x=430, y=80)
date_to_frame = Tk()
date_to_frame.title("Date to")
date_to_frame.resizable(width=FALSE, height=FALSE)
date_to_frame.geometry("400x300")

search_btn = Button(root, text='Search for just selected day', command=search_just_day())
search_btn.place(x=180, y=320)

search_btn_multi = Button(root, text='Search for a range starting with the selected day', command=search_multi_day())
search_btn_multi.place(x=380, y=320)

# Calendar input box
cal_from = Calendar(root, selectmode = 'day',
               year = 2022, month = 8,
               day = 8)
cal_from.place(x=100, y=100)


root.mainloop()




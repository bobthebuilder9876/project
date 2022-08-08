# TKinter-based Graphic User Interface

from ftplib import FTP
from tkinter import *
import tkinter.font as font
from tkinter.ttk import *

# FTP Connection details

host = "127.0.0.1" # PLACEHOLDER - Server hostname
port = 21 # PLACEHOLDER - Server port
user = "devuser" # PLACEHOLDER - Server username
pswd = "verysecurepassword1234" # PLACEHOLDER - Server password


def ftp_connect():
    ftp = FTP(host, user, pswd)
    ftp.login()


# Initialisation of form and declaration of size and key properties
root = Tk()
root.title("Medical data retrieval")
root.resizable(width=FALSE, height=FALSE)
root.geometry("900x600")


# Heading
heading = Label(root, text="Retrieve medical data")
heading['font'] = font.Font(size=18)
heading.place(x=30, y=20)


root.mainloop()




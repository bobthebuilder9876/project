from getpass import getpass
from date_range import *
import os

"""Creates a config file in the same directory. Creates file if it doesn't exist. Allows user to set 9 different values each stored on a specific line in the file.
The number entered to select a value corresponds to the line in the file that value is stored on. Line 0 is reserved for the 'last' variable used by the client
(last pull from server), which is not alterable by the user here and is blank by default."""

while True:
    print("Enter a numeric character to configure its associated setting:")
    print("1 - regular FTP pull interval")
    print("2 - server hostname")
    print("3 - server port")
    print("4 - server username")
    print("5 - server password")
    print("6 - data processing directory")
    print("7 - validated data directory")
    print("8 - invalidated data directory")
    print("9 - request manual data pull")
    print("0 - (logs.csv)\n")
    print("(press enter to cancel)\n")

    #validate input
    try:
        op = int(input(""))
    except ValueError:
        print("Invalid input.\n")
        continue
    """if not (0<=op and op<=9):
        print("Invalid input.\n")
        continue"""

    #record config file in current state
    with open("config.txt", 'a+') as file:
        file.seek(0)
        lines = file.readlines()
        linesNo = len(lines)
        #if latter fields are blank, add newlines to avoid index error
        if (linesNo<9):
            for i in range (8-linesNo):
                lines.append('\n')
            lines.append('')

    #(exit program)
    if (op == 0):
        break

    var=''
    if (op == 1):
        var = input("Enter interval (in seconds), or press enter to cancel: ")
    if (op == 2):
        var = input("Enter server host, or press enter to cancel: ")
    if (op == 3):
        var = input("Enter server port, or press enter to cancel: ")
    if (op == 4):
        var = input("Enter username, or press enter to cancel: ")
    if (op == 5):
        #getpass doesn't work in idle, but would hide the user's input on the terminal
        var = getpass("Enter new password, or press enter to cancel: ")
    if (op == 6 or op == 7):
        if (op == 6):
            var = input("Enter name for the directory where data will be processed, or press enter to cancel: ")
        if (op == 7):
            var = input("Enter name for the directory where validated data will be stored, or press enter to cancel: ")
        if (var==''):
            print("File write cancelled.\n")
            continue
        if not (os.path.isdir(var)) or (var.isspace()):
            print("\nDirectory does not exist.\n")
            continue

        var = "./" + var
        
    #op corresponds to line of file to be changed 
    lines[op] = (var + '\n') 
    
    if (op == 8):
        var = input("Enter name for the directory where invalidated data will be stored, or press enter to cancel: ")
        if (var==''):
            print("File write cancelled.\n")
            continue
        if not (os.path.isdir(var)) or (var.isspace()):
            print("\nDirectory does not exist.\n")
            continue
        var = "./" + var
        lines[op] = var
        
    if (op == 9):
        get_date_range()
        continue

    #if enter key was pressed, cancel
    if (var == ''):
        print("File write cancelled.\n")
        continue

    
    #write to file with user's alteration
    with open('config.txt', 'w+') as file:
        for line in lines:
            file.write(line)

    print('')

